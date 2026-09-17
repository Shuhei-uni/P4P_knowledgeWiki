# PyFluent MCP migration — interface and skill routing

Branch: `codex/pyfluent-mcp-migration`.
Original migration base: `75eac6e3cf2e98424c84619057da0281e1708a2e`.
Prepared-package publication: `4e6b51639a26fe1813c8b09b243ed5389b5ff945`.

## Published interface

The 22 repository-relative files from the prepared migration package are retained:
pinned upstream dependency, preserving MCP server/client, attach-only resolution,
fail-stop dependency verification, inspection and execution entry points, offline
snapshot comparison, tests and Linux/Windows CI configuration. The original mapper
is preserved unchanged at `PyAnsys/legacy/settings_tree_mapper.py`, blob
`45bcac7cadbb03848af62a651201264e4919b356`; it is not ordinary discovery.

## Skill sweep — 17 September 2026

All 41 skill entries were classified, including three already-retired workflows.
Thirteen active operational skills now route generic Fluent work through MCP:
`pyansys-workflow`, `fluent-live-inspection`, `fluent-manual-researcher`,
`fluent-case-build-and-run`, `implement-experiment`, `fluent-fleet-orchestration`,
`supervise-fluent-run`, `fluent-report-histories`, `residual-history-analysis`,
`dpm-analysis`, `ewf-analysis`, `pool-patch-volume`, and `create-figure`.

The existing `fluent-live-inspection/mcp-integration.md` is the shared route
contract. Root and PyAnsys instructions, recovery/run guidance and three related
UI prompts are aligned with it. No new orchestration skill or capability registry
was added. Scientific/research/reporting skills and invocation classes remain;
retired skills remain disabled and historical code is not deleted.

MCP owns generic discovery, validated generated execution and inspection. P4P
retains scientific phase gates, exact artifact and run-path identity, fleet
ownership, OneDrive, paired save/reopen, smoke/stream proof, complete domain/history
parsing, native figure quality and long-run verification/exact-thread wakeup.
Existing direct workers require a named capability gap and reviewed execution
scope; they are not automatic fallbacks for MCP failure. TUI/journal exceptions
retain explicit run approval. A successful MCP call is not scientific acceptance.

This sweep changes instructions and adds offline instruction-contract tests. It
does not replace retained domain algorithms, change project conclusions or start
a simulation. The new autoresearch sandbox discussed separately is not created
or configured by this sweep.

## Validation and remaining qualification

The scoped local suite on 17 September 2026 returned `86 passed, 1 skipped`:
the four existing migration test modules plus the new skill-routing contract
module. The skip is the installed-upstream contract module because upstream MCP
dependencies were unavailable locally. Python compilation of the available
migration code/scripts/tests passed. This is not the complete repository suite,
a GitHub Actions success report or live Fluent validation.

Before deployment, run the complete repository suite with pinned dependencies
and no skipped upstream contract module. Qualify one owned live workflow through
identity, discovery, approved delta, critical readback, paired save/reopen,
invariants, smoke, required histories, full horizon, final save, terminal verifier
and exact-thread wakeup. Confirm shutdown preserves Fluent, lost responses do not
cause replay and another endpoint has independent ownership/path handling.

No live Fluent sessions or Project/CFD_wiki evidence were changed. The branch is
not merged into `main`; instruction consistency is not deployment qualification.
