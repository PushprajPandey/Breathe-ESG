from decimal import Decimal

from .common import parse_decimal, parse_us_date


def _consumption_kwh(row: dict):
    return row.get("consumption_kwh") or row.get("Usage")


def _billing_start(row: dict):
    return row.get("billing_period_start") or row.get("Start Date")


def _billing_end(row: dict):
    return row.get("billing_period_end") or row.get("End Date")


def _estimation(row: dict) -> str:
    return (row.get("estimation") or row.get("Estimation") or "No").strip().lower()


def validate_utility_row(row: dict) -> tuple[str, str | None]:
    errors = []
    usage, err = parse_decimal(_consumption_kwh(row), "consumption_kwh")
    if err:
        errors.append(err)
    start, se = parse_us_date(_billing_start(row))
    if se:
        errors.append(se)
    end, ee = parse_us_date(_billing_end(row))
    if ee:
        errors.append(ee)
    if _estimation(row) == "yes":
        return "SUSPICIOUS", "Estimated consumption (estimation=Yes)"
    if errors:
        return "FAILED", "; ".join(errors)
    return "SUCCESS", None


def parse_utility_row(row: dict) -> dict:
    status, error = validate_utility_row(row)
    start, _ = parse_us_date(_billing_start(row))
    usage, _ = parse_decimal(_consumption_kwh(row), "consumption_kwh")
    site = (row.get("site_name") or "").strip()
    meter = (row.get("meter_id") or row.get("account_number") or "").strip()
    supplier = (row.get("supplier_name") or "").strip()
    state = (row.get("state") or "").strip()
    tariff = (row.get("tariff_code") or "").strip()

    if site and meter:
        description = f"Electricity - {site} ({meter})"
    elif site:
        description = f"Electricity - {site}"
    else:
        description = f"Electricity - {meter or 'meter'}"
    if supplier:
        description += f" — {supplier}"

    return {
        "parse_status": status,
        "parse_error": error or "",
        "activity_date": start.isoformat() if start else None,
        "description": description,
        "quantity": str(usage) if usage else None,
        "unit": "kWh",
        "normalized_quantity_kwh": str(usage) if usage else None,
        "scope": 2,
        "category": "grid_electricity",
        "subcategory": state or tariff or "default",
    }
