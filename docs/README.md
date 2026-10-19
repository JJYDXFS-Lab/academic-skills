# Academic Skills documentation

This is the canonical, harness-agnostic source for two ordinary AgentSkills in `skills/`: YAML `name`/`description` frontmatter and an instruction body, with linked relative resources. Reading a skill does not grant manuscript access, network or Python execution permission, editing authority or automatic discovery. If tools are unavailable, report the coverage gap rather than treating unchecked items as passed. Parallelism is optional: sequential review of the same frozen revision and scope is equally valid.

## Install and use

Obtain the source first: `git clone https://github.com/JJYDXFS-Lab/academic-skills.git` works only for readers with access to this repository (authenticate using your normal GitHub setup if it is private). A public reader without access needs an authorized copy; these instructions do not make a private repository public. No Python package is needed to read or use the instructions. Python 3 is needed only to run the optional triage helpers; `pybtex` is additionally needed only for the BibTeX comparator, installed separately in an isolated environment when authorized.

For Codex CLI, install **both complete directories** from a clean clone or other inspected artifact-free source into the documented user scope, without replacing an existing installation. Do not copy ignored local run artifacts or receipts from a development checkout:

```bash
mkdir -p "$HOME/.agents/skills"
if [ -e "$HOME/.agents/skills/latex-bib-audit" ] ||
   [ -e "$HOME/.agents/skills/academic-prose-audit" ]; then
  printf '%s\n' 'Install stopped: inspect existing skill directories first.' >&2
else
  cp -R /path/to/academic-skills/skills/latex-bib-audit /path/to/academic-skills/skills/academic-prose-audit "$HOME/.agents/skills/"
fi
```

Alternatively use `<manuscript-repo>/.agents/skills/` in place of `$HOME/.agents/skills/` for that repository only. Keep `SKILL.md`, `references/`, `scripts/`, tests and the comparator at the skill root together; copying only `SKILL.md` breaks relative resources. If you cannot install, point the agent at the two `SKILL.md` paths in the prompt instead. Codex scans user and repository skill locations; in Codex CLI run `/skills` to confirm both are listed, then mention `$latex-bib-audit` or `$academic-prose-audit`. It detects new/updated skills automatically; restart Codex if changes do not appear. This describes installation; no real Codex install/discovery was performed for this repository. See [official Codex skill locations](https://developers.openai.com/codex/skills).

Copyable first-use request after discovery (replace placeholders and authorize the report directory):

```text
Use $latex-bib-audit and $academic-prose-audit on the authorized manuscript
revision <hash>, main file <main.tex>, sections <scope>. Run bibliography
Layers 1 and 2 and contextual prose review; Layer 3 is off. Do not edit
the manuscript or Bib files. Write fresh standalone offline HTML reports
outside the source tree in <authorized-report-dir>; do not overwrite files.
Report uncertain identities and coverage gaps; propose corrections only.
```

## Coding-agent invocation

Fix the authoritative revision, scope and read-only boundary first. Example prompt: `Read /path/to/academic-skills/skills/latex-bib-audit/SKILL.md; on manuscript revision <hash>, audit bibliography metadata and citation identity, findings only.` For prose: `Read /path/to/academic-skills/skills/academic-prose-audit/SKILL.md; review sections <scope> on revision <hash>, findings only.` Supply access through the project's existing permissions. Layer 3 of the bibliography skill requires a separate explicit request and original-paper evidence. Prose review is not AI detection or scientific validation.

For a local Codex session (or any file-reading agent), an example user request is:

```text
Read /path/to/academic-skills/skills/latex-bib-audit/SKILL.md and
/path/to/academic-skills/skills/academic-prose-audit/SKILL.md.
For the authorized manuscript revision <hash>, main file <main.tex>, and
sections <scope>, run bibliography Layers 1 and 2 and a contextual prose audit
on the same frozen revision. Layer 3 is disabled. Keep the manuscript and Bib
files unchanged; author separate, fresh citation-audit.html and prose-audit.html
in an authorized <report-directory> outside the source tree. Both must open
offline with inline CSS, no external assets/network, and HTML-escaped sources.
Report file:line/key, original/proposed text or field, source evidence,
reasoning, severity, uncertainty and coverage gaps. No auto-fix.
```

The default reports are agent-authored standalone HTML, with a readable scope/revision summary, layer coverage where applicable, severity and unverified counts, and a visible `© <report year> JJYDXFS & Atom (原子). All rights reserved.` footer linking [JJYDXFS](https://jjydxfs.github.io/) and [Atom (原子)](https://atom-of-jjydxfs.github.io/). Output names can be adapted; never overwrite a report. Markdown is optional on user request. Escape all manuscript-derived HTML; no frontend framework or JavaScript is needed.

The plain Python optional triage tools are `python3 skills/latex-bib-audit/compare_candidates.py --help` and `python3 skills/academic-prose-audit/scripts/prose_candidates.py --help`. The former compares two existing same-key BibTeX files and requires separately installed `pybtex`; its real-parser integration tests are skipped when that library is absent, so actual parser behavior remains unverified here. Use `python3 skills/latex-bib-audit/compare_candidates.py original.bib candidate.bib --output /fresh/report-directory/comparison.json` to create a **new** report exclusively after a successful comparison. The latter is stdlib-only and prints non-exhaustive questions for explicitly named TeX files. Neither tool discovers the project or performs a complete audit. Both can print source-derived content: keep reports, stdout and stderr local/private. Never redirect stdout into a source or existing report: shell redirection can truncate a file before the script runs. The agent, not these scripts, must locate sources and judge evidence.

For coding agents with project-local skills, manually copy or link each full skill directory into that agent's documented project-local skill location. Confirm discovery under the agent's own instructions. Do not change global agent configuration as part of using this repo. Apply the manuscript project's locality, privacy, collaborator and editing rules.

## Manual publication

Edit and validate canonical files here first, then commit. When manually deploying a copy, record this repo's commit and SHA-256 of skill files, compare hashes after copying, and document any local adapter-only divergence. Do not treat deployment copies as a second authority, set up autosync, or depend on cross-host symlinks. Local project-specific constraints remain in that project's instructions; preserve them when republishing a portable skill.

No private run inputs or receipts belong in this source repository. Validation of these instruction files does not imply that a manuscript was audited.
