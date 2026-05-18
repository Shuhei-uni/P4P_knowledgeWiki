# Experiment Log

## Run Template
- Run ID:
- Date:
- Objective:
- Geometry:
- Mesh:
- Physics model:
- Solver settings:
- Boundary and initial conditions:
- Iteration budget:
- Convergence monitors:
- Outcome:
- Hypothesized cause (if non-converged):
- Next action:

## Runs

### Run BGM-2026-04-22-A
- Run ID: `BGM-2026-04-22-A`
- Date: 2026-04-22
- Objective: Recreate legacy Bangma-based two-phase baseline and test convergence readiness.
- Geometry: Bangma-based model provided by supervisor/team.
- Mesh: approximately 300k nodes (reported).
- Physics model: two-phase cyclone separator recreation (details pending confirmation).
- Solver settings: ran to 1000 iterations (detailed numerics pending explicit capture).
- Boundary and initial conditions: pending full setting audit.
- Iteration budget: 1000 iterations.
- Convergence monitors: residual trend indicates non-convergence.
- Outcome: `Stalled`.
- Hypothesized cause (if non-converged): mesh may be under-resolved, flow/BC settings may be incomplete or inconsistent.
- Next action: perform full solver/BC audit against `purnanto-zarrouk-cater-2013` technical notes, then rerun with controlled setting changes.
