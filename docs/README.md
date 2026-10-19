# Academic Skills documentation

This is the canonical, harness-agnostic source for two ordinary AgentSkills in `skills/`: YAML `name`/`description` frontmatter and an instruction body, with linked relative resources. Reading a skill does not grant manuscript access, network or Python execution permission, editing authority or automatic discovery. If tools are unavailable, report the coverage gap rather than treating unchecked items as passed. Parallelism is optional: sequential review of the same frozen revision and scope is equally valid.

## Coding-agent invocation

Fix the authoritative revision, scope and read-only boundary first. Example prompt: `Read /path/to/academic-skills/skills/latex-bib-audit/SKILL.md; on manuscript revision <hash>, audit bibliography metadata and citation identity, findings only.` For prose: `Read /path/to/academic-skills/skills/academic-prose-audit/SKILL.md; review sections <scope> on revision <hash>, findings only.` Supply access through the project's existing permissions. Layer 3 of the bibliography skill requires a separate explicit request and original-paper evidence. Prose review is not AI detection or scientific validation.

For a local Codex session (or any file-reading agent), an example user request is:

```text
Read /path/to/academic-skills/skills/latex-bib-audit/SKILL.md and
/path/to/academic-skills/skills/academic-prose-audit/SKILL.md.
For the authorized manuscript revision <hash>, main file <main.tex>, and
sections <scope>, run bibliography Layers 1 and 2 and a contextual prose audit
on the same frozen revision. Layer 3 is disabled. Keep the manuscript and Bib
files unchanged; put findings in a separate new <report-directory> outside
the source tree. Report file:line/key, original/proposed text or field,
source evidence, reasoning, uncertainty and coverage gaps. No auto-fix.
```

The plain Python optional triage tools are `python3 skills/latex-bib-audit/compare_candidates.py --help` and `python3 skills/academic-prose-audit/scripts/prose_candidates.py --help`. The former compares two existing same-key BibTeX files and requires separately installed `pybtex`; its real-parser integration tests are skipped when that library is absent, so actual parser behavior remains unverified here. Use `python3 skills/latex-bib-audit/compare_candidates.py original.bib candidate.bib --output /fresh/report-directory/comparison.json` to create a **new** report exclusively after a successful comparison. The latter is stdlib-only and prints non-exhaustive questions for explicitly named TeX files. Neither tool discovers the project or performs a complete audit. Both can print source-derived content: keep reports, stdout and stderr local/private. Never redirect stdout into a source or existing report: shell redirection can truncate a file before the script runs. The agent, not these scripts, must locate sources and judge evidence.

For coding agents with project-local skills, manually copy or link each full skill directory into that agent's documented project-local skill location. Confirm discovery under the agent's own instructions. Do not change global agent configuration as part of using this repo. Apply the manuscript project's locality, privacy, collaborator and editing rules.

## Manual publication

Edit and validate canonical files here first, then commit. When manually deploying a copy, record this repo's commit and SHA-256 of skill files, compare hashes after copying, and document any local adapter-only divergence. Do not treat deployment copies as a second authority, set up autosync, or depend on cross-host symlinks. Local project-specific constraints remain in that project's instructions; preserve them when republishing a portable skill.

No private run inputs or receipts belong in this source repository. Validation of these instruction files does not imply that a manuscript was audited.
