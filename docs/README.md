# Academic Skills documentation

The [bibliography](../skills/latex-bib-audit/SKILL.md) and [prose](../skills/academic-prose-audit/SKILL.md) skills contain their audit procedures and linked resources. Both review a specified manuscript revision without editing the source; reports go to a separately authorized location.

## Install and use

Access to `JJYDXFS-Lab/academic-skills` is required. In Codex, use the [copyable `$skill-installer` request](../README.md#codex-install).

The installer places complete directories under `$CODEX_HOME/skills` (default `~/.codex/skills`) and refuses an existing destination. Use normal GitHub credentials for private access. Restart Codex and check `/skills`; invoke `$latex-bib-audit` and `$academic-prose-audit` as needed. See [Codex skill locations](https://developers.openai.com/codex/skills).

**Update:** pulling a source clone does not change installed copies, and the installer will not overwrite them. Compare new skill directories with the installed ones, preserve any personal changes, then replace the two installed directories and restart Codex.

**Claude Code or another agent:** copy both complete directories from a clean clone to that agent's documented user or project skill location, then confirm discovery there. If skill installation is unavailable, point the agent at the relevant `SKILL.md` file in the prompt.

First-use prompt (replace placeholders and choose an authorized report directory):

```text
Use $latex-bib-audit and $academic-prose-audit on the authorized manuscript
revision <hash>, main file <main.tex>, sections <scope>. Run bibliography
Layers 1 and 2 and contextual prose review; Layer 3 is off. Do not edit
the manuscript or Bib files. Write fresh HTML reports in
<authorized-report-dir>. Report uncertainty and coverage gaps.
```

## Optional helpers

The skills need no Python package for discovery or manual review. Optional scripts use Python 3.9+; bibliography comparison/inventory/retrieval helpers need `pybtex`. For example, `python3 skills/latex-bib-audit/scripts/compare_candidates.py original.bib candidate.bib --output /fresh/report-directory/comparison.json` compares same-key fields, while `python3 skills/academic-prose-audit/scripts/prose_candidates.py path/to/section.tex` flags possible phrasing questions. Helpers cover only the files/keys provided and do not complete an audit; consult the linked skill instructions for their limits.
