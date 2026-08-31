---
name: fluent-fleet-orchestration
description: "Discover and control the live Fluent fleet for approved scientific work: inventory exact artifacts, take/reconcile active sessions under the phase authority envelope, plan verified transfers and placement, make output paths explicit, and preserve important restart states through OneDrive."
---

# Fluent Fleet Orchestration

Turn the currently available Fluent machines and exact case/data artifacts into a safe execution plan without making scientific setup identity depend on a server.

Servers are working compute resources. Verified scientific artifacts are the durable identities.

## Keep identities separate

Do not collapse:

- **artifact ID** — exact scientific case/data state;
- **setup ID** — server-neutral experiment definition;
- **run ID** — one execution attempt;
- **server reference** — exact runtime endpoint;
- **goal lease** — which autonomous phase currently owns active-session control.

Resolve runtime server identity using alias + live IP, for example:

```yaml
server:
  ref: 'server-2@192.168.1.42'
  id: 'server-2'
  ip: '192.168.1.42'
  profile_id: 'shuhei-server-2'
```

Use `server.ref` in placement/execution records.

## Read the phase authority envelope first

Before preflight, read the active phase contract and `phase-state.yaml`.

When the human has granted normal autonomous `/goal` authority, record an exclusive fleet lease such as:

```yaml
goal_lease:
  phase_id: phase-07
  mode: exclusive
  experiment_selection: full
  active_session_control: full
```

Under an **exclusive** lease, the scientific phase loop is explicitly authorized to control every configured Fluent working session during the goal. That includes:

- stopping an active calculation;
- terminating/replacing an abandoned or conflicting worker;
- saving a quick paired recovery state when the currently loaded endpoint is scientifically valuable and not already durable;
- closing/restarting/reconnecting Fluent;
- loading a different verified parent;
- reassigning a server to another approved experiment;
- overwriting disposable in-session setup state and run-local scratch outputs according to the new run plan.

Do not ask the human for confirmation for each of those actions while the exclusive lease is active.

The lease does **not** authorize deleting or overwriting verified durable Project/OneDrive parents/finals simply because they are inconvenient. Active session state is disposable; durable scientific artifacts are not.

If the phase handoff grants restricted rather than exclusive authority, obey those restrictions.

## Start every compute cycle with fleet preflight

For every configured server that can reasonably be checked determine:

- reachability;
- live endpoint/IP and `server.ref`;
- Fluent/PyFluent availability and version constraints;
- whether it is idle, iterating, blocked, or uncertain;
- which process/run appears to own current activity;
- verified working/output roots;
- exact useful paired `.cas.h5`/`.dat.h5` artifacts accessible locally;
- active/recovery runs present;
- important output/session state that would be lost by takeover.

Do not infer case identity from server name, directory name, iteration count, or a status string. Inspect exact paths/provenance and use manifests/hashes/readback where practical.

### Busy is not automatically blocked under an exclusive goal lease

If Fluent is iterating when an exclusive lease is active:

1. determine whether the calculation belongs to an approved active job in the same `phase-state.yaml`;
2. if yes, preserve/continue it according to that job's state;
3. if it is stale, abandoned, from an older goal, or conflicts with the new approved placement, reconcile useful state;
4. save a paired recovery artifact first when losing the current unpreserved endpoint would materially cost scientific work;
5. stop/terminate/reload/reassign the session;
6. record the takeover/recovery fact in the execution plan.

Do not let `iterating=true` by itself force `BLOCKED` when the phase has explicit takeover authority.

If session ownership cannot be identified, preserve the recoverable state where cheap, then take control under the exclusive lease.

## Build an artifact availability map

For relevant parents, finals, and important recovery points record where an exact verified copy exists:

```text
artifact: F11-final
local:
  server-1@192.168.1.31: absent
  server-2@192.168.1.42: verified
onedrive: verified | absent | unknown
```

Prefer paired case+data. A case without the required data or data without the matching case is not automatically a complete branch parent.

For important artifacts prefer a small manifest containing artifact ID, source setup/run, progress, filenames, origin `server.ref`, and SHA256 hashes when cheap to obtain.

## Give scientific design the real resource envelope

Return live server count, session state, takeover status, artifact locality, transfer possibilities, and material version limitations to `scientific-phase-loop` / `design-experiment` before runnable work is committed.

Use parallel capacity aggressively only for scientifically justified work.

When two or more servers are usable for new compute, preserve the scientific loop's bold-probe lane. Do not create filler experiments merely to maximize utilization.

## Place runs by exact-parent locality

Default placement priority:

1. usable server already has exact verified parent;
2. usable server can receive exact verified parent from OneDrive;
3. exact parent can be promoted from another active server to OneDrive, then staged;
4. only known copy is inaccessible and no verified replica exists — block the run.

A server occupied by disposable/stale activity is still potentially usable under an exclusive lease after reconciliation/takeover.

## Keep path authority with the experiment

Every runnable experiment packet keeps:

```text
experiment/
├── setup.md
├── run-paths.yaml
└── results.md
```

`run-paths.yaml` is the single durable authoritative path record. Populate it before implementation and reconcile the same file after smoke/main execution.

Record when applicable:

- goal lease / phase ID;
- `server.ref`, ID, IP, profile ID;
- takeover/recovery action performed;
- Fluent working directory;
- staging/run roots;
- parent case/data;
- prepared/smoke/final case/data;
- autosave/checkpoint locations;
- every required file-backed report/monitor destination;
- transcript/log/status/job manifests;
- deterministic verifier path/command when applicable;
- OneDrive durable artifact destinations/status.

Do not use bare filenames without a deliberately fixed containing directory.

## Resolve inherited relative paths

A loaded case may contain relative report/monitor/autosave/export paths. Before smoke and again before a long run when needed:

1. inspect important file-backed definitions;
2. identify relative/blank/inherited/ambiguous destinations;
3. resolve them to run-specific destinations;
4. rewrite only file paths where possible without changing scientific definitions;
5. deliberately establish/verify Fluent working directory when relative paths are unavoidable;
6. read back configured destinations;
7. reconcile actual destinations with canonical `run-paths.yaml`.

If an important output location cannot be resolved, return an execution blocker before expensive compute.

## OneDrive is the shared durability/transfer layer

Use server-local storage as working copy and verified OneDrive paired case+data as durable reusable copy.

Strongly prefer promotion for:

- scientifically important final states;
- likely future parents;
- selected expensive recovery checkpoints;
- important pre-change states that would be difficult to recreate.

Do not synchronize every autosave.

For promotion:

1. save matching case+data;
2. assign one artifact ID;
3. record source setup/run/progress/origin server;
4. copy both files;
5. preserve a small manifest;
6. verify copy integrity, preferably hashes;
7. update `run-paths.yaml`;
8. only then call it durable.

If OneDrive is unavailable, keep the local pair and mark `LOCAL_ONLY` durability debt.

## Produce an explicit execution plan

Before `implement-experiment`, return a concrete placement/path/session-control contract.

Example compact handoff:

```text
FLEET LEASE: phase-07 / exclusive
FLEET: reachable / running / taken-over / unavailable server refs
RECOVERY: any pre-takeover paired saves and why
ARTIFACTS: exact parent/final/recovery verification status
PLACEMENT: setup -> run -> server.ref
PATH MAP: canonical Project/.../run-paths.yaml
TRANSFERS: source -> OneDrive -> destination
DURABILITY: verified finals/checkpoints and LOCAL_ONLY debt
BLOCKERS: unavailable parent, uncertain identity, path/compatibility issue
```

The scientific loop chooses what is worth running. This skill ensures the whole live fleet can actually be controlled and used according to the granted phase authority without losing valuable scientific state or confusing session identity with artifact identity.
