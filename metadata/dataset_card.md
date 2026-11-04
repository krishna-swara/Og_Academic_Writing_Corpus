# Og-AWC Dataset Card

## Summary
Og-AWC is a developing, provenance-aware academic writing corpus and deterministic processing pipeline. Its intended tasks include analysis of revision differences and annotation of grammar, clarity, cohesion, terminology, and academic register.

## Current release contents
The bootstrap release contains schemas, source/license registries, deterministic utilities, and explicitly synthetic test fixtures. It does not contain third-party corpus text.

## Intended use
Research and development of transparent academic-writing analysis and legitimate revision-support workflows.

## Out-of-scope use
Detector evasion, plagiarism concealment, authorship verification, and claims that text will be classified as human-written.

## Data collection and licensing
Candidate sources include CASIMIR, ParaRev, JFLEG, and individually licensed open-access papers. Each source remains blocked pending verification of authoritative license terms, attribution, non-commercial/share-alike restrictions, and redistribution permissions. Metadata and permitted identifiers should be preferred when full-text redistribution is not allowed.

## Processing
Normalization, exact deduplication, and paper-group splitting are deterministic. Pipeline version and source provenance should be retained in future releases.

## Known limitations
The bootstrap fixtures are synthetic and are not empirical evidence. A source-only paper is not a revision pair. A corpus of papers does not establish an author's personal style or the human origin of a text.

## Maintenance
Update this card for every release with source versions, license review decisions, record counts, exclusions, deduplication statistics, and split methodology.
