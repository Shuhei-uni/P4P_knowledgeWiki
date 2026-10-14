# PyFluent MCP migration — prepared changes published

Branch: `codex/pyfluent-mcp-migration`.
Base: `75eac6e3cf2e98424c84619057da0281e1708a2e`.
Interface commit: `7a3532c2ffc6ccafbc8fa6724d78a1d615ff332c`.

## Publication scope

All 22 repository-relative files from `p4p-pyfluent-mcp-prepared-changes.zip`
are included on this branch. The 15 previously unuploaded files are now present
alongside the original seven interface files. This supersedes the earlier note
that verification, inspection routing, comparison, skill and test changes existed
only in the handoff archive.

The original mapper is also preserved unchanged at
`PyAnsys/legacy/settings_tree_mapper.py`, using Git blob
`45bcac7cadbb03848af62a651201264e4919b356` from the base commit.
Its compatibility entry point requires explicit historical-replay opt-in;
ordinary discovery uses upstream MCP instead.

## Included changes

- Pinned upstream dependency, preserving MCP server/client, and attach-only
  endpoint resolution shared with reviewed domain workers.
- Fail-stop dependency verification, typed readbacks, and explicit uncertainty.
- MCP inspection commands, offline setup-snapshot comparison, and a generated
  snippet execution command for the existing supervisor.
- Updated live-inspection skill and integration guidance.
- Four migration test modules and a Linux/Windows GitHub Actions workflow.

Project science, phase-state and run-path records, raw evidence, fleet
orchestration, artifact provenance, OneDrive handling, long-run supervision,
exact-thread wakeup, and domain-specific extraction workers remain retained.
A successful MCP call remains execution evidence, not experiment acceptance.

## Validation and remaining qualification

The prepared migration suite was rerun on 17 September 2026:
`52 passed, 1 skipped`. The skipped module requires the installed upstream MCP
dependencies, which were unavailable in this execution environment. Python
compilation of the authored modules and scripts passed. These results do not
represent the full repository suite or a live Fluent deployment.

Publication is complete for the prepared package; the overall migration remains
work in progress. Before merge, finish full-repository command/instruction
compatibility review, run the complete suite with the pinned dependencies and
without skipping upstream contract tests, and qualify a controlled live workflow
through identity, readback, paired save/reopen, invariants, smoke, evidence
streams, long-run completion and exact-thread wakeup. Confirm MCP shutdown leaves
Fluent running and lost responses are reconciled rather than replayed.

No live Fluent sessions were used or changed. This branch has not been merged
into `main`; publication alone is not deployment qualification.
