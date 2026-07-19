# Setup <ID> — <short setup name>

## Setup metadata

| Field | Value |
|---|---|
| Setup ID | `<ID>` |
| Lifecycle | `active` / `future` / `reported` / `archived` |
| Role | `reference` / `experiment` / `sensitivity` / `audit` |
| Parent setup | `<setup link or none>` |
| Child setups | `<links or none>` |
| Controlled changes | `<what differs from parent>` |
| Evidence-use label | `<diagnostic only / setup calculation only / report-quality / ...>` |
| Outcome | `keep` / `reject` / `needs follow-up` |
| Linked report | `<report link or none>` |

## 1. Objective

State the single experimental question this setup is intended to answer.

## 2. Inherited setup

Link the parent and summarize only the values inherited from it.

## 3. Controlled changes

List the variables intentionally changed in this branch. Keep unrelated settings fixed where possible.

## 4. Geometry and mesh

Record geometry identity, boundary topology, mesh source, mesh controls, and known mesh limitations.

## 5. Fluent setup

Record solver, models, materials, phases, operating conditions, numerics, initialization, and run controls.

## 6. Boundary conditions

Record every inlet, outlet, wall fate, phase fraction, velocity or mass flow, and backflow setting with units.

## 7. Acceptance checks

List the residual, mass/phase flux, mesh, and DPM checks required before interpreting the report.

## 8. Linked evidence

Link the results report, PyAnsys case/data artifacts, extracted settings, and relevant wiki evidence.
