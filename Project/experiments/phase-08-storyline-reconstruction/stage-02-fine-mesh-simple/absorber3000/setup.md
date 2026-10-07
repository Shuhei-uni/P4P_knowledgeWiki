# Stage 2 — matched full-feed absorber trial

| Item | Setting |
| --- | --- |
| Authority | Shuhei, 7 October 2026, add latest absorber and try 3,000 iterations |
| Question | Does the specified liquid absorber prevent the failure seen in the matched full-feed trial? |
| Server | Server 2 only; no restart or termination |
| Mesh and solver | F2, 997,604 cells; SIMPLE, steady Mixture/RNG; same methods and controls as OFF trial |
| Initial field | Exact saved OFF full-feed N0 case/data; no inherited failed field; no additional initialization |
| Feed | Nominal combined-area speed 26.81 m/s; liquid 116.93872650 kg/s and vapor 80.70292372 kg/s from N0 |
| Controlled change | Corrected libcontactv2 contact absorber, tau 10 microseconds, existing lower cell zone p71a-v2-virtual-outlet |
| Sources | Remove liquid mass and corresponding liquid-phase momentum; no vapor sink; no turbulence sink |
| Fixed treatment | Smooth walls, closed bottom, EWF off, DPM feedback off |
| Solve budget | Exactly 3,000 new iterations, three 1,000-iteration TUI batches |
| Checkpoints | Native local autosaves every 100 iterations; manual pairs at 1,000/2,000/3,000 |
| Reports | Existing 17 reports plus signed applied liquid source; report frequency 10 iterations |
| Acceptance evidence | Saved/reopened endpoint, residuals, pressure/velocity, liquid inventory, native/independent sink and source-inclusive mass balances |
| Claim limit | Successful completion supports stability for this configuration; it cannot establish that all absorber-OFF cases are numerically impossible |

The absorber changes the model by providing a liquid-removal route. It does not resolve a brine pool or establish physical validation. [OFF comparison](../full-feed3000/results.md) failed at N717. [Earlier ramp trial](../results.md) failed at N1422.

[Machine evidence](../../../../../PyAnsys/output/phase8-stage2/20261007/absorber3000/build.json) records library identity, hooks, matched controls, reports and start-pair hashes.

| Following trial | Current human direction |
| --- | --- |
| Startup sequence | Slow inlet with absorber off, then enable absorber before full-feed ramp |
| Authority and schedule | See phase [context](../../CONTEXT.md) and [state](../../phase-state.yaml); confirmed 3,000-iteration schedule; [next setup](../slow-enable3000/setup.md) |
| Handoff | Preserve this trial before starting a separate fresh low-feed trial; no Fluent restart |
