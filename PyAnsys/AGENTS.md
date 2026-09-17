# PyAnsys contract

`PyAnsys/` owns execution support and machine evidence, not project scientific
conclusions (`Project/`) or reusable CFD literature (`CFD_wiki/`).

## Read only the needed route

Start with the selected setup/results and relevant skill. For generic live
Fluent interaction follow the [MCP integration contract](../.agents/skills/fluent-live-inspection/mcp-integration.md)
through `pyansys-workflow`. It owns the default tools, preserving adapter,
validation, error semantics and narrow retained-worker exceptions. Existing
code is implementation evidence, not the first-choice discovery interface.

Use the repository's own runtime executable when present; do not rely on shell
activation or another clone's absolute path. MCP requires the pinned Python 3.12+
environment. Keep credentials on the worker host. Do not preload the whole
knowledge tree or old campaign logs.

## Focused owners

- `fluent-fleet-orchestration`: current reachability, ownership, exact artifact
  locality, placement, remote directories and OneDrive transfers.
- `implement-experiment` / `fluent-case-build-and-run`: approved delta,
  dependency order, paired save/reopen, invariants, smoke and instrumentation.
- `supervise-fluent-run`: approved long-horizon execution, terminal verification
  and exact-thread wakeup. Discovery remains attached.
- `fluent-live-inspection` / `fluent-manual-researcher`: live structure versus
  version-matched semantics and independently proven configuration mechanics.
- Domain/history/figure skills: complete scoped extraction and scientific
  presentation, with local analysis over recorded evidence.

Read [run and autosave guidance](knowledge/fluent-settings/native_run_and_autosave.md)
when configuring execution, checkpoints or recovery. The same scientific phase
gates, authority envelope and approved horizons apply with MCP.

## Identity and paths

Keep artifact, setup, run and runtime server identities separate. An alias,
version or iteration count is not case identity. Establish the exact loaded
case/data using observed paths/provenance; report missing identity honestly.
Resolve `server.ref` from alias and endpoint, retaining separate ID/IP/profile
fields because collaborators can reuse short aliases.

The experiment's canonical `run-paths.yaml` owns actual placement, Fluent working
directory, parents/children/finals, checkpoints, histories, logs/manifests and
OneDrive destinations. Use temporary derived worker inputs only; reconcile actual
locations after smoke and final execution into that same path map. Loading a
case does not establish its working directory. Source parents and all `raw/`
directories remain immutable.

Important states need matching case/data pairs. Prefer verified OneDrive copies
for important finals, likely parents and selected expensive recovery states;
keep routine autosaves local. Verify replication, preferably by hashes, before
claiming durability. If unavailable, preserve the pair and record `LOCAL_ONLY`.
Computational completion and durability are different states.

## State and verification

For a dependency-sensitive change: enable/create the approved parent, reacquire,
inspect live active options, validate/run one logical change, read back critical
values and stop dependent steps on mismatch. Reacquire after case/mesh loads,
model/type changes, object creation or phase-count changes. Missing paths mean
inspect prerequisites/version, not force an old recipe.

A successful MCP call is execution evidence only. Readback, paired save/reopen,
setup invariants, planned smoke and required history streams still have to pass.
Do not turn missing evidence into zero, infer completion from a filename, or
replay an uncertain mutation/solve. Preserve the block and reconcile first.

Stabilize carrier state before DPM/EWF unless the setup explicitly requires a
different order. Create/read back default DPM injections before detailed edits;
reacquire after type changes and verify scope/fates. Enable EWF only with its
carrier/DPM prerequisites, and Energy only when thermal fields are part of the
question. Inspect current phase/domain/wall mappings before reusing a pattern.

A TUI/journal exception needs explicit human approval for the specific run and
the shared contract's research/verification. GUI execution and process restart
are not autonomous recovery. Every success/error/timeout/cleanup path must leave
Fluent running. Poor scientific behaviour alone does not shorten a fixed horizon.

## Implementation and handoff

Keep reusable code in `src/pyansys_fluent/`; MCP bootstrap in
`scripts/connection/`; inspection/extraction in `scripts/inspection/`; thin
approved orchestration in `scripts/setup/` and `scripts/orchestration/`;
non-secret filesystem knowledge in `server-profiles/`; reusable implementation
lessons in `knowledge/`. `output/` is generated evidence, not scientific truth.

For a retained direct worker, record its exact capability gap and reviewed path;
never use it as an automatic substitute for failed MCP validation. Preserve
native coordinates, units, signs, scope, raw evidence and completeness labels.

Before handoff verify identity, declared delta, readbacks, paired persistence,
canonical paths, instrumentation, observed progress, terminal proof, wake status
where required and artifact durability. Put evidence/interpretation in the
selected Project record, reusable methods in CFD_wiki, and generic implementation
lessons in PyAnsys/knowledge. Do not create a second project log or change
scientific conclusions during implementation maintenance.
