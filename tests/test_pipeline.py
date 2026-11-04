import json
from pathlib import Path

import pytest

from og_awc.acquire import convert_pararev_rows
from og_awc.deduplicate import deduplicate
from og_awc.pipeline import prepare_dataset
from og_awc.split import assign_splits, check_paper_leakage
from og_awc.validation import validate_jsonl, validate_record

FIXTURE = Path(__file__).parent / "fixtures" / "sample_records.jsonl"


def test_fixture_jsonl_is_valid():
    assert validate_jsonl(FIXTURE) == []


def test_source_only_cannot_have_fabricated_revision():
    record = json.loads(FIXTURE.read_text(encoding="utf-8").splitlines()[0])
    record["record_type"] = "source_only"
    record["revised_text"] = "Invented revision"
    assert any("fabricated" in err for err in validate_record(record))


def test_revision_pair_requires_real_revision():
    record = json.loads(FIXTURE.read_text(encoding="utf-8").splitlines()[0])
    record["record_type"] = "revision_pair"
    record["revised_text"] = None
    assert any("genuine" in err for err in validate_record(record))


def test_deduplication_keeps_first_occurrence():
    records = [
        {"record_type": "source_only", "original_text": "A   sentence.", "revised_text": None},
        {"record_type": "source_only", "original_text": "a sentence.", "revised_text": None},
    ]
    unique, duplicates = deduplicate(records)
    assert len(unique) == 1
    assert len(duplicates) == 1


def test_split_is_deterministic_and_paper_grouped():
    records = [
        {"paper_id": "paper-1", "record_id": "1"},
        {"paper_id": "paper-1", "record_id": "2"},
        {"paper_id": "paper-2", "record_id": "3"},
    ]
    first = assign_splits(records, seed="test")
    second = assign_splits(records, seed="test")
    assert first == second
    assert check_paper_leakage(first) == []


def test_prepare_pipeline_writes_splits_and_report(tmp_path):
    report = prepare_dataset(FIXTURE, tmp_path, seed="test-seed")
    assert report["input_records"] == 3
    assert report["unique_records"] == 3
    assert (tmp_path / "train.jsonl").exists()
    assert (tmp_path / "validation.jsonl").exists()
    assert (tmp_path / "test.jsonl").exists()
    assert json.loads((tmp_path / "report.json").read_text())["split_unit"] == "paper_id"


def test_prepare_rejects_invalid_input(tmp_path):
    bad = tmp_path / "bad.jsonl"
    bad.write_text('{"not":"a corpus record"}\n', encoding="utf-8")
    with pytest.raises(ValueError):
        prepare_dataset(bad, tmp_path / "out")


def test_pararev_import_maps_real_revision_and_provenance():
    rows = [{
        "id_paragraph": "paragraph-7",
        "id_source": "paper-1",
        "id_target": "version-2",
        "parag_1": "Original paragraph.",
        "parag_2": "Revised paragraph.",
        "annot_1": {"annotation": ["Concision"], "instruction": ""},
        "annot_2": None
    }]
    records, excluded = convert_pararev_rows(rows, "2026-11-05")
    assert excluded == 0
    assert len(records) == 1
    record = records[0]
    assert record["record_type"] == "revision_pair"
    assert record["original_text"] == "Original paragraph."
    assert record["revised_text"] == "Revised paragraph."
    assert record["paper_id"].startswith("pararev-paper-")
    assert record["provenance"]["license_id"] == "cc-by-nc-sa-4.0"
    assert record["provenance"]["source_annotations"]["annot_1"]["annotation"] == ["Concision"]
    assert validate_record(record) == []


def test_pararev_article_versions_share_one_paper_split_group():
    rows = [
        {"id_paragraph": "p1", "id_source": "version-a", "id_target": "version-b",
         "parag_1": "Original one.", "parag_2": "Revised one."},
        {"id_paragraph": "p2", "id_source": "version-b", "id_target": "version-c",
         "parag_1": "Original two.", "parag_2": "Revised two."},
        {"id_paragraph": "p3", "id_source": "version-x", "id_target": "version-y",
         "parag_1": "Other original.", "parag_2": "Other revised."},
    ]
    records, excluded = convert_pararev_rows(rows, "2026-11-05")
    assert excluded == 0
    assert records[0]["paper_id"] == records[1]["paper_id"]
    assert records[0]["paper_id"] != records[2]["paper_id"]


def test_pararev_paper_grouping_is_independent_of_row_order():
    rows = [
        {"id_paragraph": "p1", "id_source": "version-a", "id_target": "version-b",
         "parag_1": "Original one.", "parag_2": "Revised one."},
        {"id_paragraph": "p2", "id_source": "version-b", "id_target": "version-c",
         "parag_1": "Original two.", "parag_2": "Revised two."},
    ]
    forward, _ = convert_pararev_rows(rows, "2026-11-05")
    reverse, _ = convert_pararev_rows(list(reversed(rows)), "2026-11-05")
    assert {r["paper_id"] for r in forward} == {r["paper_id"] for r in reverse}


def test_pararev_import_excludes_missing_revision():
    rows = [{
        "id_paragraph": "paragraph-7",
        "id_source": "paper-1",
        "id_target": "version-2",
        "parag_1": "Original paragraph.",
        "parag_2": "",
    }]
    records, excluded = convert_pararev_rows(rows, "2026-11-05")
    assert records == []
    assert excluded == 1



def test_pararev_full_import_maps_hyphenated_fields_and_metadata():
    from og_awc.acquire import convert_pararev_full_rows

    rows = [{
        "id_source": "article-version-a",
        "id_target": "article-version-b",
        "index_paragraph": 12,
        "id_paragraph": "article-version-a.article-version-b.12",
        "parag-1": "Original full paragraph.",
        "parag-2": "Revised full paragraph.",
        "list-sentences-1": [{"text": "Original sentence."}],
        "list-sentences-2": [{"text": "Revised sentence."}],
    }]
    records, excluded = convert_pararev_full_rows(rows, "2026-11-05")
    assert excluded == 0
    assert len(records) == 1
    record = records[0]
    assert record["original_text"] == "Original full paragraph."
    assert record["revised_text"] == "Revised full paragraph."
    assert record["record_id"].startswith("pararev-")
    assert record["paper_id"].startswith("pararev-paper-")
    assert record["provenance"]["source_file"] == "pararev_full_without_annotation.jsonl"
    assert record["provenance"]["source_paragraph_index"] == 12
    assert record["provenance"]["source_sentences_1"] == [{"text": "Original sentence."}]
    assert validate_record(record) == []


def test_pararev_full_import_groups_connected_versions():
    from og_awc.acquire import convert_pararev_full_rows

    rows = [
        {"id_source": "v1", "id_target": "v2", "id_paragraph": "p1",
         "parag-1": "Original one.", "parag-2": "Revised one."},
        {"id_source": "v2", "id_target": "v3", "id_paragraph": "p2",
         "parag-1": "Original two.", "parag-2": "Revised two."},
        {"id_source": "v8", "id_target": "v9", "id_paragraph": "p3",
         "parag-1": "Other original.", "parag-2": "Other revised."},
    ]
    records, excluded = convert_pararev_full_rows(rows, "2026-11-05")
    assert excluded == 0
    assert records[0]["paper_id"] == records[1]["paper_id"]
    assert records[0]["paper_id"] != records[2]["paper_id"]


def test_pararev_full_and_annotated_subset_share_record_identity():
    from og_awc.acquire import convert_pararev_full_rows

    full_rows = [{
        "id_source": "version-a", "id_target": "version-b",
        "id_paragraph": "same-paragraph", "parag-1": "Same original.",
        "parag-2": "Same revised.",
    }]
    full_records, _ = convert_pararev_full_rows(full_rows, "2026-11-05")
    annotated_rows = [{
        "id_source": "version-a", "id_target": "version-b",
        "id_paragraph": "same-paragraph", "parag_1": "Same original.",
        "parag_2": "Same revised.",
    }]
    annotated_records, _ = convert_pararev_rows(annotated_rows, "2026-11-05")
    assert full_records[0]["record_id"] == annotated_records[0]["record_id"]


def test_pararev_full_import_excludes_incomplete_pair():
    from og_awc.acquire import convert_pararev_full_rows

    rows = [{
        "id_source": "version-a",
        "id_target": "version-b",
        "id_paragraph": "paragraph-1",
        "parag-1": "Original paragraph.",
        "parag-2": "",
    }]
    records, excluded = convert_pararev_full_rows(rows, "2026-11-05")
    assert records == []
    assert excluded == 1
