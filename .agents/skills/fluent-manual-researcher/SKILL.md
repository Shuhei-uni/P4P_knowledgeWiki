---
name: fluent-manual-researcher
description: Research an uncertain Fluent setting from the version-matched official Ansys Fluent manual, including GUI screenshots and prerequisites, then translate the documented state into a live PyFluent Settings API or version-pinned TUI recipe and verify it by readback plus save/reopen. Invoke automatically when Fluent configuration cannot be located, activated, interpreted, set, or proven confidently from the live PyFluent tree alone.
---

# Fluent Manual Researcher

Use this skill when Fluent configuration is uncertain enough that guessing a PyFluent path or copying an old recipe would risk creating the wrong model.

This is a narrow capability-resolution skill. It does not redesign the experiment, choose scientific model assumptions on behalf of the project, or run an expensive solve. Its job is to answer:

> For this exact Fluent version and case state, what configuration does the Fluent manual require, and how can that state be applied and proven through PyFluent or a controlled TUI fallback?

## Automatic trigger

Invoke this skill automatically when any of the following occurs:

- a required Fluent setting cannot be found confidently in the live Settings tree;
- a Settings branch or command is unexpectedly inactive;
- the agent does not understand what a GUI/manual concept means in the current model;
- an allowed value, object type, phase-pair control, or model-specific boundary field is unclear;
- enabling a model changes the exposed tree and the correct dependency order is uncertain;
- a manual-required setting exists conceptually but live readback cannot prove its state;
- the Settings API does not expose a usable mutation path and a TUI fallback may be needed;
- a TUI prompt sequence or version dependency is uncertain;
- a previously working capability recipe no longer matches the current Fluent version or case fingerprint.

Typical examples include Eulerian phase creation, phase-interaction and drag controls, multiphase turbulence, phase-specific boundary conditions, DPM or EWF submodel dependencies, and other model-dependent controls.

Do not invoke this skill merely because a setting is unfamiliar if `fluent-live-inspection` can resolve it directly and prove the state.

## Authority and source order

Use the following evidence order.

1. **Version-matched official Ansys Fluent User's Guide** as the semantic authority for what the model or setting means, what prerequisites exist, and what configuration state is intended.
2. **Official manual screenshots** to understand GUI structure, visible controls, tabs, phase pairs, option placement, and example state.
3. **Official PyFluent documentation for the matching installed/generated API** to identify candidate Settings API or TUI access paths.
4. **The active live Fluent tree** to determine what actually exists and is active in this exact case state.
5. **Known-working repository code** as an implementation pattern when it is compatible with the current version and case fingerprint.
6. **Version-pinned TUI** only when the Settings API path is unavailable or inadequate and the TUI route can be tested and read back safely.

Do not use an old blog post, forum answer, remembered path, or another Fluent version as the primary authority when the official matching manual is available.

## Screenshot rule

Manual screenshots are useful evidence, but do not treat a selected value in an example screenshot as a scientific recommendation.

Use screenshots to answer questions such as:

- Which tab or panel owns the setting?
- Which controls appear only after another model or phase is created?
- What phase pair or object is being edited?
- What GUI state should be visible after successful configuration?

Use the surrounding manual prose to determine meaning, prerequisites, defaults, restrictions, recommendations, and model applicability.

Always separate:

```text
screenshot shows this option selected
```

from:

```text
manual recommends this option for this class of problem
```

and from:

```text
this option is scientifically appropriate for the current P4P experiment
```

Those are three different claims.

## Research workflow

### 1. Fingerprint the exact problem

Before researching a path, record the smallest useful capability fingerprint:

- Fluent version;
- PyFluent version when relevant;
- solver mode, dimension, and precision when relevant;
- loaded parent/child case identity;
- active model family;
- phase count and phase identities;
- relevant material assignments;
- relevant boundary/object types;
- the intended state that cannot currently be proved.

Do not assume that a recipe verified under one fingerprint is portable to another.

### 2. State the research question precisely

Translate the blocker into an explicit target state rather than a Python-path question.

Prefer:

> Define a two-phase Eulerian interaction pair with a specified drag law and prove the selected drag state survives save/reopen.

instead of:

> Find the `phase_interaction` attribute.

The manual describes Fluent state and physics; the API path is an implementation detail discovered afterward.

### 3. Read the relevant manual section before attempting mutation

Find the version-matched official Fluent manual section for the setting.

Extract only what the manual supports:

- prerequisites;
- creation/activation order;
- required versus optional controls;
- relevant restrictions;
- available model choices;
- defaults or recommendations, clearly labelled as such;
- phase, zone, or object scope;
- save/reload implications when documented;
- any GUI screenshot evidence that clarifies structure.

Build a short **manual state checklist** describing what should exist in Fluent if the configuration is complete.

### 4. Separate configuration mechanics from scientific choices

The researcher may determine how to configure a choice without deciding that the choice is scientifically correct.

For every non-trivial model option, classify it as one of:

- `experiment-specified` — already fixed by `setup.md` or the calling workflow;
- `manual-required` — Fluent requires a value/state for the model to be fully defined;
- `manual-default` — Fluent provides a default, but the project has not justified it scientifically;
- `candidate` — technically available and researchable, but requires scientific selection upstream;
- `unknown` — not yet supported by enough evidence.

Never convert `manual-default` or `candidate` into `experiment-specified` silently.

If a scientific value is missing, verify the mechanism with a disposable candidate only when that does not contaminate the approved experiment, and return the unresolved scientific choice explicitly.

### 5. Resolve the live automation path

Use `fluent-live-inspection` and the repository inspection tooling to inspect the smallest relevant live branch.

Prefer this order:

1. verified reusable capability recipe for the same compatible fingerprint;
2. active Settings API path;
3. active command or generated PyFluent API path;
4. version-matched PyFluent TUI path;
5. no mutation.

Inspect active children, active commands, current state, allowed values, object names, and read-only/active status where supported.

Do not rely on `dir()` or wrapper attributes alone when the live active-state methods can provide stronger evidence.

After any parent/model/type creation or activation, discard stale handles, reacquire the affected Settings objects, and inspect again.

### 6. Use TUI only as a controlled fallback

A TUI fallback is acceptable for setup mutation when all of the following are true:

- the official Fluent/PyFluent documentation supports the command family for the matching version;
- the Settings API path is absent, inactive, or inadequate;
- the command is version-pinned when prompt compatibility matters;
- the mutation is performed only in a disposable test child/session first;
- the resulting state can be read back independently through Settings state, a second documented query, or another deterministic inspection method;
- save/reopen verification is possible.

Do not use TUI merely because it is familiar. Do not use a successful command return as proof that the intended Fluent state exists.

This skill researches setup/configuration controls only. It does not override the repository rule that autonomous experiment iteration should remain on the approved Python/PyFluent execution path unless the human explicitly approves another run mechanism.

### 7. Prove the recipe in a disposable child/session

Do not first test an uncertain mutation on the only important parent or on a running experiment.

Use a disposable child or recoverable session and apply the smallest dependency-ordered sequence:

```text
load exact parent
-> inspect prerequisites
-> activate/create parent object
-> reacquire
-> set one dependency-sensitive child
-> read back
-> continue until target state is complete
```

After each important mutation, record requested versus observed state.

If a step cannot be read back, the recipe is not yet verified.

### 8. Save, reopen, and verify again

A recipe is not verified merely because the setter returned without error.

For the completed disposable configuration:

1. perform a strict pre-save readback against the manual state checklist;
2. save the child case to a declared disposable path;
3. close or leave the original session as appropriate and open the saved case in a fresh Fluent session;
4. reacquire all relevant Settings objects;
5. repeat the critical readback;
6. compare the reopened state with the intended target state.

Only a recipe that survives this gate may be returned as `VERIFIED_RECIPE`.

## Output contract

Return one of two terminal statuses.

### `VERIFIED_RECIPE`

Use only when the configuration mechanics were proven by live mutation, readback, save, fresh reopen, and second readback.

Report:

```yaml
status: VERIFIED_RECIPE
fingerprint:
  fluent_version: ...
  pyfluent_version: ...
  active_models: [...]
  relevant_objects: ...

research_question: ...
manual_authority:
  section: ...
  url: ...
  screenshot_evidence:
    - ...

manual_state_checklist:
  - ...

scientific_classification:
  experiment_specified: [...]
  manual_required: [...]
  manual_defaults: [...]
  candidates_requiring_scientific_choice: [...]

verified_recipe:
  strategy: settings-api | tui | mixed
  dependency_order:
    - ...
  operations:
    - action: ...
      requested: ...
      observed: ...

verification:
  pre_save_readback: pass
  saved_case: ...
  fresh_reopen: pass
  post_reopen_readback: pass

limitations:
  - ...
```

A `VERIFIED_RECIPE` proves **how to create and preserve the requested Fluent state**. It does not automatically prove that every chosen physics option is the correct model for the real separator.

### `RESEARCH_BLOCKED`

Use when the intended state cannot be implemented and proven safely.

Report:

- exact target state that remains unproved;
- Fluent/PyFluent fingerprint;
- manual evidence found;
- live paths/commands inspected;
- mutation attempts made in the disposable environment;
- last state that was successfully read back;
- why save/reopen verification could not be completed;
- whether the blocker is API exposure, inactive dependency state, undocumented TUI behaviour, scientific choice, version mismatch, or another bounded cause;
- the smallest next action that could resolve the blocker.

Do not return "probably configured", "looks active", or another partial-success label.

## Relationship to nearby skills

- `fluent-live-inspection` is the first tool for an uncertain live object/path. If the live tree can resolve the issue directly, stop there.
- `fluent-manual-researcher` is the escalation when the meaning, prerequisite order, or automation route is not safely recoverable from the live tree alone.
- `fluent-case-build-and-run` consumes a verified implementation recipe while building the approved child case.
- `implement-experiment` remains responsible for faithful experiment implementation, save/reopen proof, smoke testing, and execution.
- `design-experiment` and `phase-planner` own scientific/model-selection decisions that are outside the approved setup contract.

Return control to the calling workflow after capability resolution. Do not silently expand a setup-research task into a new scientific phase or production run.
