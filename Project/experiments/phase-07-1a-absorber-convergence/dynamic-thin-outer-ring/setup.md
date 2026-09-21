# Independent C8 dynamic thin-outer-ring family

## Status

**Historical — INCORRECT ABSORBER (v1), superseded on 2026-09-22.** The
preserved C8-D0/C8-P0 records below used the former lower-inventory/uniform
absorber and must not be used as v2 pressure-family parents. The human has now
reauthorized a corrected Server-3 family using the Phase 7.1A v2
throughput-controlled phase-2 absorber. This record remains the provenance of
the old pressure ladder and its raw evidence.

## Scope and parent

C8 is an independent Server-3 discovery family. It uses no C7 or Server-1
artifact. Every C8 pressure child reads the same immutable paired C8-D0 parent:

- case: `C:\Users\syok443\OneDrive - The University of Auckland\P4P-Fluent-Artifacts\Phase07\C8\independent-d0-finals\C8-D0\20260921T062500Z\C8-D0-active5000.cas.h5`
- data: matching `C8-D0-active5000.dat.h5`
- C8-D0 hashes: case `fb943ace44424ce1edfdf8e966e85bfb5bc5f55188098df48278fa703ae3543b`; data `018124b04faa7ddec37daf17b78b0e1cc6f758fc7d71a36299657bf68e41154e`.

C8-D0 is complete: it used 0.25 of the liquid inlet, vapor inlet, and
phase-2 lower-absorber command at active 0; ramped all three linearly to base
through active 2,000; then held base commands to active 5,000. All five bottom
bands remained walls. The terminal readback retained mixture/RNG, base liquid
and vapor inlets of 116.92 and 80.69 kg/s, and a phase-2-only lower-zone
absorber integral of -116.92 kg/s.

## Dynamic-switch rule

The trigger receipt is
[`c8-d0-trigger-receipt-20260921T062500Z.json`](c8-d0-trigger-receipt-20260921T062500Z.json).
It derives the following rule from raw C8-D0 active-4,000--5,000
`absorb-lower-liquid-mass` history:

| Quantity | Value |
| --- | ---: |
| Late-window median lower liquid mass | 28.67767752217757 kg |
| Opening threshold | 22.942142017742057 kg (0.80 × median) |
| Cadence | 10 active iterations |
| Persistence | 20 consecutive samples (200 active iterations) |

Every pressure child begins with all five bottom bands as walls. At the first
satisfied persistence sample it must save a local pre-switch pair, change only
`bottom-bottom-band1-thin-outer-separator-purnanto` to a pressure outlet,
read back its gauge pressure and phase-2 backflow fraction, save a local
post-switch pair, and continue. The other four bottom bands remain no-slip
walls. No initialization, patch, remesh, solver/turbulence retune, inlet
change, or absorber retune is permitted.

## Stage 1

Each packet has a 5,000-active-iteration horizon, fresh C8-D0 parent read,
file-backed residual/inventory/inlet/steam-outlet/ring-phase-flux evidence,
and local checkpoints at active 1,000--4,000. Only its terminal or last-valid
paired case/data is eligible for C8 OneDrive publication.

| Packet | Outer-ring gauge pressure |
| --- | ---: |
| C8-P0 | 1.120 MPa |
| C8-P10 | 1.110 MPa |
| C8-P30 | 1.090 MPa |
| C8-P60 | 1.060 MPa |

Run sequentially only. A sustained vapor-dominated ring outflow, unacceptable
phase/mixture accounting, destructive reverse flow, or solver failure blocks
later pressure points until the C8 evidence is assessed. Stage 2 is eligible
only if Stage 1 establishes a least-aggressive useful pressure.

## Current preserved C8-P0 state

The first executable C8-P0 attempt was an instrumentation-only failure before
iteration because ring report files were not recreated after the base monitor
reset. The corrected retry is preserved, **stopped rather than complete**:

- local run record:
  [`c8-p0-retry-20260921T074500Z/run-manifest.json`](c8-p0-retry-20260921T074500Z/run-manifest.json)
- outer-ring switch: active 200 at 1.120 MPa, after 20 persistent samples;
- file-backed monitor history extends to native iteration 7,800, equivalent to
  C8-P0 active 2,800 from the active-5,000 D0 parent;
- last planned paired checkpoint known to be written locally: C8-P0 active
  2,000. No active-3,000 or terminal C8-P0 pair is claimed.

The paused state is a workflow stop, not a numerical completion or a
scientific rejection.
