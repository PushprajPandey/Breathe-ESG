"""Build a 60-row travel sample from airlines_flights_data.csv for fixtures."""
import csv
import sys
from pathlib import Path

SOURCE = Path(r"c:\Users\sajal\Downloads\airlines_flights_data.csv")
OUT = Path(__file__).resolve().parent.parent / "fixtures" / "sample_travel.csv"
TARGET = 60


def main():
    if not SOURCE.exists():
        print(f"Source not found: {SOURCE}")
        sys.exit(1)
    rows = []
    with SOURCE.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        seen_routes = set()
        for i, row in enumerate(reader):
            route = (row.get("source_city"), row.get("destination_city"), row.get("stops"))
            if route in seen_routes and i % 500 != 0:
                continue
            seen_routes.add(route)
            rows.append(row)
            if len(rows) >= TARGET:
                break
            if i > 50000 and len(rows) >= TARGET:
                break
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)
    print(f"Wrote {len(rows)} rows to {OUT}")


if __name__ == "__main__":
    main()
