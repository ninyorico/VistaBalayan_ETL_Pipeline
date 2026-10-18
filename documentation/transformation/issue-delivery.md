# Stage 2 Issue-Linked Delivery

The Stage 2 implementation is delivered through the issue-linked commits listed below. The implementation code is in `pipeline/transform.py` and the CLI integration is in `main.py`; this ledger records the issue-specific delivery and verification scope.

## Issue #3 — Profiling and input-contract checks

- Profiles all four Stage 1 handover datasets.
- Reports source columns, required-field blanks, duplicate primary keys, dates, status values, and establishment types.
- Validated with the Stage 2 fixture.

## Issue #4 — Cleaning and standardization rules

- Trims string values and normalizes column names to snake_case.
- Parses report dates into ISO format and adds report year/month metadata.
- Converts only known numeric measures, preserving text fields such as `guest_name`, `guest_group_name`, `room_code`, and `room_type`.
- The explicit numeric-field correction is included in commit `f2315f4`.

## Issue #5 — Transformed VistaBalayan datasets

- Produces transformed CSV files for establishments, visitor reports, accommodation reports, and room occupancy details.
- Preserves source identifiers and relationship keys.
- Writes output to the ignored `pipeline/transformed/` runtime directory.
- Validated with the clean fixture and confirmed all four transformed datasets were produced.

## Issue #6 — Quarantine and transformation validation

- Writes `transformation_quarantine.csv` with run ID, batch ID, source dataset, source key, rule ID, and reason.
- Validates reconciliation, primary-key uniqueness, required fields, referential integrity, quarantine accounting, and rejection rate.
- Clean fixture result: `PASS`, zero rejected records.
- Invalid fixture result: `WARNING`, one quarantined record, manual review exit code `1`.

## Issue #7 — CLI, handover package, and verification documentation

- Provides the `py main.py transform` entry point for the local Stage 1 handover.
- Reads the approved SQLite handover first and falls back to the four local CSV files.
- Writes transformation logs under `documentation/transformation/logs/` while keeping generated runtime data ignored.
- The implementation and verification workflow are documented in `documentation/transformation/data-transformation.md`.
