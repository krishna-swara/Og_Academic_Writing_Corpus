"""Acquisition helpers for auxiliary JFLEG and ACL Anthology metadata sources.

JFLEG is retained as a sentence-level GEC benchmark, never mixed into academic
paragraph training data. ACL acquisition downloads bibliographic metadata only;
it does not download or redistribute paper PDFs/full text.
"""
from __future__ import annotations

import gzip
import hashlib
import json
import re
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .acquire import sha256_file

JFLEG_REPO = "https://raw.githubusercontent.com/keisks/jfleg"
JFLEG_REVISION = "ee06ff806a208aba815ac45313f4e750a48330a5"
JFLEG_LICENSE = "cc-by-nc-sa-4.0"
JFLEG_FILES = {
    "validation": ("dev/dev.src", [f"dev/dev.ref{i}" for i in range(4)]),
    "test": ("test/test.src", [f"test/test.ref{i}" for i in range(4)]),
}
ACL_BIB_URL = "https://aclanthology.org/anthology.bib.gz"


def _download(url: str, destination: Path, timeout: int = 120) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    partial = destination.with_suffix(destination.suffix + ".part")
    request = urllib.request.Request(url, headers={"User-Agent": "Og-AWC/0.1 dataset-acquisition"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response, partial.open("wb") as out:
            while chunk := response.read(1024 * 1024):
                out.write(chunk)
        partial.replace(destination)
    finally:
        if partial.exists():
            partial.unlink()


def convert_jfleg_files(raw_dir: str | Path, acquisition_date: str) -> tuple[list[dict[str, Any]], dict[str, int]]:
    """Convert JFLEG source/ref files to four genuine sentence-level correction pairs."""
    root = Path(raw_dir)
    records: list[dict[str, Any]] = []
    counts: dict[str, int] = {}
    for upstream_split, (source_rel, refs_rel) in JFLEG_FILES.items():
        source_path = root / source_rel
        sources = source_path.read_text(encoding="utf-8").splitlines()
        refs = [(root / rel).read_text(encoding="utf-8").splitlines() for rel in refs_rel]
        if any(len(lines) != len(sources) for lines in refs):
            raise ValueError(f"JFLEG {upstream_split}: source/reference line counts do not match")
        counts[upstream_split] = len(sources)
        for row_index, source in enumerate(sources):
            if not source.strip():
                continue
            sentence_id = f"jfleg-{upstream_split}-{row_index + 1:04d}"
            for ref_index, ref_lines in enumerate(refs):
                correction = ref_lines[row_index]
                if not correction.strip():
                    continue
                records.append({
                    "record_id": f"{sentence_id}-ref{ref_index}",
                    "source_id": "jfleg_aux",
                    "paper_id": sentence_id,
                    "record_type": "revision_pair",
                    "original_text": source.strip(),
                    "revised_text": correction.strip(),
                    "split": upstream_split,
                    "edit_labels": [],
                    "provenance": {
                        "source_url": "https://huggingface.co/datasets/jhu-clsp/jfleg",
                        "license_id": JFLEG_LICENSE,
                        "acquisition_date": acquisition_date,
                        "source_record_id": sentence_id,
                        "reviewer": None,
                        "notes": "Auxiliary sentence-level grammatical-error-correction benchmark, not academic paragraph data. Human correction reference retained as a separate pair; original upstream split preserved.",
                        "source_revision": JFLEG_REVISION,
                        "source_split": upstream_split,
                        "reference_index": ref_index,
                        "attribution": "Napoles, Sakaguchi, and Tetreault (2017), JFLEG: A Fluency Corpus and Benchmark for Grammatical Error Correction, EACL 2017.",
                        "license_url": "https://creativecommons.org/licenses/by-nc-sa/4.0/"
                    }
                })
    return records, counts


def acquire_jfleg(output_path: str | Path, raw_dir: str | Path, accept_license: bool = False) -> dict[str, Any]:
    if not accept_license:
        raise ValueError("JFLEG declares CC BY-NC-SA 4.0. Use --accept-license only if you can comply with non-commercial, attribution, and share-alike terms.")
    raw_root = Path(raw_dir)
    for _, (source_rel, refs_rel) in JFLEG_FILES.items():
        for rel in [source_rel, *refs_rel]:
            destination = raw_root / rel
            if not destination.exists():
                _download(f"{JFLEG_REPO}/{JFLEG_REVISION}/{rel}", destination)
    date = datetime.now(timezone.utc).date().isoformat()
    records, counts = convert_jfleg_files(raw_root, date)
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="\n") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
    manifest = {
        "source_id": "jfleg_aux",
        "source_url": "https://huggingface.co/datasets/jhu-clsp/jfleg",
        "upstream_repository": "https://github.com/keisks/jfleg",
        "source_revision": JFLEG_REVISION,
        "license": JFLEG_LICENSE,
        "license_url": "https://creativecommons.org/licenses/by-nc-sa/4.0/",
        "acquisition_date": date,
        "source_sentences_by_split": counts,
        "source_sentences_total": sum(counts.values()),
        "correction_pairs_written": len(records),
        "raw_file_sha256": {str(p.relative_to(raw_root)): sha256_file(p) for p in sorted(raw_root.rglob("*")) if p.is_file()},
        "raw_dir": str(raw_root),
        "normalized_path": str(output),
        "dataset_role": "auxiliary_sentence_level_gec_benchmark",
        "split_policy": "Original validation/test split is preserved; do not run the generic random split pipeline on this benchmark.",
        "publication_status": "local_only_pending_rights_review"
    }
    output.with_suffix(".manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest


def _bib_entries(text: str):
    """Yield BibTeX entries using brace-depth scanning (handles nested braces)."""
    pos = 0
    while True:
        start = text.find("@", pos)
        if start < 0:
            return
        brace = text.find("{", start)
        if brace < 0:
            return
        depth = 1
        i = brace + 1
        while i < len(text) and depth:
            if text[i] == "{":
                depth += 1
            elif text[i] == "}":
                depth -= 1
            i += 1
        if depth:
            return
        yield text[start:i]
        pos = i


def _bib_field(entry: str, field: str) -> str | None:
    match = re.search(rf"(?is)\b{re.escape(field)}\s*=\s*([{{\"])", entry)
    if not match:
        return None
    opener = match.group(1)
    start = match.end()
    if opener == "{":
        depth = 1
        i = start
        while i < len(entry) and depth:
            if entry[i] == "{":
                depth += 1
            elif entry[i] == "}":
                depth -= 1
            i += 1
        return entry[start:i - 1].strip() if depth == 0 else None
    end = entry.find('"', start)
    return entry[start:end].strip() if end >= 0 else None


def acquire_acl_catalog(output_path: str | Path, raw_dir: str | Path) -> dict[str, Any]:
    """Download ACL Anthology BibTeX metadata only; no paper PDFs/full text."""
    raw_root = Path(raw_dir)
    raw_path = raw_root / "anthology.bib.gz"
    if not raw_path.exists():
        _download(ACL_BIB_URL, raw_path, timeout=240)
    with gzip.open(raw_path, "rt", encoding="utf-8", errors="replace") as handle:
        bib_text = handle.read()
    date = datetime.now(timezone.utc).date().isoformat()
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    written = 0
    with output.open("w", encoding="utf-8", newline="\n") as handle:
        for entry in _bib_entries(bib_text):
            head = re.match(r"@([A-Za-z]+)\s*\{\s*([^,]+)", entry)
            if not head:
                continue
            item = {
                "source_id": "acl_anthology_metadata",
                "bibtex_key": head.group(2).strip(),
                "entry_type": head.group(1).lower(),
                "title": _bib_field(entry, "title"),
                "author": _bib_field(entry, "author"),
                "year": _bib_field(entry, "year"),
                "booktitle": _bib_field(entry, "booktitle"),
                "url": _bib_field(entry, "url"),
                "abstract": _bib_field(entry, "abstract"),
                "source_url": "https://aclanthology.org/",
                "license_status": "metadata_only_paper_level_text_license_not_inferred",
                "acquisition_date": date
            }
            handle.write(json.dumps(item, ensure_ascii=False, sort_keys=True) + "\n")
            written += 1
    manifest = {
        "source_id": "acl_anthology_metadata",
        "source_url": "https://aclanthology.org/faq/api/",
        "download_url": ACL_BIB_URL,
        "acquisition_date": date,
        "raw_file_sha256": sha256_file(raw_path),
        "metadata_records_written": written,
        "raw_path": str(raw_path),
        "normalized_path": str(output),
        "content_policy": "Bibliographic metadata only. No PDFs or paper full text downloaded. Per-paper publication license and third-party content must be checked before text acquisition.",
        "publication_status": "metadata_catalog_only"
    }
    output.with_suffix(".manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest
