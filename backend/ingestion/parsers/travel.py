from decimal import Decimal

from .airlines import is_airlines_format, parse_airlines_row, validate_airlines_row
from .common import great_circle_km, parse_decimal, parse_us_date

MODE_FACTORS = {
    "FLIGHT": Decimal("0.255"),
    "RAIL": Decimal("0.035"),
    "CAR": Decimal("0.17"),
    "HOTEL": Decimal("25.0"),
}

IATA_COORDS = {
    "LHR": (51.47, -0.45), "JFK": (40.64, -73.78), "CDG": (49.01, 2.55),
    "FRA": (50.03, 8.57), "LAX": (33.94, -118.41), "ORD": (41.98, -87.90),
    "SIN": (1.36, 103.99), "HKG": (22.31, 113.92), "DXB": (25.25, 55.36),
    "AMS": (52.31, 4.77), "BCN": (41.30, 2.08), "NRT": (35.76, 140.39),
    "ICN": (37.46, 126.44), "SYD": (-33.95, 151.18), "MEL": (-37.67, 144.84),
    "DEL": (28.6139, 77.2090), "BOM": (19.0760, 72.8777),
}


def distance_from_iata(origin: str, dest: str) -> Decimal | None:
    o = IATA_COORDS.get((origin or "").upper())
    d = IATA_COORDS.get((dest or "").upper())
    if o and d:
        return great_circle_km(o[0], o[1], d[0], d[1])
    return None


def _validate_concur_row(row: dict) -> tuple[str, str | None]:
    errors = []
    mode = (row.get("transport_mode") or "").strip().upper()
    if not mode:
        errors.append("Missing transport_mode")
    if not row.get("trip_id"):
        errors.append("Missing trip_id")
    trip_date, de = parse_us_date(row.get("trip_date", ""))
    if de and not row.get("trip_date"):
        errors.append("Missing trip_date")
    elif de:
        errors.append(de)
    if mode == "FLIGHT" and not row.get("origin_iata") and not row.get("distance_km"):
        errors.append("Flight requires IATA codes or distance")
    if errors:
        return "FAILED", "; ".join(errors)
    if not row.get("traveler_id"):
        return "SUSPICIOUS", "Missing traveler_id"
    if not trip_date and row.get("trip_date") == "":
        return "SUSPICIOUS", "Missing trip_date"
    return "SUCCESS", None


def validate_travel_row(row: dict) -> tuple[str, str | None]:
    if is_airlines_format(row):
        return validate_airlines_row(row)
    return _validate_concur_row(row)


def parse_travel_row(row: dict) -> dict:
    if is_airlines_format(row):
        return parse_airlines_row(row)

    status, error = _validate_concur_row(row)
    mode = (row.get("transport_mode") or "").strip().upper()
    activity_date, _ = parse_us_date(row.get("trip_date", ""))
    dist = row.get("distance_km")
    quantity = None
    unit = "km"
    if mode == "HOTEL":
        nights, _ = parse_decimal(row.get("hotel_nights"), "hotel_nights")
        quantity = nights
        unit = "nights"
    elif dist:
        quantity, _ = parse_decimal(dist, "distance_km")
    elif mode == "FLIGHT":
        quantity = distance_from_iata(row.get("origin_iata"), row.get("destination_iata"))
    else:
        quantity, _ = parse_decimal(dist, "distance_km")
    desc = f"{mode}: {row.get('origin', '')} → {row.get('destination', '')}"
    return {
        "parse_status": status,
        "parse_error": error or "",
        "activity_date": activity_date.isoformat() if activity_date else None,
        "description": desc,
        "quantity": str(quantity) if quantity else None,
        "unit": unit,
        "normalized_quantity_kwh": None,
        "scope": 3,
        "category": mode.lower(),
        "subcategory": row.get("traveler_id", ""),
    }
