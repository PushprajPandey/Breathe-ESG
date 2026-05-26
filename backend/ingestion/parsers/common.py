import math
from datetime import datetime
from decimal import Decimal, InvalidOperation


def great_circle_km(lat1, lon1, lat2, lon2) -> Decimal:
    r = 6371
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return Decimal(str(round(2 * r * math.asin(math.sqrt(a)), 2)))


def parse_sap_date(budat: str):
    if not budat or len(budat) != 8:
        return None, "Invalid BUDAT format (expected YYYYMMDD)"
    try:
        return datetime.strptime(budat, "%Y%m%d").date(), None
    except ValueError:
        return None, f"Cannot parse BUDAT: {budat}"


def parse_decimal(value, field_name="value"):
    if value is None or value == "":
        return None, f"Missing {field_name}"
    try:
        return Decimal(str(value).replace(",", "")), None
    except (InvalidOperation, ValueError):
        return None, f"Invalid decimal for {field_name}: {value}"


def parse_us_date(value: str):
    if not value:
        return None, "Missing date"
    for fmt in ("%m/%d/%Y", "%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(value.strip(), fmt).date(), None
        except ValueError:
            continue
    return None, f"Cannot parse date: {value}"
