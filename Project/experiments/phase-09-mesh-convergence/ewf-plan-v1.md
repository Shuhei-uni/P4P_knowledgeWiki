# Phase 9 — EWF Plan v1: settings and iterations

| Setting | Selected value / action |
| --- | --- |
| Current mesh / server | 342,609 cells on Server 5; this is the current pilot |
| Parent | Selected 342k initial bulk-development pair at N8580 |
| Starting film age | 0.700 ms; retain saved film and bulk fields |
| Total film-age target | 200 ms, including inherited film age |
| Bulk model / solver | Retain Mixture, RNG and bulk Coupled |
| Feed | Retain liquid 116.92 kg/s and vapor 80.69 kg/s |
| Existing bulk collector | Retain existing mass and momentum source hooks |
| Roughness | Retain 0.045 mm, Cs 0.5; bottom smooth |
| EWF / Phase Accretion | ON / ON |
| Film velocity | Full momentum equation; gravity, gas shear, wall-viscous resistance and momentum advection ON |
| Film pressure / spreading / surface tension | ON / ON / ON |
| Bulk and film surface tension | 0.04041 N/m for both; human selection |
| Flow Momentum Coupling | OFF |
| Film mass/momentum solution | Sequential: EWF Coupled Solution OFF; bulk Coupled unchanged |
| Film time scheme | Original first-order implicit; new implicit scheme OFF |
| Film spatial schemes | First-order mass and momentum |
| Server 1 / 680k peak film Courant limit | 0.8; human selection, 11 October 2026. Retain earlier block diagnostics and warnings; apply the updated ceiling to subsequent block acceptance in this lane. |
| Inner film solver | Maximum 100 subiterations; stop value 1e-5 |
| Curvature smoothing | ON; level 2, factor 0.5 |
| Small-film threshold | Retain inherited 1e-8 m |
| Maximum film thickness | Retain inherited 1 m |
| DPM collection / splash | ON / ON |
| Particle stripping / edge separation | ON / ON |
| Lower collector film wall | Enable EWF on physically mapped `wall:004`; initial film height 0 m on the newly allocated wall |
| Direct film drain | ON on lower film wall; 1.5 ms capture time; matching X/Y/Z momentum removal; retain bulk collector |
| Film/profile source refresh | Every film update; profile update interval 1 |
| Drain refresh span | Match the current fixed film step; retain existing 1% source-depletion limiter |
| Film updates per native iteration | One; film-per-flow-iters 1 and sub-time-steps 1 |
| Initial film step | Fixed 0.1 µs; adaptive stepping OFF |
| Later film steps | 2.5 µs, then nominal 5 µs |
| Server 3 film Courant operating limit | 0.8 maximum reported film Courant; human direction, 11 October 2026. Apply to the 997,604-cell lane. Fixed stepping and adaptive stepping OFF remain selected. |
| Server 5 film Courant operating limit | 0.8 maximum reported film Courant; human direction, 11 October 2026. Check the native transcript before accepting each batch. Fixed stepping and adaptive stepping OFF remain selected. |
| Particle update cadence | 20 µs film time: 200 iterations at 0.1 µs; 8 at 2.5 µs; 4 at 5 µs |
| Bulk equations | All active initially; all frozen during middle film development; all active again from 195 to 200 ms |
| Report settings | Retain inherited reporting; direct drain adds its named source and inventory expressions |
| Storage settings | Server-local checkpoints/transcript; selected shared case/data pairs on OneDrive |

| Stage | Bulk equations | Film step | Native iterations | Total film age after stage |
| --- | --- | ---: | ---: | ---: |
| Apply settings and save child | Active | 0.1 µs | 0 | 0.700 ms |
| Bulk-active adjustment | Active | 0.1 µs | 1,500 | 0.850 ms |
| Frozen transition | Frozen | 0.1 µs | 1,000 | 0.950 ms |
| First faster-step stage | Frozen | 2.5 µs | 1,000 | 3.450 ms |
| Second faster-step stage | Frozen | 5 µs | 1,000 | 8.450 ms |
| First main-growth command | Frozen | 5 µs | 5,000 | 33.450 ms |
| Main-growth command 2 | Frozen | 5 µs | 10,000 | 83.450 ms |
| Main-growth command 3 | Frozen | 5 µs | 10,000 | 133.450 ms |
| Main-growth command 4 | Frozen | 5 µs | 10,000 | 183.450 ms |
| Finish frozen development | Frozen | 5 µs | 2,310 | 195.000 ms |
| Final bulk-active stage | Active | 5 µs | 1,000 | 200.000 ms |
| **Nominal new total** | — | — | **42,810** | **200 ms** |

| Iteration setting | Value |
| --- | --- |
| Fixed-settings command size | At least 1,000 iterations; larger commands as listed above |
| Delivery | Native TUI journal; no Python short-iteration loop |
| Timestep changes | Separate from the bulk-freeze operation; update particle cadence and drain refresh span with each step |
| If 2.5 µs is selected instead of 5 µs | Recalculate remaining counts from actual inherited and accepted film age; final 195–200 ms stage is 2,000 iterations |
| Step selection | Human direction, 10 October 2026: treat fixed film steps as a ladder that can move up or down. Current planned levels are 0.1, 2.5 and 5 µs; 5 µs remains the nominal upper level |
| Move up | After at least 1,000 verified updates at the current level and passing the owning lane's numerical checks, test the next higher level in a separate block. Save a healthy checkpoint before increasing; advancement is conditional on evidence |
| Move down | After a numerical failure, recover at the next lower planned level: 5 → 2.5 µs, or 2.5 → 0.1 µs. Applies during faster-step checks, main growth and final bulk-active development |
| Recovery starting point | Preserve failed-attempt evidence; reload the last verified healthy case/data checkpoint. Exclude failed or unverified updates from accepted film age |
| Recovery settings | Retain the model and stage's bulk-equation state; match fixed film step and drain refresh span to the selected level. Particle cadence: 200 iterations at 0.1 µs, 8 at 2.5 µs, 4 at 5 µs. Verify settings and film clock before continuation |
| Recovery continuation | Verify the first 1,000 updates at the lower level, or the remaining stage duration if shorter. Continue toward 195 ms frozen and 200 ms bulk active; recalculate counts and native endpoint from accepted film age after each step change. Preserve film age |
| Repeated higher-step failure | A passing lower-step block permits reconsidering the higher level; it does not prove that the failed level is now viable. Retry only with evidence that addresses the failure; otherwise continue at the passing lower level |
| Failure at lowest planned level | Preserve evidence and use in-scope numerical recovery; the current ladder does not prescribe a smaller level |
| Other failures | Repair connection, file, or control errors without treating them as timestep failure. A diagnostic-only ledger warning follows the owning lane's authority; it does not alone trigger step reduction |
| Automation status | Plan-level bidirectional step rule; current fixed-schedule runners do not implement automatic movement up/down after recovery. Reconcile the owned runner and checkpoint before resuming a failed run |
| Execution authorized by this edit | Human authorizes Server 5 setup and execution of the staged schedule once ready; Server 3 authority revoked |
