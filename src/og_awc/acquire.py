"""Opt-in local acquisition and normalization of ParaRev's annotated subset.

ParaRev declares CC BY-NC-SA 4.0. This downloader requires an explicit
acknowledgement and writes raw/processed text locally; it never pushes data.
"""
from __future__ import annotations

import hashlib
import json
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SOURCE_ID = "pararev"
REPO_URL = "https://huggingface.co/datasets/taln-ls2n/pararev"
REVISION = "e61dc8a43ae067513208e75f79b49f9928dcbec3"
FILENAME = "pararev_manual_annot_subset.jsonl"
LICENSE_ID = "cc-by-nc-sa-4.0"
DOWNLOAD_URL = f"{REPO_URL}/resolve/{REVISION}/{FILENAME}?download=true"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _article_component_ids(rows: list[dict[str, Any]]) -> dict[str, str]:
    """Return stable paper IDs for connected source/target article-version IDs.

    ParaRev's id_source and id_target are CASIMIR article-version IDs, not
    guaranteed unique paper IDs. Treat each source/target pair as an edge and
    group every connected version lineage into one paper-level split unit.
    """
    parent: dict[str, str] = {}

    def find(value: str) -> str:
        parent.setdefault(value, value)
        if parent[value] != value:
            parent[value] = find(parent[value])
        return parent[value]

    def union(left: str, right: str) -> None:
        root_left, root_right = find(left), find(right)
        if root_left != root_right:
            # Lexicographic root selection makes the component representative
            # independent of input row order.
            first, second = sorted((root_left, root_right))
            parent[second] = first

    for row in rows:
        source_id, target_id = row.get("id_source"), row.get("id_target")
        if (isinstance(source_id, str) and source_id.strip()
                and isinstance(target_id, str) and target_id.strip()):
            union(source_id.strip(), target_id.strip())

    components: dict[str, list[str]] = {}
    for version_id in list(parent):
        components.setdefault(find(version_id), []).append(version_id)

    result: dict[str, str] = {}
    for version_ids in components.values():
        digest_input = "\\0".join(sorted(version_ids))
        paper_id = "pararev-paper-" + hashlib.sha256(digest_input.encode("utf-8")).hexdigest()[:20]
        for version_id in version_ids:
            result[version_id] = paper_id
    return result


def convert_pararev_rows(rows: list[dict[str, Any]], acquisition_date: str) -> tuple[list[dict[str, Any]], int]:
    """Map genuine paragraph revision pairs and group linked article versions."""
    version_to_paper = _article_component_ids(rows)
    records: list[dict[str, Any]] = []
    excluded = 0
    for row_number, row in enumerate(rows, 1):
        original = row.get("parag_1")
        revised = row.get("parag_2")
        source_version_id = row.get("id_source")
        target_version_id = row.get("id_target")
        paragraph_id = row.get("id_paragraph")
        if not all(isinstance(value, str) and value.strip()
                   for value in (original, revised, source_version_id, target_version_id, paragraph_id)):
            excluded += 1
            continue
        source_version_id = source_version_id.strip()
        target_version_id = target_version_id.strip()
        pair_key = f"{paragraph_id.strip()}:{source_version_id}:{target_version_id}"
        annotations = {
            "annot_1": row.get("annot_1"),
            "annot_2": row.get("annot_2"),
        }
        records.append({
            "record_id": "pararev-" + hashlib.sha256(pair_key.encode("utf-8")).hexdigest()[:20],
            "source_id": SOURCE_ID,
            "paper_id": version_to_paper[source_version_id],
            "record_type": "revision_pair",
            "original_text": original.strip(),
            "revised_text": revised.strip(),
            "split": "unassigned",
            "edit_labels": [],
            "provenance": {
                "source_url": REPO_URL,
                "license_id": LICENSE_ID,
                "acquisition_date": acquisition_date,
                "source_record_id": paragraph_id.strip(),
                "reviewer": None,
                "notes": "ParaRev annotated subset; parag_1/id_source to parag_2/id_target. paper_id groups connected CASIMIR article-version IDs so related versions remain in one split. Human annotation metadata is retained below; annotations are not reinterpreted as Og-AWC labels.",
                "source_version": REVISION,
                "source_file": FILENAME,
                "source_row_number": row_number,
                "source_article_version_id": source_version_id,
                "source_target_id": target_version_id,
                "source_annotations": annotations,
                "license_url": "https://creativecommons.org/licenses/by-nc-sa/4.0/",
                "attribution": "Jourdan et al., ParaRev: Building a dataset for Scientific Paragraph Revision annotated with revision instruction (WRAICOGS 2025)."
            }
        })
    return records, excluded

def acquire_pararev(output_path: str | Path, raw_dir: str | Path, accept_license: bool = False) -> dict[str, Any]:
    if not accept_license:
        raise ValueError("ParaRev declares CC BY-NC-SA 4.0. Re-run with --accept-license only if your use is non-commercial and you can comply with attribution and share-alike terms.")
    raw_root = Path(raw_dir)
    raw_root.mkdir(parents=True, exist_ok=True)
    raw_path = raw_root / FILENAME
    request = urllib.request.Request(DOWNLOAD_URL, headers={"User-Agent": "Og-AWC/0.1 dataset-acquisition"})
    with urllib.request.urlopen(request, timeout=90) as response, raw_path.open("wb") as target:
        while chunk := response.read(1024 * 1024):
            target.write(chunk)

    acquisition_date = datetime.now(timezone.utc).date().isoformat()
    rows: list[dict[str, Any]] = []
    with raw_path.open(encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, 1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"ParaRev JSONL line {line_no} is invalid: {exc.msg}") from exc
            if not isinstance(row, dict):
                raise ValueError(f"ParaRev JSONL line {line_no} is not an object")
            rows.append(row)

    records, excluded = convert_pararev_rows(rows, acquisition_date)
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="\n") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")

    manifest = {
        "source_id": SOURCE_ID,
        "source_url": REPO_URL,
        "source_revision": REVISION,
        "source_file": FILENAME,
        "license": LICENSE_ID,
        "license_url": "https://creativecommons.org/licenses/by-nc-sa/4.0/",
        "acquisition_date": acquisition_date,
        "raw_file_sha256": sha256_file(raw_path),
        "input_rows": len(rows),
        "revision_pairs_written": len(records),
        "rows_excluded_missing_required_fields": excluded,
        "raw_path": str(raw_path),
        "normalized_path": str(output),
        "publication_status": "local_only_pending_rights_and_attribution_review",
        "warning": "ParaRev is derived from CASIMIR. Do not combine with CASIMIR records as independent examples. This importer does not grant commercial-use rights or resolve underlying article rights."
    }
    manifest_path = output.with_suffix(".manifest.json")
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest

# Full ParaRev corpus (unannotated revision pairs)
FULL_FILENAME = "pararev_full_without_annotation.jsonl"
FULL_DOWNLOAD_URL = f"{REPO_URL}/resolve/{REVISION}/{FULL_FILENAME}?download=true"


def _iter_jsonl(path: Path):
    """Yield JSON objects from a JSONL file with line-specific errors."""
    with path.open(encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, 1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"ParaRev JSONL line {line_no} is invalid: {exc.msg}"
                ) from exc
            if not isinstance(row, dict):
                raise ValueError(f"ParaRev JSONL line {line_no} is not an object")
            yield line_no, row


def _pararev_full_record(
    row: dict[str, Any],
    row_number: int,
    acquisition_date: str,
    version_to_paper: dict[str, str],
) -> dict[str, Any] | None:
    """Normalize one row using the actual full-file hyphenated field names."""
    original = row.get("parag-1")
    revised = row.get("parag-2")
    source_version_id = row.get("id_source")
    target_version_id = row.get("id_target")
    paragraph_id = row.get("id_paragraph")
    if not all(
        isinstance(value, str) and value.strip()
        for value in (original, revised, source_version_id, target_version_id, paragraph_id)
    ):
        return None

    source_version_id = source_version_id.strip()
    target_version_id = target_version_id.strip()
    paragraph_id = paragraph_id.strip()
    pair_key = f"{paragraph_id}:{source_version_id}:{target_version_id}"
    return {
        "record_id": "pararev-" + hashlib.sha256(pair_key.encode("utf-8")).hexdigest()[:20],
        "source_id": SOURCE_ID,
        "paper_id": version_to_paper[source_version_id],
        "record_type": "revision_pair",
        "original_text": original.strip(),
        "revised_text": revised.strip(),
        "split": "unassigned",
        "edit_labels": [],
        "provenance": {
            "source_url": REPO_URL,
            "license_id": LICENSE_ID,
            "acquisition_date": acquisition_date,
            "source_record_id": paragraph_id,
            "reviewer": None,
            "notes": (
                "ParaRev full unannotated subset. Source fields parag-1/id_source "
                "and parag-2/id_target. The 641-row annotated evaluation subset is "
                "included in this full corpus; do not count it as an independent source."
            ),
            "source_version": REVISION,
            "source_file": FULL_FILENAME,
            "source_row_number": row_number,
            "source_article_version_id": source_version_id,
            "source_target_id": target_version_id,
            "source_paragraph_index": row.get("index_paragraph"),
            "source_sentences_1": row.get("list-sentences-1"),
            "source_sentences_2": row.get("list-sentences-2"),
            "license_url": "https://creativecommons.org/licenses/by-nc-sa/4.0/",
            "attribution": (
                "Jourdan et al., ParaRev: Building a dataset for Scientific Paragraph "
                "Revision annotated with revision instruction (WRAICOGS 2025)."
            ),
        },
    }


def convert_pararev_full_rows(
    rows: list[dict[str, Any]], acquisition_date: str
) -> tuple[list[dict[str, Any]], int]:
    """Convert full-corpus rows; expects upstream's hyphenated text field names."""
    version_to_paper = _article_component_ids(rows)
    records = []
    excluded = 0
    for row_number, row in enumerate(rows, 1):
        record = _pararev_full_record(row, row_number, acquisition_date, version_to_paper)
        if record is None:
            excluded += 1
        else:
            records.append(record)
    return records, excluded


def acquire_pararev_full(
    output_path: str | Path,
    raw_dir: str | Path,
    accept_license: bool = False,
) -> dict[str, Any]:
    """Download and normalize the 48k-pair ParaRev full file locally.

    A first streaming pass collects only article-version edges for paper grouping;
    a second pass writes normalized pairs, avoiding loading the 152 MB JSONL into RAM.
    """
    if not accept_license:
        raise ValueError(
            "ParaRev declares CC BY-NC-SA 4.0. Re-run with --accept-license only "
            "if your use is non-commercial and you can comply with attribution "
            "and share-alike terms."
        )

    raw_root = Path(raw_dir)
    raw_root.mkdir(parents=True, exist_ok=True)
    raw_path = raw_root / FULL_FILENAME
    partial_path = raw_path.with_suffix(raw_path.suffix + ".part")
    request = urllib.request.Request(
        FULL_DOWNLOAD_URL,
        headers={"User-Agent": "Og-AWC/0.1 dataset-acquisition"},
    )
    try:
        with urllib.request.urlopen(request, timeout=180) as response, partial_path.open("wb") as target:
            while chunk := response.read(1024 * 1024):
                target.write(chunk)
        partial_path.replace(raw_path)
    finally:
        if partial_path.exists():
            partial_path.unlink()

    acquisition_date = datetime.now(timezone.utc).date().isoformat()
    version_edges: list[dict[str, Any]] = []
    input_rows = 0
    for _, row in _iter_jsonl(raw_path):
        input_rows += 1
        version_edges.append({
            "id_source": row.get("id_source"),
            "id_target": row.get("id_target"),
        })
    version_to_paper = _article_component_ids(version_edges)

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary_output = output.with_suffix(output.suffix + ".tmp")
    written = 0
    excluded = 0
    try:
        with temporary_output.open("w", encoding="utf-8", newline="\n") as handle:
            for row_number, row in _iter_jsonl(raw_path):
                record = _pararev_full_record(
                    row, row_number, acquisition_date, version_to_paper
                )
                if record is None:
                    excluded += 1
                    continue
                handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
                written += 1
        temporary_output.replace(output)
    finally:
        if temporary_output.exists():
            temporary_output.unlink()

    manifest = {
        "source_id": SOURCE_ID,
        "subset": "pararev_full",
        "source_url": REPO_URL,
        "source_revision": REVISION,
        "source_file": FULL_FILENAME,
        "license": LICENSE_ID,
        "license_url": "https://creativecommons.org/licenses/by-nc-sa/4.0/",
        "acquisition_date": acquisition_date,
        "raw_file_sha256": sha256_file(raw_path),
        "input_rows": input_rows,
        "revision_pairs_written": written,
        "rows_excluded_missing_required_fields": excluded,
        "article_version_ids": len(version_to_paper),
        "paper_components": len(set(version_to_paper.values())),
        "raw_path": str(raw_path),
        "normalized_path": str(output),
        "publication_status": "local_only_pending_rights_and_attribution_review",
        "overlap_policy": (
            "The 641-row manually annotated ParaRev subset is included in this full "
            "corpus. It is not an independent dataset; matching record IDs identify "
            "the same paragraph pair across the two normalized files."
        ),
        "warning": (
            "ParaRev is derived from CASIMIR. Do not combine with CASIMIR records "
            "as independent examples. This importer does not grant commercial-use "
            "rights or resolve underlying article rights."
        ),
    }
    output.with_suffix(".manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    return manifest
