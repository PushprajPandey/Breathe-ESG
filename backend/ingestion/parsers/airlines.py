"""Parser for airline booking / flight search exports (e.g. airlines_flights_data.csv)."""
from datetime import date, timedelta
from decimal import Decimal

from .common import great_circle_km, parse_decimal

# Major Indian cities in typical domestic flight datasets
CITY_COORDS = {
    "DELHI": (28.6139, 77.2090),
    "MUMBAI": (19.0760, 72.8777),
    "BANGALORE": (12.9716, 77.5946),
    "BENGALURU": (12.9716, 77.5946),
    "KOLKATA": (22.5726, 88.3639),
    "HYDERABAD": (17.3850, 78.4867),
    "CHENNAI": (13.0827, 80.2707),
    "PUNE": (18.5204, 73.8567),
    "AHMEDABAD": (23.0225, 72.5714),
    "GOA": (15.2993, 74.1240),
    "KOCHI": (9.9312, 76.2673),
    "COCHIN": (9.9312, 76.2673),
    "JAIPUR": (26.9124, 75.7873),
    "LUCKNOW": (26.8467, 80.9462),
    "SRINAGAR": (34.0837, 74.7973),
    "GUWAHATI": (26.1445, 91.7362),
    "CHANDIGARH": (30.7333, 76.7794),
    "INDORE": (22.7196, 75.8577),
    "NAGPUR": (21.1458, 79.0882),
    "PATNA": (25.5941, 85.1376),
    "BHUBANESWAR": (20.2961, 85.8245),
    "VARANASI": (25.3176, 82.9739),
    "AMRITSAR": (31.6340, 74.8723),
    "THIRUVANANTHAPURAM": (8.5241, 76.9366),
    "COIMBATORE": (11.0168, 76.9558),
    "MANGALORE": (12.9141, 74.8560),
    "VISAKHAPATNAM": (17.6868, 83.2185),
    "RANCHI": (23.3441, 85.3096),
    "RAIPUR": (21.2514, 81.6296),
}


def norm_city(name: str) -> str:
    return (name or "").strip().upper().replace(" ", "_")


def distance_between_cities(origin: str, destination: str) -> Decimal | None:
    o = CITY_COORDS.get(norm_city(origin))
    d = CITY_COORDS.get(norm_city(destination))
    if o and d:
        return great_circle_km(o[0], o[1], d[0], d[1])
    return None


def is_airlines_format(row: dict) -> bool:
    return bool(row.get("source_city") and row.get("destination_city") and row.get("airline"))


def trip_date_from_row(row: dict) -> date:
    """Derive activity date from days_left (booking dataset convention)."""
    base = date(2024, 6, 1)
    try:
        days_left = int(float(row.get("days_left", 30)))
    except (TypeError, ValueError):
        days_left = 30
    try:
        idx = int(float(row.get("index", 0)))
    except (TypeError, ValueError):
        idx = 0
    return base - timedelta(days=min(days_left + (idx % 14), 180))


def validate_airlines_row(row: dict) -> tuple[str, str | None]:
    if not row.get("source_city"):
        return "FAILED", "Missing source_city"
    if not row.get("destination_city"):
        return "FAILED", "Missing destination_city"
    if norm_city(row["source_city"]) == norm_city(row["destination_city"]):
        return "FAILED", "Origin and destination are the same"
    dist = distance_between_cities(row["source_city"], row["destination_city"])
    if not dist:
        return "SUSPICIOUS", f"Unknown city pair: {row['source_city']} → {row['destination_city']}"
    stops = (row.get("stops") or "").strip().lower()
    try:
        duration = float(row.get("duration", 0))
    except (TypeError, ValueError):
        duration = 0
    if stops == "one" and duration > 8:
        return "SUSPICIOUS", "Connecting flight with long duration"
    if stops == "two_or_more":
        return "SUSPICIOUS", "Multiple stops"
    return "SUCCESS", None


def parse_airlines_row(row: dict) -> dict:
    status, error = validate_airlines_row(row)
    origin = row.get("source_city", "")
    dest = row.get("destination_city", "")
    airline = row.get("airline", "")
    flight = row.get("flight", row.get("index", ""))
    travel_class = row.get("class", "Economy")
    activity = trip_date_from_row(row)
    dist = distance_between_cities(origin, dest)
    price, _ = parse_decimal(row.get("price"), "price")

    desc = f"FLIGHT: {airline} {flight} — {origin} → {dest} ({travel_class})"

    return {
        "parse_status": status,
        "parse_error": error or "",
        "activity_date": activity.isoformat(),
        "description": desc,
        "quantity": str(dist) if dist else None,
        "unit": "km",
        "normalized_quantity_kwh": None,
        "scope": 3,
        "category": "flight",
        "subcategory": airline.replace(" ", "_")[:50],
        "trip_id": f"FLT-{flight}",
        "traveler_id": "",
        "cost_usd": str(price) if price else None,
    }
