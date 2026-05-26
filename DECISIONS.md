# Design Decisions — Breathe ESG

## Ingestion mechanism (all three sources)

**Decision:** CSV file upload per source tab — not live API pull.

**Why:** Matches how enterprise teams actually deliver data in week-one onboarding: scheduled SAP report export, facilities portal download, T&E CSV export. No client API keys required for a 4-day prototype.

**Ask PM:** SFTP drop zone vs manual upload; virus scan requirement; PII retention policy for traveler IDs.

---

## SAP — flat CSV (MSEG + MKPF + MAKT)

**Decision:** Flat-file CSV from custom ABAP report `ZAP_ASSIGNMENT_2` structure.

**Subset handled:** Goods issue consumption (`BWART=201`), English `MAKTX`, plants in lookup table, units L/KG/M3/GAL, `BUDAT` as YYYYMMDD.

**Also added:** Optional German/alternate header aliases (`WERK`, `MATERIAL`, etc.) mapped to canonical columns.

**Ignored:** IDoc, OData, BAPI, cost center allocation, German-only exports without mapping.

**Ask PM:** Which movement types beyond 201 count as Scope 1? Should cost center (`KOSTL`) be captured for internal carbon chargebacks?

---

## Utility — portal CSV

**Decision:** Portal CSV — supports **two** shapes:

1. ENERGY STAR Portfolio Manager (`Start Date`, `Usage`, `Estimation`)
2. Supplier export shape (Tata Power columns: `consumption_kwh`, `billing_period_start`, `site_name`)

**Why ENERGY STAR:** It is the EPA's standard template, used by thousands of enterprise facilities teams globally. It directly addresses the assignment requirement of billing periods not aligning to calendar months — the template's `Start Date`/`End Date` columns make this explicit rather than assuming monthly rows.

**Ignored:** PDF bill OCR, utility API polling.

**Ask PM:** Single global grid emission factor vs per-state factors (we seed Maharashtra MERC 2026 at ₹8.5/kWh). International clients will need country-specific grid factors.

---

## Travel — CSV (Concur shape + airlines dataset)

**Decision:** CSV upload; auto-detect **Concur-style** vs **airlines booking** headers.

**Subset:** Flights (great-circle km from cities or IATA codes via Haversine formula), hotels (nights × emission factor), rail/car when distance is present. Connecting flights (`stops=one`) flagged as `SUSPICIOUS`.

**Why Haversine for distance:** Concur's API documentation confirms that itinerary exports include origin/destination codes but not computed distance. Great-circle distance is the standard approximation used by DEFRA and ICAO methodologies for flight emissions.

**Ignored:** Live Concur API OAuth flow, cabin-class multipliers (Business = 2.0×, First = 4.0×), radiative forcing uplift factor.

**Cap:** 5,000 rows per upload to handle large airline booking exports without timeout.

**Ask PM:** Should we apply DEFRA cabin-class multipliers? Official DEFRA factors vs ICAO Carbon Calculator — they differ by ~15% on long-haul.

---

## Parsers are not universal

**Decision:** Fixed rule-based parsers — **not** trained models, **not** automatic column inference for arbitrary client formats.

**Why:** Assignment evaluates judgment. We document researched formats and extend parsers deliberately. A client with a non-standard format gets a new column alias mapping or parser module — same pipeline, explicit rules, auditable behavior.

**Tradeoff:** Onboarding a client with a completely different SAP configuration requires a developer. Acceptable for enterprise onboarding; not acceptable for self-serve.

---

## Authentication and roles

**Decision:** JWT (JSON Web Tokens) for API authentication, not Django session cookies.

**Why:** The React SPA is deployed on Vercel and the Django backend on Railway — two separate domains. Cookie-based session auth would require complex `SameSite=None; Secure` CORS configuration and breaks on some browsers. JWT sent as `Authorization: Bearer <token>` header works cleanly across origins.

- `ADMIN` role — manage clients, users, emission factors; see all tenants
- `ANALYST` role — ingest files, review and approve records for their assigned client only

---

## Error handling

**Decision:** Custom DRF JSON exception handler replacing Django's default HTML error pages.

**Why:** The frontend is a React SPA on a separate domain. Django's default `DEBUG=False` error pages are HTML — useless and confusing to a JavaScript client. Every error, including 500s, returns `{success: false, error: {code, message, details}}`.

- `422 Unprocessable Entity` returned when attempting to modify a locked record — semantically more accurate than 400 (the request is valid, the business rule rejects it)
- Stack traces never exposed to the client in production

---

## Analyst UX decisions

- Source-specific columns in the Review table (SAP shows `WERKS`/plant name; utility shows meter ID and billing period; travel shows route and transport mode)
- Ingestion **issues panel** on each source tab shows failed and suspicious raw rows with `parse_error` message — analyst sees exactly which rows failed and why without needing database access
- **Review note** column on flagged rows explains the suspicion reason (e.g. "Estimated read", "Unknown plant code", "Connecting flight — verify distance")
- Upload history list per source tab with row counts so analysts can track ingestion runs over time