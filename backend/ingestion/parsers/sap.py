from decimal import Decimal

from ingestion.plant_lookup import get_plant_label
from tenants.models import Plant

from .common import parse_decimal, parse_sap_date

VALID_UNITS = {"L", "KG", "M3", "GAL", "l", "kg", "m3", "gal"}
MATERIAL_SCOPE = {
    "DIESEL-001": ("diesel", 1),
    "NATGAS-002": ("natural_gas", 1),
    "LPG-003": ("lpg", 1),
    "HFO-004": ("heavy_fuel_oil", 1),
}

# Optional German / alternate SAP export headers → canonical keys
SAP_HEADER_ALIASES = {
    "MBLNR": ["MBLNR", "DOC_NO", "DOCUMENT"],
    "BUDAT": ["BUDAT", "POSTING_DATE", "BUCHDAT"],
    "MATNR": ["MATNR", "MATERIAL", "MATERIAL_NR"],
    "MAKTX": ["MAKTX", "MATERIAL_TEXT", "MAKTX_EN"],
    "MENGE": ["MENGE", "QUANTITY", "MNG01"],
    "MEINS": ["MEINS", "UNIT", "UOM"],
    "WERKS": ["WERKS", "PLANT", "WERK"],
    "BWART": ["BWART", "MOVEMENT_TYPE"],
}


def normalize_sap_row(row: dict) -> dict:
    """Map German or alternate column names to canonical MSEG/MKPF fields."""
    upper_map = {k.upper().strip(): v for k, v in row.items()}
    out = dict(row)
    for canonical, aliases in SAP_HEADER_ALIASES.items():
        if out.get(canonical):
            continue
        for alias in aliases:
            if alias.upper() in upper_map:
                out[canonical] = upper_map[alias.upper()]
                break
    return out


UNIT_TO_KWH = {
    "L": Decimal("0.01"),
    "KG": Decimal("0.014"),
    "M3": Decimal("10.55"),
    "GAL": Decimal("0.037"),
}


def validate_sap_row(row: dict) -> tuple[str, str | None]:
    row = normalize_sap_row(row)
    errors = []
    if not row.get("MBLNR"):
        errors.append("Missing MBLNR")
    if not row.get("MATNR"):
        errors.append("Missing MATNR")
    meins = (row.get("MEINS") or "").strip().upper()
    if not meins:
        errors.append("Missing MEINS")
    elif meins not in {u.upper() for u in VALID_UNITS}:
        errors.append(f"Unknown unit: {meins}")
    qty, err = parse_decimal(row.get("MENGE"), "MENGE")
    if err:
        errors.append(err)
    _, date_err = parse_sap_date(str(row.get("BUDAT", "")))
    if date_err:
        errors.append(date_err)
    matnr = (row.get("MATNR") or "").strip().upper()
    if matnr and matnr not in MATERIAL_SCOPE:
        if "UNKNOWN" in matnr:
            errors.append(f"Unknown material: {matnr}")
    werks = (row.get("WERKS") or "").strip()
    if werks and not Plant.objects.filter(code=werks).exists():
        errors.append(f"Unknown plant code: {werks} (not in lookup table)")
    if errors:
        if any(
            "Missing" in e or "Invalid" in e or "Unknown unit" in e or "Unknown material" in e for e in errors
        ):
            status = "FAILED"
        else:
            status = "SUSPICIOUS"
        return status, "; ".join(errors)
    return "SUCCESS", None


def parse_sap_row(row: dict, client_id=None) -> dict:
    row = normalize_sap_row(row)
    status, error = validate_sap_row(row)
    matnr = (row.get("MATNR") or "").strip().upper()
    fuel_cat = MATERIAL_SCOPE.get(matnr, ("unknown", 1))[0]
    activity_date, _ = parse_sap_date(str(row.get("BUDAT", "")))
    qty, _ = parse_decimal(row.get("MENGE"), "MENGE")
    unit = (row.get("MEINS") or "").strip().upper()
    norm_kwh = None
    if qty and unit in UNIT_TO_KWH:
        norm_kwh = qty * UNIT_TO_KWH[unit]
    werks = row.get("WERKS", "")
    plant_label = get_plant_label(werks, client_id)
    material = row.get("MAKTX") or matnr
    desc = f"{material} @ {plant_label}" if plant_label else material
    return {
        "parse_status": status,
        "parse_error": error or "",
        "activity_date": activity_date.isoformat() if activity_date else None,
        "description": desc,
        "quantity": str(qty) if qty else None,
        "unit": unit,
        "normalized_quantity_kwh": str(norm_kwh) if norm_kwh else None,
        "scope": 1,
        "category": fuel_cat,
        "subcategory": werks,
    }
