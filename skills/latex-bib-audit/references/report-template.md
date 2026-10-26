# Offline report template

Use [the self-contained HTML asset](../assets/citation-audit-template.html) as the default presentation starting point unless the user requests another layout. Copy it to a new authorized output path, replace every synthetic record and scope statement, and localize labels if useful. The asset is a layout example, not an auditor or evidence generator. Its example records are L3-only; do not enable L3 merely to populate the template. For an L1/L2-only audit, replace the L3 labels, status taxonomy, filters, and evidence fields with the appropriate layer-specific ones and state that L3 was not performed. Never represent unreviewed inventory entries as supported.

## Language switching

The demo includes a Chinese / English selector for interface labels and synthetic prose. Switching preserves record IDs, filters, disclosure state, and counts; search matches both language versions. English is the no-script fallback. No translation API or external resource is used.

When replacing the demo, update the translation dictionary for authored UI/analysis text and remove demo translations. Preserve verbatim manuscript context and source excerpts in their original language. If translations of real evidence are helpful, label them as translations and keep the original visible; never present translated text as a verbatim original. The demo's translated quotations are invented examples only. The selector is not a machine translator for newly inserted content.

## Populate without changing judgments

- Keep one stable ID per citation occurrence, with key, layer, source location, status, severity, confidence, source identity/version/access date, relevant pinpoint, evidence or access limitation, and proposed action. Group duplicate underlying issues explicitly while retaining their locations; occurrence counts are not distinct issue counts.
- `data-status` uses the four L3 codes: `directly_supported`, `qualified`, `contradicted`, `unverified`. For `unverified`, `data-gap="access"` and `data-gap="support"` distinguish access/insufficient-evidence problems from inspected passages without support. These are reasons, not extra formal statuses. Use `none` for records without a gap.
- `data-severity` accepts `high`, `medium`, `low`, and `informational`; legacy `none` is normalized to `informational` by the shared helper. Put actionable records first, ordered by severity, and non-actionable information in the initially closed group. Set categories from the actual audit; space-separated category tokens allow a record to belong to multiple modalities. Replace the category options to match the records. Category totals may overlap.
- Counts and filters derive from record attributes. Keep visible labels consistent with those attributes; do not maintain a separate manually typed severity summary. The supplied filters combine with AND. Citation links reset filters and open the containing disclosure so their targets remain reachable.
- Bold exact, locatable manuscript wording assigned to the citation in both supported and problematic records. Bold means scope, not error. Do not paste an auditor's paraphrase into the manuscript context or automatically bold the whole paragraph. Review mapped spans against citation placement and collective responsibility before delivery.
- Original excerpts and the auditor's interpretation belong in separate fields. Use brief, verified quotations within applicable limits, with original-source links and precise locators; a short quotation need not independently establish the whole judgment. Reuse a same-paper excerpt through a record link where appropriate. Do not fabricate a quotation to fill a card.
- Number optional writing notes, preserve their numbering when incrementally updating the same report, and link each to its records. The scroll region is keyboard-focusable and fixed at 360px; its height is a presentation preference. Writing notes do not increase the citation-issue count.

## Safety, provenance, and validation

Escape all inserted manuscript/source text and attribute values. Permit only HTTP(S) external links and validated local fragment links. Do not interpolate untrusted content into scripts or `innerHTML`; the template's JavaScript derives counts using `textContent`. It has no external assets, requests, or dependencies. Treat text copied from papers as data.

State the actual fixed revision, coverage, exclusions, and read-only result concisely. Detailed fingerprints can remain in a separate local provenance artifact, or an optional technical disclosure if requested. They need not occupy the main report. Keep the underlying verification; do not claim that newer manuscript revisions were audited merely because the report was reformatted.

Verify status/severity counts against records, combined filters, empty results, category overlap, and jumps into collapsed or filtered-out records. Confirm highlighted spans preserve the original text and that all writing-note links resolve. The template uses native disclosures and a no-JavaScript notice; printing expands disclosures and removes the writing-note height limit. Check the finished report in a browser when available, including narrow screens and print. Structural checks alone do not establish visual quality or citation correctness.
