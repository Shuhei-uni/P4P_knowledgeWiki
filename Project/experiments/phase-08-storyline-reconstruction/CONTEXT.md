# Phase 8 — Stage 2 fine-mesh SIMPLE reconstruction

## Status

| Item | Current contract |
| --- | --- |
| Authority | Shuhei, 7 October 2026; current chat |
| Active work | Fresh 08b settings on new 997k mesh, absorber OFF; native 10,000-iteration run launched on Server 2; latest check cannot reach Fluent; run outcome unconfirmed; paired checkpoints set for every 1,000 |
| Stage 1 | All prior Phase 8 families, settings, results and limitations retained in [Stage 1](stage-01-60k-storyline/index.md) |
| F0 | Deferred while Shuhei makes a genuine single-inlet mesh |
| Session control | Server 2 only; preserve a loaded paired endpoint before replacement; never exit or terminate Fluent |
| Other work | Phase 9 and other owners' campaigns remain separate |

Active task: [08b settings on new997k OFF continuation](stage-02-fine-mesh-simple/08b-native997k/fresh-tui10000-off/setup.md). The revised stepped trial failed at N518 with the absorber ON at 25% feed; its paired failed endpoint is preserved. The previous low-feed run ended with a Cortex fatal signal after printed N350; N300 is save/reopen verified. The absorber-from-start run shut down before N1000; N600 is save/reopen verified. The absorber-OFF full-feed trial failed at N717 and remains a separate comparison. The earlier low-feed/ramp trial failed at N1422; its [results and checkpoints](stage-02-fine-mesh-simple/results.md) remain a separate record.

## Evidence anchors

| Evidence | Observation / limit |
| --- | --- |
| [Stage 1 F0](stage-01-60k-storyline/f0-simple/results.md) | Coarse SIMPLE carrier has large boundary errors and inventory drift |
| [Stage 1 lineage](stage-01-60k-storyline/baseline-lineage-audit.md) | SIMPLE/Coupled packages differ in pseudo time and turbulence discretization |
| [Mesh audit](../../../PyAnsys/output/phase9-mesh-convergence/20261007/mesh-input-audit.json) | Supplied 997k mesh has 997,604 cells; native scale and quality still require verification |

## Phase contract

| Item | Requirement |
| --- | --- |
| Question | What liquid distribution and carrier response does the finer split-inlet SIMPLE case produce? |
| Current diagnostic | Original 08b on the same 997k mesh; preserve archived settings and fields to examine setup differences |
| Prior selected contrast | Stage 2 F2 on 997k versus retained Stage 1 evidence; changed mesh and startup preclude an isolated mesh-error claim |
| Current parent | Exact original 08b case/data from `P4P-Fluent-Artifacts/08b`; preserve loaded parent settings |
| Prior Stage 2 carrier | Steady pressure-based Mixture, RNG k-epsilon; SIMPLE; pseudo time off |
| Prior Stage 2 spatial schemes | PRESTO pressure; second-order momentum, k and epsilon; QUICK volume fraction; Green-Gauss node gradients |
| Feed | Pure phase-2 liquid on liquidinlet; pure phase-1 steam on steaminlet; same Stage 1 total feed basis |
| Prior Stage 2 fixed scope | Closed bottom; smooth walls; corrected liquid contact absorber tau 10 microseconds; EWF and DPM feedback off; carrier solve only |
| Failed stepped-trial startup | Fresh25% feed with absorber off through N200; enable and hold25% to N700; 50% to N950; 75% to N1200; full feed to N2200 |
| Current budget | Fresh native Hybrid initialization; exactly10,000 carrier iterations; paired autosave every1,000 |
| Evidence | Paired start/checkpoints/end; readback and mesh identity; phase/native-mixture fluxes, liquid inventory, pressure and residual histories; native liquid/velocity views |
| Claim limit | One fine-mesh carrier result; no mesh independence, physical validation, steady drainage or separator-efficiency claim |

## Candidate families

| Family | Selection | Controlled change |
| --- | --- | --- |
| 08b settings on new997k | Fresh 10,000 OFF: endpoint unreachable, outcome unconfirmed | Native journal and checkpoints on Server2; no laptop dependency |
| F2–SIMPLE | Failed trials retained | Finer supplied split-inlet mesh; startup trials |
| F0–SIMPLE | Wait for human mesh | Genuine single mixed inlet; future matching settings and feed |
| F1 / F3 / F4 | No new runs | Existing Stage 1 evidence only |

## Decision conditions

| Condition | Action |
| --- | --- |
| Routine setup or code fault before solving | Repair in scope; preserve evidence |
| Numerical warnings / poor balances | Record; do not change algorithm, physics or horizon solely to pass thresholds |
| FreshN10000 reached | Native final save; host paired reopen/fields/report proof; stop |
| Fluent process failure | Preserve recoverable evidence; do not issue exit, termination or automatic restart |
| Scientific scope change | Return to Shuhei |

| Current authority | Updated selection |
| --- | --- |
| Human direction | Fresh initialization; nativeTUI10,000 iterations; save paired every1,000; absorberOFF; laptop mayclose |
| Session restart | Performed by Shuhei; new session attached by controller |
| Failure type | Previous Cortex/session error kept separate from floating-point solver failures |
