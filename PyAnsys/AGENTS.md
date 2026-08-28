# AGENTS.md

`PyAnsys/` owns the executable implementation, execution support, inspection,
and data-extraction layer for Fluent. It is not the authority for project
scientific conclusions (`../Project/`) or reusable CFD literature/method
knowledge (`../CFD_wiki/`).

## Progressive context

Load context only for the branch being worked:

```text
selected Project setup/results
→ relevant skill
→ proven PyAnsys code
→ live Fluent inspection when the current tree or version is uncertain
```

Do not preload the entire `knowledge/` tree, old logs, or every setup script.
When a task changes DPM, multiphase, Energy, EWF, or another version-sensitive
model, read only the relevant focused skill, the selected Project setup, and
the proven code path.

## Runtime and folder roles

From the repository root, use `PyAnsys/.venv/bin/python` for non-interactive
commands when that repository runtime exists. Do not rely on activation state
from another shell, and do not hard-code a different clone's absolute path.

- `src/pyansys_fluent/`: reusable library and extraction logic.
- `scripts/connection/`: connection and bootstrap checks.
- `scripts/inspection/`: non-mutating discovery, snapshots, and probes.
- `scripts/setup/`: thin case-specific setup/run orchestration.
- `scripts/orchestration/`: generic detached run supervision and event-driven handoff.
- `server-profiles/`: non-secret per-endpoint remote directory knowledge;
  routing and filesystem context only, never case identity or live availability.
- Report/post-processing helpers that were tied to retired campaign trees are
  not kept as a second active layer; current read-only checks live in
  `scripts/inspection/` and reusable modules under `src/`.
- `knowledge/fluent-settings/native_run_and_autosave.md`: the durable current
  run-supervision, recovery, autosave, and handoff policy. The legacy filename
  is kept for stable links; Python-supervised execution remains the default.
- `output/`: generated extracts and diagnostics; never the scientific authority.

Prefer an existing helper or proven script before writing campaign-specific
code. Skills describe the workflow; code is the implementation evidence.

## Fluent state and identity

Treat Fluent as a dependency-ordered state machine, not a static object tree.
`server_id`, IP/hostname, port, Fluent version, and iteration count are
connection or diagnostic metadata, not case identity. Inspect the loaded
case/data state and use an explicit or independently observed case/data path. If
identity cannot be established, record it as unavailable rather than guessing.

Keep artifact ID, setup ID, run ID, and runtime server reference separate. A
scientific setup must remain meaningful when re-placed onto another compatible
server.

Because collaborators may each have a `server-1`, `server-2`, and so on, do not
use the short server ID alone as the durable execution identity. Fleet preflight
should resolve the actual endpoint and record:

```yaml
server:
  ref: 'server-2@192.168.1.42'
  id: 'server-2'
  ip: '192.168.1.42'
  profile_id: 'shuhei-server-2'
```

Use `server.ref` for run placement and handoff while retaining the separate ID
and IP fields for machine-readable use. Static server profiles may use
collision-resistant names such as `shuhei-server-2` or `partner-server-2`
without hard-coding the IP into the public repository.

For a non-trivial change, use this order:

```text
enable/change parent
→ reacquire affected object
→ inspect children/options
→ set one logical child
→ read back the critical value
→ classify any failure before continuing
```

Reacquire after loading a case/data or mesh, enabling a model, creating an
object, changing an object/type, or changing phase count. A missing child path
means inspect the live parent and dependency state; it does not prove that the
old path is valid or that the model is disabled.

Readback mismatch is a failure even when the setter returned without an
exception. Use these failure labels: `order/dependency issue`,
`path/version issue`, `invalid value/format issue`, `PyFluent wrapper
limitation`, `requires human-approved TUI/journal fallback`, or `requires
manual GUI cleanup`.

## Fleet preflight and placement

Before new Fluent compute is committed, use `fluent-fleet-orchestration` to
check which configured servers are actually reachable and usable now, which are
busy, and which exact paired case/data artifacts are available on each machine
or through OneDrive.

Do not assume a server is available because it was used earlier in the phase.
Do not assume a parent exists on every server. Repeat live preflight whenever a
new compute cycle starts or server availability materially changes.

Prefer run placement in this order: exact verified parent already local;
verified parent available through OneDrive; verified parent publishable from
another active server; otherwise block until a trusted replica can be found.
Use useful active servers in parallel when the scientific work justifies it,
but never invent low-value experiments solely to increase utilization.

A setup record remains server-neutral. Exact runtime server reference, local
paths, transfer steps, and durability destinations belong to the execution
plan.

## Experiment packet and path authority

Keep the path record with the experiment rather than inside `PyAnsys/` runtime
output:

```text
Project/.../experiment/
├── setup.md
├── run-paths.yaml
└── results.md
```

`setup.md` is the scientific contract, `run-paths.yaml` is the authoritative
human-readable and machine-readable record of runtime server placement and
actual artifact/output paths, and `results.md` is the evidence/interpretation
record.

The canonical `run-paths.yaml` must state the runtime `server.ref`, separate
server ID and IP, actual Fluent working directory, run root,
parent/child/final case-data paths, autosaves/checkpoints, file-backed
monitor/report outputs such as `.out`, logs/transcripts, manifests, and OneDrive
final/recovery destinations when applicable. Do not reconstruct these paths from
a short server alias, case filename, launch directory, or code defaults.

A remote runner may use a temporary derived copy of path configuration, but do
not create another durable path manifest that competes with the Project packet.
Reconcile actual observed output locations back into the same Project
`run-paths.yaml` after smoke testing and final execution.

## CASE → INITIALISE / RUN

Setup construction and long-run execution are separate responsibilities.

- A setup script loads the exact resolved parent artifact, verifies remote
  inputs, inspects the current state, applies only the selected delta, verifies
  critical invariants, and writes the required case artifact.
- For autonomous work inside `scientific-phase-loop`, the default run mechanism
  is a Python/PyFluent runner launched through `supervise-fluent-run` and the
  detached `scripts/orchestration/run_and_handoff.py` worker.
- Do not keep an AI agent alive merely to watch Fluent advance. The detached
  worker owns the synchronous runner, logs, completion checks, and terminal
  manifest. When the job reaches `COMPLETE` or `BLOCKED`, it may resume the
  exact recorded Codex session with `codex exec resume <SESSION_ID> ...`.
- Use an explicit Codex session/thread ID for each scientific loop. Never use
  `--last` for autonomous handoff when several servers or jobs may finish
  independently.
- A zero runner exit code is not sufficient completion proof. The job contract
  must declare local required files and/or a deterministic verifier command so
  the final save and required execution evidence are checked before `COMPLETE`.
- Prefer one clear Python-issued run for the planned horizon over fine-grained
  one-iteration polling loops. Periodic recovery artifacts may still be
  configured when the experiment requires them; the worker should not
  micromanage normal solver progress.
- TUI-driven iteration, Fluent journal/batch submission, or GUI-owned execution
  are exceptions that require explicit human approval for that run. Do not use
  them automatically as a fallback when the Python/PyFluent path fails.
- A floating-point error, initialization failure, Fluent crash, unreconciled
  connection/run state, or final-save failure is a blocker: preserve the last
  verified state and hand the execution evidence back for a rethink. Poor
  residuals or scientifically unpromising behaviour are not execution stop
  conditions when Fluent can still continue.
- Refuse duplicate launches while an old job manifest exists unless the prior
  state has been reconciled and an explicit forced rerun is justified.
- Record the actual parent artifact identity, controlled change, readback, case
  artifact, run ID, runtime server reference, Python runner, requested budget,
  observed final state, remote artifact paths, durability status, terminal job
  manifest, handoff status, and unresolved execution uncertainty.

## Durable case/data preservation

Treat server-local storage as working storage, not the sole long-term home of
important scientific state.

Strongly prefer saving and promoting a **complete matching case+data pair** to
the approved OneDrive location for:

- scientifically important final run states;
- final states likely to become future branch parents;
- selected expensive recovery checkpoints whose loss would require substantial
  rerunning;
- important pre-change/reference states that would be difficult to reconstruct.

Do not synchronize every routine autosave or checkpoint. Keep high-frequency
recovery local when appropriate, then promote deliberately selected recovery
states and finals.

For important promoted artifacts, preserve one artifact ID plus source
setup/run, iteration or progress, filenames, origin `server.ref`, and hashes
when feasible. Verify the copied pair before treating it as durable. A file
merely appearing in a local OneDrive folder is not enough evidence of successful
preservation when the artifact is crucial.

If OneDrive is temporarily unavailable, keep the complete local pair intact and
record the state as `LOCAL_ONLY` durability debt. A run may be computationally
complete while still not yet safely replicated.

The aim is practical portability: loss or shutdown of one server should not
strand final results or force reconstruction of an expensive parent when a
verified shared copy could have prevented it.

## High-risk model guardrails

Stabilize the carrier setup before adding DPM or EWF unless the selected setup
explicitly requires another order. Create/read back default DPM injections
before editing detailed properties, reacquire after injection/type changes, and
verify particle scope and fates. Enable EWF only after its carrier/DPM
preconditions are established. Enable Energy only when thermal fields are part
of the question. Inspect the current phase/domain/wall mapping before using a
proven pattern.

## Evidence and synchronization

Generated YAML/JSON, CSV, plots, transcripts, and debug snapshots document what
was observed; they do not become project findings automatically. Preserve raw
artifacts, units, scope, signs, native coordinates, completeness, and identity
status. Do not turn missing evidence into zero, interpolate unknown gaps, or
infer completion from a filename.

Put current experiment evidence and findings in the selected `Project` record.
Put reusable CFD lessons in `CFD_wiki/`. Put implementation/discovery details
that are durable across cases in `PyAnsys/knowledge/`. Use OneDrive for verified
large case/data artifact preservation and transfer; do not create a second
scientific project log there.

## Troubleshooting and delegation

When a deep path fails, inspect the live branch and allowed values, check the
relevant local knowledge, and isolate the smallest failing operation. If the
Python/PyFluent path cannot perform the required operation, classify that
failure and return it. TUI or journal fallback requires explicit human approval;
do not silently take that route.

Use a bounded specialist review or probe only when it answers a concrete
uncertainty. There is no mandatory multi-agent ceremony; the main agent owns
reconciliation of live evidence, proven code, and project intent.

Before handoff, verify dependency order, critical readbacks, artifact
locations, case identity, the canonical experiment `run-paths.yaml`, runtime
server reference, durability status for important artifacts, terminal job
manifest, failure classification, and that no raw file or unrequested project
conclusion was changed.
