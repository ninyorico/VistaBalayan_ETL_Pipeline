"""Stage 2 transformation of the local VistaBalayan Stage 1 handover."""
from __future__ import annotations

import csv
import hashlib
import json
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DATASETS = (
    "establishments",
    "visitor_reports",
    "accommodation_reports",
    "room_occupancy_details",
)
PRIMARY_KEYS = {
    "establishments": "id",
    "visitor_reports": "id",
    "accommodation_reports": "id",
    "room_occupancy_details": "id",
}
REQUIRED = {
    "establishments": ("id", "name", "type", "status"),
    "visitor_reports": ("id", "establishment_id", "report_date", "status"),
    "accommodation_reports": ("id", "establishment_id", "report_date", "status"),
    "room_occupancy_details": ("id", "accommodation_report_id"),
}
PARENT_KEYS = {
    "visitor_reports": ("establishment_id", "establishments", "id"),
    "accommodation_reports": ("establishment_id", "establishments", "id"),
    "room_occupancy_details": ("accommodation_report_id", "accommodation_reports", "id"),
}


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def snake(value: str) -> str:
    value = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", value or "")
    value = re.sub(r"[^A-Za-z0-9]+", "_", value).strip("_").lower()
    return value or "unnamed_column"


def parse_date(value: Any) -> str | None:
    text = str(value or "").strip()
    if not text:
        return None
    candidate = text.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(candidate).date().isoformat()
    except ValueError:
        pass
    for fmt in ("%Y/%m/%d", "%m/%d/%Y", "%d/%m/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(text[:10], fmt).date().isoformat()
        except ValueError:
            continue
    return None


NUMERIC_FIELDS = {
    # Visitor-report measures.
    "female_visitors",
    "male_visitors",
    "total_female",
    "total_guests",
    "total_male",
    "total_visitors",
    "visitor_count",
    # Accommodation-report measures.
    "foreign_guest_check_ins",
    "foreign_guest_nights",
    "guest_check_ins",
    "guest_nights",
    "room_usage_count",
    "rooms_occupied",
    "short_stay_check_ins",
    "total_check_ins",
    "total_guest_nights",
    "total_occupied_rooms",
    "total_rooms",
    # Room-occupancy-detail measures.
    "check_ins",
    "number_of_rooms",
    "occupied_rooms",
}


def is_numeric_field(name: str) -> bool:
    """Return whether a field is a known numeric measure.

    Do not infer numeric type from broad substrings such as ``guest`` or
    ``room_``: VistaBalayan also has text fields such as ``guest_name``,
    ``guest_group_name``, ``room_code``, and ``room_type``.
    """
    return name in NUMERIC_FIELDS


def read_rows(sqlite_path: Path, raw_dir: Path, dataset: str) -> list[dict[str, Any]]:
    if sqlite_path.exists():
        with sqlite3.connect(sqlite_path) as conn:
            conn.row_factory = sqlite3.Row
            try:
                return [dict(row) for row in conn.execute(f"SELECT * FROM {dataset}")]
            except sqlite3.Error:
                pass
    path = raw_dir / f"{dataset}.csv"
    if not path.exists():
        raise FileNotFoundError(f"Missing Stage 1 input: {path}")
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    columns: list[str] = []
    for row in rows:
        for key in row:
            if key not in columns:
                columns.append(key)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def contract_row(dataset: str, row: dict[str, Any]) -> dict[str, Any]:
    names = {
        "establishments": {"id": "establishment_id", "name": "establishment_name", "type": "establishment_type", "status": "establishment_status"},
        "visitor_reports": {"id": "visitor_report_id", "status": "report_status"},
        "accommodation_reports": {"id": "accommodation_report_id", "status": "report_status"},
        "room_occupancy_details": {"id": "room_occupancy_detail_id"},
    }[dataset]
    return {names.get(key, key): value for key, value in row.items()}


def profile(rows: list[dict[str, Any]], dataset: str) -> dict[str, Any]:
    normalized = [{snake(k): v for k, v in row.items()} for row in rows]
    key = PRIMARY_KEYS[dataset]
    seen: set[str] = set()
    duplicates = 0
    blank_required = {field: 0 for field in REQUIRED[dataset]}
    invalid_dates = 0
    for row in normalized:
        value = str(row.get(key, "") or "").strip()
        if value and value in seen:
            duplicates += 1
        if value:
            seen.add(value)
        for field in REQUIRED[dataset]:
            if not str(row.get(field, "") or "").strip():
                blank_required[field] += 1
        if "report_date" in row and str(row.get("report_date") or "").strip() and parse_date(row.get("report_date")) is None:
            invalid_dates += 1
    return {
        "records_read": len(rows),
        "columns": sorted({snake(k) for row in rows for k in row}),
        "blank_required": blank_required,
        "duplicate_primary_key_count": duplicates,
        "invalid_report_date_count": invalid_dates,
        "status_values": sorted({str(row.get("status", "")).strip() for row in normalized if str(row.get("status", "")).strip()}),
        "type_values": sorted({str(row.get("type", "")).strip() for row in normalized if str(row.get("type", "")).strip()}),
    }


def quarantine(run_id: str, batch_id: str, dataset: str, row: dict[str, Any], rule_id: str, reason: str) -> dict[str, Any]:
    key = PRIMARY_KEYS.get(dataset, "id")
    return {
        "run_id": run_id,
        "batch_id": batch_id,
        "source_dataset": dataset,
        "source_record_key": str(row.get(key, row.get(snake(key), "")) or ""),
        "original_record": json.dumps(row, ensure_ascii=False, sort_keys=True, default=str),
        "rule_id": rule_id,
        "quarantine_reason": reason,
        "quarantined_at": now_iso(),
    }


def transform_rows(rows: list[dict[str, Any]], dataset: str, run_id: str, batch_id: str, parent_values: set[str]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, int]]:
    output: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    modified = 0
    key = PRIMARY_KEYS[dataset]
    seen: set[str] = set()
    for source in rows:
        row = {snake(k): v for k, v in source.items()}
        changed = False
        for field, value in list(row.items()):
            if isinstance(value, str):
                trimmed = value.strip()
                changed |= trimmed != value
                row[field] = trimmed
        identifier = str(row.get(key, "") or "").strip()
        if not identifier:
            rejected.append(quarantine(run_id, batch_id, dataset, source, "C-02", f"missing required identifier: {key}"))
            continue
        if identifier in seen:
            rejected.append(quarantine(run_id, batch_id, dataset, source, "C-03", f"duplicate primary key: {key}={identifier}"))
            continue
        seen.add(identifier)
        missing = [field for field in REQUIRED[dataset] if not str(row.get(field, "") or "").strip()]
        if missing:
            rejected.append(quarantine(run_id, batch_id, dataset, source, "C-02", f"missing required fields: {', '.join(missing)}"))
            continue
        if dataset in PARENT_KEYS:
            foreign_key, _, _ = PARENT_KEYS[dataset]
            if str(row.get(foreign_key, "")).strip() not in parent_values:
                rejected.append(quarantine(run_id, batch_id, dataset, source, "C-08", f"missing parent for {foreign_key}"))
                continue
        if "report_date" in row:
            parsed = parse_date(row["report_date"])
            if parsed is None:
                rejected.append(quarantine(run_id, batch_id, dataset, source, "C-05", "invalid report_date"))
                continue
            changed |= parsed != row["report_date"]
            row["report_date"] = parsed
            row["report_year"] = parsed[:4]
            row["report_month"] = parsed[5:7]
        numeric_error = False
        for field, value in list(row.items()):
            if field in ("id", "establishment_id", "accommodation_report_id") or not is_numeric_field(field) or str(value or "").strip() == "":
                continue
            try:
                number = int(str(value).strip())
                if number < 0:
                    numeric_error = True
                    break
                changed |= str(value).strip() != str(number)
                row[field] = number
            except (TypeError, ValueError):
                numeric_error = True
                break
        if numeric_error:
            rejected.append(quarantine(run_id, batch_id, dataset, source, "C-06", "invalid or negative numeric measure"))
            continue
        if changed:
            modified += 1
        output.append(row)
    return output, rejected, {"records_output": len(output), "records_rejected": len(rejected), "records_modified": modified}


def run(sqlite_path: Path, raw_dir: Path, output_dir: Path, log_dir: Path, run_id: str | None = None) -> dict[str, Any]:
    run_id = run_id or "TRN_" + datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    batch_id = "BATCH_" + run_id.removeprefix("TRN_")
    start = now_iso()
    all_rows: dict[str, list[dict[str, Any]]] = {}
    profiles: dict[str, Any] = {}
    try:
        for dataset in DATASETS:
            all_rows[dataset] = read_rows(sqlite_path, raw_dir, dataset)
            profiles[dataset] = profile(all_rows[dataset], dataset)
    except (FileNotFoundError, sqlite3.Error) as exc:
        result = {"overall_status": "FAIL", "status": "FAILED", "run_id": run_id, "error_code": "INPUT_MISSING", "error_message": str(exc)}
        log_dir.mkdir(parents=True, exist_ok=True)
        (log_dir / f"transformation_{run_id}.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
        return result

    transformed: dict[str, list[dict[str, Any]]] = {}
    quarantine_rows: list[dict[str, Any]] = []
    stats: dict[str, Any] = {}
    establishment_ids = {str(r.get("id", "")).strip() for r in all_rows["establishments"]}
    accepted_establishments, rejected, counts = transform_rows(all_rows["establishments"], "establishments", run_id, batch_id, set())
    transformed["establishments"] = accepted_establishments
    quarantine_rows.extend(rejected)
    stats["establishments"] = {"records_read": len(all_rows["establishments"]), **counts}
    accommodation_ids = {str(r.get("id", "")).strip() for r in all_rows["accommodation_reports"]}
    for dataset, parents in (("visitor_reports", establishment_ids), ("accommodation_reports", establishment_ids), ("room_occupancy_details", accommodation_ids)):
        accepted, rejected, counts = transform_rows(all_rows[dataset], dataset, run_id, batch_id, parents)
        transformed[dataset] = accepted
        quarantine_rows.extend(rejected)
        stats[dataset] = {"records_read": len(all_rows[dataset]), **counts}

    output_dir.mkdir(parents=True, exist_ok=True)
    for dataset, rows in transformed.items():
        write_csv(output_dir / f"{dataset}_transformed.csv", [contract_row(dataset, row) for row in rows])
    write_csv(output_dir / "transformation_quarantine.csv", quarantine_rows)
    validation = validate_outputs(transformed, quarantine_rows, stats)
    result = {
        "overall_status": validation["overall_status"],
        "status": "SUCCESS" if validation["overall_status"] != "FAIL" else "FAILED",
        "run_id": run_id,
        "parent_run_id": "EXT_FROM_STAGE1_HANDOVER",
        "batch_id": batch_id,
        "start_timestamp": start,
        "end_timestamp": now_iso(),
        "profiles": profiles,
        "datasets": stats,
        "quarantine_count": len(quarantine_rows),
        "validation": validation,
        "output_dir": str(output_dir),
        "rules_version": "stage2-v1",
    }
    log_dir.mkdir(parents=True, exist_ok=True)
    (log_dir / f"transformation_{run_id}.json").write_text(json.dumps(result, indent=2, default=str), encoding="utf-8")
    return result


def validate_outputs(transformed: dict[str, list[dict[str, Any]]], quarantine_rows: list[dict[str, Any]], stats: dict[str, Any]) -> dict[str, Any]:
    checks: dict[str, str] = {}
    critical_failures: list[str] = []
    for dataset, rows in transformed.items():
        key = PRIMARY_KEYS[dataset]
        unique = len({str(row.get(key, "")) for row in rows}) == len(rows)
        checks[f"{dataset}.key_uniqueness"] = "PASS" if unique else "FAIL"
        if not unique:
            critical_failures.append(f"{dataset}.key_uniqueness")
        reconciliation = stats[dataset]["records_read"] == stats[dataset]["records_output"] + stats[dataset]["records_rejected"]
        checks[f"{dataset}.reconciliation"] = "PASS" if reconciliation else "FAIL"
        if not reconciliation:
            critical_failures.append(f"{dataset}.reconciliation")
        for row in rows:
            if any(not str(row.get(field, "") or "").strip() for field in REQUIRED[dataset]):
                critical_failures.append(f"{dataset}.required_fields")
                checks[f"{dataset}.required_fields"] = "FAIL"
                break
        else:
            checks.setdefault(f"{dataset}.required_fields", "PASS")
    establishment_ids = {str(row["id"]) for row in transformed["establishments"]}
    for dataset in ("visitor_reports", "accommodation_reports"):
        orphan = sum(str(row.get("establishment_id")) not in establishment_ids for row in transformed[dataset])
        checks[f"{dataset}.referential_integrity"] = "PASS" if orphan == 0 else "FAIL"
        if orphan:
            critical_failures.append(f"{dataset}.referential_integrity")
    accommodation_ids = {str(row["id"]) for row in transformed["accommodation_reports"]}
    orphan = sum(str(row.get("accommodation_report_id")) not in accommodation_ids for row in transformed["room_occupancy_details"])
    checks["room_occupancy_details.referential_integrity"] = "PASS" if orphan == 0 else "FAIL"
    if orphan:
        critical_failures.append("room_occupancy_details.referential_integrity")
    invalid_quarantine = [row for row in quarantine_rows if not row.get("rule_id") or not row.get("quarantine_reason")]
    checks["quarantine.accounting"] = "PASS" if not invalid_quarantine else "FAIL"
    if invalid_quarantine:
        critical_failures.append("quarantine.accounting")
    total_read = sum(item["records_read"] for item in stats.values())
    rejection_rate = (len(quarantine_rows) / total_read * 100) if total_read else 0
    checks["rejection_rate"] = "PASS" if rejection_rate <= 1 else "WARNING"
    overall = "FAIL" if critical_failures else ("WARNING" if rejection_rate > 1 else "PASS")
    return {"overall_status": overall, "checks": checks, "critical_failures": critical_failures, "rejection_rate_percent": round(rejection_rate, 4), "records_read": total_read, "records_rejected": len(quarantine_rows)}
