---
name: setup-report
description: "Create and manage concrete Fluent setup records and setup-linked result reports. Start from the scientific intent of the setup, distinguish exploratory/diagnostic/sensitivity work from verification or validation, make the Fluent build contract explicit, and keep interpretation user-led by default. Use for new setup branches, setup definitions, lifecycle/lineage work, result-report creation, or setup/report cleanup."
---

# Setup Report

## Purpose

`Setups/` documents concrete simulation instances. A setup record has two jobs:

1. make the intended Fluent case reproducible enough for an implementation agent to build or verify it; and
2. make the scientific reason for the case obvious enough that later analysis can collect relevant evidence.

A setup record is **not** a place for the agent to decide what the result means before the run exists.

Keep reusable CFD methods in `CFD_wiki`, project-level conclusions in `ResearchProject_wiki`, and executable automation in `PyAnsys/`.

Before working on a setup, read:

1. repository `AGENTS.md`;
2. `Setups/order-dictionary.md`;
3. the relevant parent/comparison setup and linked results;
4. the project roadmap when current research direction matters.

## Core principle: intent first, interpretation later

Before creating or materially revising a setup record, establish the **intent contract**. Use information already supplied by the user or repository; do not ask again for facts that are already clear.

Record:

- **Primary question** — what this case is trying to learn, test, reproduce, verify, or validate.
- **Investigation mode** — one of the following, or a clearer user-defined label:
  - `exploratory`: learn what the model does; unexpected behavior is useful evidence;
  - `diagnostic`: isolate why an existing case behaves a certain way;
  - `sensitivity`: vary one or more declared factors and compare responses;
  - `verification`: test numerical/model implementation consistency, convergence, or independence;
  - `validation`: compare against independent physical/experimental evidence and support a stated validity claim;
  - `production/decision`: use an already-qualified model to support an engineering decision.
- **Controlled changes** — what is intentionally different from the reference.
- **Frozen context** — what should remain unchanged for the comparison to remain meaningful.
- **Evidence sought** — what measurements would help answer the primary question. These are analysis targets, not automatic conclusions.
- **Interpretation owner** — default `user-led`. Use `joint` or `agent-led` only when the user explicitly requests it.

If the investigation mode or primary question is genuinely ambiguous and would change the case definition, ask the user before finalising the setup. If the user has already made the intent clear, proceed without a redundant approval loop.

### Claim-strength rule

The investigation mode determines how strong later claims may be:

- exploratory/diagnostic/sensitivity setups may produce useful directional or mechanistic evidence without satisfying validation-grade criteria;
- verification setups require explicit numerical checks relevant to the verification question;
- validation setups must name the independent reference, comparison quantity, tolerances/uncertainty treatment, and validity scope before a validation claim can be made;
- never upgrade an exploratory result into a validated result merely because the numbers look good.

## Setup record structure

Use `Setups/templates/setup-record-template.md` as a flexible guide, not a mandatory form. Omit sections that add no value and add sections when the experiment needs them.

A useful setup record normally contains:

1. **Intent and question** — concise statement of why this case exists and its investigation mode.
2. **Reference and controlled changes** — parent/baseline, intentional differences, frozen settings.
3. **Fluent build contract** — exact geometry/mesh identity, models, materials, phases, boundary conditions, initialization, numerics, and run controls needed by the implementation agent.
4. **Build/readback gates** — only the checks needed to prove the intended case was actually created.
5. **Evidence to collect** — setup-specific measurements or histories that should exist before/during the run because they may be impossible to reconstruct afterwards.
6. **Interpretation contract** — who will interpret the result and what decisions are intentionally deferred until evidence exists.
7. **Lineage/provenance** — setup ID, lifecycle, linked artifacts, parent/comparison cases.

Do not pad a setup record with generic CFD explanations. Prefer a short, exact build instruction over a long narrative.

## Experimental setup behavior

For exploratory, diagnostic, and sensitivity work:

- describe hypotheses as hypotheses, not expected truths;
- avoid success/failure language unless the user has supplied a genuine criterion;
- prefer `observations to collect`, `comparison questions`, or `screening signals` over rigid acceptance gates;
- a surprising or numerically imperfect result may still answer the experimental question;
- do not silently stop or reject a case merely because it fails a criterion that was invented by the agent.

For verification/validation work:

- explicit criteria are appropriate, but they must be tied to the stated verification/validation objective;
- record the evidence basis and uncertainty/limitations required for the intended claim;
- if a required criterion is missing, mark the claim as unresolved rather than inventing one.

## Fluent implementation contract

The setup record should be directly useful to the Fluent implementation agent. Clearly separate:

- **required state**: exact settings that define the experiment;
- **preserved state**: settings inherited from the parent and not intended to change;
- **operator-assisted items**: geometry, patching, zone identification, or other tasks where the user wants the agent to stop and request help;
- **implementation freedom**: safe choices that do not alter experimental meaning.

When a parent case exists, prefer a controlled delta over restating every inherited value. Read back critical inherited settings before relying on them.

Case identity must come from explicit file/case evidence or an independently verified setup mapping. Never infer a case from a Fluent server/connection ID.

## Evidence planning, not interpretation

A setup may suggest analyses because some evidence must be instrumented before solving. Examples include report definitions, time histories, phase fluxes, local probes, liquid inventory, VOF interface measures, DPM injection results, or EWF bookkeeping.

For each requested measurement, state **why it is relevant to the primary question**.

Do not require carrier/DPM/EWF analyses simply because a script exists. The post-simulation analysis skill will inspect the actual case, propose applicable analyses, and ask the user how broad the analysis should be when the choice is material.

## Results report behavior

When actual numerical evidence exists, use `Setups/templates/results-report-template.md`.

The default result report is an **evidence packet**, not an agent verdict. It should:

- remind the reader what question the setup was intended to investigate;
- state exactly what was run and which evidence was collected;
- present measured and derived values clearly;
- identify missing evidence, numerical limitations, and comparison caveats;
- distinguish observations from interpretations;
- set `Interpretation status: pending user direction` unless the user already supplied an interpretation framework or explicitly delegated interpretation;
- end with focused questions or decision options for the user when interpretation is still open.

Do not automatically end every report with `keep`, `reject`, `needs follow-up`, a preferred pressure/model, or a next simulation. Those are decisions for the user unless a decision rule was supplied in advance.

If the user asks for interpretation, add it as a clearly separated section and state whether it is user-provided, jointly developed, or agent-proposed.

## Lifecycle and lineage

Lifecycle management remains separate from scientific interpretation.

Use:

- `active` — currently being built, run, or actively analysed;
- `future` — intentionally planned but not started;
- `reported` — no longer active and has useful setup-linked numerical evidence;
- `archived` — historical, superseded, invalid, parked, or setup-only.

A report may be preliminary while a setup remains active. `reported` does not mean validated.

When creating or renaming setup records:

1. preserve assigned setup numbers;
2. use a new number/branch suffix instead of rewriting history;
3. avoid `current`, `latest`, and `final` in filenames;
4. use `NN[-branch]-short-description.md`;
5. update `Setups/order-dictionary.md` and affected links when lineage or paths change.

For lifecycle-only mutations where the desired state is not already explicit, present the proposed change and obtain the user's final call before moving/archiving/renaming records. Do not add an approval gate to ordinary setup drafting when the user has already asked for the setup to be created.

## Technical extraction and drift

Use `Setups/templates/technical-setup-report-template.md` when a machine-extracted Fluent state needs to be compared with the intended setup record.

Treat extracted Fluent state as evidence of what was actually loaded/configured; treat the setup record as evidence of intended experiment definition. When they disagree, record the drift and ask for a decision when it changes experimental meaning. Do not silently reinterpret the setup to match the export.

## Completion check

Before finishing setup/report work, confirm:

- the primary question and investigation mode are visible near the top;
- the controlled changes and frozen comparison context are unambiguous;
- the Fluent implementation agent can identify what must be built/read back;
- pre-run monitors required for the intended evidence are identified;
- hypotheses are not written as conclusions;
- validation language appears only when a validation contract exists;
- interpretation ownership is explicit and defaults to the user;
- result reports preserve measured/derived evidence without forcing an agent verdict;
- lineage, setup identity, and artifact links remain traceable.
