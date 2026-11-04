# Og Academic Writing Corpus (Og-AWC)

A provenance-aware corpus toolkit and deterministic pipeline for academic writing analysis and legitimate revision research.

## What it does

- Validates structured sentence/paragraph records and provenance.
- Deduplicates normalized original/revision pairs.
- Assigns train/validation/test splits by **paper ID** to prevent same-paper leakage.
- Writes reproducible local split files and a preparation report.
- Keeps synthetic fixtures separate from research data and requires real revision text for revision-pair records.

The core pipeline uses Python and deterministic processing. It has no generative AI, hosted AI API, or Ollama dependency.

## Quick start

Requires Python 3.10+.

```bash
python -m pip install -e ".[dev]"
pytest
og-awc validate --input tests/fixtures/sample_records.jsonl
og-awc prepare --input tests/fixtures/sample_records.jsonl --output-dir processed/demo
```

The `prepare` command writes `all.jsonl`, `train.jsonl`, `validation.jsonl`, `test.jsonl`, `duplicates.jsonl`, and `report.json`. Default ratios are 80/10/10, assigned deterministically using paper IDs and a seed. Small datasets may not populate every split. These are local working outputs; generating a file does not grant permission to publish or redistribute its source text.

## Data and licensing safeguards

Candidate sources include CASIMIR, ParaRev, JFLEG, and individually licensed open-access papers. See `metadata/source_registry.json` and `metadata/license_registry.json`. Their declared terms are a starting point only; source-text redistribution remains disabled pending review of authoritative dataset versions, underlying paper rights, attribution, non-commercial/share-alike conditions, and included third-party content.

ParaRev is related to CASIMIR; track source lineage and remove overlap rather than treating related records as independent examples. Open access is not blanket permission to redistribute. Do not commit source data until its exact terms allow it.

## Record principles

- Preserve source IDs, paper IDs, source versions, acquisition dates, and license provenance.
- Never invent a revised version for a source-only paper.
- Label synthetic fixtures explicitly; they are not empirical research data.
- Split by paper/article ID, never by random sentence.
- Review generated artifacts and source permissions before publication.

## Scope and limitations

This project supports transparent writing improvement. It does not promise AI-detector evasion, plagiarism concealment, authorship verification, or a particular detector outcome. A paper corpus alone does not establish personal writing style or human authorship.

## Development

Run `pytest -q`. GitHub Actions runs tests and validates the synthetic fixture on pushes and pull requests.

## License

The project code and documentation license is described in the repository license file. It does not grant rights to third-party datasets or paper content referenced by this project.
