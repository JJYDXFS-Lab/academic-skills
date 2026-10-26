# Opt-in claim evidence (Layer 3)

Only after the owner explicitly requests claim verification: resolve the citation key to its actual item, DOI/identifier, version and publication status. Check the original primary paper, official open-access version, or author-accepted manuscript; do not use secondary summaries as substitute. Public identifier/title queries are allowed only within the approved access boundary; unpublished claim text stays local. Record URL/identifier, version, access date, and precise section plus page, paragraph, equation, figure or table. For HTML without pagination, use heading and unique paragraph/table locator; if no pinpoint is accessible, mark `unverified` and state what was attempted.

Compare the exact local claim with the source's population, method, quantity, qualifiers and caveats. Mark directly supported, supported with qualification, contradicted or unable to verify; an abstract, snippet, metadata match or successful PDF download alone does not support a detailed claim. Keep disagreements with Layer 1 identity and Layer 2 mapping visible. Do not invent text, page numbers, intended references or corrections.


## Establish responsibility before judging support

Read the actual citation position and enough surrounding prose to resolve parentheses, appositions, coordinated clauses, and paragraph-level synthesis. Record the specific claim this citation supports; a large extraction window is context, not an obligation to support every sentence in it.

For grouped citations, map the sources' contributions to the collective claim. Each paper need not implement every listed example or establish every component, but every source assigned to the claim must have an explainable contribution. Support from A does not validate an unrelated X in [A, X]; assess X separately and record a support gap if its relevant original text supplies no contribution. A source's related-work discussion can support background context, but does not establish that its own method implements the discussed mechanism. Conversely, an explicit attribution to a named method, numerical result, theorem, or tightly defined task still requires support for that attribution. Do not move a citation to an unrelated claim merely to make it pass.

Use the reasonable reading of the manuscript's wording. Do not silently strengthen a capability into simultaneous public availability, a learned mapping into a mathematical inverse, or an illustrative mechanism into a requirement for every member of a family. Distinguish authors' marked hypotheses, analogies, proposals, and synthesis from results attributed to a cited paper. Explicit universal quantifiers, causal claims, and numerical ranges still matter when they materially change the assertion.

## Check materiality and evidence

Before issuing an adverse finding:

1. State the local or collective claim and the source's assigned contribution.
2. Inspect the relevant original passage, including nearby definitions, experiments, limitations, or appendices when needed. A keyword miss or a short excerpt omitting a detail is not evidence that the full paper lacks support.
3. Identify the concrete discrepancy and how it changes the claim's meaning. Consider whether a reasonable reading and the other grouped sources already supply the necessary support.

A more precise formulation is not automatically a citation defect. If the claim is adequately supported at its stated level, mark it supported and keep any optional writing suggestion separate from actionable findings. Do not promote an ambiguous citation placement to a confident factual error; explain the ambiguity and, when material, ask the author to resolve its intended scope. Do not use charitable interpretation to excuse an explicit wrong input representation, implemented task, number, or theoretical result.

Use the existing support statuses consistently:

- **Directly supported:** the assigned contribution supports the reasonable local or collective claim; optional elaboration is not needed for correctness.
- **Supported with qualification:** a material condition or restriction is needed for that claim to hold. State the restriction, rather than merely suggesting more detail.
- **Contradicted:** original evidence conflicts with the assigned assertion. Absence of a matching sentence, or proof of only a weaker proposition, is not contradiction. Require incompatible evidence; otherwise record the unsupported claim as Unable to verify, or Supported with qualification when a specific supported restriction resolves the gap.
- **Unable to verify:** distinguish inaccessible/insufficient source evidence from relevant passages inspected without finding the claimed support. Record what was inspected and the remaining gap; do not claim exhaustive absence from a failed search.

Keep severity separate from confidence. Group repeated occurrences of the same substantive issue while retaining all source locations; report coverage counts separately from distinct actionable issues. A brief, verified original excerpt plus a precise locator makes a finding reviewable, but the excerpt need not carry the entire argument. Respect quotation limits and reuse a same-paper excerpt by reference where appropriate.

For behavioral validation of changes to these rules, use the invented cases in [L3 calibration cases](l3-calibration-cases.md). These are decision checks, not real-paper evidence or automated proof of audit accuracy.
