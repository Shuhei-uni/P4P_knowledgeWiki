---
record_type: "setup-record"
programme: "full-geometry"
geometry: "<exact geometry / mesh / case programme>"
physics_family: "<mixture / vof / dpm-ewf / other>"
campaign: "<lowercase-kebab-case-campaign>"
record_id: "<campaign-scoped ID or none>"
stage: "<none or campaign stage label>"
lifecycle: "active | future | reported | archived"
canonical_path: "Setups/full-geometry/<physics>/<campaign>/<filename>.md"
report_home: "Setups/reports/full-geometry/<physics>/<campaign>/"
---

> **RETAINED TEMPLATE — NOT FOR NEW SELECTED EXPERIMENTS**
> New selected experiments use [`Project/experiments/`](../../Project/experiments/) with co-located `setup.md` and `results.md`. Use this template only when reviewing or explicitly repairing a retained `Setups/` setup record.

# Setup Record — <campaign / stage / setup name>

> This is a flexible setup record, not a form that must be filled completely. Keep only sections that help define, build, run, or later analyse this specific case.
>
> Store one canonical copy under the campaign setup path. Use a redirect or an explicitly labelled compatibility snapshot for old links; do not maintain duplicate authorities.

## Intent

| Field | Value |
|---|---|
| Record ID | `<campaign-scoped ID or none>` |
| Record role | `campaign-contract` / `setup` / `stage-plan` |
| Programme | `full-geometry` / `purnanto-reference` / `<other>` |
| Geometry identity | `<exact mesh/case evidence or link>` |
| Campaign | `<lowercase-kebab-case campaign path>` |
| Investigation mode | `exploratory` / `diagnostic` / `sensitivity` / `verification` / `validation` / `production-decision` / `<other>` |
| Primary question | `<what are we trying to learn or establish?>` |
| Interpretation owner | `user-led` by default / `joint` / `agent-led if explicitly requested` |
| Parent / reference | `<link or none>` |
| Lifecycle | `active` / `future` / `reported` / `archived` |
| Canonical setup path | `Setups/full-geometry/<physics>/<campaign>/<filename>.md` |
| Mirrored report home | `Setups/reports/full-geometry/<physics>/<campaign>/` |
| Linked results | `<link or none>` |

### Why this setup exists

Describe the question in plain language. For an experiment, state what uncertainty or mechanism is being probed. For verification/validation, state the exact claim being tested and its scope.

### Hypothesis or expectation — optional

Record only if useful. Label it as a hypothesis/expectation, not a conclusion.

## Controlled comparison

### Intentional changes

| Variable / feature | Reference | This setup | Why changed |
|---|---|---|---|
| `<...>` | `<...>` | `<...>` | `<...>` |

### Frozen context

List only settings that must remain fixed for the comparison to remain meaningful. Link the parent for everything else rather than duplicating it.

## Fluent build contract

Give the implementation agent enough exact information to create or verify the case.

### Geometry and mesh

- Geometry/mesh identity: `<artifact or description>`
- Required zone/topology facts: `<...>`
- Operator-assisted items: `<where the agent should stop and ask the user for help, or none>`

### Models, materials, phases and operating conditions

Record required values and important inherited values that must be read back. Omit generic explanation.

### Boundary conditions

| Zone / role | Type | Required state | Notes / readback |
|---|---|---|---|
| `<...>` | `<...>` | `<value + unit + phase state>` | `<...>` |

### Initialization and run controls

State exactly what initialization, patching, transient/steady controls, timestep/iterations, autosave, or restart behavior defines this experiment.

### Build/readback gates

List only checks required to prove that the intended case was created. If ambiguity in geometry or zone mapping requires the user, say so explicitly.

## Evidence to collect

Do not turn this section into a generic post-processing checklist. Include measurements because they answer the primary question or because they must be instrumented before solving.

| Evidence / measurement | Why it is relevant | When it must be captured | Required or optional |
|---|---|---|---|
| `<...>` | `<connection to primary question>` | `before run / during run / final state / post-process` | `<...>` |

Possible evidence can include residual/monitor history, phase fluxes, local pressures, liquid inventory, VOF interface behavior, DPM fates, EWF quantities, contours, or setup-specific derived metrics. Use only what is relevant.

## Interpretation contract

- Interpretation status before results: `not started`.
- Default interpretation owner: `user-led`.
- Decisions intentionally deferred until results exist: `<pressure selection / model choice / whether evidence is sufficient / next experiment / etc.>`
- Pre-agreed decision or validation criteria, if any: `<criteria or none>`

For exploratory/diagnostic work, do not invent acceptance criteria. For verification/validation work, state the required criterion and evidence source explicitly.

## Provenance and linked evidence

- Parent/reference setup: `<link>`
- Case/data artifacts: `<links when available>`
- Build/readback evidence: `<links>`
- Relevant reusable CFD method: `<link if needed>`
- Relevant project/literature context: `<link if needed>`

## Open items

List unresolved implementation or experimental-design decisions. Do not fill gaps by assumption when they could change the meaning of the experiment.
