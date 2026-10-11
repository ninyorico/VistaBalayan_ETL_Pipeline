# VistaBalayan Tourism Data Analytics and Decision Support Pipeline

## Overview

This repository implements the **VistaBalayan Data Extraction Pipeline** for ETL/Lab 2 work.

The current milestone is **Stage 1: Data Extraction**. The pipeline extracts these four VistaBalayan tables:

- `establishments`
- `visitor_reports`
- `accommodation_reports`
- `room_occupancy_details`

Important Stage 1 code files:

- `pipeline/database.py` — connection loading and Supabase/PostgREST connection test.
- `pipeline/extract.py` — batch extraction to CSV files.
- `main.py` — command-line pipeline runner.
- `pipeline/staging.py` — CSV-to-SQLite staging builder.
- `pipeline/validate.py` — metadata and relationship validator.

Supporting Stage 1 files:

- `pipeline/pipeline_config.json` — table/file/relationship configuration.
- `requirements.txt` — setup compatibility file; Stage 1 code uses Python standard library only.
- `.env.example` — local secret template.
- `docs/extraction/data-extraction.md` — procedures and validation results.

Generated CSV files, logs, SQLite files, and `.env` are ignored by Git.

---

## Windows setup / daily start

Create the virtual environment and install requirements once:

```powershell
cd C:\Users\banco\VistaBalayan_ETL_Pipeline
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install -r requirements.txt
```

After that, you do **not** need to recreate `.venv` or reinstall requirements every time. In a new PowerShell window, just go to the project folder and activate the existing environment:

```powershell
cd C:\Users\banco\VistaBalayan_ETL_Pipeline
.\.venv\Scripts\Activate.ps1
```

Then run the pipeline commands below in that same activated PowerShell window.

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

The `pipeline/raw/` folder is included in the repository with a `.gitkeep` placeholder. Put or generate CSV files there:

```text
pipeline/raw/establishments.csv
pipeline/raw/visitor_reports.csv
pipeline/raw/accommodation_reports.csv
pipeline/raw/room_occupancy_details.csv
```

The CSV files are local data files and are ignored by Git.

### Build SQLite staging database from CSV exports

```powershell
py main.py build-sqlite
```

This creates:

```text
pipeline/processed/vistabalayan_staging.sqlite
```

### Validate metadata and relationships

```powershell
py main.py validate
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

## Validation

The latest local validation passed with:

```text
overall_status: PASS
```
