# Technical Setup Evidence Template

Use this companion when a machine-extracted Fluent state needs to be compared with the intended setup definition. This is an implementation/readback record, not a scientific interpretation report.

## 1. Purpose

- Record what Fluent actually exposes for one concrete case/checkpoint.
- Compare observed state with the intended setup contract.
- Identify replay-critical drift or uncertain extraction without deciding what the simulation result means.
- Provide evidence the implementation agent can use to correct or verify the case.

Authority rule:

- the **setup definition** records what the experiment intended;
- the **Fluent extraction** records what was actually observed in the loaded case;
- when they disagree, record the drift. Do not silently rewrite either source to make them agree.
- if the drift changes experimental meaning, hand the decision to the user or setup workflow.

## 2. Sources

| Item | Path | Role |
|---|---|---|
| Setup definition | `...` | Intended experiment/build contract |
| Fluent export / readback | `...` | Observed case state |
| Case/data checkpoint | `...` | Artifact identity |
| Supporting extraction | `...` | Optional raw evidence |

## 3. Case identity

| Field | Intended / recorded | Observed | Status / notes |
|---|---|---|---|
| Setup ID | `...` | `...` |  |
| Case/data filename | `...` | `...` |  |
| Fluent version | `...` | `...` |  |
| Geometry / mesh identity | `...` | `...` |  |
| Investigation mode | `...` | `n/a unless encoded` | context only |

Never infer case identity from a Fluent connection/server ID.

## 4. Geometry and mesh readback

| Topic | Intended setup | Observed Fluent state | Status | Notes |
|---|---|---|---|---|
| Boundary topology | `...` | `...` | `match / drift / uncertain / not serialized` |  |
| Mesh source/count | `...` | `...` |  |  |
| Relevant mesh controls | `...` | `...` |  |  |

If a detail is not serialized or observable, say so rather than inferring it.

## 5. Physics and solver readback

| Topic | Intended setup | Observed Fluent state | Status | Notes |
|---|---|---|---|---|
| Solver / steady-transient | `...` | `...` |  |  |
| Operating conditions | `...` | `...` |  |  |
| Models | `...` | `...` |  |  |
| Materials / phases | `...` | `...` |  |  |
| Cell zones | `...` | `...` |  |  |

## 6. Boundary conditions

| Boundary | Intended state | Observed state | Status | Notes |
|---|---|---|---|---|
| `<zone>` | `...` | `...` |  |  |

Preserve units, phase-specific values, backflow settings, profiles/UDFs, and any ambiguity that affects the experiment.

## 7. Initialization, numerics and run control

| Topic | Intended setup | Observed state | Status | Notes |
|---|---|---|---|---|
| Coupling / schemes | `...` | `...` |  |  |
| Under-relaxation / controls | `...` | `...` |  |  |
| Initialization / patching | `...` | `...` |  |  |
| Timestep / iteration controls | `...` | `...` |  |  |
| Monitor/report definitions | `...` | `...` |  |  |

## 8. Drift log

List only differences that matter for replay, controlled comparison, evidence collection, verification, or validation scope.

| Topic | Intended | Observed | Drift class | Why it matters | Action owner |
|---|---|---|---|---|---|
| `...` | `...` | `...` | `match / rounded / intentional / likely error / uncertain / not serialized` | `<effect on setup meaning>` | `agent / user decision / follow-up inspection` |

Do not label a drift as scientifically acceptable/unacceptable unless the setup already contains that criterion.

## 9. Evidence-collection readiness

When the setup names measurements that must exist before/during the solve, verify them here.

| Required evidence instrumentation | Observed state | Ready? | Notes |
|---|---|---|---|
| `<monitor/report/probe/history>` | `<...>` | `yes / no / uncertain` | `<...>` |

## 10. Open implementation decisions

- unresolved intended-vs-observed differences;
- items the implementation agent can repair without changing experimental meaning;
- items that require user direction because they would change the setup question or controlled comparison;
- follow-up readbacks needed before the case is considered build-verified.

Do not include scientific outcome interpretation here. That belongs in the setup-linked results report after evidence is collected and interpretation direction is established.
