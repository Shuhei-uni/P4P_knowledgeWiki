---
name: fluent-live-inspection
description: Inspect live Fluent paths, named objects, allowed values, or uncertain case state through the P4P-preserving PyFluent MCP interface before implementation or analysis.
---

# Fluent live inspection

Use upstream discovery, not an improvised Settings-tree crawler. For installation,
client configuration, or a transport/version mismatch, read [MCP integration](mcp-integration.md).

## Workflow

1. Resolve fleet placement and ownership. Use the MCP process bound to that server
   alias; call `connect` without arguments, then capture `session_status` and
   `solver_status`. Endpoint identity is not case identity; unavailable or failed
   MCP status remains uncertainty, not `not running`.
2. Establish the loaded case/data from verified experiment records and independent
   live evidence. Missing identity remains unavailable.
3. Use `find_api` for candidate paths; its bundled schema is not proof of current
   activity. Use `describe_path` on the smallest relevant live branch, or
   `probe_path`, `get_active_status`, `get_allowed_values`, and named-object tools
   for a focused question. Preserve null/unknown separately from false/empty.
4. For changes, return to the implementation workflow. Validate generated Python
   through `validate_code`, execute through `run_code`, reacquire affected objects,
   and inspect critical values again. Parent/model/type changes invalidate earlier
   assumptions. A successful MCP call is execution evidence, not a passed gate.
5. Return the observed path, state, scope, endpoint, and unresolved uncertainty.
   `fluent-case-build-and-run` still owns readback, save/reopen, invariant,
   smoke/instrumentation, and completion proof.

For mesh quality use `mesh_quality`; for available fields use `list_fields`.
Generic reports and screenshots supplement, not replace, the selected evidence contract.

When uncertainty concerns physical meaning, prerequisites, or a verified mutation
strategy rather than tree structure, escalate to `fluent-manual-researcher`.
Keep its version-matched manual research and save/reopen-verified recipe requirement.
TUI/journal fallback remains an explicitly approved reviewed-worker exception.

## Failure and compatibility

After a lost response or partial mutation, reconcile live state and existing run
records before retrying. Never infer that a timeout stopped Fluent.

MCP unavailability blocks the generic route; it does not authorize a silent
fallback to `dir()`, recursive probing, or model activation during inspection.
`explore_settings_space.py` and `inspect_fluent_session.py` now use MCP.
`compare_case_setup.py` compares captured MCP snapshots offline and never reloads
an active workspace. Capture exact invariant paths to avoid truncated state.

Reviewed P4P domain workers remain available for scientific setup, extraction,
file movement, and supervised runs. Reuse their proven logic, not another case's
names, values, paths, or assumptions. The retired mapper is historical replay only.
