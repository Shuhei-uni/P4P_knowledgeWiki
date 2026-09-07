# Split-Inlet Constant-Water-Level Liquid Sink

## 1. Purpose and status

Setup `07b` is a diagnostic child of setup `07` and a modelling-response branch
to the setup `07a` closed-bottom mesh-study failure.

- Parent carrier setup: [07-pure-phase-split-actual-area.md](07-pure-phase-split-actual-area.md)
- Triggering study: [07a-split-inlet-carrier-mesh-convergence.md](07a-split-inlet-carrier-mesh-convergence.md)
- Study ID: `split_inlet_constant_water_level_sink_20260807`
- Implementation status: `Accepted` for compiled/hooked persistence and
  one-iteration source execution.
- Scientific status: `Diagnostic / unresolved`. The clean 900k `tau = 0.1 s`
  qualification reached its 6,000-iteration full-strength limit without an
  accepted stability window or steady liquid closure.
- DPM status: off; no injections were updated or tracked.

This branch keeps `bottom` as a no-slip wall because the project interpretation
is that it represents Purnanto's assumed constant water level. A volumetric
source removes only the Eulerian liquid phase from the cells directly adjacent
to that wall. It does not turn the wall into an outlet and does not remove vapor.

## 2. Modelling interpretation

The sink is an unresolved-reservoir abstraction:

```text
resolved separator domain
  -> liquid reaches the bottom-adjacent cell layer
  -> liquid mass and its carried momentum are removed volumetrically
  -> removed liquid is treated as transferred to an unresolved brine reservoir
```

It is not equivalent to a resolved brine pipe, drain, weir or pressure outlet.
It can test whether maintaining the assumed water-level cutoff allows a stable
carrier solution, but it cannot predict brine-outlet hydraulics.

## 3. Implementation-smoke baseline and production-start rule

The one-iteration implementation smoke test used the protected setup-07a 900k
checkpoint:

```text
C:\Users\qtra338\Documents\Mesh study\split_inlet_constant_water_level_sink_20260807\mesh-900k_07b_sink_hook_v1_retry2_prehook.cas.h5
C:\Users\qtra338\Documents\Mesh study\split_inlet_constant_water_level_sink_20260807\mesh-900k_07b_sink_hook_v1_retry2_prehook.dat.h5
```

The cold-reload verification read back:

- Fluent 2024 R2 with 16 partitions;
- `5,335,623` tetrahedral cells;
- domain volume `22.65842 m3` and characteristic size `0.01619378 m`;
- minimum orthogonal quality `0.202194` and maximum aspect ratio `20.1267`;
- steady pressure-based Mixture model;
- phase 1 `water-vapor-at-psep`, phase 2 `water-liquid-at-psep`;
- RNG `k-epsilon`, gravity `(0,-9.81,0) m/s2`, Energy off;
- liquid inlet `116.92 kg/s`, vapor inlet `80.69 kg/s`;
- steam-outlet gauge pressure `1,120,000 Pa`;
- SIMPLE/PRESTO! and the inherited setup-07a discretization/URFs;
- `bottom` zone ID `50059`, type `wall`;
- DPM interaction off.

This saved solution was used only to prove that the source executes and
integrates correctly. It is not the start state for the actual setup-07b
qualification calculation because it already contains the setup-07a
closed-bottom accumulation history.

The mandatory actual-run start is the clean original mesh:

```text
C:\Users\qtra338\Documents\Mesh study\Meshes\mesh-900k.msh
```

The clean-mesh reconstruction must apply:

```text
C:\Users\qtra338\Documents\Mesh study\Source\mesh_study_settings.set
```

and then read back the authoritative setup-07a fingerprint
`424a9bf02bbd78060dee3a2874103e5149aa4aa555a09e2add69da4d2a0158c5`,
allocate/load/hook the UDF with ramp zero, and perform fresh Hybrid
Initialization. Loading any setup-07a `.dat.h5` field as the production initial
condition is prohibited.

This clean start has now been prepared and cold-reload verified. The accepted
source mesh SHA-256 is
`353bf13ca13d4a32a4cd505d991e64b1ea6f306cc3e8add438859b9117a5afef`.
The preparation loaded the original `.msh`, transferred the authoritative
case-only/settings definition, allocated and hooked the UDF at `R = 0`, and
performed fresh Hybrid Initialization. It loaded no saved solution data and
ran zero production iterations.

Prepared qualification checkpoint:

```text
C:\Users\qtra338\Documents\Mesh study\split_inlet_constant_water_level_sink_20260807\clean_900k_preparation\mesh-900k_07b_clean_original_prepared_v3_fresh_hybrid_ramp0.cas.h5
C:\Users\qtra338\Documents\Mesh study\split_inlet_constant_water_level_sink_20260807\clean_900k_preparation\mesh-900k_07b_clean_original_prepared_v3_fresh_hybrid_ramp0.dat.h5
```

The normalized complete-settings fingerprint after initialization is
`424a9bf02bbd78060dee3a2874103e5149aa4aa555a09e2add69da4d2a0158c5`,
matching the authoritative carrier setup. The only omitted fingerprint subtree
is Fluent's lifecycle-generated default `initialization.patch.vof_smooth_options`,
which appears after Hybrid Initialization and is not a changed model setting.
Generic `wall` name warnings from the imported settings are noncritical here:
the required `wall-fluid` and `bottom` zones both exist and were read back as
walls. Missing or ambiguous required zones still cause a hard stop.

No baseline geometry, material, model, boundary or solver setting was changed
by the hook implementation apart from enabling the required cell-zone source
containers and attaching the UDF source functions.

## 4. Source formulation

For a liquid volume fraction `alpha_l`, liquid density `rho_l`, user ramp `R`
and sink time scale `tau`, the liquid mass source is:

```text
S_l = -rho_l * alpha_l * R / tau              [kg m^-3 s^-1]
```

The source is zero outside the one-cell layer adjacent to `bottom`. It is also
zero when `R = 0`, which makes the saved hooked baseline safe to inspect.

The carried mixture momentum is removed consistently:

```text
S_mx = S_l * u_m
S_my = S_l * v_m
S_mz = S_l * w_m                              [N m^-3]
```

where `(u_m,v_m,w_m)` is mixture velocity. The linearized derivatives supplied
to Fluent are `-rho_l R/tau` for the liquid mass source and `S_l` for the
corresponding mixture-momentum component.

There is deliberately:

- no vapor mass source;
- no energy source because Energy remains off;
- no DPM source or tracking;
- no use of `CURRENT_TIMESTEP`, because this is a steady source model and `tau`
  is an explicit physical/numerical parameter rather than a transient timestep.

## 5. Fluent hook placement

The implementation follows the Fluent Mixture-model source placement:

| Function | Fluent hook | Scope |
|---|---|---|
| `cwl_update_sink_mask` | Adjust hook | reconstruct bottom-adjacent cell mask |
| `cwl_liquid_mass_sink` | phase-2 mass source | liquid only |
| `cwl_x_momentum_sink` | mixture x-momentum source | carried momentum |
| `cwl_y_momentum_sink` | mixture y-momentum source | carried momentum |
| `cwl_z_momentum_sink` | mixture z-momentum source | carried momentum |

Five user-defined memories preserve the cell mask and evaluated mass/x/y/z
source fields. The compiled library is
`lib07b_cwl_bdfa31b0ec_r4` for the old-field implementation smoke and
`lib07b_cwl_bdfa31b0ec_r4_clean1` for the accepted clean-origin checkpoint;
source SHA-256 is
`bdfa31b0ec4ae3851a8585720be23fdcecee18a6d2682e1adc78a52ec738e645`.

Official implementation anchors:

- [Mixture-model UDF hook table](https://ansyshelp.ansys.com/public/Views/Secured/corp/v242/en/flu_udf/x1-79900012.2.html)
- [`DEFINE_SOURCE` and model-specific examples](https://ansyshelp.ansys.com/public/Views/Secured/corp/v242/en/flu_udf/flu_udf_ModelSpecificDEFINE.html)
- [Fluent UDF data-access macros](https://ansyshelp.ansys.com/public/Views/Secured/corp/v242/en/flu_udf/flu_udf_DataAccessMacros.html)
- [Parallelizing Fluent UDFs](https://ansyshelp.ansys.com/public/Views/Secured/corp/v242/en/flu_udf/flu_udf_sec_using_udfs_parallel.html)

## 6. Runtime parameters

The companion controller creates and reads back these RP variables:

| Variable | Implemented value | Meaning |
|---|---:|---|
| `user/cwl07b/bottom-zone-id` | `50059` | water-level wall zone |
| `user/cwl07b/liquid-phase-index` | `1` | zero-based liquid sub-thread index |
| `user/cwl07b/tau-s` | `0.1 s` | provisional removal time scale |
| `user/cwl07b/ramp` | `0` in saved baselines | safe source multiplier |
| `user/cwl07b/alpha-min` | `1e-12` | liquid-volume-fraction guard |

`tau = 0.1 s` is not calibrated. It is an initial qualification value and must
not be treated as a validated drainage time scale.

## 7. Implementation history and failure handling

The failed attempts are preserved rather than hidden:

1. `r1`: remote source transfer/compile checking exposed a false-positive error
   parser; protected checkpoint restored.
2. `r2`: Fluent 2024 R2 invalidated list-child handles after source-list resize;
   protected checkpoint restored.
3. `r3`: atomic source-list assignment succeeded, but the load transcript showed
   five UDMs had not been allocated. This case is explicitly nonfunctional and
   must not be calculated; no iterations ran.
4. `r4`: the workflow allocated and read back five UDM fields before library
   load, required a positive reservation message, atomically attached every
   source, read back full baseline parity and saved a new ramp-zero pair.

The relevant machine correction record is
`PyAnsys/output/split_inlet_constant_water_level_sink_20260807/r3_udm_failure_correction.json`.

## 8. Accepted implementation evidence

Ramp-zero compiled/hooked checkpoint:

```text
C:\Users\qtra338\Documents\Mesh study\split_inlet_constant_water_level_sink_20260807\mesh-900k_07b_sink_hook_v1_retry4_hooked_ramp0.cas.h5
C:\Users\qtra338\Documents\Mesh study\split_inlet_constant_water_level_sink_20260807\mesh-900k_07b_sink_hook_v1_retry4_hooked_ramp0.dat.h5
```

Cold reload caused Fluent to auto-compile/load the stored UDF source and printed:

```text
CWL07B: reserved 5 UDMs at offset 0 for lib07b_cwl_bdfa31b0ec_r4.
```

Complete readback then confirmed:

- all five named UDM fields exist;
- liquid mass source is attached to phase 2 only;
- phase-1/vapor source container remains disabled;
- x/y/z momentum sinks are attached to the mixture;
- ramp remains zero after reload;
- all carrier baseline checks pass;
- DPM remains off.

## 9. One-iteration smoke proof

The protected ramp-zero pair was cold-reloaded and advanced exactly one
diagnostic iteration with `R = 0.05` and `tau = 0.1 s`. The ramp was then reset
to zero and the result saved separately.

| Quantity | Observed |
|---|---:|
| Residual-history iteration | `6000 -> 6001` |
| Marked bottom-adjacent cells | `5,438` |
| Mask-volume integral | `0.027726243 m3` |
| Liquid inventory in marked cells | `0.959465 kg` |
| Integrated liquid mass source | `-0.47973263 kg/s` |
| Expected source from formula | `-0.959465 * 0.05 / 0.1 = -0.4797325 kg/s` |
| Ramp after test | `0` |

The agreement between measured and expected sink rate is within report
rounding. This proves function execution, sign, scope and source integration;
it does not prove a converged physical solution.

Separate smoke checkpoint:

```text
C:\Users\qtra338\Documents\Mesh study\split_inlet_constant_water_level_sink_20260807\mesh-900k_07b_sink_smoke_v2_one_iter_ramp_reset0.cas.h5
C:\Users\qtra338\Documents\Mesh study\split_inlet_constant_water_level_sink_20260807\mesh-900k_07b_sink_smoke_v2_one_iter_ramp_reset0.dat.h5
```

The first smoke wrapper result (`smoke_v1`) is labelled unresolved only because
it used Fluent's per-command iteration control as if it were the cumulative
iteration number. Its console still showed valid source execution, but it did
not reach the integration/save step and is superseded by accepted `smoke_v2`.

## 10. Evidence classifications

### Accepted

- compiled UDF with built-in Clang in Fluent 2024 R2;
- five-UDM allocation and cold-reload persistence;
- exact phase/mixture source-hook readback;
- unchanged carrier setup and DPM-off state;
- one-iteration bottom-mask and liquid-sink execution;
- separate ramp-zero case/data preservation;
- clean original 900k mesh identity and quality readback;
- authoritative settings-fingerprint parity;
- fresh Hybrid Initialization with no saved solution data loaded and zero
  production iterations;
- cold-reload verification of the clean-origin prepared checkpoint.

### Diagnostic

- `R = 0.05`, `tau = 0.1 s` one-iteration source magnitude;
- bottom-adjacent one-cell sink-layer choice;
- existing iteration-6000 carrier field used as the smoke starting state.
- completed clean-origin `tau = 0.1 s` qualification through 500 ramp
  iterations plus 6,000 full-strength iterations;
- final pressure, outlet-flow, velocity, vorticity, sink-rate and liquid-
  inventory histories from the qualification.

### Unresolved

- source-CAD/image evidence tying the `bottom` plane to the intended constant
  water-level elevation;
- sensitivity to `tau`, ramp schedule and sink-layer resolution;
- iteration-independent pressure, velocity, phase inventory and source rate;
- full steady liquid balance including the integrated sink term;
- whether a resolved brine outlet changes the pressure/swirl solution;
- any separator-efficiency, validation, mesh-independence, DPM or EWF claim.
- use of `tau = 0.1 s` or the one-cell sink as an accepted constant-water-level
  model: the sink removed only `8.06194 kg/s` at the endpoint while the domain
  liquid inventory continued increasing.

## 11. Qualification plan before production use

Use the 900k mesh first. Do not repeat the seven-mesh ladder yet.

### Active `tau = 0.1 s` qualification

Run `mesh-900k_tau0p100_qualification_v1` was launched on 2026-08-07 from the
accepted clean-origin checkpoint. The controller reloaded the protected
fresh-Hybrid pair, verified the 5,335,623-cell setup and source hooks, confirmed
DPM off, and saved a separate run-local ramp-zero start pair. Remote free space
at launch was `109.32 GB`.

The scheduled ramp is `R=0.05/100`, `0.10/100`, `0.25/150`, and `0.50/150`
iterations, followed by `R=1` in 250-iteration blocks. The full-strength stage
has a 2,500-iteration minimum and 6,000-iteration maximum. Early completion
requires two consecutive passing 500-iteration windows, source-inclusive
liquid and mixture imbalance at or below `0.5%`, primary monitor drift at or
below `0.5%`, velocity/vorticity drift at or below `1%`, non-growing residuals,
and every final scaled residual at or below `1e-3`.

The original clean checkpoint is never overwritten. Separate start,
ramp-complete, 1,000-iteration full-strength and final/failure ramp-reset-zero
checkpoints are written under:

```text
C:\Users\qtra338\Documents\Mesh study\split_inlet_constant_water_level_sink_20260807\mesh-900k_tau0p100_qualification_v1
```

The run completed on 2026-08-08 NZST at the maximum budget. It did not produce
either of the two required consecutive passing windows; in fact, zero
acceptance windows passed. The endpoint and final-window evidence is:

| Quantity | R1 = 6000 endpoint / final-window result |
|---|---:|
| Total solver iterations | `6,500` (`500` ramp + `6,000` at `R = 1`) |
| Integrated liquid sink magnitude | `8.06194 kg/s` |
| Liquid inlet | `116.92 kg/s` |
| Liquid flow through steam outlet | `2.23770 kg/s` out |
| Source-inclusive liquid imbalance (corrected) | `91.1909%` |
| Domain liquid inventory | `191.836 kg` |
| Pressure drop | `34.8475 kPa` |
| Steam-outlet vapor flow | `81.3862 kg/s` out |
| Carrier outlet quality | `97.3241%` (`trend only`) |
| Outlet/domain velocity | `48.8051 / 34.6175 m/s` |
| Domain-average vorticity | `86.2906 s^-1` |
| Final continuity residual | `0.279243` |
| Final phase-volume-fraction residual | `1.8933e-3` |

Across the final 500 full-strength iterations, pressure drop drifted `2.60%`,
sink magnitude `17.89%`, domain liquid inventory `10.07%`, domain velocity
`1.76%`, and vorticity `1.42%`. Only vapor outlet flow (`0.0357%`) and outlet
velocity (`0.269%`) met their respective stability limits. The final residual
level gate also failed: continuity remained about `0.28`, the volume-fraction
residual remained above `1e-3`, and the `k` residual trend was classified as
growing.

This is not a case where more iterations merely polish a converged solution.
The one-cell sink rate rises with the bottom-layer inventory but remains far
below the liquid inlet, while total domain liquid inventory continues to rise.
The `tau = 0.1 s` branch is therefore classified `Completed diagnostic —
unresolved at maximum iteration budget`, not accepted.

Post-run accounting correction: the controller field named
`liquid_source_augmented_imbalance_percent` added the sink twice. Fluent's
phase-2 flux-report `Net` already contained the phase-2 cell-zone source, as
shown by `114.682304 - 8.061935 = 106.620369 kg/s`, matching the reported
phase-2 Net. The corrected source-inclusive liquid imbalance is therefore
`91.1909%`, not the raw derived `84.2956%`. The mixture report is boundary-net
based and its single source augmentation remains valid. This correction does
not change the failed classification or any acceptance-window decision.

The run preserved separate verified checkpoints at full-strength R1 = 1,000,
2,000, 3,000, 4,000, 5,000 and 6,000. The final R1 = 6,000 pair is:

```text
C:\Users\qtra338\Documents\Mesh study\split_inlet_constant_water_level_sink_20260807\mesh-900k_tau0p100_qualification_v1\r1_iter6000_cumulative6500.cas.h5
C:\Users\qtra338\Documents\Mesh study\split_inlet_constant_water_level_sink_20260807\mesh-900k_tau0p100_qualification_v1\r1_iter6000_cumulative6500.dat.h5
```

The controller then reset the source ramp to zero and saved a second,
non-overwriting final pair:

```text
C:\Users\qtra338\Documents\Mesh study\split_inlet_constant_water_level_sink_20260807\mesh-900k_tau0p100_qualification_v1\max_r1_6000_unresolved_ramp_reset0.cas.h5
C:\Users\qtra338\Documents\Mesh study\split_inlet_constant_water_level_sink_20260807\mesh-900k_tau0p100_qualification_v1\max_r1_6000_unresolved_ramp_reset0.dat.h5
```

DPM remained off throughout. A controller disconnect during the R1 = 2,750 to
3,000 block was recovered without overwriting evidence: the newer live state
was saved separately, the completed block was reconciled, and the remaining
blocks resumed from the live field. This creates a residual-history gap for
that block but does not change the endpoint classification.

1. Start from the accepted clean-origin, fresh-Hybrid, ramp-zero checkpoint
   recorded in Section 3. Do not substitute the 6000-iteration setup-07a data
   field or the implementation-smoke data.
2. Ramp the source gradually rather than switching immediately to `R = 1`.
3. Do not automatically schedule `tau = 0.05/0.20 s` as production runs. A
   narrowly scoped sensitivity may be useful for documenting model dependence,
   but the failed `tau = 0.1 s` mass-removal capacity already blocks physical
   acceptance of this one-cell formulation.
4. Monitor residuals, pressure drop, inlet/outlet phase flows, integrated sink
   rate, domain liquid inventory, bottom-layer inventory, outlet velocity and
   vorticity.
5. Require steady liquid closure using:

   ```text
   liquid inlet + liquid steam-outlet flow + integrated liquid sink = 0
   ```

6. Require sink rate, pressure and velocity monitors to become iteration
   independent before comparing with setup 07a.
7. Treat the sink abstraction as unresolved and move to a resolved brine outlet
   for the next steady-performance branch. Retain any later tau/layer test as a
   diagnostic sensitivity only.
8. Only after a qualified carrier solution should any mesh ladder, DPM or EWF
   study resume.

## 12. Files and reproducibility

Local implementation:

- `PyAnsys/udf/constant_water_level_sink.c`
- `PyAnsys/src/pyansys_fluent/constant_water_level_sink.py`
- `PyAnsys/scripts/setup/setup07b_constant_water_level_sink.py`
- `PyAnsys/scripts/setup/prepare_setup07b_clean_900k.py`
- `PyAnsys/scripts/setup/run_setup07b_sink_qualification.py`
- `PyAnsys/scripts/setup/resume_setup07b_sink_qualification.py`
- `PyAnsys/scripts/setup/reconcile_setup07b_completed_block.py`
- `PyAnsys/scripts/setup/capture_setup07b_live_recovery.py`
- `PyAnsys/scripts/connection/check_setup07b_sink_status.py`
- `PyAnsys/scripts/inspection/inspect_constant_water_level_sink.py`
- `PyAnsys/scripts/inspection/probe_constant_water_level_udm.py`
- `PyAnsys/scripts/inspection/probe_constant_water_level_source_terms.py`
- `PyAnsys/scripts/inspection/verify_constant_water_level_sink.py`
- `PyAnsys/tests/test_constant_water_level_sink.py`

Machine-readable evidence root:

```text
PyAnsys/output/split_inlet_constant_water_level_sink_20260807
```

Primary evidence:

- `mesh-900k_07b_sink_hook_v1_retry4_manifest.json`;
- `mesh-900k_07b_sink_smoke_v2_verification.json`;
- `udm_allocation_probe.json`;
- `source_term_activation_probe_atomic.json`;
- `r3_udm_failure_correction.json`;
- `clean_900k_preparation/mesh-900k_07b_clean_original_prepared_v3_manifest.json`.
- `mesh-900k_tau0p100_qualification_v1/qualification_manifest.json`;
- `mesh-900k_tau0p100_qualification_v1/physical_monitor_history.csv`;
- `mesh-900k_tau0p100_qualification_v1/mass_balance_history.csv`;
- `mesh-900k_tau0p100_qualification_v1/residual_history.csv`;
- `mesh-900k_tau0p100_qualification_v1/QUALIFICATION_RESULT.md`.
