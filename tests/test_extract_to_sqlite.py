import csv
import importlib.util
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "extract_to_sqlite.py"
spec = importlib.util.spec_from_file_location("extract_to_sqlite", SCRIPT)
assert spec is not None and spec.loader is not None
extract_to_sqlite = importlib.util.module_from_spec(spec)
spec.loader.exec_module(extract_to_sqlite)


def write_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def test_extracts_csv_exports_to_sqlite_and_validates_relationships(tmp_path):
    raw = tmp_path / "raw"
    out = tmp_path / "processed" / "staging.sqlite"
    logs = tmp_path / "logs"
    config = ROOT / "config" / "pipeline_config.json"

    write_csv(raw / "establishments.csv", [
        {"id": "est-1", "name": "Balayan Beach Resort", "type": "Resort", "status": "active"},
    ])
    write_csv(raw / "visitor_reports.csv", [
        {"id": "vis-1", "establishment_id": "est-1", "report_date": "2026-10-01", "status": "approved", "total_guests": "10"},
    ])
    write_csv(raw / "accommodation_reports.csv", [
        {"id": "acc-1", "establishment_id": "est-1", "report_date": "2026-10-01", "status": "approved", "total_rooms": "5"},
    ])
    write_csv(raw / "room_occupancy_details.csv", [
        {"id": "room-1", "accommodation_report_id": "acc-1", "room_type": "Standard", "occupied_rooms": "2"},
    ])

    result = extract_to_sqlite.run(config, raw, out, logs)

    assert result["overall_status"] == "PASS"
    assert out.exists()
    with sqlite3.connect(out) as conn:
        assert conn.execute("select count(*) from establishments").fetchone()[0] == 1
        assert conn.execute("select count(*) from visitor_reports").fetchone()[0] == 1
        assert conn.execute("select count(*) from accommodation_reports").fetchone()[0] == 1
        assert conn.execute("select count(*) from room_occupancy_details").fetchone()[0] == 1
    assert Path(result["log_path"]).exists()


def test_fails_when_child_report_references_missing_establishment(tmp_path):
    raw = tmp_path / "raw"
    out = tmp_path / "processed" / "staging.sqlite"
    logs = tmp_path / "logs"
    config = ROOT / "config" / "pipeline_config.json"

    write_csv(raw / "establishments.csv", [
        {"id": "est-1", "name": "Balayan Beach Resort", "type": "Resort", "status": "active"},
    ])
    write_csv(raw / "visitor_reports.csv", [
        {"id": "vis-1", "establishment_id": "missing-est", "report_date": "2026-10-01", "status": "approved"},
    ])

    result = extract_to_sqlite.run(config, raw, out, logs)

    assert result["overall_status"] == "FAIL"
    relationship_issues = [issue for issue in result["issues"] if issue.get("check") == "foreign_key_relationship"]
    assert any(issue.get("missing_parent_count") == 1 for issue in relationship_issues)
