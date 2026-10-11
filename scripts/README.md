# ETL Runner Scripts

This folder contains helper scripts for the VistaBalayan batch ETL activity.

## Run CSV export extraction

1. Export the required Supabase/PostgreSQL tables as CSV files.
2. Place them in `data/raw/` using these names:
   - `establishments.csv`
   - `visitor_reports.csv`
   - `accommodation_reports.csv`
   - `room_occupancy_details.csv`
3. Run:

```bash
python3 scripts/extract_to_sqlite.py
```

The script writes:

- SQLite staging database: `data/processed/vistabalayan_staging.sqlite`
- JSON extraction log: `logs/extraction_run_YYYYMMDD_HHMMSS.json`

The script is read-only with respect to Supabase/PostgreSQL. It only reads local CSV exports.
