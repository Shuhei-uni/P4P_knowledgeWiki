# 997k — EWF Plan v1 on Server 3

| Setup | Selected value |
| --- | --- |
| Parent | Selected 997,604-cell N8080 pair; film age 0.650 ms |
| Parent proof | [N8080 checkpoint](../../../../PyAnsys/output/phase9-mesh-convergence/20261007/997k-checkpoint-8080-1791479563848407000.json) |
| Common settings | [EWF Plan v1](../ewf-plan-v1.md); retain bulk Coupled, Mixture/RNG, full feed, roughness and existing bulk collector |
| Film solver | Sequential; original first-order implicit; first-order mass/momentum; 100 inner iterations / 1e-5 stop |
| Film forces | Full momentum, gravity, gas shear, wall viscosity, advection, pressure, spreading and surface tension |
| Film surface tension | 0.04041 N/m; bulk retains approved native value |
| Film smoothing | ON; level 2, factor 0.5 |
| Film Courant operating limit | 0.8; human direction, 11 October 2026. Verify peak reported Courant before accepting a block for continuation. |
| Lower film wall | `wall:004`; initially dry; direct mass and X/Y/Z momentum drain; 1.5 ms capture time |
| Feedback | Flow Momentum Coupling OFF; existing bulk collector retained |
| Source refresh | Every update; profile interval 1; drain span matches fixed film step; 1% depletion limiter |
| Particle cadence | 20 µs film time: 200 / 8 / 4 updates at 0.1 / 2.5 / 5 µs |
| Storage | Server-local transcripts, paired stage checkpoints and data autosaves every 1,000 updates |
| Claim limit | Numerical continuation; no steady-film or physical-validation claim |

| Stage | Bulk equations | Film step (µs) | New iterations | Film age after stage (ms) |
| --- | --- | ---: | ---: | ---: |
| Adjustment | Active | 0.1 | 1,500 | 0.800 |
| Frozen transition | Frozen | 0.1 | 1,000 | 0.900 |
| First faster step | Frozen | 2.5 | 1,000 | 3.400 |
| Second faster step | Frozen | 5 | 1,000 | 8.400 |
| Main growth 1 | Frozen | 5 | 5,000 | 33.400 |
| Main growth 2 | Frozen | 5 | 10,000 | 83.400 |
| Main growth 3 | Frozen | 5 | 10,000 | 133.400 |
| Main growth 4 | Frozen | 5 | 10,000 | 183.400 |
| Finish frozen development | Frozen | 5 | 2,320 | 195.000 |
| Final bulk-active stage | Active | 5 | 1,000 | 200.000 |
| Total | — | — | 42,820 | 200.000 |

| Verification | Required evidence |
| --- | --- |
| Prepared child | Parent hashes, original fields retained, settings readback, save/reopen at N8080 |
| Frozen mode | Positive applied film removal in a matched frozen OFF/ON probe; removal ledger within 1%; unchanged production bulk fields. Keep the full secondary/DPM ledger as a separate diagnostic until its source timing is reconciled. |
| Native horizon | Exactly one film update per native iteration; transcript film clocks match the stage schedule |
| Endpoint | N50900 / 200 ms; bulk active; final pair reopened and checked |
