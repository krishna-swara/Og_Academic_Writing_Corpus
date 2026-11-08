"""Opt-in acquisition of the public CoEdIT text-editing release.

Records are deliberately marked pending rights/quality review. This module does
not approve examples or expose them to production retrieval.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DATASET_ID = "grammarly/coedit"
DATASET_URL = "https://huggingface.co/datasets/grammarly/coedit"
PAPER_URL = "https://arxiv.org/abs/2305.09857"
DECLARED_LICENSE = "apache-2.0"


def _record_id(row: dict[str, Any]) -> str:
    upstream_id = row.get("_id")
    if upstream_id is not None:
        return f"coedit-{upstream_id}"
    payload = json.dumps(
        [row.get("task"), row.get("src"), row.get("tgt")],
        ensure_ascii=False, separators=(",", ":"),
    )
    return "coedit-" + hashlib.sha256(payload.encode("utf-8")).hexdigest()[:24]


def convert_coedit_rows(
    rows: list[dict[str, Any]], acquisition_date: str, revision: str
) -> tuple[list[dict[str, Any]], int]:
    """Normalize source/target pairs without fabricating human-review labels."""
    records: list[dict[str, Any]] = []
    excluded = 0
    for row in rows:
        src, tgt = row.get("src"), row.get("tgt")
        if not isinstance(src, str) or not src.strip() or not isinstance(tgt, str) or not tgt.strip():
            excluded += 1
            continue
        instruction, separator, original = src.partition(":")
        original_text = original.strip() if separator and original.strip() else src.strip()
        task = str(row.get("task") or "unspecified")
        record_id = _record_id(row)
        records.append({
            "record_id": record_id,
            # Sentence-level CoEdIT rows have no reliable paper grouping.
            # Each upstream row is an explicit split-isolation group.
            "paper_id": record_id,
            "source_id": "grammarly-coedit",
            "record_type": "revision_pair",
            "original_text": original_text,
            "revised_text": tgt.strip(),
            "split": "unassigned",
            "edit_labels": [task],
            "meaning_preserved": False,
            "human_review_status": "pending",
            "provenance": {
                "source_url": DATASET_URL,
                "paper_url": PAPER_URL,
                "license_id": DECLARED_LICENSE,
                "license_evidence": "Hugging Face dataset card metadata; upstream source lineage review remains outstanding",
                "rights_review_status": "pending_upstream_lineage_review",
                "text_mining_permitted": False,
                "acquisition_date": acquisition_date,
                "source_version": revision,
                "source_record_id": str(row.get("_id", record_id)),
                "source_task": task,
                "source_instruction": instruction.strip() if separator else "",
                "notes": (
                    "Public CoEdIT release. Preserve task and upstream identity. "
                    "This record is pending rights, lineage, and quality review; "
                    "it is not approved training or retrieval data. The upstream "
                    "record is not asserted to be human-authored or meaning-preserving."
                ),
            },
        })
    return records, excluded


def acquire_coedit(output_path: str | Path) -> dict[str, Any]:
    """Download the public train split through Hugging Face and write local JSONL."""
    try:
        from datasets import load_dataset
        from huggingface_hub import HfApi
    except ImportError as exc:
        raise RuntimeError(
            "Install the optional dependency group first: pip install -e '.[hf]'"
        ) from exc

    info = HfApi().dataset_info(DATASET_ID)
    revision = info.sha
    if not revision:
        raise RuntimeError("Hugging Face did not return an immutable dataset revision")
    dataset = load_dataset(DATASET_ID, split="train", revision=revision)
    acquisition_date = datetime.now(timezone.utc).date().isoformat()
    records, excluded = convert_coedit_rows(
        [dict(row) for row in dataset], acquisition_date, revision
    )
    if not records:
        raise RuntimeError("CoEdIT acquisition produced zero valid source/target pairs")

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="\n") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")

    manifest = {
        "dataset_id": DATASET_ID,
        "dataset_revision": revision,
        "declared_license": DECLARED_LICENSE,
        "rights_review_status": "pending_upstream_lineage_review",
        "records_written": len(records),
        "records_excluded": excluded,
        "output": str(output),
        "raw_text_committed_to_git": False,
        "approved_for_training": False,
        "approved_for_retrieval": False,
    }
    output.with_suffix(output.suffix + ".manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    return manifest
