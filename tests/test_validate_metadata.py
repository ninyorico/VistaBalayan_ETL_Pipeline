import csv
import importlib.util
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXTRACT_SCRIPT = ROOT / "scripts" / "extract_to_sqlite.py"
VALIDATE_SCRIPT = ROOT / "scripts" / "validate_metadata.py"

extract_spec = importlib.util.spec_from_file_location("extract_to_sqlite", EXTRACT_SCRIPT)
assert extract_spec is not None and extract_spec.loader is not None
extract_to_sqlite = importlib.util.module_from_spec(extract_spec)
extract_spec.loader.exec_module(extract_to_sqlite)

validate_spec = importlib.util.spec_from_file_location("validate_metadata", VALIDATE_SCRIPT)
assert validate_spec is not None and validate_spec.loader is not None
validate_metadata = importlib.util.module_from_spec(validate_spec)
validate_spec.loader.exec_module(validate_metadata)


def write_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def make_valid_sqlite(tmp_path):
    raw = tmp_path / "raw"
    out = tmp_path / "processed" / "staging.sqlite"
    logs = tmp_path / "logs"
    config = ROOT / "config" / "pipeline_config.json"

    write_csv(raw / "establishments.csv", [
        {"id": "est-1", "name": "Balayan Beach Resort", "type": "Resort", "status": "active", "created_at": "2026-10-01"},
    ])
    write_csv(raw / "visitor_reports.csv", [
        {"id": "vis-1", "establishment_id": "est-1", "report_date": "2026-10-01", "status": "approved", "created_at": "2026-10-02"},
    ])
    write_csv(raw / "accommodation_reports.csv", [
        {"id": "acc-1", "establishment_id": "est-1", "report_date": "2026-10-01", "status": "approved", "created_at": "2026-10-02"},
    ])
    write_csv(raw / "room_occupancy_details.csv", [
        {"id": "room-1", "accommodation_report_id": "acc-1", "created_at": "2026-10-02"},
    ])
    extraction = extract_to_sqlite.run(config, raw, out, logs)
    assert extraction["overall_status"] == "PASS"
    return config, out, logs


def test_validate_metadata_passes_valid_staging_sqlite(tmp_path):
    config, out, logs = make_valid_sqlite(tmp_path)

    result = validate_metadata.validate_sqlite(config, out, logs)

    assert result["overall_status"] == "PASS"
    assert result["tables"]["establishments"]["row_count"] == 1
    assert result["tables"]["visitor_reports"]["row_count"] == 1
    assert result["tables"]["accommodation_reports"]["row_count"] == 1
    assert result["tables"]["room_occupancy_details"]["row_count"] == 1
    assert Path(result["log_path"]).exists()


def test_validate_metadata_fails_missing_foreign_key_parent(tmp_path):
    config, out, logs = make_valid_sqlite(tmp_path)
    with sqlite3.connect(out) as conn:
        conn.execute("UPDATE visitor_reports SET establishment_id = 'missing-est'")
        conn.commit()

    result = validate_metadata.validate_sqlite(config, out, logs)

    assert result["overall_status"] == "FAIL"
    relationship_checks = [c for c in result["checks"] if c.get("check") == "foreign_key_relationship"]
    assert any(c.get("table") == "visitor_reports" and c.get("missing_parent_count") == 1 for c in relationship_checks)
