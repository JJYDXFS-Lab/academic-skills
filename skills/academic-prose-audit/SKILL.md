---
name: academic-prose-audit
description: Read-only contextual academic phrasing/register audit of an authorized fixed manuscript revision, with file:line evidence and minimal meaning-preserving suggestions for natural, precise author voice. Parallel section review; edits require separate approval.
---

# Academic prose audit

## 1. Fix scope and boundaries

Identify authoritative revision/hash, reachable prose files/sections, exclusions, discipline, audience, terminology and author preferences. Record a read-only boundary and obey the local project's locality and source-of-truth rules: a local clone may be stale. Keep unpublished prose local; do not upload, edit or push manuscript sources without exact approval or run untrusted TeX with shell escape. The main task is to assess academic phrasing and register for natural, precise author voice; grammar and TeX screening are supporting safeguards. "AI flavor" names a stylistic impression, not AI-authorship detection, a score, or evasion advice. This is not a claim-support verdict.

**Done:** revision, sections, exclusions, terminology, locality and write boundary are explicit.

## 2. Read prose in context

Read [contextual phrasing checks](references/contextual-phrasing.md) for diagnostic questions and counterexamples, including repeated sentence/punctuation patterns and sentence information content. Judge a sentence's function in its paragraph, not a phrase list.

Inspect sentences with paragraph and section purpose. Distinguish prose from TeX commands, equations, citation keys, labels, comments, Bib entries, protected names and literal quotations. Do not change protected spans by default; editing quotations requires explicit request. Track locations and coverage gaps for macros, generated inputs, unsupported syntax and missing files. Text search finds candidates but is not complete parsing.

Optional local triage, only after fixing an authorized file list: `python3 <skill-dir>/scripts/prose_candidates.py path/to/section.tex` (replace `<skill-dir>` with the directory containing this `SKILL.md`). This stdlib-only helper reads explicitly named `.tex` files and prints `file:line` context and review questions; it never edits its inputs. It masks detectable comments, math, commands and arguments (including citations and labels), verbatim and quotation spans and skips unsupported environments. TeX coverage is deliberately non-exhaustive: common unsupported environments and straight-quote ambiguity can hide prose without a precise coverage count, while custom macros, generated inputs, complex catcodes and unmatched constructs can hide prose or yield false positives. It does not expand `\input`, discover files, prove an absence of issues or produce audit findings by itself. Treat its small set of phrase cues as optional questions, not banned words, style rules, scientific conclusions or replacement instructions. Verify every candidate against the actual surrounding paragraph and section; do not infer clean coverage from zero output.

The CLI's stdout includes manuscript snippets: keep console output, redirects and logs private. It validates every named file before printing any findings and fails with a coverage error on detected unclosed regions; a failed scan does not certify any portion of that file. Stderr reports skipped command-argument counts, including a rough count containing letters; these include citation keys and labels, so neither count measures reviewed prose or proves completeness. Prose inside command arguments (for example section headings or custom macros) is intentionally masked and must be reviewed separately in context.

Examine academic phrasing in the paragraph's argument: empty or generic claims, promotional or overwritten language, stock transitions and repeated rhetorical templates, vague metaphors, synonym churn, unnatural collocations, redundant or unclear wording, generic conclusions and overconfident phrasing. Explain what this particular use obscures or overstates. Do not use banned-word lists: no word alone proves a problem. `story` may name a study or story-generation task; `buy` may denote a purchase or buy order. Titles, quotations and technical terms may legitimately use either. Preserve legitimate disciplinary style and deliberate repetition; neither ordinary wording nor stylistic awkwardness is evidence of AI generation.

Across neighboring sentences and paragraphs, check repeated openings, transitions, symmetrical constructions, conclusion templates and punctuation patterns. For em dashes (TeX `---` or Unicode `—`, not TeX en-dash `--` ranges), inspect their actual count in a stated passage and what each interruption does: a single useful clarification may belong, while recurring dramatic asides can obscure the argument. No dash ban or arbitrary frequency threshold applies. For a potentially generic sentence, ask what action, result, comparison or condition it communicates and whether replacing its method/domain names would leave only interchangeable framing. This substitution is a question, not a verdict: topic introductions, roadmaps and meaningful summaries can be concise and general. Distinguish unsupported promotional claims and absent referents/comparators from useful summary; do not invent specifics, numbers or evidence to make a sentence look informative. Suggest removing empty framing where meaning permits; otherwise ask the author for the missing detail.

Before suggesting a replacement, preserve quantities and units, comparison baselines, scope and negation, conditions and quantifiers, modality, causal direction, technical terms, necessary hedges, citation attachment and author voice. Prefer the smallest natural change that suits the domain. Do not strengthen claims for polish, reflexively weaken supported claims, or replace domain terms with ornate synonyms. Ask the author when intent is unclear. Passive voice, `only` and hedges are context cues, not defects by themselves.

**Done:** findings were checked against context and protected spans; legitimate uses and coverage limits are separated.

## 3. Return traceable, conservative findings

Default deliverable: the agent authors a new, standalone `prose-audit.html` (name adaptable) in an authorized report location outside the source tree. Never overwrite an existing report. It must open offline with inline CSS, no CDN/network requests/external assets and no framework or JavaScript requirement. Include a readable summary of revision, scope, exclusions, reviewed coverage, finding and severity totals, unverified/undecided counts and coverage gaps. Foreground the exact original phrase and minimal natural suggestion (or author question) side by side; for each finding show `file:line`, brief paragraph/section context, the specific reason it is problematic here, evidence, severity and confidence. Native `<details>` may hold long context. HTML-escape all source and evidence text; never execute manuscript HTML. Markdown is optional on user request; the triage helper does not generate the full audit report.

State actual execution mode (sequential or parallel), worker count and any worker receipt/failure or incomplete portion in the report summary; this is not proof that a particular host supports subagents.

Escape HTML attribute values as well as text; render source-derived links only after validating an `https:` or `http:` scheme. Keep local/file and script schemes as escaped plain text.

Use `substantive` when wording distorts meaning/calibration, `editorial` for demonstrable phrasing/register/clarity problems, and keep optional taste preferences distinct from defects. Do not rewrite a paragraph to fix one phrase. Omit weak findings or mark them as author questions; never infer a problem from a stock word alone. Include useful deliberate nonissues. No findings means no high-confidence issues in reviewed scope, not perfect prose.

For pattern findings, give the observed examples and count/scope (for example, the openings in a named paragraph), then explain why the repetition matters here; do not present a punctuation count alone as a defect. For specificity findings, name the missing referent/comparison or unsupported assertion and give a meaning-preserving local suggestion or author question. Both remain style/clarity judgments, never authorship claims.

Label source-support questions `support unreviewed`; refer them to `latex-bib-audit` Layer 3 only if explicitly enabled. Its default Layers 1/2 do not validate scientific claims. Tone alone cannot show a claim is false.

**Done:** the fresh HTML report makes each issue contextualized, locatable and actionable without unsupported authorship or scientific conclusions.

## 4. Parallel review and reconciliation

When subagents are actually available and scope benefits, proactively assign bounded read-only sections within the available limits/budget; routine delegation needs no separate approval. For small scope or no subagents, perform the same audit sequentially. First fix revision, glossary, ownership and report schema; avoid nested uncontrolled spawning and concurrent final-HTML or source writes. Collect actual worker findings, nonissues, gaps and failures; reassign bounded gaps or report incomplete coverage honestly. Never claim parallel work without worker receipts.

Delegation is conditional on host/project spawn policy and workers staying inside the same authorized privacy/locality boundary; availability alone never authorizes manuscript upload. The coordinator checks recurring templates/transitions across section boundaries as well as terminology. Prose and bibliography work may share a fixed revision and file-scope agreement, but not a merged BibTeX inventory or evidential conclusions.

Give workers one fixed revision, scope, glossary and read-only boundary. Partition nonoverlapping sections/paragraphs; adjacent paragraphs can provide context without duplicate finding ownership. Workers return findings, nonissues and gaps, not concurrent edits. One coordinator deduplicates boundary issues, checks terminology and recurring templates across sections, reconciles disagreements and confirms revision identity. Recheck affected sections if revision moves; do not blend snapshots. This pass may run beside bibliography Layers 1/2 on the same fixed revision with independent judgments. Layer 3 still requires separate opt-in and original evidence.

**Done:** sections are owned once and disagreements/revision remain visible.

## 5. Optional approved changes

Default deliverable is findings only. Apply only specifically approved suggestions under project editing rules while preserving collaborator changes. Compare new passages with originals for meaning, numbers, qualifiers, terminology and TeX integrity; re-audit affected context. Wording edits do not validate citations or claims.

**Done:** either no source changed or approved edits have separately recorded limited verification.

## Provenance

This skill independently adapts diagnostic ideas from [Academic Humanizer at 94b88b2](https://github.com/AIScientists-Dev/academic-humanizer/tree/94b88b23703bed7df507acae7d6d5876209a0cdf) (MIT, 2026 AIScientists-Dev; itself builds on blader/humanizer and adopts ARMS standards) and [Academic Writing Expert at 07a872c](https://github.com/shuozhang-shz/academic-writing-expert/tree/07a872c43a7ab08f6eef2b83c21ef33f35679434) (MIT, 2026 Academic Writing Expert contributors; [NOTICE](https://github.com/shuozhang-shz/academic-writing-expert/blob/07a872c43a7ab08f6eef2b83c21ef33f35679434/NOTICE.md) excludes third-party works). No upstream code, examples or substantial text was copied; license links and exclusions are in the reference.

Context-first, claim-preserving principles were informed by public registry summaries of Academic Writing Polisher (figpad, v1.0.1) and SCI/SSCI Polishing (yila-ai, v1.0.0). This independent diagnostic guidance does not install or copy either package, script or reference. Their complete packages/licenses were not reviewed here; importing their material requires separate licensing/security review.

The earlier registry references are [Academic Writing Polisher v1.0.1](https://clawhub.ai/figpad/skills/academic-writing-polisher) and [SCI/SSCI Polishing v1.0.0](https://clawhub.ai/yila-ai/skills/sci-ssci-polishing), consulted as summaries in October 2026. They did not supply copied text or packages.

The contextual phrasing reference is diagnostic only: no blanket em-dash rule, word-count cutoff, automatic weakening of `demonstrate`, invented evidence or claim-support verdict. Original-paper support belongs only to explicitly opted-in bibliography Layer 3.
