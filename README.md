# VistaBalayan Tourism Data Analytics and Decision Support Pipeline

## Overview

The **VistaBalayan Tourism Data Analytics and Decision Support Pipeline** is designed to collect, extract, validate, transform, process, and analyze tourism data from the VistaBalayan Tourism System.

The pipeline processes tourism records such as **establishment information, visitor reports, accommodation reports, and room occupancy details**. The source data is stored in the VistaBalayan **PostgreSQL database**, while **Python** is used to retrieve tourism records for batch processing.

The pipeline is organized into several stages:

```text
VistaBalayan Tourism System
          |
          v
   PostgreSQL Database
          |
          v
   1. Data Extraction
          |
          v
   2. Data Transformation
          |
          v
   3. Data Processing / Storage
          |
          v
   4. Data Analytics
          |
          v
   5. Reporting and Decision Support
```

> **Current Progress:** The project is currently at **Stage 1: Data Extraction**. The current work focuses on retrieving tourism records from the VistaBalayan PostgreSQL database and validating the extracted data before it proceeds to the succeeding stages.

---

## Pipeline Stages

### Stage 1 — Data Extraction

The Data Extraction stage retrieves tourism records from the VistaBalayan PostgreSQL database using Python batch processing.

The current extraction scope includes:

- `establishments`
- `visitor_reports`
- `accommodation_reports`
- `room_occupancy_details`

The extracted data undergoes initial validation to verify the source connection, required tables and columns, identifiers, relationships, record counts, and extraction status.

**Status:** 🟡 In Progress

**Documentation:** `documentation/data-extraction.md`

---

### Stage 2 — Data Transformation

The Data Transformation stage will process the extracted tourism data and prepare it for succeeding analytical operations.

Planned activities include:

- Data cleaning
- Data standardization
- Data type handling
- Data integration
- Data aggregation
- Validation of transformed records

**Status:** ⚪ Not Yet Started

---

### Stage 3 — Data Processing / Storage

The Data Processing / Storage stage will organize and store the transformed tourism data in the designated processed-data layer for succeeding analytics and reporting activities.

The specific processing and storage procedures will be documented as the pipeline progresses.

**Status:** ⚪ Not Yet Started

---

### Stage 4 — Data Analytics

The Data Analytics stage will analyze the processed tourism data to generate useful insights for tourism monitoring and planning.

Planned analytics may include:

- Visitor volume trends
- Accommodation performance summaries
- Room occupancy trends
- Establishment activity summaries
- Monthly or seasonal tourism patterns
- Comparative tourism indicators

**Status:** ⚪ Not Yet Started

---

### Stage 5 — Reporting and Decision Support

The Reporting and Decision Support stage will present the analyzed data in a format that can support tourism officers, LGU decision-makers, and stakeholders.

Planned outputs may include:

- Summary reports
- Decision-support indicators
- Tourism trend findings
- Extracted and validated data reports
- Recommendations based on analytics results

**Status:** ⚪ Not Yet Started

---

## Current Repository Structure

```text
VistaBalayan_ETL_Pipeline/
├── documentation/
│   ├── data-extraction.md
│   ├── extraction-results.md
│   └── logs/
│       └── .gitkeep
├── pipeline/
│   ├── raw/
│   │   └── .gitkeep
│   ├── processed/
│   │   └── .gitkeep
│   ├── __init__.py
│   ├── database.py
│   ├── extract.py
│   ├── pipeline_config.json
│   ├── staging.py
│   └── validate.py
├── main.py
├── README.md
├── requirements.txt
├── .env.example
└── .gitignore
```

---

## Important Files and Folders

- `main.py` — command-line runner for the pipeline.
- `pipeline/database.py` — loads connection settings and tests the database/Supabase connection.
- `pipeline/extract.py` — extracts source records into CSV files.
- `pipeline/staging.py` — builds a local SQLite staging database from extracted CSV files.
- `pipeline/validate.py` — validates metadata, required tables, columns, identifiers, and relationships.
- `pipeline/pipeline_config.json` — contains table, file, and relationship configuration.
- `pipeline/raw/` — local folder for extracted CSV files.
- `pipeline/processed/` — local folder for generated processed files such as SQLite output.
- `documentation/data-extraction.md` — Stage 1 extraction guide and procedure.
- `documentation/extraction-results.md` — recorded Stage 1 extraction and validation results.
- `documentation/logs/` — local folder for generated extraction and validation logs.
- `.env.example` — template for local environment variables.
- `requirements.txt` — setup compatibility file; Stage 1 currently uses only Python standard-library modules.

---

## Generated Files

The repository includes placeholder `.gitkeep` files so that empty runtime folders appear on GitHub.

The following files are generated locally and are ignored by Git:

```text
pipeline/raw/*.csv
pipeline/processed/*.sqlite
documentation/logs/*.json
documentation/logs/*.log
.env
.venv/
```

This keeps the repository clean while still allowing the pipeline to create local extraction outputs, processed files, and logs.

---

## Windows Setup

Create the virtual environment and install requirements once:

```powershell
cd C:\Users\banco\VistaBalayan_ETL_Pipeline
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install -r requirements.txt
```

After that, you do **not** need to recreate `.venv` or reinstall requirements every time.

For every new PowerShell or VS Code terminal, activate the existing environment:

```powershell
cd C:\Users\banco\VistaBalayan_ETL_Pipeline
.\.venv\Scripts\Activate.ps1
```

If the terminal prompt already shows `(.venv)`, the virtual environment is already activated.

---

## Environment Setup

If extracting directly from Supabase/PostgreSQL, create a private `.env` file from the example file:

```powershell
Copy-Item .env.example .env
notepad .env
```

Fill in the required local connection values inside `.env`.

> Do not commit `.env`. It is ignored by Git because it may contain private credentials.

---

## Main Commands

### Test Database Connection

```powershell
py main.py test-connection
```

### Extract Source Tables to CSV

```powershell
py main.py extract-csv
```

Expected CSV outputs:

```text
pipeline/raw/establishments.csv
pipeline/raw/visitor_reports.csv
pipeline/raw/accommodation_reports.csv
pipeline/raw/room_occupancy_details.csv
```

### Build SQLite Staging Database

```powershell
py main.py build-sqlite
```

Expected SQLite output:

```text
pipeline/processed/vistabalayan_staging.sqlite
```

### Validate Extracted Data

```powershell
py main.py validate
```

This checks the extracted data, table relationships, record counts, and validation metadata.

### Run the Full Direct Pipeline

When `.env` is configured with valid connection values:

```powershell
py main.py all
```

---

## Stage 1 Output Documentation

The extraction guide and recorded results are separated:

```text
documentation/data-extraction.md
documentation/extraction-results.md
```

- `documentation/data-extraction.md` explains the Stage 1 extraction process, scope, commands, and validation procedure.
- `documentation/extraction-results.md` records the completed local extraction and validation results.

---

## Current Stage 1 Status

The Stage 1 pipeline currently supports:

- Database connection testing
- Extraction of the four selected source tables
- CSV output generation
- SQLite staging database generation
- Metadata validation
- Relationship validation
- Local JSON log generation

Current validation result is recorded in:

```text
documentation/extraction-results.md
```

---

## Notes

- The project is currently focused only on **Stage 1: Data Extraction**.
- Stages 2 to 5 are planned for future development.
- Runtime outputs are generated locally and are not uploaded to GitHub.
- `requirements.txt` is intentionally kept for setup compatibility, even though Stage 1 currently uses only Python built-in modules.
