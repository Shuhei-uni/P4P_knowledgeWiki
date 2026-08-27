> **Legacy source:** ResearchProject_wiki/wiki/progress/blockers.md  
> **Migration note:** These excerpts preserve the historical blocker record; no blocker status or interpretation has been rewritten. Raw and machine-generated artifacts remain at their legacy paths.

# Historical blocker notes

> **Legacy source:** ResearchProject_wiki/wiki/progress/blockers.md
> **Migration note:** Selected historical limitations are preserved without changing their status or interpretation.

### BLK-011 | Frozen 02c parent is not visible from the currently idle Fluent endpoint
- Status: Active — case-only build blocked
- First observed: 2026-08-16
- Related run(s): `02c-I20-I160-PREPARATION-2026-08-16`
- Symptom: the active 02c I20–I160 builder correctly refused to proceed because the required frozen `02c-B` pre-initialization parent path was not visible to the accessible idle Fluent session.
- Current interpretation: this is a remote-file/session-availability constraint, not evidence that the documented parent, H artifacts, or the intended I settings are invalid. The build was stopped before any case mutation, initialization, iteration, data write, or journal submission.
- Recovery action: reconnect to an idle Fluent session with access to the documented frozen parent; verify the parent boundary/model contract; then build and reload-verify every independent I child before submitting the separate native journal.
- Scope note (2026-08-16): a Student-only I20/I40/I60 50-iteration surrogate smoke completed successfully at the execution-integrity level. It does not clear this blocker because its saved source, mesh, and DPM state are not the verified server-2 frozen-parent lineage.
