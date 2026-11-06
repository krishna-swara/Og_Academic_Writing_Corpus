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
- Removes the hard-coded ARIES version claim; set `ARIES_GIT_COMMIT` to the exact upstream commit before running.

## Important limitations
- This is a code correction, not a rerun of the 1,720-document corpus.
- The existing v5 metrics and audit outputs remain historical outputs and have not been recalculated.
- Do not interpret the old 86.41% result or the old mismatch classifications as validated by this branch.
- Verify the official ARIES checkout/API and run tests against a small known sample before a full run.
