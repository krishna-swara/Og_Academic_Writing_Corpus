# Og Academic Writing Corpus (Og-AWC)

A provenance-aware corpus toolkit and deterministic pipeline for academic writing analysis and legitimate revision research.

## Quick start

Requires Python 3.10+.

```bash
python -m pip install -e ".[dev]"
pytest
```

### Acquire the first academic revision subset

ParaRev's manually annotated subset contains 641 paragraph pairs and declares CC BY-NC-SA 4.0. It is derived from CASIMIR. The importer is opt-in, pins an upstream revision, records attribution/provenance and a source-file SHA-256, and writes data locally only.

```bash
og-awc acquire-pararev --accept-license
og-awc validate --input processed/pararev_pairs.jsonl
og-awc prepare --input processed/pararev_pairs.jsonl --output-dir processed/pararev_splits
```

The full unannotated ParaRev file is available as a separate local acquisition. Its upstream JSONL uses hyphenated field names and contains the 641 annotated evaluation pairs as a subset; stable record IDs are shared so overlapping rows can be identified.

```bash
og-awc acquire-pararev-full --accept-license
og-awc validate --input processed/pararev_full_pairs.jsonl
og-awc prepare --input processed/pararev_full_pairs.jsonl --output-dir processed/pararev_full_splits
```

Do not count the 641 annotated subset and full corpus as independent examples. If combining them, deduplicate by record identity/text and retain the annotations as metadata rather than extra independent samples.

Use `--accept-license` only if the use is non-commercial and you can comply with attribution and share-alike requirements. Underlying paper rights may impose additional restrictions. Do not commit the downloaded data or publish processed text until the rights review is complete.

### Other sources

- CASIMIR's card declares MIT, but the dataset includes OpenReview articles; underlying paper and third-party rights still need review.
- JFLEG declares CC BY-NC-SA 4.0 but is a general grammatical-error-correction benchmark, not academic writing. Keep it separate as an auxiliary benchmark.
- ParaRev is extracted from CASIMIR. Do not combine both sources as independent examples; track lineage and deduplicate.

## Core features

- Structured JSONL validation and provenance.
- Exact normalized-text deduplication.
- Deterministic train/validation/test assignment by paper ID.
- Local split files and preparation reports.
- No generative AI, hosted AI API, or Ollama dependency.

## Data safeguards

- Never fabricate a revised text for source-only material.
- Preserve source versions, IDs, licenses, attribution, and acquisition dates.
- Keep raw/processed third-party text local by default.
- Open access is not blanket permission to redistribute.
- No detector-evasion, plagiarism-concealment, or authorship-verification claims.

See `metadata/source_registry.json`, `metadata/license_registry.json`, `metadata/dataset_card.md`, and [`metadata/source_discovery.md`](metadata/source_discovery.md) for source triage and next acquisition priorities. The BAWE, MICUSP, and ACL Anthology entries are candidates with access/license checks pending; they are not yet ingested.

## Corpus expansion and writing policy

- Source candidates, access restrictions, and acquisition priorities: [metadata/source_discovery.md](metadata/source_discovery.md).
- Editorial and annotation rules for clarity, natural scholarly voice, section-aware revision, evidence preservation, and research integrity: [metadata/academic_writing_rules.md](metadata/academic_writing_rules.md).
- Curated metadata-only bibliography of real research papers: [metadata/seed_papers.json](metadata/seed_papers.json).

The corpus is designed to support authentic, clear academic communication while preserving author meaning and voice. It is not designed for detector evasion or plagiarism concealment. Real paper text remains subject to source-specific license and third-party rights checks.
