# Academic Skills

Independent Method Lab source for reusable academic-review instructions for coding agents. Read [docs/README.md](docs/README.md) before use.

**Install for Codex:** ask the bundled `$skill-installer` to install both `skills/latex-bib-audit` and `skills/academic-prose-audit` from `JJYDXFS-Lab/academic-skills` (repository access required). It installs into `$CODEX_HOME/skills` and refuses existing destinations; updating needs a staged comparison and backup, not a rerun. Restart Codex after installation or update. See [installation and first-use instructions](docs/README.md#install-and-use) for a copyable request, private-repo access, update/fallback guidance and a read-only audit prompt.

Non-invasive by default: source manuscripts and bibliographies remain byte-for-byte unchanged. Findings and optional candidates belong only in a separate, explicitly selected output location; they are not accepted replacements or automatic edits. Corrections are a separate human-approved task.

- [LaTeX bibliography audit](skills/latex-bib-audit/SKILL.md): metadata and citation identity by default, claim support only by explicit opt-in.
- [Academic prose audit](skills/academic-prose-audit/SKILL.md): read-only, context-first academic phrasing and register review for natural, precise author voice; flags generic claims, stock rhetoric and awkward phrasing with exact evidence and minimal meaning-preserving suggestions. Not AI-authorship detection or a score.

The read-only Research Office catalog is a pointer, not an installer or authorization. This repository contains no manuscripts, notebooks, third-party skill packages, private inputs or run artifacts.
