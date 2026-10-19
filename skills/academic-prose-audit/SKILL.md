---
name: academic-prose-audit
description: Read-only contextual audit of academic phrasing and register in an authorized fixed manuscript revision; locatable, meaning-preserving suggestions, not an authorship or citation-support detector.
---

# Academic prose audit

## Goal

Audit English manuscript prose for natural, precise academic voice; report in the language the user chooses (ask or follow their stated preference). Grammar and TeX hygiene are supporting checks, not the goal. Requests such as “audit the prose,” “check AI-sounding phrasing,” “check register,” or “review generic wording” trigger a contextual audit; “polish,” “copyedit,” or “rewrite” alone do **not** silently authorize a full audit. For those, honor the narrower request and ask before expanding. “AI-sounding” is a subjective style description, never evidence of AI authorship or a detection score.

Fix the authorized revision and exact local file/section list before reading. For local files record path, SHA-256 of input bytes, and modification time; also record repository HEAD when available, but a Git HEAD is **not** a substitute for the file hash and a missing Git repo is not a blocker. Identify exclusions, discipline, audience, established technical terms, and author preferences. Manuscript inputs are read-only: do not edit, push, upload, or run untrusted TeX; keep snippets, terminal output, and reports private. Only save a new report in a user-authorized location; do not overwrite one. Changes to manuscript source require separate, specific approval and a separate verification pass. See [safety and coverage](references/safety-and-coverage.md) when dealing with markup, privacy, or authorization.

## Workflow

Read each sentence in paragraph and section context. Distinguish authored prose from commands, citation keys, labels, math, comments, literal quotations, and quoted source material. Protect those spans; quote edits need explicit authorization. Headings, captions, footnotes and emphasis can contain authored prose and should not disappear behind TeX syntax. Record gaps (custom macros, generated inputs, inaccessible files, unsupported syntax); no output from a tool does not prove full coverage. For targeted questions and counterexamples, consult [contextual phrasing](references/contextual-phrasing.md), not a banned-word list.

Optionally run the stdlib locator on explicitly authorized files: `python3 <skill-dir>/scripts/prose_candidates.py path/to/section.tex` (also accepts `.md` and `.txt`). It prints private `file:line` questions about potential patterns, not judgments, percentages, rewrites, or a complete audit. Review its candidates and gaps manually against original context; never treat counts as thresholds. It reads inputs only, does not discover files or expand `\input`, and does not support `.docx`. See [safety and coverage](references/safety-and-coverage.md) for supported syntax and blind spots.

If host policy explicitly permits subagents and scope warrants it, partition nonoverlapping sections under one fixed revision/glossary and read-only boundary. Otherwise review sequentially. Reconcile cross-section patterns, duplicates, disagreements and incomplete worker coverage yourself. Do not imply parallel work occurred without receipts. See [parallel review](references/parallel-review.md) only when delegating.

## Judgment

Ask what a phrase does **here**: does generic framing obscure a real comparison, promotional language overstate a result, or a repeated transition/ending crowd out the argument? Inspect repeated sentence starts, paragraph transitions, symmetrical templates, and em-dash function with actual nearby instances and a stated span; neither a word nor a count establishes a defect. Legitimate disciplinary language, deliberate repetition and useful general introductions are nonissues. A question about missing specificity must identify what is missing, never supply a fabricated number or mechanism.

Preserve the author's meaning: quantities, units, comparator, scope, negation, conditions, qualifiers, modality, causal strength, technical terminology and citation attachment. Suggest the **smallest** natural change, or ask when intent/evidence is unclear. Do not invent sources, claim a citation supports a proposition, reflexively weaken warranted claims, or strengthen them for polish. See [contextual phrasing](references/contextual-phrasing.md) for complete synthetic original/overwritten/minimal examples. Scientific support is `support unreviewed`; only a separately opted-in `latex-bib-audit` Layer 3 can check original-paper support (Layers 1/2 cannot).

## Output

Default to a fresh standalone offline HTML report outside manuscript sources, with inline CSS, no external assets/requests or required JavaScript. If requested, use `.md` or `.txt` instead; source files remain untouched. In the user-chosen report language, state scope, hash/path/mtime (and HEAD if available), reviewed coverage and gaps, actual sequential/parallel mode and worker failures, and counts by severity. For each genuine finding give `file:line`, short paragraph context, exact original, minimal suggestion **or** author question, why it matters here, evidence, severity (`substantive` or `editorial`) and confidence. Map it to a [contextual phrasing](references/contextual-phrasing.md) question category or explain a grounded exception. Keep taste preferences and useful nonissues separate; omit weak findings rather than converting candidates into verdicts. Pattern findings need actual examples and count/scope. No findings means only no high-confidence problems within reviewed coverage.

HTML-escape source text and attributes; never execute embedded manuscript HTML or turn source-derived URLs into clickable links unless their scheme is explicitly validated as HTTP(S). Keep unverified support questions labeled, not asserted. Use [report output](references/report-output.md) for layout, accessible presentation, and a complete synthetic finding. See [provenance](references/provenance.md) only when tracing adapted diagnostic ideas; this skill does not import upstream packages or imply permission to reproduce their content.
