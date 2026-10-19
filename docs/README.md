# Academic Skills documentation

This is the canonical portable source for the two ordinary AgentSkills in `skills/`: a YAML `name` and `description` frontmatter and an instruction body, with optional linked `references/`. Reading a skill does not grant manuscript access, network access, permission to edit or configured skill discovery.

## Coding-agent invocation

Fix the authoritative revision, scope and read-only boundary first. Example prompt: `Read /path/to/academic-skills/skills/latex-bib-audit/SKILL.md; on manuscript revision <hash>, audit bibliography metadata and citation identity, findings only.` For prose: `Read /path/to/academic-skills/skills/academic-prose-audit/SKILL.md; review sections <scope> on revision <hash>, findings only.` Supply access through the project's existing permissions. Layer 3 of the bibliography skill requires a separate explicit request and original-paper evidence. Prose review is not AI detection or scientific validation.

For coding agents with project-local skills, manually copy or link each full skill directory into that agent's documented project-local skill location. Confirm discovery under the agent's own instructions. Do not change global agent configuration as part of using this repo. Apply the manuscript project's locality, privacy, collaborator and editing rules.

## Manual publication

Edit and validate canonical files here first, then commit. When manually deploying a copy, record this repo's commit and SHA-256 of skill files, compare hashes after copying, and document any local adapter-only divergence. Do not treat deployment copies as a second authority, set up autosync, or depend on cross-host symlinks. Local project-specific constraints remain in that project's instructions; preserve them when republishing a portable skill.

No private run inputs or receipts belong in this source repository. Validation of these instruction files does not imply that a manuscript was audited.
