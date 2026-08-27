> **Retired source:** Setups/full-geometry/mixture/transient-liquid-outlet/stage-05-outlet-family-preflight.md
> **Migration note:** Historical wording, evidence status, and uncertainty labels are preserved; this Project copy is not a reinterpretation. Machine-generated artifacts remain with their original external owners; the retired written source is recoverable from Git history.

# FG-MIX-T01 Stage 5 — Outlet-Family Compatibility Preflight

## Intent

| Field | Value |
|---|---|
| Stage ID | `FG-MIX-T01-S5` |
| Investigation mode | diagnostic / compatibility preflight |
| Primary question | Can the locked transient method be applied without family-specific numerical tuning to representative Pressure Outlet, Outlet Vent, and Mass-Flow Outlet cases? |
| Interpretation owner | user-led |
| Parent | immutable common `t = 0` parent + method lock from [Stage 4](../stage-04/setup.md) |

## Why this stage exists

Stage 4 qualifies the transient method on a Pressure Outlet case. Before committing to the full six-case campaign, check that the same method is at least operationally compatible with each retained outlet family.

This is deliberately short. It is not a second scientific outlet screen and it should not consume the full production horizon.

## Representative cases

| Preflight | Outlet family | Control | Reason |
|---|---|---:|---|
| `PF-PO` | Pressure Outlet | `1.200 MPa` gauge | same representative used for numerical qualification |
| `PF-OV` | Outlet Vent | `K = 10` | retained useful liquid in the steady screen and represents the vent family |
| `PF-MF` | Mass-Flow Outlet | `58.4235 kg/s liquid` | aggressive early-retention case and a strong test of whether MF is usable transiently |

Each case must be rebuilt independently from the same immutable common `t = 0` parent.

## Frozen transient method

Use the exact Stage-4 method lock:

- selected initialization method;
- selected fixed timestep;
- PISO / pressure-velocity settings;
- Mixture VF formulation;
- temporal scheme and any common startup rule;
- maximum iterations per timestep;
- monitor/report definitions;
- checkpoint policy.

Do not reduce timestep only for MF, increase the iteration cap only for OV, or introduce family-specific relaxation changes during this preflight. If a family cannot use the common method, that is the result of this stage.

## Physical-time budget

Run each representative case from `t = 0` to:

```text
0.05 s
```

If a case is numerically healthy but still dominated by startup and the user wants more evidence before deciding, extend all three identically toward:

```text
0.10 s
```

Do not use a steady-style iteration budget as the comparison basis.

## Required evidence

For all three cases record:

- `V_l,Y010(t)`;
- `V_l,Y030(t)`;
- total liquid inventory;
- phase-separated brine and steam outlet fluxes;
- brine-pipe-entry pressure;
- residuals / iterations per timestep;
- reverse-flow events;
- Fluent warnings, divergence, FPE or other numerical failure;
- transient storage + flux liquid-balance behavior.

The preflight report should emphasize **method compatibility and failure mode**, not rank outlet performance from such a short physical interval.

## Preflight gate

Possible outcomes:

### All three families operate with the locked method

Proceed to the full six-case screen without changing the method.

### One family fails immediately or repeatedly cannot converge per timestep

Do not silently tune that family and then compare it against the others as though the method were common. Record the failure and let the user choose between:

- excluding that family from the common-method production screen;
- creating a separate numerical-method branch for that family; or
- revisiting Stage 4 with a method that can be shared by all three.

### A case shows extreme physical response but remains numerically interpretable

That is not automatically a preflight failure. Preserve the evidence and proceed/stop only by user decision.

## No production interpretation yet

A preflight case surviving `0.05–0.10 s` does not establish that it retains a realistic liquid inventory, reaches a bounded solution, or is physically preferable. Those are Stage-6 questions.

## Handoff

Proceed to [Stage 6 — Six-Case Aggressive Retention Screen](../stage-06/setup.md) once the common-method compatibility question is resolved.