# Og-AWC academic writing rules

These rules define the editorial and annotation policy for legitimate academic-writing support. They are guidance, not a universal style template. Discipline, venue, assignment brief, research design, and author intent take precedence.

## 1. Core objective

Help authors communicate their own research accurately, clearly, and naturally in an appropriate scholarly register. Preserve meaning, evidence, uncertainty, terminology, and authorial intent. Do not optimize text to evade AI detectors, conceal plagiarism, or misrepresent authorship.

## 2. Meaning and evidence must survive every edit

- Never add findings, data, methods, citations, causal claims, limitations, or implications that are not supported by the supplied source.
- Do not strengthen correlation into causation, preliminary evidence into proof, or a qualified result into a universal claim.
- Preserve numerical values, units, sample sizes, statistical notation, named entities, technical terms, and citation targets exactly unless the author explicitly corrects them.
- Keep uncertainty and hedging proportional to the evidence (for example, may, suggests, is consistent with); do not remove cautious language merely to sound confident.
- If a sentence is ambiguous or underspecified, flag the ambiguity or ask the author rather than guessing.

## 3. Clarity, precision, and concision

- Prefer precise, familiar wording over inflated vocabulary and ornamental synonyms.
- Give each sentence a clear job; avoid stacking several unrelated claims into one sentence.
- Remove repetition only when it does not remove emphasis, qualification, or necessary context.
- Replace vague references (this, it, they, these results) when the referent is unclear.
- Define abbreviations at first use where the target style requires it.
- Use technical terms consistently; do not vary terminology just to create lexical variety.
- Use transitions to express real logical relationships, not as decorative sentence starters.
- Vary sentence length naturally to support reasoning. Do not enforce a fixed sentence length or a mechanical rhythm.

## 4. Natural scholarly voice

- Retain the author's point of view, preferred terminology, level of formality, and discipline-specific conventions where they are appropriate.
- Avoid generic filler, stock openings, repetitive conclusion phrases, exaggerated claims, unnecessary signposting, and thesaurus-driven paraphrases.
- Do not force active voice everywhere. Choose active or passive voice according to whether the actor or the process/result deserves emphasis and according to disciplinary convention.
- Do not make prose artificially complex to make it appear academic. Clear and direct prose is scholarly prose.
- Do not deliberately introduce errors, awkwardness, random synonym swaps, or stylistic noise to simulate human writing.

## 5. Argument and paragraph structure

- A paragraph should have a discernible role: claim, context, evidence, method, interpretation, contrast, limitation, or transition.
- Keep claims connected to the evidence and explain why evidence supports the interpretation.
- Distinguish prior literature, the present study's procedure, observed results, and the authors' interpretation.
- Do not manufacture a rhetorical move, gap, novelty claim, or contribution statement unsupported by the paper.
- Preserve meaningful contrasts and counterarguments; do not flatten nuanced discussion into a single position.

## 6. Section-aware conventions

| Section | Editorial checks |
|---|---|
| Title | Accurate scope; no unsupported promise or exaggerated novelty |
| Abstract | Problem, approach, key results, and implication aligned with the full paper; no new evidence |
| Introduction | Context, focused problem/gap, rationale, objective/contribution; citations support claims |
| Related work | Fair synthesis and comparison; distinguish others' findings from the current study |
| Methods | Reproducible detail; past/present tense chosen consistently; no invented procedural detail |
| Results | Report observations faithfully; keep interpretation distinct where the field expects it |
| Discussion | Interpret within evidence; address alternatives, limits, and implications |
| Conclusion | Answer the stated objective; no new results or overgeneralization |
| Limitations | Specific and candid; do not hide or exaggerate constraints |

These are prompts for review, not rigid templates. Some disciplines and article types use different structures.

## 7. Citation and research integrity

- Cite ideas, findings, wording, data, figures, and methods that are not the author's own, following the target style.
- Never invent a reference, DOI, author, quotation, page number, or bibliographic detail.
- A retrieved example is evidence for analysis, not reusable prose. Do not reproduce source passages as the user's original writing.
- Mark quotations clearly and preserve attribution. Paraphrasing does not remove the need to cite.
- Respect self-plagiarism, permissions, participant confidentiality, and third-party material restrictions.
- Keep the source URL, DOI, publication metadata, license statement, retrieval date, and attribution with every real-paper example.

## 8. Dataset and annotation rules

- Distinguish `revision_pair`, `source_only`, `human_reviewed_edit`, `synthetic_fixture`, and `guideline` records. Never invent a revised text for source-only records.
- Record whether an edit is author-integrated, peer-review-driven, editor-provided, student work, benchmark correction, or unknown. Do not collapse these into one generic label.
- Preserve original/revised direction, version IDs, paragraph/sentence alignment, section, discipline, venue, year, and source identifiers where available.
- Keep article-level IDs as the split unit. All versions, paragraphs, and derived subsets from one article must remain in one split.
- Track source lineage and subset overlap. ParaRev is derived from CASIMIR; its 641 annotated rows are included in the full ParaRev corpus. Never count these as independent examples.
- Deduplicate conservatively. Keep a duplicate/lineage audit rather than silently deleting provenance.
- Store source text locally unless the exact license and underlying rights allow the intended processing and redistribution. Access is not a redistribution license.
- Keep benchmark/test records out of training and tuning. Report source, article, and split leakage checks.

## 9. Suggested edit labels

Use multi-label annotations where appropriate; allow `uncertain` and `not_applicable`.

- `clarity`
- `precision`
- `concision`
- `cohesion`
- `paragraph_structure`
- `argumentation`
- `evidence_alignment`
- `terminology_consistency`
- `grammar`
- `punctuation`
- `academic_register`
- `hedging_and_stance`
- `citation_integrity`
- `section_convention`
- `author_voice_preservation`

Annotators should record the reason for an edit and whether it changes meaning. A style edit that changes a scientific claim is not a style-only edit.

## 10. Review checklist

Before accepting an edit, ask:

1. Is the author's meaning and claim strength unchanged?
2. Are facts, numbers, citations, and technical terms intact?
3. Is the sentence clearer or more precise?
4. Does the paragraph's reasoning still flow?
5. Does the prose sound appropriate for this discipline and section?
6. Has unnecessary repetition been removed without losing nuance?
7. Is the author's voice retained rather than replaced by a generic template?
8. Are sources and permissions recorded?
9. Is the edit genuinely human-authored/reviewed if labeled as such?
10. Has the record been assigned to the correct article-level split?

## Reference guidance

- APA Style, Style and Grammar Guidelines: https://apastyle.apa.org/style-grammar-guidelines
- APA Style, Grammar: https://apastyle.apa.org/style-grammar-guidelines/grammar/
- KTH, Scientific style: https://www.kth.se/larande/sprak/utbildning/sprak/eng/writing-guide/scientific-style
- University of Leeds, Clear, concise and formal: https://library.leeds.ac.uk/info/14011/writing/221/language-and-style
- ACL Anthology copyright FAQ: https://aclanthology.org/faq/copyright/
- ACL publication ethics policy: https://www.aclweb.org/adminwiki/index.php/ACL_Policy_on_Publication_Ethics

Style guides may be copyrighted. This document summarizes operational principles in original wording and links to the authoritative guidance; it does not reproduce proprietary manuals.
