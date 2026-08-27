> **Legacy source:** Setups/reports/full-geometry/mixture/steady-liquid-outlet/02c/future-runs.md  
> **Migration note:** Historical wording, evidence status, and uncertainty labels are preserved; this Project copy is not a reinterpretation. Raw and machine-generated artifacts remain at their legacy paths.

# Setup 02c — Future Pressure-Point Placeholders

This page contains no unverified numerical performance claims. It fixes the remaining experimental matrix and records the execution provenance/evidence required for a valid comparison with [Case B](results.md).

## Scope amendment — 2026-08-16

At the user's request, the former upper-pressure H20–H50 and I20–I160 sweeps are cancelled and are no longer future work. The only current upper-pressure point is `02c-H` at `1.140 MPa`; it was built and run on the Student endpoint from the explicit Student pre-initialization surrogate, and its verified 500-iteration endpoint is recorded in [02c results](results.md). The historical H/I preparation notes below are retained only as an evidence trail for artifacts that had already been prepared or smoke-tested; do not submit those queues or create additional members under those former IDs. This scope amendment did not contact or modify the separate server-1 Fluent session that had previously accepted the H20–H50 queue.

### Current single H point — completed

| Case | Brine pressure | Steam pressure | Status |
|---|---:|---:|---|
| `02c-H` | `1.140 MPa` | `1.120 MPa` | Student-native 500-iteration endpoint verified and post-processed; unstable / indeterminate, not converged |

Student endpoint: `C:\Users\Shuhei Yokkaichi\Documents\CFD\Test case\02c-H-brine-p1140kpa-unprimed-student-iter500-20260816T091812Z.cas.h5` with matching `.dat.h5`. The endpoint has zero vapour flux through the brine outlet by the selected absolute-flow extraction, but the raw liquid brine flux is positive (`+616.795 kg/s`), indicating reverse flow into the domain; continuity ends at `2.288839e-1` and turbulent-viscosity limiting is present. This is execution and diagnostic evidence only, not a pressure-selection result.

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
| `02c-D` | `1.1225 MPa` | `+2.5 kPa` | `02c-D-brine-p1122p5kpa-unprimed-preinit-20260812T102345Z.cas.h5` | paired 500-iteration endpoint verified and post-processed; directional candidate, unresolved liquid state |
| `02c-E` | `1.1275 MPa` | `+7.5 kPa` | `02c-E-brine-p1127p5kpa-unprimed-preinit-20260812T102546Z.cas.h5` | paired 500-iteration endpoint verified and post-processed; inventory-draining / unresolved |
| `02c-F` | `1.1300 MPa` | `+10.0 kPa` | `02c-F-brine-p1130kpa-unprimed-preinit-20260812T102700Z.cas.h5` | paired 500-iteration endpoint verified and post-processed; inventory-draining / unresolved |
| `02c-G` | `1.1350 MPa` | `+15.0 kPa` | `02c-G-brine-p1135kpa-unprimed-preinit-20260812T102800Z.cas.h5` | paired 500-iteration endpoint verified and post-processed; inventory-draining / unresolved |

For each point: load its own pre-initialization child, Hybrid Initialize without a liquid patch, run one native `500`-iteration screen, and write a paired case/data endpoint before loading the next child. Do not use a preceding pressure point's case/data as an initial condition. The queue's first native-autosave configuration attempt stopped at an interactive-menu argument mismatch before Case D started, so the launched fallback queue uses the verified explicit paired end-of-screen write; it still preserves every *completed* screen before advancing. Capture outlet phase flows and total continuous-liquid inventory at consistent intervals when the monitor definitions are available; the latter determines whether Case C-like high liquid drainage is settling or simply depleting initial inventory.

### Native sequential queue launch — 2026-08-14 (NZST)

- Queue order: `02c-D` → paired endpoint save → `02c-E` → paired endpoint save → `02c-F` → paired endpoint save → `02c-G` → paired endpoint save.
- Fluent-native journal: `C:\Users\syok443\P4P simulation\brine outlet\02c-positive-backpressure-queue-20260813T205605Z.jou`.
- Queue transcript: `C:\Users\syok443\P4P simulation\brine outlet\02c-positive-backpressure-queue-20260813T205605Z.trn`.
- Launch evidence: Fluent accepted the quoted journal path, started the transcript, accepted the residual-monitor setup, and began loading Case D's independent pre-initialization case.
- Initial queue status: `RUNNING / completion unverified` while Fluent was busy. Subsequent read-only remote file checks verified all four paired endpoint case/data files, and explicit reloads confirmed Fluent 2025 R2 could read each endpoint for post-processing. No endpoint was inferred from the queue transcript alone.
- Limitation: the present queue records residual history and a final paired checkpoint per case. Existing liquid-inventory monitor definitions were not present in the frozen children, so inventory-versus-iteration remains a required follow-up measurement rather than an artifact manufactured by this queue.
- Post-processing record: [02c results](results.md) contains the comparison dashboard, per-case D–G endpoint metrics, residual links, model audits, and complete inherited-DPM bundles. The vapour-routing direction strengthens across D–G, but D–G remain early numerical diagnostics without liquid-inventory histories or a common stable window.
- Next action: instrument total continuous-liquid inventory, lower-vessel/pipe-entry pressure diagnostics, and the agreed visual outputs; then continue only bracket-adjacent points from the frozen parent under a common stability gate. Do not treat E–G liquid outflow above inlet as demonstrated recovery or as proof of a drainage limit.

## Historical cancelled preparation — former H20 to H50 sweep

This is an explicit 02c amendment following the D–G result. Here `+20` through `+50 kPa` means above the nominal `1.140 MPa` inlet reference/initial gauge pressure, not above the `1.120 MPa` steam outlet. The resulting brine-outlet pressures are `1.160` through `1.190 MPa`; the steam outlet remains fixed at `1.120 MPa`. The sweep is intended to locate the broad response direction and any obvious reverse-flow/liquid-accumulation regime before finer tuning.

| Case | Brine pressure | Above inlet reference | Above steam outlet | Pre-initialization artifact | Planned endpoint |
|---|---:|---:|---:|---|---|
| `02c-H20` | `1.160 MPa` | `+20 kPa` | `+40 kPa` | `brine-p1160kpa-unprimed-preinit-<build-stamp>.cas.h5` | 500 iterations |
| `02c-H25` | `1.165 MPa` | `+25 kPa` | `+45 kPa` | `brine-p1165kpa-unprimed-preinit-<build-stamp>.cas.h5` | 500 iterations |
| `02c-H30` | `1.170 MPa` | `+30 kPa` | `+50 kPa` | `brine-p1170kpa-unprimed-preinit-<build-stamp>.cas.h5` | 500 iterations |
| `02c-H35` | `1.175 MPa` | `+35 kPa` | `+55 kPa` | `brine-p1175kpa-unprimed-preinit-<build-stamp>.cas.h5` | 500 iterations |
| `02c-H40` | `1.180 MPa` | `+40 kPa` | `+60 kPa` | `brine-p1180kpa-unprimed-preinit-<build-stamp>.cas.h5` | 500 iterations |
| `02c-H45` | `1.185 MPa` | `+45 kPa` | `+65 kPa` | `brine-p1185kpa-unprimed-preinit-<build-stamp>.cas.h5` | 500 iterations |
| `02c-H50` | `1.190 MPa` | `+50 kPa` | `+70 kPa` | `brine-p1190kpa-unprimed-preinit-<build-stamp>.cas.h5` | 500 iterations |

Controls remain frozen to the same 02c parent. Only the brine-outlet mixture-phase gauge pressure changes. The queue must reload each independent pre-initialization child, Hybrid Initialize without a liquid patch, run 500 Fluent-native iterations, save a paired endpoint, then advance to the next child. No Python iteration loop is permitted.

This coarse sweep requires a common monitor package before interpretation: brine/steam liquid and vapour flows, total continuous-liquid inventory, lower-vessel and brine-pipe-entry pressure diagnostics, reverse-flow warnings, residuals, and the agreed field visuals. A pressure above the nominal inlet reference is a testable hypothesis, not proof that the local static pressure should be higher; the inlet reference is not a fixed pressure boundary because both inlets remain velocity inlets.

### H20–H50 native queue launch — 2026-08-16 (UTC)

- Build manifest: `PyAnsys/output/02c-above-inlet-20-to-50-build-20260816T002025Z.json`.
- Every H20–H50 pre-initialization child was written and reload-verified against the frozen parent before queue submission.
- Local journal: `PyAnsys/output/02c-above-inlet-20-to-50-queue-20260816T003500Z.jou`.
- Remote journal: `C:\Users\syok443\P4P simulation\brine outlet\02c-above-inlet-20-to-50-queue-20260816T003500Z.jou`.
- Remote transcript: `C:\Users\syok443\P4P simulation\brine outlet\02c-above-inlet-20-to-50-queue-20260816T003500Z.trn`.
- Queue order: `02c-H20` → `H25` → `H30` → `H35` → `H40` → `H45` → `H50`; each member uses Hybrid Initialization, 500 native steady iterations, paired case/data write, and then advances.
- Current launch state: `RUNNING / H20 active; completion unverified`. Early H20 iterations show reverse flow on both pressure outlets and turbulent-viscosity limiting; this is recorded as a diagnostic signal, not yet as a failed endpoint.
- No Python iteration loop, pressure rescue, numerical tuning, or queue interruption was issued. If Fluent becomes unavailable, stop the queue and record the affected case rather than launching a replacement solver.

## Historical cancelled preparation — former I20 to I160 sweep

This separate, intentionally coarser amendment retains the same frozen 02c-B pre-initialization parent and changes only the brine-outlet mixture-phase gauge pressure. It uses `20 kPa` increments above the `1.140 MPa` inlet reference to test up to `1.300 MPa`. The inlet reference is not a fixed pressure boundary because both inlets remain velocity inlets; this is therefore a broad diagnostic screen, not a pressure-selection or drainage-limit claim.

| Case | Brine pressure | Above inlet reference | Above steam outlet | Planned case-only suffix |
|---|---:|---:|---:|---|
| `02c-I20` | `1.160 MPa` | `+20 kPa` | `+40 kPa` | `brine-p1160kpa-unprimed-coarse130` |
| `02c-I40` | `1.180 MPa` | `+40 kPa` | `+60 kPa` | `brine-p1180kpa-unprimed-coarse130` |
| `02c-I60` | `1.200 MPa` | `+60 kPa` | `+80 kPa` | `brine-p1200kpa-unprimed-coarse130` |
| `02c-I80` | `1.220 MPa` | `+80 kPa` | `+100 kPa` | `brine-p1220kpa-unprimed-coarse130` |
| `02c-I100` | `1.240 MPa` | `+100 kPa` | `+120 kPa` | `brine-p1240kpa-unprimed-coarse130` |
| `02c-I120` | `1.260 MPa` | `+120 kPa` | `+140 kPa` | `brine-p1260kpa-unprimed-coarse130` |
| `02c-I140` | `1.280 MPa` | `+140 kPa` | `+160 kPa` | `brine-p1280kpa-unprimed-coarse130` |
| `02c-I160` | `1.300 MPa` | `+160 kPa` | `+180 kPa` | `brine-p1300kpa-unprimed-coarse130` |

### Preparation state — 2026-08-16 (UTC)

- The case-only builder and a separate local native journal were prepared for I20 → I40 → I60 → I80 → I100 → I120 → I140 → I160. The journal is 02c-above-inlet-20-to-130-coarse-queue-20260816T014600Z.jou (historical machine artifact path: `../../../PyAnsys/output/02c-above-inlet-20-to-130-coarse-queue-20260816T014600Z.jou`; not migrated).
- The journal is **not submitted**. It would later load each independently parent-derived child, Hybrid Initialize, run `500` native steady iterations, write a unique paired endpoint, and then advance.
- `Observed`: the currently accessible idle Fluent session did not expose the exact frozen 02c-B parent path. The case-only build therefore stopped before any new child, initialization, iteration, data write, or journal submission. No I pre-initialization case exists yet.
- The next build must reconnect to an idle Fluent session that can read the documented frozen parent, then verify each I child by reload/readback before any journal is authorized.

### Student-only I20/I40/I60 50-iteration smoke — 2026-08-16 (UTC)

The requested first three I members were also exercised on the Student endpoint as an automation diagnostic, after the user authorized replacing the current Student state. This does **not** resolve the production-parent blocker above. Each child was built independently from the saved Student surrogate `02c-C-brine-p1125kpa-unprimed-preinit-20260815T231711Z.cas.h5`, then the submitted native journal loaded that child, Hybrid Initialized, iterated `50`, and wrote a paired endpoint.

| Case | Brine gauge pressure | Reload verification |
|---|---:|---|
| `02c-I20` | `1.160 MPa` | paired case/data visible and reopened; 50 residual points through iteration 50 |
| `02c-I40` | `1.180 MPa` | paired case/data visible and reopened; 50 residual points through iteration 50 |
| `02c-I60` | `1.200 MPa` | paired case/data visible and reopened; 50 residual points through iteration 50 |

The local journal is `PyAnsys/output/02c-student-I20-I60-iter50-20260816T020800Z.jou`; the Student-host transcript is `C:\\Users\\Shuhei Yokkaichi\\Documents\\CFD\\Test case\\02c-student-I20-I60-iter50-20260816T020800Z.trn`. Each reloaded endpoint retained steady Mixture/RNG k-epsilon and steam outlet `1.120 MPa`. The execution emitted reverse-flow and turbulent-viscosity-limit diagnostics, so it passes the execution-integrity smoke criterion only—not convergence, mesh parity, DPM parity, or 02c pressure-performance interpretation.
