# Split-Inlet Carrier-Field Mesh-Convergence Study

## 1. Purpose and status

Define the controlled carrier-field mesh-convergence study for the
post-replication spiral/split-inlet model.

- Parent setup: [07-pure-phase-split-actual-area.md](07-pure-phase-split-actual-area.md)
- Evidence status: `Planned / blocked at preflight`
- Primary study excludes DPM and Eulerian Wall Film (EWF).
- Only mesh resolution may vary between accepted coarse, medium, and fine runs.

## 2. Authoritative baseline and reconciliation

The strongest record of the actual split-inlet Fluent case is:

```text
C:\Users\syok443\Documents\Setup07extractor\FFF.1-2.cas.h5
C:\Users\syok443\Documents\Setup07extractor\FFF.1-2-02541.dat.h5
```

This identity is `Observed` in the machine-exported archive:
`../PyAnsys/cases/actual_setup_archives/07-pure-phase-split-actual-area-live-fff-1-2/`.

The archive verifies:

- split velocity inlets `liquidinlet` and `steaminlet`;
- steam pressure outlet `steamoutlet`;
- steady pressure-based Mixture model with two phases;
- vapor primary phase and liquid secondary phase;
- RNG k-epsilon with swirl-dominated flow enabled;
- Energy off and gravity on;
- both inlet velocities at `27.118 m/s`;
- liquid inlet liquid volume fraction `1`, steam inlet liquid volume fraction `0`.

The archive also contains active DPM and uses `Coupled` plus first-order
momentum, turbulence, and multiphase schemes. The intended setup-07 record uses
`SIMPLE`, second-order momentum/turbulence, and `QUICK` volume fraction where
available. Therefore the case file is authoritative for actual geometry and
live state, but the frozen carrier-study numerics require an explicit
preflight decision and readback. No production run may silently mix the two
definitions.

## 3. Geometry and operating condition

Intended geometry:

- spiral-inlet BOC separator;
- full inlet `0.724 m x 0.724 m`;
- outer-wall liquid strip width `0.006754 m`;
- inner/core steam width `0.717246 m`.

The inlet split orientation must be visually or geometrically verified before
the mesh ladder is accepted. Boundary names alone are insufficient.

Reference condition:

| Quantity | Value | Evidence |
|---|---:|---|
| Enthalpy condition | `1600 kJ/kg` | `Reported`, Purnanto Case 4 |
| Liquid target | `116.92 kg/s` | `Reported` |
| Steam target | `80.69 kg/s` | `Reported` |
| Shared inlet velocity | `27.118 m/s` | `Calculated`, setup 07 |
| Liquid-inlet turbulence intensity | `2.10999999%` | `User-specified`, setup 07 |
| Steam-inlet turbulence intensity | `2.10999999%` | `User-specified`, setup 07 |
| Liquid hydraulic diameter | `0.01338 m` | `Calculated`, setup 07 |
| Steam hydraulic diameter | `0.72061 m` | `Calculated`, setup 07 |

## 4. Frozen physics and numerics contract

The following must be identical by Fluent readback for all three meshes:

- pressure-based, steady solver;
- Mixture model with two phases;
- vapor primary phase and liquid secondary phase;
- identical materials, properties, phase interactions, and slip/drag settings;
- RNG k-epsilon, differential viscosity and swirl-dominated option as baseline;
- gravity and operating pressure;
- Energy off;
- all inlet/outlet/wall boundary values and backflow settings;
- initialization, solution controls, under-relaxation factors, discretization,
  pressure-velocity coupling, residual criteria, and monitor definitions;
- processor count.

DPM and EWF must be disabled or absent during initialization and iteration.
The preflight snapshot must state which numerics authority is selected:

1. `intended`: SIMPLE plus second-order/QUICK; or
2. `actual`: Coupled plus first-order.

The preferred report-facing choice is `intended`, because it matches the
documented setup lineage. It must first pass a same-mesh carrier stability
qualification. Changing numerics between mesh levels invalidates the study.

## 5. Mesh matrix

Use one geometry, topology method, local-control pattern, inflation policy, and
named-selection contract. Vary only the global resolution scale.

| Level | Nominal linear size relative to medium | Nominal cell count relative to medium |
|---|---:|---:|
| Coarse | `1.25` | `0.512` |
| Medium | `1.00` | `1.000` |
| Fine | `0.80` | `1.953` |

Actual characteristic size is:

```text
h = (fluid-domain volume / cell count)^(1/3)
```

Actual refinement ratios, not nominal labels, control Richardson/GCI analysis.
Existing `mesh-trial1` metadata around `1.4445M` cells are diagnostic only:
the repository has no three-mesh systematic ladder and some exports lose
required zones.

## 6. Acceptance criteria

### Preflight

- identical geometry, domain volume, boundary areas, zone roles, and face
  orientation;
- liquid strip resolved and confirmed on outer-wall side;
- no mesh-check errors;
- minimum orthogonal quality `>= 0.05` preferred; `0.01-0.05` requires an
  explicit diagnostic justification;
- active processor count captured from Fluent and unchanged.

### Iteration independence per mesh

- all residual histories preserved; residual reduction of at least three
  orders where attainable is a supporting check, not the sole criterion;
- primary integral-monitor drift `<= 0.5%` over the accepted final window;
- secondary velocity/swirl/recirculation-monitor drift `<= 1%`;
- complete mixture and phase mass imbalance `<= 0.5%` of total inlet,
  preferably `<= 0.2%`;
- no unresolved oscillation, monotonic inventory drift, or outlet-flow drift.

### Mesh independence

- medium-to-fine change `<= 1%` for pressure drop, steam-outlet vapor flow,
  steam-outlet liquid flow/carryover, and the primary velocity/swirl metric;
- medium-to-fine change `<= 2%` for secondary recirculation metrics;
- no reversal of qualitative flow topology.

Use Richardson extrapolation and GCI only for a systematic, monotonic
three-grid sequence with a usable observed order. Target fine-grid GCI is
`<= 2%` for primary metrics, with asymptotic-ratio consistency approximately
`0.8-1.2`. Otherwise report percentage changes and classify the study
`mesh sensitivity unresolved`.

## 7. Required outputs

Remote/local output root:

```text
split_inlet_mesh_convergence_20260729/
```

For each `coarse`, `medium`, and `fine`:

```text
<level>_preflight.json
<level>_settings_readback.json
<level>_mesh_quality.txt
<level>_mesh_metrics.json
<level>_transcript.trn
<level>_residual_history.csv
<level>_monitor_history.csv
<level>_mass_balance.csv
<level>_surface_metrics.csv
<level>_initialized.cas.h5
<level>_initialized.dat.h5
<level>_checkpoint_<iteration>.cas.h5
<level>_checkpoint_<iteration>.dat.h5
<level>_final.cas.h5
<level>_final.dat.h5
```

Cross-mesh outputs:

```text
mesh_matrix.csv
convergence_summary.csv
richardson_gci.csv
study_manifest.json
study_report.md
```

## 8. Current blockers

1. The configured Fluent endpoint `10.104.145.85:54904` timed out on
   `2026-07-29`; live version, case identity, and processor count are unknown.
2. No case/data/mesh binaries or systematic mesh ladder are stored locally.
3. Correct outer-liquid/inner-steam geometry and zone areas are not yet proven
   for the authoritative case.
4. `SIMPLE`/second-order intended numerics conflict with the actual live
   `Coupled`/first-order state.
5. The historical split-inlet solution lacks complete phase/mixture
   mass-balance and stable physical-monitor evidence.

Until these are resolved, results remain `Planned / blocked at preflight`.

