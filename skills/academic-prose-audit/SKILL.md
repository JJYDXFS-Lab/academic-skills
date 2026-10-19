---
name: academic-prose-audit
description: Read-only academic prose/register audit of an authorized fixed manuscript revision, with file:line contextual findings and minimal meaning-preserving suggestions. Parallel section review; edits require separate approval.
---

# Academic prose audit

## 1. Fix scope and boundaries

Identify authoritative revision/hash, reachable prose files/sections, exclusions, discipline, audience, terminology and author preferences. Record a read-only boundary and obey the local project's locality and source-of-truth rules: a local clone may be stale. Keep unpublished prose local; do not upload, edit or push manuscript sources without exact approval or run untrusted TeX with shell escape. This is not an AI-authorship detector or a claim-support verdict.

**Done:** revision, sections, exclusions, terminology, locality and write boundary are explicit.

## 2. Read prose in context

Inspect sentences with paragraph and section purpose. Distinguish prose from TeX commands, equations, citation keys, labels, comments, Bib entries, protected names and literal quotations. Do not change protected spans by default; editing quotations requires explicit request. Track locations and coverage gaps for macros, generated inputs, unsupported syntax and missing files. Text search finds candidates but is not complete parsing.

Optional local triage, only after fixing an authorized file list: `python3 <skill-dir>/scripts/prose_candidates.py path/to/section.tex` (replace `<skill-dir>` with the directory containing this `SKILL.md`). This stdlib-only helper reads explicitly named `.tex` files and prints `file:line` context and review questions; it never edits its inputs. It masks detectable comments, math, commands and arguments (including citations and labels), verbatim and quotation spans and skips unsupported environments. TeX coverage is deliberately non-exhaustive: common unsupported environments and straight-quote ambiguity can hide prose without a precise coverage count, while custom macros, generated inputs, complex catcodes and unmatched constructs can hide prose or yield false positives. It does not expand `\input`, discover files, prove an absence of issues or produce audit findings by itself. Treat its small set of phrase cues as optional questions, not banned words, style rules, scientific conclusions or replacement instructions. Verify every candidate against the actual surrounding paragraph and section; do not infer clean coverage from zero output.

The CLI's stdout includes manuscript snippets: keep console output, redirects and logs private. It validates every named file before printing any findings and fails with a coverage error on detected unclosed regions; a failed scan does not certify any portion of that file. Stderr reports skipped command-argument counts, including a rough count containing letters; these include citation keys and labels, so neither count measures reviewed prose or proves completeness. Prose inside command arguments (for example section headings or custom macros) is intentionally masked and must be reviewed separately in context.

Assess colloquial, promotional, vague, metaphorical, redundant, unclear or overconfident language in context, not using banned-word lists. `story` may name a study or story-generation task; `buy` may denote a purchase or buy order. Titles, quotations and technical terms may legitimately use either. Repetition and ordinary wording are not evidence of AI generation.

Before suggesting a replacement, preserve quantities and units, comparison baselines, scope and negation, conditions and quantifiers, modality, causal direction, technical terms and citation attachment. Do not strengthen claims for polish, reflexively weaken supported claims, or replace domain terms with ornate synonyms. Ask the author when intent is unclear. Passive voice, `only` and hedges are context cues, not defects by themselves.

**Done:** findings were checked against context and protected spans; legitimate uses and coverage limits are separated.

## 3. Return traceable, conservative findings

Default deliverable: the agent authors a new, standalone `prose-audit.html` (name adaptable) in an authorized report location outside the source tree. Never overwrite an existing report. It must open offline with inline CSS, no CDN/network requests/external assets and no framework or JavaScript requirement. Include a readable summary of revision, scope, exclusions, reviewed coverage, finding and severity totals, unverified/undecided counts and coverage gaps. Per finding show `file:line`, exact original phrase and context, issue, evidence/why, minimal suggested replacement or author question, severity and confidence. Native `<details>` may hold long context. HTML-escape all source and evidence text; never execute manuscript HTML. Include a visible footer: `© <report year> JJYDXFS & Atom (原子). All rights reserved.` with `JJYDXFS` linked to `https://jjydxfs.github.io/` and `Atom (原子)` linked to `https://atom-of-jjydxfs.github.io/`. The offline report need not fetch these links. Markdown is optional on user request; the triage helper does not generate the full audit report.
Escape HTML attribute values as well as text; render source-derived links only after validating an `https:` or `http:` scheme. Keep local/file and script schemes as escaped plain text.

Use `substantive` when wording distorts meaning/calibration, `editorial` for clear register/clarity problems, and keep optional preferences separate. Do not rewrite a paragraph to fix one phrase. Omit weak findings or mark them as questions. Include useful deliberate nonissues. No findings means no high-confidence issues in reviewed scope, not perfect prose.

Label source-support questions `support unreviewed`; refer them to `latex-bib-audit` Layer 3 only if explicitly enabled. Its default Layers 1/2 do not validate scientific claims. Tone alone cannot show a claim is false.

**Done:** the fresh HTML report makes each issue contextualized, locatable and actionable without unsupported authorship or scientific conclusions.

## 4. Parallel review and reconciliation

Give workers one fixed revision, scope, glossary and read-only boundary. Partition nonoverlapping sections/paragraphs; adjacent paragraphs can provide context without duplicate finding ownership. Workers return findings, nonissues and gaps, not concurrent edits. One coordinator deduplicates boundary issues, checks terminology across sections, reconciles disagreements and confirms revision identity. Recheck affected sections if revision moves; do not blend snapshots. This pass may run beside bibliography Layers 1/2 on a shared fixed inventory with independent judgments. Layer 3 still requires separate opt-in and original evidence.

**Done:** sections are owned once and disagreements/revision remain visible.

## 5. Optional approved changes

Default deliverable is findings only. Apply only specifically approved suggestions under project editing rules while preserving collaborator changes. Compare new passages with originals for meaning, numbers, qualifiers, terminology and TeX integrity; re-audit affected context. Wording edits do not validate citations or claims.

**Done:** either no source changed or approved edits have separately recorded limited verification.

## Provenance

Context-first, claim-preserving principles were informed by public registry summaries of Academic Writing Polisher (figpad, v1.0.1) and SCI/SSCI Polishing (yila-ai, v1.0.0). This independent diagnostic guidance does not install or copy either package, script or reference. Their complete packages/licenses were not reviewed here; importing their material requires separate licensing/security review.
