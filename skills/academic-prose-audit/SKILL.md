---
name: academic-prose-audit
description: Read-only contextual audit of academic phrasing and register in an authorized fixed manuscript revision; locatable, meaning-preserving suggestions, not an authorship or citation-support detector.
---

# Academic prose audit

## Goal

Audit English manuscript prose for natural, precise academic voice; report in the user's chosen language. Grammar and TeX hygiene are supporting checks. “Audit the prose,” “check AI-sounding phrasing,” “check register,” or “review generic wording” request contextual review; “polish,” “copyedit,” or “rewrite” alone do **not** authorize a full audit. “AI-sounding” is subjective style, not evidence of authorship or a detection score.

Fix the authorized revision and local files/sections before reading. Record path, SHA-256 of input bytes, mtime and HEAD if available (HEAD cannot replace the file hash). Identify exclusions, discipline, audience, technical terms and author preferences. Inputs are read-only: do not edit, push, upload, or run untrusted TeX; keep snippets and outputs private. Save only a fresh report in an authorized location. Source edits need separate approval and verification. See [safety and coverage](references/safety-and-coverage.md).

## Workflow

Read each sentence in paragraph and section context. Protect commands, citation keys, labels, math, comments and literal quotations; quote edits require explicit authorization. Headings, captions, footnotes, theorem/proof prose and emphasis can contain authored text. In floats, read caption prose while ignoring tabular cells, raw figure data and command keys; inspect visually whenever markup obscures the authored sentence. Record gaps (custom macros, generated inputs, inaccessible files, unsupported syntax); no tool output proves full coverage. Use [contextual phrasing](references/contextual-phrasing.md), not a banned-word list.

Optionally run the stdlib locator on explicitly authorized `.tex`, `.md` or `.txt` files: `python3 <skill-dir>/scripts/prose_candidates.py path/to/section.tex`. Its private `file:line` questions are not judgments, coverage percentages or a full audit. Review candidates and gaps manually; counts are not thresholds. It reads only explicit inputs, does not expand `\input` or handle `.docx`. A malformed protected span aborts the whole file before any snippet is printed; repair the input or inspect that file manually, never interpret silence as clearance. See [safety and coverage](references/safety-and-coverage.md) for limits.

Delegate nonoverlapping sections only if host policy permits; keep one revision/glossary and read-only boundary. Otherwise work sequentially. Reconcile duplicates, disagreements and missing coverage; never claim parallel review without receipts. See [parallel review](references/parallel-review.md) when delegating.

## Judgment

Ask what a phrase does **here**: does framing obscure a comparison, promotional language overstate evidence, or repetition crowd out argument? Examine sentence starts, transitions, templates and em dashes with actual nearby instances and a stated span. Neither a word nor a count establishes a defect; disciplinary language and deliberate repetition may be useful. Name missing specificity without inventing numbers or mechanisms.

Preserve quantities, units, comparator, scope, negation, conditions, qualifiers, modality, causal strength, terminology and citation attachment. Suggest the **smallest** natural change or ask when uncertain. Never invent sources, claim citation support, or change claim strength for polish. See [contextual phrasing](references/contextual-phrasing.md) for examples. Label scientific support `support unreviewed`; only separately opted-in `latex-bib-audit` Layer 3 checks original-paper support.

## Output

Default to a fresh offline HTML report outside source files, with inline CSS and no external assets/requests or required JavaScript; use `.md` or `.txt` if requested. In the chosen language state scope, path/hash/mtime/HEAD, coverage and gaps, actual review mode and worker failures, and severity counts. For each finding give `file:line`, short context, exact original, minimal suggestion **or** question, contextual reason, evidence, severity (`substantive`/`editorial`) and confidence. Map to a [contextual phrasing](references/contextual-phrasing.md) category or explain the exception. Separate taste and nonissues; omit weak findings. Patterns need examples and count/scope. No findings means none high-confidence within reviewed coverage.

HTML-escape source text and attributes; never execute embedded HTML or link source URLs without HTTP(S) scheme validation. Label support questions as unverified. See [report output](references/report-output.md) for layout and [provenance](references/provenance.md) only when tracing adapted ideas.
