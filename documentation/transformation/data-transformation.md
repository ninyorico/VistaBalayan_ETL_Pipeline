# Stage 2: Data Transformation Documentation

## VistaBalayan Tourism Data Analytics and Decision Support Pipeline

## Objective

The objective of Stage 2 is to receive the validated VistaBalayan data handed over from Stage 1 and produce cleaned, standardized, traceable, and business-ready datasets for the Load Stage.

Stage 2 does not re-extract data from Supabase, modify the source database, or load transformed records into a target database. It works from the approved Stage 1 handover and preserves the original extracted files.

All Stage 2 documentation is written in Markdown.

---

# 1. Transformation Input and Processing Specification

## 1.1 Input Source

The Transformation Stage receives the four validated Stage 1 CSV exports and the local SQLite staging database:

| Stage 1 handover output | Use in Stage 2 |
|---|---|
| `pipeline/raw/establishments.csv` | Establishment reference and classification data |
| `pipeline/raw/visitor_reports.csv` | Visitor-report facts and report-period data |
| `pipeline/raw/accommodation_reports.csv` | Accommodation-report facts and report-period data |
| `pipeline/raw/room_occupancy_details.csv` | Room-level details related to accommodation reports |
| `pipeline/processed/vistabalayan_staging.sqlite` | Local relational staging and read-only transformation input |

The verified Stage 1 handover contains 38 establishments, 2,400 visitor reports, 1,857 accommodation reports, and 5,938 room occupancy details. The transformation run must reference the actual extraction run identifier and batch metadata when those values are available in the local run log. No credential, Supabase URL, access token, or private `.env` value may be copied into transformation logs.

## 1.2 Batch Processing Method

The initial implementation will use Python and the existing local SQLite staging layer. The current repository uses Python standard-library components for Stage 1; a Pandas dependency may be introduced only if the implementation issue explicitly approves it. The transformation design does not require a new database connection.

A transformation batch is the complete set of validated records received from one approved Stage 1 handover, or a documented report-date window when a later implementation supports windowed processing. The batch will process parent/reference data before child/fact data:

1. `establishments`
2. `visitor_reports` and `accommodation_reports`
3. `room_occupancy_details`
4. transformed outputs, quarantine records, and validation metadata

The first implementation is manually triggered after Stage 1 approval. A scheduler is not included in this repository. A failed batch must preserve its input, record the failure, and be rerunnable after correction. The transformation must be idempotent: rerunning the same `run_id` and input handover must replace or deterministically reproduce the same local output rather than append duplicate transformed records.

## 1.3 Transformation Scope

| Input dataset | Transformation scope |
|---|---|
| `establishments` | Normalize identifiers and text, validate establishment type/status, preserve active/inactive meaning, and produce a standardized establishment reference dataset. |
| `visitor_reports` | Normalize identifiers and report dates/status values, validate numeric visitor fields when present, preserve establishment linkage, and produce standardized visitor-report facts. |
| `accommodation_reports` | Normalize identifiers and report dates/status values, validate accommodation metrics when present, preserve establishment linkage, and produce standardized accommodation-report facts. |
| `room_occupancy_details` | Normalize identifiers and room-level fields when present, validate numeric occupancy values, preserve the accommodation-report relationship, and produce standardized room-detail facts. |

Common transformation activities include column-name normalization to lowercase `snake_case`, whitespace cleanup, type conversion, missing-value classification, duplicate detection, date normalization, relationship preservation, and controlled quarantine of records that cannot be safely transformed.

The original Stage 1 CSV files and SQLite staging database are never modified. Every retained, modified, rejected, and quarantined record is counted.

## 1.4 Dependencies and Assumptions

- Stage 1 has completed and is approved for transformation.
- The four input files and/or the approved SQLite staging database are available locally.
- The Stage 1 primary keys and foreign keys remain available for lineage and joins.
- Source columns not present in an export are not fabricated and are not treated as null-filled business data without an approved rule.
- The current source relationship is `establishments` → `visitor_reports`, `establishments` → `accommodation_reports`, and `accommodation_reports` → `room_occupancy_details`.
- Visitor and accommodation report families remain separate because they represent different reporting forms and must not be combined merely because they share an establishment.
- Room details are joined to accommodation reports only through `accommodation_report_id`; no name-based relationship is allowed.
- Transformation output is prepared for Load but is not loaded into Supabase or another target database in Stage 2.

---

# 2. Data Profiling and Issue Identification

Profiling must run before cleaning rules are applied. The implementation will calculate counts and percentages from the actual Stage 1 handover; the table below defines the issues to investigate and must be updated with confirmed results during execution.

## 2.1 Potential Data Quality Issues

| Dataset and column | Issue type | Example to check | Affected records | Planned treatment |
|---|---|---|---:|---|
| All configured tables: column names | Inconsistent naming | `Report Date`, `reportDate`, or `report_date` | To be measured | Apply `C-01` and record the source-to-target mapping. |
| All configured tables: identifiers | Missing or blank identifiers | Empty `id`, `establishment_id`, or `accommodation_report_id` | To be measured | Quarantine when the identifier is required for lineage (`C-02`). |
| All configured tables: primary keys | Duplicate identifiers | Repeated `id` values | To be measured | Compare records; retain only a verifiable canonical record or quarantine unresolved duplicates (`C-03`). |
| Establishments: `name`, `type`, `status` | Whitespace or inconsistent categories | ` Active ` versus `active` | To be measured | Trim and map approved status/type values (`C-04`, `S-02`). |
| Visitor reports: `report_date` | Invalid or mixed date format | Unparseable date or timestamp | To be measured | Convert valid values to ISO date; quarantine invalid values (`C-05`, `S-03`). |
| Accommodation reports: `report_date` | Invalid or mixed date format | Missing or invalid reporting day | To be measured | Convert valid values; quarantine invalid required dates (`C-05`, `S-03`). |
| Visitor/accommodation metrics | Invalid numeric values | Negative counts, text in count fields, or non-integer values | To be measured | Convert valid values and quarantine unrecoverable values (`C-06`). |
| Room occupancy details | Invalid occupancy values | Negative rooms or occupied rooms above available rooms | To be measured | Apply hard business checks and quarantine impossible records (`C-07`). |
| Child relationship columns | Orphan records | Report references an absent establishment or room detail references an absent accommodation report | To be measured | Quarantine the child record and preserve the reason (`C-08`). |
| Report status fields | Unknown status values | A value outside the approved status vocabulary | To be measured | Preserve the raw value, map only approved aliases, and send unresolved values to review (`S-02`). |

## 2.2 Profiling Procedure

1. Confirm the handover files and schema before processing.
2. Count records, nulls, blank strings, whitespace-only values, and duplicate identifiers per dataset.
3. Inspect date parseability and report-date ranges.
4. Inspect numeric fields that are actually present; do not assume every metric column exists in every export.
5. Check parent-child relationships against the staged reference tables.
6. Profile status and type vocabularies without changing values.
7. Check whether a join would multiply rows unexpectedly.
8. Record samples without placing full sensitive rows in logs.
9. Record the actual affected counts, percentages, rule IDs, and treatment decision.

## 2.3 Profiling Results and Issue Tracking

Potential issues must be replaced or supplemented with actual results after the profiling command runs. An issue not found must be recorded as zero detected occurrences. Newly discovered issues must receive a rule ID before cleaning proceeds. No record may be silently discarded.

---

# 3. Data Cleaning Rules

## 3.1 Data Cleaning Overview

Cleaning operates on copies of the Stage 1 handover. Valid records are retained, safely correctable records are modified and counted, and records that cannot be processed reliably are placed in a quarantine output with a rule ID and reason.

## 3.2 Data Cleaning Rules

| Rule ID and name | Target | Condition | Action | Justification |
|---|---|---|---|---|
| `C-01` Whitespace and column cleanup | All datasets and text columns | Leading/trailing whitespace or non-standard source column labels | Trim text values and map column labels to documented names. Do not trim inside meaningful names unless the rule is approved. | Prevents false mismatches while preserving source meaning. |
| `C-02` Required identifier handling | `id`, `establishment_id`, `accommodation_report_id` | Required identifier is null, blank, or malformed | Retain only when lineage remains reliable; otherwise quarantine and log the record. Never invent a UUID. | Prevents untraceable output and fabricated relationships. |
| `C-03` Duplicate identifier handling | Primary-key columns | Multiple rows share a configured primary key | Compare the complete available records. Retain a canonical row only when the selection is verifiable; otherwise quarantine the unresolved duplicate group. | Prevents inflated counts without silently deleting evidence. |
| `C-04` Text/category normalization | Establishment names, types, statuses, and report statuses | Case, whitespace, or approved alias differences | Trim values and map only documented aliases to canonical values. Preserve the original value in lineage or quarantine metadata when changed. | Supports consistent grouping without changing unknown business values. |
| `C-05` Date validation | `report_date` and available timestamp/date columns | Mixed, invalid, or missing date values | Parse valid values and output ISO `YYYY-MM-DD` dates. Quarantine invalid required dates; do not infer a date from a filename. | Ensures reliable period filtering and reporting. |
| `C-06` Numeric validation | Visitor, accommodation, and room metrics when present | Non-numeric, fractional integer, negative, or otherwise invalid values | Convert valid values to the documented numeric type. Quarantine values that cannot be safely corrected. | Prevents invalid measures from entering analysis. |
| `C-07` Occupancy consistency | Accommodation and room occupancy measures when present | Occupied rooms exceed available rooms or a value is negative | Preserve the source row in quarantine and record the failed business condition. Do not silently cap the value. | Prevents distorted occupancy calculations. |
| `C-08` Orphan relationship handling | Child foreign keys | A child references no staged parent | Quarantine the child row with the missing parent key and relationship name. | Maintains referential integrity and supports investigation. |
| `C-09` Invalid character handling | Applicable text fields | Control or invalid characters prevent reliable parsing | Remove or correct only when the intended value is unambiguous; otherwise quarantine. | Avoids corrupting legitimate establishment or report text. |

## 3.3 Missing Values and Duplicate Handling

No arbitrary identifiers, dates, counts, or status values will be inserted. Missing non-required descriptive values may remain null when the output contract permits them. Missing required identifiers, dates, or relationship keys are quarantined unless a documented source mapping resolves them.

Duplicate records are not removed solely because they look similar. The implementation must use the configured key and available source metadata. If a canonical record cannot be established, all unresolved duplicates remain available in quarantine with the duplicate group and reason.

## 3.4 Quarantine Output

The quarantine output will contain at least:

| Field | Purpose |
|---|---|
| `run_id` | Transformation run that identified the issue |
| `batch_id` | Input batch being processed |
| `source_dataset` | Source table/file name |
| `source_record_key` | Available source identifier |
| `original_record` | Minimal serialized original values needed for review |
| `rule_id` | Cleaning or validation rule that failed |
| `quarantine_reason` | Human-readable reason |
| `quarantined_at` | ISO 8601 timestamp |

Full raw rows and credentials must not be copied into operational logs unnecessarily.

---

# 4. Standardization and Data Type Rules

## 4.1 Standardization Overview

The standardized output uses stable lowercase `snake_case` names, explicit types, ISO date formats, preserved source identifiers, and documented canonical categories. Conversion failures follow the cleaning and quarantine rules rather than being coerced into misleading values.

## 4.2 Data Type and Format Rules

| Rule ID and name | Target fields | Standard format/type | On conversion failure |
|---|---|---|---|
| `S-01` Column names | All output columns | Lowercase `snake_case` | Stop schema mapping if a required field cannot be mapped; record the mismatch. |
| `S-02` Text and controlled values | Names, types, statuses, and descriptive fields | UTF-8 text; approved categories use documented canonical spelling | Preserve unknown values and flag for review; do not invent a category. |
| `S-03` Dates and timestamps | `report_date` and available date fields | Dates as `YYYY-MM-DD`; timestamps as ISO 8601 with timezone policy documented by implementation | Quarantine invalid required dates. |
| `S-04` Identifier fields | `id`, `establishment_id`, `accommodation_report_id` | Non-empty source identifiers preserved as strings/UUID text | Quarantine missing or malformed identifiers. |
| `S-05` Count measures | Visitor, room, occupancy, and guest count fields when present | Integer, non-negative unless an approved source rule states otherwise | Quarantine non-convertible or impossible values. |
| `S-06` Decimal measures | Monetary or decimal fields if present in a future source export | Decimal with precision defined by the approved output contract | Reject and log values that cannot be converted; do not use binary floating-point rounding for persisted currency. |

## 4.3 Source-to-Standardized Mapping

| Source dataset | Source field | Standardized field | Target type | Transformation |
|---|---|---|---|---|
| `establishments` | `id` | `establishment_id` | String/UUID text | Preserve identifier and validate presence. |
| `establishments` | `name` | `establishment_name` | Text | Trim whitespace; preserve meaning. |
| `establishments` | `type` | `establishment_type` | Text | Trim and map approved aliases only. |
| `establishments` | `status` | `establishment_status` | Text | Trim and map approved status aliases only. |
| `visitor_reports` | `id` | `visitor_report_id` | String/UUID text | Preserve identifier and validate uniqueness. |
| `visitor_reports` | `establishment_id` | `establishment_id` | String/UUID text | Preserve the relationship key. |
| `visitor_reports` | `report_date` | `report_date` | ISO date | Parse and standardize. |
| `visitor_reports` | `status` | `report_status` | Text | Preserve or map approved values. |
| `accommodation_reports` | `id` | `accommodation_report_id` | String/UUID text | Preserve identifier and validate uniqueness. |
| `accommodation_reports` | `establishment_id` | `establishment_id` | String/UUID text | Preserve the relationship key. |
| `accommodation_reports` | `report_date` | `report_date` | ISO date | Parse and standardize. |
| `accommodation_reports` | `status` | `report_status` | Text | Preserve or map approved values. |
| `room_occupancy_details` | `id` | `room_occupancy_detail_id` | String/UUID text | Preserve identifier and validate uniqueness. |
| `room_occupancy_details` | `accommodation_report_id` | `accommodation_report_id` | String/UUID text | Preserve the relationship key. |

Additional source columns are carried forward only after profiling confirms their actual names and types. No field is fabricated because it appears in a planning example.

## 4.4 Conversion Failure Handling

Missing required columns, incompatible schema changes, or unmappable identifiers stop the affected transformation batch. Row-level conversion failures are quarantined when the rest of the dataset can be safely processed. Every failure is counted and included in the transformation metadata.

---

# 5. Business Transformation Rules

## 5.1 Business Transformation Overview

Business transformations create consistent downstream datasets without introducing unsupported tourism metrics. Source relationships and report families remain identifiable. Any new derived measure must be approved against the actual source fields before implementation.

## 5.2 Business Transformation Rules

| Rule ID and name | Input columns | Logic | Output | Business reason |
|---|---|---|---|---|
| `B-01` Establishment reference preparation | Establishment identifier, name, type, status | Clean and standardize the establishment reference while preserving the source key. | `dim_establishment`-style standardized reference output | Provides a stable parent reference for downstream reports. |
| `B-02` Visitor report preparation | Visitor report key, establishment key, report date, status, available measures | Standardize the report row and retain its establishment and period lineage. | `fact_visitor_report`-style output | Supports visitor monitoring without losing source identity. |
| `B-03` Accommodation report preparation | Accommodation report key, establishment key, report date, status, available measures | Standardize the report row and retain its establishment and period lineage. | `fact_accommodation_report`-style output | Supports accommodation reporting and later occupancy analysis. |
| `B-04` Room-detail integration | Room detail key, accommodation report key, available room measures | Join room details to accommodation reports on the validated report key only. | `fact_room_occupancy_detail`-style output | Preserves room-level detail and prevents name-based misattribution. |
| `B-05` Reporting-period derivation | Valid `report_date` | Derive `report_year` and `report_month` only from a valid report date. | Period attributes in report outputs | Supports period-based analytics without changing the source date. |
| `B-06` Output preparation | All accepted transformed outputs | Package datasets, quarantine records, counts, rules, and validation results with linked run metadata. | Load handover package | Makes the next stage auditable and repeatable. |

## 5.3 Joins, Aggregations, and Filtering

- Establishments are the parent reference for visitor and accommodation reports.
- Room details join to accommodation reports using `accommodation_report_id`.
- Joins must be validated for one-to-many cardinality and must not multiply report rows unexpectedly.
- Visitor reports and accommodation reports are not unioned into one fact table unless a later approved contract defines the common schema.
- No tourism record is excluded solely because it is pending or inactive unless an approved business rule explicitly requires that filter. If filtering is approved, excluded counts and reasons are logged.
- Aggregations are not applied in the first transformation implementation unless the required measures and reporting grain are confirmed from the actual exports. Load-stage storage and analytics calculations remain out of scope.

---

# 6. Transformed Data Contract and Naming Convention

## 6.1 Required Output Schema

The initial transformed handover will contain standardized datasets with source lineage preserved:

| Output dataset | Required output columns | Key/relationship |
|---|---|---|
| `establishments_transformed` | `establishment_id`, `establishment_name`, `establishment_type`, `establishment_status` | `establishment_id` unique candidate key |
| `visitor_reports_transformed` | `visitor_report_id`, `establishment_id`, `report_date`, `report_status`, plus profiled source measures | `visitor_report_id` unique; `establishment_id` references establishments |
| `accommodation_reports_transformed` | `accommodation_report_id`, `establishment_id`, `report_date`, `report_status`, plus profiled source measures | `accommodation_report_id` unique; `establishment_id` references establishments |
| `room_occupancy_details_transformed` | `room_occupancy_detail_id`, `accommodation_report_id`, plus profiled room measures | `room_occupancy_detail_id` unique; `accommodation_report_id` references accommodation reports |
| `transformation_quarantine` | `run_id`, `batch_id`, `source_dataset`, `source_record_key`, `rule_id`, `quarantine_reason`, `original_record`, `quarantined_at` | Review output, not a loadable fact dataset |

The exact additional measure columns are finalized from the actual Stage 1 schema during implementation. Surrogate keys are not introduced unless the Load-stage contract requires them.

## 6.2 Naming Convention

- Dataset and table names use lowercase `snake_case`.
- Dimension-like reference output uses a `dim_` prefix only when the Load-stage design approves dimensional modeling.
- Report outputs use descriptive names and retain source identifiers.
- Foreign-key names identify the referenced entity, such as `establishment_id` and `accommodation_report_id`.
- Derived period fields use `report_year` and `report_month`.
- Source identifiers are never replaced by arbitrary generated values.

## 6.3 Source-to-Target Mapping

Every output column must have one of these mappings: direct source preservation, documented rename, validated type conversion, or approved derived calculation. The transformation metadata must record the rule IDs applied to each dataset.

## 6.4 Schema Consistency

The transformation checks required columns before processing. Added, removed, or renamed source columns cause a schema-review result. Safely mappable changes may proceed only after the mapping is recorded. Incompatible changes stop the batch rather than silently producing an incomplete output.

---

# 7. Transformation Validation and Data Quality Checks

Transformation validation verifies the correctness and integrity of transformed outputs. It does not repeat Stage 1 connection or extraction-execution checks.

| Check ID and name | Target | Purpose | Pass criteria | Severity |
|---|---|---|---|---|
| `V-01` Record reconciliation | Each row-level dataset | Detect lost or unaccounted records | `records_read = records_output + records_rejected`; modified retained rows remain in output | Critical |
| `V-02` Required output fields | All transformed datasets | Ensure required lineage fields remain available | Required identifiers and dates are not null in accepted output | Critical |
| `V-03` Key uniqueness | All configured output keys | Prevent duplicate transformed records | Duplicate count is zero after approved handling | Critical |
| `V-04` Type and format conformance | Dates, identifiers, numeric fields | Confirm output contract | All accepted values match target types and formats | Critical |
| `V-05` Referential integrity | Report and room-detail relationships | Prevent orphan outputs | 100% of accepted child keys match their parent output | Critical |
| `V-06` Join cardinality | Report/detail joins | Prevent row multiplication | Join produces the documented one-to-many relationship and no unexpected duplicate parent rows | Critical |
| `V-07` Business-value checks | Numeric occupancy and count measures when present | Detect impossible values | No accepted negative counts or impossible occupancy relationships | Critical |
| `V-08` Status/category review | Controlled text values | Detect unapproved values | Values are mapped, explicitly preserved for review, or quarantined | Non-critical or critical depending on field |
| `V-09` Quarantine accounting | Rejected records | Ensure failures are traceable | Every rejected row has a dataset, rule ID, reason, and batch ID | Critical |
| `V-10` Transformation status | Entire batch | Determine handover readiness | No unresolved critical failures and all required results recorded | Critical |

## 7.1 Reconciliation Rules

For row-level cleaning:

```text
records_read = records_output + records_rejected
```

`records_modified` is tracked separately because a modified and retained row remains part of `records_output`. For joins and derived outputs, the pipeline also reconciles contributing input records, measure totals where applicable, unmatched records, and unexpected row multiplication. Filtered records are counted with the documented exclusion reason.

## 7.2 Validation Result Categories

- `PASS`: the check satisfies its criteria.
- `WARNING`: a non-critical issue is documented for review.
- `FAIL`: a critical condition is not satisfied and the batch cannot be handed over automatically.

---

# 8. Transformation Metadata and Log Specification

## 8.1 Required Metadata Fields

| Field | Purpose | Example |
|---|---|---|
| `run_id` | Identifies the transformation run | `TRN_20261018_0800` |
| `parent_run_id` | Links to the Stage 1 extraction run | `EXT_<verified_run_id>` |
| `batch_id` | Identifies the processed input batch | `BATCH_20261018_01` |
| `batch_window` | Records the report-date range when applicable | `2026-10-01 to 2026-10-17` |
| `dataset_name` | Identifies the transformed dataset | `visitor_reports` |
| `start_timestamp` | Transformation start time | ISO 8601 timestamp |
| `end_timestamp` | Transformation end time | ISO 8601 timestamp |
| `status` | Batch result | `SUCCESS`, `WARNING`, or `FAILED` |
| `records_read` | Input records received | Integer |
| `records_output` | Accepted transformed records | Integer |
| `records_rejected` | Quarantined/rejected records | Integer |
| `records_modified` | Accepted records changed by rules | Integer |
| `rules_applied` | Rule IDs and affected counts | `C-01: 25; S-03: 10` |
| `validation_results` | Per-check outcomes | JSON or structured text |
| `error_code` / `error_message` | Failure information | Code and safe description |
| `duration_seconds` | Processing duration | Decimal/integer seconds |
| `code_version` / `rules_version` | Reproducibility identifier | Git commit or rules version |

The `parent_run_id` references Stage 1 metadata rather than duplicating secrets or the full extraction log.

## 8.2 Logging and Monitoring

Transformation logs support monitoring, troubleshooting, auditing, lineage, and recovery. Logs must identify the affected dataset, rule, counts, validation results, and safe error details. They must not contain `.env` contents, API keys, passwords, or unnecessary full sensitive source records.

---

# 9. Log Retention, Rejected Data, and Access

| Requirement | Specification |
|---|---|
| Transformation log retention | At least 30 days, and longer when required for an active investigation or audit. |
| Transformation log location | Project-controlled transformation log storage, such as `documentation/transformation/logs/` for local development output. |
| Quarantine location | A transformation quarantine file/table under the controlled transformation output area. |
| Quarantine retention | At least 30 days and longer while review, recovery, or audit is active. |
| Read access | Authorized ETL developers, data reviewers, and project administrators. |
| Write access | The transformation process and authorized maintainers. |
| Delete access | Designated project administrators through an approved retention process. |
| Archiving | Required for records needed beyond operational retention. |
| Deletion | Prohibited before the retention period ends or while records are needed for troubleshooting, auditing, or recovery. |

Extraction logs and transformation logs have different ownership and purposes. Extraction logs describe source retrieval and staging. Transformation logs describe cleaning, conversion, quarantine, and output validation. The original extracted data remains unchanged.

---

# 10. Transformation Acceptance and Handover Rules

## 10.1 Acceptance Threshold

The initial rejection-rate threshold is **1%**, subject to project approval before the first implementation run. The rate is calculated as:

```text
Rejection Rate (%) = (records_rejected / records_read) × 100
```

A batch with zero input records is not automatically approved; it requires investigation.

## 10.2 Acceptance Rules

| Rule ID | Condition | Acceptance criteria | Pipeline action | Decision | Responsible role |
|---|---|---|---|---|---|
| `A-01` Automatic approval | All critical checks pass, reconciliation succeeds, and rejection rate is at or below 1% | No unresolved critical failures | Package outputs for Load | Automatic | ETL pipeline |
| `A-02` Manual review | Non-critical warnings exist or rejection rate exceeds 1% without a critical failure | Issue, count, and impact are documented | Hold output pending review | Manual | ETL reviewer/project owner |
| `A-03` Rejected/failed batch | Critical validation fails, schema is incompatible, or reconciliation fails | Critical issue is unresolved | Stop handover; correct and rerun using the same input | Automatic stop with review | ETL pipeline and reviewer |
| `A-04` Load handover | Batch is approved | Outputs, quarantine summary, metadata, and validation results are complete | Transfer package to Load stage without loading it | After approval | ETL pipeline |

## 10.3 Overall Decision

| Overall condition | Decision | Action |
|---|---|---|
| All critical checks pass and rejection rate is within threshold | `APPROVED` | Proceed to Load handover |
| Warnings exist or rejection rate exceeds threshold | `MANUAL REVIEW` | Hold for authorized review |
| Critical failure or unsuccessful reconciliation | `REJECTED` | Stop, correct, and rerun or investigate |

## 10.4 Handover Package

The approved handover contains:

- standardized establishment, visitor-report, accommodation-report, and room-detail outputs;
- transformation `run_id` and linked Stage 1 `parent_run_id`;
- input, output, modified, rejected, and quarantined counts;
- applied cleaning, standardization, and business rule IDs;
- validation results and overall decision;
- quarantine reference and safe error details when applicable;
- output schema and source-to-target mapping.

Loading into a target database or warehouse is part of the next stage and is not performed here.

---

# 11. Common Transformation Problems and Mitigation

| Problem | Possible cause | Impact | Mitigation |
|---|---|---|---|
| Duplicate output after rerun | Non-idempotent append behavior | Inflated tourism counts | Use deterministic batch output replacement or upsert logic keyed by source identifier and `run_id`. |
| Missing timestamp column | Source export does not contain a configured optional timestamp | Incomplete audit metadata or failed assumptions | Treat the field as absent, record a warning, and use only available approved date fields. |
| Unexpected source column change | Source schema changed or export header differs | Incorrect mapping or failed transformation | Validate the schema before processing; stop incompatible batches and update the mapping deliberately. |
| Orphan report or room detail | Parent row is absent from the handover | Broken lineage and invalid joins | Quarantine the child row with the missing parent key; do not invent a parent. |
| Invalid report date | Blank, malformed, or ambiguous date | Incorrect period analytics | Parse only unambiguous values; quarantine unresolved dates rather than inferring them. |
| Invalid occupancy measure | Negative count or occupied rooms exceed available rooms | Incorrect occupancy indicators | Apply `C-07`, quarantine the row, and require review. |
| Unexpected row multiplication | Join key is not unique or join is performed on names | Inflated report totals | Validate key cardinality before joining and use only approved identifier relationships. |
| Late-arriving report | A source record arrives after the original handover | Incomplete reporting period | Re-run a documented lookback handover or controlled batch; do not mutate the original run. |
| Excessive quarantine rate | Source quality problem or overly strict rule | Batch cannot be approved | Produce counts and samples, review rules, correct the source/mapping, and rerun from preserved input. |

---

# Expected Output

Stage 2 is complete only when the transformation implementation and its documentation are consistent. The expected deliverables are:

1. Cleaned VistaBalayan datasets with safe corrections applied.
2. Standardized datasets with consistent names, dates, identifiers, and numeric types.
3. Business-ready outputs preserving establishment and report lineage.
4. A quarantine output for records that cannot be safely transformed.
5. Validation results covering reconciliation, keys, relationships, types, joins, and business rules.
6. Transformation metadata and logs linked to the Stage 1 parent run.
7. An `APPROVED`, `MANUAL REVIEW`, or `REJECTED` decision.
8. A load handover package without loading records into the target database.

The Stage 2 implementation remains **not started** until the project issues approve the rules and the actual Stage 1 handover is profiled. No profiling counts are fabricated in this specification; they must be populated from the real handover during execution.
