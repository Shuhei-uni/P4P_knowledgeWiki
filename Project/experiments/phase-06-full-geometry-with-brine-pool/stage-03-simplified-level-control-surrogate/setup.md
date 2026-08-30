# Phase 06 / Stage 03 — simplified level-control surrogate

## Stage question

Can a declared quasi-steady brine-outlet feedback rule hold a lower-region
liquid-inventory proxy near a target more effectively than a fixed brine
pressure or the rejected generic outlet-vent condition?

This is an explicitly simplified numerical-control model. It is **not** a
claim that the rule, target, or tuning represents the real separator.

## Research basis

Geothermal separator practice uses a level-control valve on the brine discharge
to prevent vessel draining and steam passage, and modulates brine discharge to
control vessel level. A liquid balance links liquid holdup to the difference
between liquid inlet and outlet flow. These principles support an outer
quasi-steady feedback surrogate, but they do not determine this separator's
setpoint or valve curve. [Steam Separator Selection for a Geothermal Power
Station](https://www.worldgeothermal.org/pdf/IGAstandard/NZGW/2021/120.pdf)

## Declared assumptions

| Item | Assumption | Label and reason |
|---|---|---|
| Controlled variable | phase-2 liquid mass in `codex_y010_pool_below_y_0p10m` | **Assumed numerical proxy**; Stage 1 proves it responds, not that it is plant level. |
| Target | 200 kg | **Assumed numerical target**; near the early fixed-pressure lower-region inventory, deliberately not a plant level. |
| Control action | alter only `brineoutlet` gauge pressure between bounded steady chunks | **Assumed quasi-steady actuator**; represents net brine-line resistance/backpressure, not a valve model. |
| Direction | when the proxy is above target, reduce outlet pressure; when below target, increase it | **Hypothesis**: lower brine backpressure increases brine drainage. |
| Bounds | 1.115–1.1375 MPa gauge | **Observed safe screen bracket** from Stage 5; not a selected plant pressure range. |
| Controller | bounded proportional step with pressure updates only after a fixed chunk | **Assumed surrogate**; no physical PID gains, valve stroke, or dynamic time response claimed. |
| Success | proxy approaches/holds target while phase liquid net rate, full mass imbalance, and residual evidence do not worsen | **Required numerical evidence**, not plant validation. |

## What this stage must prove before Stage 4

1. The lower-region proxy and phase-flow reports can be read after each steady
   chunk.
2. The outlet pressure update has the expected drainage direction, or the
   proposed control sign is rejected.
3. The bounded rule neither hides nor worsens liquid and full-domain closure.
4. Every pressure update, report window, and endpoint pair is retained.

## Boundaries

- Retain full geometry, F11 parent, steady Mixture/RNG model, gravity, inlets,
  steam outlet, and phase definitions for this first surrogate test.
- Do not call the 200 kg proxy target a plant level, setpoint, or measured
  elevation.
- Do not use a mass-flow outlet unless strict outward flow is proved; Stage 1
  did not meet that gate.
- A result that controls the proxy but retains poor balance/residual behaviour
  is not a credible controlled operating condition.
