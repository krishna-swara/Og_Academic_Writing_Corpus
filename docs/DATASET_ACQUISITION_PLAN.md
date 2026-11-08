# Dataset Acquisition and Preparation Plan

## Objective
Build a broad but auditable writing-improvement dataset. Do not treat every available text collection as interchangeable. Maintain separate tracks:

1. **Unpaired style corpus:** rights-cleared human-authored documents used for descriptive style analysis and retrieval context. These are not input/output supervision pairs.
2. **Revision pairs:** genuine source-to-revised examples with task, provenance, annotator/source information, and rights review.
3. **Grammar and fluency benchmarks:** sentence-level corrections kept in their original benchmark splits.
4. **Preference data:** explicit human choices between candidate edits, with consent and annotation guidelines.
5. **Synthetic data:** model-generated examples, separately labelled and never described as human-authored.

## Starter source candidates

| Source | Potential role | Hub-declared terms / rights status | Action |
|---|---|---|---|
| `grammarly/coedit` | Multi-task text editing pairs (grammar, paraphrase, simplification, etc.) | Hugging Face card declares Apache-2.0; the card says the public 69k subset excludes data withheld for licensing restrictions. Audit source lineage and card before training or redistribution. | First starter candidate; acquire locally to a quarantine/pending-review area, then validate. |
| `PleIAs/common_corpus` | Large unpaired, multilingual, multi-domain text; includes OpenScience | Dataset card describes document-level licence/provenance metadata and commercial/non-commercial use. Full snapshot is enormous (about 4.49 TB in the current Hub viewer); never download wholesale. | Later, stream/sample only records with individually verified PD, CC0, CC-BY or other approved terms; retain per-document licence and source metadata. |
| `jhu-clsp/jfleg` | Grammar/fluency benchmark with four human references per source sentence | CC BY-NC-SA 4.0 declared. Not suitable for an unknown commercial destination without a separate compatible permission. | Do not acquire into the commercial-eligible track; keep as a separately gated research-only candidate. |
| ParaRev | Academic paragraph revision pairs | CC BY-NC-SA 4.0 declared; source-paper rights also need review. | Do not acquire for the default product corpus. |
| ACL Anthology metadata | Bibliographic discovery and paper metadata | Metadata access is not a licence to redistribute article full text. | Metadata-only until per-paper terms are checked. |
| OpenAlex / PMC Open Access / arXiv | Academic style reference corpus | Rights vary by work and version; repository access is not blanket reuse permission. | Select individual works by explicit licence and text-mining permissions; store provenance. |

## Acquisition policy
- A Hugging Face licence tag is a discovery signal, not independent legal verification. Check the dataset card, repository licence files, upstream source licences, attribution, share-alike, non-commercial, privacy, and redistribution terms.
- Store a source-level and, where possible, record-level rights decision. Unknown or conflicting rights mean quarantine/no training.
- Keep raw downloads out of Git. Record exact dataset revision/commit, file hashes, acquisition timestamp, source URL, card snapshot, licence evidence, and filtering parameters.
- Do not combine source datasets as independent examples when one derives from another. Track lineage and deduplicate.
- Preserve upstream train/validation/test splits for benchmarks. For newly split corpora, split by paper/document/source group, not by paragraph, to prevent leakage.
- Keep benchmark/evaluation examples out of training.
- Do not invent human labels, edit rationales, or meaning-preservation judgments. Mark them pending until reviewed.
- Apply PII and sensitive-content screening, language detection, length bounds, malformed-record checks, duplicate detection, and contamination checks.
- No raw source text or user-uploaded document text is committed to Git.

## First acquisition sequence
1. Review and pin the current `grammarly/coedit` dataset card and revision.
2. Download its public 69k release to a local quarantine directory using the official Hugging Face `datasets` client.
3. Preserve task labels and original IDs; normalize to the Og-AWC schema without fabricating paper IDs or annotator identity.
4. Mark all records `pending_rights_and_quality_review`; do not expose them as approved retrieval examples.
5. Run schema validation, exact/near duplicate checks, source lineage review, and a stratified human sample review.
6. Only after approval, prepare document/source-group splits and a benchmark report.
7. Later, sample Common Corpus OpenScience records by individually approved licence and stream in bounded batches.

## Integration contract
Og-AWC publishes versioned, validated manifests and approved JSONL exports. Og_Dataset consumes only records whose rights, provenance, review status, and quality status meet its runtime policy. Keep unpaired style references separate from revision pairs. Keep pending records unavailable to user-facing retrieval.
