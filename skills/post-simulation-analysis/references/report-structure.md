# Setup-linked post-simulation report structure

Use this structure for `Setups/reports/<setup-id>/results.md`. Keep it concise: link to generated CSV, JSON, and transcript files instead of duplicating them.

## 1. Setup link and evidence

State:

- setup definition link, setup ID, parent/comparison scope where relevant;
- case and data checkpoint names;
- Fluent version, server/session identity, analysis script revision or run label;
- evidence class: `diagnostic`, `partial`, `reported`, `not converged`, or another precise scope label;
- links to the output bundle and raw transcript/CSV files.

Do not call a run validated merely because an output exists.

## 2. Analysis applicability

Use a compact table to show what was actually applicable to this setup.

| Analysis | Status | Evidence/reason |
|---|---|---|
| Carrier residual/flux checks | completed / deferred / not available | checkpoint and monitor scope |
| DPM fate analysis | completed / not applicable | active injection branch and output link |
| EWF audit/snapshot | completed / not applicable | confirmed active film wall(s) |
| EWF history/closure | deferred / completed | interval and monitor availability |
| Splash / stripping / separation | active / inactive / not applicable | readback, not assumption |

Use `Not applicable` for physics absent from the setup. Use `Deferred` when the physics exists but its evidence has not yet been captured.

## 3. Carrier-field and numerical state

Include this when carrier results or convergence evidence exist:

- inlet/outlet phase fluxes and the exact scope of any efficiency/dryness metric;
- residual/monitor status;
- mass-balance limitation or convergence limitation;
- a clear distinction between a scoped diagnostic and full separator validation.

## 4. DPM results (only for active DPM)

Summarise one row per injection:

| Diameter | Injection | Net flow | Escaped | Trapped | Incomplete | Final absorbed | EWF absorbed events | Splash events | Closure residual |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|

Then state:

- terminal zones, especially escaped outlets and trapped walls;
- whether the final fate totals include generated secondary splash parcels;
- whether the mass-flow closure is within printed/reporting precision;
- limitations such as unresolved/incomplete particles.

Do not add splash events or represented secondary mass as a second sink when their later final fates are already included.

## 5. EWF final-state results (only for active EWF)

Report confirmed film walls and a table with exact Fluent units:

| Quantity | Reduction/scope | Value | Unit | Interpretation limit |
|---|---|---:|---|---|
| Film Courant Number | facet maximum | | | final-state numerical diagnostic only |
| Film Mass | sum of film walls | | kg | current inventory |
| Film Thickness | maximum / area-weighted average | | m | local versus distributed film |
| Film DPM Mass Source | sum | | kg/s | instantaneous/source basis |
| Film Outflow Mass | sum | | kg or Fluent-reported unit | identify whether cumulative |
| Film Mass Flow Rate | named boundary | | kg/s | preserve Fluent sign |
| Film Velocity | average / maximum / components | | m/s | direction needs spatial context |

Include stripped and separated quantities only when their models were active. Do not include an empty EWF section for a non-EWF case.

## 6. EWF history and bookkeeping (only when applicable)

If only one final checkpoint exists, state `bookkeeping-only` and name the missing terms. Do not combine inventory in `kg` directly with rates in `kg/s`.

For a defined interval, report:

```text
initial film inventory
+ integrated DPM-to-film source
+ integrated film inflow
= final film inventory
+ integrated film outflow
+ integrated stripping/separation when active
+ explicit unresolved residual
```

State the interval, monitor frequency, integration method, and the time basis used by Fluent.

## 7. Interpretation, limitations, and next action

Separate these three elements:

- **Measured:** direct values and files produced by Fluent.
- **Derived:** equations, ratios, or comparisons made from those values.
- **Unresolved:** incomplete trajectories, unclosed balance, missing history, inactive/unknown mechanism, or version-adapter limitation.

End with the smallest justified next action. Examples: continue the carrier solve, create histories before a rerun, compare to the named parent, repair a confirmed model mismatch, or keep the result diagnostic.
