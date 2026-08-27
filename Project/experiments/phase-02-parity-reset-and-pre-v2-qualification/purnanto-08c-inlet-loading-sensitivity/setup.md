> **Retired source:** Setups/past/reported/08c-purnanto-parity-inlet-velocity-sensitivity.md
> **Migration note:** Historical wording, evidence status, and uncertainty labels are preserved; this Project copy is not a reinterpretation. Machine-generated artifacts remain with their original external owners; the retired written source is recoverable from Git history.

# Purnanto Parity Inlet-Velocity Sensitivity

## Setup metadata

| Field | Value |
|---|---|
| Setup ID | `08c` |
| Lifecycle | `reported` |
| Role | inlet-loading sensitivity branch |
| Parent setup | [08b](../purnanto-08b-parity-split-inlet/setup.md) |
| Evidence-use label | preliminary diagnostic comparison; acceptance pending |
| Outcome | needs follow-up |
| Linked report | [08 family comparison](velocity-family-comparison.md) |

## 1. Purpose

Define setup `08c` as the immediate child branch after setup `08b`.

This branch exists to test the supervisor-directed next question:

- if the inlet velocity is changed, how does separator efficiency respond?
- can that sensitivity be isolated without changing the inlet thermodynamic state definition?

Setup `08c` must stay tightly controlled:

- inherit the accepted `08b` carrier-field setup as the parent authority;
- change inlet loading only through the inlet velocity / mass-throughput definition;
- keep the inlet state basis tied to the same enthalpy assumption used for setup `08b`;
- treat this as a loading sensitivity branch, not as a fresh parity rebuild.

Primary authority:

- [08b-purnanto-parity-split-inlet-rebuild.md](../purnanto-08b-parity-split-inlet/setup.md)
- Historical setup ordering is recoverable from Git history.
- [Project state and next decision](../../../index.md)

## 2. Setup Identity

| Item | Value |
|---|---|
| Setup order | `08c` |
| Branch role | inlet-velocity sensitivity child of `08b` |
| Parent authority | accepted or working `08b` parity branch |
| Geometry label | `purnanto` |
| Continuous-phase intent | keep the `08b` continuous model stack unchanged |
| Inlet representation | same split-inlet topology as `08b` |
| Main branch variable | inlet velocity, implemented through changed inlet mass loading on the same inlet areas |
| Thermodynamic rule | keep inlet specific enthalpy basis fixed unless a later branch explicitly studies enthalpy sensitivity |
| DPM status | hold off unless the carrier sensitivity first looks stable and interpretable |

Evidence labels used in this report:

- `Observed`: taken from the loaded Purnanto case/data audit.
- `Retained`: inherited intentionally from setup `08b`.
- `User-specified`: deliberate project change for this branch.
- `Assumed`: temporary placeholder until better evidence is available.
- `Uncertain`: unresolved item that must not be treated as settled.

## 3. Parent-Child Rule

Setup `08c` is not allowed to reopen the broad parity question already handled by `08b`.

Treat setup `08b` as fixing:

- solver family and numerics stack;
- multiphase model choice;
- turbulence model choice;
- materials and phase definitions;
- gravity, operating pressure, and outlet settings;
- inlet split topology and inlet-area definition.

Setup `08c` changes only the loading level imposed at the split inlet.

## 4. Inlet Velocity Interpretation Rule

For the current split-inlet `Mass-Flow Inlet` branch, changing inlet velocity means:

- keep the inlet areas fixed;
- change the imposed inlet mass flow rates;
- allow the superficial inlet velocities to move as a consequence of the changed mass loading on those same areas.

This branch therefore treats inlet velocity sensitivity and inlet mass-throughput sensitivity as the same controlled test on the current mesh branch.

`User-specified`:

- do not introduce a new `Velocity Inlet` boundary type just to perform this sweep;
- stay with the split `Mass-Flow Inlet` implementation used by setup `08b` unless a later dedicated branch tests boundary-type sensitivity.

## 5. Enthalpy Rule

Supervisor instruction interpreted for this branch:

- keep the inlet **specific enthalpy** basis fixed;
- vary the inlet **flow rate / velocity**;
- observe how separator efficiency changes under different loading.

Working interpretation:

- changing mass flow rate does **not** automatically require changing the inlet specific enthalpy;
- what changes is the **energy flow rate** carried into the separator, because `energy rate = mass flow rate x specific enthalpy`;
- the inlet thermodynamic state can still be held constant while throughput changes.

For this project branch that means:

- keep the same enthalpy-derived steam/water state basis used for setup `08b`;
- keep the same phase-definition logic at the inlet unless a later branch explicitly studies different inlet enthalpy values;
- do not silently recalculate a new inlet enthalpy for each velocity point.

`Uncertain`:

- if the supervisor later wants the inlet phase fractions recalculated from a different well-state assumption at each flow point, that becomes a separate enthalpy-sensitivity or well-condition-sensitivity branch, not this one.

## 6. Controlled Variable Set

### Held fixed from setup `08b`

- geometry;
- mesh branch;
- operating pressure;
- gravity;
- turbulence and multiphase model stack;
- outlet boundary settings;
- inlet area split;
- inlet state basis tied to the same enthalpy assumption as `08b`.

### Varied in setup `08c`

- total inlet mass flow rate;
- corresponding split-zone mass flow allocation;
- resulting split-zone inlet velocities;
- resulting separator efficiency metrics.

### Default split rule

Unless the next calculation proves a different supervisor instruction:

- preserve the same steam-side / liquid-side split logic used in setup `08b`;
- scale both inlet zones together so the loading change is the main test variable;
- avoid changing both loading and inlet composition logic in the same branch.

## 7. Suggested Test Matrix

Use the mass-flow-inlet form of the branch, but choose the mass flows so they correspond to the target inlet velocities you want to test on the unchanged split areas.

Current working matrix:

1. low-end sensitivity case = `20.00 m/s`
2. current reference case = approximately `08b` loading, with the existing split areas and target mass flows
3. high-end sensitivity case = `32.14 m/s`

Evidence note:

- `Observed`: `32.14 m/s` is recorded as the reference velocity in the live Purnanto audit.
- `User-specified`: `20.00 m/s` is currently treated as the low-end sensitivity point requested for this branch.
- `Uncertain`: if you later confirm that the paper used `32.00 m/s` rather than `32.14 m/s`, update the high-end point explicitly instead of rounding silently.

### 7.1 Equivalent Mass-Flow Targets For The Velocity Points

Using the current split areas:

- liquid-side area `A_liquid = 0.0048896 m2`
- steam-side area `A_steam = 0.5192864 m2`

and the live-audit phase densities:

- liquid density `rho_liquid = 881.21088 kg/m3`
- vapor density `rho_vapor = 5.7974339 kg/m3`

the equivalent split-zone mass-flow targets are:

| Target velocity | Liquid inlet mass flow | Steam/vapor inlet mass flow | Total inlet mass flow |
|---:|---:|---:|---:|
| `20.00 m/s` | `86.18 kg/s` | `60.21 kg/s` | `146.39 kg/s` |
| `27.118 m/s` | `116.85 kg/s` | `81.64 kg/s` | `198.48 kg/s` |
| `32.14 m/s` | `138.48 kg/s` | `96.76 kg/s` | `235.24 kg/s` |

Interpretation rule:

- keep the same inlet areas;
- keep the same enthalpy basis;
- impose these mass-flow values through the two split `Mass-Flow Inlet` boundaries;
- treat the resulting nominal inlet velocities as the branch labels for comparison.

### 7.2 Generated Case-Only Artifacts

`Observed` / `User-specified`, generated through PyFluent without initialization or iterations:

| Case label | Remote case file | Liquid inlet readback | Steam/vapor inlet readback |
|---|---|---:|---:|
| `08c-v20p00` | `C:\Users\syok443\Documents\TwoPhaseInletV2(Purnanto)\TwoPhaseInletV2(Purnanto)-08c-v20p00.cas.h5` | `86.18 kg/s` on `liquidinlet` `phase-2` | `60.21 kg/s` on `steaminlet` `phase-1` |
| `08c-v32p14` | `C:\Users\syok443\Documents\TwoPhaseInletV2(Purnanto)\TwoPhaseInletV2(Purnanto)-08c-v32p14.cas.h5` | `138.48 kg/s` on `liquidinlet` `phase-2` | `96.76 kg/s` on `steaminlet` `phase-1` |

Build notes:

- source parent case: `C:\Users\syok443\Documents\TwoPhaseInletV2(Purnanto)\TwoPhaseInletV2(Purnanto).cas.h5`;
- script: `../../../PyAnsys/scripts/setup/setup08c_purnanto_velocity_sensitivity_cases.py`;
- local readback summary: `../../../PyAnsys/output/setup08c_velocity_sensitivity_cases_summary.json`;
- opposite split-inlet phase mass-flow readbacks were `0.0 kg/s` for both generated cases.

### 7.3 Reference-Case Caution

The current `08b` branch target is still documented as:

- vapor `80.69 kg/s`
- liquid `116.92 kg/s`

This means the active `08b` reference case is tied to the project target mass flows first, not to the live-audit density-derived `27.118 m/s` or `27.11 m/s` value exactly.

For `08c`:

- use the existing `08b` case as the practical reference point;
- treat `20.00 m/s` and `32.14 m/s` as the main sensitivity endpoints;
- do not relabel the parent `08b` branch as a strict `27.118 m/s` case unless the inlet-property basis is reconciled explicitly.

## 8. Metrics To Compare

Primary comparison metrics:

- steam-outlet liquid carryover;
- steam-line carryover efficiency;
- outlet vapor recovery;
- pressure drop;
- inlet-to-outlet phase mass-balance trend;
- residual and monitor stability.

Useful secondary diagnostics:

- tangential velocity pattern near the separator core;
- visible shift in recirculation structure;
- outlet backflow tendency;
- whether higher loading destabilizes the separator field before efficiency changes can be trusted.

## 9. Acceptance Gate

Treat setup `08c` as useful only if:

1. the parent `08b` settings are inherited without accidental drift;
2. each loading point is documented with the actual imposed split-zone mass flows and resulting velocities;
3. the enthalpy basis is explicitly stated as fixed across the sweep;
4. efficiency trends are interpreted only after basic residual and monitor behavior is acceptable;
5. any degraded performance is attributed first to changed loading, not to uncontrolled setup changes.

## 10. Immediate Build Questions

Use setup `08c` to answer:

1. Does separator efficiency degrade as inlet velocity/loading increases on the `08b` parity branch?
2. Is there a roughly stable loading range where the separator response stays acceptable?
3. Does higher inlet velocity mainly affect carryover, pressure drop, monitor stability, or all three?
4. Is an inlet-velocity sweep strong enough to justify a later enthalpy-sensitivity branch, or is loading sensitivity already the dominant signal?

## 11. Branch Position In The Roadmap

Interpret setup `08c` as:

- a child sensitivity branch grown from the `08b` parity-reset parent;
- earlier than the parked `09` DPM sensitivity family;
- still part of the continuous-phase loading study, not yet the next DPM escalation.

This means:

- setup `08b` remains the parent parity authority;
- setup `08c` becomes the next loading-sensitivity step;
- setup family `09` should stay parked until the project decides whether inlet-loading sensitivity or DPM uncertainty is the more important next report-facing result.
