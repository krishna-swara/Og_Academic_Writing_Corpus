"""Stable exact-text deduplication helpers."""
from __future__ import annotations

import hashlib
import re
from typing import Any


def normalized_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().casefold()


def record_fingerprint(record: dict[str, Any]) -> str:
    payload = "\\0".join((
        normalized_text(record.get("original_text", "")),
        normalized_text(record.get("revised_text") or ""),
        str(record.get("record_type", "")),
    ))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def deduplicate(records: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Keep first occurrence; return (unique, duplicates) in input order."""
    seen: set[str] = set()
    unique, duplicates = [], []
    for record in records:
        fingerprint = record_fingerprint(record)
        if fingerprint in seen:
            duplicates.append(record)
        else:
            seen.add(fingerprint)
            unique.append(record)
    return unique, duplicates
