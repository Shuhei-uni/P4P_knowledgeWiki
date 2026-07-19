# Technical Setup Report Template

Use this template for setup-instance companion reports that focus on the actual Fluent export, geometry/mesh handling, and report-vs-extraction drift.

## 1. Purpose

- Record the machine-extracted Fluent state for one concrete setup.
- Separate actual Fluent export values from the human-facing narrative report.
- Capture human-error candidates explicitly when the report and the export disagree.
- Keep geometry, meshing, setup, and run-control details in one place without duplicating the whole lineage story.

Rule:

- if the Fluent export and the human report disagree, treat the export as the replay authority and record the report text as the intended or narrative interpretation.

## 2. Sources

| Item | Path | Notes |
|---|---|---|
| Fluent export archive | `...` | Primary machine-readable source |
| Narrative setup report | `...` | Human-facing companion report |
| Related intended-vs-actual note | `...` | Optional drift companion |
| Supporting notes | `...` | Optional scratch or extraction note |

## 3. Setup Identity

| Field | Value | Status | Notes |
|---|---|---|---|
| Setup label | `...` |  |  |
| Fluent version | `...` |  |  |
| Geometry label | `...` |  |  |
| Boundary topology | `...` |  |  |
| Multiphase model | `...` |  |  |
| Solver family | `...` |  |  |
| DPM state | `...` |  |  |

## 4. Geometry And Mesh

| Topic | Human report says | Extracted Fluent state | Status | Notes |
|---|---|---|---|---|
| CAD / physical geometry | `...` | `...` |  |  |
| Mesh type | `...` | `...` |  |  |
| Mesh control settings | `...` | `...` |  |  |
| Mesh quality or count | `...` | `...` |  |  |

If the archive does not serialize a geometry or mesh detail, say so explicitly rather than inferring it.

## 5. Fluent Setup

| Topic | Human report says | Extracted Fluent state | Status | Notes |
|---|---|---|---|---|
| Solver / time | `...` | `...` |  |  |
| Operating conditions | `...` | `...` |  |  |
| Models | `...` | `...` |  |  |
| Materials | `...` | `...` |  |  |
| Cell zones | `...` | `...` |  |  |

## 6. Boundary Conditions

| Boundary | Human report says | Extracted Fluent state | Status | Notes |
|---|---|---|---|---|
| Inlet | `...` | `...` |  |  |
| Outlet | `...` | `...` |  |  |
| Walls | `...` | `...` |  |  |

## 7. Solution, Initialization, And Run Control

| Topic | Human report says | Extracted Fluent state | Status | Notes |
|---|---|---|---|---|
| Pressure-velocity coupling | `...` | `...` |  |  |
| Discretization schemes | `...` | `...` |  |  |
| Under-relaxation | `...` | `...` |  |  |
| Initialization | `...` | `...` |  |  |
| Iteration count | `...` | `...` |  |  |
| Residual criteria | `...` | `...` |  |  |

## 8. Drift Log

List only the differences that matter for replay, validation, or interpretation.

| Topic | Reported | Extracted | Drift type | Action |
|---|---|---|---|---|
| `...` | `...` | `...` | `match` / `rounded` / `intentional` / `human-error-candidate` / `not-serialized` | `...` |

## 9. Open Items

- Items that remain unresolved after the extraction.
- Items that require a user decision.
- Items that need a follow-up Fluent inspection.

