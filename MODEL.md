# Data Model — Breathe ESG

## Overview

Breathe ESG models enterprise carbon data as a **multi-tenant** pipeline: raw file uploads → parsed rows → normalized emissions records → analyst review → immutable audit trail.

## Multi-tenancy

Every business record is scoped to a **Client** (`tenants.Client`):

- `FileUpload.client`, `NormalizedRecord.client`, `CustomUser.client`, `Plant.client`
- Analysts only see data for their assigned client; **ADMIN** users can list all clients via `/api/clients/`
- Tenant isolation is enforced in queryset filters on records, audit logs, and uploads

## Plant lookup (SAP)

SAP `WERKS` plant codes are opaque integers without context. **`tenants.Plant`** maps `code → name, region, country` per client.

- Ingestion flags rows with unknown `WERKS` as **SUSPICIOUS**
- Descriptions include resolved plant name: `Diesel Fuel @ 4521 (Mumbai Refinery)`
- Seeded via `python manage.py seed_data`

## Core entities

| Model              | Purpose                                                               |
| ------------------ | --------------------------------------------------------------------- |
| `Client`           | Organization (name, slug)                                             |
| `Plant`            | SAP WERKS lookup table                                                |
| `CustomUser`       | Login with role `ADMIN` or `ANALYST`                                  |
| `FileUpload`       | CSV upload metadata (`rows_parsed`, `rows_failed`, `rows_suspicious`) |
| `RawRecord`        | One JSON row per CSV line + `parse_status` + `parse_error`            |
| `EmissionFactor`   | Lookup: kg CO₂e per unit by category/year/subcategory                 |
| `NormalizedRecord` | Calculated emissions + review workflow                                |
| `AuditLog`         | Before/after JSON snapshots for every action                          |
| `ApprovalRecord`   | Formal approval linkage when record is locked                         |

## Scope categorization

| Source                | Scope | Logic                                       |
| --------------------- | ----- | ------------------------------------------- |
| SAP (fuel/material)   | 1     | Direct combustion (`BWART=201` consumption) |
| Utility (electricity) | 2     | Grid electricity from meter kWh             |
| Travel                | 3     | Flights, hotels, ground transport           |

## Ingestion outcomes per row

| `RawRecord.parse_status` | NormalizedRecord created? | Review status                           |
| ------------------------ | ------------------------- | --------------------------------------- |
| `SUCCESS`                | Yes                       | `PENDING`                               |
| `SUSPICIOUS`             | Yes                       | `FLAGGED` (analyst must review)         |
| `FAILED`                 | No                        | N/A — visible on Ingestion issues panel |

## Unit normalization pipeline

1. **Parse** — Source-specific validators (SAP `MEINS`, utility dates, travel distance)
2. **Normalize** — Standard quantity + unit; optional `normalized_quantity_kwh`
3. **Factor lookup** — `EmissionFactor` by source, category, unit, subcategory (e.g. Maharashtra grid)
4. **Calculate** — `emission_kgco2e = quantity × factor_kgco2e_per_unit`
5. **Review** — Analyst approve → `is_locked=True`

## Source of truth

| Layer                | What it stores                         |
| -------------------- | -------------------------------------- |
| `RawRecord.raw_data` | Exact uploaded row (never overwritten) |
| `FileUpload`         | Which file, when, who, parse counts    |
| `NormalizedRecord`   | Analyst-facing emissions row           |
| `AuditLog`           | Who approved/flagged and state diff    |
| Approved + locked    | Auditor-facing truth                   |


```

Once `is_locked=True`, the `NormalizedRecord` is immutable — any attempt to modify it returns HTTP 422. The only permitted action on a locked record is reading it or exporting it to the audit log.

## API surfaces for assignment workflow

- `POST /api/upload/{source}/` — ingest file
- `GET /api/uploads/` — recent uploads with counts
- `GET /api/uploads/{id}/issues/` — failed + suspicious raw rows with errors
- `GET /api/records/` — review dashboard
- `PATCH /api/records/{id}/approve/` — lock for audit
