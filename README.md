# VistaBalayan ETL Pipeline

Minimal **Stage 1 Data Extraction** project for VistaBalayan.

This version only keeps the files needed for the current workflow:

```text
CSV exports → SQLite staging database → metadata/relationship validation
```

## Required CSV files

Place these exported Supabase CSV files in `data/raw/`:

```text
data/raw/establishments.csv
data/raw/visitor_reports.csv
data/raw/accommodation_reports.csv
data/raw/room_occupancy_details.csv
```

The `data/raw/`, `data/processed/`, and `logs/` folders do not need to be committed. The program creates output folders when needed.

## Project files

```text
main.py
README.md
.gitignore
config/pipeline_config.json
src/staging.py
src/validate.py
```

## Run on Windows PowerShell

Build the SQLite staging database:

```powershell
py main.py build-sqlite
```

Validate the SQLite database:

```powershell
py main.py validate
```

## Outputs

```text
data/processed/vistabalayan_staging.sqlite
logs/extraction_run_YYYYMMDD_HHMMSS.json
logs/metadata_validation_YYYYMMDD_HHMMSS.json
```

## Verified result

The local Stage 1 extraction and validation previously passed with:

```text
overall_status: PASS
establishments: 38
visitor_reports: 2397
accommodation_reports: 1857
room_occupancy_details: 5938
```
