> **Retired source:** Setups/full-geometry/mixture/steady-liquid-outlet/03b-brine-pressure-continuation.md
> **Migration note:** Historical wording, evidence status, and uncertainty labels are preserved; this Project copy is not a reinterpretation. Machine-generated artifacts remain with their original external owners; the retired written source is recoverable from Git history.

# Setup 03B — Steady Brine-Outlet Pressure Continuation

> **Lifecycle:** `draft — child experiment of 03A`  
> **Parent:** [`03A — 08b-parity full-geometry steady Mixture baseline`](../03A/setup-source.md)
> **Primary objective:** use the developed 03A steady field as the parent and progressively change only the brine-outlet pressure **without reinitialization**, following the same solution branch instead of repeating independent pressure cases.  
> **Key distinction from 02c/02e:** this is steady numerical continuation, not a collection of separately initialized pressure siblings and not a physical transient pressure ramp.

## Canonical metadata

| Field | Value |
|---|---|
| Programme | `full-geometry` |
| Physics family | `mixture` |
| Campaign | `steady-liquid-outlet` |
| Setup ID | `03B` |
| Parent setup | `03A` |
| Setup authority | 03A field and its 08b / audited-Purnanto carrier settings |
| Time model | steady |
| Initialization | **none in 03B** — continue from parent field |
| Liquid patch | none |
| Steam outlet | fixed at `1.120 MPa gauge` |
| Experimental variable | brine Pressure Outlet gauge pressure only |
| Main question | can a stable full-geometry steady branch be followed toward a brine pressure that gives stationary liquid inventory and sensible phase routing? |

---

## 1. Scientific purpose

The earlier `02c` and `02e` pressure studies demonstrated that brine-outlet pressure strongly changes the solution, but they mostly tested pressure values as separate cases. That makes each result sensitive to both:

1. the requested brine pressure; and
2. whether the chosen initial field could survive the jump to that pressure.

03B removes that ambiguity as far as possible by using continuation:

```text
03A developed field at 1.120 MPa
→ small pressure change
→ continue solving from current field
→ allow new plateau to develop
→ save checkpoint
→ next small pressure change
```

No Hybrid Initialization occurs between pressure levels.

This means a pressure such as `1.1375 MPa` is approached from the nearest lower-pressure developed field rather than imposed on a fresh or unrelated parent.

`FG-MIX-T01-S1-C1375` remains historical evidence that the region around `1.1375 MPa` is interesting, but it is **not** loaded as the 03B parent.

---

## 2. Parent requirements

03B may start only from an immutable 03A case/data checkpoint that has:

- the 08b-derived carrier setup applied and read back;
- full geometry and physical brine outlet;
- steam outlet fixed at `1.120 MPa`;
- brine outlet at `1.120 MPa`;
- no liquid patch;
- no DPM/EWF additions;
- no unexplained setup drift;
- a numerically useful developed field.

Preferably, before entering 03B:

- phase fluxes are no longer changing violently;
- total liquid inventory is sufficiently developed to interpret its trend;
- no FPE / AMG breakdown is active;
- outlet reverse-flow behaviour has been recorded.

If 03A cannot establish such a field, stop and diagnose 03A rather than using pressure continuation as a numerical rescue.

---

## 3. Settings held fixed

03B changes **only brine-outlet gauge pressure**.

Keep unchanged from 03A:

- mesh and geometry;
- phase definitions and material properties;
- Mixture interaction model;
- RNG `k-epsilon` configuration;
- wall treatment;
- gravity and operating pressure;
- split inlet geometry, phase composition and velocity;
- inlet turbulence settings;
- steam-outlet pressure and all backflow settings;
- brine-outlet boundary type, direction treatment, backflow composition and turbulence settings;
- SIMPLE / Green-Gauss Node Based / PRESTO! / second-order / QUICK numerics;
- all URFs;
- residual monitor criteria;
- pseudo-time state;
- no patching;
- no DPM or EWF.

If another field must change to keep the run alive, stop this branch and create a separately named child sensitivity. Do not hide numerical tuning inside 03B.

---

## 4. Continuation rule

### 4.1 Starting point

Load the saved 03A case/data endpoint:

```text
P_steam = 1.120 MPa gauge
P_brine = 1.120 MPa gauge
```

Do **not** initialize.

Record the parent flux and inventory state before changing pressure.

### 4.2 Initial continuation ladder

Use the following first-pass pressure ladder:

```text
1.1200 MPa   03A parent
1.1250 MPa
1.1300 MPa
1.1350 MPa
1.1375 MPa
```

The `1.1375 MPa` point is retained as a useful historical marker because earlier full-geometry work showed strong pressure sensitivity around this region. It is not treated as a privileged final pressure.

If the solution remains stable and still indicates excessive drainage at `1.1375 MPa`, continuation may proceed upward, but step size should become adaptive rather than simply continuing a coarse grid.

### 4.3 Adaptive refinement

Use pressure response, not a fixed sweep table, to choose the next increment.

Recommended rule:

- while liquid drainage changes smoothly and the solver is robust: increments up to `5 kPa` are acceptable;
- once liquid-outlet flux, vapour short-circuit, inventory trend, or reverse flow changes sharply: reduce to `2.5 kPa`;
- near a suspected transition between drainage and accumulation/reversal: reduce further to approximately `1.25 kPa` if useful.

Example:

```text
stable at 1.1350
→ test 1.1375
→ strong response appears
→ next useful points may be 1.13625, 1.13875, etc.
```

Do not create a dense pressure grid merely for completeness. The objective is to trace the branch efficiently and identify where a stationary liquid state may exist.

---

## 5. What happens at each pressure plateau

For each pressure level:

1. save the incoming checkpoint before changing pressure;
2. change **only** brine-outlet gauge pressure;
3. positively read back the new pressure value;
4. continue steady iterations from the existing field;
5. monitor phase fluxes and liquid inventory continuously;
6. do not advance to the next pressure while the current response is still changing violently;
7. save a labelled case/data checkpoint and monitor data for the plateau;
8. decide the next pressure increment from the observed response.

A practical iteration structure is:

- inspect at approximately every `100` iterations;
- aim for at least `200` iterations after a pressure change unless the response clearly fails earlier;
- continue toward `500` or beyond where needed to determine whether fluxes/inventory are plateauing;
- never call a pressure point steady just because it has reached a fixed iteration count.

The exact plateau length is therefore diagnostic rather than rigid.

---

## 6. Primary monitors

The continuation decision should be driven mainly by flux and inventory histories.

For every pressure plateau record:

| Quantity | Interpretation |
|---|---|
| liquid inlet mass flow | reference liquid supply, target approximately `116.92 kg/s` |
| vapour inlet mass flow | reference steam supply, target approximately `80.69 kg/s` |
| liquid → brine outlet | desired liquid discharge |
| liquid → steam outlet | liquid carryover / wrong outlet |
| vapour → steam outlet | desired vapour discharge |
| vapour → brine outlet | vapour short-circuit / wrong outlet |
| total liquid inventory | whether separator is filling, draining, or stationary |
| Y010 liquid inventory | lower-vessel diagnostic only; no patch |
| Y030 liquid inventory | lower-vessel diagnostic only; no patch |
| brine reverse-flow sign / area | detects approach to pressure-driven reversal |
| brine-pipe-entry static pressure | compare local internal state with imposed outlet pressure |
| residuals | numerical health / divergence diagnostic |
| FPE, AMG and turbulent-viscosity warnings | failure evidence |

Flux plots should be retained for each pressure plateau because they provide the fastest interpretation of whether the pressure change moved the solution in the correct or incorrect direction.

---

## 7. Desired steady-branch condition

The main target is not a particular brine pressure. The target is a solution state where liquid inventory is no longer systematically draining or accumulating and the phase fluxes are compatible with the imposed inlet supply.

The strongest candidate region will satisfy, as closely as the model permits:

```text
liquid in ≈ liquid out through brine + liquid out through steam
vapour in ≈ vapour out through steam + vapour out through brine
```

with:

- total liquid inventory approaching a plateau;
- outlet fluxes approaching plateaus;
- no sustained brine reverse flow unless that state is intentionally being characterized;
- no FPE / AMG breakdown;
- bounded residual behaviour.

A mathematically stationary state and a physically good separator state are not identical. First identify whether a steady branch exists; then judge the phase routing quality separately.

---

## 8. Failure and refinement procedure

If the run fails after a pressure increase:

```text
DO NOT reinitialize
DO NOT restart from 03A at the failed pressure
```

Instead:

1. return to the last stable saved plateau;
2. reduce the pressure step between the stable and failed values;
3. continue from that stable field;
4. determine whether the failure marks a genuine branch limit or merely an excessively large continuation step.

Example:

```text
1.1375 MPa stable
1.1400 MPa FPE

restore 1.1375 checkpoint
→ try 1.13875 MPa
→ continue
```

If progressively smaller pressure steps still fail at approximately the same state, record that as evidence of a possible steady-branch limit or severe outlet-reversal instability.

Do not introduce new solver controls inside this procedure. A need for different numerics should become a separate experiment.

---

## 9. Why this differs from 02c / 02e

The old pressure studies are still valuable as reconnaissance, but 03B is deliberately different:

```text
02c / 02e style:
pressure A → own startup/run
pressure B → own startup/run
pressure C → own startup/run

03B:
one developed field
1.120 → 1.125 → 1.130 → 1.135 → 1.1375 → adaptive refinement
```

Thus 03B tests whether neighbouring steady solutions can be connected through small changes in brine backpressure.

This reduces the chance that a pressure is rejected merely because a fresh initial field could not survive the jump to it.

---

## 10. Checkpoint naming and traceability

Every pressure plateau must retain its lineage.

Suggested naming pattern:

```text
FG-MIX-S03B-P1120
FG-MIX-S03B-P1125
FG-MIX-S03B-P1130
FG-MIX-S03B-P1135
FG-MIX-S03B-P11375
```

If adaptive points are inserted, encode the exact pressure rather than renumbering the entire sequence.

For each checkpoint save:

- case/data pair;
- pressure value;
- parent checkpoint name;
- iteration range at that pressure;
- phase-flux histories;
- liquid-inventory histories;
- residual history;
- failure/warning messages if any;
- interpretation: draining / approximately stationary / accumulating / reverse-flow / failed.

The 03A source checkpoint must remain immutable.

---

## 11. Optional confirmation after finding a candidate

Once continuation identifies one or more promising stationary pressures, do not immediately claim they are unique physical operating points.

Useful later confirmations may include:

- continue downward from a higher-pressure developed field to check hysteresis / path dependence;
- restart one or two candidate pressures from a deliberately independent field;
- compare a finer mesh;
- replace the pressure outlet with a more physical downstream hydraulic representation if required.

These are **later validation steps**, not part of the primary 03B continuation run.

---

## 12. Completion criterion

03B is complete when it has done one of the following:

1. identified a stable pressure region where phase fluxes and liquid inventory approach a meaningful steady plateau;
2. demonstrated a repeatable transition from drainage toward accumulation/reverse flow and bracketed that transition sufficiently closely to guide the next model decision; or
3. shown that the 08b-derived full-geometry steady branch cannot be continued into the required retention region without encountering a reproducible numerical/physical branch limit.

The output of 03B should therefore be a **pressure-continuation trajectory**, not merely a table of independent pass/fail cases.
