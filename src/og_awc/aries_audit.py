"""Pure text-parity classification helpers for the ARIES audit.

These functions classify formatting/normalization differences without modifying
source text. Normalized parity is a secondary diagnostic, never a replacement
for strict character-for-character parity.
"""
import re
import unicodedata

NORMALIZED_EQUIVALENT_CLASSES = {
    "exact_match",
    "unicode_normalization",
    "whitespace_only",
    "paragraph_boundary",
}


def classify_mismatch(our_text, official_text):
    """Return the difference class while preserving both original strings."""
    our_text = our_text or ""
    official_text = official_text or ""
    if our_text == official_text:
        return "exact_match"

    our_nfc = unicodedata.normalize("NFC", our_text)
    official_nfc = unicodedata.normalize("NFC", official_text)
    if our_nfc == official_nfc:
        return "unicode_normalization"

    def paragraphs(value):
        value = value.replace("\r\n", "\n").replace("\r", "\n")
        parts = [
            part for part in re.split(r"\n\s*\n+", value.strip())
            if part.strip()
        ]
        return [
            re.sub(r"[ \t\f\v]+", " ", part).strip()
            for part in parts
        ]

    our_parts = paragraphs(our_nfc)
    official_parts = paragraphs(official_nfc)

    if our_parts == official_parts:
        return "whitespace_only"

    flatten = lambda parts: re.sub(r"\s+", " ", " ".join(parts)).strip()
    if flatten(our_parts) == flatten(official_parts):
        return "paragraph_boundary"

    return "substantive_text"


def is_normalized_equivalent(source_class, target_class):
    """True only when both sides differ, at most, by formatting/normalization."""
    return (
        source_class in NORMALIZED_EQUIVALENT_CLASSES
        and target_class in NORMALIZED_EQUIVALENT_CLASSES
    )
