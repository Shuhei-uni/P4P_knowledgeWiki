# Phase 9 — EWF Plan v1: settings and iterations

| Setting | Selected value / action |
| --- | --- |
| Current mesh / server | 342,609 cells on Server 5; this is the current pilot |
| Parent | Selected 342k initial bulk-development pair at N8580 |
| Starting film age | 0.700 ms; retain saved film and bulk fields |
| Sufficient film-age endpoint | **Final endpoint for every mesh: 195 ms total film age, with bulk equations frozen.** Save and preserve the paired case/data files before any bulk reactivation. |
| Optional bonus endpoint | No new bulk-active extension is required or selected. An already accepted command may finish and save its result, but that result is supplementary; retain the frozen 195 ms pair as the final EWF endpoint. |
| Required pair 1 — before EWF run | After applying and verifying the agreed EWF settings, save both case and data **before the first iteration of this EWF schedule**. Retain inherited film age and bulk fields; do not reinitialize to manufacture a starting state. Record native iteration, film clock, bulk-equation state and both file hashes. |
| Required pair 2 — final EWF state | Save both case and data at **195 ms total film age while bulk remains frozen**. Verify the native clock and paired file identity. Identify this pair as the selected final state for the mesh. |
| Server 5 selected pairs | Before EWF run: **N8580 / 0.700 ms**, prepared settings, bulk active. Final: **N111460 / 195.000 ms**, bulk frozen. Both pairs already saved and hash-verified. [Selected pair manifest](../../../PyAnsys/output/phase9-ewf-server5/20261009/selected-ewf-final-pairs.json). |
| Completion claim limit | Applies to all runs covered by this plan. Reaching the selected film age does not alone establish steady film, mesh independence, whole-separator closure or physical validation. |
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
| Server 1 / 680k numerical acceptance limits | Disabled by human instruction. Record diagnostics; selected final endpoint is now 195 ms with bulk frozen. This shared endpoint rule supersedes the earlier 200 ms schedule. |
| Server 1 / 680k selected continuation | Owning chat must preserve the pre-EWF-run pair and final frozen 195 ms pair. Recalculate counts from its actual inherited and accepted film age; do not submit a new bulk-active extension. Preserve any command already accepted by Fluent. [Lane setup](server1-680k/setup.md). |
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
| Server 3 numerical limit checks | Disabled by human direction. Selected endpoint is 195 ms with bulk frozen. Courant remains a diagnostic; no threshold gates continuation. |
| Server 5 numerical limits | Disabled. Frozen 195 ms endpoint is selected and complete; no further solve or recovery selected. Current already accepted bulk-active command may finish unchanged. |
| Server 5 next fixed step | Human direction, 13 October 2026: use 2.5 µs from the next newly submitted command; leave the accepted 1 µs command unchanged. Adaptive stepping OFF. Drain refresh span 2.5 µs and particle update cadence 8. Numerical limits remain disabled. Recalculate counts from the accepted film clock. |
| Server 5 final-stage error recovery | Superseded by human endpoint selection, 14 October 2026. The already accepted 1 µs bulk-active retry may finish, but do not submit another retry or continuation. Select the frozen N111460 / 195 ms pair. |
| Particle update cadence | 20 µs film time: 200 iterations at 0.1 µs; 8 at 2.5 µs; 4 at 5 µs |
| Bulk equations | All active initially; frozen during film development through 195 ms. Final EWF pair must retain frozen bulk equations; no bulk reactivation is required. |
| Report settings | Retain inherited reporting; direct drain adds its named source and inventory expressions |
| Storage settings | Checkpoints/transcripts on the Fluent computer local disk. Preserve and identify the selected starting and final case/data pairs; OneDrive is for sharing selected starts/finals. |

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
| **Nominal new total for sufficient completion** | — | — | **41,810** | **195 ms** |

| Iteration setting | Value |
| --- | --- |
| Fixed-settings command size | At least 1,000 iterations; larger commands as listed above |
| Delivery | Native TUI journal; no Python short-iteration loop |
| Timestep changes | Separate from the bulk-freeze operation; update particle cadence and drain refresh span with each step |
| If 2.5 µs is selected instead of 5 µs | Recalculate counts from actual inherited and accepted film age to the selected 195 ms endpoint. No final bulk-active stage is required. |
| Step selection | Human direction, 10 October 2026: treat fixed film steps as a ladder that can move up or down. Current planned levels are 0.1, 2.5 and 5 µs; 5 µs remains the nominal upper level |
| Move up | After at least 1,000 verified updates at the current level and passing the owning lane's numerical checks, test the next higher level in a separate block. Save a healthy checkpoint before increasing; advancement is conditional on evidence |
| Move down | After an actual numerical error before the selected 195 ms endpoint, use the owning lane’s approved numerical recovery. Preserve failed evidence and the last verified pair. No recovery is required for an unselected supplementary stage. |
| Recovery starting point | Preserve failed-attempt evidence; reload the last verified healthy case/data checkpoint. Exclude failed or unverified updates from accepted film age |
| Recovery settings | Retain the model and stage's bulk-equation state; match fixed film step and drain refresh span to the selected level. Particle cadence: 200 iterations at 0.1 µs, 8 at 2.5 µs, 4 at 5 µs. Verify settings and film clock before continuation |
| Recovery continuation | Preserve film age and recalculate counts toward 195 ms with bulk frozen. After the frozen 195 ms pair is verified, the EWF development run is complete; do not add a bulk-active extension. |
| Repeated higher-step failure | A passing lower-step block permits reconsidering the higher level; it does not prove that the failed level is now viable. Retry only with evidence that addresses the failure; otherwise continue at the passing lower level |
| Failure at lowest planned level | Preserve evidence and use in-scope numerical recovery; the current ladder does not prescribe a smaller level |
| Other failures | Repair connection, file, or control errors without treating them as timestep failure. A diagnostic-only ledger warning follows the owning lane's authority; it does not alone trigger step reduction |
| Automation status | Plan-level bidirectional step rule; current fixed-schedule runners do not implement automatic movement up/down after recovery. Reconcile the owned runner and checkpoint before resuming a failed run |
| Execution authorized by this edit | Human direction, 14 October 2026: apply this two-pair preservation and frozen 195 ms endpoint rule to all meshes. This chat controls Server 5 only; other owning chats apply the shared plan on their own servers. |
