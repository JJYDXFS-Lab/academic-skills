# Academic Skills documentation

This is the canonical, harness-agnostic source for two ordinary AgentSkills in `skills/`: YAML `name`/`description` frontmatter and an instruction body, with linked relative resources. Reading a skill does not grant manuscript access, network or Python execution permission, editing authority or automatic discovery. If tools are unavailable, report the coverage gap rather than treating unchecked items as passed. Parallelism is optional: sequential review of the same frozen revision and scope is equally valid.

## Install and use

Readers need access to `JJYDXFS-Lab/academic-skills` (authenticate with normal GitHub credentials if private); these instructions do not make a private repository public. No Python package is needed to read or use the skills. Python 3 is needed only for optional triage helpers; `pybtex` is separately needed only for the BibTeX comparator, installed in an isolated environment when authorized.

In Codex CLI, use its bundled `$skill-installer` (available on installations that include it). Copyable request:

```text
$skill-installer Install both skills from GitHub repository JJYDXFS-Lab/academic-skills:
skills/latex-bib-audit and skills/academic-prose-audit. Do not replace any
existing installation; report any access or existing-directory error.
```

The bundled installer's documented command is `scripts/install-skill-from-github.py --repo JJYDXFS-Lab/academic-skills --path skills/latex-bib-audit skills/academic-prose-audit`; it installs both complete directories under `$CODEX_HOME/skills` (default `~/.codex/skills`) and aborts if a destination exists. For private access it uses existing Git credentials or `GITHUB_TOKEN`/`GH_TOKEN`; do not put tokens in prompts or reports. Restart Codex after installation to discover the new skills; then use `/skills` to confirm both and invoke `$latex-bib-audit` or `$academic-prose-audit`. This documents the local bundled installer; no actual Codex skill installation/discovery was performed for this repository. See [official Codex skill locations](https://developers.openai.com/codex/skills).

**Updating installed copies:** this bundled installer has no in-place update/force option; rerunning the install against existing directories stops, and `git pull` in a source clone does not update installed copies. Ask Codex to use `$skill-installer` with a fresh `--dest` staging directory for both complete skills, compare each staged directory with the installed copy, and preserve or resolve local edits with the user before changing anything. Once both are staged successfully, back up only the two old skill directories outside active skill discovery, then replace only those named directories with their staged counterparts. Restore the backups if replacement fails; report the source revision and any local differences, and restart Codex. The staging destination must be new and separate from `$CODEX_HOME/skills`; this is a deliberate update workflow, not a promise of atomic multi-skill installation.

If `$skill-installer` is absent, or for another agent's documented project-local skill location, obtain a clean clone or inspected artifact-free source and copy **both complete directories** without replacing existing destinations. Do not copy ignored local run artifacts or receipts from a development checkout:

```bash
d="${CODEX_HOME:-$HOME/.codex}/skills"
mkdir -p "$d"
if [ -e "$d/latex-bib-audit" ] ||
   [ -e "$d/academic-prose-audit" ]; then
  printf '%s\n' 'Install stopped: inspect existing skill directories first.' >&2
else
  cp -R /path/to/academic-skills/skills/latex-bib-audit /path/to/academic-skills/skills/academic-prose-audit "$d/"
fi
```

For a project-local fallback, use the agent's documented project skill location instead and create its parent directory first. Keep `SKILL.md`, `references/`, `scripts`, tests and the comparator together; copying only `SKILL.md` breaks relative resources. Restart Codex after manual installation. If installation is unavailable, point the agent at both `SKILL.md` paths in the prompt instead.

Copyable first-use request after discovery (replace placeholders and authorize the report directory):

```text
Use $latex-bib-audit and $academic-prose-audit on the authorized manuscript
revision <hash>, main file <main.tex>, sections <scope>. Run bibliography
Layers 1 and 2 and contextual academic phrasing/register review for natural,
precise author voice; Layer 3 is off. Do not edit
the manuscript or Bib files. Write fresh standalone offline HTML reports
outside the source tree in <authorized-report-dir>; do not overwrite files.
Report uncertain identities and coverage gaps; propose corrections only.
```

## Coding-agent invocation

Fix the authoritative revision, scope and read-only boundary first. Example prompt: `Read /path/to/academic-skills/skills/latex-bib-audit/SKILL.md; on manuscript revision <hash>, audit bibliography metadata and citation identity, findings only.` For prose: `Read /path/to/academic-skills/skills/academic-prose-audit/SKILL.md; review sections <scope> on revision <hash> for contextual academic phrasing, findings only.` Supply access through the project's existing permissions. Layer 3 of the bibliography skill requires a separate explicit request and original-paper evidence. "AI flavor" is a stylistic impression, not AI detection, scoring or evasion; prose review does not scientifically validate claims.

For a local Codex session (or any file-reading agent), an example user request is:

```text
Read /path/to/academic-skills/skills/latex-bib-audit/SKILL.md and
/path/to/academic-skills/skills/academic-prose-audit/SKILL.md.
For the authorized manuscript revision <hash>, main file <main.tex>, and
sections <scope>, run bibliography Layers 1 and 2 and a contextual academic
phrasing/register audit for natural, precise author voice
on the same frozen revision. Layer 3 is disabled. Keep the manuscript and Bib
files unchanged; author separate, fresh citation-audit.html and prose-audit.html
in an authorized <report-directory> outside the source tree. Both must open
offline with inline CSS, no external assets/network, and HTML-escaped sources.
Report file:line/key, exact original and minimal suggestion/question side by
side, why the phrase is problematic here, evidence, severity, uncertainty and
coverage gaps. No auto-fix or AI-authorship inference.
```

The default reports are agent-authored standalone HTML, with a readable scope/revision summary, layer coverage where applicable, severity and unverified counts. Output names can be adapted; never overwrite a report. Markdown is optional on user request. Escape all manuscript-derived HTML; no frontend framework or JavaScript is needed.

The plain Python optional triage tools are `python3 skills/latex-bib-audit/compare_candidates.py --help` and `python3 skills/academic-prose-audit/scripts/prose_candidates.py --help`. The former compares two existing same-key BibTeX files and requires separately installed `pybtex`; its real-parser integration tests are skipped when that library is absent, so actual parser behavior remains unverified here. Use `python3 skills/latex-bib-audit/compare_candidates.py original.bib candidate.bib --output /fresh/report-directory/comparison.json` to create a **new** report exclusively after a successful comparison. The latter is stdlib-only and prints non-exhaustive questions for explicitly named TeX files. Neither tool discovers the project or performs a complete audit. Both can print source-derived content: keep reports, stdout and stderr local/private. Never redirect stdout into a source or existing report: shell redirection can truncate a file before the script runs. The agent, not these scripts, must locate sources and judge evidence.

For other coding agents, use their own documented installation or project-local skill location and confirm discovery. Do not change global agent configuration as part of using this repo. Apply the manuscript project's locality, privacy, collaborator and editing rules.

## Manual publication

Edit and validate canonical files here first, then commit. When manually deploying a copy, record this repo's commit and SHA-256 of skill files, compare hashes after copying, and document any local adapter-only divergence. Do not treat deployment copies as a second authority, set up autosync, or depend on cross-host symlinks. Local project-specific constraints remain in that project's instructions; preserve them when republishing a portable skill.

No private run inputs or receipts belong in this source repository. Validation of these instruction files does not imply that a manuscript was audited.
