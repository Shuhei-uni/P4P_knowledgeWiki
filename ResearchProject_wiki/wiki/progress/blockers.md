# Blockers

## Active Blockers

### BLK-001 | Baseline run not converging
- Status: Active
- First observed: 2026-04-22
- Related run(s): `BGM-2026-04-22-A`
- Symptom: no satisfactory convergence after 1000 iterations.

### BLK-002 | No interpretation framework for simulation outputs
- Status: Active
- First observed: 2026-04-22
- Related run(s): `BGM-2026-04-22-A` and follow-up runs
- Symptom: uncertainty about which outputs indicate separator performance and what model change should follow from results.

### BLK-003 | Split-inlet orientation and allocation not yet frozen
- Status: Active
- First observed: 2026-04-30
- Related run(s): next split-inlet A/B case
- Symptom: `left/right` wording is not precise enough to guarantee the correct wall-side vs inner-side phase placement on the spiral-inlet face.

## Ranked Hypotheses
1. Incomplete or incorrect boundary-condition setup relative to literature baseline.
2. Initialization strategy not robust enough for strong swirl two-phase setup.
3. Mesh resolution and/or near-boundary quality not sufficient for stable progression.
4. Missing stabilization tuning in numerics for this specific configuration.
5. No fixed KPI/monitor definition, causing unclear interpretation of whether the model is physically acceptable.
6. The first realistic-inlet case may be misapplied if the inlet-side orientation is not defined by geometry meaning.

## Recovery Plan
1. Audit current setup against technical checklist from `wiki/technical/sources/purnanto-etal-2013.md`.
2. Lock a minimal reproducible baseline definition in `wiki/model/baseline-cfd.md`.
3. Define a fixed post-processing template (contours + line probes + outlet mass-flow summaries).
4. Execute one-parameter-at-a-time reruns and log each run with KPI outcomes.
5. Trigger mesh refinement test only after setup audit is complete.
6. Freeze inlet-side naming as `outer liquid` and `inner steam` before building the split-inlet mesh.
