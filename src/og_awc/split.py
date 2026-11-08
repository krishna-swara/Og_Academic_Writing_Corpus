"""Deterministic group-level splitting to prevent cross-split leakage."""
from __future__ import annotations

import hashlib
from collections import defaultdict
from typing import Any


def _split_group(record: dict[str, Any]) -> str:
    group_id = record.get("split_group_id")
    if isinstance(group_id, str) and group_id.strip():
        return "split_group:" + group_id.strip()
    return "paper:" + str(record["paper_id"])


def assign_splits(records: list[dict[str, Any]], ratios: dict[str, float] | None = None, seed: str = "og-awc-v1") -> list[dict[str, Any]]:
    ratios = ratios or {"train": 0.8, "validation": 0.1, "test": 0.1}
    if set(ratios) != {"train", "validation", "test"}:
        raise ValueError("ratios must define train, validation, and test")
    if any(value < 0 for value in ratios.values()) or abs(sum(ratios.values()) - 1.0) > 1e-9:
        raise ValueError("split ratios must be non-negative and sum to 1")
    boundaries = (ratios["train"], ratios["train"] + ratios["validation"])
    group_splits: dict[str, str] = {}
    for group_id in {_split_group(r) for r in records}:
        digest = hashlib.sha256(f"{seed}:{group_id}".encode("utf-8")).hexdigest()
        bucket = int(digest[:16], 16) / float(16**16)
        group_splits[group_id] = "train" if bucket < boundaries[0] else "validation" if bucket < boundaries[1] else "test"
    output = []
    for record in records:
        copied = dict(record)
        copied["split"] = group_splits[_split_group(record)]
        output.append(copied)
    return output


def check_paper_leakage(records: list[dict[str, Any]]) -> list[str]:
    membership: dict[str, set[str]] = defaultdict(set)
    for record in records:
        membership[_split_group(record)].add(str(record["split"]))
    return [f"split group {group_id!r} appears in multiple splits: {sorted(splits)}"
            for group_id, splits in membership.items() if len(splits) > 1]
