# Stage 1: Extraction Results

## VistaBalayan Tourism Data Analytics and Decision Support Pipeline

This document records the verified Stage 1 extraction, local staging, and validation handover. Raw CSV files, the SQLite database, credentials, and generated JSON logs remain local and are excluded from Git.

---

# 1. Verified Current Run

The real VistaBalayan extraction was executed locally using the private Supabase configuration. Credentials and source connection values are intentionally not recorded here.

| Stage 1 operation | Result |
|---|---|
| Source connection test | `PASS` |
| CSV extraction | `PASS` |
| SQLite staging build | `PASS` |
| Metadata and relationship validation | `PASS` |
| Overall Stage 1 result | `PASS` |

## 1.1 Extracted record counts

| Source table | Records | Batches |
|---|---:|---:|
| `establishments` | 38 | 1 |
| `visitor_reports` | 2,400 | 3 |
| `accommodation_reports` | 1,857 | 2 |
| `room_occupancy_details` | 5,938 | 6 |

The batch size was a page size. It did not limit the total number of records extracted; the extractor continued through ordered batches until all available records were retrieved.

## 1.2 Relationship validation

All required relationships passed with `missing_parent_count: 0`:

- `visitor_reports.establishment_id` → `establishments.id`
- `accommodation_reports.establishment_id` → `establishments.id`
- `room_occupancy_details.accommodation_report_id` → `accommodation_reports.id`

Primary-key presence and uniqueness checks also passed for the configured tables.

## 1.3 Non-critical warnings

The validator reported configured timestamp columns that were not present in some source exports:

- `visitor_reports.updated_at`
- `accommodation_reports.updated_at`
- `room_occupancy_details.created_at`
- `room_occupancy_details.updated_at`

These warnings did not affect the required identifiers, report dates, or foreign-key relationships. They must remain visible to the transformation-stage profiling process and must not be silently treated as available fields.

---

# 2. Stage 1 Handover Decision

```text
Stage 1: COMPLETED
Stage 1 Decision: APPROVED FOR TRANSFORMATION
Stage 2: DOCUMENTATION DEFINED; IMPLEMENTATION NOT STARTED
```

The transformation stage must consume the validated local handover. It must not re-extract data from Supabase as part of transformation processing.

The current handover consists of the four local CSV exports and the local SQLite staging database produced by the verified run:

```text
pipeline/raw/establishments.csv
pipeline/raw/visitor_reports.csv
pipeline/raw/accommodation_reports.csv
pipeline/raw/room_occupancy_details.csv
pipeline/processed/vistabalayan_staging.sqlite
```

These files are local runtime artifacts and remain ignored by Git.

---

# 3. Historical Reference

An earlier local run recorded `2,397` visitor reports. That number is retained only as historical reference. The current verified run contains `2,400` visitor reports and is the result used for the Stage 1 handover decision.
