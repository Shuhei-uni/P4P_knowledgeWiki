# AGENTS.md

## Mission
`PyAnsys/` is a remote Fluent automation workspace for building, inspecting, rebuilding, and extending simulation setups through PyFluent, gRPC, TUI fallbacks, and case-specific orchestration scripts.

From now on, the workflow is intentionally split into two separate responsibilities:
- setup-building scripts produce or modify only `.cas.h5`
- Fluent itself owns initialization, iteration, and native autosave; Python may prepare the run and reconnect later for inspection or recovery

Never make a long simulation depend on a laptop-side Python/gRPC loop. Do not
poll iterations from Python, write periodic checkpoints from Python, or treat a
local run-state JSON as the authoritative recovery record. See
`knowledge/fluent-settings/native_run_and_autosave.md`.

The explicitly documented `03A-stage3` F01–F12 adaptive blocking workflow is a narrow user-approved exception to the normal long-run rule. It is defined below and in `knowledge/fluent-settings/native_run_and_autosave.md`; do not generalize it to other campaigns.

Do not collapse setup construction and run/save orchestration back into one monolithic script unless the user explicitly asks for that.

The main risk in this folder is not just wrong values. The main risk is writing automation that assumes Fluent is a stable Python object tree when it actually behaves like a dependency-ordered GUI state machine.

This file defines the strict local workflow for agents working in `PyAnsys/`.

## Python runtime
For every non-interactive PyAnsys command, invoke the repository's interpreter
directly:

```bash
/Users/shuheiyokkaichi/Developer/P4P_knowledgeWiki/PyAnsys/.venv/bin/python
```

Before a live Fluent command, verify the interpreter in that same shell with:

```bash
/Users/shuheiyokkaichi/Developer/P4P_knowledgeWiki/PyAnsys/.venv/bin/python -c 'import sys; print(sys.executable)'
```

Do not rely on `source .venv/bin/activate` from a previous command or tool
invocation; its shell state does not persist. Interactive activation is optional
only when it occurs in the same terminal session as the command.

## Directory Purpose In The Repo
`PyAnsys/` is the executable layer of the repository.

It should own:
- automation code and reusable helpers;
- inspection and probe scripts;
- read-only reconnecting monitors for Fluent-native runs;
- setup rebuild and case-only save orchestration;
- native-run preparation notes and Fluent-native journal guidance;
- post-run inspection and offline case/data analysis;
- extracted machine-readable setup knowledge;
- machine-readable verification targets and claim-gate logic.

It should not become the main place for:
- reusable CFD literature interpretation, which belongs in `../CFD_wiki/`;
- project sign-off decisions, which belong in `../ResearchProject_wiki/wiki/vnv/`;
- setup lineage history, which belongs in `../Setups/`.

## Core Mental Model
- Treat Fluent as a live GUI state machine, not a static API.
- Assume settings paths can change by Fluent version, solver mode, active models, phase count, boundary type, and object creation order.
- Assume object handles can become stale after enabling a model, changing a type, creating an object, or loading a case/mesh.
- Prefer a reproducible, inspectable setup flow over a clever or compact script.

Canonical rule:

```text
enable parent -> refresh/reacquire -> inspect children/options -> set child -> read back -> classify failure
```

## Fluent connection ID is not case identity

`server_id` is only a connection-routing alias. It selects which configured
Fluent endpoint PyFluent should contact; it does not identify the case, data
file, setup branch, checkpoint, or simulation lineage. The same configured
endpoint can host different cases over time, and different endpoints can host
the same case or continuation.

For every live Fluent workflow:

1. connect using the requested `server_id` only as transport configuration;
2. inspect the state loaded in that Fluent session before interpreting results;
3. use explicitly loaded or independently observed case/data filenames as case
   identity when available;
4. if Fluent does not expose the active filenames, mark case identity as
   `unavailable` and do not infer it from the server ID, Fluent version,
   iteration count, monitor shape, hostname, port, or an older record;
5. attach a setup ID only when the setup is explicitly supplied or independently
   established by the loaded case evidence.

The statement “server 3 means setup X” is invalid. Never persist `server_id` in
setup reports, result JSON, Markdown reports, manifests, filenames, or other
report-facing evidence. It may remain in CLI arguments, `.env` routing, and
transient connection diagnostics because those are transport details, not case
provenance.

## Required Reading Order
Before writing or changing any non-trivial setup script, read these files in order:

1. `knowledge/fluent-settings/README.md`
2. `knowledge/fluent-settings/agent_start_prompt.md`
3. `knowledge/fluent-settings/indices/master_index.json`
4. `knowledge/fluent-settings/orders/global_setup_order.yaml`
5. `knowledge/fluent-settings/indices/path_dependency_index.json`
6. the relevant model-specific `trees/*.md` and `orders/*.yaml`
7. `src/pyansys_fluent/common.py`
8. `src/pyansys_fluent/connection.py`
9. `src/pyansys_fluent/dependency_workflow.py`
10. `src/pyansys_fluent/setup_common.py`
11. `docs/PYANSYS_OVERHAUL_BLUEPRINT.md`

## Student Edition Remote Fallback
When working against the Windows Student Edition host, treat remote Fluent startup as a special case:

- If headless Fluent over SSH exits immediately after the gRPC server starts, assume stdin/EOF is the problem before assuming the setup script is broken.
- Prefer the opt-in local manual-launch path in `src/pyansys_fluent/connection.py` when the remote Student session is unstable.
- On the Windows host, set the launch environment explicitly if `.env` loading is unreliable in that Python environment:
  - `FLUENT_LOCAL_EXE`
  - `FLUENT_LOCAL_OUTPUT_DIR`
  - `FLUENT_LOCAL_PROCESSOR_COUNT`
  - `FLUENT_LOCAL_GUI`
  - `FLUENT_ALLOW_REMOTE_HOST`
  - `FLUENT_INSECURE_MODE`
- Verify the live session with `scripts/connection/check_connection.py` before running a long setup script.
- If `connect_to_fluent()` starts asking for TLS certificates or otherwise refuses the remote handoff, stop and switch to the local manual-launch path instead of iterating on shell quoting.
- When invoking a Windows batch wrapper from SSH, use `call <script>.cmd` so `cmd.exe` executes the batch file instead of treating the path as a raw command token.

If the task touches DPM, multiphase, Energy, or EWF, read that model's tree and order file before editing code.

## Multi-Agent Workflow
For non-trivial `PyAnsys/` work, use a fixed multi-agent workflow. The goal is to separate:
- Fluent nesting and call-order knowledge
- external API and documentation validation
- physics and setup-lineage intent
- actual script execution and refactoring

Default agent roles:

1. `knowledge agent`
   Scope:
   - `PyAnsys/knowledge/fluent-settings/`
   - especially `trees/`, `orders/`, `indices/`, and `logs/successful_paths.md`
   Responsibility:
   - extract the likely settings hierarchy
   - extract required parent activations
   - identify stale-handle and reacquire points
   - identify known risky branches and prior successful orders

2. `docs agent`
   Scope:
   - official/current PyFluent docs
   - official/current Fluent docs
   - version-sensitive API or TUI references
   Responsibility:
   - confirm or reject the local knowledge assumption
   - identify version-specific path or wrapper differences
   - identify TUI fallback candidates
   - identify cases where the wrapper is likely incomplete

3. `context agent`
   Scope:
   - `Setups/`
   - `CFD_wiki/`
   - `ResearchProject_wiki/` when the task is project-specific
   Responsibility:
   - explain why the setting exists physically
   - verify that the requested model choice is scientifically consistent
   - surface case-lineage constraints or inherited assumptions
   - identify whether the setup should preserve or intentionally diverge from prior cases

4. `execution agent`
   Scope:
   - `PyAnsys/src/`
   - `PyAnsys/scripts/`
   Responsibility:
   - implement or edit the actual script
   - keep orchestration thin and dependency-safe
   - run inspection-first workflow before mutation-heavy changes
   - push new discovered knowledge back into `PyAnsys/knowledge/`

The `execution agent` must not invent Fluent paths from memory when the other three roles can establish them first.

## Multi-Agent Execution Order
Unless the task is trivial, follow this order:

1. `knowledge agent` pass
2. `docs agent` pass
3. `context agent` pass
4. reconciliation by the main/execution agent
5. live inspection or probe pass against Fluent
6. only then script mutation or new setup-script authoring

Live inspection is mandatory before relying on any deep Fluent path for a non-trivial mutation.

## Required Outputs From Each Agent
Do not accept vague prose summaries from subagents. Each role should return structured outputs.

`knowledge agent` must return:
- target setting or branch
- required parent models/objects
- expected hierarchy or object path
- steps that require refresh/reacquire
- expected child names or options to inspect
- known failure signatures
- known successful order if available

`docs agent` must return:
- source used
- confirmed or conflicting path assumptions
- relevant version caveats
- wrapper limitation risks
- TUI fallback candidates
- unresolved uncertainties

`context agent` must return:
- physics purpose of the setting
- what physical assumption it changes
- whether the model choice is appropriate for this case
- setup-lineage constraints from prior reports/cases
- what must remain unchanged for comparability

`execution agent` must return:
- intended script edit plan
- live inspection points it will perform before setting values
- readback points
- fallback decision points
- knowledge files to update if new information is learned

## Task Sizing Rule
Use the full multi-agent workflow when any of these are true:
- the task touches DPM, multiphase, Energy, or EWF
- the task requires discovering or confirming nested Fluent paths
- the task changes model activation order
- the task derives a new setup from an old setup
- the task is likely to need TUI fallback
- the task changes physics assumptions, not just script plumbing

You may skip the full workflow only for small tasks such as:
- argument parsing cleanup
- pure refactors with no Fluent behavior change
- logging/output formatting changes
- file path handling or environment bootstrapping
- native Fluent autosave configuration or reconnection monitoring that does not own the iteration loop

## Main-Agent Reconciliation Rule
The main agent is responsible for resolving conflicts between:
- local knowledge notes
- current official documentation
- case physics intent
- live Fluent inspection

Resolution priority:
1. live Fluent inspection
2. scientifically required case intent
3. current official documentation
4. local knowledge notes

If these disagree, do not silently pick one. State the conflict and implement the safest testable path.

## Folder Roles
- `src/pyansys_fluent/`: reusable library code only
- `scripts/connection/`: connection/bootstrap/preflight only
- `scripts/inspection/`: non-mutating discovery, snapshotting, and probes
- `scripts/setup/`: case-specific orchestration only
- `knowledge/fluent-settings/`: agent knowledge base, dependency order, fallback strategy, and discovery log
- `knowledge/`: machine-readable or semi-structured local knowledge, including validation targets and claim-gate support files when present
- `extractors/`: case/data extraction tools and extracted-structure helpers
- `docs/`: operator notes, workflow docs, and environment procedures
- `tests/`: automation checks that do not require burying validation logic in ad hoc scripts
- `output/`: generated extracts and temporary automation outputs; do not treat as the authoritative knowledge layer
- `cases/actual_setup_archives/`: archived real setup snapshots for comparison/fallback

## Cross-System Sync Rules
- If a script changes project claim-gating behavior, make sure the human-readable rule still matches `../ResearchProject_wiki/wiki/vnv/`.
- If a script reveals a reusable CFD method lesson, summarize it in `../CFD_wiki/` rather than leaving it only in code comments.
- If a script defines or changes a concrete setup branch, sync the setup identity into `../Setups/`.
- If a script emits target manifests or automated check summaries that a human must review, link them from the corresponding `ResearchProject_wiki/wiki/vnv/` page.

Do not put case-specific orchestration logic into `src/` unless it is truly reusable across multiple setup scripts.

## Non-Negotiable Script Workflow
Treat setup building and simulation running as separate workflows.

### A. Setup-building scripts
Every non-trivial setup script that creates or modifies a setup must follow this sequence:

1. connect to Fluent through `src/pyansys_fluent/connection.py`
2. verify all required remote inputs exist before mutating anything
3. load the target mesh or source case explicitly
4. inspect current state when the script depends on named boundaries, phases, materials, or model activation
5. enable parent model or create parent object first
6. refresh and reacquire the affected object
7. inspect child names, command names, and allowed values
8. set one logical child at a time
9. refresh and reacquire again after any parent/type/object-creation change
10. read back the applied value
11. classify failure before choosing retry, TUI fallback, or manual cleanup
12. write the resulting setup as `.cas.h5`

Setup-building scripts should stop at a valid case-only artifact unless the user explicitly requests otherwise.

### B. Native Fluent run/save workflow

There is no repository-standard Python iteration runner. The approved workflow
is documented in `knowledge/fluent-settings/native_run_and_autosave.md`:

1. use Python for connection, input verification, setup mutation, and readback;
2. save a case-only setup artifact;
3. configure Fluent's native calculation activity and autosave controls;
4. initialize and start the calculation from Fluent or a Fluent-native journal;
5. let Fluent own iteration and checkpoint timing;
6. reconnect with Python later for live monitoring, recovery, or post-run inspection.

The standard read-only monitor is `scripts/inspection/monitor_native_run.py`.
It may reconnect with bounded backoff and persist observations, but it must not
issue solver commands or infer case identity from a connection alias.

Do not add Python loops around `solver.tui.solve.iterate(...)` or
`solver.settings.solution.run_calculation.iterate(...)`. Do not make a
checkpoint depend on a Python call returning successfully after each iteration
block.

### C. Explicit 03A Stage-3 adaptive checkpoint exception

The user has explicitly approved a narrow exception for:

`Setups/full-geometry/mixture/steady-liquid-outlet/03a-stage3-fluent-recommended-convergence-sweep.md`

and only its F01–F12 production branches.

The Stage-3 experiment requires the execution agent to evaluate a whole-field gate at discrete checkpoints before deciding whether to remain at the current state or advance. For these branches, the execution agent may therefore remain attached to Fluent and issue **one synchronous blocking solve call per scientific decision block**:

- first intermediate-state block: `750` iterations;
- later intermediate-state reassessment blocks: `250` iterations;
- final-condition blocks: as specified by the Stage-3 authority.

The blocking call returning is the intended agent wake-up mechanism. After return, the agent inspects the histories, evaluates the frozen Stage-3 gate, records the decision, performs any prescribed checkpoint/transition, and only then issues the next solve block.

This exception does **not** authorize a generic Python iteration runner:

- no Python `for`/`while` loop around solve calls;
- no one-iteration or fine-grained client loop;
- no automatic repetition of an uncertain block after connection loss;
- Fluent-native local autosave remains mandatory for recovery;
- reconnect to the same Fluent process first after transport failure and establish actual stage/iteration state before taking further solver action;
- gRPC/client/transport failure is not `NUMERICAL_FAILURE` unless Fluent itself has numerically failed;
- the exception does not apply outside F01–F12 unless the user explicitly extends it.

## Script Architecture Rules
Case scripts in `scripts/setup/` must stay thin orchestration layers.

Preferred structure:
- parser and input validation
- connection and remote path verification
- case/mesh loading
- live discovery and role mapping
- model enablement blocks
- materials blocks
- cell zone and boundary blocks
- optional DPM or EWF blocks
- final case-only write block

Reusable logic belongs in `src/pyansys_fluent/`.

Examples of logic that should be shared instead of copied:
- connection and `.env` handling
- remote file/path checks
- safe state capture
- dependency-aware step execution
- boundary-role detection and name remapping
- JSON snapshot writing
- case-only loading and other focused setup/run IO helpers

## Dependency and Reacquire Rules
The following rules are mandatory:

- After enabling a model, reacquire the relevant settings branch before touching children.
- After creating a Fluent object, reacquire it before modifying nested fields.
- After changing injection type, particle type, boundary type, phase count, or model family, reacquire the object before setting dependent children.
- After loading a different case, data file, or mesh, do not reuse previously captured object handles.
- If a child path is missing, first suspect parent activation or stale handles before assuming the path is wrong.

## Failure Handling Rules
Use these categories exactly:
- `order/dependency issue`
- `path/version issue`
- `invalid value/format issue`
- `PyFluent wrapper limitation`
- `requires TUI fallback`
- `requires manual GUI cleanup`

If a step fails:
1. capture the exact parent path, child path, requested value, and error
2. inspect the live object children, commands, and allowed values
3. classify the failure
4. isolate the failing branch in the smallest possible test
5. use TUI fallback only after the Settings API path has been inspected and classified
6. do not rerun the whole setup blindly

If readback does not match the requested value, treat that as a real failure even when no exception was raised.

## Fallback Order
When a Settings API path fails, use this fallback order:

1. check parent-model and object-creation order
2. reacquire the live object
3. inspect child names, command names, and allowed values
4. check `knowledge/fluent-settings/indices/path_dependency_index.json`
5. check the relevant `trees/*.md` and `orders/*.yaml`
6. check `knowledge/fluent-settings/docs/documentation_map.md`
7. try a minimal TUI fallback
8. record a manual GUI fix only if automation is genuinely blocked

Do not jump to manual GUI cleanup before trying the dependency-order diagnosis.

## Knowledge Update Rules
Any time an agent discovers a new working path, required order, TUI workaround, or repeatable failure mode, update the knowledge layer.

Minimum rule:
- append successful live discoveries to `knowledge/fluent-settings/logs/successful_paths.md`

Update the relevant knowledge files when needed:
- `trees/*.md` for discovered live structure
- `orders/*.yaml` for verified order dependencies
- `indices/path_dependency_index.json` for hidden dependencies
- `docs/source_notes.md` or `docs/documentation_map.md` when external documentation meaningfully changed the approach

Do not leave important setup knowledge buried only inside a case script.

## Inspection First Rule
Before writing a new setup script for a new Fluent branch, prefer this sequence:

1. `scripts/connection/check_connection.py`
2. `scripts/inspection/inspect_fluent_session.py`
3. a targeted inspection/probe script if the task involves unclear paths
4. only then write or change the setup script

If the task is exploratory, write an inspection script before writing a mutation-heavy setup script.

For multi-agent work, the inspection pass should explicitly test the assumptions produced by the knowledge and docs agents before applying any setup mutation.

## DPM, Multiphase, Energy, and EWF Guardrails
For this repository, treat these as high-risk areas:
- DPM injection surface binding
- DPM inert-particle material creation and assignment
- Mixture vs VOF path differences
- phase-specific boundary tabs
- Energy-dependent temperature fields
- EWF wall tabs and DPM-wall-film coupling

Mandatory order constraints:
- stabilize the carrier-field setup before enabling DPM unless the task explicitly requires otherwise
- create default DPM injections before editing detailed injection properties
- reacquire each injection after changing particle type or injection type
- enable EWF only after the basic carrier case or DPM case is working
- enable Energy only when thermal fields are actually needed

## Anti-Patterns
Do not:
- write one-off setup scripts that duplicate large blocks from other scripts without extracting shared helpers
- mutate deep child settings immediately after parent activation without reacquiring objects
- assume a path seen in one case or version exists in another
- treat a successful setter call as proof that the setting took effect
- hide failures behind broad `try/except` without classification and readback
- restart the full setup just because one deep child path failed
- mix non-mutating inspection logic with heavy mutation logic unless the script is explicitly designed as a staged workflow

## Change Discipline
When editing `PyAnsys/`:
- prefer surgical edits that preserve the current workflow layering
- keep setup scripts readable and procedural at the top level
- move repeated mechanics into `src/pyansys_fluent/`
- preserve existing CLI flags unless there is a strong reason to change them
- avoid renaming scripts or moving files unless the new layout clearly improves the workflow contract
- keep long-run execution inside Fluent, except for the explicit F01–F12 Stage-3 adaptive blocking decision workflow above; setup deliverables remain `.cas.h5`, and all other Python use stays limited to preparation, reconnection, inspection, and post-processing

## Completion Checklist
Before finishing work in `PyAnsys/`, verify:

1. the script follows the canonical dependency-order workflow
2. the required multi-agent passes were used if the task was non-trivial
3. shared logic was placed in `src/` when appropriate
4. new risky paths have inspection or readback coverage
5. failure behavior is classified, not silent
6. the relevant knowledge files were updated if new path/order knowledge was learned
7. the script remains a thin orchestration layer rather than a new monolith
8. setup scripts save `.cas.h5` only; long-run iteration and autosave stay inside Fluent except for the explicit F01–F12 Stage-3 adaptive blocking decision workflow, while Python otherwise remains limited to preparation, reconnection, inspection, and post-processing

## Conflict Rule
If a direct instruction from the user conflicts with this file, follow the user's instruction.

Otherwise, this file is the operating contract for agents working inside `PyAnsys/`.