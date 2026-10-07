# Phase 8 — Stage 2 fine-mesh SIMPLE reconstruction

## Status

| Item | Current contract |
| --- | --- |
| Authority | Shuhei, 7 October 2026; current chat |
| Active work | Stage 2 F2–SIMPLE, 997,604 cells, nominal 26.81 m/s, 5,000 total solve iterations |
| Stage 1 | All prior Phase 8 families, settings, results and limitations retained in [Stage 1](stage-01-60k-storyline/index.md) |
| F0 | Deferred while Shuhei makes a genuine single-inlet mesh |
| Session control | Server 2 only; preserve a loaded paired endpoint before replacement; never exit or terminate Fluent |
| Other work | Phase 9 and other owners' campaigns remain separate |

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
| Selected contrast | Stage 2 F2 on 997k versus retained Stage 1 evidence; changed mesh and startup preclude an isolated mesh-error claim |
| Carrier | Steady pressure-based Mixture, RNG k-epsilon; SIMPLE; pseudo time off |
| Spatial schemes | PRESTO pressure; second-order momentum, k and epsilon; QUICK volume fraction; Green-Gauss node gradients |
| Feed | Pure phase-2 liquid on liquidinlet; pure phase-1 steam on steaminlet; same Stage 1 total feed basis |
| Fixed scope | Closed bottom; smooth walls; absorber, EWF and DPM feedback off; carrier solve only |
| Startup | Fresh low-feed initialization; 500 iterations at 5%; ramp to full feed over next 1,500; full feed from N2000 through N5000 |
| Budget | Exactly 5,000 total solve iterations, including verification updates; no extra continuation |
| Evidence | Paired start/checkpoints/end; readback and mesh identity; phase/native-mixture fluxes, liquid inventory, pressure and residual histories; native liquid/velocity views |
| Claim limit | One fine-mesh carrier result; no mesh independence, physical validation, steady drainage or separator-efficiency claim |

## Candidate families

| Family | Selection | Controlled change |
| --- | --- | --- |
| F2–SIMPLE | Run now | Finer supplied split-inlet mesh; bounded low-feed/ramp startup |
| F0–SIMPLE | Wait for human mesh | Genuine single mixed inlet; future matching settings and feed |
| F1 / F3 / F4 | No new runs | Existing Stage 1 evidence only |

## Decision conditions

| Condition | Action |
| --- | --- |
| Routine setup or code fault before solving | Repair in scope; preserve evidence |
| Numerical warnings / poor balances | Record; do not change algorithm, physics or horizon solely to pass thresholds |
| N5000 reached | Save and verify final pair, analyse evidence, stop |
| Fluent process failure | Preserve recoverable evidence; do not issue exit, termination or automatic restart |
| Scientific scope change | Return to Shuhei |
