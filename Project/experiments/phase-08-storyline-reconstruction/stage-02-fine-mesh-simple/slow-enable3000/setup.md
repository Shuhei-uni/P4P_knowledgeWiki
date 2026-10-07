# Stage 2 — slow inlet, delayed absorber activation

| Item | Setting |
| --- | --- |
| Authority | Shuhei, 7 October 2026: confirmed 1,000 low + 1,000 ramp + 1,000 full |
| Status | N0 saved/reopened; host controller launched after user Server 2 restart |
| Question | Does a low-feed start followed by absorber activation and a ramp avoid the full-feed startup failure? |
| Precedent | Partial repeat: earlier low-feed/ramp trial had no absorber; current full-feed trial enabled absorber from N0 |
| Mesh / carrier | F2, 997,604 cells; SIMPLE, steady Mixture/RNG |
| Fixed controls | Same discretization, relaxation, smooth walls, closed bottom; EWF and DPM feedback off |
| Initial field | Fresh Hybrid initialization at 25% feed, absorber off; preserve current endpoint before replacement |
| Low-feed setting | Scale both pure-phase mass feeds to 25%; nominal combined-area speed 6.7025 m/s |
| Full-feed basis | Liquid 116.93872650 kg/s; vapor 80.70292372 kg/s; nominal 26.81 m/s |
| Absorber | Corrected libcontactv2; tau 10 microseconds; liquid mass and carried momentum only; existing lower collector zone |
| Horizon | Exactly 3,000 total new solve iterations; all verification included |
| Session | Server 2 only; attach existing session; no restart or termination |
| Claim limit | Startup-path sensitivity for this configuration; no universal numerical-impossibility or physical-validation claim |

| Native iteration | Feed | Absorber | Action |
| --- | --- | --- | --- |
| N0–N1000 | 25% | Off | Low-feed development; 1,000-iteration TUI batch |
| N1000 | 25% | Off → On | Save pre-enable pair; activate and read back hooks; save post-enable pair without advancing iterations |
| N1000–N2000 | 32.5%, 40%, 47.5%, 55%, 62.5%, 70%, 77.5%, 85%, 92.5%, 100% | On | Ten 100-iteration feed steps |
| N2000–N3000 | 100% | On | 1,000-iteration full-feed hold |

| Required evidence | Purpose |
| --- | --- |
| Paired fresh N0; pre/post-enable N1000; N2000; final N3000 | Preserve field lineage and activation boundary |
| Native local autosaves every 100 iterations | Retain usable fields near any failure |
| Carrier reports throughout; applied signed liquid source active after N1000 | Check phase and mixture mass balance including removal |
| Lower liquid mass / tau | Independent absorber-removal estimate after activation |
| Liquid inventory, pressure, residual histories | Distinguish completion from sustained numerical stability |
| Native liquid and velocity views | Inspect separator behaviour at saved valid checkpoints |
| Final save/reopen and matched-control readback | Verify requested horizon and retained settings |

[Current trial](../absorber3000/results.md) has stopped; its N600 endpoint is save/reopen verified. [Phase context](../../CONTEXT.md) and [machine state](../../phase-state.yaml) own the active queue.
