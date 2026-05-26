import csv
import io
from decimal import Decimal

from audit.models import AuditAction, AuditLog
from emissions.models import EmissionFactor, NormalizedRecord, ReviewStatus
from ingestion.models import FileUpload, ParseStatus, RawRecord, SourceType, UploadStatus
from ingestion.parsers import (
    parse_sap_row,
    parse_travel_row,
    parse_utility_row,
    validate_sap_row,
    validate_travel_row,
    validate_utility_row,
)

PARSERS = {
    SourceType.SAP: (validate_sap_row, parse_sap_row),
    SourceType.UTILITY: (validate_utility_row, parse_utility_row),
    SourceType.TRAVEL: (validate_travel_row, parse_travel_row),
}

SCOPE_MAP = {SourceType.SAP: 1, SourceType.UTILITY: 2, SourceType.TRAVEL: 3}
# Cap travel ingests — full airline datasets can be 300k+ rows
MAX_TRAVEL_ROWS = 5000


def _lookup_factor(source_type, category, unit, subcategory=""):
    if subcategory:
        factor = EmissionFactor.objects.filter(
            source_type=source_type,
            category__iexact=category,
            unit__iexact=unit,
            subcategory__iexact=subcategory,
        ).first()
        if factor:
            return factor
    return EmissionFactor.objects.filter(
        source_type=source_type,
        category__iexact=category,
        unit__iexact=unit,
        subcategory="",
    ).first() or EmissionFactor.objects.filter(
        source_type=source_type,
        category__iexact=category,
        unit__iexact=unit,
    ).first()


def _calculate_emissions(parsed: dict, source_type: str) -> tuple[EmissionFactor | None, Decimal | None]:
    factor = _lookup_factor(
        source_type,
        parsed.get("category", ""),
        parsed.get("unit", ""),
        parsed.get("subcategory", ""),
    )
    if not factor and parsed.get("unit") == "nights":
        factor = _lookup_factor(source_type, "hotel", "nights")
    if not factor:
        factor = EmissionFactor.objects.filter(source_type=source_type).first()
    qty = parsed.get("quantity")
    if not factor or not qty:
        return factor, None
    try:
        emission = Decimal(str(qty)) * factor.factor_kgco2e_per_unit
        return factor, emission
    except Exception:
        return factor, None


def process_upload(upload: FileUpload, user=None):
    upload.status = UploadStatus.PROCESSING
    upload.save(update_fields=["status"])

    source_type = upload.source_type
    validate_fn, parse_fn = PARSERS[source_type]

    upload.file_path.open("r")
    content = upload.file_path.read()
    if isinstance(content, bytes):
        content = content.decode("utf-8-sig")
    upload.file_path.close()

    reader = csv.DictReader(io.StringIO(content))
    fieldnames = reader.fieldnames or []
    rows_parsed = 0
    rows_failed = 0
    rows_suspicious = 0
    rows_truncated = False
    max_rows = MAX_TRAVEL_ROWS if source_type == SourceType.TRAVEL else None

    for row_num, row in enumerate(reader, start=1):
        if max_rows and row_num > max_rows:
            rows_truncated = True
            break
        clean_row = {k.strip(): (v.strip() if isinstance(v, str) else v) for k, v in row.items() if k}
        status, err = validate_fn(clean_row)
        if source_type == SourceType.SAP:
            parsed = parse_fn(clean_row, client_id=upload.client_id)
        else:
            parsed = parse_fn(clean_row)
        if status == "FAILED":
            parse_status = ParseStatus.FAILED
            rows_failed += 1
        elif status == "SUSPICIOUS" or parsed.get("parse_status") == "SUSPICIOUS":
            parse_status = ParseStatus.SUSPICIOUS
            rows_suspicious += 1
        else:
            parse_status = ParseStatus.SUCCESS
            rows_parsed += 1

        raw = RawRecord.objects.create(
            upload=upload,
            raw_data=clean_row,
            row_number=row_num,
            parse_status=parse_status,
            parse_error=err or parsed.get("parse_error", ""),
        )

        if parse_status == ParseStatus.FAILED:
            continue

        from datetime import datetime

        activity_date = None
        if parsed.get("activity_date"):
            try:
                activity_date = datetime.fromisoformat(parsed["activity_date"]).date()
            except ValueError:
                pass

        factor, emission = _calculate_emissions(parsed, source_type)
        norm = NormalizedRecord.objects.create(
            raw_record=raw,
            client=upload.client,
            source_type=source_type,
            activity_date=activity_date,
            description=parsed.get("description", ""),
            quantity=Decimal(parsed["quantity"]) if parsed.get("quantity") else None,
            unit=parsed.get("unit", ""),
            normalized_quantity_kwh=(
                Decimal(parsed["normalized_quantity_kwh"])
                if parsed.get("normalized_quantity_kwh")
                else None
            ),
            emission_factor=factor,
            emission_kgco2e=emission,
            scope=SCOPE_MAP.get(source_type, parsed.get("scope", 1)),
            review_status=(
                ReviewStatus.PENDING
                if parse_status != ParseStatus.SUSPICIOUS
                else ReviewStatus.PENDING
            ),
        )
        if parse_status == ParseStatus.SUSPICIOUS:
            norm.review_status = ReviewStatus.FLAGGED
            norm.save(update_fields=["review_status"])

        AuditLog.objects.create(
            record=norm,
            action=AuditAction.CREATED,
            performed_by=user,
            after_state={"review_status": norm.review_status, "emission_kgco2e": str(emission or "")},
            message=f"Ingested row {row_num} from {source_type}",
        )

    upload.rows_parsed = rows_parsed
    upload.rows_failed = rows_failed
    upload.rows_suspicious = rows_suspicious
    upload.rows_truncated = rows_truncated
    upload.status = UploadStatus.COMPLETED
    upload.save()

    msg = (
        f"Upload {upload.id}: {rows_parsed} clean, {rows_suspicious} suspicious, "
        f"{rows_failed} failed"
    )
    if rows_truncated:
        msg += f" (truncated at {MAX_TRAVEL_ROWS} rows)"
    AuditLog.objects.create(
        action=AuditAction.UPLOADED,
        performed_by=user,
        message=msg,
        after_state={
            "upload_id": upload.id,
            "rows_parsed": rows_parsed,
            "rows_suspicious": rows_suspicious,
            "rows_failed": rows_failed,
            "rows_truncated": rows_truncated,
            "format": (
                "airlines"
                if "source_city" in fieldnames
                else "concur"
                if source_type == SourceType.TRAVEL
                else "sap"
                if source_type == SourceType.SAP
                else "utility"
            ),
        },
    )
    return upload
