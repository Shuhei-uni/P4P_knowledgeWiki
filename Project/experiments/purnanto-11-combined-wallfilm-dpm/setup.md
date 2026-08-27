> **Legacy source:** Setups/archived/11-combined-wallfilm-dpm-plan.md  
> **Migration note:** Historical wording, evidence status, and uncertainty labels are preserved; this Project copy is not a reinterpretation. Raw and machine-generated artifacts remain at their legacy paths.

# Setup 11 — Combined Wall-Film and DPM Physics Plan

## Setup metadata

| Field | Value |
|---|---|
| Setup ID | `11` family plan |
| Lifecycle | `future` |
| Role | combined wall-film / re-entrainment / custom-DPM confirmation family |
| Parent setup | selected stable results from setup `10` |
| Child plans | `11a` EWF + re-entrainment; `11b` EWF + re-entrainment + selected custom DPM/material |
| Evidence-use label | future combination plan; results pending |
| Outcome | needs follow-up |
| Linked report | none |

## 1. Purpose

Combine only mechanisms that were individually interpretable in setup `10`.

- `11a`: does a wall film with the selected re-entrainment closure change total steam-line carryover?
- `11b`: does adding the selected custom DPM trajectory or material model change the film-aware result?

## 2. Parent selection

- `11a` starts from `10a` and adds the selected `10b` wall-return/re-entrainment closure.
- `11b` starts from accepted `11a` and adds the selected stable `10c` law or material variant.
- If a `10` feature is unstable, unbounded, or not mass-conserving, do not carry it into `11`.

## 3. `11a` solver/model changes

Starting from `10a`:

- retain transient pressure-based `Mixture` solver;
- retain `RNG k-epsilon`, Energy off, gravity, mesh, inlet loading, outlets, DPM payload, and DPM coupling;
- retain EWF on the selected wall zones;
- enable the selected `10b` re-entrainment / film-stripping / wall-return closure;
- retain standard DPM-to-wall-film coupling;
- do not add custom DPM drag, custom material, species transport, or geometry changes.

Required outputs:

- film mass and thickness versus time;
- deposition, drainage, and re-entrainment rates;
- direct escaped DPM mass;
- continuous-phase liquid at the steam outlet;
- total film-aware liquid carryover;
- complete phase balance and residual/monitor stability.

## 4. `11b` solver/model changes

Starting from accepted `11a`:

- change only the selected `10c-T` custom wall-impact law or `10c-M` material variant;
- retain EWF, re-entrainment, transient controls, and all boundary conditions;
- if trajectory and material are both important, run separate `11b-T` and `11b-M` cases before any final combined case;
- report whether the change affects film formation, re-entrainment, direct escape, or only DPM fate classification.

## 5. Combination acceptance gate

`11a` is interpretable only if:

1. `10a` film inventory is bounded;
2. the selected `10b` closure has conserved and documented returned mass;
3. direct DPM escape, film-mediated carryover, and resolved phase flux can be separated;
4. the conclusion is stable over the averaging window.

`11b` is interpretable only if:

1. `11a` passes;
2. the selected `10c` law/material has documented properties and valid ranges;
3. no second uncontrolled change is introduced;
4. the carryover change is larger than numerical uncertainty or is explicitly reported as unresolved.

If a gate fails, keep the result as diagnostic evidence and report the failure mechanism. Do not call the combined model validated.

## 6. Final comparison table

| Case | Physics | Purpose |
|---|---|---|
| `09c` | two-way DPM, no EWF | coupling reference |
| `10a` | EWF deposition/drainage | film formation baseline |
| `10b` | DPM wall-return surrogate, no EWF | wall-fate sensitivity |
| `10c` | custom DPM/material, no EWF | trajectory/material sensitivity |
| `11a` | EWF + selected re-entrainment | film-aware carryover |
| `11b` | `11a` + selected custom DPM/material | full candidate model |
