---
name: fluent-fleet-orchestration
description: "Discover the live Fluent server fleet, inventory exact case/data artifacts, plan verified transfers and server placement for approved simulation work, make every run output location explicit, and preserve important restart states through OneDrive. Use whenever scientific work needs new Fluent compute, especially when multiple independent servers may be online or offline and parent cases are not available on every machine."
---

# Fluent Fleet Orchestration

Turn the currently available Fluent machines and case/data artifacts into a safe execution plan without making scientific setup identity depend on a server.

Servers are interchangeable compute only when the exact required scientific artifact can be proven available there. Server-local disks are working storage, not the only durable scientific archive.

## Keep scientific and execution identities separate

Do not collapse these concepts:

- **artifact ID** — one exact scientific case/data state used as a parent, final result, or recovery point;
- **setup ID** — the server-neutral scientific experiment definition;
- **run ID** — one actual execution attempt of a setup;
- **server reference** — the exact machine endpoint used for that run.

A short `server-1` or `server-2` alias is not globally unique when collaborators may use the same local numbering. During fleet preflight, resolve the actual IP used for the connection and form the runtime server reference from both values:

```yaml
server:
  ref: 'server-2@192.168.1.42'
  id: 'server-2'
  ip: '192.168.1.42'
  profile_id: 'shuhei-server-2'
```

Use `server.ref` as the canonical server identity in placement and execution records. Keep `server.id` and `server.ip` separately as well so tooling does not need to parse the combined string.

The scientific setup must mean the same experiment regardless of the server reference used to execute it. IPs, hostnames, ports, local paths, and server aliases are execution facts, not scientific identity.

Static files under `PyAnsys/server-profiles/` may use a collision-resistant profile namespace such as `shuhei-server-2` or `partner-server-2`; they do not need to hard-code the IP. Resolve the live endpoint during preflight.

## Start every new compute cycle with fleet preflight

Before selecting placement or launching new Fluent work, establish the live resource envelope.

For every configured server that can reasonably be checked, determine:

- whether it is reachable now;
- the actual endpoint/IP being used and resulting `server.ref`;
- whether Fluent/PyFluent execution is available;
- whether it is idle, occupied, or in an uncertain state;
- the verified working/output roots from `PyAnsys/server-profiles/` when available;
- which exact paired `.cas.h5` / `.dat.h5` artifacts are locally accessible and useful to the current phase;
- which active or recovery runs already occupy that server;
- any material version or environment limitation that could prevent a scientifically equivalent run.

Do not infer scientific case identity from a directory name, server reference, status file, or Fluent iteration count. Inspect explicit paths and, where practical, verify artifact identity from a manifest, hash, saved provenance, or direct case/data inspection.

Server availability is temporary state. Repeat fleet preflight whenever the scientific loop needs another round of compute, after a material server outage/recovery, or when existing placement assumptions may no longer be true.

## Build an artifact availability map

For each parent, final result, or important restart state relevant to the planned work, record where an exact verified copy currently exists. Use full runtime server references when there is any chance of alias collision.

```text
artifact: F11-final
local:
  server-1@192.168.1.31: absent
  server-2@192.168.1.42: verified
  server-1@192.168.1.55: absent
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
origin_server_ref: 'server-2@192.168.1.42'
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

## Keep the run path record with the experiment

Every experiment packet should keep its scientific contract, execution-location record, and results together:

```text
experiment/
├── setup.md
├── run-paths.yaml
└── results.md
```

`run-paths.yaml` is the **single durable authoritative path record** for that experiment. It belongs in the same canonical `Project/` experiment directory as `setup.md` and `results.md`, not in `PyAnsys/output/`, a server-local run directory, or a separate documentation tree.

The file may contain absolute paths on remote Fluent servers and OneDrive. Its location in `Project/` does not imply that the large artifacts themselves belong in Git.

Create/populate `run-paths.yaml` once placement is known, before implementation begins. Update the same file when smoke testing or the long run reveals actual paths, transfers, or durability status. Do not create multiple competing long-lived path manifests.

If a remote Python runner needs a machine-local copy of the path configuration, that copy is transient/derived. The canonical `Project/.../run-paths.yaml` remains the source of truth and must be reconciled with the actual run afterward.

## Make every filesystem destination explicit

Do not let Fluent, Python, or a previously launched session decide where outputs happen to land.

Before `implement-experiment` starts mutating or solving, `run-paths.yaml` must resolve every important write location. Prefer absolute paths. At minimum state, when applicable:

- runtime `server.ref`, `server.id`, and `server.ip`;
- the observed or deliberately set Fluent working directory;
- staging/temporary root;
- run root;
- verified parent case and data paths;
- built child/setup case path;
- smoke-test case/data paths when they are saved;
- final case path;
- final data path;
- autosave/checkpoint directory and filename pattern;
- every file-backed report/monitor destination, including Fluent `.out` files;
- transcript path;
- Python runner log/status path;
- journal path only when a human-approved journal is used;
- artifact manifest path;
- the OneDrive destination for durable final/recovery artifacts.

Do not use a bare filename such as `mass-flow.out`, `final.dat.h5`, or `checkpoint.cas.h5` without also resolving and recording the directory in which Fluent will create it.

The active Fluent session may have been launched from an unrelated directory. Treat the inherited session working directory as unsafe for scientific outputs unless it has been deliberately inspected and accepted for this run. Loading a case from a directory also does not prove that later relative outputs will be written beside that case.

### Inspect relative paths embedded in the loaded case

A loaded Fluent case may already contain report files, monitor files, autosave definitions, exports, or other file-backed objects with relative destinations. Before the smoke test and again before the long run when needed:

1. inspect the active file-backed output definitions;
2. identify any relative, blank, inherited, or ambiguous destination;
3. resolve it to the intended run path;
4. where Fluent/PyFluent supports it, rewrite only the output destination to an explicit run-specific path;
5. where the interface requires a relative filename, deliberately establish and verify the working directory and record the resulting absolute destination;
6. read back the configured destination when possible.

Changing only a report/monitor **file destination** is an implementation detail and should not change its scientific definition, scope, quantity, or sampling behaviour.

If the location of an important generated file cannot be resolved before launch, treat that as missing execution information rather than hoping the file can be found later.

### Canonical `run-paths.yaml`

Prefer YAML because this record is both machine-read and routinely inspected by humans. Keep the schema simple and deterministic. Quote Windows paths when that avoids YAML ambiguity.

A useful record is:

```yaml
setup_id: S4-05
run_id: S4-05-run-001
server:
  ref: 'server-2@192.168.1.42'
  id: 'server-2'
  ip: '192.168.1.42'
  profile_id: 'shuhei-server-2'

paths:
  fluent_working_dir: 'C:\P4P\runs\S4-05-run-001'
  run_root: 'C:\P4P\runs\S4-05-run-001'
  parent_case: 'C:\P4P\parents\F11.cas.h5'
  parent_data: 'C:\P4P\parents\F11.dat.h5'
  child_case: 'C:\P4P\runs\S4-05-run-001\setup.cas.h5'
  final_case: 'C:\P4P\runs\S4-05-run-001\final.cas.h5'
  final_data: 'C:\P4P\runs\S4-05-run-001\final.dat.h5'
  autosave_root: 'C:\P4P\runs\S4-05-run-001\checkpoints'
  transcript: 'C:\P4P\runs\S4-05-run-001\logs\fluent.trn'
  runner_log: 'C:\P4P\runs\S4-05-run-001\logs\runner.log'
  artifact_manifest: 'C:\P4P\runs\S4-05-run-001\artifact-manifest.json'

report_files:
  brine_mass_flow: 'C:\P4P\runs\S4-05-run-001\reports\brine_mass_flow.out'

durability:
  onedrive_final_root: '...'
  status: PENDING
```

The exact schema may evolve, but the experiment-local file is authoritative. Code, agents, and later analysis should use or reconcile against it rather than reconstructing locations from assumptions.

Before launch, create required remote directories and check that intended destinations are writable and will not unintentionally overwrite another run. After the smoke test and after the long run, verify that required outputs appeared at the declared locations and update the same `run-paths.yaml` with any reconciled actual locations or path anomalies.

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
7. update `run-paths.yaml` with the verified durable locations;
8. only then describe the OneDrive copy as verified/durable.

Never assume synchronization completed merely because a file appeared in a local OneDrive folder. For crucial artifacts, verify that the intended files are present and complete through the available filesystem/sync evidence.

If OneDrive is temporarily unavailable, preserve the full local case/data pair, record the local paths in `run-paths.yaml`, and report the artifact as `LOCAL_ONLY` durability debt rather than pretending it is safely replicated.

## Produce an explicit execution plan

Before `implement-experiment`, make placement, staging, paths, and durability concrete. The execution plan is represented durably by the experiment-local `run-paths.yaml` plus the setup's scientific contract.

The exact remote paths and runtime server reference belong to `run-paths.yaml`, not `setup.md`. `setup.md` remains server-neutral.

`implement-experiment` should receive this placement contract and execute it faithfully. If staging cannot prove the required parent, or important output locations remain ambiguous, do not substitute a similarly named local file or implicit working directory; return the placement/path failure for re-planning.

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
FLEET: active / busy / unavailable server refs
ARTIFACTS: exact parent/final/recovery locations and verification status
PLACEMENT: setup -> run -> server.ref
PATH MAP: canonical Project/.../run-paths.yaml
TRANSFERS: required source -> OneDrive -> destination actions
DURABILITY: verified OneDrive finals/checkpoints and any LOCAL_ONLY debt
BLOCKERS: unavailable parent, uncertain identity, ambiguous output path, compatibility issues
```

The scientific orchestrator decides what experiments are worth doing. This skill makes the justified work runnable, locatable, parallel where sensible, and less dependent on any one physical server.