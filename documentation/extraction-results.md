# Stage 1: Extraction Results

## VistaBalayan Tourism Data Analytics and Decision Support Pipeline

This file records the local Stage 1 extraction and validation results separately from the extraction guide.

---

# 1. Recorded Historical Local Extraction Result

The following numbers are a historical local result recorded before the current clean checkout. They document the last known successful CSV-to-SQLite run, but the raw CSV inputs and source-run metadata are not committed to this repository:

```json
{
  "overall_status": "PASS",
  "sqlite_output": "C:\\Users\\banco\\VistaBalayan_ETL_Pipeline\\pipeline\\processed\\vistabalayan_staging.sqlite",
  "tables": {
    "establishments": 38,
    "visitor_reports": 2397,
    "accommodation_reports": 1857,
    "room_occupancy_details": 5938
  }
}
```

This confirms that the earlier local CSV-to-SQLite extraction step loaded all four Stage 1 source tables. It does not by itself approve the current checkout for Transformation.

---

# 2. Historical Validation Results

The local Stage 1 metadata validation completed successfully:

```text
overall_status: PASS
```

Validated table counts:

- `establishments`: 38
- `visitor_reports`: 2,397
- `accommodation_reports`: 1,857
- `room_occupancy_details`: 5,938

Relationship checks passed with `missing_parent_count: 0` for:

- `visitor_reports.establishment_id` → `establishments.id`
- `accommodation_reports.establishment_id` → `establishments.id`
- `room_occupancy_details.accommodation_report_id` → `accommodation_reports.id`

The command entry point was also checked with:

```text
python3 main.py --help
```

---

# 3. Current Checkout Status

The current repository intentionally excludes raw CSV exports, generated SQLite files, and operational JSON logs. Therefore, a fresh Stage 1 validation cannot be reproduced from Git alone until one of the following is supplied locally:

- a new direct Supabase extraction using a private `.env`; or
- the four raw CSV exports placed in `pipeline/raw/`.

Until that run completes and its output is recorded here, the current decision remains:

```text
Stage 1: IN PROGRESS
Transformation handover: NOT APPROVED
```
