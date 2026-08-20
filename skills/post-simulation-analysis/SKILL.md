---
name: post-simulation-analysis
description: "Plan and perform setup-specific post-simulation analysis for existing Ansys Fluent case/data results. Start from the setup's scientific question, discover what evidence is available, propose analyses with an explicit relevance rationale, ask the user to choose or refine the analysis when the choice is material, reuse existing carrier/DPM/EWF scripts where they fit, and create custom read-only extraction when they do not. Reports are evidence-first and user-interpreted by default."
---

# Adaptive Post-Simulation Analysis

## Purpose

Analyse an already-built Fluent case/data state in a way that answers the **specific setup question**.

Existing scripts are analysis tools, not the analysis plan.

The workflow should be able to handle:

- a case that fits the existing carrier/DPM/EWF diagnostic scripts exactly;
- a VOF, transient, pressure-sensitivity, local-drainage, mesh/timestep, or other setup where those scripts cover only part of the question;
- a case where the most relevant evidence has not yet been extracted and must be discovered or gathered with a one-off read-only PyFluent calculation;
- a case where the available checkpoint cannot answer the intended question and the correct result is a clear evidence gap rather than a forced interpretation.

Do not rebuild setup physics in this skill. If answering the question requires changing physics, initialization, mesh, boundary conditions, or rerunning with new monitors, describe that requirement and hand it back to setup/run planning.

## Core principle

The analysis sequence is:

```text
setup intent
-> live/file evidence discovery
-> candidate analyses + relevance
-> user analysis choice when material
-> deterministic/custom extraction
-> evidence quality check
-> evidence-first report
-> user interpretation handoff
-> optional interpretation after direction
```

Do not reverse this into `available script -> run script -> invent a conclusion`.

## 1. Recover the investigation intent

Before choosing analyses, read:

1. repository `AGENTS.md` and `Setups/order-dictionary.md`;
2. the target setup definition;
3. the relevant parent/reference/comparison setup when the question is comparative;
4. the target setup's existing results report, if present;
5. `PyAnsys/AGENTS.md` and only the diagnostic documentation relevant to candidate tools.

Extract or infer only what the sources support:

- setup ID and case/data identity basis;
- investigation mode: exploratory, diagnostic, sensitivity, verification, validation, production/decision, or user-defined equivalent;
- primary question;
- controlled changes and frozen comparison context;
- evidence already requested in the setup;
- pre-agreed decision/validation criteria, if any;
- interpretation owner, defaulting to `user-led`.

If the setup predates the intent-first format, reconstruct the likely question from the setup and report, but label uncertain intent. Ask the user when that uncertainty would materially change what data should be gathered.

Do not assume an exploratory setup is a validation exercise. Do not invent acceptance criteria from normal CFD conventions unless the user asks for a proposed criterion.

## 2. Discover available evidence before committing to an analysis

Perform cheap, read-only discovery first. This discovery does not require the user to pre-select analyses because its purpose is to make the analysis choice informed.

Discover as applicable:

- observed case/data filenames or whether identity is unavailable;
- Fluent and PyFluent version;
- steady/transient state, iteration count or physical time;
- active multiphase/turbulence/energy/DPM/EWF models;
- phase names;
- boundary/cell-zone names and types;
- active DPM injections and their source surfaces;
- confirmed EWF film walls and enabled mechanisms;
- existing report definitions, monitor histories and autosave/checkpoint data;
- available field variables and surfaces needed for likely metrics;
- existing PyAnsys output bundles for this case;
- comparison checkpoints named by the setup.

Use Settings API/live audits/file manifests where appropriate. A missing Settings API path is a version/adapter finding, not proof that a model is disabled.

### Case identity gate

Treat connection metadata only as routing information.

- A Fluent `server_id`, hostname, port, iteration count, or version is never case/setup identity.
- When the workflow explicitly loads a case/data pair, retain those filenames as the identity basis.
- When an already-open session does not expose filenames, record identity as `unavailable` unless independent evidence maps the session to a setup.
- Do not create setup-linked scientific claims from an unidentified live session. You may still report an unlinked diagnostic.
- Never persist `server_id` as report provenance.

## 3. Build an analysis menu around the question

After discovery, create a compact **analysis plan**. Each proposed analysis must state why it is relevant.

Use this shape:

| Candidate analysis | Question it helps answer | Data/source | Method | Cost/risk | Recommendation |
|---|---|---|---|---|---|
| `<metric or diagnostic>` | `<specific connection to setup question>` | `<existing history / final data / live report / comparison case>` | `<existing script / custom read-only extraction / offline calculation>` | `<low / moderate / requires rerun>` | `core / useful / optional / not recommended` |

Candidate categories may include, but are not limited to:

- numerical state and convergence/monitor stability;
- total or phase mass-flow closure;
- outlet flow split, recovery, carryover, leakage or backflow;
- pressure drop or local pressure distribution;
- liquid/vapour inventory and its transient trend;
- VOF interface position, topology, oscillation or time-averaged occupancy;
- local volume fraction, velocity, pressure, turbulence or residence behavior;
- DPM fate, trajectory, diameter dependence and represented mass flow;
- EWF inventory, thickness, velocity, source, drainage and mechanism-specific terms;
- mesh sensitivity, timestep sensitivity, initialization sensitivity or cross-case response surfaces;
- geometry-specific local probes;
- a setup-specific derived metric defined from relevant Fluent quantities;
- comparison with experimental/literature/reference data when the setup is explicitly verification/validation-oriented.

Do not include an analysis just because a reusable script exists.

### User analysis-choice gate

When the user has already named the analyses they want, execute those and add only clearly necessary supporting checks.

When the user asks generically to "analyse the case/results" and more than one materially different analysis path is reasonable:

1. perform discovery;
2. show the candidate analysis menu and the rationale;
3. identify the smallest core pack you recommend;
4. ask the user which analyses they want, whether any metric matters most, and whether they want evidence-only or interpretive help.

Do not ask a generic question such as "what analysis do you want?" before discovery. Give the user an informed choice.

If a cheap supporting extraction is necessary to make an approved analysis meaningful, the agent may include it without another approval. If a proposed analysis requires a rerun, new monitor history, model/setup change, or substantial new computation, flag that before proceeding.

## 4. Choose the best extraction method, not just the existing script

### Reuse existing tools when they fit

Current reusable tools include carrier/post-simulation extraction and the EWF/DPM diagnostics under `PyAnsys/scripts/inspection/` and `PyAnsys/src/pyansys_fluent/`.

Use them when their outputs answer an approved analysis question. Preserve their raw JSON/CSV/transcript artifacts and link them from the report.

### Extend beyond existing scripts when needed

If no existing script exposes the needed evidence:

1. inspect the live/file state to identify the relevant Fluent quantity, zone, surface, report definition, monitor, or field variable;
2. search the repository for an existing accessor or extraction pattern;
3. when Fluent/PyFluent API behavior is uncertain, consult the version-relevant official Fluent/PyFluent documentation;
4. prefer a read-only Settings API query, Fluent report/surface/volume integral, field-data extraction, transcript command, or offline calculation from saved data;
5. create a small one-off analysis script or command when that is safer and more reproducible than manual console interaction;
6. record exactly how the quantity was obtained, its units, zone/surface scope, sign convention, reduction, and time/iteration basis;
7. if the extraction is likely reusable, place it in the appropriate PyAnsys analysis module rather than embedding opaque logic only in the report.

Custom analysis must not silently enable or change physical models. Namespaced post-processing/report objects may be created when necessary and safe; record them and avoid overwriting user objects.

If the desired evidence cannot be reconstructed from the existing checkpoint, say so. Do not substitute a vaguely related metric merely because it is available.

### Reconstructing residual histories from batched runs

Use `PyAnsys/scripts/report/build_03a_stage3_stitched_scaled_residuals.py` as the reference implementation:

- `parse_native_stream()` reads Fluent residual rows from each transcript.
- `merge_series()` joins chunks by native iteration and removes verified duplicate iterations.
- `build_data()` preserves source segments, gaps, stage boundaries, and failure tails.
- `plot()` creates the log-scaled branch plot; display-only clipping must be annotated.

Run it with `PyAnsys/.venv/bin/python -u PyAnsys/scripts/report/build_03a_stage3_stitched_scaled_residuals.py`. Keep missing iterations missing—do not interpolate—and save the JSON plus PNG beside the report.

### Recovering report-plot histories from native `.out` files

Use `PyAnsys/scripts/inspection/extract_report_plot_histories.py` when Fluent's `Solution -> Monitors -> Report Plots` are configured but the live PyFluent monitor buffers are empty, or when report-file paths are relative and their directory is uncertain. Fluent Report Files are separate post-processing artifacts; they do not have to be beside the `.cas/.dat` pair. A relative name such as `./metric-rfile.out` only works when it resolves from Fluent's current working directory.

The read-only procedure is:

1. inspect the existing session and its `solution.monitor.report_files` state;
2. pass the remote Windows directory containing the `.out` files with `--report-dir` rather than changing Fluent's working directory;
3. let the extractor check each file, read Fluent's Lisp-style history forms through Scheme, reconstruct iteration/value pairs, and write a local JSON manifest plus overview PNG;
4. use repeated `--report-name` filters for a focused analysis, or omit them to recover every configured active report file;
5. preserve the raw paths, point counts, report-definition names, and any read errors in the report's evidence links.

Example:

```bash
PyAnsys/.venv/bin/python -u PyAnsys/scripts/inspection/extract_report_plot_histories.py \
  --server-id 1 \
  --report-dir 'C:\path\to\report-directory' \
  --output-dir PyAnsys/output/report_plot_histories
```

Adapt `--report-dir` to the case's remote layout and use `--report-name` for the relevant phase, zone, pressure, inventory, routing, or balance histories. The extractor does not assume a particular setup family, number of phases, steady/transient mode, unit system, sign convention, or report-definition naming scheme. If a Fluent version serializes report files with a different header/data shape, update `parse_report_forms()` and retain the explicit failure rather than treating an empty or unreadable file as zero history. If the files are absent from the saved checkpoint, classify the evidence as `requires rerun` and instrument the report files before the next solve.

## 5. Analysis-specific safeguards

The following are **module safeguards**, not universal reasons to run the module.

### Carrier / phase-flow analysis

When phase fluxes or balance metrics are relevant:

- preserve Fluent sign convention and show any outward-positive conversion explicitly;
- state the exact inlet/outlet zones and phase scope;
- distinguish scoped outlet metrics from full-domain conservation or separator validation;
- use monitor histories when the question concerns stability over time/iterations rather than a single checkpoint.

### DPM analysis

Run DPM only when it is relevant to the setup question or explicitly requested.

When a DPM Particle Tracks Summary is run, for every selected injection require:

1. `number tracked = ...`;
2. a `Mass Transfer Summary` section;
3. at least one parsed mass-transfer row;
4. a completed transcript/quiet interval appropriate to the command;
5. immediate preservation of raw transcript and partial structured output.

Preserve counts, zone/fate rows, represented/net mass flow, elapsed-time statistics where available, and closure bookkeeping. Do not replace missing fates with zero.

Splash events and EWF absorbed-event counters are mechanism/event diagnostics, not automatically additional terminal mass sinks. Avoid double-counting secondary parcels whose later terminal fates are already included.

An active inherited DPM branch does **not** make a full DPM sweep mandatory when DPM is irrelevant to the setup question. If its configuration could materially contaminate interpretation, audit and report that fact even if detailed fate analysis is skipped.

### EWF analysis

Run EWF analysis only for confirmed active film walls/mechanisms and when it helps answer the approved question.

For final-state snapshots, preserve exact units and distinguish:

- inventory/cumulative quantities in `kg`;
- rates/sources in `kg/s`;
- local/maximum/area-weighted reductions;
- active versus inactive stripping, separation, splash or other mechanisms.

A single final `.dat.h5` is a snapshot. It cannot establish a time-integrated EWF closure unless the required histories exist.

### VOF / transient analysis

For VOF or other unsteady interface questions, do not reduce the result automatically to final residuals and outlet fluxes. Consider whether the setup question needs:

- physical-time histories;
- time-window averages and variation;
- liquid inventory versus time;
- interface/volume-fraction surfaces or occupancy;
- periodicity/oscillation behavior;
- timestep and initialization comparison;
- local outlet/interface behavior.

A final-state contour alone cannot establish a statistically stable transient behavior.

### Sensitivity / comparison analysis

For a controlled matrix, compare like with like:

- same metric definition, units, surfaces and sign conventions;
- comparable physical-time or convergence/stability windows;
- explicit note when cases stop at different iteration counts or states;
- distinguish directional screening from a converged ranking.

Do not select a winning case unless the user supplied or later chooses a decision rule.

### Verification / validation analysis

For verification, analyse the numerical claim actually being tested: e.g. mesh/timestep independence, iterative convergence, implementation consistency, or conservation.

For validation, require an independent reference and declared comparison metric/scope. Include uncertainty/tolerance treatment appropriate to the user's validation plan. If those ingredients are absent, report `validation claim unresolved`; do not invent a validation verdict.

## 6. Completion must be evidence-based, not time-based

Do not use a fixed wall-clock supervision duration as the primary completion rule.

For each analysis command, define completion predicates such as:

- process/client completion;
- Fluent health/liveness when live;
- expected transcript marker(s);
- required JSON/CSV/image/artifact existence;
- parser completion;
- file size/content stability when Fluent may flush asynchronously;
- command-specific timeout and explicit error state.

Do not start a conflicting Fluent analysis while a prior command is still producing output.

If an analysis fails its completion gate, preserve partial artifacts and report it as incomplete. Do not infer missing values.

## 7. Evaluate evidence quality before interpretation

Classify the result of each approved analysis as:

- `complete` — required evidence for that analysis was captured;
- `partial` — useful but incomplete evidence exists;
- `unavailable` — the quantity cannot be recovered from the current checkpoint/session;
- `not applicable` — the model/quantity does not apply to this setup;
- `requires rerun` — the evidence needed a monitor/history/state that was not captured;
- `blocked` — a technical failure prevented extraction.

Separate **analysis execution completeness** from **scientific adequacy**. A perfectly complete DPM transcript can still be irrelevant to the setup question; a partial transient history can still provide exploratory evidence without supporting a final claim.

## 8. Report evidence before meaning

When report-facing evidence changed, write or update `Setups/reports/<setup-id>/results.md` using `Setups/templates/results-report-template.md` and `references/report-structure.md`.

The default report must:

- restate the setup's primary question and investigation mode;
- state what was actually run;
- list analyses performed and why each was relevant;
- present measured values before derived metrics;
- record numerical/evidence limitations;
- summarize neutral observations;
- set `Interpretation status: pending user direction` unless interpretation was already delegated or criteria were pre-agreed;
- end with focused interpretation questions when a decision remains open.

Do not paste full transcripts into the report. Link raw PyAnsys artifacts.

Preserve earlier checkpoint evidence rather than silently replacing it. Add a dated/checkpoint subsection or explicitly supersede a prior item with provenance.

## 9. Interpretation handoff

By default, the agent does **not** decide:

- whether a case is physically good or bad;
- whether a pressure/model is preferred;
- whether a setup should be kept or rejected;
- the causal explanation for an observed pattern;
- the next experiment;
- whether evidence constitutes validation.

Instead, after presenting the evidence, ask focused questions based on what was found. Examples:

- Which metric should control the comparison?
- Should this checkpoint be treated as an exploratory signal or evaluated against a specific criterion?
- Do you want possible physical explanations for this trend, or should the report remain evidence-only?
- Should we compare against the parent, another case in the matrix, or literature/experimental data?
- Is the current numerical state sufficient for the decision you want to make?
- Which additional analysis would resolve the most important remaining uncertainty?

When the user supplies an interpretation or asks the agent to interpret, add a clearly separated optional interpretation section. Mark it `user-provided`, `joint`, or `agent-proposed` and tie each claim to the evidence used.

## 10. Relationship to setup/run planning

When post-analysis discovers that decisive evidence is missing because it needed to be instrumented before solving, return a concrete request to the setup/run workflow, for example:

- create a liquid-inventory time-history monitor;
- freeze named pressure probe surfaces across a sensitivity matrix;
- export interface statistics every timestep;
- rerun a comparison case to a common physical-time window;
- add a report definition before the next solve.

Explain why the new evidence is relevant to the setup question. Do not automatically modify and rerun the case from this skill.

## Completion check

- The analysis plan starts from the setup question, not from the script inventory.
- Cheap discovery was performed before asking the user to choose among materially different analyses.
- Every executed analysis has a stated relevance to the setup question.
- Existing scripts were reused where appropriate but were not treated as mandatory.
- Custom evidence gathering was attempted when a relevant quantity was not covered by existing scripts.
- Relative Report File paths were resolved and checked before declaring report-plot history unavailable.
- No physics/setup state was silently changed to expose a result.
- Case/data identity is traceable or explicitly unavailable.
- Analysis completion is based on output predicates, not a universal wait time.
- Measured, derived, observed-pattern and unresolved evidence are distinguishable.
- Validation claims are made only under an explicit validation contract.
- Interpretation ownership is explicit and defaults to the user.
- The report hands decisions back to the user unless interpretation was explicitly delegated.
