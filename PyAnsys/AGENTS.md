# PyAnsys agent guide

`PyAnsys/` is the executable Fluent/PyFluent layer of the repository. Keep automation reproducible, inspectable, and separated from project interpretation and setup history.

## Three responsibilities

Treat every simulation workflow as three separate responsibilities:

1. **Setup building** — create or modify the Fluent setup and verify the resulting `.cas.h5`.
2. **Run planning** — choose the simplest execution mode that matches the experiment: simple TUI, Fluent journal, or agent-owned Python orchestration.
3. **Run execution** — carry out that plan, preserve recovery evidence, and hand off clear status/results.

Do not collapse all three into one large script unless there is a strong reason.

## Run-mode selection

Use the simplest mode that gives the experiment the control it actually needs.

### 1. Simple TUI run

Use one direct Fluent/TUI solve command when:

- one case is already prepared;
- no settings change is required mid-run;
- no adaptive decision is required before completion.

Configure any required Fluent-native autosave first, then submit the run command. There is no benefit in adding an orchestration loop around a single uninterrupted calculation.

### 2. Fluent journal batch

Use a Fluent journal when several cases or fixed stages can run independently with no agent decision between them.

Typical examples:

- a pressure sweep of already-built sibling cases;
- multiple cases that each follow `load -> initialize -> run -> save`;
- a fixed sequence whose settings do not depend on intermediate results.

A batch journal must be robust: use explicit full paths, unique outputs, recovery/autosave where needed, transcripts/logging, and deterministic initialization/run/save steps. Prefer one journal over keeping an agent attached merely to submit the next independent case.

### 3. Agent-owned Python run

Use Python orchestration when the next action depends on the current result, for example:

- staged ramping;
- changing solver/model controls after a checkpoint;
- adaptive convergence gates;
- conditional continuation/termination;
- recovery logic that must inspect state before deciding what to do next.

The script should behave as a recoverable state machine, not a blind iteration loop. At each decision point:

```text
run block -> inspect evidence -> record state/checkpoint -> decide -> mutate if required -> continue
```

After transport uncertainty, reconnect and establish the actual Fluent stage/iteration state before issuing another solve command. Do not silently repeat an uncertain block.

When creating this type of workflow, always provide the exact launch command and a short supervisor guide so another agent can oversee it: what to watch, where checkpoints/logs live, how to identify the current stage, stop conditions, and how to resume safely.

See `knowledge/fluent-settings/native_run_and_autosave.md` for the detailed run-mode policy.

## Python runtime

For non-interactive PyAnsys work, invoke the repository interpreter directly:

```bash
/Users/shuheiyokkaichi/Developer/P4P_knowledgeWiki/PyAnsys/.venv/bin/python
```

Do not rely on activation state from an earlier shell/tool call.

## Fluent mental model

Treat Fluent as a dependency-ordered live state machine, not a static Python object tree.

Canonical mutation rule:

```text
enable/create parent -> reacquire -> inspect active children/options -> set child -> read back
```

Reacquire objects after loading a case/mesh, enabling a model, creating an object, changing a type, changing phase count, or changing boundary/model family.

A successful setter call is not proof of success; read back critical settings.

## Case identity

`server_id` is routing only. It never identifies a setup, case, checkpoint, or result.

Use explicit/observed case and data filenames for provenance. If the live session does not expose them and no independent mapping exists, record case identity as `unavailable`. Do not put `server_id` in report-facing identity fields.

## Read before non-trivial Fluent mutation

Read only what is relevant:

1. `knowledge/fluent-settings/README.md`;
2. `knowledge/fluent-settings/orders/global_setup_order.yaml`;
3. the relevant model `trees/*.md` and `orders/*.yaml`;
4. `knowledge/fluent-settings/indices/path_dependency_index.json` when a path/order is unclear;
5. the reusable helper being changed under `src/pyansys_fluent/`.

For a new or uncertain deep Fluent path, inspect the live session before writing mutation-heavy code. Use official Fluent/PyFluent documentation when local knowledge and the live tree do not resolve it.

## Code placement

- `src/pyansys_fluent/` — reusable mechanics.
- `scripts/connection/` — connection/bootstrap checks.
- `scripts/inspection/` — read-only discovery and analysis helpers.
- `scripts/setup/` — case-specific setup and run orchestration.
- `knowledge/fluent-settings/` — verified paths, dependency order, fallbacks, and run guidance.
- `extractors/` — reusable case/data extraction.
- `output/` — temporary/generated evidence only.

Keep setup scripts thin. Move repeated mechanics into `src/`.

## `output/` storage policy

`PyAnsys/output/` is scratch/evidence storage, not an archive.

Keep only outputs that are still useful for:

- setup/readback checks;
- post-simulation analysis and result reports;
- data used by plots and the final plots themselves;
- compact manifests/diagnostics needed to reproduce a conclusion;
- active debugging.

Delete temporary or superseded outputs once they are no longer required. In particular, avoid retaining repeated snapshots, duplicate JSON/CSV exports, superseded plots, large temporary field dumps, and copied case/data files that already have an authoritative location elsewhere.

Prefer the smallest retained artifact that preserves the evidence. Do not delete the only copy of a result or checkpoint needed for recovery/reporting. Repository-wide cleanup rules live in `../skills/repo-maintenance/SKILL.md`.

## Failure handling

When a Fluent mutation fails:

1. inspect parent activation/order and reacquire the object;
2. inspect active children, commands, and allowed values;
3. classify the problem as dependency/order, path/version, value/format, wrapper limitation, TUI fallback, or manual-only;
4. isolate the smallest failing branch;
5. use TUI only after the Settings API path has been inspected;
6. record reusable discoveries in `knowledge/fluent-settings/`.

Do not rerun an entire setup blindly because one deep setting failed.

## Multi-agent use

Use subagents when they reduce uncertainty, not by default for every task. The useful roles are:

- local Fluent/path knowledge;
- current official documentation;
- setup/physics context;
- execution/refactoring.

The main agent reconciles conflicts. For API/path questions, the live Fluent tree is the strongest evidence; for scientific intent, the explicit setup/user requirement is authoritative.

## Cross-system boundaries

- Reusable CFD knowledge belongs in `../CFD_wiki/`.
- Concrete setup lineage belongs in `../Setups/`.
- Project interpretation/V&V decisions belong in `../ResearchProject_wiki/`.
- PyAnsys should contain executable automation and the technical knowledge needed to operate it.

## Before finishing

Confirm that:

- the setup/run-plan/run responsibilities are clear;
- the selected run mode matches the experiment complexity;
- critical Fluent changes were inspected/read back;
- case identity is explicit or marked unavailable;
- reusable code/knowledge went to the right layer;
- temporary `output/` artifacts were minimized or cleaned up;
- complex Python-run workflows include an exact command and supervisor/resume instructions.

If a direct user instruction conflicts with this guide, follow the user instruction.
