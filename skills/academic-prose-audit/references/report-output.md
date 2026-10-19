# Report output

Make a new offline self-contained HTML report in an authorized report directory; refuse overwrite. Escape HTML text and attribute values from source, use validated HTTP(S) links only, and avoid scripts/CDNs and remote images. Native `<details>` can keep context readable. User may instead request Markdown or plain text. Provide totals, coverage gaps, unverified/undecided counts, language, hashes/mtime/HEAD, and actual worker mode. Map each finding to a contextual-phrasing question category or explain its grounded exception.

Synthetic finding (all source lines below invented):

| Field | Example |
| --- | --- |
| Location/context | `synthetic.tex:12`, Discussion; paragraph contrasts models A and B on dataset D. |
| Original | “Our groundbreaking model revolutionizes accuracy.” |
| Minimal suggestion | “Model A achieved higher accuracy than model B on D.” **Only if** that comparison is already established in the paragraph; otherwise ask: “Which comparison and dataset justify this claim?” |
| Why/severity/confidence | “Groundbreaking” and “revolutionizes” promise more than the supplied comparison; `editorial`, medium confidence pending author confirmation. Support unreviewed. |

Overwritten example: original “Under condition C, A increased by 4 percentage points over B on D.” / overwritten “Our remarkable approach delivers a transformative improvement.” / minimal “Under condition C, A was 4 percentage points higher than B on D.” This preserves conditions, unit, baseline and dataset without inserting unverified claims. For a valid deliberate use of “robust” as a statistical term, record a nonissue instead of a finding. Do not turn this example's made-up evidence into manuscript facts.
