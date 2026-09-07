# Split-Inlet Capacity-Matched Thick-Sink Diagnostic

## Purpose and status

Setup `07d` is a controlled sink-strength child of setup `07c`. It uses the
available compute window before brine-outlet geometry can be created to test
whether the setup-07c failure was primarily insufficient local removal
capacity.

- Study ID: `split_inlet_strong_sink_sensitivity_20260810`
- Run label: `mesh-900k_band0p140165_tau0p020_v1`
- Final status: `Completed diagnostic / unresolved at maximum iteration budget`
- Parent: [07c-split-inlet-thickened-constant-water-level-liquid-sink.md](07c-split-inlet-thickened-constant-water-level-liquid-sink.md)
- DPM/EWF: off; no injections or wall-film model.

## Controlled change and rationale

Setup 07c ended with `2.24882 kg` of liquid in the active band and a sink of
`22.4882 kg/s` at `tau=0.1 s`. The time scale that would make that endpoint
band inventory produce a sink equal to the `116.92 kg/s` liquid inlet is:

```text
tau_capacity = m_liquid,band / m_liquid,inlet
             = 2.24882 / 116.92
             = 0.01923 s
```

Setup 07d therefore uses `tau=0.02 s`, a fivefold source-strength increase.
This is a capacity-matched diagnostic, not a calibrated physical drain law.

Everything else remains unchanged from the clean setup-07c origin:

- original `mesh-900k.msh`, 5,335,623 cells;
- fixed `0.1401652536 m` complete bottom-local sink band;
- authoritative `mesh_study_settings.set` and full settings fingerprint;
- steady pressure-based Mixture, vapor primary/liquid secondary;
- RNG k-epsilon, gravity `(0,-9.81,0)`, Energy off;
- SIMPLE/PRESTO and inherited discretization/URFs;
- liquid/vapor inlets `116.92/80.69 kg/s`;
- steam outlet `1.12 MPa`, bottom retained as a wall;
- fresh Hybrid Initialization and no setup-07a/07c saved solution data;
- the same guarded ramp, 250-iteration blocks and acceptance criteria.

## Decision value

- If liquid closure and primary monitors stabilize without source overshoot,
  the result shows that the surrogate can be numerically capacity-matched,
  but its physical validity remains unresolved because `tau` is empirical and
  outlet hydraulics are absent.
- If the sink overshoots, oscillates, or still fails closure/stability, the
  result strengthens the conclusion that sink capacity alone cannot replace a
  resolved brine outlet.

No outcome can establish separator efficiency, mesh convergence, a physical
free surface or physical-time accumulation.

## Execution contract

- guarded 1,000-iteration ramp;
- up to 2,000 full-strength iterations in 250-iteration blocks;
- separate start, smoke, ramp-complete, 1,000-, 2,000- and final case/data;
- early stop on two consecutive accepted 500-iteration windows, non-finite
  fields, abrupt pressure change, or guarded sink overshoot;
- transcripts, residuals, physical monitors, phase/mixture mass balance,
  mesh/readback evidence and machine-readable manifest retained separately;
- no setup-07a/07b/07c file may be overwritten.

## Preflight recovery record

Two zero-production-iteration attempts were preserved before the calculation
was allowed to run:

1. Recompiling the already-loaded setup-07c library in the persistent Fluent
   session could not reserve the same five UDM locations a second time. The
   controller reset the ramp to zero and saved a separate failure pair.
2. Restoring the verified setup-07c prepared checkpoint succeeded and reserved
   the UDMs at offset zero, but the first recovery gate compared its
   source-hooked fingerprint (`c5294907...`) with the earlier source-free
   carrier fingerprint (`424a9bf0...`). The source-hooked value exactly matches
   the parent setup-07c prepared settings, so the gate was corrected to compare
   prepared state with prepared state.

Neither attempt ran a production iteration, and both are retained as
implementation evidence. The production controller must restore the verified
prepared checkpoint, confirm the source-hooked fingerprint, change only
`tau`, fresh Hybrid Initialize and then start the guarded ramp.

## Completed execution and result

The corrected third attempt restored the verified source-hooked setup-07c
prepared checkpoint, matched fingerprint `c5294907...`, changed only
`tau=0.02 s`, performed fresh Hybrid Initialization and completed the full
contract: 1,000 guarded ramp iterations plus 2,000 full-strength iterations.
It saved separate start, ramp-complete, R1 = 1,000, R1 = 2,000 and final
case/data checkpoints. The final saved state has the source ramp reset to zero
and DPM read back off.

Endpoint evidence at R1 = 2,000:

- integrated liquid sink: `46.987392 kg/s`, or `40.19%` of the
  `116.92 kg/s` liquid feed;
- unclosed/source-inclusive liquid rate: `69.932422 kg/s`, or corrected liquid
  imbalance `59.812198%`;
- source-inclusive mixture imbalance: `35.167855%`;
- domain liquid inventory: `66.65597 kg`;
- liquid inventory in the marked band: `0.93974784 kg`;
- pressure drop: `26.8901 kPa`;
- steam-outlet vapor/liquid: `81.127219/0.00018636 kg/s` out;
- carrier outlet quality: `99.99977%`, trend only;
- outlet/domain velocity: `45.7491/30.7938 m/s`;
- domain vorticity: `83.3916 s^-1`;
- final continuity and phase-2 volume-fraction residuals:
  `0.229682` and `7.34191e-4`.

Final-500 drift was `6.618%` for pressure drop, `23.044%` for sink magnitude,
`14.120%` for domain liquid inventory, `3.161%` for outlet velocity,
`6.901%` for domain velocity and `0.797%` for vorticity. Vapor outlet drift
was `0.140%`. Zero consecutive acceptance windows passed.

## Interpretation

The fivefold source-coefficient increase produced only a `2.09x` endpoint
sink increase (`22.49 -> 46.99 kg/s`) because liquid available inside the
fixed band fell from `2.24882` to `0.93975 kg`. This confirms that local sink
capacity and local liquid supply are coupled. It improves the numerical liquid
balance but neither closes it nor establishes iteration independence.

The outcome is therefore `Diagnostic / unresolved`. It strengthens the
resolved-brine-outlet recommendation: increasing an empirical local removal
coefficient cannot substitute for a boundary with a defined location,
pressure-flow relation and directly reportable phase flux. No mesh-convergence,
separator-efficiency, physical free-surface or physical-time accumulation
claim is permitted.

## Preserved outputs

- Local evidence:
  `../PyAnsys/output/split_inlet_strong_sink_sensitivity_20260810/mesh-900k_band0p140165_tau0p020_v1/`.
- Machine-readable result: `qualification_manifest.json`.
- Detailed local result:
  `../PyAnsys/output/split_inlet_strong_sink_sensitivity_20260810/mesh-900k_band0p140165_tau0p020_v1/QUALIFICATION_RESULT.md`.
- Histories: `physical_monitor_history.csv`, `mass_balance_history.csv` and
  `residual_history.csv`.
- Recovery provenance: the two zero-production-iteration attempt manifests and
  controller logs remain alongside the accepted production evidence.
- Controlled-comparison audit: `CONTROLLED_COMPARISON_AUDIT.json/.md`; exact
  mesh/settings/mask parity and matched pre-sink stability limits pass.
- Meeting comparisons:
  `../PyAnsys/output/setup07_meeting_visuals_20260811/10_fixed_sink_strength_history.png`,
  `11_fixed_sink_diminishing_return.png` and
  `12_fixed_sink_residual_comparison.png`.
