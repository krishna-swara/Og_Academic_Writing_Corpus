# ARIES v5.1 audit corrections

This branch preserves the original `audit/aries-v5` test run and adds a corrected runner.

## Changes
- Correctly handles both in-place and returned-object variants of the official `fuse_back_matter()`.
- Classifies Unicode normalization before whitespace differences.
- Preserves paragraph boundaries during whitespace classification.
- Keeps invalid-index exceptions identifiable by the dedicated handler.
- Counts a document as processed even when one or both S2ORC files are missing.
- Makes test mode opt-in through `ARIES_TEST_MODE=1`; full processing is the default.
- Separates whitespace mismatch side counts from record counts.
- Adds strict edit-category and parity reconciliation assertions.
- Records SHA-256 hashes of the actual imported `DocEdits` and `fuse_back_matter` source files; it does not claim an upstream Git commit when the local ARIES checkout has no Git metadata.

## Implementation provenance

The run manifest records `aries_implementation_source_hashes` for the Python files containing the imported `DocEdits` and `fuse_back_matter` implementations. These hashes identify the code actually loaded at runtime and are separate from the hashes of `paper_edits.jsonl` and S2ORC data files. No Git commit is asserted when the local ARIES directory is not a Git checkout.

## Important limitations
- This is a code correction, not a rerun of the 1,720-document corpus.
- The existing v5 metrics and audit outputs remain historical outputs and have not been recalculated.
- Do not interpret the old 86.41% result or the old mismatch classifications as validated by this branch.
- Verify the official ARIES checkout/API and run tests against a small known sample before a full run.


## Strict and normalized parity reporting

The v5.1 runner now reports two separate pair-level rates over successfully reconstructed revision pairs:

- `strict_parity_rate`: both source and target match character-for-character.
- `normalized_parity_rate`: both sides are either exact or differ only by Unicode NFC normalization, horizontal whitespace, or paragraph-boundary formatting.
- `normalized_only_matches`: normalized-equivalent pairs that are not strict exact matches.
- `records_with_formatting_only_mismatch`: pair count with formatting/normalization differences but no substantive side.
- Each parity audit record includes `normalized_parity_match`.

The validated revision-pair output remains strict-only. Normalized-only pairs remain in the audit and are not silently promoted into the strict validated-pairs file.

Pure classification helpers live in `src/og_awc/aries_audit.py`; regression tests are in `tests/test_aries_audit.py`. Tests cover exact text, horizontal whitespace, paragraph breaks, Unicode NFC, changed words, changed word order, changed paragraph content, and preservation of original strings.

A 50-document user-run diagnostic previously found 514 paragraph-boundary mismatch sides with identical flattened text. That is a test-sample observation, not a full-corpus result. The full 1,720-document run remains outstanding.


## Portability and failure accounting follow-up

- The runner resolves the ARIES checkout from `ARIES_SOURCE_ROOT`; when unset, it uses `~/Downloads/aries-master` as a backward-compatible default. The configured root is inserted at the front of `sys.path` before ARIES imports.
- The manifest records each imported implementation's Python module, path relative to the configured ARIES source root, and SHA-256. The runner refuses to record implementation provenance if either imported source file is outside that root.
- S2ORC loading/fusion failures and `DocEdits.from_list()` construction failures are caught at document scope. Every affected unique edit is written to the reconstruction error log and counted in a dedicated terminal category, so these failures do not silently abort or disappear from reconciliation.
- The terminal reconciliation includes missing papers, document-load errors, edit-construction errors, additions, deletions, empty/malformed edits, checked revision pairs, invalid indices, and per-edit reconstruction exceptions.
- The final console summary prints the terminal categories and the reconciled total. The unused `ParagraphEdit` import and unpopulated `invalid_reconstruction_mismatches` metric have been removed.

## Interpretation of the checked-in full audit log

`full_audit_log.txt` contains captured output reporting 1,720 processed documents and a 87.23% strict / 100.00% normalized parity result. It is retained as a historical run log, but the corresponding machine-readable metrics, complete output set, and run manifest are not checked in alongside it. Therefore the log is evidence of a user-reported run, not independently reproducible proof that the current v5.1 runner produced those results. A fresh full run must preserve its metrics, error files, output hashes, implementation hashes, and input hashes together before its results are treated as validated.
