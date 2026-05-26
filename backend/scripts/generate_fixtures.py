"""Generate sample CSV fixtures for Breathe ESG."""
import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

FIXTURES = Path(__file__).resolve().parent.parent / "fixtures"

PLANTS = ["4521", "2041", "1021"]
LGORTS = ["GN00", "FG00", "WP00", "RM00"]
MATERIALS = [
    ("DIESEL-001", "Diesel Fuel", "L"),
    ("NATGAS-002", "Natural Gas", "M3"),
    ("LPG-003", "LPG", "KG"),
    ("HFO-004", "Heavy Fuel Oil", "GAL"),
]
UNITS = ["L", "KG", "M3", "GAL"]


def generate_sap():
    rows = []
    doc_base = 5000001000
    start = datetime(2024, 1, 1)
    for i in range(45):
        mat, desc, default_unit = random.choice(MATERIALS)
        month_offset = i // 8
        day = (i % 28) + 1
        dt = datetime(2024, 1 + month_offset, min(day, 28))
        budat = dt.strftime("%Y%m%d")
        plant = PLANTS[i % 3]
        qty = round(random.uniform(50, 2500), 3)
        unit = random.choice(UNITS) if random.random() > 0.3 else default_unit
        rows.append({
            "MBLNR": str(doc_base + i),
            "MJAHR": "2024",
            "BUDAT": budat,
            "ZEILE": f"{(i % 4) + 1:04d}",
            "WERKS": plant,
            "LGORT": LGORTS[i % 4],
            "MATNR": mat,
            "MAKTX": desc,
            "MENGE": f"{qty:.3f}",
            "MEINS": unit,
            "BWART": "201",
        })
    # 5 bad rows
    rows.append({**rows[0], "MEINS": "", "MENGE": "100.000", "MBLNR": "5000001991"})
    rows.append({**rows[1], "MENGE": "", "MEINS": "L", "MBLNR": "5000001992"})
    rows.append({**rows[2], "MATNR": "UNKNOWN-999", "MAKTX": "", "MBLNR": "5000001993"})
    rows.append({**rows[3], "MEINS": "INVALID", "MBLNR": "5000001994"})
    rows.append({**rows[4], "BUDAT": "invalid", "MBLNR": "5000001995"})

    path = FIXTURES / "sample_sap.csv"
    fields = ["MBLNR", "MJAHR", "BUDAT", "ZEILE", "WERKS", "LGORT", "MATNR", "MAKTX", "MENGE", "MEINS", "BWART"]
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    print(f"Wrote {path} ({len(rows)} rows)")


def generate_utility():
    rows = []
    meters = ["MTR-001-A", "MTR-001-B"]
    account = "ACC-UK-LON-001"
    # 12 months, offset billing 15th to 14th
    monthly_usage = [42000, 45000, 38000, 32000, 28000, 24000, 22000, 23000, 26000, 30000, 36000, 40000]
    for month in range(12):
        start = datetime(2024, 1, 15) + timedelta(days=30 * month)
        end = start + timedelta(days=30)
        for mi, meter in enumerate(meters):
            usage = monthly_usage[month] + (500 if mi == 0 else 0)
            if month in (6, 7):
                usage = int(usage * 0.75)
            est = "Yes" if month in (2, 5, 9) and mi == 0 else "No"
            cost = round(usage * 0.28, 2)
            rows.append({
                "account_number": account,
                "meter_id": meter,
                "Start Date": start.strftime("%m/%d/%Y"),
                "End Date": end.strftime("%m/%d/%Y"),
                "Usage": usage,
                "Cost": cost,
                "Estimation": est,
            })

    path = FIXTURES / "sample_utility.csv"
    fields = ["account_number", "meter_id", "Start Date", "End Date", "Usage", "Cost", "Estimation"]
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    print(f"Wrote {path} ({len(rows)} rows)")


def generate_travel():
    rows = []
    employees = ["EMP001", "EMP002", "EMP003"]
    airports = [
        ("LHR", "JFK"), ("CDG", "FRA"), ("LAX", "ORD"), ("SIN", "HKG"),
        ("DXB", "LHR"), ("AMS", "BCN"), ("NRT", "ICN"), ("SYD", "MEL"),
    ]
    trip_id = 1000
    for i in range(20):
        o, d = random.choice(airports)
        rows.append({
            "trip_id": f"TRIP-{trip_id}",
            "traveler_id": employees[i % 3],
            "trip_date": f"2024-{(i % 6) + 1:02d}-{(i % 28) + 1:02d}",
            "origin": o,
            "destination": d,
            "transport_mode": "FLIGHT",
            "distance_km": "",
            "origin_iata": o,
            "destination_iata": d,
            "hotel_nights": "",
            "cost_usd": round(random.uniform(200, 2500), 2),
        })
        trip_id += 1
    for i in range(10):
        rows.append({
            "trip_id": f"TRIP-{trip_id}",
            "traveler_id": employees[i % 3],
            "trip_date": f"2024-{(i % 6) + 1:02d}-15",
            "origin": "London",
            "destination": "London",
            "transport_mode": "HOTEL",
            "distance_km": "",
            "origin_iata": "",
            "destination_iata": "",
            "hotel_nights": random.randint(1, 5),
            "cost_usd": round(random.uniform(150, 800), 2),
        })
        trip_id += 1
    modes = ["RAIL", "CAR", "RAIL", "CAR"]
    for i in range(10):
        dist = random.randint(50, 500) if i != 7 else ""
        rows.append({
            "trip_id": f"TRIP-{trip_id}",
            "traveler_id": employees[i % 3] if i != 8 else "",
            "trip_date": f"2024-03-{(i + 1):02d}" if i != 9 else "",
            "origin": "Manchester",
            "destination": "Birmingham",
            "transport_mode": modes[i % 4],
            "distance_km": dist,
            "origin_iata": "",
            "destination_iata": "",
            "hotel_nights": "",
            "cost_usd": round(random.uniform(30, 200), 2),
        })
        trip_id += 1

    path = FIXTURES / "sample_travel.csv"
    fields = [
        "trip_id", "traveler_id", "trip_date", "origin", "destination",
        "transport_mode", "distance_km", "origin_iata", "destination_iata",
        "hotel_nights", "cost_usd",
    ]
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    print(f"Wrote {path} ({len(rows)} rows)")


if __name__ == "__main__":
    FIXTURES.mkdir(parents=True, exist_ok=True)
    generate_sap()
    generate_utility()
    generate_travel()
