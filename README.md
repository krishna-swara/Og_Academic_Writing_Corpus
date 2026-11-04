# Og Academic Writing Corpus (Og-AWC)

A carefully documented corpus and deterministic data pipeline for academic writing analysis and revision research.

## Project goals

Og-AWC is designed to support transparent, reproducible academic-writing improvement workflows using structured examples, explicit provenance, and human-reviewed revision pairs.

The project focuses on:
- sentence- and paragraph-level revision records with traceable provenance;
- grammar, clarity, cohesion, terminology, and academic-register annotations;
- deterministic normalization, deduplication, validation, and leakage-resistant splitting;
- clear separation between source text, genuine revision pairs, synthetic fixtures, and human-approved edits.

## Non-goals and safeguards

- No generative AI, hosted AI API, or Ollama dependency is part of the core pipeline.
- The project does not promise to evade AI detectors, plagiarism checks, or similarity systems.
- A published-paper corpus is not, by itself, evidence of an author's personal style or human authorship.
- Never fabricate a revised version for a source-only paper.
- Never redistribute third-party text unless the applicable license and terms permit it.
- Public accessibility does not imply permission to download, transform, or redistribute content.

## Repository layout

```text
raw_sources/       Optional locally acquired source material (not committed by default)
processed/         Normalized corpus outputs (generated; review before publishing)
annotations/       Human-reviewed edit annotations
evaluation/        Paper-level validation and test splits
metadata/          Source and license registries, dataset card
schemas/           JSON Schemas for records and registries
src/og_awc/        Deterministic processing and validation package
scripts/           Command-line pipeline entry points
tests/             Automated tests and synthetic fixtures
```

## Data policy

Every imported source must have a registry entry containing its canonical name, source URL, version or release, acquisition date, license identifier and URL, attribution requirements, redistribution status, and notes on restrictions. If terms are unclear, mark the source as `review_required` and do not redistribute its contents.

CASIMIR, ParaRev, and JFLEG are candidate sources, not blanket permission to redistribute. Verify the current dataset card, upstream terms, underlying paper rights, and any non-commercial/share-alike or attribution conditions before acquisition or publication. ParaRev's relationship to CASIMIR must be considered during deduplication; overlapping records must not be counted as independent examples.

Published papers may be used only in ways permitted by their specific licenses and terms. Prefer storing metadata and permitted identifiers rather than full text when redistribution rights are absent.

## Record principles

- Preserve source IDs and paper/article IDs.
- Keep original and revised text distinct.
- Populate `revised_text` only when an actual revision is supplied or a human reviewer has approved the edit.
- Label synthetic examples explicitly as test fixtures; never present them as collected research data.
- Split by paper/article ID, not random sentence, to prevent train/validation/test leakage.
- Keep transformations deterministic and record pipeline versions.

## Quick start

Requires Python 3.10 or newer.

```bash
python -m pip install -e ".[dev]"
pytest
og-awc validate --input tests/fixtures/sample_records.jsonl
```

The first implementation milestone provides schemas, registries, validation, deduplication, group-aware splitting, and synthetic test fixtures. It does not bundle third-party corpora.

## Project status

Early development. No third-party corpus text is included in this repository at bootstrap. Source acquisition is intentionally gated on license review.

## License

The repository's own code and documentation license will be declared separately. That license does not grant rights to third-party datasets or paper content referenced by this project.
