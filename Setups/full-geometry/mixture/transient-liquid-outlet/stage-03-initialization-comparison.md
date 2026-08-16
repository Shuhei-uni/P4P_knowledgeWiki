# FG-MIX-T01 Stage 3 — Initialization Comparison

## Intent

| Field | Value |
|---|---|
| Stage ID | `FG-MIX-T01-S3` |
| Investigation mode | diagnostic / numerical sensitivity |
| Primary question | Does starting transient Mixture from the developed steady parent materially change the early transient trajectory compared with Fluent Hybrid Initialization when both receive the same Y010 patch? |
| Interpretation owner | user-led |
| Parent | [Stages 1–2 — Steady Parent and Transient Start States](stage-01-02-steady-parent-and-transient-start.md) |
| Comparison case | `T-PO-1`, Pressure Outlet at `1.200 MPa` gauge |

## Why this stage exists

The six-case campaign should not inherit an arbitrary initialization choice. This stage tests whether the developed steady flow field gives a cleaner or materially different transient startup than Fluent Hybrid Initialization.

The experiment is **not** patched versus unpatched. Both branches use the identical Y010 liquid patch. The only intended difference is the pre-patch flow field.

## Case matrix

| Case | Starting flow field | Brine outlet | Y010 patch | Purpose |
|---|---|---|---|---|
| `INIT-S` | accepted unpatched steady parent | Pressure Outlet `1.200 MPa` gauge | yes, once at `t=0` | developed-flow start |
| `INIT-H` | Fluent Hybrid Initialization | Pressure Outlet `1.200 MPa` gauge | yes, once at `t=0` | Fluent initialization control |

## Provisional transient method

Use one deliberately common method for both branches. This stage is not the final timestep qualification.

Suggested provisional controls:

- pressure-velocity coupling: `PISO` with neighbor correction;
- Mixture volume-fraction formulation: implicit;
- temporal discretization: bounded second-order implicit where startup remains stable;
- provisional timestep: `2.5e-4 s`;
- maximum iterations per timestep: `15–20`;
- fixed timestep for both branches.

If bounded second-order cannot run one branch but can run the other, record that as part of the initialization result rather than silently changing only one case.

## Physical-time budget

Run both branches through the same physical-time window.

Initial comparison horizon:

```text
0.05 s
```

If the trajectories are still rapidly separating or have not passed the obvious startup adjustment, extend both identically toward:

```text
0.10 s
```

Do not compare by equal iteration count; compare at equal physical time.

## Required evidence

Record the same histories for both branches:

- `V_l,Y010(t)`;
- `V_l,Y030(t)`;
- total continuous-liquid inventory `V_l,total(t)`;
- liquid mass flux at the brine outlet;
- vapour mass flux at the brine outlet;
- liquid mass flux at the steam outlet;
- vapour mass flux at the steam outlet;
- brine-pipe-entry pressure;
- residuals and iterations required within each timestep;
- any reverse-flow or numerical warning events.

Preserve at least the initial state and the final comparison state for both branches.

## What to compare

The important question is not whether the first few timesteps are identical. A changed brine pressure plus the Y010 patch will create a startup readjustment.

Compare:

1. magnitude and duration of the initial adjustment;
2. whether either branch repeatedly exhausts the per-timestep iteration cap;
3. whether liquid-inventory trajectories move toward the same trend after startup;
4. whether outlet phase-flux histories move toward the same trend;
5. whether brine-pipe-entry pressure settles toward the same range;
6. whether one initialization produces numerical corruption that the other avoids.

## Decision gate

No automatic numerical threshold is imposed. The user selects the initialization rule from the observed histories.

Possible outcomes:

### A. Trajectories become similar and steady-start is cleaner

Use the developed steady parent as the production initialization basis.

### B. Trajectories become similar and neither has a meaningful advantage

Either method is technically usable; prefer the developed steady parent for consistency with the reusable-parent architecture unless the user chooses otherwise.

### C. Hybrid Initialization is clearly more robust

Use Hybrid Initialization as the common production method and record why the steady parent is retained only as diagnostic evidence.

### D. The branches remain materially different through the comparison horizon

Initialization sensitivity is unresolved. Do **not** immediately launch the six-case screen. Extend/diagnose the comparison or explicitly promote initialization method to an experimental factor.

## Create the final common `t = 0` parent

After the user selects the initialization method, create one immutable common transient parent for the production mesh.

The common parent should use the baseline common case definition, not any partially evolved T-PO-1 result:

```text
selected initialization method
→ common physical/model state
→ baseline brine Pressure Outlet at 1.120 MPa gauge
→ patch Y010 once
→ flow time = 0 s
→ save paired case/data transient parent
```

Later children may change the brine outlet type/value after loading this parent and before timestep 1. They must not reinitialize or repatch.

Conceptual artifact names:

```text
FG-MIX-T01-transient-t0-parent-<mesh-id>.cas.h5
FG-MIX-T01-transient-t0-parent-<mesh-id>.dat.h5
```

## Handoff

Proceed to [Stage 4 — Transient Numerical Qualification](stage-04-transient-numerical-qualification.md).