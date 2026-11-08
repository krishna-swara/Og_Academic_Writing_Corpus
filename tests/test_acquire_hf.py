from og_awc.acquire_hf import convert_coedit_rows
from og_awc.validation import validate_record


def test_coedit_conversion_preserves_task_and_marks_pending_review():
    rows = [{
        "_id": 12,
        "task": "gec",
        "src": "Improve grammar: This are a sentence.",
        "tgt": "This is a sentence.",
    }]
    records, excluded = convert_coedit_rows(rows, "2026-11-08", "abc123")
    assert excluded == 0
    assert len(records) == 1
    record = records[0]
    assert record["original_text"] == "This are a sentence."
    assert record["revised_text"] == "This is a sentence."
    assert record["edit_labels"] == ["gec"]
    assert record["paper_id"] == "not_provided"\n    assert record["split_group_id"] == record["record_id"]
    assert record["meaning_preserved"] is False
    assert record["human_review_status"] == "pending"
    assert record["provenance"]["rights_review_status"] == "pending_upstream_lineage_review"
    assert record["provenance"]["text_mining_permitted"] is False
    assert validate_record(record) == []


def test_coedit_conversion_excludes_incomplete_rows():
    records, excluded = convert_coedit_rows(
        [{"_id": 1, "src": "source", "tgt": ""}],
        "2026-11-08",
        "abc123",
    )
    assert records == []
    assert excluded == 1
