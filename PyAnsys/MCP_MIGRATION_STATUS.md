# PyFluent MCP migration — work in progress

Branch: `codex/pyfluent-mcp-migration`.
Base: `75eac6e3cf2e98424c84619057da0281e1708a2e`.
First migration commit: `7a3532c2ffc6ccafbc8fa6724d78a1d615ff332c`.

## Present on this branch

- Pinned upstream `ansys/pyfluent-mcp` dependency.
- An upstream-backed MCP server with P4P attach-only session policy.
- A small MCP wire client with explicit execution-uncertainty handling and no automatic replay.
- Existing endpoint aliases retained; automatic Fluent launch removed from the shared connection helper.

This is not yet a complete migration or a qualified deployment. Subsequent upload requests were blocked by the tool's safety-status check, so prepared verification, inspection routing, comparison, skill and test changes are not in this commit. Do not assume those changes are present merely because the branch has a migration name.

## Preserved

Project science, phase-state and run-path records, evidence, fleet orchestration, artifact provenance, OneDrive handling, long-run supervision, exact-thread wakeup, and domain-specific extraction workers were not replaced. A successful MCP call remains execution evidence only, not experiment acceptance.

## Outstanding before merge

Review and integrate the remaining migration changes, reconcile instruction and command references, run the complete repository test suite with the pinned upstream dependencies, and qualify one controlled live workflow through identity, readback, save/reopen, invariants, smoke, evidence streams and completion verification. Confirm MCP shutdown leaves Fluent running. No live Fluent sessions were used or changed during this migration.

The local prepared-file test run passed 52 tests and skipped the installed-upstream contract-test module because its dependencies were unavailable. This is not a test result for the complete repository or the current branch alone.
