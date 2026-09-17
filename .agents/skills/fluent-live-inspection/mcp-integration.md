# P4P Fluent MCP integration

## Ownership

`ansys/pyfluent-mcp` owns generic API discovery, validation, execution and inspection.
P4P owns scientific decisions, phase gates, durable state, recovery, fleet leases,
artifact identity/movement, run paths, verification, supervision and interpretation.
The host adapter contains session-preservation policy, not a second discovery engine.

`Project/`, `CFD_wiki/`, phase-state files, run-path records, case/data evidence and
existing long-run/self-wake machinery are retained. Reviewed domain workers still
use direct PyFluent where their transcript, field-data, filesystem, or supervision
contracts require it. They are not a fallback for agent-generated discovery/code.

## Runtime

Use Python 3.12 or later in the P4P runtime:

```bash
python -m pip install -r PyAnsys/requirements-minimal.txt
python PyAnsys/scripts/connection/fluent_mcp_server.py --server-id 1
```

The second command starts a STDIO MCP server, not Fluent. Configure an MCP client
with the absolute runtime Python path as `command`, the absolute server script
path and `--server-id 1` as `args`. Register separate server entries for the other
active fleet aliases. Use the same script from Windows; no shell activation or
Unix-only executable path is required. The Python client starts it automatically.

Existing `PyAnsys/.env` endpoint variables are retained, including numeric aliases
and `student`. Credentials stay on the worker/MCP host. The alias is bound at server
startup; the agent calls `connect` with no `connect_kwargs`. No default launch,
endpoint switching, process shutdown, or ephemeral compare sessions are exposed.
P4P's fleet owner must enforce one writer across MCP and direct workers; a lock
inside one MCP process does not coordinate separate machines.

The source revision and main runtime dependencies are pinned in
`PyAnsys/requirements-mcp.txt`. Review upgrades against both offline contract tests
and the live acceptance below. Do not substitute an older PyPI release for the pin:
the required domain tools and lifecycle behaviours were checked against that source.

## Inspection and execution

```bash
python PyAnsys/scripts/inspection/inspect_fluent_session.py --server-id 1 --paths setup.models.viscous.model --output-json before.json
python PyAnsys/scripts/inspection/explore_settings_space.py --query "turbulence model"
python PyAnsys/scripts/orchestration/execute_fluent_code.py --server-id 1 --code-file selected-change.py --output-json execution.json
```

Use new evidence paths from the experiment's canonical `run-paths.yaml`; the
examples are filenames, not permission to choose an unrelated output directory.
The code file contains a PyFluent snippet using the upstream `solver` binding,
not a standalone script that imports PyFluent or connects itself. Validation is
performed upstream. The execution receipt says `EXECUTED`, never `COMPLETE` or
scientifically verified. An empty receipt after abrupt process termination is not
completion evidence. Required-files checks alone must not qualify the experiment.

For a hypothesis, run the MCP execution command under the existing
`run_and_handoff.py` / `supervise-fluent-run` contract, with the same deterministic
final-save/evidence verifier and exact-thread self-wake. Discovery remains attached.
No short tool timeout is imposed by default. A timeout or returned execution error
can follow partial mutation: persist the existing BLOCK state, inspect, and reconcile
before any new execution. A new MCP process does not clear scientific uncertainty.

## Comparison and retired routes

Capture matching exact paths before the change and after save/reopen, then use:

```bash
python PyAnsys/scripts/inspection/compare_case_setup.py --base-snapshot before.json --candidate-snapshot reopened.json --allow-change setup.models.viscous.model
```

The comparison blocks missing, inactive, skipped, or truncated state. Its successful
status means only that captured differences are inside the declared scope; expected
new values and case/data identity still require verification. Select narrower paths
when upstream returns `<large_state_omitted>`.

The explorer no longer supports `--mesh`, `--fluent-exe`, `--seed-json`, or adaptive
parent activation. The comparison no longer accepts live case paths. Legacy tree
mapping is preserved verbatim under `PyAnsys/legacy/` for reviewed historical replay
only, behind `P4P_ALLOW_LEGACY_TREE_MAPPER=1`; never use that switch as recovery from
MCP failure. Existing domain extractors' small `safe_*` accessors are compatibility
helpers, not an agent-facing discovery service.

## Acceptance

Offline: run `python -m pytest PyAnsys/tests -q`. The real-upstream contract tests
need the pinned dependencies; they must not be skipped in the installed runtime.
They exercise registration/STDIO, offline validation, and mocked attach/cleanup.
They do not qualify Fluent physics, live APIs, or save/reopen persistence.

Live deployment remains unqualified until an owned session proves: exact parent
identity; required live discovery; one approved delta; critical readback; paired
save/reopen; invariant checks; roughly 50 smoke iterations where appropriate;
required evidence streams; planned-horizon completion and final save; supervisor
verification and exact-thread wake; transport shutdown with Fluent still running.
Also test lost-response reconciliation without replay and a second fleet endpoint.
Record these outcomes in the existing experiment/run evidence, not another registry.
