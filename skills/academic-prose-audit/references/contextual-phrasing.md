# Contextual phrasing checks

Read the sentence's function in its paragraph and the section argument. These are questions, not forbidden words, authorship detection, evasion advice or rewriting instructions. Examples are newly composed synthetic prompts; verify any proposed change against author intent and actual evidence.

| Question | Candidate concern here | Legitimate use or boundary |
| --- | --- | --- |
| Does a temporal opening locate a real change? | `In recent years, our method improves accuracy on D.` The opening gives no period or relevant trend; ask whether it can be removed. | `Since the 2021 protocol change, ...` dates a comparison and should remain if material. |
| Does a contribution claim name its contribution? | `Our groundbreaking framework revolutionizes the field.` Ask for a concrete advance or omit unsupported promotion. | `We introduce a framework that supports X under Y` is concrete; substantiated novelty need not be muted. |
| Does a transition express a relation? | Three paragraphs start `Furthermore` without distinct added reasons; identify the redundant bridge. | `However` can signal a real contrast; repetition may deliberately structure enumerated results. |
| Do adjacent paragraphs share an empty template? | Each closes `This highlights the importance of our approach` without explaining the result; ask what follows from each finding. | Consistent Methods structure and repeated technical terms can improve comparability. |
| Does emphasis or meta prose add information? | `Importantly, it is worth noting that accuracy increased` may add no priority; suggest removing framing only if nothing is lost. | `Importantly` can distinguish a prespecified primary endpoint; a roadmap may orient a complex section. |
| Is a collocation or synonym natural here? | `The algorithm harvested a robust victory` may obscure the measured comparison; ask for the domain's terms. | `Harvested samples` in fieldwork and `association` in statistics are meaningful, not synonyms to eliminate. |

An introduction may legitimately summarize a cited adoption trend with `In recent years`; check whether that temporal scope conveys real evidence before flagging it. `Robust` is a technical term in statistics and optimization; distinguish it from vague praise.

## Protect meaning before any suggestion

| Original claim | Unsafe shift | Conservative response |
| --- | --- | --- |
| `Only group A improved under treatment T.` | `Group A improved only under treatment T.` changes the scope of `only`. | Preserve scope or ask which restriction is intended. |
| `We found no evidence of an effect.` | `We found evidence of no effect.` asserts stronger evidence. | Keep the absence-of-evidence claim; ask about an equivalence test if relevant. |
| `The difference was not statistically significant (p = 0.18).` | `The groups were equivalent.` does not follow. | Preserve the result; distinguish equivalence testing. |
| `Under condition C, accuracy increased by 4 percentage points over baseline B on D.` | `Accuracy improved significantly.` discards condition, units, comparator and dataset while adding ambiguous significance. | Retain C, 4 percentage points, B and D; ask separately whether a significance test exists. |
| `X was associated with Y in the adjusted model (\cite{key}).` | `X caused Y` changes causal strength; moving the citation may change its attachment. | Preserve association, model qualifier and citation scope. |

Give each real finding `file:line`, paragraph context, why problematic **here**, and a minimal suggestion or author question. Separate style taste from defects; record useful nonissues. No numerical evidence may be invented. Support questions are `support unreviewed`, not original-paper verification; only separately opted-in bibliography Layer 3 checks support.

## Sources and adaptation boundary

- [Academic Humanizer, commit 94b88b23703bed7df507acae7d6d5876209a0cdf](https://github.com/AIScientists-Dev/academic-humanizer/blob/94b88b23703bed7df507acae7d6d5876209a0cdf/SKILL.md): audit-first and contextual questions about generic openings, transitions, contribution templates and emphasis. [MIT license](https://github.com/AIScientists-Dev/academic-humanizer/blob/94b88b23703bed7df507acae7d6d5876209a0cdf/LICENSE), copyright 2026 AIScientists-Dev; its license acknowledges blader/humanizer and ARMS. We exclude its rewriting workflow, blanket em-dash removal, sentence-length threshold, automatic `demonstrate` downgrade and examples adding unsupported numbers.
- [Academic Writing Expert, commit 07a872c43a7ab08f6eef2b83c21ef33f35679434](https://github.com/shuozhang-shz/academic-writing-expert/blob/07a872c43a7ab08f6eef2b83c21ef33f35679434/references/language-and-style.md): scope/qualifier/hedge preservation and absence-of-evidence distinctions. [MIT license](https://github.com/shuozhang-shz/academic-writing-expert/blob/07a872c43a7ab08f6eef2b83c21ef33f35679434/LICENSE), copyright 2026 Academic Writing Expert contributors; its [NOTICE](https://github.com/shuozhang-shz/academic-writing-expert/blob/07a872c43a7ab08f6eef2b83c21ef33f35679434/NOTICE.md) excludes third-party books, articles and slides. We exclude its default rewriting workflow and do not copy its worked examples or third-party materials.

Only diagnostic ideas are paraphrased here with newly composed examples; no upstream package, code or substantial text is redistributed. Before any later substantial copying, retain the applicable MIT copyright/license notices and check third-party provenance.
