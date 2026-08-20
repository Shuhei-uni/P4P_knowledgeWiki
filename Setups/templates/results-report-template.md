---
record_type: "result-report"
programme: "full-geometry"
geometry: "<exact geometry / mesh / case programme>"
physics_family: "<mixture / vof / dpm-ewf / other>"
campaign: "<lowercase-kebab-case-campaign>"
record_id: "<setup/stage/run ID or none>"
experiment_id: "<setup/stage/experiment folder ID>"
run_id: "<run/checkpoint ID or none>"
lifecycle: "active | reported | archived"
canonical_path: "Setups/reports/full-geometry/<physics>/<campaign>/<experiment-id>/<filename>.md"
setup_path: "Setups/full-geometry/<physics>/<campaign>/<setup-or-stage>.md"
---

# Results Report — <campaign / setup / stage / run>

> **Filing rule:** for new full-geometry work, save this report under `Setups/reports/full-geometry/<physics>/<campaign>/<experiment-id>/`. Do not save completed-run reports beside `setup.md` under `Setups/full-geometry/...`.
>
> Default behavior: this report presents the evidence clearly and leaves scientific interpretation to the user unless an interpretation framework was supplied in advance or the user explicitly asks the agent to interpret.
>
> Use one report file per completed run, checkpoint, or evidence packet. Keep companion plots/evidence under this experiment folder, never in a shared campaign-level `plots/` directory.

## 1. What this run was trying to investigate

- Setup/stage definition: `<link to Setups/full-geometry/... or legacy setup>`
- Experiment folder: `Setups/reports/full-geometry/<physics>/<campaign>/<experiment-id>/`
- Report path: `Setups/reports/full-geometry/<physics>/<campaign>/<experiment-id>/<filename>.md`
- Run/checkpoint ID: `<stable ID, date-qualified ID, or none>`
- Investigation mode: `<exploratory / diagnostic / sensitivity / verification / validation / ...>`
- Primary question: `<copied or faithfully summarized from setup>`
- Controlled change(s): `<what differed from reference>`
- Reference/comparison case: `<link or none>`
- Interpretation owner: `user-led` / `joint` / `agent-led`
- Interpretation status: `pending user direction` / `criteria supplied in setup` / `interpreted on user request`

Keep this short. Do not rewrite the entire setup definition.

## 2. What was actually run

| Item | Observed value / evidence |
|---|---|
| Case/data identity | `<files or unavailable>` |
| Fluent version | `<...>` |
| Initialization/restart state | `<...>` |
| Iterations / physical time | `<...>` |
| Relevant model state | `<only what matters to this run>` |
| Deviations from intended setup | `<none or exact deviation>` |

Link raw setup/readback evidence where available.

## 3. Evidence collected and why

List the analyses actually performed. Do not force carrier, DPM, EWF, VOF, or another analysis category into the report when it is irrelevant.

| Analysis / evidence | Status | Why it matters to this setup question | Source |
|---|---|---|---|
| `<...>` | `completed / partial / unavailable / not applicable / deferred` | `<relevance>` | `<artifact link>` |

If a useful analysis was not captured, explain what is missing and whether it can be recovered from the existing case/data or requires a rerun.

## 4. Results

Organize this section around the setup question rather than around a fixed script taxonomy.

### <Result group relevant to the setup>

Present direct Fluent measurements first. Use compact tables and preserve units, sign conventions, time/iteration scope, and surface/zone definitions.

### Derived quantities — when useful

Show equations or transformations used to turn measured values into derived metrics. Keep measured and derived values distinguishable.

### Visual / spatial evidence — when useful

Record contour, vector, streamline, pathline, interface, particle, film, or geometry observations with evidence links. Describe what is visible without assigning physical meaning that the user has not requested.

## 5. Numerical state and evidence quality

Record only limitations that affect how the evidence can be used:

- residual/monitor behavior;
- time-window or iteration-window stability;
- mass/phase closure where relevant;
- timestep/mesh independence where relevant to the investigation mode;
- incomplete or missing outputs;
- inherited configuration caveats;
- differences between intended and observed setup state.

For exploratory or diagnostic runs, numerical imperfection may be part of the evidence. Do not automatically turn every imperfection into a failed run. For verification/validation, apply the pre-agreed criteria explicitly.

## 6. Observations without interpretation

Summarize the most important evidence as neutral statements.

Use labels where helpful:

- **Measured:** direct Fluent/export value.
- **Derived:** calculated from measured values.
- **Observed pattern:** visible trend or comparison supported by the evidence.
- **Unresolved:** data or comparison still missing.

Avoid causal claims, model selection, operating-point selection, `keep/reject`, or recommendations here unless they follow a decision rule the user supplied before interpretation.

## 7. Interpretation handoff

**Interpretation status:** `pending user direction` by default.

State the decisions that the evidence could inform, then ask focused questions rather than choosing for the user. Do not ask generic questions when the setup already contains the user's interpretation criteria.

## 8. Interpretation — optional, only after direction

Add this section only when the user explicitly interprets the result, asks for joint interpretation, asks the agent to interpret, or supplied a decision framework in advance.

Record:

- interpretation owner: `user-provided` / `joint` / `agent-proposed`;
- evidence used;
- interpretation and confidence/scope;
- alternatives or unresolved explanations when material;
- any user-approved next action.

Do not silently rewrite evidence sections to match a later interpretation. Preserve the evidence and append/update this section transparently.
