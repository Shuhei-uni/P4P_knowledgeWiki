# Phase 9 — EWF Plan v1

## Agreed comparison

| Item | Plan |
| --- | --- |
| Human direction | Shuhei, 9 October 2026: write Plan v1; use 200 ms film time and accept continued film growth at that horizon |
| Purpose | Develop a repeatable film on the five Phase 9 meshes for a bounded mesh-sensitivity comparison |
| Priority | Numerical stability first; total development cost second; retain interpretable film transport and entrainment |
| Command policy | Human direction: use native TUI solves of at least 1,000 iterations; prefer larger uninterrupted commands while inputs remain fixed |
| Budget intent | Plan the whole campaign with practical per-mesh iteration allowances; seek useful, stable results rather than exhaustive accuracy studies |
| Target | **200 ms total native film age from film initialization**, including accepted startup, qualification and final bulk-active advancement |
| Film mass | Measured output; no 6 kg target, forced inventory or mass-based stopping rule |
| Accepted limitation | Film will probably still grow at 200 ms; positive storage alone does not reject the comparison or require a longer run |
| Required distinction | Accept continued physical/modelled development; reject numerical divergence, unexplained source loss or thickness-cap removal |
| Status | Written plan; numerical candidates remain unqualified for this campaign |
| Execution boundary | This writing request starts no solve, changes no Fluent settings and changes no session ownership |
| Existing preparation | [Phase 9 setup](setup.md) continues to own mesh transfer, startup and full-feed preparation |
| Claim | Mesh sensitivity of a developing film under a declared preparation procedure; no steady-film or mesh-independence claim from reaching 200 ms |

## Starting state and fixed basis

| Item | Requirement |
| --- | --- |
| Meshes | 60,964; 342,609; 679,970; 997,604; 2,596,657 fluid cells |
| Parent per mesh | Its verified Phase 9 full-feed case/data pair; record hashes, native iteration, film age and fields before changes |
| Preservation | Preserve valuable endpoints; no bulk reinitialization or film reset |
| Bulk basis | Retain Phase 9 Mixture/RNG, bulk Coupled solver, materials, full feed and intended bulk collector |
| Full feed | Liquid 116.92 kg/s; vapor 80.69 kg/s |
| Roughness | Retain 0.045 mm and Cs 0.5 on the Phase 9 physical wall scope; bottom smooth |
| Physical mapping | Same film walls, collector region and intended edge routes across meshes; verify geometry rather than copy zone names |
| Readback | Verify each saved endpoint; historical setup files do not prove current settings |
| Property check | Resolve the recorded bulk/film surface-tension difference: Phase 9 bulk 0.04041 N/m versus inspected Stage 4 film 0.07194 N/m; use one declared operating-property basis where applicable |
| Property restriction | Do not tune density, viscosity, surface tension, roughness or drain strength to obtain a chosen film mass |

## Candidate EWF settings

| Setting | Plan v1 choice | Qualification or limit |
| --- | --- | --- |
| EWF / Phase Accretion | ON / ON | Retain film supply and mass transport |
| Film velocity | Full momentum equation | Retain gravity, gas shear, wall-viscous resistance and momentum advection |
| Pressure / spreading / surface tension | Retain ON initially | Earlier conditional OFF tests did not establish a stable replacement |
| Flow Momentum Coupling | OFF | Historical ON attempts produced repeated failures; omitted interface-motion feedback remains a model limit |
| Film mass/momentum solution | Test sequential solution with original first-order implicit scheme | Separate from the retained bulk Coupled solver; latest 5 µs trial removed a numerical burst but failed source consistency |
| Spatial schemes | Retain first-order film mass and momentum for initial qualification | Keep schemes consistent across meshes; numerical diffusion remains a limit |
| Inner film controls | Maximum 100 subiterations; stop value 1e-5 | Require achieved residual evidence; increasing the cap does not repair a flat or divergent residual |
| Curvature smoothing | Retain tested level 2, factor 0.5 in the candidate packet | Verify applicability to the selected solver; no claim of a complete stability repair or smoothing independence |
| Small-film threshold | Preserve and record the inherited value initially | Do not mandate 1e-10 m; exact internal effects and transferability require confirmation. It is not the maximum-thickness cap |
| Maximum film thickness | Record inherited setting; do not lower it to remove liquid | Cap activation invalidates the affected comparison; the cap is not a physical thin-film validity criterion |
| Particle stripping / edge separation | Retain ON | Record release, return route and particle fate; release is not automatically an external outlet |
| DPM collection / splash | Retain initially | Preserve compatible film/particle material properties and physical source flags during solver tests |
| Particle update interval | Start with the tested 20 µs film-time interval | Verify effective cadence; adjust iteration count when film step changes |
| Direct film drain | Proven lower-film mass sink with matched XYZ momentum removal; capture time 1.5 ms | Prove removal with frozen bulk and verify delivery into the collector |
| Drain refresh | Refresh every film update initially | Verify actual callback cadence and depletion protection; no silent change to the sink law at larger steps |
| Film step | Fixed conservative initial check; qualify 2.5 µs, then 5 µs where supported | No universal step across meshes; use wall spacing, local speed, sources and achieved solves |
| Adaptive stepping | Defer automatic growth for the first qualification | Historical nominal maximum-step settings did not prove an effective ceiling |
| Analytical velocity | Excluded from the first route | Earlier trials produced extreme velocities without a measured cost benefit |

## Development sequence

```mermaid
flowchart LR
    A[Verified full-feed parent] --> B[Apply and verify EWF changes]
    B --> C[Adjust with bulk active and small film step]
    C --> D[Check frozen-bulk transition]
    D --> H[Qualify faster step and develop film]
    H --> E[Restore bulk within time budget]
    E --> F[Compare at total film age 200 ms]
```

| Stage | Action | Required evidence |
| --- | --- | --- |
| 1. Pilot | Use the saved 60k endpoint to qualify one method before replicating it | Exact parent, effective settings, fields and clock |
| 2. Build check | Compare actual parent settings with the candidate packet; apply only required changes in a preserved child; verify drainage and refresh | Reuse applicable proven drain evidence; if a new fixture is needed, use at least 1,000 native updates, then restore exact production fields and active bulk equations |
| 3. Bulk-active adjustment | Human-reduced allowance: retain all intended bulk equations and the inherited conservative 0.1 µs film step; use one 1,000–2,500-iteration command from the per-mesh schedule below | Assess its final 1,000-update window after completion; no short smoke solve, simultaneous timestep increase or bulk freeze |
| 4. Freeze readiness | Use the final 1,000-update window of the shortened adjustment, plus film numerical/accounting checks; do not automatically restore the former counts to obtain two windows | Retain pressure-drop range <=5% of mean, bulk inventory range <=10% of mean and outlet-liquid range <=5% of full liquid feed; this shortened transition screen is not the original two-window preparation proof |
| 5. Frozen transition and step qualification | Preserve the adjusted pair; freeze bulk at 0.1 µs; run `/solve/iterate 1000`, then 1,000 updates at 2.5 µs; for a 5 µs production candidate, run a further 1,000 at 5 µs | Both faster-step checks count toward frozen growth in the budget below; check actual steps, inner residuals, source cadence and corrected ledger |
| 5a. Resolve known gap | Check the remaining sequential-solver source discrepancy before long development | Latest 5/2.5 µs source gaps were 1.318%/1.168%; neither passed the existing 1% screen; no promotion on a low Courant number alone |
| 5b. Main growth | Continue frozen-bulk development with the qualified step; prefer 5,000–10,000 iterations per native command where no earlier experiment decision is required | Upper/lower film growth, transport, sources, release and numerical health; preserve required checks without routine stop/relaunch cycles |
| 6. Developing-film check | Review saved evidence at about 50, 100 and 150 ms without routine solver stops; use the next planned command boundary for any required correction | Check growth, upper/lower transport, source consistency and numerical health; no full timestep-refinement campaign by default |
| 7. Bulk reactivation | Halved final allowance: restore all intended bulk equations at 195 ms; retain the selected film step and run the final 5 ms in one native command | Nominally 1,000 active iterations at 5 µs or 2,000 at 2.5 µs; inspect bulk response, outlet routing, pressure drop and accounting |
| 8. Endpoint | Save and verify the paired state at total native film age 200 ms | Common-age fields, final histories, actual equation flags and source accounting |
| 9. Other meshes | Confirm the method on the finest wall mesh before broad replication; qualify each mesh's timestep | Same physics and comparison procedure; mesh-specific numerical controls recorded |

## Whole-campaign iteration budget

| Budget basis | Assumption |
| --- | --- |
| Count scope | **New iterations after each verified full-feed preparation endpoint**; do not repeat completed transfer, low-feed hold, ramp or full-feed preparation |
| Update mapping | One accepted film step per native iteration; verify before using this arithmetic |
| Bulk-active adjustment | 0.1 µs; per-mesh counts below are practical allowances, not a convergence law |
| Common final stage | Bulk active from 195 to 200 ms on every mesh; reactivation moves 5 ms later to halve active iterations while preserving the 200 ms endpoint and selected timesteps |
| Nominal step selection | Budget 5 µs for 60k/342k and 2.5 µs for 680k/997k/2.6M; these are cost/stability planning assumptions, not measured mesh-specific limits |
| Wall-mesh decision | Actual wall spacing, forcing and passing numerical checks decide the usable step; total cell count does not set it |
| Exact counts | Read each parent's actual film age and deduct it from the remaining 200 ms; table values are rounded and assume a near-zero parent age |
| Included checks | Frozen-growth counts include the 1,000-update 2.5 µs check and, where selected, the 1,000-update 5 µs check |
| Extra-work allowance | Up to 10,000 additional iterations per mesh for a necessary drain fixture, bulk adjustment, one focused numerical/source repair, a diagnostic comparison or clock alignment; do not spend this allowance automatically |

| Mesh | Bulk-active adjustment | Frozen check at 0.1 µs | Nominal growth step | Frozen growth to 195 ms, including step checks | Bulk active, 195–200 ms | Nominal new total | Budget with contingency |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 60k | 1,000 | 1,000 | 5 µs | about 39,460 | 1,000 | about **43,000** | **53,000** |
| 342k | 1,500 | 1,000 | 5 µs | about 39,450 | 1,000 | about **43,000** | **53,000** |
| 680k | 1,500 | 1,000 | 2.5 µs | about 77,900 | 2,000 | about **83,000** | **93,000** |
| 997k | 2,000 | 1,000 | 2.5 µs | about 77,880 | 2,000 | about **83,000** | **93,000** |
| 2.6M | 2,500 | 1,000 | 2.5 µs | about 77,860 | 2,000 | about **84,000** | **94,000** |
| Total | 8,500 | 5,000 | — | about 312,550 | 8,000 | about **336,000** | **386,000** |

| Native command stage | Planned command size / decision |
| --- | --- |
| Active adjustment | One `/solve/iterate 1000`, `1500`, `2000` or `2500`, according to mesh |
| Freeze check | One `/solve/iterate 1000` at unchanged 0.1 µs |
| Step checks | One `/solve/iterate 1000` per selected new step; changing a step and freezing bulk remain separate operations |
| First longer growth block | `/solve/iterate 5000` at the selected step |
| Remaining frozen growth | Prefer `/solve/iterate 10000`; combine the remainder into a final command of at least 1,000 iterations, ending at 195 ms |
| Reactivation check | One `/solve/iterate 1000` at 5 µs or `/solve/iterate 2000` at 2.5 µs; use the final 1,000-update window for the common shortened bulk screen |
| Cost expectation | Roughly 10–15 solve submissions per mesh without recovery; actual command count depends on clock alignment and step selection |
| Native storage | Autosave locally during long commands; no remote stop/relaunch for each 1,000-update analysis window |

| Budget contingency | Bounded response |
| --- | --- |
| 5 µs fails on 60k or 342k | Use a passing 2.5 µs route; nominal total becomes about 82,000/83,000, before the same 10,000-iteration contingency; preserve the common 195–200 ms final stage |
| Both smaller meshes need 2.5 µs | Revised rounded campaign allowance: about 415,000 nominal or 465,000 including contingency |
| 2.5 µs is unstable | Spend the remaining bounded repair allowance on one evidence-led numerical/source correction; preserve an unresolved endpoint if it does not work |
| A slower route is required | At 1 µs, 200 ms alone needs about 200,000 film updates per mesh; this is outside the selected practical schedule and requires a budget/scope decision before long compute |
| A larger mesh safely supports 5 µs | It can reduce its growth work by roughly 40,000 updates; treat this as optional savings after evidence, not a reason for repeated speed trials |
| Approaching allowance | Record completed age, failed/passing checks and remaining cost; no open-ended search or silent budget extension |
| Wall-clock forecast | Measure whole-command throughput on the first 5,000-update growth block per mesh, including DPM and reports; cell count or old-machine timings cannot give a reliable runtime forecast |

| Campaign order | Purpose |
| --- | --- |
| First: 60k | Complete the transition checks and first longer growth block before copying the numerical recipe |
| Next: 2.6M feasibility check | Its owning Server 4 chat tests the same route through a first longer block; catch an impractical fine-wall step early without changing fleet ownership |
| Then: remaining meshes | Use the selected common physical packet for 342k, 680k and 997k; complete each 200 ms endpoint within the schedule |
| Completion | Collect all five common-age endpoints and final-window metrics; report unsuccessful meshes explicitly rather than substitute a different age or silently drop them |

| Scheduling rule | Requirement |
| --- | --- |
| Settings transition | Do not change the EWF packet, increase timestep and freeze bulk in one operation; verify each transition separately |
| Adjustment allowance | Use the per-mesh EWF-adjustment count above; any extra adjustment consumes the 10,000-iteration contingency. This new EWF schedule is separate from the existing startup preparation budget |
| Failed readiness | Recover the numerical/source problem or preserve an unqualified endpoint; do not freeze a failing state simply to meet the time target |
| Film stationarity before freeze | Not required; growing film remains an accepted limitation, separate from numerical and bulk-preparation checks |
| Clock during adjustment | All accepted production film advancement during bulk-active adjustment and the freeze check counts toward 200 ms |
| Final active-bulk allowance | Reserve 195–200 ms on every mesh; do not consume this interval with frozen development |
| Unequal startup ages | Include actual startup age; record each freeze age and preparation difference; equal final age alone does not remove startup-history effects |
| Pilot budget | Reserve enough film age for qualification and final bulk response; do not plan frozen development all the way to 200 ms |
| Branch accounting | Count only accepted continuation age; exclude discarded sibling tests and disposable fixtures |
| Fixed-input solves | Minimum scheduled command `/solve/iterate 1000`; use larger counts up to the next required settings, qualification or horizon decision. No planned short smoke or trim solves |
| Native execution | Submit a prepared native TUI journal for each fixed-input stage; avoid Python-driven short iteration loops and per-window remote command dispatch |
| Assessment windows | A 1,000-update analysis window is not a command boundary; assess consecutive windows inside a larger native solve |
| Observation | Read passive native output during the solve; no synchronous status/report queries or pauses for chat updates |
| Failure protection | Long requested commands may stop early on an actual numerical failure or guard breach; the 1,000-iteration minimum does not require continuing a failing solve |
| Checkpoint cost | Use native server-local autosaves during long commands; full save/reopen verification at consequential transitions and final endpoints, not every analysis window |
| Exact horizon | Plan the final block in advance with at least 1,000 iterations and a qualified fixed step, while preserving particle/source timing; do not leave a short 200 ms trim command |
| Recovery | Preserve failed evidence and restore a verified parent; requalify affected numerical controls without resetting film fields |
| Stop at 200 ms | Do not extend only because film mass still grows or differs from 6 kg |
| Unsettled bulk at 200 ms | Report the remaining bulk/preparation sensitivity; do not silently extend one mesh and compare unequal ages |
| Storage / ownership | Server-local checkpoints and transcripts; selected shared start/final pairs only; existing Phase 9 fleet and restart restrictions remain |

## Acceptance and comparison evidence

| Check | Plan v1 rule |
| --- | --- |
| Film growth | Allowed at 200 ms; report storage rate and its trend |
| Practical completion | Reach 200 ms with usable numerical evidence and final bulk-active outputs; no automatic extra iterations for film stationarity, residual perfection or a prescribed film mass |
| Final bulk screen | Use the existing Phase 9 5% pressure / 10% inventory / 5%-of-inlet liquid-outlet range thresholds on the final 1,000-update window; this shortened check does not establish the original two-window qualification; report remaining drift at 200 ms |
| Accuracy scope | No mandatory timestep-refinement study on every mesh, higher-order scheme campaign or formal convergence-order fit; different selected timesteps remain a mesh-comparison limitation |
| Numerical fields | Finite mass, thickness and velocity; nonnegative thickness; no clipping or unresolved extreme-speed bursts |
| Film Courant | Initial operating ceiling 0.1; preserve/reduce step above it; reject at 1 or above. These are campaign guards, not universal stability guarantees |
| Inner convergence | Every recorded film update meets the 1e-5 stop criterion; missing residuals are not passes |
| Film accounting | Retain the corrected native-source convention and existing 1% block consistency screen; include direct drain and each physical transfer once |
| Accounting interpretation | Distinguish a reported-rate discrepancy from proven physical mass loss; investigate the former before promoting the run |
| Entrainment evidence | Report stripping/separation rates and their destination; enabled flags alone do not establish credible entrainment |
| Drainage evidence | Separate direct film removal, native film outflow, bulk collector removal and release back to particles/bulk |
| Spatial fields | Thickness, mass-weighted speed and transport toward the collector; upper/lower inventory and wall coverage |
| Bulk outputs | Pressure drop, bulk liquid inventory and boundary-only liquid carryover with bulk equations active; collector sources separate |
| Time comparison | Common 200 ms endpoint and common final film-time window; retain raw histories rather than compare endpoints alone |
| Mesh interpretation | Compare film mass/distribution, drain/release and bulk outputs; document wall discretization, timestep and preparation differences |
| Claim boundary | Ongoing storage is an accepted Phase 9 limitation; time-step, startup and bulk-relaxation effects must remain visible alongside mesh effects |

## Cost and evidence basis

| Item | Selection or observation | Source |
| --- | --- | --- |
| Reporting cost | Use the tested 17 essential per-update reports during frozen development; restore required bulk histories during active stages | [Report-cost result](../phase-07-2a-wall-liquid-routing/stage-04-ewf-wall-parameters/report-cost/results.md) |
| Reporting delivery | Keep essential local histories and achieved inner residuals; avoid redundant reports, interactive plots and repeated remote report requests during native solves | Human command/overhead direction; report-frequency reduction remains separate from the tested report-count reduction |
| Runtime measure | Accepted film milliseconds per wall minute, including qualification/recovery and final bulk cost | [Film-development method](../phase-07-2a-wall-liquid-routing/stage-03-shortened-reconstruction/early-ewf-startup/film-development/results.md) |
| 6 kg is not equilibrium | N45606 retained 6.36 kg with positive storage and repeated inner residual failures | [Case history](../phase-07-2a-wall-liquid-routing/stage-02-combined-ewf-roughness/case-history-N45606.md) |
| Growth persists | Stage 3 reached 9.54 kg at 500 ms with frozen bulk and positive storage | [500 ms experiment](../phase-07-2a-wall-liquid-routing/stage-03-shortened-reconstruction/early-ewf-startup/inlet-speed-500ms/results.md) |
| Solver candidate | Sequential 5 µs passed all 1,000 inner solves and suppressed the coupled-branch burst; source consistency remained unqualified | [Staged-finalisation results](../phase-07-2a-wall-liquid-routing/stage-04-ewf-wall-parameters/staged-finalisation/results.md) |
| Retain release | Stripping OFF reduced short-window variation but increased storage and failed longer checks | [Setting sensitivity](../phase-07-2a-wall-liquid-routing/stage-04-ewf-wall-parameters/setting-sensitivity/results.md) |
| Drain capability | Direct film removal proved with frozen bulk; upper-wall delivery remains a separate issue | [Direct drain](../phase-07-2a-wall-liquid-routing/stage-04-ewf-wall-parameters/ewf-only-drain/results.md) |
| Frozen-flow limit | Fluent assumes converged bulk flow and negligible film influence for its steady frozen-flow formulation; this plan uses freezing as preparation followed by bulk reactivation | [Fluent 2025 R2 theory](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_th/flu_th_ewf_sec_sol_alg.html) |

| Required figure | Axes / content |
| --- | --- |
| Development | Film mass versus actual film age for each mesh; mark bulk freeze/reactivation |
| Film budget | Input, direct drain, release and storage rates versus film age; use the verified source convention |
| Numerical health | Accepted step, Courant, achieved film residuals and mass-weighted/maximum speed |
| Common-age comparison | Shared-scale wall thickness at 200 ms; compact table of film mass, drainage, release and active-bulk outputs |
