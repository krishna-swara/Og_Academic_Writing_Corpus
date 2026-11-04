import json
from pathlib import Path

from og_awc.deduplicate import deduplicate
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
