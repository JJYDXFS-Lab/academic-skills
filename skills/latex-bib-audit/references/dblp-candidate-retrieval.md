# DBLP candidate retrieval

This abstracts ideas from an owner-provided bibliography notebook reviewed on 2026-10-19. Its code and inputs were neither executed nor copied. This guidance is **not** a downloader, permission to bypass access controls, or proof of metadata correctness.

The source notebook parsed BibTeX, normalized titles, searched a bounded set of DBLP hits, selected by venue/year preference, fetched BibTeX, replaced keys with regex and appended output. It could silently omit incomplete inputs, insert title-only placeholders after failed retrieval and attempted automated challenge solving. These are not verified entries or acceptable automatic replacement behavior.

For a separately authorized candidate helper:

- Parse and retain every original entry/key; reconcile input/output counts and report missing titles/keys.
- Keep DBLP record IDs separate from manuscript keys. Compare DOI/arXiv, authors and intended publication version; normalized title or top hits alone cannot resolve identity.
- Mark failures and ambiguous results `unverified` with actual error; never substitute synthetic placeholders for richer input entries.
- Write separate candidate and field-difference ledgers with deterministic collision/rerun behavior. Parse returned BibTeX and change candidate keys structurally, not with regex.
- Preserve case protection, macros, inherited/custom fields and legitimate versions. Require explicit approval before manuscript changes.
- Reject HTML as BibTeX, bound requests/retries/output and honor numeric or HTTP-date Retry-After.
- Never automate challenge solving or synthetic challenge timing. Record blocked access and seek another authoritative source or an owner-provided export.
- Treat DBLP as corroboration; resolve conflicts using publisher, proceedings or appropriate arXiv records.

Candidate ledger: `input key | original entry | DBLP ID/source | identity/version | matching evidence | field differences | retrieval/ambiguity status`.

This only informs Layer 1; it establishes neither Layer 2 mapping nor Layer 3 support. A future helper needs focused tests for incomplete entries, ambiguous versions, HTML/errors, lookup failures and repeated runs.
