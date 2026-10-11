# VistaBalayan Tourism Data Analytics and Decision Support Pipeline

## Overview

This repository implements the **VistaBalayan Data Extraction Pipeline** for ETL/Lab 2 work.

The current milestone is **Stage 1: Data Extraction**. The pipeline extracts these four VistaBalayan tables:

- `establishments`
- `visitor_reports`
- `accommodation_reports`
- `room_occupancy_details`

The issue-required structure is included:

- `src/database.py` — connection loading and Supabase/PostgREST connection test.
- `src/extract.py` — batch extraction to CSV files.
- `main.py` — command-line pipeline runner.
- `requirements.txt` — Python/test dependencies.
- `.env.example` — local secret template.
- `documentation/data-extraction.md` — procedures and test results.

Generated CSV files, logs, SQLite files, and `.env` are ignored by Git.

---

## Windows setup

```powershell
cd C:\Users\banco\VistaBalayan_ETL_Pipeline
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install -r requirements.txt
```

If you are extracting directly from Supabase, create a private `.env` file:

```powershell
Copy-Item .env.example .env
notepad .env
```

Do not commit `.env`.

---

## Main commands

### Test Supabase connection

```powershell
py main.py test-connection
```

### Extract four source tables to CSV

```powershell
py main.py extract-csv
```

This creates:

```text
data/raw/establishments.csv
data/raw/visitor_reports.csv
data/raw/accommodation_reports.csv
data/raw/room_occupancy_details.csv
```

### Build SQLite staging database from CSV exports

```powershell
py main.py build-sqlite
```

This creates:

```text
data/processed/vistabalayan_staging.sqlite
```

The direct script also works:

```powershell
py scripts\extract_to_sqlite.py
```

### Validate metadata and relationships

```powershell
py main.py validate
```

The direct script also works:

```powershell
py scripts\validate_metadata.py
```

### Full direct pipeline

When `.env` is configured with valid Supabase values:

```powershell
py main.py all
```

---

## Local extraction result already verified

The current local CSV-to-SQLite extraction passed with these counts:

- `establishments`: 38
- `visitor_reports`: 2,397
- `accommodation_reports`: 1,857
- `room_occupancy_details`: 5,938

---

## Tests

```powershell
py -m pytest -q
```

Verified result:

```text
8 passed in 2.72s
```
