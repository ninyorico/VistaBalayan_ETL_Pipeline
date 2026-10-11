#!/usr/bin/env python3
"""Minimal Stage 1 VistaBalayan ETL runner.

Current workflow:
1. Build a local SQLite staging database from CSV exports.
2. Validate table counts, required columns, primary keys, and relationships.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.staging import run as build_sqlite
from src.validate import validate_sqlite


def command_build_sqlite(args: argparse.Namespace) -> dict:
    return build_sqlite(args.config, raw_dir=args.raw_dir, sqlite_output=args.sqlite_output, log_dir=args.log_dir)


def command_validate(args: argparse.Namespace) -> dict:
    return validate_sqlite(args.config, sqlite_path=args.sqlite_output, log_dir=args.log_dir)


def add_common_paths(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--config", default=Path("config/pipeline_config.json"), type=Path)
    parser.add_argument("--raw-dir", default=Path("data/raw"), type=Path)
    parser.add_argument("--sqlite-output", default=Path("data/processed/vistabalayan_staging.sqlite"), type=Path)
    parser.add_argument("--log-dir", default=Path("logs"), type=Path)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="VistaBalayan Stage 1 CSV-to-SQLite ETL")
    subparsers = parser.add_subparsers(dest="command", required=True)

    sqlite_parser = subparsers.add_parser("build-sqlite", help="Build SQLite staging DB from data/raw CSV files")
    add_common_paths(sqlite_parser)
    sqlite_parser.set_defaults(func=command_build_sqlite)

    validate_parser = subparsers.add_parser("validate", help="Validate SQLite metadata and relationships")
    add_common_paths(validate_parser)
    validate_parser.set_defaults(func=command_validate)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    result = args.func(args)
    print(json.dumps(result, indent=2))
    return 0 if result.get("overall_status", result.get("status")) == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
