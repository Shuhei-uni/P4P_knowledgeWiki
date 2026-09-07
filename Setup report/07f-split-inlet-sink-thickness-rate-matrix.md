# Split-Inlet Sink Thickness and Rate Diagnostic Matrix

## Purpose and status

Setup `07f` is a bounded diagnostic extension of setups `07c`-`07e`. The
user requested additional cases with a thicker active sink zone and a faster
liquid-removal rate while brine-outlet geometry remains unavailable.

- Study ID: `split_inlet_sink_thickness_rate_matrix_20260811`
- Parent implementation: [07c-split-inlet-thickened-constant-water-level-liquid-sink.md](07c-split-inlet-thickened-constant-water-level-liquid-sink.md)
- Comparison anchor: [07d-split-inlet-capacity-matched-thick-sink.md](07d-split-inlet-capacity-matched-thick-sink.md)
- Launch status: `Running diagnostic matrix` on 2026-08-11 NZST.
- Scientific status: `Unresolved by design` until each terminal history is
  assessed. No case can validate a physical brine outlet, separator
  efficiency, mesh independence, a free surface or physical-time accumulation.
- DPM/EWF: off; no injection update, tracking or wall-film calculation.

## Controlled baseline

Each case independently restores the verified setup-07c clean-original 900k
prepared checkpoint. The checkpoint originates from `mesh-900k.msh`, the
authoritative `mesh_study_settings.set`, full carrier-settings readback and
fresh Hybrid Initialization; no setup-07a accumulated solution data are used.
After restoring the prepared state, the controller changes only the runtime
sink-band height and `tau`, reads both values back, rebuilds and integrates the
mask, performs a new Hybrid Initialization and starts the guarded ramp.

Readback for the first case confirmed:

- Fluent 2024 R2 with 16 partitions;
- 5,335,623 cells, 923,066 nodes and `22.65842 m3` domain volume;
- minimum orthogonal quality `0.202194`, maximum aspect ratio `20.1267` and no
  negative-volume mesh-check error;
- steady pressure-based Mixture, vapor primary/liquid secondary;
- RNG k-epsilon, gravity `(0,-9.81,0) m/s2`, Energy off;
- SIMPLE/PRESTO and inherited setup-07 discretization/URFs;
- liquid/vapor inlets `116.92/80.69 kg/s`, steam outlet `1.12 MPa`;
- `bottom` retained as a wall and DPM interaction off.

## Matrix

| Order | Run label | Band height | Relative height | `tau` | Relative coefficient | Purpose |
|---:|---|---:|---:|---:|---:|---|
| 1 | `mesh-900k_band0p280331_tau0p020_v3_rpc25` | `0.2803305072 m` | `2.0x` setup 07c/07d | `0.020 s` | `5x` setup-07c coefficient | isolate doubled thickness at the qualified 07d rate |
| 2 | `mesh-900k_band0p280331_tau0p005_v5_single_controller` | `0.2803305072 m` | `2.0x` | `0.005 s` | `20x` setup-07c coefficient | isolate a further `4x` rate increase at fixed doubled thickness |
| 3 | `mesh-900k_band0p420496_tau0p005_v5_single_controller` | `0.4204957609 m` | `3.0x` | `0.005 s` | `20x` | isolate a further `1.5x` thickness increase at the faster rate |

The first-case mask readback is accepted for execution: `184,145` cells,
`0.88704756 m3`, centroid range approximately `y=-6.43746` to `-6.16067 m`,
and runtime RP readback `thickness=0.28033050723644937 m`, `tau=0.02 s`,
`R=0`. A separate fresh-initialized ramp-zero case/data pair was saved before
the first iteration.

The initial `v1` startup was stopped and preserved after 79 startup iterations
because the inherited Adjust hook rebuilt and printed the fixed 5.3-million-
cell mask on every iteration, producing roughly `8-11 min/iteration`. The mask
depends only on fixed cell-centroid position and the case band height, so the
`v2_staticmask` controller builds/broadcasts it on demand whenever thickness,
`tau` or ramp changes and clears only the per-iteration Adjust hook. A live
one-iteration smoke check reduced wall time to about `6.17 s`, retained all RP
readbacks and kept DPM off. The formal `v2` cases restart from the clean origin;
the interrupted `v1` field is not reused.

The first `v2_staticmask` case subsequently reached `2,500` cumulative and
`1,500` full-strength recorded iterations before its next 250-iteration gRPC
call timed out. This was a controller transport failure, not a numerical
safety stop: Fluent remained healthy, the sink was `44.199736 kg/s`, pressure
drop was `25.1905 kPa`, DPM was off and the residual trends were non-growing,
although continuity (`~0.20`) and all physical-stability/closure gates still
failed. The newer partial live field was saved separately as an explicitly
unverified recovery pair. Formal execution restarted from the clean origin
under `v3_rpc25` labels, with every ramp and full-strength request bounded to
25 iterations so a single RPC remains comfortably below the connection
timeout. No `v1` or `v2` field is reused by the formal retry.

The `v3_rpc25` doubled-band, `tau=0.020 s` case completed its full
`3,000`-iteration contract. The following `tau=0.005 s` case recorded `2,375`
cumulative / `1,375` full-strength iterations before its manifest and log
stopped advancing while Fluent remained healthy. Its last recorded
sink/pressure/inventory were `45.411518 kg/s`, `24.6526 kPa` and `54.03819 kg`,
with zero passing windows. The newer in-memory field was saved separately as
unverified recovery evidence. A sandboxed process-liveness check then
misclassified permission denial as process absence and allowed two duplicate
preflight controllers to start. An escalated process audit detected all three
trees; the duplicates and original stalled tree were terminated before any
new production iteration. The overlapping `v4` preflights were preserved and
one failed the fingerprint guard, as intended. Cases 2 and 3 now restart clean
under `v5_single_controller` labels with exactly one audited controller; case
1 is not rerun and no partial case-2 field is reused.

The single-controller v5 launch actually completed parity/mask preflight and
saved a separate clean ramp-zero checkpoint. A concurrent health probe did not
return while Fluent was busy, which was initially misdiagnosed as a dead gRPC
service; v5 was stopped before its first production iteration and its accepted
preflight evidence remains preserved. A final single-controller v6 retry then
connected and restored the parent, but Fluent returned empty captured text for
mesh size/check/quality report calls. The mandatory mesh parser rejected this
before initialization or production. All local controllers are audited absent
and the queue is stopped. Cases 2 and 3 require a clean/repaired Fluent session
before retry; no further automation should bypass the report/readback gate.

## Source law and interpretation

The existing phase-2 liquid-only source is unchanged:

```text
S_l = -rho_l * alpha_l * R / tau
S_mi = S_l * u_mi
```

The source remains proportional to the liquid inventory that actually occupies
the selected band. Increasing band height changes the region that can supply
the source; reducing `tau` increases the local coefficient. Neither operation
defines a brine-outlet pressure-flow relationship.

## Execution and acceptance contract

- guarded 1,000-iteration ramp with the existing setup-07c schedule;
- 1,000 minimum and 2,000 maximum full-strength iterations per case;
- 25-iteration ramp and full-strength RPC blocks after the preserved
  `v2_staticmask` transport interruption;
- fixed-mask on-demand rebuild/broadcast at initialization and each ramp/tau
  change; no per-iteration whole-domain mask reconstruction;
- two consecutive accepted 500-iteration windows required for early success;
- source guard at `175 kg/s`, DPM-off readback, non-finite-field protection and
  an abrupt pressure-change stop;
- separate start, ramp-complete, R1=1000, R1=2000 and final ramp-reset-zero
  case/data checkpoints where reached;
- transcripts, mesh/settings/RP/mask readback, residuals, physical monitors,
  phase/mixture balance and machine-readable manifests retained separately;
- the queue stops after any case-level controller failure rather than starting
  the next case on an uncertain Fluent state.

Primary assessment quantities are integrated liquid sink, corrected liquid
imbalance, source-inclusive mixture imbalance, domain/band liquid inventory,
pressure drop, steam-outlet vapor/liquid flow, outlet/domain velocity,
vorticity and all residual histories. Steady iteration is not physical time;
inventory change with iteration is an iteration-independence diagnostic.

## Output locations

- Local queue manifest:
  `../PyAnsys/output/split_inlet_sink_thickness_rate_matrix_20260811/queue_manifest.json`
- Per-case evidence:
  `../PyAnsys/output/split_inlet_sink_thickness_rate_matrix_20260811/<run-label>/`
- Remote case/data root:
  `C:\Users\qtra338\Documents\Mesh study\split_inlet_sink_thickness_rate_matrix_20260811\`

## Decision rule

These runs are useful only if they show whether the prior capacity limit moves
when the source has access to more liquid. A lower imbalance alone is not
acceptance: pressure, inventory, velocity/swirl and residual histories must
also become iteration independent. Regardless of outcome, a resolved brine
outlet remains the required branch for physical outlet and separator claims.
