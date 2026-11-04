"""Deterministic paper-level splitting to prevent cross-split leakage."""
from __future__ import annotations

import hashlib
from collections import defaultdict
from typing import Any


def assign_splits(records: list[dict[str, Any]], ratios: dict[str, float] | None = None, seed: str = "og-awc-v1") -> list[dict[str, Any]]:
    ratios = ratios or {"train": 0.8, "validation": 0.1, "test": 0.1}
    if set(ratios) != {"train", "validation", "test"}:
        raise ValueError("ratios must define train, validation, and test")
    if any(value < 0 for value in ratios.values()) or abs(sum(ratios.values()) - 1.0) > 1e-9:
        raise ValueError("split ratios must be non-negative and sum to 1")
    boundaries = (ratios["train"], ratios["train"] + ratios["validation"])
    paper_splits: dict[str, str] = {}
    for paper_id in {str(r["paper_id"]) for r in records}:
        digest = hashlib.sha256(f"{seed}:{paper_id}".encode("utf-8")).hexdigest()
        bucket = int(digest[:16], 16) / float(16**16)
        paper_splits[paper_id] = "train" if bucket < boundaries[0] else "validation" if bucket < boundaries[1] else "test"
    output = []
    for record in records:
        copied = dict(record)
        copied["split"] = paper_splits[str(record["paper_id"])]
        output.append(copied)
    return output


def check_paper_leakage(records: list[dict[str, Any]]) -> list[str]:
    membership: dict[str, set[str]] = defaultdict(set)
    for record in records:
        membership[str(record["paper_id"])].add(str(record["split"]))
    return [f"paper_id {paper_id!r} appears in multiple splits: {sorted(splits)}"
            for paper_id, splits in membership.items() if len(splits) > 1]
