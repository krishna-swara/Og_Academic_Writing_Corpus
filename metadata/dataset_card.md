# Og-AWC Dataset Card

## Summary
Og-AWC is a provenance-aware academic writing revision corpus and deterministic processing toolkit. It focuses on real revision pairs, revision annotations, and reproducible paper-level evaluation splits.

## Sources and current acquisition status
- **ParaRev annotated subset:** 641 paragraph revision pairs according to its Hugging Face dataset card. The source card declares CC BY-NC-SA 4.0. An opt-in downloader is provided; raw and normalized data are written locally and are not committed to this repository by default.
- **CASIMIR:** its Hugging Face card declares MIT and describes revisions of 15,646 OpenReview scientific articles. Underlying article rights and included third-party content require separate review; it is not automatically ingested.
- **JFLEG:** its card declares CC BY-NC-SA 4.0 and describes 1,503 source sentences with four human corrections each. It is a general GEC benchmark, not academic-writing material, and should remain a separate auxiliary benchmark.
- **Individually licensed open-access papers:** per-item review required.

ParaRev is derived from CASIMIR. Track lineage and do not count overlapping records as independent examples.

## Acquisition
Run:
```bash
og-awc acquire-pararev --accept-license
```
This command explicitly acknowledges ParaRev's declared CC BY-NC-SA 4.0 terms, downloads a pinned source revision into ignored `raw_sources/`, and writes normalized revision pairs and an acquisition manifest under ignored `processed/`. It does not upload or publish the data.

Only use this path if the intended use is non-commercial and the applicable attribution/share-alike obligations can be met. The declared dataset license does not itself resolve every underlying article right. Review terms before redistribution or commercial use.

## Processing
The importer preserves source IDs, paper IDs, version IDs, source revision, annotation metadata, license, acquisition date, and SHA-256 of the downloaded source file. It excludes rows without both original and revised paragraphs. The deterministic pipeline deduplicates and splits by paper ID.

## Intended use
Research and development of transparent academic-writing analysis and legitimate revision-support workflows.

## Out-of-scope use
Detector evasion, plagiarism concealment, authorship verification, or claims that text will be classified as human-written.

## Limitations
The manually annotated ParaRev subset is a limited subset, not a representative sample of all academic disciplines. Annotation categories are preserved as upstream metadata and are not silently converted into Og-AWC labels. A source-only paper is not a revision pair. Corpus patterns do not establish an author's personal style or the human origin of a text.

## Release policy
Third-party text remains local by default. Any public release must include a source-specific rights review, required attribution, compatible share-alike terms, versioned manifests, and paper-level leakage checks.
