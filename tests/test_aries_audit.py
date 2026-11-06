import pytest

from og_awc.aries_audit import classify_mismatch, is_normalized_equivalent


@pytest.mark.parametrize("left,right,expected", [
    ("same text", "same text", "exact_match"),
    ("a  b", "a b", "whitespace_only"),
    ("a\nb", "a\n\nb", "paragraph_boundary"),
    ("cafe\u0301", "café", "unicode_normalization"),
    ("the original sentence", "the revised sentence", "substantive_text"),
    ("one two three", "one three two", "substantive_text"),
    ("paragraph one\n\nparagraph two", "paragraph one\n\nparagraph three", "substantive_text"),
])
def test_classify_mismatch(left, right, expected):
    assert classify_mismatch(left, right) == expected


def test_classification_does_not_modify_input_strings():
    original = "first\n\nsecond"
    reconstructed = "first\nsecond"
    classify_mismatch(reconstructed, original)
    assert reconstructed == "first\nsecond"
    assert original == "first\n\nsecond"


def test_normalized_equivalence_requires_both_sides_to_be_safe_classes():
    assert is_normalized_equivalent("exact_match", "paragraph_boundary")
    assert is_normalized_equivalent("whitespace_only", "unicode_normalization")
    assert not is_normalized_equivalent("paragraph_boundary", "substantive_text")
    assert not is_normalized_equivalent("substantive_text", "substantive_text")
