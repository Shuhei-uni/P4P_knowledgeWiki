---
name: fluent-live-inspection
description: Inspect live Fluent paths, named objects, allowed values, or uncertain case state through the P4P-preserving PyFluent MCP interface before implementation or analysis.
---

# Fluent live inspection

Use [MCP integration](mcp-integration.md) for the shared tool route, session
policy, errors and retained-worker exceptions. Inspect current state; this skill
does not load another case, activate a model, change a working directory or solve.

## Workflow

1. Resolve the fleet endpoint and ownership. Check `session_status`; attach with
   argument-free `connect` only when needed. Endpoint identity is not case identity.
2. Reconcile the loaded case/data with exact experiment records and independent
   evidence. Report unavailable identity rather than guessing from an alias.
3. Use `find_api`/`get_help` for candidate paths. Use `describe_path` and
   `get_state` for the smallest relevant live scope. Use focused probes,
   `get_targeted_context` and named-object/template tools when needed.
4. Preserve unknown, inactive, empty, failed and truncated results. Narrow a
   missing/truncated read; do not turn it into absence or a passing invariant.
5. Return observed paths, values, scope, version/endpoint, identity confidence
   and unresolved uncertainty to the caller.

For mesh diagnostics use `mesh_quality`; for field names use `list_fields`.
Setup digests and screenshots supplement the evidence contract, not replace it.
A discovered field does not supply its history or establish its phase meaning.

## Mutation handoff

Return required dependency changes to `fluent-case-build-and-run` or the caller's
approved implementation workflow. It uses `validate_code` then `run_code`,
reacquires affected objects, and repeats critical inspection. It also owns
save/reopen, invariants and smoke/instrumentation proof. Inspection itself is
not permission to mutate.

Escalate physical meaning, prerequisites, or unresolved implementation mechanics
to `fluent-manual-researcher`. A schema search cannot answer those questions.

## Recovery

After a lost response, reconcile current state and run records before retrying.
MCP unavailability blocks this generic route; it does not authorize a custom
crawler, `dir()` probe, parent activation or direct-PyFluent fallback.

`inspect_fluent_session.py` and `explore_settings_space.py` are MCP CLI clients.
`compare_case_setup.py` compares captured MCP snapshots offline; it does not load
cases into a live workspace. Existing domain code supplies domain logic only
under the shared retained-worker exception, never case-specific assumptions.
