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
- `documentation/extraction/data-extraction.md` — Stage 1 extraction guide and command procedure.
- `documentation/extraction/extraction-results.md` — recorded local extraction and validation results.
- `documentation/extraction/logs/` — local generated extraction JSON/log output folder.
- `documentation/transformation/data-transformation.md` — Stage 2 transformation specification.

Generated CSV files, documentation logs, and SQLite files are ignored by Git.

**Stage 1 status:** Completed and approved for transformation based on the verified real-data extraction, staging, and validation run documented in `documentation/extraction/extraction-results.md`.

**Stage 2 status:** Documentation defined; implementation not started.

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

---

## Main commands

Place the exported CSV files inside `pipeline/raw/`:

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

---

## Local extraction result

The recorded extraction and validation outputs are kept separately from the guide:

```text
documentation/extraction/extraction-results.md
```
