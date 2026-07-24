---
name: post-simulation-analysis
description: "Use for evidence-led post-simulation analysis and reporting of existing Ansys Fluent case/data results, including carrier-field checks, DPM particle-track fate and mass-flow closure, Eulerian Wall Film (EWF) configuration/final-state diagnostics, transcript capture, and setup-linked reports in Setups/reports/. Use when deciding which analyses apply to a concrete Fluent setup; do not use to rebuild a setup or enable/change solver physics."
---

# Post-Simulation Analysis

## Purpose and boundary

Analyse an already-built Fluent case/data state without rebuilding the setup or changing its physics. Use the resulting evidence to create or extend the report for that exact setup branch.

Keep roles separate:

- `PyAnsys/` owns executable inspection and generated artifacts.
- `Setups/reports/<setup-id>/` owns the concise, report-facing interpretation of one concrete setup.
- `Setups/` setup definitions own case identity and lineage; do not alter them merely because analysis was run.
- `ResearchProject_wiki` owns project-level conclusions and sign-off.

`snapshot` creates or reuses only namespaced `ewfdiag-*` report definitions. It must never enable EWF, splashing, stripping, edge separation, coupling, or any other physics merely to expose an output.

## Route the analysis from the setup

Before running anything, read in order:

1. Repository `AGENTS.md` and `Setups/order-dictionary.md`.
2. The target setup definition and its immediate parent/comparison setup when relevant.
3. The target setup's existing `Setups/reports/<setup-id>/` report, if present.
4. `PyAnsys/AGENTS.md` and the current diagnostic documentation:
   - `PyAnsys/docs/EWF_DPM_DIAGNOSTICS.md`
   - `PyAnsys/docs/EWF_DPM_TRANSCRIPT_CAPTURE.md` when DPM tracking is needed.

Make an applicability table before execution. Treat a model as applicable only when the setup definition and live audit support it.

| Setup evidence | Run | Do not infer |
|---|---|---|
| Any solved carrier case | carrier residual/flux/stability checks already supported by the case workflow | full separator validation from a scoped outlet metric alone |
| Active DPM injections | complete Particle Tracks Summary sweep for every live injection | DPM analysis for a case without an active injection branch |
| Active EWF film wall | `audit`, then `snapshot` on only the confirmed film walls | EWF on ordinary walls, or film analysis on `bottom` unless it is actually a film wall |
| EWF plus wall/global splash enabled | preserve absorbed and splashed event counts in DPM reporting | splash events as an extra terminal mass sink |
| Edge separation or particle stripping enabled | include the corresponding separated/stripped report terms | those mechanisms from a field-menu item alone |
| No EWF | carrier and/or DPM analysis only | film inventory, film drainage, EWF source, or EWF closure |
| No DPM | carrier and, when applicable, EWF analysis only | injection fate, splash parcel, or DPM mass-flow claims |

Record every omitted analysis as `Not applicable`, `Not available`, or `Deferred`, with the reason. Do not turn an omitted mechanism into a zero-valued result.

### Mandatory DPM coverage

When the live audit discovers one or more DPM injections, run a complete DPM
Particle Tracks Summary for every discovered injection by default. Do not omit
DPM merely because carrier or EWF checks are incomplete. The only exceptions
are when the user explicitly excludes DPM or explicitly limits the injection
selection; record that instruction and every omitted injection in the report.

If a DPM sweep fails its completion gate, preserve its partial artifacts and
report the sweep as incomplete. Never substitute missing fates or mass terms
with zero.

## Preflight and safe execution

Use the already-open Fluent session unless explicit case/data loading is required and authorised. Confirm the loaded case/data pair, setup ID, Fluent version, and server before interpreting any output.

### Mandatory live-analysis supervision rule

For **every** live Fluent analysis command or script (`audit`, `snapshot`,
`dpm`, `all`, carrier extraction, residual export, or another diagnostic
runner), retain the controlling shell and supervise its output for a minimum
of **320 seconds** from launch. Poll the console and expected output artifacts
at approximately 60-second intervals. Silence, a partial console return, or a
client-side return is not a completion signal: Fluent can continue reporting
or calculating after the Python client appears quiet.

The only permitted early exit is after verifying that the command has produced
its complete expected output set and has emitted no unresolved error. For
example, a snapshot requires its raw results plus snapshot, film-flux, and
bookkeeping payloads; a DPM sweep requires its full transcript and final
JSON/CSV bundle for every selected injection. If the client returns without
those artifacts, keep the supervising shell alive for the full 320 seconds.
After 320 seconds, continue one-minute polling until completion or an explicit
Fluent/client failure. Never start a second analysis command while the first
command remains incomplete.

```bash
/Users/shuheiyokkaichi/Developer/P4P_knowledgeWiki/PyAnsys/.venv/bin/python -c 'import sys; print(sys.executable)'
/Users/shuheiyokkaichi/Developer/P4P_knowledgeWiki/PyAnsys/.venv/bin/python PyAnsys/scripts/connection/check_connection.py --server-id 1
```

Use this explicit interpreter for every non-interactive command below. Do not
rely on a prior `source .venv/bin/activate`, because its shell state may not
survive a separate tool invocation.

Use the modular runner:

```bash
/Users/shuheiyokkaichi/Developer/P4P_knowledgeWiki/PyAnsys/.venv/bin/python PyAnsys/scripts/inspection/run_ewf_dpm_diagnostics.py --server-id 1 --mode audit
```

Start with `audit`. It is read-only and establishes live injection names, wall-film assignments, UDF overrides, and diagnostic limitations. Treat a missing Settings API path as a version/adapter finding, not proof that a model is disabled.

Run `snapshot` only for confirmed EWF cases. Supply the actual film walls and flux boundaries rather than assuming generic names:

```bash
/Users/shuheiyokkaichi/Developer/P4P_knowledgeWiki/PyAnsys/.venv/bin/python PyAnsys/scripts/inspection/run_ewf_dpm_diagnostics.py \
  --server-id 1 --mode snapshot --film-wall <film-wall> \
  --flux-boundary <boundary> --object-policy reuse
```

When the audit finds active DPM injections, this sweep is mandatory unless the
user explicitly excludes DPM or limits the injection set. Prefer stable
injection names only for an explicitly narrowed request; otherwise omit them
to track every live injection in diameter order:

```bash
/Users/shuheiyokkaichi/Developer/P4P_knowledgeWiki/PyAnsys/.venv/bin/python PyAnsys/scripts/inspection/run_ewf_dpm_diagnostics.py \
  --server-id 1 --mode dpm --order diameter-ascending --keep-going \
  --dpm-timeout-seconds 600 --transcript-quiet-seconds 1.0
```

Use `all` only after separate `audit`, `snapshot`, and `dpm` runs have each been validated for the specific Fluent version and case.

## DPM completion gate and wait rules

For every injection, require all of the following before submitting the next command:

1. A `number tracked = ...` line.
2. A `Mass Transfer Summary` section.
3. At least one parsed mass-transfer row.
4. A quiet transcript interval of at least `1.0 s`.
5. Immediate write of that injection's raw transcript and partial CSV/JSON state.

Use `--dpm-timeout-seconds 600` unless a documented case-specific limit is justified. A timeout, parser failure, or client error is a hard stop; do not queue the next injection merely because `--keep-going` was supplied.

Run a complete DPM sweep in a persistent terminal session. The universal
320-second live-analysis supervision rule applies in full to every sweep. Do
not reconnect, launch another tracker, or use another server while the
existing sweep remains incomplete. If the process itself ends before the final
transcript and output bundle exist, keep supervising for the 320-second
minimum and record an incomplete DPM execution rather than inferring missing
fates as zero.

Capture through `solver.transcript`, not Python `redirect_stdout`. Preserve:

- `dpm_live_transcript.txt`;
- one `dpm_raw/<index>-<injection>.txt` file per completed injection;
- partial outputs during the sweep;
- final `dpm_injection_summary.csv`, `dpm_zone_summary.csv`, `bookkeeping.json`, and `raw_results.json`.

## Interpret each analysis correctly

### Audit

Use `model_audit.json` to answer what Fluent was configured to do: active film walls, wall impingement/splash settings, optional EWF mechanisms, UDF overrides, and injection identity. It establishes scope; it does not prove the physical outcome.

### DPM

For each named injection, retain counts, fate-by-zone rows, elapsed-time statistics, mass-transfer rows, and the DPM closure:

```text
net injected mass flow
≈ escaped + trapped + absorbed + incomplete + other terminal fates
```

`splashed = ...` is a secondary-parcel/event diagnostic. If final fate totals include the generated secondary parcels, do not add their splash mass again to the terminal closure. Keep the EWF absorbed-event counter separate from the final `Absorbed` fate row; they can differ.

### EWF final-state snapshot

On confirmed film walls only, capture the final values and units for:

- maximum film Courant number;
- total film mass/inventory;
- maximum and area-weighted film thickness;
- Film DPM Mass Source;
- Film Outflow Mass and boundary Film Mass Flow Rate;
- average/maximum film velocity and velocity components;
- Film Stripped Mass only if stripping is active;
- Film Separated Mass only if edge separation is active.

Distinguish inventory/cumulative quantities in `kg` from source or flux rates in `kg/s`. A single final `.dat.h5` supports a snapshot, not a time-integrated EWF mass closure.

### EWF histories and closure

Create report-history files before continuing or rerunning the calculation. A defensible EWF closure needs a defined interval, initial/final inventory, and time-integrated source/inflow/outflow terms. Label a final-state-only result `bookkeeping-only`; do not claim conservation from mixed `kg` and `kg/s` values.

## Report the result

When a report is requested or analysis supplies new result evidence:

1. Use `Setups/reports/<setup-id>/results.md` unless the evidence genuinely needs a separate focused companion.
2. Link the report to exactly one setup definition. A comparison companion may name its parent/child scope explicitly, but must not replace individual setup reports.
3. Link to raw PyAnsys outputs; do not paste complete transcripts into the report.
4. Update `Setups/reports/index.md` when creating a new report file.
5. Preserve prior findings; append or add a dated evidence subsection instead of silently replacing a result from a different case/data checkpoint.

Read [the report structure reference](references/report-structure.md) before drafting or revising a report.

## Completion checklist

- Analysis scope follows the setup's actual active physics.
- Case/data identity, Fluent version, surfaces, and injection scope are recorded.
- DPM raw transcripts and final output bundle exist for every reported injection.
- EWF fields are reported only for active EWF mechanisms and with units/time-basis labels.
- Claims distinguish measured, derived, unresolved, and not-applicable items.
- The setup-linked report and reports index are updated only when report-facing evidence changed.
# Scope-specific DPM interpretation

For Purnanto-derived branches governed by the simplified-geometry scope, the report-facing DPM metric is observed escape through `steamoutlet`. Fluent's `Incomplete` fate remains available in raw artifacts but must not be elevated into an acceptance gate, blocker, recovery action, or mandatory next simulation. Analysis execution completeness (whether every requested transcript/CSV was produced) remains a separate operational requirement.
