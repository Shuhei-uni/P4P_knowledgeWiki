# Stage-1 Candidate Screen — FG-MIX-T01

## Status and interpretation

This report records the user-requested quick Stage-1 screen on the Student
server using the exact production mesh `Full-geomV2-231kcells.msh.h5`. Three
independent unpatched Mixture cases were run for `1,000` native steady
iterations at brine-outlet pressures between the earlier 02c G/H points.

**Provisional candidate-parent recommendation: `FG-MIX-T01-S1-C1375` at
`1.1375 MPa` brine-outlet gauge pressure.** This is a user-authorized,
diagnostic selection for constructing the next stage. It is not a converged
steady parent, validated operating pressure, or separator-performance result.

The recommendation is a balance of numerical steadiness and phase-routing
behaviour. `C139` has the lowest mean continuity residual in the retained tail,
but its epsilon history is more variable and its endpoint has substantially
more liquid carryover to the steam outlet and vapour through the brine outlet.
`C1375` has the smoothest retained residual tail among the two higher-pressure
cases and the lowest measured wrong-outlet vapour and steam-outlet liquid
flows. All three remain open/non-converged and require a Stage-2 readback gate
before reuse.

Interpretation status: user-directed provisional selection; final claim
strength remains diagnostic only.

## Governing setup and exact mesh

- Setup/stage: [FG-MIX-T01 Stages 1–2](../../../../../full-geometry/mixture/transient-liquid-outlet/stage-01-02-steady-parent-and-transient-start.md)
- Parent contract: [02c Mixture brine-outlet pressure sensitivity, unprimed](../../../../../full-geometry/mixture/steady-liquid-outlet/02c-mixture-brine-outlet-pressure-sensitivity-unprimed.md)
- Fluent: Ansys Fluent 2025 R2 Student
- Mesh input: `C:\Users\Shuhei Yokkaichi\Documents\CFD\Brine outlet\Full-geomV2-231kcells.msh.h5`
- Mesh readback on every case reload: `231,376` mixed cells and `697,078` nodes
- Mesh handling: no remeshing, adaptation, scaling change, or mesh substitution
- Common model: pressure-based, steady, Mixture, RNG `k-epsilon`, Energy off
- Common boundary contract: split velocity inlets at `27.118 m/s`, inlet initial gauge pressure `1.140 MPa`, steam outlet pressure `1.120 MPa`, brine backflow liquid volume fraction `1.0`, steam-outlet backflow liquid volume fraction `0.0`
- Initialization: independent Fluent-native Hybrid Initialization from each case-only child; no Y010 or other liquid patch
- Run budget: one native `/solve/iterate 1000` command per case

The case-only build snapshot is [fg_mix_t01_stage1_candidates_20260816T102830Z.json](../../../../../../PyAnsys/output/fg_mix_t01_stage1_candidates_20260816T102830Z.json).

## Case matrix and endpoint artifacts

The common steam-outlet gauge pressure was `1.120 MPa` for all cases.

| Candidate | Brine pressure | ΔP above steam outlet | Endpoint case/data | Execution status |
|---|---:|---:|---|---|
| `FG-MIX-T01-S1-C136` | `1.1360 MPa` | `+16.0 kPa` | `C:\Users\Shuhei Yokkaichi\Documents\CFD\Brine outlet\FG-MIX-T01-S1-C136-brine-p1136kpa-unpatched-preinit-20260816T102830Z-iter1000-20260816T103114Z.cas.h5/.dat.h5` | completed 1,000; paired endpoint verified |
| `FG-MIX-T01-S1-C1375` | `1.1375 MPa` | `+17.5 kPa` | `C:\Users\Shuhei Yokkaichi\Documents\CFD\Brine outlet\FG-MIX-T01-S1-C1375-brine-p1137p5kpa-unpatched-preinit-20260816T102830Z-iter1000-20260816T104203Z.cas.h5/.dat.h5` | completed 1,000; paired endpoint verified |
| `FG-MIX-T01-S1-C139` | `1.1390 MPa` | `+19.0 kPa` | `C:\Users\Shuhei Yokkaichi\Documents\CFD\Brine outlet\FG-MIX-T01-S1-C139-brine-p1139kpa-unpatched-preinit-20260816T102830Z-iter1000-20260816T105250Z.cas.h5/.dat.h5` | completed 1,000; paired endpoint verified |

The native-run manifests and journals are:

- `C136`: [manifest](../../../../../../PyAnsys/output/fg_mix_t01_stage1_C136_20260816T103114Z.json), [journal](../../../../../../PyAnsys/output/fg_mix_t01_stage1_C136_20260816T103114Z.jou)
- `C1375`: [manifest](../../../../../../PyAnsys/output/fg_mix_t01_stage1_C1375_20260816T104203Z.json), [journal](../../../../../../PyAnsys/output/fg_mix_t01_stage1_C1375_20260816T104203Z.jou)
- `C139`: [manifest](../../../../../../PyAnsys/output/fg_mix_t01_stage1_C139_20260816T105250Z.json), [journal](../../../../../../PyAnsys/output/fg_mix_t01_stage1_C139_20260816T105250Z.jou)

## Numerical-health comparison

The endpoint data retained `400` residual-history points spanning reported
iterations `4–1,000`; the histories were explicitly reloaded from each paired
endpoint. Tail statistics below use the final `100` retained history points,
not an invented convergence threshold.

| Candidate | Final continuity | Tail mean ± SD | Tail CV | Final x/y/z residuals | Final `vf-phase-2` | Numerical reading |
|---|---:|---:|---:|---|---:|---|
| `C136` | `2.4976e-1` | `2.0000e-1 ± 3.0787e-2` | `0.154` | `9.151e-4 / 7.067e-4 / 1.058e-3` | `1.618e-2` | bounded but widest continuity/epsilon movement of the three |
| `C1375` | `2.2536e-1` | `2.1912e-1 ± 1.5645e-2` | `0.071` | `7.989e-4 / 7.606e-4 / 9.505e-4` | `1.645e-2` | smoothest retained continuity tail; still non-converged |
| `C139` | `1.7239e-1` | `1.8930e-1 ± 1.6841e-2` | `0.089` | `5.736e-4 / 5.757e-4 / 5.983e-4` | `1.059e-2` | lowest continuity and velocity residual levels, but epsilon spikes and persistent limiting |

Additional tail observations:

- `C1375` epsilon tail mean/CV: `3.889e-2 / 0.592`.
- `C139` epsilon tail mean/CV: `8.175e-2 / 1.09`, with a retained tail maximum of `4.872e-1`.
- `C136` epsilon tail mean/CV: `4.753e-2 / 1.21`.
- Fluent transcripts reported repeated reversed-flow warnings at the pressure outlets and turbulent-viscosity limiting in all three cases. These are numerical-health limitations, not convergence evidence.

Residual extraction artifacts:

- [C136 residual JSON](../../../../../../PyAnsys/output/post_simulation_analysis/FG-MIX-T01-S1-C136-iter1000-residual-check.json) and [plot](../../../../../../PyAnsys/output/post_simulation_analysis/FG-MIX-T01-S1-C136-iter1000-residual-check.png)
- [C1375 residual JSON](../../../../../../PyAnsys/output/post_simulation_analysis/FG-MIX-T01-S1-C1375-iter1000-residual-check.json) and [plot](../../../../../../PyAnsys/output/post_simulation_analysis/FG-MIX-T01-S1-C1375-iter1000-residual-check.png)
- [C139 residual JSON](../../../../../../PyAnsys/output/post_simulation_analysis/FG-MIX-T01-S1-C139-iter1000-residual-check.json) and [plot](../../../../../../PyAnsys/output/post_simulation_analysis/FG-MIX-T01-S1-C139-iter1000-residual-check.png)

## Phase-flux comparison

Fluent fluxes were re-extracted after explicit endpoint reload. Outlet values
below are shown as outward-positive magnitudes for side-by-side screening. The
domain is intentionally open for this diagnostic geometry, so the liquid
balance is not a convergence or recovery fraction.

| Candidate | Liquid inlet [kg/s] | Liquid → brine [kg/s] | Liquid → steam [kg/s] | Vapour inlet [kg/s] | Vapour → brine [kg/s] | Vapour → steam [kg/s] | Vapour brine / vapour inlet |
|---|---:|---:|---:|---:|---:|---:|---:|
| `C136` | `116.921` | `541.299` | `23.633` | `80.690` | `19.317` | `58.475` | `23.94%` |
| `C1375` | `116.921` | `603.948` | `22.333` | `80.690` | `16.944` | `60.581` | `21.00%` |
| `C139` | `116.921` | `460.750` | `45.682` | `80.690` | `22.600` | `55.636` | `28.01%` |

All three have liquid-brine outflow above the liquid inlet at the recorded
endpoint, so the liquid field is still inventory-draining/open. `C1375`
has the lowest measured vapour flow through the brine outlet and the lowest
steam-outlet liquid flow among the three, while `C139` has the highest
steam-outlet liquid carryover and highest vapour wrong-outlet fraction.

Flux extraction artifacts:

- [C136 flux JSON](../../../../../../PyAnsys/output/post_simulation_analysis/FG-MIX-T01-S1-C136-iter1000-flux-check.json)
- [C1375 flux JSON](../../../../../../PyAnsys/output/post_simulation_analysis/FG-MIX-T01-S1-C1375-iter1000-flux-check.json)
- [C139 flux JSON](../../../../../../PyAnsys/output/post_simulation_analysis/FG-MIX-T01-S1-C139-iter1000-flux-check.json)

## Parent handoff decision

Use the `C1375` endpoint as the **provisional Stage-1 candidate parent** for
the next setup-construction stage:

```text
C:\Users\Shuhei Yokkaichi\Documents\CFD\Brine outlet\FG-MIX-T01-S1-C1375-brine-p1137p5kpa-unpatched-preinit-20260816T102830Z-iter1000-20260816T104203Z.cas.h5
C:\Users\Shuhei Yokkaichi\Documents\CFD\Brine outlet\FG-MIX-T01-S1-C1375-brine-p1137p5kpa-unpatched-preinit-20260816T102830Z-iter1000-20260816T104203Z.dat.h5
```

Before Stage 2 uses this parent, re-read the paired files and verify the
exact mesh, phase/material mapping, boundary pressures, inlet conditions,
monitor package, and case/data identity. Do not patch Y010 or run additional
steady iterations after applying the Stage-2 child conditions unless the
stage plan explicitly requires it.

This handoff is conditional because the selected field is not converged:
continuity remains approximately `2.25e-1` at the endpoint, the liquid phase
balance is open, and reverse-flow/viscosity-limit diagnostics persist. The
candidate is suitable for controlled startup construction only, not for
separator efficiency, pressure selection, validation, or final reporting.

## Evidence limitations

- The post-processing helper could not discover the phase-material mapping
  from the live state and used the documented phase-order fallback
  `phase-1 = vapour`, `phase-2 = liquid`; the build snapshot independently
  records the intended material/model contract.
- No total liquid-inventory, lower-vessel pressure, or brine-pipe-entry
  monitor was present in these case-only children, so inventory flattening and
  local pressure stability could not be used in the selection.
- The retained residual histories are diagnostic and do not satisfy a
  convergence gate. `C1375` is a provisional parent choice based on relative
  evidence within this common screen.
