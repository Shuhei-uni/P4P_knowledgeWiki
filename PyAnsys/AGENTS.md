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
- `server-profiles/`: non-secret per-server remote directory knowledge; routing
  and filesystem context only, never case identity.
- Report/post-processing helpers that were tied to retired campaign trees are
  not kept as a second active layer; current read-only checks live in
  `scripts/inspection/` and reusable modules under `src/`.
- `knowledge/fluent-settings/native_run_and_autosave.md`: the durable current
  run-supervision, recovery, and autosave policy. The legacy filename is kept
  for stable links; Python-supervised execution is now the default.
- `output/`: generated extracts and diagnostics; never the scientific authority.

Prefer an existing helper or proven script before writing campaign-specific
code. Skills describe the workflow; code is the implementation evidence.

## Fluent state and identity

Treat Fluent as a dependency-ordered state machine, not a static object tree.
`server_id`, hostname, port, Fluent version, and iteration count are connection
or diagnostic metadata, not case identity. Inspect the loaded case/data state
and use an explicit or independently observed case/data path. If identity
cannot be established, record it as unavailable rather than guessing.

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

## CASE → INITIALISE / RUN

Setup construction and long-run supervision are separate responsibilities.

- A setup script loads an explicit parent, verifies remote inputs, inspects the
  current state, applies only the selected delta, verifies critical invariants,
  and writes the required case artifact.
- For autonomous work inside `scientific-phase-loop`, the default run mechanism
  is a Python/PyFluent runner supervised by an agent using `supervise-fluent-run`.
- The supervising agent stays with the runner terminal for the planned horizon,
  remains mostly read-only while Fluent is advancing, wakes on meaningful
  events/errors, and verifies the final data before handoff.
- Prefer one clear Python-issued run for the planned horizon over fine-grained
  one-iteration polling loops. Periodic recovery artifacts may still be
  configured when the experiment requires them, but the agent should not
  micromanage normal solver progress.
- TUI-driven iteration, Fluent journal/batch submission, or GUI-owned execution
  are exceptions that require explicit human approval for that run. Do not use
  them automatically as a fallback when the Python/PyFluent path fails.
- A floating-point error, initialization failure, Fluent crash, unreconciled
  connection/run state, or final-save failure is a blocker: preserve the last
  verified state and return the execution evidence for a rethink. Poor
  residuals or scientifically unpromising behaviour are not execution stop
  conditions when Fluent can still continue.
- Record the actual parent identity, controlled change, readback, case artifact,
  Python runner, requested budget, observed final state, remote artifact paths,
  and unresolved execution uncertainty.

## High-risk model guardrails

Stabilize the carrier setup before adding DPM or EWF unless the selected setup
explicitly requires another order. Create/read back default DPM injections
before editing detailed properties, reacquire after injection/type changes, and
verify particle scope and fates. Enable EWF only after its carrier/DPM
preconditions are established. Enable Energy only when thermal fields are part
of the question. Inspect the current phase/domain/wall mapping before using a
proven pattern.

## Evidence and synchronization

Generated JSON, CSV, plots, transcripts, and debug snapshots document what was
observed; they do not become project findings automatically. Preserve raw
artifacts, units, scope, signs, native coordinates, completeness, and identity
status. Do not turn missing evidence into zero, interpolate unknown gaps, or
infer completion from a filename.

Put current experiment evidence and findings in the selected `Project` record.
Put reusable CFD lessons in `CFD_wiki/`. Put implementation/discovery details
that are durable across cases in `PyAnsys/knowledge/`. Do not create a second
project log inside this folder.

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
locations, case identity, failure classification, and that no raw file or
unrequested project conclusion was changed.
