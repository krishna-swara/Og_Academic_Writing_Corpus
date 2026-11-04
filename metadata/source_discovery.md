# Source discovery and triage

This file separates **dataset candidates** from **software/tool references**. A GitHub repository mentioning academic writing is not automatically a corpus, and a public download is not automatically licensed for redistribution.

## Dataset and corpus candidates

| Candidate | What it may contribute | Current decision | Next verification |
|---|---|---|---|
| [ParaRev](https://huggingface.co/datasets/taln-ls2n/pararev) | Real scientific-paragraph revision pairs; manually annotated subset and full configuration | Existing importer targets the 641-row manually annotated subset. Full configuration is a separate, larger acquisition target. | Inspect full-config schema/counts, pin revision, test importer, retain CASIMIR lineage, and review underlying article rights before public release. |
| [CASIMIR](https://huggingface.co/datasets/taln-ls2n/CASIMIR) | Scientific article revision history and associated review material | High-value research candidate; not automatically ingestible. | Inspect split/schema and article-level provenance; verify the dataset card's declared license against underlying OpenReview and third-party rights. |
| [BAWE](https://www.coventry.ac.uk/research/research-directories/current-projects/bawe/) | British Academic Written English student assignments; useful for genre/register and academic-language analysis | Candidate source-only corpus, not a revision-pair dataset. | Confirm current access route, permitted research use, redistribution restrictions, metadata, and whether texts can be downloaded programmatically. |
| [MICUSP](https://micusp.elicorpora.info/) | Michigan Corpus of Upper-level Student Papers; useful for student academic writing and genre analysis | Candidate source-only corpus, not a revision-pair dataset. | Confirm access conditions, license/terms, download availability, and metadata before ingestion. |
| [ACL Anthology](https://aclanthology.org/) | Research papers in computational linguistics; useful for domain-specific academic prose and citation/section structure | Candidate source-only paper collection; each paper's license must be checked. | Use paper-level license/provenance metadata; do not assume every hosted paper has identical reuse rights. |
| [Academic Phrasebank](https://www.phrasebank.manchester.ac.uk/) | Rhetorical move and phrase-function reference for academic writing support | Reference resource, not a general-purpose raw-text corpus. | Review its terms before copying phrase examples; prefer linking and manually encoding permitted category metadata. |

## GitHub repository leads from an initial search

These are **leads to inspect**, not approved data sources. Their descriptions alone do not establish that they contain downloadable corpora or grant reuse rights.

| Repository | Initial relevance | Triage |
|---|---|---|
| [Maryam-Nasseri/LCA-AW-Lexical-Complexity-Analyzer-for-Academic-Writing](https://github.com/Maryam-Nasseri/LCA-AW-Lexical-Complexity-Analyzer-for-Academic-Writing) | BAWE-derived academic vocabulary / lexical complexity tooling | Potentially useful analysis code and vocabulary resource. Inspect source files and the BAWE-derived list's terms; do not assume the corpus itself is included or redistributable. |
| [Pegi1727/Lexical-Architecture-in-Native-and-Multilingual-Academic-Writing-A-Pre-AI-Corpus-Study](https://github.com/Pegi1727/Lexical-Architecture-in-Native-and-Multilingual-Academic-Writing-A-Pre-AI-Corpus-Study) | Corpus study comparing lexical patterns | Research/methodology lead. Verify whether data and scripts are actually present and what their licenses permit. |
| [microshuhao/journal-adapt-writing-skill](https://github.com/microshuhao/journal-adapt-writing-skill) | Journal-adaptation workflow | Possible workflow inspiration, not yet a verified corpus. |
| [caiyanx911-sketch/scholar-style-workbench](https://github.com/caiyanx911-sketch/scholar-style-workbench) | Corpus-based Chinese academic writing profiles | Possible analysis/tooling reference; inspect language scope and data provenance. |
| [flyyyyypig/xw-academic-writing-polish](https://github.com/flyyyyypig/xw-academic-writing-polish) | Corpus-driven polishing workflow | Possible workflow reference; verify corpus provenance and implementation. |
| [ZihanZheng2000/water-domain-ai-writing-revision](https://github.com/ZihanZheng2000/water-domain-ai-writing-revision) | Domain-specific revision workflow for water research | Narrow-domain tool/research lead, not a general academic corpus. |
| [NahidShahmoradi/significant-corpus-analysis](https://github.com/NahidShahmoradi/significant-corpus-analysis) | Corpus analysis of one lexical item | Narrow linguistic analysis; low priority for core ingestion. |
| [Tim-Hampson/Abstracted_Identity](https://github.com/Tim-Hampson/Abstracted_Identity) | Analysis of academic abstracts across the GenAI period | Potentially useful research question/method, not yet a verified reusable corpus. |

## Admission checklist

A candidate should not enter the core corpus until the following are recorded:

1. Actual downloadable text/data exists and the schema has been inspected.
2. License and terms are verified at the dataset and underlying-document levels.
3. Source URL, version/revision, acquisition date, checksums, and original IDs can be retained.
4. The record type is honest: source-only paper, genuine revision pair, or human annotation.
5. Overlap and derivation relationships are documented; CASIMIR and ParaRev are not independent examples.
6. Train/validation/test assignment is grouped by paper/article ID to prevent leakage.

## Prioritization

1. Finish and test the ParaRev full-configuration importer locally; keep its raw text out of public GitHub until rights are reviewed.
2. Evaluate BAWE and MICUSP as source-only academic writing corpora for genre/register analysis.
3. Evaluate ACL Anthology only with paper-level license filtering.
4. Reuse useful lexical-analysis code only after inspecting its license and dependencies.
5. Keep general grammar-correction benchmarks separate from academic-writing revision data.

**Status meaning:** “candidate” means worth investigating, not approved for ingestion or redistribution.


## Additional source candidates and real-paper seed list

| Source | What to collect | Admission rule |
|---|---|---|
| [ParaRev full](https://huggingface.co/datasets/taln-ls2n/pararev) | Full scientific paragraph revision pairs | Use the pinned importer; annotated 641 subset overlaps with full data; retain CASIMIR lineage. |
| [PMC Open Access Subset](https://pmc.ncbi.nlm.nih.gov/tools/openftlist/) | Biomedical full-text papers | Select only articles with explicit reusable licenses. License is article-specific. Use only NCBI-authorized bulk retrieval services. |
| [ACL Anthology](https://aclanthology.org/) | NLP/computational-linguistics papers and metadata | Start with metadata and paper-level license filtering. ACL's policy differs before/after 2016 and excludes third-party materials. |
| [BAWE via Oxford Text Archive](https://ota.bodleian.ox.ac.uk/repository/xmlui/handle/20.500.12024/2539) | Student academic texts and genre metadata | Register and comply with non-commercial access conditions; do not assume redistribution permission. |
| [MICUSP](https://elicorpora.info/main) | Upper-level student papers and metadata | Research/teaching access; commercial use needs prior permission. Confirm terms before bulk processing. |

### Real research papers to index first

The metadata-only starter bibliography is in [seed_papers.json](seed_papers.json). It starts with the CASIMIR and ParaRev dataset papers plus the ACL Anthology Reference Corpus paper. These are real scholarly publications and useful methodology references; they are not a license to copy their full text. Expand the bibliography by discipline and section after paper-level rights review.

### Acquisition order

1. Finish the ParaRev full importer and test the full-file schema, output count, and stable overlap with the 641 annotated records.
2. Add a CASIMIR lineage manifest and overlap audit before any CASIMIR ingestion.
3. Build a metadata-first ACL Anthology paper catalog; ingest full text only where per-paper and third-party rights permit.
4. Add PMC Open Access as a biomedical source with article-level license filters and compliant NCBI retrieval.
5. Obtain BAWE and MICUSP through their official access routes and honor research-only/non-commercial conditions.
6. Keep source-only paper examples separate from genuine author revision pairs and human-reviewed edits.
