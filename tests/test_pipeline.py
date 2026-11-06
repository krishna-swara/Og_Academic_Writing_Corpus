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
    from og_awc.acquire import SOURCE_CONFIGS
    config = SOURCE_CONFIGS["pararev_annotated"]
    records, excluded = convert_pararev_rows(
        rows,
        "2026-11-05"
    )
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
    records, excluded = convert_pararev_rows(
        rows,
        "2026-11-05"
    )
    assert records == []
    assert excluded == 1



def test_pararev_full_import_maps_hyphenated_fields_and_metadata():
    from og_awc.acquire import convert_pararev_rows
    
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
    records, excluded = convert_pararev_rows(
        rows,
        "2026-11-05"
    )
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


def test_jfleg_converter_preserves_four_human_references_and_upstream_splits(tmp_path):
    from og_awc.acquire_auxiliary import convert_jfleg_files

    for split, folder in [("validation", "dev"), ("test", "test")]:
        (tmp_path / folder).mkdir()
        (tmp_path / folder / f"{folder}.src").write_text("Original sentence.\n", encoding="utf-8")
        for index in range(4):
            (tmp_path / folder / f"{folder}.ref{index}").write_text(
                f"Human correction {index}.\n", encoding="utf-8"
            )
    records, counts = convert_jfleg_files(tmp_path, "2026-11-05")
    assert counts == {"validation": 1, "test": 1}
    assert len(records) == 8
    assert {r["split"] for r in records} == {"validation", "test"}
    assert len({r["paper_id"] for r in records if r["split"] == "validation"}) == 1
    assert len({r["paper_id"] for r in records if r["split"] == "test"}) == 1


def test_pararev_full_import_supports_underscore_field_formats():
    from og_awc.acquire import convert_pararev_full_rows

    rows = [{
        "id_source": "article-version-a",
        "id_target": "article-version-b",
        "index_paragraph": 12,
        "id_paragraph": "article-version-a.article-version-b.12",
        "parag_1": "Original full paragraph with underscores.",
        "parag_2": "Revised full paragraph with underscores.",
        "list_sentences_1": [{"text": "Original sentence."}],
        "list_sentences_2": [{"text": "Revised sentence."}],
    }]
    records, excluded = convert_pararev_full_rows(rows, "2026-11-05")
    assert excluded == 0
    assert len(records) == 1
    record = records[0]
    assert record["original_text"] == "Original full paragraph with underscores."
    assert record["revised_text"] == "Revised full paragraph with underscores."
    assert validate_record(record) == []


def test_pararev_full_import_handles_mixed_field_formats():
    from og_awc.acquire import convert_pararev_full_rows

    rows = [
        # First row uses hyphenated format
        {
            "id_source": "v1",
            "id_target": "v2",
            "id_paragraph": "p1",
            "parag-1": "Original with hyphens.",
            "parag-2": "Revised with hyphens.",
        },
        # Second row uses underscore format
        {
            "id_source": "v3",
            "id_target": "v4",
            "id_paragraph": "p2",
            "parag_1": "Original with underscores.",
            "parag_2": "Revised with underscores.",
        },
        # Third row mixes formats (should still work)
        {
            "id_source": "v5",
            "id_target": "v6",
            "id_paragraph": "p3",
            "parag-1": "Original with hyphen.",
            "parag_2": "Revised with underscore.",
        }
    ]
    records, excluded = convert_pararev_full_rows(rows, "2026-11-05")
    assert excluded == 0
    assert len(records) == 3
    # Verify all records were correctly imported
    assert records[0]["original_text"] == "Original with hyphens."
    assert records[0]["revised_text"] == "Revised with hyphens."
    assert records[1]["original_text"] == "Original with underscores."
    assert records[1]["revised_text"] == "Revised with underscores."
    assert records[2]["original_text"] == "Original with hyphen."
    assert records[2]["revised_text"] == "Revised with underscore."
    # All records should pass validation
    for record in records:
        assert validate_record(record) == []


def test_pararev_annotated_import_supports_both_field_formats():
    from og_awc.acquire import convert_pararev_rows

    # Test hyphenated format
    rows_hyphenated = [{
        "id_paragraph": "paragraph-7",
        "id_source": "paper-1",
        "id_target": "version-2",
        "parag-1": "Original with hyphens.",
        "parag-2": "Revised with hyphens.",
    }]
    records1, excluded1 = convert_pararev_rows(rows_hyphenated, "2026-11-05")
    assert excluded1 == 0
    assert len(records1) == 1
    # Verify hyphenated format works correctly
    assert records1[0]["original_text"] == "Original with hyphens."
    assert records1[0]["revised_text"] == "Revised with hyphens."
    assert records1[0]["source_id"] == "pararev_annotated"
    
    # Test underscore format
    rows_underscore = [{
        "id_paragraph": "paragraph-8",
        "id_source": "paper-2",
        "id_target": "version-3",
        "parag_1": "Original with underscores.",
        "parag_2": "Revised with underscores.",
    }]
    records2, excluded2 = convert_pararev_rows(rows_underscore, "2026-11-05")
    assert excluded2 == 0
    assert len(records2) == 1
    # Verify underscore format works correctly
    assert records2[0]["original_text"] == "Original with underscores."
    assert records2[0]["revised_text"] == "Revised with underscores."
    assert records2[0]["source_id"] == "pararev_annotated"
    # Validate both records
    combined_records = records1 + records2
    assert all(validate_record(r) == [] for r in combined_records)


def test_jfleg_converter_rejects_mismatched_reference_files(tmp_path):
    from og_awc.acquire_auxiliary import convert_jfleg_files

    (tmp_path / "dev").mkdir()
    (tmp_path / "test").mkdir()
    for folder in ("dev", "test"):
        (tmp_path / folder / f"{folder}.src").write_text("Source.\n", encoding="utf-8")
        for index in range(4):
            (tmp_path / folder / f"{folder}.ref{index}").write_text(
                "Correction.\n" if index else "", encoding="utf-8"
            )
    with pytest.raises(ValueError, match="line counts"):
        convert_jfleg_files(tmp_path, "2026-11-05")


def test_acl_bibtex_parser_handles_nested_braces():
    from og_awc.acquire_auxiliary import _bib_entries, _bib_field

    entries = list(_bib_entries(
        "@inproceedings{sample-2024-test, title={A {Nested} Title}, "
        "author={Doe, Jane}, year={2024}}"
    ))
    assert len(entries) == 1
    entry = entries[0]
    assert _bib_field(entry, "title") == "A {Nested} Title"
    assert _bib_field(entry, "author") == "Doe, Jane"
    assert _bib_field(entry, "year") == "2024"