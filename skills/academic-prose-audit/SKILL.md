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

Assess colloquial, promotional, vague, metaphorical, redundant, unclear or overconfident language in context, not using banned-word lists. `story` may name a study or story-generation task; `buy` may denote a purchase or buy order. Titles, quotations and technical terms may legitimately use either. Repetition and ordinary wording are not evidence of AI generation.

Preserve numbers, comparisons, conditions, uncertainty, causal direction, technical meaning, terminology and author voice. Do not strengthen claims for polish, reflexively weaken supported claims, or replace domain terms with ornate synonyms. Ask if intent is unclear.

**Done:** findings were checked against context and protected spans; legitimate uses and coverage limits are separated.

## 3. Return traceable, conservative findings

For high-confidence issues report `file:line | exact phrase + context | issue | why | minimal replacement or author question | severity/confidence`. Use `substantive` when wording distorts meaning/calibration, `editorial` for clear register/clarity problems, and keep optional preferences separate. Do not rewrite a paragraph to fix one phrase. Omit weak findings or mark them as questions. Include revision/scope/coverage and useful deliberate nonissues. No findings means no high-confidence issues in reviewed scope, not perfect prose.

Label source-support questions `support unreviewed`; refer them to `latex-bib-audit` Layer 3 only if explicitly enabled. Its default Layers 1/2 do not validate scientific claims. Tone alone cannot show a claim is false.

**Done:** each issue is contextualized, locatable and actionable without unsupported authorship or scientific conclusions.

## 4. Parallel review and reconciliation

Give workers one fixed revision, scope, glossary and read-only boundary. Partition nonoverlapping sections/paragraphs; adjacent paragraphs can provide context without duplicate finding ownership. Workers return findings, nonissues and gaps, not concurrent edits. One coordinator deduplicates boundary issues, checks terminology across sections, reconciles disagreements and confirms revision identity. Recheck affected sections if revision moves; do not blend snapshots. This pass may run beside bibliography Layers 1/2 on a shared fixed inventory with independent judgments. Layer 3 still requires separate opt-in and original evidence.

**Done:** sections are owned once and disagreements/revision remain visible.

## 5. Optional approved changes

Default deliverable is findings only. Apply only specifically approved suggestions under project editing rules while preserving collaborator changes. Compare new passages with originals for meaning, numbers, qualifiers, terminology and TeX integrity; re-audit affected context. Wording edits do not validate citations or claims.

**Done:** either no source changed or approved edits have separately recorded limited verification.

## Provenance

Context-first, claim-preserving principles were informed by public registry summaries of Academic Writing Polisher (figpad, v1.0.1) and SCI/SSCI Polishing (yila-ai, v1.0.0). This independent diagnostic guidance does not install or copy either package, script or reference. Their complete packages/licenses were not reviewed here; importing their material requires separate licensing/security review.
