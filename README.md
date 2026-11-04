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
