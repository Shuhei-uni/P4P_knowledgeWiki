# C8 corrected v2 absorber — paused Server-3 result

## Status and claim limit

**Paused/abandoned before qualification.** This record reports only the
corrected v2 state and the solver evidence that was actually present before
the Server-3 Fluent stream disappeared. It is not a converged D0 result, not
a pressure-ladder result, and not evidence that the thin-ring intervention
worked. The old C8 lineage remains separately labeled **INCORRECT ABSORBER
(v1)**.

The post-stop direct endpoint check could not reconnect to Server 3, so the
final live GUI state cannot be claimed beyond the last local transcript and
the durable run manifests. No restart, recovery run, or pressure-child run
was attempted after the stop.

## Corrected state actually loaded

The D0 run loaded the prepared corrected all-wall pair:

- case: `C:\Users\syok443\OneDrive - The University of Auckland\P4P-Fluent-Artifacts\Phase07\C8-v2\20260922T120000Z\C8-V2-thin-outer-all-wall-prepared.cas.h5`
- data: matching `C8-V2-thin-outer-all-wall-prepared.dat.h5`
- mesh: `237,137` cells;
- lower absorber zone: `p71a-v2-virtual-outlet`;
- v2 command at readback: `P71V2Command = 116.9200000000001 kg/s`;
- phase-2 mass source: `P71V2Sink`;
- matching phase-2 liquid momentum, `k`, and `epsilon` source hooks;
- direct phase-1 mass source: disabled;
- all five bottom bands, including the thin outer ring, remained walls;
- `steamoutlet` remained a pressure outlet at `1,120,000 Pa` gauge with
  phase-2 backflow volume fraction `0`.

The persisted v2 expressions were the throughput-controlled form
`P71V2Sink = -P71V2Command*P71V2Alpha/P71V2NormalizationVolume`, with the
normalization volume floored at `1e-6 m^3`. The prepared pair was reopened and
the same source and boundary state was read back before iteration.

## Solver evidence present before the stop

The prepared pair and `active000` pair were written. The inherited Fluent
global iteration was `5000`; the transcript then contains eight completed
iterations, `5001` through `5008`, before the automation failed with
`RuntimeError: Stream removed (Socket closed)`. No later checkpoint was
written, and no valid active-iteration checkpoint beyond `active000` is
claimed.

| Fluent iteration | continuity | x-velocity | y-velocity | z-velocity | k | epsilon | phase-2 vf |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 5000 (start) | 1.3096e-1 | 1.3555e-4 | 1.6188e-4 | 1.3393e-4 | 7.1641e-3 | 2.9470e-2 | 5.6553e-3 |
| 5008 (last captured) | 1.3276e-1 | 1.3677e-4 | 1.5669e-4 | 1.3667e-4 | 7.5457e-3 | 2.8400e-2 | 5.6132e-3 |

During the captured block:

- reverse flow was reported on `1,139–1,156` faces of pressure-outlet zone
  `42`;
- turbulent-viscosity limiting at the `1e5` viscosity-ratio cap increased
  from `19,284` to `20,182` cells;
- continuity, `k`, `epsilon`, and phase-2 volume-fraction residuals remained
  above their configured convergence criteria at the last captured point;
- the thin-ring trigger was never evaluated as satisfied, the ring was never
  opened, and no pressure child was started.

This is therefore a short, non-stationary numerical snapshot. The residual
and reverse-flow evidence is useful for diagnosing why the branch was stopped,
but it cannot support a steady-state or separation-performance claim.

## Durable machine evidence

- local run manifest:
  [C8-D0-V2 run manifest](c8-v2-supervised-20260922T120000Z/c8-d0-v2/run-manifest.json)
- captured solver transcript:
  [C8-D0-V2 transcript](c8-v2-supervised-20260922T120000Z/c8-d0-v2/transcript.txt)
- supervisor record:
  [C8 v2 supervisor manifest](c8-v2-supervised-20260922T120000Z/supervisor-manifest.json)
- prepared/baseline provenance:
  [v2 baseline build manifest](c8-v2-baselines-20260922T120000Z/build-manifest.json)

The supervisor and D0 records are retained as blocked/partial execution
evidence. They must not be interpreted as completion of the planned
`1.120/1.110/1.090/1.060 MPa` family.
