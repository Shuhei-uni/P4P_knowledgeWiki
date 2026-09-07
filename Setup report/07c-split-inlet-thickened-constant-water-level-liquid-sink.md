# Split-Inlet Thickened Constant-Water-Level Liquid Sink

## 1. Purpose and status

Setup `07c` is a diagnostic child of setup `07b`. It tests whether the failed
one-cell constant-water-level abstraction was limited mainly by the thickness
of its bottom-local removal zone.

- Parent: [07b-split-inlet-constant-water-level-liquid-sink.md](07b-split-inlet-constant-water-level-liquid-sink.md)
- Carrier lineage: [07-pure-phase-split-actual-area.md](07-pure-phase-split-actual-area.md)
- Triggering mesh study: [07a-split-inlet-carrier-mesh-convergence.md](07a-split-inlet-carrier-mesh-convergence.md)
- Study ID: `split_inlet_thickened_water_level_sink_20260808`
- Run label: `mesh-900k_band0p140165_tau0p100_v1`
- Implementation status: `Accepted` for clean-origin reconstruction, mask
  creation, compiled/hooked source persistence and supervised checkpointing.
- Scientific status: `Completed diagnostic / unresolved`. Zero acceptance
  windows passed before the 2,000-iteration full-strength limit.
- DPM status: off throughout; no injections were updated or tracked.

The test changed only the source-mask thickness relative to setup `07b`. It
did not change the physical geometry, mesh, materials, carrier models,
boundary conditions, solver controls, sink time scale or initialization rule.

## 2. Controlled baseline

The formal run started from clean original:

```text
C:\Users\qtra338\Documents\Mesh study\Meshes\mesh-900k.msh
```

with SHA-256
`353bf13ca13d4a32a4cd505d991e64b1ea6f306cc3e8add438859b9117a5afef`.
It applied:

```text
C:\Users\qtra338\Documents\Mesh study\Source\mesh_study_settings.set
```

and reproduced normalized carrier fingerprint
`424a9bf02bbd78060dee3a2874103e5149aa4aa555a09e2add69da4d2a0158c5`.
No saved accumulated solution data were loaded. The field was fresh Hybrid
Initialized after settings and source readback.

Fluent readback confirmed:

- Fluent 2024 R2 with 16 partitions;
- 5,335,623 cells, 10,743,466 faces and 923,066 nodes;
- domain volume `22.65842 m3` and characteristic size `0.01619378 m`;
- minimum orthogonal quality `0.202194`, maximum aspect ratio `20.1267`, and
  no negative cell volumes or mesh-check errors;
- steady pressure-based Mixture, vapor primary and liquid secondary;
- phase 1 `water-vapor-at-psep`, phase 2 `water-liquid-at-psep`;
- RNG k-epsilon, gravity `(0,-9.81,0) m/s2`, Energy off;
- SIMPLE/PRESTO! with inherited discretization and URFs;
- liquid/vapor inlets `116.92/80.69 kg/s` and steam-outlet gauge pressure
  `1,120,000 Pa`;
- `bottom` zone ID `50059` as a stationary no-slip wall with area
  `3.1649776 m2` at `y=-6.441 m`;
- `steamoutlet` as the only pressure outlet;
- DPM interaction off.

Generic `wall` import warnings were recorded but did not involve any required
zone. Required zone names/types were unambiguous after settings transfer.

## 3. Source formulation and only intended change

The setup-07b liquid and carried-momentum equations were retained:

```text
S_l = -rho_l * alpha_l * R / tau
S_mi = S_l * u_mi
```

with `tau=0.1 s`, liquid mass hooked only to phase 2, mixture momentum hooked
in x/y/z, and no vapor or energy source.

The sole sensitivity variable was the mask thickness above `bottom`:

| Property | Setup 07b | Setup 07c |
|---|---:|---:|
| Mask concept | one bottom-adjacent cell layer | fixed bottom-local band |
| Thickness | about `0.00876033 m` equivalent | `0.1401652536 m` |
| Nominal layers | 1 | 16 |
| Marked cells | 5,438 | 92,058 |
| Marked volume | `0.027726243 m3` | `0.44378932 m3` |

The 07c mask spans the complete bottom-local cell band between approximately
`y=-6.43746` and `-6.30084 m`; it is not restricted to a small surface patch.

The compiled source is
`PyAnsys/udf/constant_water_level_thick_sink.c`, SHA-256
`b336651c7ab1da476b61325e8bdd3e2fa184258c9e6dd23bc87db4c15e26def9`,
and the Fluent library is `lib07c_cwl_b336651c7a_r2`.

## 4. Execution contract and recovery

The controller used a guarded 1,000-iteration ramp:

```text
R=0.025 / 100 iterations
R=0.05  / 100
R=0.10  / 150
R=0.25  / 150
R=0.50  / 250
R=0.75  / 250
```

It then used `R=1` in 250-iteration blocks for at most 2,000 iterations. Early
completion required two consecutive passing 500-iteration windows. Primary
monitor drift had to be `<=0.5%`, velocity/vorticity drift `<=1%`, phase and
mixture imbalance `<=0.5%`, all residuals non-growing and final scaled
residuals `<=1e-3`.

The initial controller safely false-stopped after R1 = 250 because the
startup-change guard compared a full-strength sample against the last ramp
sample. The state was preserved as a separate pair. A recovery controller
reloaded it, verified actual versus recorded counts, saved a separate resume
start and continued without overwriting any evidence.

The completed calculation contains 3,000 solver iterations: 1,000 ramp plus
2,000 full-strength. It stopped at the budget limit with zero accepted
windows. The ramp was reset to zero before the separate final checkpoint.

## 5. Results

At R1 = 2000:

| Quantity | Result |
|---|---:|
| Sink magnitude | `22.4882 kg/s` |
| Sink/liquid-inlet fraction | `19.23%` |
| Domain liquid inventory | `71.7785 kg` |
| Bottom-band liquid inventory | `2.24882 kg` |
| Pressure drop | `27.1372 kPa` |
| Steam-outlet vapor | `81.2960 kg/s` out |
| Steam-outlet liquid | `0.000102861 kg/s` out |
| Carrier quality | `99.99987%` (`trend only`) |
| Source-inclusive liquid imbalance | `80.7661%` |
| Source-inclusive mixture imbalance | `47.4802%` |
| Outlet/domain velocity | `45.6588 / 30.7530 m/s` |
| Domain vorticity | `82.4945 s^-1` |
| Continuity / liquid-VF residual | `0.191551 / 6.9815e-4` |

Final-500 drift was pressure `8.53%`, sink `29.99%`, domain liquid inventory
`16.93%`, vapor outlet `0.0362%`, outlet velocity `4.24%`, domain velocity
`6.78%` and vorticity `0.860%`. The residual series were not explosively
growing, but continuity failed the absolute residual gate by two orders of
magnitude. Pressure, inventory and velocity remained strongly iteration
dependent.

At equal full-strength counts, 07c increased sink magnitude by `15.44x` at
R1 = 1000, `16.20x` at 1500 and `12.93x` at 2000 relative to 07b. This proves
that the thicker zone changes capacity, but the endpoint sink still removed
only `19.23%` of liquid inflow and did not stabilize the domain.

## 6. Mass-balance analysis correction

The raw controller's `liquid_source_augmented_*` field must not be cited. The
phase-2 Fluent flux-report `Net` already includes the liquid cell-zone source,
so adding the sink again double-counted it. The invalid raw 07c value is
`61.5322%`; the corrected source-inclusive liquid imbalance is the reported
phase-2 `liquid_imbalance_percent`, `80.7661%`.

The mixture report equals the selected-boundary net and therefore still needs
one source augmentation. The recorded 07c source-inclusive mixture imbalance,
`47.4802%`, remains valid.

The same liquid-only correction applies to setup 07b: `84.2956%` is replaced
by `91.1909%`. Neither classification changes because all corrected balances
remain far above `0.5%` and the physical-monitor/residual gates also failed.
Raw evidence remains unchanged; see `analysis_correction.json` beside the 07c
qualification manifest.

## 7. Evidence and checkpoints

Machine-readable and report evidence:

- [QUALIFICATION_RESULT.md](../PyAnsys/output/split_inlet_thickened_water_level_sink_20260808/mesh-900k_band0p140165_tau0p100_v1/QUALIFICATION_RESULT.md)
- [qualification_manifest.json](../PyAnsys/output/split_inlet_thickened_water_level_sink_20260808/mesh-900k_band0p140165_tau0p100_v1/qualification_manifest.json)
- [analysis_correction.json](../PyAnsys/output/split_inlet_thickened_water_level_sink_20260808/mesh-900k_band0p140165_tau0p100_v1/analysis_correction.json)
- physical-monitor, mass-balance and residual CSVs;
- mesh-quality report;
- preserved failed-attempt manifests and remote transcripts.

Verified separate remote case/data include:

```text
ramp_complete_cumulative1000_r0p75.cas.h5/.dat.h5
diagnostic_stop_r1_250_ramp_reset0.cas.h5/.dat.h5
resume_start_r1_250_cumulative1250_ramp0.cas.h5/.dat.h5
r1_iter1000_cumulative2000_resume.cas.h5/.dat.h5
r1_iter2000_cumulative3000_resume.cas.h5/.dat.h5
diagnostic_resume_r1_2000_ramp_reset0.cas.h5/.dat.h5
```

## 8. Meeting visualization evidence (2026-08-10)

The meeting graphics use the saved full-strength
`r1_iter2000_cumulative3000_resume` case/data for sink-source contours and
carrier pathlines. The separate ramp-reset final was restored to the live
session after export. Fluent readback kept DPM interaction off.

The graphics show:

- the active UDF mask spans the complete `0.1401652536 m` bottom-local band;
- verified Mixture-model carrier pathlines released from `liquidinlet` retain
  the strong swirling flow structure;
- the endpoint sink removes `22.4882 kg/s`, only `19.23%` of the liquid inlet,
  leaving a corrected source-inclusive unclosed liquid rate of `94.4318 kg/s`;
- continuity, pressure, liquid inventory and velocity remain outside their
  acceptance limits.

The pathlines are continuous carrier trajectories, not droplets. A requested
steam-inlet release was excluded because its Fluent readback did not preserve
the requested release surface; no ambiguous image is used.

Meeting evidence:

- [Tuesday meeting brief](../PyAnsys/output/setup07_meeting_visuals_20260811/MEETING_BRIEF.md)
- [sink-mask and carrier-pathline figure](../PyAnsys/output/setup07_meeting_visuals_20260811/08_sink_band_and_carrier_swirl.png)
- [liquid-rate closure figure](../PyAnsys/output/setup07_meeting_visuals_20260811/04_endpoint_liquid_rate_closure.png)
- [Fluent graphics manifest](../PyAnsys/output/setup07_meeting_visuals_20260811/fluent/fluent_graphics_manifest.json)

## 9. Decision and next step

Setup `07c` is retained as `Completed diagnostic / physical qualification
failed`. Thickening the local sink is not accepted as a substitute for outlet
hydraulics and should not be extended into another mesh ladder or DPM/EWF
campaign.

The preferred next steady-model step is a resolved brine outlet. Once geometry
editing is available, qualify it first on one medium mesh for complete phase
and mixture closure, fixed-inventory behavior, stable pressure/velocity
monitors and residual convergence. Only then reconsider mesh independence and
particle/wall-film models.
