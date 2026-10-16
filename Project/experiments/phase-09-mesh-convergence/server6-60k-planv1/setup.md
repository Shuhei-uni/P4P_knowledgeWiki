# Server 6 — 60k EWF Plan v1

| Item | Selected setup |
| --- | --- |
| Authority | Human, 14 October 2026: match EWF Plan v1 and run to 200 ms |
| Parent | Verified N8082 / 0.665 ms saved 60,964-cell pair |
| Owning settings | [EWF Plan v1](../ewf-plan-v1.md); mesh/server-specific histories retained |
| Film solution | Sequential; full momentum with gravity, shear, wall viscosity, pressure, spreading, advection and surface tension |
| Surface tension | Bulk and film 0.04041 N/m |
| Flow Momentum Coupling | OFF on both film walls |
| Smoothing | ON; level 2; factor 0.5 |
| Discretization | Original first-order implicit; first-order film mass/momentum; new implicit scheme OFF |
| Particle processes | Collection, splash, stripping and edge separation ON |
| Lower film wall | wall:004; allocated with zero initial height; original main-wall film preserved |
| Drain | Direct lower-wall mass and XYZ momentum removal; capture time 1.5 ms; 1% refresh depletion bound |
| Fixed controls | One film update per native iteration; profile update interval 1; DPM every 20 µs film time |
| Inner solve | Maximum 100 iterations; stop value 1e-5 |
| Roughness | 0.045 mm; Cs 0.5; bottom smooth |
| Bulk collector | Retained |
| Drain verification | Matched seeded OFF/ON frozen-bulk probe; production pair restored afterwards |
| Target | 200 ms total film time; nominal N50899 |
| Evidence | [Machine records](../../../../PyAnsys/output/phase9-server6-60k-planv1/20261014/) |

| Stage | Bulk | Step (µs) | Updates | Film endpoint (ms) |
| --- | --- | ---: | ---: | ---: |
| Adjustment | Active | 0.1 | 1500 | 0.815 |
| Transition | Frozen | 0.1 | 1000 | 0.915 |
| Faster step 1 | Frozen | 2.5 | 1000 | 3.415 |
| Faster step 2 | Frozen | 5 | 1000 | 8.415 |
| First growth | Frozen | 5 | 5000 | 33.415 |
| Growth 2 | Frozen | 5 | 10000 | 83.415 |
| Growth 3 | Frozen | 5 | 10000 | 133.415 |
| Growth 4 | Frozen | 5 | 10000 | 183.415 |
| Finish frozen | Frozen | 5 | 2317 | 195 |
| Reactivation | Active | 5 | 1000 | 200 |

| Limit | Treatment |
| --- | --- |
| Seeded probe | Functional drain check; excludes probe time from production; not proof of production conservation |
| Developing film | No steady-state or separator-validation claim |
| Failure | Preserve transcript and failed endpoint; reconcile saved pair before any continuation |
