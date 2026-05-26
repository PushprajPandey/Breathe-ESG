# Deliberate Tradeoffs — Breathe ESG

Three capabilities we **chose not to build** for this release, and why.

## 1. Real SAP RFC / OData integration

**Not built:** Live connection to SAP S/4HANA or ECC via RFC, OData, or CPI.

**Tradeoff:** Flat CSV upload is manual but ships in days. RFC requires SAP credentials, network allowlists, ABAP transport approvals, and ongoing breakage on SAP upgrades.

**Cost:** Analysts must export reports on a schedule; no real-time inventory sync.

**When to revisit:** Customer has SAP PI/CPI and a named functional owner for `ZAP_ASSIGNMENT_2` or equivalent custom report.

## 2. Real-time utility API polling

**Not built:** Automated pulls from utility portals or smart-meter APIs.

**Tradeoff:** Portal CSV matches how facilities teams already work (ENERGY STAR uploads). Utility APIs are fragmented (one endpoint per supplier, inconsistent auth).

**Cost:** Data latency of monthly billing cycles; estimated reads flagged manually.

**When to revisit:** Customer standardizes on a single MDM/utility data vendor (e.g. Urjanet, Arcadia).

## 3. Automated emission factor updates

**Not built:** Scheduled ingestion of DEFRA/EPA/eGRID factor releases.

**Tradeoff:** Seeded static factors for 2024 keep calculations explainable and auditable. Auto-updates without governance create year-over-year reporting breaks.

**Cost:** Factors must be updated via migration/seed or admin when regulations change.

**When to revisit:** Factor versioning UI with approval workflow and effective-date rules.
