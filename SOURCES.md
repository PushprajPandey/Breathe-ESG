# Data Sources Research — Breathe ESG

## Reference files in `/data`

### 1. `460311045-Material-Document-Flow-Report-MSEG-MKPF-MAKT-tables-txt.txt`

Real SAP ABAP report **ZAP_ASSIGNMENT_2** (authored by Pavan Golesar, 2013) joining three SAP MM tables:

- **MKPF** — Material document header: `MBLNR` (document number), `MJAHR` (year), `BUDAT` (posting date in `YYYYMMDD` — SAP's native date format)
- **MSEG** — Material document segment: `ZEILE` (line item), `WERKS` (plant), `LGORT` (storage location), `MATNR` (material number), `MENGE` (quantity), `MEINS` (unit of measure), `BWART` (movement type)
- **MAKT** — Material description: `MAKTX` (English text description)

Movement type `BWART=201` (Goods Issue to Cost Center) represents actual fuel/material consumption — this is the correct Scope 1 signal. Other movement types (101 = Goods Receipt, 261 = Production Order issue) are out of scope for emissions.

`MEINS` is intentionally inconsistent across rows (`L`, `KG`, `M3`, `GAL`) because real SAP systems allow unit of measure to be set per material master record — different plants or legacy configurations use different units for the same material category.

**Sample:** `backend/fixtures/sample_sap.csv` — 50 rows, 5 intentional bad rows (missing `MEINS`, null `MENGE`, unknown `MATNR`) to exercise the validation pipeline.

**Plant codes:** `4521`, `2041`, `1021`, `2011` seeded in `tenants.Plant`.

**What would break in production:** New movement types not mapped to Scope 1; materials with no entry in `EmissionFactor`; plants not in the lookup table; clients running SAP in German locale with untranslated `MAKTX`.

---

### 2. `MeterConsumptionDataSpreadsheet_metered_en.xlsx` (ENERGY STAR Portfolio Manager)

Official EPA Portfolio Manager meter consumption template — the standard format used by facilities teams at US and international enterprise clients to track and report building energy usage. Downloaded directly from the ENERGY STAR portal.

Sheet **"Energy Use"** columns:
- `Start Date` (Required) — meter read date, not calendar month start
- `End Date` (Required) — next meter read date
- `Usage` (Required) — kWh consumed in the period
- `Cost` (Optional) — billing amount
- `Estimation` (Optional) — `Yes/No`; estimated reads occur when the meter is inaccessible

Sheet **"Validation"** — dropdown source for `Yes/No` estimation flag.

Key insight: billing periods are meter-read dates, not calendar months. A 12-month year produces 12 offset rows per meter (e.g. Jan 15 → Feb 13, Feb 14 → Mar 15). Our ingestion pipeline handles period-to-month attribution by splitting consumption proportionally across calendar months.

`Estimation=Yes` rows are flagged as `SUSPICIOUS` because estimated reads can be revised by the utility on the next bill, making them unreliable for locked audit records.

**Samples:**
- `sample_utility.csv` — 24 rows (2 meters × 12 months), Tata Power Maharashtra supplier, offset billing periods, 3 estimated rows flagged suspicious, rate ₹8.5/kWh from MERC 2026 commercial high-tension tariff

**What would break in production:** PDF-only bills with no portal export; utilities that bill in non-kWh units (therms, MMBTU) without unit conversion; multi-fuel meters mixing electricity and gas on one account; clients outside Maharashtra needing different grid emission factors.

---

### 3. Travel — Concur-style CSV + airlines dataset

**Format researched:** SAP Concur Travel itinerary and expense export (Concur developer API docs, `/api-reference/travel/itinerary/`). Key finding: Concur exposes `BookingOrigin`, `BookingDestination`, and airline/hotel metadata but **does not reliably include distance** — distance must be computed from city coordinates or IATA codes using the Haversine (great-circle) formula.

**`airlines_flights_data.csv`** is a public dataset of Indian domestic flight routes containing:
- `source_city`, `destination_city` — origin/destination city names
- `airline` — carrier name (IndiGo, Air India, SpiceJet, etc.)
- `stops` — `non-stop` or `one` (connecting flight)
- `duration` — total flight time
- `price` — ticket price in INR

This dataset was used to generate realistic Indian city-pair combinations and airline names for the travel fixture. Routes, airlines, and pricing reflect real domestic routes (Delhi–Mumbai, Mumbai–Bangalore, etc.).

**Sample:** `backend/fixtures/sample_travel.csv` — 60 rows combining Concur-style columns with city pairs drawn from the airlines dataset:
- 30 flights with `origin_iata`/`destination_iata` codes, no `distance_km` (pipeline calculates great-circle)
- 15 hotel stays with `hotel_nights` and city only
- 15 ground transport rows with known distances
- Connecting flights (`stops=one`) flagged as `SUSPICIOUS` — radiative forcing at altitude makes these higher-impact and harder to factor accurately

**What would break in production:** Non-IATA city names (tier-2 Indian cities without IATA codes); multi-leg itineraries not split into individual segments; international routes needing different emission factors; 300k+ row files from large corporates without streaming/batching.

---

## Why sample data looks realistic

All three fixtures were fabricated from **researched structures**, not invented columns:

- SAP dates as `YYYYMMDD`, mixed `MEINS` units, real SAP table field names from a production ABAP report
- Utility billing cycles mid-month reflecting actual meter read schedules, winter/summer kWh spread reflecting seasonal AC load in Maharashtra
- Travel routes are real Delhi–Mumbai, Mumbai–Bangalore domestic sectors with real Indian airline names from a public booking dataset