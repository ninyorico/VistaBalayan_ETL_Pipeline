# Stage 1: Data Extraction Documentation

## VistaBalayan Tourism Data Analytics and Decision Support Pipeline

## Objective

The objective of the extraction stage is to retrieve tourism data from the VistaBalayan source system and prepare a documented, traceable, and validated dataset for the succeeding Transformation Stage.

The VistaBalayan pipeline processes tourism records including visitor reports, accommodation reports, room occupancy details, and establishment information. PostgreSQL/Supabase serves as the primary structured data storage, while Python retrieves tourism records through batch extraction.

---

# 1. Stage 1 Implementation Scope

This repository focuses on **Stage 1: Data Extraction** only.

## 1.1 Important Stage 1 code files

- `src/database.py` — Supabase/PostgREST connection loading and connection test.
- `src/extract.py` — batch extraction logic that saves source tables as CSV files.
- `main.py` — command-line entry point for connection test, CSV extraction, SQLite build, and validation.
- `src/staging.py` — local CSV-to-SQLite staging builder.
- `src/validate.py` — metadata, count, column, date, primary-key, and relationship validator.

Supporting files for setup, documentation, and safe repository use:

- `config/pipeline_config.json` — Stage 1 table/file/relationship configuration.
- `requirements.txt` — setup compatibility file; Stage 1 code uses Python standard library only.
- `.env.example` — template for private local connection values.
- `.gitignore` — excludes `.env`, virtual environments, logs, raw CSV exports, and generated SQLite files.
- `documentation/data-extraction.md` — Stage 1 extraction procedure and validation results.

## 1.2 Stage 1 checklist mapping

- Create project folder and virtual environment: repository structure supports `.venv/` and Windows `py -m venv .venv`.
- Install dependencies and create `requirements.txt`: `requirements.txt` is present.
- Set up `.env` and `.gitignore`: `.env.example` is present and `.env` is ignored.
- Create `src/database.py` and test the connection: `main.py test-connection` uses `src/database.py`.
- Create `src/extract.py`: implemented with batch CSV export helpers.
- Extract all four tables in batches and save as CSV files: `main.py extract-csv` exports the four configured tables.
- Configure `main.py`: implemented with subcommands.
- Run extraction and handle errors: extraction logs table-level failures in `logs/csv_extraction_*.json`.
- Check CSV files, record counts, columns, and relationships: SQLite build and metadata validation commands perform these checks.
- Fix discrepancies: validation output lists `failed_checks` and `warning_checks` for correction.
- Create `documentation/data-extraction.md`: this file documents the extraction procedure.
- Record procedures and validation results: see Sections 6 and 7.
- Review files and exclude sensitive data: `.gitignore` excludes secrets and generated data.
- Commit and push the Stage 1 extraction implementation.

---

# 2. Data Source and Extraction Specifications

## 2.1 Source System

**Source System:** VistaBalayan System

**Purpose:** The VistaBalayan system collects and manages tourism information submitted by participating tourist establishments. Establishment staff encode and submit tourism records, which are stored in the database and used for monitoring, reporting, analytics, dashboards, and decision-support functions.

The source records include:

- Establishment information
- Visitor reports
- Accommodation reports
- Room occupancy details

## 2.2 Source Database or File

**Database Management System:** PostgreSQL/Supabase

**Source Database:** VistaBalayan PostgreSQL Database

**Intermediate File Format:** CSV

**Local Staging Format:** SQLite

PostgreSQL/Supabase is used as the primary database for structured tourism information. The extraction layer can pull records from Supabase through PostgREST into CSV files, then build a local SQLite staging database for safe Lab 2 metadata work without committing or exposing credentials.

## 2.3 Extraction Method

**Extraction Type:** Batch Extraction

**Extraction Tool:** Python

Python retrieves tourism records from the source system in batches and saves the extracted tables as CSV files.

```text
VistaBalayan PostgreSQL/Supabase
              |
              v
       src/database.py
              |
              v
        src/extract.py
              |
              v
         data/raw/*.csv
              |
              v
      src/staging.py
              |
              v
 data/processed/vistabalayan_staging.sqlite
              |
              v
      src/validate.py
```

## 2.4 Extraction Schedule

The pipeline is designed for daily batch processing, with weekly or monthly aggregation when required. Manual Lab 2 runs are executed from the command line.

## 2.5 Extraction Scope

The extraction includes these source tables:

- `establishments` — tourism establishment information.
- `visitor_reports` — visitor counts and visitor-origin information.
- `accommodation_reports` — accommodation and guest statistics.
- `room_occupancy_details` — room-level occupancy information.

## 2.6 Source Limitations and Assumptions

1. Tourism records must exist in PostgreSQL/Supabase before extraction begins.
2. A local `.env` file is required only when extracting directly from Supabase.
3. Raw CSV exports may also be placed manually in `data/raw/` for offline Lab 2 processing.
4. Required source tables and columns must exist.
5. Generated raw CSV files, logs, SQLite files, and credentials are excluded from Git.
6. Unexpected database schema changes may cause extraction validation to fail.
7. Database connectivity problems may interrupt direct Supabase extraction.

---

# 3. Source Tables and Relationships

## 3.1 `establishments`

Purpose: contains information identifying and classifying tourism establishments.

Important columns:

- `id` — primary key.
- `name` — establishment name.
- `type` — establishment classification.
- `status` — active/inactive status.
- `created_at`, `updated_at` — metadata timestamps when present.

## 3.2 `visitor_reports`

Purpose: contains visitor information submitted by tourism establishments.

Important columns:

- `id` — primary key.
- `establishment_id` — foreign key to `establishments.id`.
- `report_date` — date covered by the report.
- `status` — report approval/review status.
- Visitor count/origin columns when present in the export.

## 3.3 `accommodation_reports`

Purpose: contains accommodation-related tourism statistics.

Important columns:

- `id` — primary key.
- `establishment_id` — foreign key to `establishments.id`.
- `report_date` — date covered by the report.
- `status` — report approval/review status.
- Accommodation metrics when present in the export.

## 3.4 `room_occupancy_details`

Purpose: provides detailed room-level accommodation information.

Important columns:

- `id` — primary key.
- `accommodation_report_id` — foreign key to `accommodation_reports.id`.
- Room, occupancy, check-in, or guest-night fields when present in the export.

## 3.5 Source Relationships

- `establishments.id` → `visitor_reports.establishment_id`
- `establishments.id` → `accommodation_reports.establishment_id`
- `accommodation_reports.id` → `room_occupancy_details.accommodation_report_id`

---

# 4. Validation and Data Quality Checks

The extraction stage verifies that data was successfully retrieved from the source. Cleaning, standardization, and business transformations belong to later stages.

Validation checks include:

- Source connection check.
- Required table/file existence.
- Required column presence.
- Primary-key blank checks.
- Primary-key duplicate checks.
- Record counts per table.
- Date parseability for configured date columns.
- Foreign-key relationship checks.
- Extraction status and log generation.

Validation result categories:

- **PASS** — critical extraction requirements are satisfied.
- **WARNING** — extraction completed but a non-critical condition needs review.
- **FAIL** — a critical requirement failed.

---

# 5. Command Procedure

## 5.1 Windows setup

```powershell
cd C:\Users\banco\VistaBalayan_ETL_Pipeline
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install -r requirements.txt
```

If using direct Supabase extraction, create `.env` from the template:

```powershell
Copy-Item .env.example .env
notepad .env
```

Do not commit `.env`.

## 5.2 Test source connection

```powershell
py main.py test-connection
```

This uses `src/database.py` and reads connection values from `.env`.

## 5.3 Extract all four source tables to CSV

```powershell
py main.py extract-csv
```

Expected CSV outputs:

- `data/raw/establishments.csv`
- `data/raw/visitor_reports.csv`
- `data/raw/accommodation_reports.csv`
- `data/raw/room_occupancy_details.csv`

## 5.4 Build local SQLite staging database

If CSV files already exist in `data/raw/`, run:

```powershell
py main.py build-sqlite
```

This writes:

```text
data/processed/vistabalayan_staging.sqlite
```

## 5.5 Validate metadata and relationships

```powershell
py main.py validate
```

## 5.6 Run full direct pipeline

When `.env` has valid Supabase values:

```powershell
py main.py all
```

---

# 6. Recorded Local Extraction Result

The user's successful local extraction produced:

```json
{
  "overall_status": "PASS",
  "sqlite_output": "C:\\Users\\banco\\VistaBalayan_ETL_Pipeline\\data\\processed\\vistabalayan_staging.sqlite",
  "tables": {
    "establishments": 38,
    "visitor_reports": 2397,
    "accommodation_reports": 1857,
    "room_occupancy_details": 5938
  }
}
```

This confirms that the local CSV-to-SQLite extraction step successfully loaded all four Stage 1 source tables.

---

# 7. Validation Results

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

# 8. Sensitive Data Review

The repository excludes:

- `.env`
- `.env.*` except `.env.example`
- `.venv/` and `venv/`
- `__pycache__/`
- `.pytest_cache/`
- `data/raw/*.csv`
- `data/processed/*.sqlite`
- `data/processed/*.db`
- `logs/*.json`
- `logs/*.log`

Only Stage 1 code, configuration templates, and documentation should be committed.
