# Setup 02c — Future Pressure-Point Placeholders

This page contains no unverified numerical performance claims. It fixes the remaining experimental matrix and records the execution provenance/evidence required for a valid comparison with [Case B](results.md).

## Frozen common protocol

For every future point, rebuild from the Case B pre-initialization parent snapshot, not from a solved Case B field:

`C:\Users\syok443\P4P simulation\brine outlet\02c-B-brine-p1120kpa-unprimed-preinit-20260812T043007Z.cas.h5`

Hold fixed: mesh; zones; Mixture/RNG k-epsilon model; gravity; operating pressure; split velocity-inlet values; inlet volume fractions; steam-outlet pressure; walls; materials; numerical controls; and no-liquid-patch Hybrid Initialization. Record any deviation as a new branch.

Each point requires a unique paired case/data checkpoint at iteration 500, explicit reload for analysis, carrier flux/residual extraction, audit, DPM sweep if inherited injections remain active, and the same sign convention as Case B.

## Case A — lower brine pressure

| Field | Required value |
|---|---|
| Case ID | `02c-A` |
| Brine outlet gauge pressure | `1.115 MPa` (`1,115,000 Pa`) |
| Steam outlet gauge pressure | `1.120 MPa` |
| Status | built, Hybrid Initialized without liquid patch, run, and post-processed as a preliminary 649-iteration diagnostic; see [results](results.md) |
| Intended comparison | whether lower brine pressure improves liquid drainage while increasing/decreasing vapour wrong-outlet fraction |

Record after execution: checkpoint paths, achieved iterations, final residuals, liquid inlet/brine/steam flows, vapour inlet/brine/steam flows, liquid closure error, steam wrong-outlet fraction, liquid inventory trend, pressure diagnostics, visual outputs, and complete DPM bundle when applicable.

Execution record (not a convergence or performance claim):

- Parent explicitly loaded: `C:\Users\syok443\P4P simulation\brine outlet\02c-B-brine-p1120kpa-unprimed-preinit-20260812T043007Z.cas.h5`.
- Case A pre-initialization snapshot: `C:\Users\syok443\P4P simulation\brine outlet\02c-A-brine-p1115kpa-unprimed-preinit-20260812T050411Z.cas.h5`.
- The requested 500-iteration milestone was reached. A recovery continuation overlapped the already advancing native solve and was allowed to complete rather than being interrupted; the final endpoint is 649 iterations.
- Verified paired final checkpoint: `C:\Users\syok443\P4P simulation\brine outlet\02c-A-brine-p1115kpa-unprimed-iter649-20260812T051900Z.cas.h5` and `C:\Users\syok443\P4P simulation\brine outlet\02c-A-brine-p1115kpa-unprimed-iter649-20260812T051900Z.dat.h5`.
- A separate recoverable intermediate pair written during the asynchronous status check is named `...iter500-20260812T051350Z`; it actually represents an approximately 351-iteration state and must not be used as an iteration-500 result.
- Live monitoring near the final continuation showed continuity around `8.8e-2` to `1.1e-1`, persistent reverse flow at the steam outlet (about 290–320 faces), and occasional turbulent-viscosity limiting. Treat the checkpoint as a preliminary screen until full carrier/phase-flux and convergence analysis is completed.

## Case C — higher brine pressure

| Field | Required value |
|---|---|
| Case ID | `02c-C` |
| Brine outlet gauge pressure | `1.125 MPa` (`1,125,000 Pa`) |
| Steam outlet gauge pressure | `1.120 MPa` |
| Status | built, Hybrid Initialized without liquid patch, run through the native Fluent TUI 500-iteration screen, and post-processed as an early diagnostic; see [results](results.md) |
| Intended comparison | whether higher brine pressure reduces vapour short-circuit while retaining adequate liquid drainage |

Record the same fields and evidence set as Case A and Case B.

Execution record (not a convergence or performance claim):

- Parent explicitly loaded: `C:\Users\syok443\P4P simulation\brine outlet\02c-B-brine-p1120kpa-unprimed-preinit-20260812T043007Z.cas.h5`.
- Only brine-outlet mixture-phase momentum gauge pressure was changed, to `1.125 MPa`; liquid backflow volume fraction read back as `1.0`.
- Pre-initialization snapshot: `C:\Users\syok443\P4P simulation\brine outlet\02c-C-brine-p1125kpa-unprimed-preinit-20260812T052700Z.cas.h5`.
- Fluent-native TUI sequence: Hybrid Initialization, then `solve/iterate 500`.
- Verified paired final checkpoint: `C:\Users\syok443\P4P simulation\brine outlet\02c-C-brine-p1125kpa-unprimed-iter500-20260812T055550Z.cas.h5` and `C:\Users\syok443\P4P simulation\brine outlet\02c-C-brine-p1125kpa-unprimed-iter500-20260812T055550Z.dat.h5`.
- Near iteration 495, continuity was `1.172346e-1`; reverse flow persisted at the steam outlet and occasional turbulent-viscosity limiting was observed. Explicit-reload analysis is required before numerical interpretation.

## Comparison gate after A/B/C

Do not rank the three pressures by a single outlet quantity. Compare only a common stable window, or explicitly label the comparison as early-iteration screening. A candidate pressure must be assessed jointly for:

1. liquid closure error;
2. brine liquid-recovery fraction;
3. vapour wrong-outlet fraction;
4. residual/monitor maturity and liquid-inventory trend; and
5. visual evidence near the lower vessel, brine-pipe entrance, brine pipe, steam core, and steam outlet.

Case B supplies only an early-screening reference; it is not a steady benchmark for selecting A or C.
