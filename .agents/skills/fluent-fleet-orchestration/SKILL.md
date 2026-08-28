---
name: fluent-fleet-orchestration
description: "Discover the live Fluent server fleet, inventory exact case/data artifacts, plan verified transfers and server placement for approved simulation work, and preserve important restart states through OneDrive. Use whenever scientific work needs new Fluent compute, especially when multiple independent servers may be online or offline and parent cases are not available on every machine."
---

# Fluent Fleet Orchestration

Turn the currently available Fluent machines and case/data artifacts into a safe execution plan without making scientific setup identity depend on a server.

Servers are interchangeable compute only when the exact required scientific artifact can be proven available there. Server-local disks are working storage, not the only durable scientific archive.

## Keep four identities separate

Do not collapse these concepts:

- **artifact ID** — one exact scientific case/data state used as a parent, final result, or recovery point;
- **setup ID** — the server-neutral scientific experiment definition;
- **run ID** — one actual execution attempt of a setup;
- **server ID** — the machine used for that execution.

A setup must mean the same experiment regardless of whether it runs on Server 1, Server 2, or Server 3. Hostnames, ports, local paths, and server aliases are execution facts, not scientific identity.

## Start every new compute cycle with fleet preflight

Before selecting placement or launching new Fluent work, establish the live resource envelope.

For every configured server that can reasonably be checked, determine:

- whether it is reachable now;
- whether Fluent/PyFluent execution is available;
- whether it is idle, occupied, or in an uncertain state;
- the verified working/output roots from `PyAnsys/server-profiles/` when available;
- which exact paired `.cas.h5` / `.dat.h5` artifacts are locally accessible and useful to the current phase;
- which active or recovery runs already occupy that server;
- any material version or environment limitation that could prevent a scientifically equivalent run.

Do not infer scientific case identity from a directory name, server name, status file, or Fluent iteration count. Inspect explicit paths and, where practical, verify artifact identity from a manifest, hash, saved provenance, or direct case/data inspection.

Server availability is temporary state. Repeat fleet preflight whenever the scientific loop needs another round of compute, after a material server outage/recovery, or when existing placement assumptions may no longer be true.

## Build an artifact availability map

For each parent, final result, or important restart state relevant to the planned work, record where an exact verified copy currently exists:

```text
artifact: F11-final
local:
  server-1: absent
  server-2: verified
  server-3: absent
onedrive: verified | absent | unknown
```

Prefer paired case+data as the reusable scientific artifact. A data file without its matching case, or a case without the required data state, is not automatically a complete restart/branch parent.

When practical, identify artifacts by a small manifest containing:

```yaml
artifact_id: F11-final
source_setup: ...
source_run: ...
progress: ...
case_file: ...
data_file: ...
case_sha256: ...
data_sha256: ...
origin_server: ...
```

Hashes are strongly preferred for transferred important artifacts when the workflow can produce them cheaply. If hashes are unavailable, use the strongest available independent identity evidence and state the limitation.

## Give scientific design the real resource envelope

Fleet state can influence which scientifically justified experiments can be executed efficiently, especially discovery matrices and independent branches.

Return the live server count, locality constraints, and transfer possibilities to `scientific-phase-loop` / `design-experiment` before expensive runnable work is committed.

Use available parallel capacity aggressively when several worthwhile independent experiments already exist. Prefer concurrent high-information branches over serial execution on one machine when the parent artifacts can be staged safely.

Do not invent weak experiments merely to keep every server busy. Scientific value comes first; utilization is an optimisation within the set of justified work.

## Place runs by exact-parent locality

For every approved setup, resolve an execution placement using this default priority:

1. an available server already has the exact verified parent case/data locally;
2. an available server can receive the exact verified parent from OneDrive;
3. the parent can be published from another active server to OneDrive and then staged to the chosen server;
4. the only known copy is on an unavailable server — mark the run blocked unless another verified replica can be found.

Also consider whether a server is already occupied, whether several related runs would contend for the same local parent, and whether moving one verified parent once would unlock useful parallel execution.

Do not copy artifacts between machines merely because another server is idle. Transfer only when it unlocks justified work, improves resilience, or preserves an important state.

## Use OneDrive as the shared durability and transfer layer

Treat OneDrive as a verified shared cache/archive for important Fluent artifacts, not as scientific identity by itself.

The default durability posture is:

```text
server-local storage = working copy
OneDrive verified case+data = durable reusable copy
```

Strongly prefer promoting the following to OneDrive as complete paired case+data artifacts:

- every scientifically important final run state;
- every final parent likely to be branched from again;
- selected expensive recovery checkpoints whose loss would force substantial rerunning;
- important pre-change/reference states that would be difficult to reconstruct.

Do **not** synchronize every autosave or every routine checkpoint. Keep local high-frequency autosaves when useful for immediate recovery, then promote only deliberately selected recovery states and final states to avoid unnecessary transfer and storage overhead.

Whenever an important artifact is promoted:

1. save the matching full case and data pair;
2. give the pair one artifact ID;
3. record source setup/run and progress/iteration;
4. copy/upload both files to the approved OneDrive location;
5. preserve a small manifest with filenames and provenance;
6. verify the copied files, preferably with hashes for important artifacts;
7. only then describe the OneDrive copy as verified/durable.

Never assume synchronization completed merely because a file appeared in a local OneDrive folder. For crucial artifacts, verify that the intended files are present and complete through the available filesystem/sync evidence.

If OneDrive is temporarily unavailable, preserve the full local case/data pair and report the artifact as `LOCAL_ONLY` durability debt rather than pretending it is safely replicated.

## Produce an explicit execution plan

Before `implement-experiment`, make placement and staging concrete. A useful execution plan contains:

```yaml
setup_id: S4-05
run_id: S4-05-run-001
server: server-3
parent:
  artifact_id: F11-final
  source: onedrive
  case_hash: ...
  data_hash: ...
staging:
  transfer_required: true
  verify_before_load: true
remote:
  parent_case: ...
  parent_data: ...
  run_root: ...
durability:
  final_to_onedrive: true
  important_checkpoint_policy: selected-only
```

The exact remote paths belong to the execution plan, not the scientific setup definition.

`implement-experiment` should receive this placement contract and execute it faithfully. If staging cannot prove the required parent, do not substitute a similarly named local file; return the placement failure for re-planning.

## Use the fleet in waves when useful

For discovery matrices or several independent hypothesis branches, schedule in waves against the current live fleet.

Example with three active servers:

```text
wave 1: D1 | D2 | D3
analyse/update understanding
wave 2: only the next cases still justified by wave 1
```

Do not commit later waves blindly when earlier evidence could make them unnecessary.

If a server becomes unavailable, re-run preflight and re-place only work whose exact parent/recovery artifact can be proven elsewhere. Never assume that a checkpoint stranded on an offline server is available for migration.

## Preserve recovery portability

When an expensive run reaches a checkpoint worth protecting, prefer saving a complete paired case/data recovery state and promoting that selected checkpoint to OneDrive when practical.

This reduces dependence on any single server and allows a later execution plan to resume or derive a child on another machine after:

- a server shutdown;
- local disk loss;
- a machine becoming unavailable for an extended period;
- redistribution of work across the fleet.

Migration still requires verification that the target Fluent/PyFluent environment can load and continue the artifact scientifically equivalently. Shared storage solves locality, not compatibility.

## Handoff

Return a compact operational state rather than scientific interpretation:

```text
FLEET: active / busy / unavailable servers
ARTIFACTS: exact parent/final/recovery locations and verification status
PLACEMENT: setup -> run -> server
TRANSFERS: required source -> OneDrive -> destination actions
DURABILITY: verified OneDrive finals/checkpoints and any LOCAL_ONLY debt
BLOCKERS: unavailable parent, uncertain identity, missing paths, compatibility issues
```

The scientific orchestrator decides what experiments are worth doing. This skill makes the justified work runnable, parallel where sensible, and less dependent on any one physical server.