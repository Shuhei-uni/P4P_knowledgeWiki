# P4P Fluent MCP integration

This is the shared execution-route contract for skills that touch Fluent.
Read it before first use or when the route, permissions, or installed tools are
uncertain. Domain skills own their scientific procedure; this file owns how
that procedure reaches Fluent.

## Ownership and default route

Use the P4P-preserving `ansys/pyfluent-mcp` interface for generic Fluent
connection, API discovery, validation, execution, and inspection. P4P retains
scientific selection, phase gates, identity, paths, fleet ownership, artifact
movement, supervision, evidence reduction, and interpretation.

The default is **MCP first**, not an existing script first. Existing code can
supply a proven domain algorithm, but its API paths must be grounded against
the current MCP/live state. Do not copy another case's names, values or paths.
Do not build a parallel Settings-tree crawler, capability registry, or setup
compiler to recover functionality already exposed by upstream.

In calling lifecycle skills, "Python/PyFluent run" means a P4P worker using
this contract; it does not authorize agent-generated direct-PyFluent scripts.
Scientific gates and approved horizons are unchanged by the transport choice.

## Runtime and sessions

Use the repository runtime, Python 3.12+, and the pins in
`PyAnsys/requirements-mcp.txt`:

```bash
python -m pip install -r PyAnsys/requirements-minimal.txt
python PyAnsys/scripts/connection/fluent_mcp_server.py --server-id 1
```

The launcher starts MCP, not Fluent. Configure the MCP client with the absolute
runtime Python and launcher paths; bind each process to one existing fleet
alias. Existing `PyAnsys/.env` variables remain host-local secrets. Inspect the
registered tool schemas instead of copying argument shapes from old examples.

Call `session_status` first. If this process has not attached, call `connect`
without `connect_kwargs`. Reuse an established connection. A failed/previously
attached process requires reconciliation before another client is created.
A server alias or `configured:<alias>` endpoint is not loaded-artifact proof.

Use this repository's preserving adapter, not an unrestricted stock server:
`disconnect`, `manage_fluent`, and `compare_files` are excluded. Closing the
MCP transport must preserve Fluent. Reopening a saved pair means loading it
in an owned, still-running session, not restarting or launching Fluent.

Fleet orchestration owns **one writer per Fluent session**, including direct
workers and graphics changes. The backend lock covers only its own process;
it is not a fleet lease. Never open a competing writer to evade a busy call.

## Route by capability

| Need | Default route | P4P responsibility |
| --- | --- | --- |
| Connectivity/current solve status | `session_status`, `solver_status` | Fleet lease, run identity, completion proof |
| Candidate API paths/docs | `find_api`, `get_help` | Bundled schema is not live activation evidence |
| Live path/state/options | `describe_path`, `get_state`, focused `probe_path`, `get_active_status`, `get_allowed_values`, `get_targeted_context` | Exact scope, prerequisites, independent critical readback |
| Named objects/templates | `list_named_objects`, `find_named_object`, `select_named_objects`, `describe_named_object_template` | Verify phase/zone/object identity before use |
| Load/change/save/solve/export through Settings | `validate_code` then `run_code` | Approved intent, budgets, paths and postconditions |
| Mesh diagnostics / available fields | `mesh_quality` / `list_fields` | Missing metrics are not a pass; field names are not samples |
| Setup digest / inspection report | `summarize_setup`, `simulation_report` | Not substitutes for required histories or invariant audits |
| Native graphics | Ground scene/export paths, then validated `run_code`; `screenshot` for a suitable verified view | Checkpoint, camera, ranges, resolution and visual QA |
| Case comparison | Capture matching exact paths; compare MCP snapshots offline | Expected new values, identity and save/reopen proof remain separate |

Tool output is evidence, not acceptance. Check protocol errors, top-level error
status and per-path errors. Preserve missing/null, inactive/skipped values,
empty results and `<large_state_omitted>` as distinct observations. Narrow
queries when state is truncated. An unavailable probe or empty enumeration is
not proof that a model or object is absent.

## Generated execution

The code file is a PyFluent **snippet using the supplied `solver` binding**,
not a standalone program that imports PyFluent, connects, or starts a process.
Ground the smallest relevant path, validate, execute one logical change,
reacquire after dependency changes, and read back the critical state before
any dependent operation. `validate_code` is a precheck, not scientific proof.

The existing CLI uses the same MCP route:

```bash
python PyAnsys/scripts/inspection/inspect_fluent_session.py --server-id 1 --paths setup.models.viscous.model --output-json before.json
python PyAnsys/scripts/inspection/explore_settings_space.py --query "turbulence model"
python PyAnsys/scripts/orchestration/execute_fluent_code.py --server-id 1 --code-file selected-change.py --output-json execution.json
```

Use new output paths from canonical `run-paths.yaml`. The execution receipt
says `EXECUTED`, not experiment `COMPLETE`, verified setup, or phase `PASS`.
An empty receipt after interruption proves nothing. Keep any calculation and
required final save within a coherent worker lifetime; do not assume a new MCP
process retains another process's Python namespace.

For hypothesis work, put the MCP worker under `run_and_handoff.py` using
`supervise-fluent-run`. For discovery remain attached. Completion must parse
and verify actual progress, paired saves and required streams, not just test
that a receipt file exists. Preserve exact-thread wakeup on both terminal
states. Generic MCP status/report tools do not replace that supervisor.

## Narrow retained-worker exceptions

Keep useful existing P4P workers where upstream lacks the required semantics:
remote filesystem/OneDrive transfer, complete report/residual history export,
DPM transcript completion/parsing, EWF scoped reductions, field-data extraction,
and operational supervision. Local numerical analysis and plotting also remain
ordinary Python; forcing them through MCP adds no Fluent capability.

Before invoking a direct worker, name the missing MCP capability and the exact
existing worker that supplies it; record the reason in the existing run evidence.
Review its success, error, timeout and cleanup paths for session preservation,
exact scope and no unintended solve/state changes. A generic setup helper,
`safe_*` accessor, or retired mapper is not an exception merely because it exists.
Do not paste/import arbitrary repository modules into the MCP sandbox.

TUI/journal execution requires **explicit human approval for that run**, plus
version-matched manual research, recoverable-child testing, independent readback
and save/reopen proof. A researched recipe does not grant permission by itself.
MCP unavailability or sandbox rejection is not permission to bypass the route,
disable its checks, launch Fluent, or fall back to unrestricted Python/TUI.

## Failure, recovery and comparisons

After a lost response or an execution error, treat the operation as potentially
partially applied. Persist the block in the existing run/phase records; inspect
file-backed progress and live state when safely available. Status queries may
wait behind a long solve. A timeout does not prove the solve stopped, and a
new client does not clear unresolved execution. Reconcile before any replay.

For setup comparisons, capture the same critical paths before mutation and after
paired save/reopen, then use:

```bash
python PyAnsys/scripts/inspection/compare_case_setup.py --base-snapshot before.json --candidate-snapshot reopened.json --allow-change setup.models.viscous.model
```

`WITHIN_DECLARED_DIFF_SCOPE` is not invariant/value/identity qualification.
The comparator rejects incomplete captured state. The explorer no longer accepts
`--mesh`, `--fluent-exe`, `--seed-json` or adaptive activation; comparison no longer
loads live case paths. The legacy mapper is historical replay only, not recovery.

## Acceptance

Run offline tests with the pinned dependencies; installed-upstream contract tests
must not be skipped in a qualified deployment. Then prove an owned-session path:
exact parent, live discovery, approved delta, critical readback, paired save/reopen,
invariants, approximately 50 smoke iterations when appropriate, durable evidence
streams, full planned horizon, final save, verifier and exact-thread wakeup.
Verify MCP shutdown preserves Fluent, lost responses do not cause replay, and a
second endpoint has its own ownership and paths. Record results in existing run
evidence. Passing instruction tests is not live deployment qualification.
