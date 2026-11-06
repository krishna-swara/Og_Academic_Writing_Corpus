#!/usr/bin/env python3
# ARIES v5: Full audit fixes implemented per v4 review
# Core fixes: back-matter fusion, strict index validation, full input accounting, explicit output separation, mismatch classification, complete manifest hashing
import json
import os
import hashlib
import sys
from pathlib import Path
from datetime import datetime
# Add official ARIES module path to sys.path (matches working v3/v4 configurations)
sys.path.append("/Users/sam/Downloads/aries-master")
from aries.alignment.doc_edits import DocEdits, ParagraphEdit  # Correct official ARIES import (matches all prior scripts)
from aries.util.s2orc import fuse_back_matter as official_fuse_back_matter  # Use official ARIES back-matter fusion
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from og_awc.aries_audit import classify_mismatch, is_normalized_equivalent

# Configuration (correct paths matching all prior v3/v4 implementations)
RAW_ARIES_DIR = Path("raw_sources/aries")
PAPER_EDITS_PATH = RAW_ARIES_DIR / "paper_edits.jsonl"
S2ORC_DIR = RAW_ARIES_DIR / "s2orc"
OUTPUT_DIR = Path("processed/aries_full_v5")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
# Test mode: process only first N documents (30-100 per audit recommendation)
TEST_MODE = os.environ.get("ARIES_TEST_MODE", "0") == "1"
TEST_DOC_LIMIT = int(os.environ.get("ARIES_TEST_DOC_LIMIT", "50"))

# We use the official ARIES fuse_back_matter() function imported as official_fuse_back_matter()
# This ensures 100% match with ARIES's paragraph indexing, ordering, and separator logic

# Fix 2: Strict index validation (reject negative/non-integer/out-of-range indices)
# Match official ARIES implementation: fuse_back_matter() merges into pdf_parse.body_text
def get_paragraph_text_by_index(paper, idx):
    # Official ARIES fuse_back_matter() merges back matter into paper["pdf_parse"]["body_text"]
    if "pdf_parse" not in paper or "body_text" not in paper["pdf_parse"]:
        raise ValueError("Paper not processed with official ARIES fuse_back_matter()")
    body = paper["pdf_parse"]["body_text"]
    # Strict index validation per user's requirements (reject negative/out-of-range indices)
    if not isinstance(idx, int) or idx < 0 or idx >= len(body):
        raise IndexError(f"Invalid paragraph index: {idx} (valid range: 0-{len(body)-1})")
    return body[idx]["text"]

# Fix 3: Load paper and fuse back matter immediately
def load_s2orc_paper(pdf_id, s2orc_dir):
    paper_path = s2orc_dir / f"{pdf_id}.json"
    if not paper_path.exists():
        return None
    with open(paper_path, 'r') as f:
        paper = json.load(f)
    # Apply OFFICIAL ARIES back-matter fusion to ensure EXACT paragraph indexing match
    # Fix: Some ARIES versions return the modified paper instead of modifying in-place
    fused_paper = official_fuse_back_matter(paper)
    if fused_paper is not None:
        paper = fused_paper
    return paper

# Reconstruct text from indices using validated paragraph lookup
def reconstruct_text_from_indices(paper, indices):
    texts = []
    for idx in indices:
        try:
            text = get_paragraph_text_by_index(paper, idx)
            texts.append(text)
        except IndexError:
            raise
    # Match official separator exactly (no trailing newlines)
    return "\n\n".join(texts)

# Calculate file hash for provenance
def calculate_file_hash(file_path):
    """Calculate SHA-256 hash of a file for provenance tracking"""
    hash_sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()

def main():
    # Fix 4: Full metrics reconciliation per audit requirements
    metrics = {
        "raw_input_edits": 0,
        "unique_edits": 0,
        "duplicate_composite_keys": 0,
        "missing_source_or_target_papers": 0,
        "invalid_indices": 0,
        "additions": 0,
        "deletions": 0,
        "empty_malformed_edits": 0,
        "revision_pairs_checked": 0,
        "exact_matches": 0,
        "mismatches": 0,
        "normalized_matches": 0,
        "normalized_only_matches": 0,
        "records_with_formatting_only_mismatch": 0,
        "strict_parity_rate": 0.0,
        "normalized_parity_rate": 0.0,
        "reconstruction_exceptions": 0,
        "whitespace_only_mismatch_sides": 0,
        "records_with_whitespace_only_mismatch": 0,
        "unicode_normalization_mismatches": 0,
        "paragraph_boundary_mismatches": 0,
        "substantive_text_mismatches": 0,
        "invalid_reconstruction_mismatches": 0
    }
    seen_unique_keys = set()
    docs_processed = 0

    # Fix 5: Capture all output files per audit's explicit separation
    validated_pairs = []  # Exact-parity non-identical pairs
    revision_events = []  # All additions/deletions
    parity_audit = []     # All checked revision pairs (including mismatches)
    reconstruction_errors = []  # All exceptions/invalid records

    # Calculate input hashes for manifest (including S2ORC inputs and script)
    script_hash = calculate_file_hash(Path(__file__))
    paper_edits_hash = calculate_file_hash(PAPER_EDITS_PATH)
    # Collect S2ORC file hashes for manifest
    s2orc_hashes = {}
    for s2orc_file in S2ORC_DIR.glob("*.json"):
        s2orc_hashes[s2orc_file.name] = calculate_file_hash(s2orc_file)

    # Process all documents (stop at TEST_DOC_LIMIT if in test mode)
    with open(PAPER_EDITS_PATH, 'r') as f:
        for line in f:
            if TEST_MODE and docs_processed >= TEST_DOC_LIMIT:
                break
            record = json.loads(line.strip())
            doc_id = record["doc_id"]
            source_pdf_id = record["source_pdf_id"]
            target_pdf_id = record["target_pdf_id"]
            edits_list = record["edits"]

            # Fix 6: Count raw edits BEFORE any processing to ensure full accounting
            for _ in edits_list:
                metrics["raw_input_edits"] += 1

            # Deduplicate and count every edit before paper loading. Missing-paper
            # records must still participate in the unique-edit reconciliation.
            unique_edit_records = []
            for edit_rec in sorted(edits_list, key=lambda x: x["edit_id"]):
                unique_key = (doc_id, edit_rec["edit_id"])
                if unique_key in seen_unique_keys:
                    metrics["duplicate_composite_keys"] += 1
                    continue
                seen_unique_keys.add(unique_key)
                metrics["unique_edits"] += 1
                unique_edit_records.append(edit_rec)

            # Load papers with fused back matter
            source_paper = load_s2orc_paper(source_pdf_id, S2ORC_DIR)
            target_paper = load_s2orc_paper(target_pdf_id, S2ORC_DIR)
            if not source_paper or not target_paper:
                metrics["missing_source_or_target_papers"] += len(unique_edit_records)
                docs_processed += 1
                if TEST_MODE and docs_processed % 10 == 0:
                    print(f"Processed {docs_processed}/{TEST_DOC_LIMIT} documents...")
                continue

            official_edits = DocEdits.from_list(source_paper, target_paper, unique_edit_records)

            for edit_rec in unique_edit_records:
                edit_id = edit_rec["edit_id"]
                source_idxs = edit_rec["source_idxs"]
                target_idxs = edit_rec["target_idxs"]

                try:
                    official_edit = official_edits.edit_ids_map[edit_id]
                    official_source = official_edit.get_source_text()
                    official_target = official_edit.get_target_text()

                    # Classify additions/deletions
                    if official_source == "" and official_target != "":
                        metrics["additions"] += 1
                        revision_events.append({
                            "doc_id": doc_id, "edit_id": edit_id,
                            "source_pdf_id": source_pdf_id, "target_pdf_id": target_pdf_id,
                            "type": "addition", "target_text": official_target
                        })
                        continue
                    if official_target == "" and official_source != "":
                        metrics["deletions"] += 1
                        revision_events.append({
                            "doc_id": doc_id, "edit_id": edit_id,
                            "source_pdf_id": source_pdf_id, "target_pdf_id": target_pdf_id,
                            "type": "deletion", "source_text": official_source
                        })
                        continue
                    if official_source == "" and official_target == "":
                        metrics["empty_malformed_edits"] += 1
                        continue

                    # Reconstruct both sides first. Only successful comparisons count as checked.
                    our_source = reconstruct_text_from_indices(source_paper, source_idxs)
                    our_target = reconstruct_text_from_indices(target_paper, target_idxs)
                    metrics["revision_pairs_checked"] += 1

                    # Add debug logging for first few comparisons to identify issues
                    if len(parity_audit) < 5:
                        print(f"DEBUG: Edit {edit_id} - Source comparison:")
                        print(f"OUR_SOURCE:\n{repr(our_source)}")
                        print(f"OFFICIAL_SOURCE:\n{repr(official_source)}")
                        print(f"EQUAL? {our_source == official_source}")
                        print(f"OUR_TARGET:\n{repr(our_target)}")
                        print(f"OFFICIAL_TARGET:\n{repr(official_target)}")
                        print(f"TARGET EQUAL? {our_target == official_target}\n---")
                    
                    # Add to parity audit log with classification
                    source_class = classify_mismatch(our_source, official_source)
                    target_class = classify_mismatch(our_target, official_target)
                    audit_entry = {
                        "doc_id": doc_id, "edit_id": edit_id,
                        "source_pdf_id": source_pdf_id, "target_pdf_id": target_pdf_id,
                        "source_idxs": source_idxs, "target_idxs": target_idxs,
                        "official_source": official_source, "our_source": our_source,
                        "source_mismatch_class": source_class,
                        "official_target": official_target, "our_target": our_target,
                        "target_mismatch_class": target_class,
                        "normalized_parity_match": is_normalized_equivalent(source_class, target_class)
                    }
                    parity_audit.append(audit_entry)

                    if source_class == "whitespace_only" or target_class == "whitespace_only":
                        metrics["records_with_whitespace_only_mismatch"] += 1

                    normalized_pair = is_normalized_equivalent(source_class, target_class)
                    if normalized_pair:
                        metrics["normalized_matches"] += 1
                        if source_class != "exact_match" or target_class != "exact_match":
                            metrics["normalized_only_matches"] += 1
                            metrics["records_with_formatting_only_mismatch"] += 1

                    if source_class == "exact_match" and target_class == "exact_match":
                        metrics["exact_matches"] += 1
                        validated_pairs.append({
                            "doc_id": doc_id, "edit_id": edit_id,
                            "source_pdf_id": source_pdf_id, "target_pdf_id": target_pdf_id,
                            "source_text": official_source, "target_text": official_target
                        })
                    else:
                        metrics["mismatches"] += 1
                        # Update category-specific counters
                        if source_class != "exact_match":
                            if source_class == "whitespace_only":
                                metrics["whitespace_only_mismatch_sides"] += 1
                            elif source_class == "unicode_normalization":
                                metrics["unicode_normalization_mismatches"] +=1
                            elif source_class == "paragraph_boundary":
                                metrics["paragraph_boundary_mismatches"] +=1
                            elif source_class == "substantive_text":
                                metrics["substantive_text_mismatches"] +=1
                        if target_class != "exact_match":
                            if target_class == "whitespace_only":
                                metrics["whitespace_only_mismatch_sides"] += 1
                            elif target_class == "unicode_normalization":
                                metrics["unicode_normalization_mismatches"] +=1
                            elif target_class == "paragraph_boundary":
                                metrics["paragraph_boundary_mismatches"] +=1
                            elif target_class == "substantive_text":
                                metrics["substantive_text_mismatches"] +=1

                except IndexError as e:
                    metrics["invalid_indices"] += 1
                    reconstruction_errors.append({
                        "doc_id": doc_id, "edit_id": edit_id, "error": str(e), "type": "invalid_index"
                    })
                except Exception as e:
                    metrics["reconstruction_exceptions"] += 1
                    reconstruction_errors.append({
                        "doc_id": doc_id, "edit_id": edit_id, "error": str(e), "type": "general_exception"
                    })

            docs_processed += 1
            if docs_processed % 10 == 0:
                print(f"Processed {docs_processed}/{TEST_DOC_LIMIT if TEST_MODE else 1720} documents...")

    # Reconciliation: every unique edit must be assigned to one terminal category.
    terminal_total = (
        metrics["missing_source_or_target_papers"]
        + metrics["additions"]
        + metrics["deletions"]
        + metrics["empty_malformed_edits"]
        + metrics["revision_pairs_checked"]
        + metrics["invalid_indices"]
        + metrics["reconstruction_exceptions"]
    )
    if terminal_total != metrics["unique_edits"]:
        raise RuntimeError(
            f"Edit accounting failed: terminal categories={terminal_total}, "
            f"unique_edits={metrics['unique_edits']}"
        )
    if metrics["exact_matches"] + metrics["mismatches"] != metrics["revision_pairs_checked"]:
        raise RuntimeError("Parity accounting failed: exact_matches + mismatches != revision_pairs_checked")

    # Rates use successfully reconstructed revision pairs as denominator.
    denominator = metrics["revision_pairs_checked"]
    if denominator:
        metrics["strict_parity_rate"] = round(
            metrics["exact_matches"] / denominator * 100, 4
        )
        metrics["normalized_parity_rate"] = round(
            metrics["normalized_matches"] / denominator * 100, 4
        )

    # Save all outputs to v5 directory
    pairs_path = OUTPUT_DIR / "aries_validated_revision_pairs.jsonl"
    events_path = OUTPUT_DIR / "aries_revision_events.jsonl"
    audit_path = OUTPUT_DIR / "aries_parity_audit.jsonl"
    errors_path = OUTPUT_DIR / "aries_reconstruction_errors.jsonl"
    metrics_path = OUTPUT_DIR / "aries_reconstruction_metrics.json"
    manifest_path = OUTPUT_DIR / "aries_reconstruction_manifest.json"
    samples_path = OUTPUT_DIR / "parity_failure_samples.json"

    with open(pairs_path, 'w') as f:
        for pair in validated_pairs:
            f.write(json.dumps(pair) + "\n")
    with open(events_path, 'w') as f:
        for event in revision_events:
            f.write(json.dumps(event) + "\n")
    with open(audit_path, 'w') as f:
        for entry in parity_audit:
            f.write(json.dumps(entry) + "\n")
    with open(errors_path, 'w') as f:
        for err in reconstruction_errors:
            f.write(json.dumps(err) + "\n")
    with open(metrics_path, 'w') as f:
        json.dump(metrics, f, indent=2)

    # Generate 30 failure samples for audit
    failure_samples = []
    for entry in parity_audit:
        if entry["source_mismatch_class"] != "exact_match" or entry["target_mismatch_class"] != "exact_match":
            failure_samples.append(entry)
            if len(failure_samples) >= 30:
                break
    with open(samples_path, 'w') as f:
        json.dump(failure_samples, f, indent=2)

    # Fix 7: Complete manifest with all required hashes (script, S2ORC, all outputs)
    manifest = {
        "run_timestamp": datetime.now().isoformat(),
        "test_mode": TEST_MODE,
        "test_doc_limit": TEST_DOC_LIMIT if TEST_MODE else None,
        "script_hash": script_hash,
        "input_file_hashes": {
            "paper_edits.jsonl": paper_edits_hash,
            "s2orc_files": s2orc_hashes
        },
        "output_file_hashes": {
            "aries_validated_revision_pairs.jsonl": calculate_file_hash(pairs_path),
            "aries_revision_events.jsonl": calculate_file_hash(events_path),
            "aries_parity_audit.jsonl": calculate_file_hash(audit_path),
            "aries_reconstruction_errors.jsonl": calculate_file_hash(errors_path),
            "aries_reconstruction_metrics.json": calculate_file_hash(metrics_path),
            "parity_failure_samples.json": calculate_file_hash(samples_path)
        },
        "python_version": sys.version,
        "aries_implementation_version": os.environ.get("ARIES_GIT_COMMIT", "UNSPECIFIED"),
        "audit_note": "Set ARIES_GIT_COMMIT to the exact ARIES source commit before running."
    }
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)

    # Final summary
    print("\n=== ARIES v5 Test Run Complete ===")
    print(f"Documents processed: {docs_processed}")
    print(f"Raw input edits: {metrics['raw_input_edits']}")
    print(f"Unique edits: {metrics['unique_edits']}")
    print(f"Revision pairs checked: {metrics['revision_pairs_checked']}")
    print(f"Strict parity: {metrics['strict_parity_rate']:.2f}% ({metrics['exact_matches']} exact pairs)")
    print(f"Normalized parity: {metrics['normalized_parity_rate']:.2f}% ({metrics['normalized_matches']} normalized-equivalent pairs)")
    print(f"Normalized-only matches: {metrics['normalized_only_matches']}")
    print(f"Total strict mismatches: {metrics['mismatches']}")
    print(f"Formatting-only mismatch records: {metrics['records_with_formatting_only_mismatch']}")
    print(f"Whitespace-only mismatch sides: {metrics['whitespace_only_mismatch_sides']}")
    print(f"Records with whitespace-only mismatch: {metrics['records_with_whitespace_only_mismatch']}")
    print(f"Additions: {metrics['additions']}, Deletions: {metrics['deletions']}")
    print(f"All outputs saved to: {OUTPUT_DIR}")

if __name__ == "__main__":
    main()