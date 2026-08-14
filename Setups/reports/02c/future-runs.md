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

## Positive-backpressure extension — Cases D/E/F/G

The observed A/B/C early-screen vapour routing is sufficiently promising to extend the test domain above the fixed `1.120 MPa` steam outlet. This is an intentional amendment to setup `02c`, not a claim that Case C selected an operating pressure.

| Case | Brine gauge pressure | ΔP versus steam outlet | Pre-initialization remote case | Status |
|---|---:|---:|---|---|
| `02c-D` | `1.1225 MPa` | `+2.5 kPa` | `02c-D-brine-p1122p5kpa-unprimed-preinit-20260812T102345Z.cas.h5` | case-only prepared |
| `02c-E` | `1.1275 MPa` | `+7.5 kPa` | `02c-E-brine-p1127p5kpa-unprimed-preinit-20260812T102546Z.cas.h5` | case-only prepared |
| `02c-F` | `1.1300 MPa` | `+10.0 kPa` | `02c-F-brine-p1130kpa-unprimed-preinit-20260812T102700Z.cas.h5` | case-only prepared |
| `02c-G` | `1.1350 MPa` | `+15.0 kPa` | `02c-G-brine-p1135kpa-unprimed-preinit-20260812T102800Z.cas.h5` | case-only prepared |

For each point: load its own pre-initialization child, Hybrid Initialize without a liquid patch, run one native `500`-iteration screen, and write a paired case/data endpoint before loading the next child. Do not use a preceding pressure point's case/data as an initial condition. The queue's first native-autosave configuration attempt stopped at an interactive-menu argument mismatch before Case D started, so the launched fallback queue uses the verified explicit paired end-of-screen write; it still preserves every *completed* screen before advancing. Capture outlet phase flows and total continuous-liquid inventory at consistent intervals when the monitor definitions are available; the latter determines whether Case C-like high liquid drainage is settling or simply depleting initial inventory.

### Native sequential queue launch — 2026-08-14 (NZST)

- Queue order: `02c-D` → paired endpoint save → `02c-E` → paired endpoint save → `02c-F` → paired endpoint save → `02c-G` → paired endpoint save.
- Fluent-native journal: `C:\Users\syok443\P4P simulation\brine outlet\02c-positive-backpressure-queue-20260813T205605Z.jou`.
- Queue transcript: `C:\Users\syok443\P4P simulation\brine outlet\02c-positive-backpressure-queue-20260813T205605Z.trn`.
- Launch evidence: Fluent accepted the quoted journal path, started the transcript, accepted the residual-monitor setup, and began loading Case D's independent pre-initialization case.
- Initial queue status: `RUNNING / completion unverified`. Two later bounded read-only reconnect attempts found the TCP endpoint reachable but did not regain the PyFluent handoff while Fluent was busy. No additional solver command, reload, interruption, exit, or new Fluent process was issued.
- Limitation: the present queue records residual history and a final paired checkpoint per case. Existing liquid-inventory monitor definitions were not present in the frozen children, so inventory-versus-iteration remains a required follow-up measurement rather than an artifact manufactured by this queue.
