---
name: cfd-numerical-analysis
description: "Assess whether a CFD simulation is numerically trustworthy enough to answer its experiment question. Use for residual/monitor behaviour, conservation, stationarity, mesh/timestep/iteration sensitivity, solver instability, reversed flow, Courant behaviour, and separating numerical failure from physical conclusions."
---

# CFD Numerical Analysis

Answer one question:

> Is this CFD evidence numerically adequate for the claim we want to make?

Do not equate solver completion with physical validity, and do not equate imperfect residual convergence with automatic failure.

## Start from the intended claim

Read the experiment question and analysis plan. Numerical adequacy is claim-specific.

Examples:

- a diagnostic run may only need to demonstrate that one method crashes later than another;
- a ranking of separator efficiency needs much stronger stationarity and conservation evidence;
- a mesh-independence claim requires a mesh study, not merely low residuals.

## Evidence categories

Assess as applicable:

### Iterative / nonlinear behaviour

- scaled residual histories;
- monotonic, oscillatory, plateaued, diverging, or cyclic behaviour;
- physical monitor drift;
- convergence within each transient timestep;
- whether additional iterations materially change the quantity of interest.

### Conservation and routing

- total mass balance;
- phase-specific balance when meaningful;
- inlet/outlet sign convention;
- inventory accumulation for transient cases;
- whether apparent imbalance is expected storage or genuine closure failure.

### Stability and solver health

- FPEs;
- AMG divergence;
- turbulent-viscosity limiting;
- reversed-flow events;
- Courant/interface-Courant behaviour;
- clipping/limiting;
- nonphysical values;
- stalled or repeatedly recovering solver state.

### Independence / verification

- iteration-window independence;
- timestep sensitivity;
- mesh sensitivity;
- initialization sensitivity;
- discretization sensitivity;
- repeated/restarted consistency where appropriate.

## Distinguish steady from transient logic

For steady simulations, ask whether monitored quantities approach a stable fixed or bounded state appropriate to the question.

For transient simulations, do not demand constant instantaneous values. Ask instead whether:

- the startup transient has passed;
- the required physical horizon is long enough;
- statistics/time averages are stable over the chosen window;
- periodic or broadband unsteadiness is resolved rather than numerical noise;
- timestep and inner-iteration treatment are adequate.

## Do not overuse universal thresholds

Residual targets and mass-balance tolerances depend on the problem, quantity of interest, solver formulation, and project criteria. Use declared project criteria when available.

If no criterion exists, report numerical evidence and uncertainty rather than silently inventing a pass/fail threshold. You may propose a sensitivity test that would resolve the uncertainty.

## Diagnose failure mode

When a case is unusable, classify why:

- **implementation/setup mismatch**;
- **numerical instability**;
- **insufficient iterations/physical time**;
- **insufficient timestep resolution**;
- **insufficient mesh resolution**;
- **non-stationary physical solution under a steady formulation**;
- **missing evidence**;
- **unknown / requires targeted diagnostic**.

Do not jump from "residual oscillates" directly to "physics model wrong".

## Use comparisons carefully

Compare like with like:

- same metric definition and zones;
- comparable iteration or physical-time windows;
- same sign convention and normalization;
- explicit note when one run failed early;
- no interpolation across missing failure segments unless scientifically justified and declared.

## Delegate adversarial checks

For consequential numerical conclusions, use a subagent or `interrogate` to challenge:

- whether the selected window is cherry-picked;
- whether the balance definition is correct;
- whether an apparent improvement is just longer runtime;
- whether two cases differ in more than the claimed numerical variable.

## Output

Return:

1. numerical status: `adequate`, `adequate_for_limited_claim`, `insufficient`, or `failed`;
2. strongest evidence supporting that status;
3. the exact claims that are safe/unsafe;
4. numerical limitations;
5. the smallest next numerical test needed, if unresolved.

Keep physics interpretation separate. Hand the bounded numerical status to `interpret-experiment` and `next-action`.