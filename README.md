# Academic Skills

Independent Method Lab source for reusable academic-review instructions for coding agents. Read [docs/README.md](docs/README.md) before use.

**Install for Codex:** after obtaining access to this repository, copy the two complete folders in `skills/` from a clean clone to `$HOME/.agents/skills/` (personal) or your manuscript repository's `.agents/skills/` (project-scoped). Keep each `SKILL.md` with its scripts and references. In Codex CLI, use `/skills` to confirm discovery and invoke `$latex-bib-audit` or `$academic-prose-audit`; if they do not appear, restart Codex. See [installation and first-use instructions](docs/README.md#install-and-use) for safe copy commands, private-repo access, prerequisites and the read-only example prompt.

Non-invasive by default: source manuscripts and bibliographies remain byte-for-byte unchanged. Findings and optional candidates belong only in a separate, explicitly selected output location; they are not accepted replacements or automatic edits. Corrections are a separate human-approved task.

- [LaTeX bibliography audit](skills/latex-bib-audit/SKILL.md): metadata and citation identity by default, claim support only by explicit opt-in.
- [Academic prose audit](skills/academic-prose-audit/SKILL.md): read-only contextual register and clarity findings.

The read-only Research Office catalog is a pointer, not an installer or authorization. This repository contains no manuscripts, notebooks, third-party skill packages, private inputs or run artifacts.
