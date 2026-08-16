# Setup-linked post-simulation report structure

Use this as guidance for `Setups/reports/<setup-id>/results.md`. The structure is intentionally adaptive: organize the central results around the setup question, not around a mandatory carrier/DPM/EWF sequence.

## 1. Investigation context

State briefly:

- setup definition and setup ID;
- investigation mode;
- primary question;
- controlled change and reference/comparison scope;
- interpretation owner and current interpretation status.

Default to:

```text
Interpretation owner: user-led
Interpretation status: pending user direction
```

unless the user has already supplied criteria or delegated interpretation.

## 2. Run identity and observed state

Record:

- case/data checkpoint names when available;
- Fluent version;
- iteration count or physical-time window;
- initialization/restart status where relevant;
- relevant active model state;
- deviations from the intended setup;
- links to setup/readback and raw output bundles.

Never use a Fluent `server_id` as case or setup identity.

## 3. Analysis plan and applicability

Show what evidence was collected **and why**.

| Analysis / evidence | Status | Relevance to primary question | Source/method |
|---|---|---|---|
| `<...>` | `complete / partial / unavailable / not applicable / requires rerun / blocked` | `<...>` | `<artifact or method>` |

Do not create empty DPM/EWF/VOF sections merely because the template knows those models exist.

If an existing script was not suitable, record the custom read-only extraction or derived calculation used instead.

## 4. Results organized around the setup question

Choose headings that match the experiment. Examples:

- brine-outlet liquid/vapour split;
- pressure response across the sensitivity matrix;
- liquid inventory evolution;
- VOF interface behavior;
- timestep/mesh/initialization sensitivity;
- DPM diameter response;
- EWF drainage behavior;
- local pressure/velocity structure;
- numerical verification comparison.

Within each result group:

1. show direct measured values first;
2. show derived quantities separately;
3. preserve units, zone/surface definitions, signs, reductions, and time/iteration scope;
4. link raw evidence rather than duplicating full transcripts.

## 5. Module-specific content when relevant

These are optional modules, not mandatory report sections.

### Carrier / phase flow

Report inlet/outlet phase fluxes, balance metrics, monitor trends, and scoped efficiency/recovery metrics when they answer the setup question. Distinguish a local/scoped diagnostic from full separator validation.

### DPM

For selected relevant injections, retain injection identity, size, source surface, tracked counts, zone/fate output, represented/net mass flow and closure bookkeeping. State whether secondary splash parcels/events are already represented in final fates. Do not substitute missing categories with zero.

### EWF

For confirmed film walls, preserve exact Fluent units and distinguish final inventory (`kg`) from source/flux rates (`kg/s`). Include stripping/separation/splash terms only when active and relevant. A single final checkpoint is not a time-integrated film closure.

### VOF / transient

When interface dynamics matter, report physical-time histories, time-window statistics, liquid inventory, interface/volume-fraction behavior, or timestep/initialization comparisons as required. Do not infer stable transient behavior from a final contour alone.

### Verification / validation

For verification, report the numerical comparison the setup defined. For validation, name the independent reference, comparison metric, tolerance/uncertainty basis and validity scope. Without those ingredients, use `validation claim unresolved`.

## 6. Evidence quality and limitations

Record limitations only insofar as they affect use of the evidence:

- residual/monitor behavior;
- common-window comparability;
- mass/phase closure where relevant;
- timestep/mesh independence where relevant;
- unavailable histories;
- inherited setup caveats;
- intended-vs-observed setup drift;
- incomplete analysis artifacts.

An exploratory run can remain scientifically useful even when it is not validation-grade. Avoid turning generic CFD quality checks into automatic rejection rules for every experiment.

## 7. Neutral observations

Separate:

- **Measured** — direct Fluent/export quantities;
- **Derived** — calculations from measured values;
- **Observed pattern** — trends/comparisons directly supported by the evidence;
- **Unresolved** — missing evidence or ambiguous comparison.

This section should be readable without requiring the reader to accept the agent's physical interpretation.

## 8. Interpretation handoff

Unless interpretation was already delegated, end the evidence portion with focused questions for the user. Examples:

- Which metric should control the decision?
- Should this be treated as a screening signal, a numerical verification result, or compared against a specific validation target?
- Which case/reference should be the main comparison?
- Do you want possible physical explanations for the observed pattern?
- Is another analysis needed before choosing a next experiment?

Do not automatically conclude `keep`, `reject`, choose a preferred operating point/model, or prescribe the next setup.

## 9. Optional interpretation

Add only after the user provides direction or when criteria were explicitly defined in advance.

Record:

- interpretation owner: `user-provided`, `joint`, or `agent-proposed`;
- evidence used;
- interpretation and scope/confidence;
- alternative explanations where material;
- user-approved decision or next action.

Preserve the original evidence when interpretation changes later.
