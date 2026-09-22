# Phase 7.1A — Interpretation

## Why this phase existed

By Phase 7.1A the project had already selected the lower phase-2 absorber as the working liquid-removal architecture.

The question changed from mechanism discovery to: can the absorber be made to behave like a virtual liquid outlet and produce a sufficiently developed, bounded separator state for the next physics study?

## Key reframe: v2 virtual outlet

Inspection of the earlier absorber implementation showed that it did not behave like the intended instantaneous outlet. It used slower feedback/update logic and inventory-based control.

The v2 idea was simpler: make the requested absorber throughput follow the liquid inlet throughput, while distributing the sink only where phase-2 liquid is locally available.

This produces a feed-forward virtual outlet rather than asking the controller to infer the required removal from accumulated inventory.

## Main development sequence

| Step | What changed | What was learned |
| --- | --- | --- |
| v2 absorber build | inlet-matched phase-2 sink | source could track commanded liquid throughput once lower liquid became available |
| inlet-loading development | ramp from low loading toward full loading | gentler development prevented the immediate severe behaviour seen in earlier full-load starts, but inventory was still growing |
| accidental low-load hold | inlet ramp failed to advance as intended | unexpectedly produced the calmest residual field seen so far; revealed value of developing the carrier at low load first |
| controlled ramp from developed field | increase to full loading | residuals rose but did not collapse into earlier severe behaviour |
| Coupled + Global Time Step continuation | stronger pressure-velocity coupling / pseudo-time stabilization | continuity and residual levels improved and the long continuation became durable |
| run4 terminal continuation | second +1000 at full loading | selected as the Phase-7.2A parent |

## Representative evidence before run4

The v2 inlet-loading experiment reached the full 116.92 kg/s liquid and 80.69 kg/s vapor targets. The absorber applied source matched the liquid command to numerical precision once liquid was available.

However, at native iteration 4002:

- total liquid mass was still 318.661 kg;
- lower-zone liquid mass was 2.497 kg;
- phase-2 liquid through steamoutlet was about 22.116 kg/s;
- continuity was 1.73e-2;
- all seven residuals were higher than at iteration 2000.

That run therefore established a working v2 source but not a bounded operating state.

The corresponding summary figure is:
[v2 inlet-loading summary](../../PyAnsys/output/phase71a_v2_inlet_loading/20260922T031500Z/v2-inlet-loading-summary.png).

## Why run4 was the promotion point

At the final run4 state, native coordinate 5586:

- total liquid mass: 295.8536 kg;
- total liquid volume: 0.3357353 m3;
- absorber command/removal: 116.92 / 116.92 kg/s;
- command error: 4.26e-14 kg/s;
- continuity residual: 2.7841e-3;
- phase-2 volume-fraction residual: 5.4762e-4;
- phase-2 liquid through steamoutlet: about 24.3344 kg/s;
- no AMG, FPE, nonfinite, or fatal solver event over the final continuation.

The residuals were still oscillatory, reverse flow persisted, and viscosity limiting remained active. The solution was therefore not fully converged or physically validated.

The important change was that the macroscopic behaviour became usable: after the loading transient the liquid inventory approached a much flatter state, continuity was the best obtained so far, source tracking was exact, and the solver could continue without numerical collapse.

Useful control figures are stored in [roughness-family/r0-smooth-control](roughness-family/r0-smooth-control/), including:

- [control-window residual health](roughness-family/r0-smooth-control/control-06-residual-health.png)
- [warm-up total liquid inventory](roughness-family/r0-smooth-control/warmup-01-total-liquid-inventory.png)
- [warm-up phase-resolved fluxes](roughness-family/r0-smooth-control/warmup-04-phase-fluxes.png)

## Interpretation

The decisive lesson was that scaled residuals alone were not the phase-level success criterion.

The useful parent was identified by the combination of:

1. bounded / flattening liquid inventory;
2. best source-inclusive mass behaviour obtained so far;
3. lowest useful continuity level obtained so far;
4. exact absorber command tracking;
5. solver endurance.

The remaining roughly 24 kg/s liquid carryover through steamoutlet showed that the model was still far from a satisfactory separator result. But this now looked like a liquid-routing / separation-physics problem, rather than a failure to establish any usable global state.

## Why this led to Phase 7.2A

The next question became: with the global state now good enough to use as a parent, why is so much liquid still travelling to the steam outlet?

Phase 7.2A therefore freezes the absorber and numerical scaffold and changes the wall interaction.

## Evidence gaps / TODO

- TODO: calculate matched late-window inventory slopes for run4 and its immediate parent if the final report needs a quantitative boundedness comparison rather than the visual plateau argument.
- TODO: retain the accidental low-load hold as a genuine discovery, but clearly label it as an unintended setup bug that revealed a useful initialization/development strategy.
