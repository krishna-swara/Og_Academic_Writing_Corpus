"""Validation rules for Og-AWC JSONL records."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

REQUIRED = {"record_id", "source_id", "paper_id", "record_type", "original_text", "revised_text", "split", "provenance"}
PAIR_TYPES = {"revision_pair", "human_reviewed_edit"}
VALID_TYPES = PAIR_TYPES | {"source_only", "synthetic_fixture"}
VALID_SPLITS = {"train", "validation", "test", "unassigned"}


def validate_record(record: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    missing = REQUIRED - record.keys()
    if missing:
        return [f"missing required fields: {', '.join(sorted(missing))}"]
    for field in ("record_id", "source_id", "paper_id", "original_text"):
        if not isinstance(record[field], str) or not record[field].strip():
            errors.append(f"{field} must be a non-empty string")
    if record["record_type"] not in VALID_TYPES:
        errors.append("record_type is not supported")
    if record["split"] not in VALID_SPLITS:
        errors.append("split must be train, validation, test, or unassigned")
    if record["record_type"] in PAIR_TYPES and not (isinstance(record["revised_text"], str) and record["revised_text"].strip()):
        errors.append("revision records require a genuine non-empty revised_text")
    if record["record_type"] == "source_only" and record["revised_text"] not in (None, ""):
        errors.append("source_only records must not contain fabricated revised_text")
    if not isinstance(record["provenance"], dict):
        errors.append("provenance must be an object")
    else:
        for field in ("source_url", "license_id", "acquisition_date"):
            if field not in record["provenance"]:
                errors.append(f"provenance.{field} is required")
        if not record["provenance"].get("license_id"):
            errors.append("provenance.license_id must be non-empty")
    return errors


def validate_jsonl(path: str | Path) -> list[str]:
    errors: list[str] = []
    with Path(path).open(encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, 1):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                errors.append(f"line {line_no}: invalid JSON: {exc.msg}")
                continue
            if not isinstance(record, dict):
                errors.append(f"line {line_no}: record must be a JSON object")
                continue
            errors.extend(f"line {line_no}: {err}" for err in validate_record(record))
    return errors
