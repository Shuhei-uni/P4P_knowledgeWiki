# Phase 06 / Stage 04 — stronger-feedback hypothesis

## Hypothesis

If the Stage-03 outer controller is limited by gain and update horizon rather
than by the wrong control direction, a stronger bounded pressure response over
ten steady chunks will reduce liquid-inventory drift toward the 200 kg
numerical target without worsening liquid balance relative to Stage 03.

## Exact delta

From the same F11 paired parent, retain all Stage-03 settings except:

- ten chunks of 100 steady iterations rather than five; and
- gain `2,000 Pa/kg` with capped pressure step `5,000 Pa`, instead of
  `500 Pa/kg` and `2,000 Pa`.

Pressure remains bounded 1.115–1.1375 MPa gauge. The target remains the
assumed 200 kg `y≤0.10 m` phase-2 liquid-mass proxy.

## Required evidence

- chunk-by-chunk proxy and read-back pressure history;
- phase-2 liquid inlet, brine, and steam-outlet flows;
- full and relative mass imbalance; and
- paired final case/data and file-backed histories.

## Core figures

| Figure | Question | Plot / data |
|---|---|---|
| F1 | Does the stronger rule hold the proxy near target? | proxy mass and 200 kg target versus native iteration; controller pressure steps overlaid or aligned. |
| F2 | Does the apparent control respect liquid balance? | phase-2 liquid inlet/outlet flows and derived net liquid rate versus iteration. |
| F3 | Is the rule numerically less harmful than the reference? | full and relative mass imbalance versus iteration, compared with Stages 1 and 3. |

## Claim limit

This tests only the declared numerical surrogate. It does not validate plant
level control or identify a plant controller gain.
