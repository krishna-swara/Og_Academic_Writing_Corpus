"""Local, deterministic preparation of corpus JSONL files."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .deduplicate import deduplicate
from .split import assign_splits, check_paper_leakage
from .validation import validate_record


def read_jsonl(path: str | Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with Path(path).open(encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, 1):
            if not line.strip():
                continue
            try:
                value = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"line {line_no}: invalid JSON: {exc.msg}") from exc
            if not isinstance(value, dict):
                raise ValueError(f"line {line_no}: expected a JSON object")
            errors = validate_record(value)
            if errors:
                raise ValueError(f"line {line_no}: " + "; ".join(errors))
            records.append(value)
    return records


def write_jsonl(path: str | Path, records: list[dict[str, Any]]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8", newline="\n") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")


def prepare_dataset(input_path: str | Path, output_dir: str | Path, seed: str = "og-awc-v1") -> dict[str, int]:
    """Validate, exact-deduplicate, paper-split, and write local outputs.

    Outputs are local working artifacts, not permission to publish source text.
    """
    records = read_jsonl(input_path)
    unique, duplicates = deduplicate(records)
    split_records = assign_splits(unique, seed=seed)
    leakage = check_paper_leakage(split_records)
    if leakage:
        raise RuntimeError("paper leakage detected: " + "; ".join(leakage))

    out = Path(output_dir)
    write_jsonl(out / "all.jsonl", split_records)
    for split_name in ("train", "validation", "test"):
        write_jsonl(out / f"{split_name}.jsonl", [r for r in split_records if r["split"] == split_name])
    write_jsonl(out / "duplicates.jsonl", duplicates)
    report = {
        "input_records": len(records),
        "unique_records": len(unique),
        "duplicate_records": len(duplicates),
        "train_records": sum(r["split"] == "train" for r in split_records),
        "validation_records": sum(r["split"] == "validation" for r in split_records),
        "test_records": sum(r["split"] == "test" for r in split_records),
        "split_unit": "paper_id",
        "seed": seed,
        "publication_note": "Local outputs only. Review source licenses and redistribution permissions before publishing.",
    }
    (out / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report
