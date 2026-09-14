# Phase 7.1A baseline setup record — active Fluent model

## Record status

| Field | Value |
| --- | --- |
| Record type | Read-only baseline/reference fingerprint |
| Phase | Phase 7.1A — absorber convergence and solver stability |
| Audit date | 2026-09-11 |
| Runtime inspected | `student@10.0.0.5:55780` |
| Fluent version | 2025 R2 |
| Fluent state during audit | Connected; not advancing; no settings changed; no iterations run |
| Scientific role | Reference state for future one-delta steady comparisons |
| Run authorization | None. This file does not authorize a new run. |
| Phase context | [`CONTEXT.md`](CONTEXT.md) |

This record captures the settings actually read from the currently loaded
Fluent session. It is intentionally separate from a runnable `setup.md`:
the purpose is to establish what the model is, not to authorize or design the
first Phase 7.1A experiment.

The live Fluent Settings tree is the primary source for the values below.
Actual P7-E0 execution/readback records were used to reconcile the parent
lineage. Older setup prose and reusable helper recipes are treated as
secondary evidence where they disagree with live readback.

## Identity and confidence

- **Observed:** the reachable runtime is `student@10.0.0.5:55780` and Fluent
  reports version 2025 R2.
- **Missing Info:** the inspected Fluent Settings tree did not expose a
  definitive loaded case filename. The state is **Inferred** to be from the
  cold-continuation/recovery lineage because its autosave/report roots identify
  `CellZoneAbsorberColdContinuation` and
  `P7-E5-CZ-ABSORB-COLD-RAMP11692-CONT5000`.
- The lineage label is not a substitute for an independently proven paired
  case/data identity. A future runnable setup must load and verify such a
  pair before mutation.
- **Observed:** the live general settings, original boundary roles, model
  states, solution methods, and solution controls match the actual P7-E0
  execution/reference readback for the fields compared.

## Active solver and operating conditions

| Setting | Active value |
| --- | --- |
| Solver | Pressure-based |
| Time formulation | Steady |
| Velocity formulation | Absolute |
| Gravity | Enabled: `[0, -9.81, 0] m/s²` |
| Operating pressure | `0 Pa` |
| Operating density method | `minimum-phase-averaged` |
| Reference pressure method | `Connected and disconnected fluid zones` |
| Reference pressure location | `[0, 0, 0]` |
| Reference-value zone | `separator-purnanto` |
| Reference-value area | `1` |
| Reference density | `1.225 kg/m³` |
| Reference temperature | `288.16 K` |
| Reference velocity | `1 m/s` |
| Reference viscosity | `1.7894e-05 Pa·s` |

The `minimum-phase-averaged` operating-density method is an actual live
setting. Fluent's official multiphase guidance identifies it as the default
method and says it is generally suitable for most multiphase cases; it must
nevertheless be held fixed or explicitly declared as a delta in comparisons.
See [Steps for Using a Multiphase Model](https://ansyshelp.ansys.com/public/views/secured/corp/v251/en/flu_ug/flu_ug_sec_multiphase_setup.html).

## Active multiphase model

| Setting | Active value |
| --- | --- |
| Multiphase model | Mixture |
| Number of continuous phases | Two |
| Primary phase | `water-vapor-at-psep` |
| Secondary phase | `water-liquid-at-psep` |
| VOF formulation | Implicit |
| Interface type | Dispersed |
| VOF cutoff | `1e-06` |
| Implicit body force | False |
| Active multiphase Settings children | `model`, `vof_parameters`, `advanced_formulation`, `phases` |
| Mixture/phase equation | Enabled (`mp=true`) |
| Drift-related equation | Enabled (`drift=true`) |

The Mixture model's phase/slip framework is active. Fluent's documentation
states that the Mixture model computes secondary-phase slip velocities by
default. It describes Drift Force as an optional slip/drift treatment whose
inclusion can noticeably affect convergence. See [Setting Up the Mixture Model](https://ansyshelp.ansys.com/public/Views/Secured/corp/v251/en/flu_ug/flu_ug_sec_mphase_using_steps_mixture.html).

The `drift=true` readback is a solver-equation flag. It is not, by itself,
proof that an explicit interphase mass-transfer law is active; that question
is addressed in [Dormant or inactive branches](#dormant-or-inactive-branches).

## Active phase materials

### Phase 1 — vapor

| Property | Active value |
| --- | --- |
| Material | `water-vapor-at-psep` |
| Chemical formula | `h2o-sep` |
| Density | Constant `5.797433853149414 kg/m³` |
| Viscosity | Constant `1.520620025985409e-05 Pa·s` |

### Phase 2 — liquid

| Property | Active value |
| --- | --- |
| Material | `water-liquid-at-psep` |
| Chemical formula | `h2o-psep` |
| Density | Constant `881.2108764648438 kg/m³` |
| Viscosity | Constant `0.0001455440069548786 Pa·s` |

Other materials exist in the material database, but they were not identified
as the active continuous-phase assignments in this audit.

## Active turbulence model

| Setting | Active value |
| --- | --- |
| Viscous model | `k-epsilon` |
| Variant | RNG |
| RNG differential viscosity | True |
| RNG swirl-dominated-flow option | True |
| Near-wall treatment | Standard wall functions |
| Curvature correction | False |
| Kato-Launder production | False |
| Production limiter | False |
| Multiphase turbulence dispersion in relative velocity | False |
| Turbulence damping | False |
| Non-Newtonian turbulence | False |
| User-defined turbulent-viscosity function | None |

This exact turbulence block is the reference that the first Phase 7.1A
turbulence comparison must preserve except for its one declared closure delta.
In particular, the numerical order of the (k) equation is recorded in the
solution-methods section below and must not be silently changed during a
closure comparison.

## Active energy, species, and other physics state

| Physics branch | Active state |
| --- | --- |
| Energy | Off |
| Species | Off |
| Radiation | None |
| Acoustics | Off |
| Structure/system coupling | Off/disabled |
| UDM cell memory | `0` locations |
| UDM node memory | `0` locations |
| Zone-based UDM | False |
| Named expressions | None |

## Active cell zones and absorber source

| Cell zone | Active state |
| --- | --- |
| `separator-purnanto` | Fluid mixture zone; no cell-zone source |
| `p7-e5-lower-y010` | Separate fluid zone; lower absorber region |

### Lower absorber

| Absorber setting | Active value |
| --- | --- |
| Removed phase | Phase 2 only (`water-liquid-at-psep`) |
| Mass-source state | Enabled |
| Volumetric source | `-379.2377886984495 kg/(m³·s)` |
| Geometric volume | `0.3083026098250161 m³` |
| Integrated source | `-116.92 kg/s` |
| Direct phase-1 mass source | Off |
| Parent-zone source | Off |
| Mixture momentum source fields | Read as `-0.0` in the current cold-start state |
| Bottom boundary | Remains a stationary, no-slip wall |

The integrated value is verified by the source-density/volume product:

```text
-379.2377886984495 kg/(m³·s) × 0.3083026098250161 m³
= -116.92 kg/s
```

This is the active liquid-removal mechanism in the current case. It is a
localized phase-2 cell-zone sink and is not a bottom outlet, porous opening,
explicit phase-interaction mass-transfer law, DPM sink, or vapor sink.

The lower-zone mixture momentum source reading of `-0.0` is an observed value,
not a second hidden mechanism. The matched source law uses the lower-zone
phase-2 velocity basis; in this cold-start lineage that basis is effectively
zero. Earlier G100 states had nonzero momentum-source values because their
lower-zone liquid/velocity basis was nonzero.

### Cell registers

The following registers exist as geometric selections. They are not, by
themselves, active source regions:

| Register | Selection | Display colour |
| --- | --- | --- |
| `p7_e5_cz_lower_y010` | `0 ≤ y ≤ 0.1` | Black |
| `p7_e5_absorb_adjacent_y030` | `0.1 ≤ y ≤ 0.3` | Blue |
| `p7_e5_absorb_broad_y050` | `0 ≤ y ≤ 0.5` | Cyan |

## Active boundary conditions

### Continuous-phase flow boundaries

| Boundary | Active setting |
| --- | --- |
| `liquidinlet` | Mass-flow inlet; normal direction; gauge/supersonic pressure field `1,140,000 Pa`; phase-2 mass flow `116.92 kg/s`; phase-1 mass flow `0`; turbulence intensity `0.0211`; hydraulic diameter `0.01338 m` |
| `steaminlet` | Mass-flow inlet; normal direction; gauge/supersonic pressure field `1,140,000 Pa`; phase-1 mass flow `80.69 kg/s`; phase-2 mass flow `0`; turbulence intensity `0.0211`; hydraulic diameter `0.72061 m` |
| `steamoutlet` | Pressure outlet; gauge pressure `1,120,000 Pa`; Total Pressure backflow specification; normal direction; backflow intensity `0.0211`; backflow hydraulic diameter `0.875936 m`; phase-2 backflow volume fraction `0` |

### Wall boundaries

| Boundary | Active setting |
| --- | --- |
| `bottom` | Stationary, no-slip wall; roughness height `0`; roughness constant `0.5` |
| `wall` | Stationary, no-slip wall; roughness height `0`; roughness constant `0.5` |
| `separator-purnanto:1` | Stationary, no-slip wall; roughness height `0`; roughness constant `0.5` |
| `wall:004` | Stationary, no-slip wall; roughness height `0`; roughness constant `0.5` |

## Active solution methods

| Equation/control | Active value |
| --- | --- |
| Pressure–velocity coupling | SIMPLE |
| N-phase solve | False |
| Gradient | Green-Gauss node-based |
| Pressure | PRESTO! |
| Momentum | Second-order upwind |
| Turbulent kinetic energy (k) | First-order upwind |
| Dissipation ε | Second-order upwind |
| Multiphase/volume fraction | QUICK |
| Pseudo-time segregated solver | Off |
| High-order term relaxation | Disabled; factor `0.25`; standard mode |
| Implicit body-force expert option | False |
| Expert velocity formulation | Absolute |
| Physical velocity formulation | False |
| Rhie-Chow flux disabled | False |
| Expert PRESTO pressure flag | False; main pressure scheme is still read as `presto!` |
| First-to-second-order blending | `1.0` |

### Multiphase numerical options

| Option | Active value |
| --- | --- |
| Compressible enhanced numerics | True |
| Alternate boundary-condition formulation | False |
| Viscosity averaging | False |
| Low-order Rhie-Chow | False |
| Recommended default controls | False |
| Revert pre-r20.1 defaults | False |
| VOF high-order Rhie-Chow | False |
| VOF hybrid treatment | False |
| Unstructured-variable PRESTO | False |
| Warped-face gradient correction | False |
| NB-gradient boundary treatment | `modified-boundary-treatment` |

Fluent's official guidance describes enhanced compressible numerics as a
stability-oriented option for compressible multiphase calculations. It is
active in this baseline and must not be silently disabled in a comparison.
See [Steps for Using a Multiphase Model](https://ansyshelp.ansys.com/public/views/secured/corp/v251/en/flu_ug/flu_ug_sec_multiphase_setup.html).

## Active solution controls

### Under-relaxation factors

| Quantity | Active value |
| --- | ---: |
| Pressure | `0.3` |
| Momentum | `0.7` |
| Turbulent kinetic energy (k) | `0.8` |
| Dissipation ε | `0.8` |
| Mixture/phase | `0.40000000596` |
| Drift | `0.1` |
| Body force | `1.0` |
| Density | `1.0` |
| Turbulent viscosity | `1.0` |

### Equation switches

| Equation | Active state |
| --- | --- |
| Flow | True |
| (k)-epsilon | True |
| Mixture/phase | True |
| Drift | True |

### Solver limits

| Limit | Active value |
| --- | ---: |
| Minimum pressure | `1` |
| Maximum pressure | `5e10` |
| Minimum turbulent kinetic energy | `1e-14` |
| Minimum epsilon | `1e-20` |
| Maximum turbulent-viscosity ratio | `100000` |
| Minimum volume-fraction matrix solution | `1e-8` |

### AMG and linear-solver controls

| Control | Active value |
| --- | --- |
| (k), epsilon, momentum, and mixture cycle | Flexible-cycle |
| (k), epsilon, momentum, and mixture termination | `0.1` |
| (k), epsilon, momentum, and mixture residual-reduction tolerance | `0.7` |
| Pressure cycle | V-cycle |
| Pressure termination | `0.1` |
| Pressure stabilization | Off |
| Scalar pre/post sweeps | `0 / 1` |
| Maximum cycle | `30` |
| Conservative coarsening | True |
| Aggressive coarsening | False |
| Laplace coarsening | False |
| Smoother | Gauss-Seidel |
| Flexible-cycle sweeps | `2` |
| Maximum fine relaxations | `30` |
| Coarse relaxations | `50` |
| Global relaxation method | Gauss-Seidel |

### Advanced solver controls

| Control | Active value |
| --- | --- |
| Spatial discretization limiter | Default |
| Limiter topology | Cell-to-limiting-cell-to-face |
| Limiter filter | False |
| Linearized mass-transfer UDF capability switch | True |
| Singhal cavitation switch | False |
| Save cell residuals | False |
| Keep temporary memory | False |
| Allow all discretization schemes | False |

## Initialization and runtime controls

| Setting | Readback |
| --- | --- |
| Initialization type | Hybrid |
| Initialization reference frame | Relative |
| Hybrid initialization iterations | `10` |
| Explicit initialization URF | `[1.0, 1.0]` |
| Initial pressure | False |
| External aero initialization | False |
| Constant velocity initialization | False |
| Averaged turbulent parameters | True |
| Reconstructed-interface VOF smoothing option | True (stored option) |
| Volumetric VOF smoothing option | True (stored option) |
| VOF smoothing relaxation | `0.5` (stored option) |
| Reporting interval | `1` |
| Profile update interval | `1` |
| Data sampling | Disabled |

The stored VOF smoothing options are configuration values. They are not proof
that a patch or field-reset operation was executed in this audit. Patching or
resetting remains outside the autonomous Phase 7.1A route.

### Autosave/readback state

- Case autosave frequency: each time.
- Data autosave frequency: every `100` iterations.
- Retain most recent: `6` pairs.
- Current remote autosave root read from the loaded branch:

  `C:\Users\Shuhei Yokkaichi\Documents\FluentRuns\Phase07\CellZoneAbsorberColdContinuation\20260910T211158Z\P7-E5-CZ-ABSORB-COLD-RAMP11692-CONT5000\checkpoint-%i`

This root is runtime evidence, not a substitute for a durable `run-paths.yaml`
or a proven case/data identity.

## Active residual and reporting settings

| Residual equation | Criterion |
| --- | ---: |
| Continuity | `1e-4` |
| X velocity | `1e-3` |
| Y velocity | `1e-3` |
| Z velocity | `1e-3` |
| (k) | `1e-3` |
| Epsilon | `1e-3` |
| Phase-2 volume fraction | `1e-3` |

Additional residual-monitor settings:

- Scaled residuals: enabled.
- Local scaling: disabled.
- Criteria type: absolute.
- Residual print: enabled.
- Residual plot: enabled.
- Native monitor save/display count readback: `4100`.
- Seven physical equation groups are checked: continuity, three momentum
  components, (k), epsilon, and phase-2 volume fraction.

The current monitor tree contains approximately 99 curve styles/objects,
which appears to be inherited monitor configuration. That count must not be
interpreted as 99 independently active physical equations.

## Dormant or inactive branches

These items were present as Settings paths or objects but were not proven to
be active contributors to the current carrier solution.

| Branch | Readback | Classification |
| --- | --- | --- |
| Explicit multiphase Phase Interaction | Inactive; active multiphase children exclude `phase_interaction` | Not active/proven |
| `linearized_mass_transfer_udf` | True | Configured capability switch, dormant without an active Phase Interaction/UDF mechanism |
| DPM continuous-phase interaction | False | Not coupled to carrier equations |
| DPM injection objects | Six objects; each total flow `1e-20 kg/s` | Trace/dormant objects |
| DPM boundary fates | Inlets/outlet escape; walls reflect; bottom trap | DPM fate configuration, not the Eulerian absorber |
| Curvature correction | False | Not active |
| Kato-Launder production | False | Not active |
| Turbulence production limiter | False | Not active |
| Turbulence damping | False | Not active |
| Multiphase turbulence dispersion | False | Not active |
| Perforated-wall setup | Method `None` | Not active |
| Turbo-specific non-reflecting treatment | False | Not active |
| General non-reflecting values | Sigma `0.15`; sigma2 `5.0` | Stored general branch values, not an active special outlet treatment |
| Cavitation | No active model proven; Singhal switch false | Not active/proven |
| Boiling/phase-change branches | No active energy or phase-change model proven | Not active/proven |
| Surface-tension branch | No active surface-tension mechanism proven in this readback | Not active/proven |

Fluent documents `DEFINE_LINEARIZED_MASS_TRANSFER` as a user-defined
interphase mass-transfer mechanism coupled to the flow equations. That is a
different mechanism from the current lower-zone phase-2 source. See the
[Fluent Customization Manual](https://ansyshelp.ansys.com/public/Views/Secured/corp/v251/en/pdf/Ansys_Fluent_UDF_Manual.pdf).

## Parent and documentation reconciliation

| Source | Finding | Confidence/use |
| --- | --- | --- |
| Current live Fluent readback | Active reference settings documented in this file | Primary evidence for the loaded state |
| Actual P7-E0 final readback | Matches the current live model, original boundaries, methods, and controls for the compared fields | Strong lineage support |
| Older E0 source candidate | Uses the same major carrier model but contains finite DPM injection payloads | Historical source evidence; not current execution truth |
| Actual E0 execution manifests | Six DPM injections at trace `1e-20 kg/s`; DPM interaction off | Strong evidence for the executed branch |
| `setup_carrier.py` helper | Requests `mixture-averaged` operating density and second-order (k) | Implementation intention; not the current live-state authority |
| Older setup prose | Does not enumerate every exact leaf setting | Insufficient by itself for reconstruction |

The two most consequential drift points are:

1. The live/actual E0 state uses `minimum-phase-averaged`, while the helper
   recipe requests `mixture-averaged`.
2. The live/actual E0 state uses first-order (k), while the helper recipe
   requests second-order (k).

Neither difference should be silently corrected before the first Phase 7.1A
comparison. If either is changed, it must be the declared controlled delta of
its own setup.

## Baseline lock for future setup design

Until a new setup explicitly declares otherwise, the following are frozen:

- pressure-based steady solver;
- Mixture, implicit/dispersed two-phase model;
- phase 1 vapor and phase 2 liquid material assignments;
- RNG (k)-epsilon, including differential viscosity and swirl options;
- standard wall functions;
- energy and species off;
- gravity and operating conditions;
- lower `p7-e5-lower-y010` phase-2-only absorber at integrated
  `116.92 kg/s`;
- zero direct phase-1 source and no parent-zone source;
- bottom as a stationary no-slip wall;
- current inlet and steam-outlet boundary roles and phase routing;
- SIMPLE, Green-Gauss node-based gradients, PRESTO!, second-order momentum,
  first-order (k), second-order epsilon, and QUICK phase fraction;
- current URFs, equation limits, AMG controls, enhanced compressible
  numerics, and residual criteria; and
- DPM continuous-phase interaction off with the current trace injection state.

The first Phase 7.1A turbulence setup may change only the selected turbulence
closure after its exact alternative and paired parent case/data identity have
been verified. This baseline record does not itself approve that setup.

