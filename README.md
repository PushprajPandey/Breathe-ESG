# Breathe ESG

Production-ready carbon emissions data ingestion and analyst review platform for enterprise clients.

## Stack

- **Backend:** Django 5 + Django REST Framework + JWT auth
- **Frontend:** React 18 + Vite + Tailwind CSS + React Query
- **Database:** PostgreSQL (production) / SQLite (local dev)
- **Design:** Stitch UI reference in `/stitch`

## Quick Start

### Backend

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env        # set SECRET_KEY, DATABASE_URL
python manage.py migrate
python manage.py seed_data  # seeds clients, users, plants, emission factors
python manage.py runserver
```

Demo credentials:

| Role | Username | Password |
|------|----------|----------|
| Admin | `admin` | `admin123` |
| Analyst | `analyst` | `analyst123` |

### Frontend

```bash
cd frontend
npm install
cp .env.example .env   # set VITE_API_BASE_URL=http://127.0.0.1:8000
npm run dev
```

Open http://localhost:5173

### End-to-end flow

1. Sign in as `analyst`
2. **Data Ingestion** → upload any fixture from `backend/fixtures/`
3. **Review Dashboard** → approve, flag, or reject records
4. **Audit Log** → view locked records and export CSV

## Sample Data

All fixtures are in `backend/fixtures/` — fabricated from real-world source research:

| File | Source | Rows | Notes |
|------|--------|------|-------|
| `sample_sap.csv` | SAP MSEG+MKPF+MAKT (ABAP report) | 50 | 5 intentional bad rows |
| `sample_utility.csv` | ENERGY STAR Portfolio Manager template | 24 | 3 estimated rows → FLAGGED |
| `sample_travel.csv` | Concur-style + Indian airlines dataset | 60 | Flights with IATA codes, no distance |

See [SOURCES.md](./SOURCES.md) for full research documentation on each format.

## Project Structure

```
breathe-esg/
├── backend/
│   ├── breatheesg/
│   │   ├── settings/
│   │   │   ├── base.py
│   │   │   └── production.py
│   │   └── wsgi.py
│   ├── tenants/        # Client, Plant, CustomUser
│   ├── ingestion/      # FileUpload, RawRecord, parsers
│   ├── emissions/      # NormalizedRecord, EmissionFactor
│   ├── audit/          # AuditLog, ApprovalRecord
│   ├── fixtures/       # sample_sap.csv, sample_utility.csv, sample_travel.csv
│   ├── requirements.txt
│   └── Procfile
├── frontend/
│   ├── src/
│   │   ├── pages/      # Login, Dashboard, Ingestion, Review, AuditLog, Settings
│   │   ├── components/
│   │   ├── api/        # Axios instance + interceptors
│   │   └── context/    # Auth context
│   ├── vercel.json
│   └── .env.example
├── data/               # Source research files
├── MODEL.md
├── DECISIONS.md
├── TRADEOFFS.md
└── SOURCES.md
```

## Ingestion Pipeline

```
Upload CSV → Parse rows → RawRecord per row
                ├── FAILED      → shown on Ingestion issues panel (not in Review)
                ├── SUSPICIOUS  → NormalizedRecord created, status = FLAGGED
                └── SUCCESS     → NormalizedRecord created, status = PENDING
                                      ↓
                              Analyst reviews in Review Dashboard
                                      ↓
                              APPROVED → is_locked = True → Audit Log
```


## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/auth/login/` | Obtain JWT token pair |
| `POST` | `/api/auth/refresh/` | Refresh access token |
| `POST` | `/api/upload/{source}/` | Upload CSV (`sap`, `utility`, `travel`) |
| `GET` | `/api/uploads/` | List recent uploads with row counts |
| `GET` | `/api/uploads/{id}/issues/` | Failed + suspicious raw rows |
| `GET` | `/api/records/` | List normalized records (filterable) |
| `PATCH` | `/api/records/{id}/approve/` | Approve and lock record |
| `PATCH` | `/api/records/{id}/flag/` | Flag as suspicious |
| `POST` | `/api/records/bulk-approve/` | Bulk approve by ID list |
| `GET` | `/api/records/stats/` | Dashboard summary counts |
| `GET` | `/api/audit-log/` | Locked audit trail |
| `GET` | `/api/clients/` | List clients (ADMIN only) |
| `GET` | `/api/health/` | Health check |

## Error Handling

All errors return consistent JSON — no HTML error pages in production:

```json
{
  "success": false,
  "error": {
    "code": "RECORD_LOCKED",
    "message": "This record has been locked for audit and cannot be modified.",
    "details": {}
  }
}
```



## Documentation

| File | Contents |
|------|----------|
| [MODEL.md](./MODEL.md) | Data model, multi-tenancy, scope categorization, audit trail |
| [DECISIONS.md](./DECISIONS.md) | Every design decision with justification and PM questions |
| [TRADEOFFS.md](./TRADEOFFS.md) | Three deliberate omissions and when to revisit them |
| [SOURCES.md](./SOURCES.md) | Real-world format research for all three data sources |