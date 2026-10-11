import csv
from pathlib import Path

from src.database import load_database_config, load_dotenv
from src.extract import export_table_to_csv, normalize_rows


class FakeConfig:
    batch_size = 2


class FakeClient:
    config = FakeConfig()

    def __init__(self):
        self.calls = []
        self.rows = {
            0: [
                {"id": "1", "name": "One", "details": {"a": 1}},
                {"id": "2", "name": "Two", "details": {"b": 2}},
            ],
            2: [
                {"id": "3", "name": "Three", "extra value": "ok"},
            ],
        }

    def fetch_rows(self, table, offset=0, limit=None):
        self.calls.append((table, offset, limit))
        return self.rows.get(offset, [])


def test_load_database_config_from_env_file(tmp_path, monkeypatch):
    env_file = tmp_path / ".env"
    env_file.write_text(
        "SUPABASE_URL=https://example.supabase.co\nSUPABASE_ANON_KEY=test-key\nBATCH_SIZE=25\n",
        encoding="utf-8",
    )
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_ANON_KEY", raising=False)
    monkeypatch.delenv("SUPABASE_SERVICE_ROLE_KEY", raising=False)
    monkeypatch.delenv("BATCH_SIZE", raising=False)

    config = load_database_config(env_file)

    assert config.supabase_url == "https://example.supabase.co"
    assert config.supabase_key == "test-key"
    assert config.batch_size == 25
    assert config.rest_url == "https://example.supabase.co/rest/v1"


def test_normalize_rows_handles_nested_json_and_column_names():
    columns, rows = normalize_rows([{"ID": 1, "Long Name": "A", "meta": {"z": 2}}])

    assert columns == ["id", "long_name", "meta"]
    assert rows[0]["id"] == "1"
    assert rows[0]["long_name"] == "A"
    assert rows[0]["meta"] == '{"z": 2}'


def test_export_table_to_csv_extracts_in_batches(tmp_path):
    client = FakeClient()

    result = export_table_to_csv(client, "establishments", tmp_path)

    assert result["status"] == "PASS"
    assert result["records_extracted"] == 3
    assert result["batches"] == 2
    assert client.calls == [("establishments", 0, 2), ("establishments", 2, 2)]

    output_csv = Path(result["output_csv"])
    with output_csv.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    assert rows[0]["name"] == "One"
    assert rows[2]["extra_value"] == "ok"
