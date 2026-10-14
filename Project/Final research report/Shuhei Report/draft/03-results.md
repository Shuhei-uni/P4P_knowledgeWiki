# Part 3 — Results

<!-- Findings follow the physical model-development questions, rather than experiment date. -->

## 4. Results

The results follow liquid from inlet placement to wall retention, collection and film development. Earlier exploratory studies are retained in Appendix A.13.

Each comparison uses its stated mesh and settings. Outlet liquid flow is positive outwards unless a signed value is given. Steady iteration describes numerical development; accepted film time describes the transient film calculation.

### 4.1. Mesh development and the wall-liquid field

The polyhedral–hexahedral mesh had larger interior cells, polyhedral transitions and thin layers along the wall (Figure 6). The workflow gave control over the mesh near the expected liquid path; Section 3.4 gives its near-wall resolution.

At iteration 10,000, the historical tetrahedral field showed thin wall-side liquid enrichment. The 60,964-cell SIMPLE reconstruction showed a broader region with a higher liquid fraction. Inlet representation and preparation also differed, and the coarse SIMPLE state had a large mass-balance error. The comparison shows changed fields; reduced numerical diffusion remains a possible explanation, not a measured accuracy gain.

![Native mesh sections and liquid-fraction fields for the historical tetrahedral case and polyhedral–hexahedral reconstruction](../figures/results-mesh-spatial-comparison.png)

*Figure 6. Mesh sections (a–b) and bulk-liquid fraction (c–d) at each geometry's inlet midpoint. Left: historical split-feed tetrahedral case, 7,601,261 cells. Right: mixed-feed SIMPLE reconstruction, 60,964 cells. Both liquid fields are saved at iteration 10,000 on a common 0–1 scale. Each column uses one case mesh.*

<!-- Evidence: [native mesh and liquid-field comparison, source pairs and export manifests](../../../meetings/Poster/poster-sections/mesh-and-volume-fraction-comparison.md); solved 60k topology and wall-resolution evidence in Appendix A.10. The separate 342k mesh illustration used elsewhere is not substituted for the 60k contour's mesh here. -->

### 4.2. Two-phase inlet and wall-side liquid placement

Split feed produced a more continuous liquid-rich wall band and deeper lower-region enrichment than mixed feed (Figure 7). At nominal 26.81 m/s, retained liquid increased by 471.9 kg, or 37.4% (Table 4). Split feed retained more liquid at all five tested speeds, 20.11–32.14 m/s.

Both cases used the same 60,964-cell mesh, total phase feed, Coupled settings, initialisation and 10,000-update horizon. Mixed feed supplied both phases across both inlet faces; split feed supplied liquid through the wall-side strip. Complete phase segregation was an assumed profile (Section 3.3). It changed internal liquid placement but did not provide collection: both cases discharged almost all incoming liquid through the steam outlet.

![Bulk-liquid fraction at inlet height and through the vessel height with mixed and wall-side split feed](../figures/results-inlet-spatial-comparison.png)

*Figure 7. Bulk-liquid fraction at nominal 26.81 m/s and iteration 10,000. (a–b) Inlet-height sections; (c–d) vertical centre sections. Mixed feed: (a, c); split feed: (b, d). Both use a 0–1 scale, a closed bottom, and no absorber or EWF. Contours show distribution; volume integrals quantify mass.*

*Table 4. Matched inlet-placement results. Inventories are iteration-10,000 endpoints; outlet ratios use iterations 9500–10,000. Liquid feed was 116.9387 kg/s.*

| Quantity | Mixed feed | Wall-side split feed |
| --- | ---: | ---: |
| Bulk-liquid inventory (kg) | 1262.6 | 1734.5 |
| Outward steam-outlet liquid / liquid feed (%) | 99.671 | 99.404 |

<!-- Evidence: [matched inlet setup and numerical basis](../../../experiments/phase-08-storyline-reconstruction/stage-01-60k-storyline/baseline-lineage-audit.md), [mixed-feed results](../../../experiments/phase-08-storyline-reconstruction/stage-01-60k-storyline/f1-one-inlet/results.md), [split-feed inventory and spatial findings](../../../experiments/phase-08-storyline-reconstruction/stage-01-60k-storyline/f2-split-inlet/results.md), and [native inlet-plane exports](../../../meetings/Poster/poster-sections/mesh-and-volume-fraction-comparison.md). Percentage inventory change is calculated from the rounded published endpoint values. -->

### 4.3. Liquid accumulation and the need for collection

The three finer split-inlet SIMPLE cases accumulated liquid near the wall and base while discharging little through the steam outlet (Table 5; Figure 8). At iteration 3000, the 997,604-cell case held 69.16% of its liquid below $y=1$ m.

*Table 5. Absorber-free checkpoints at iteration 3000 under the same reduced-relaxation SIMPLE settings. The fields are still developing.*

| Cells | Bulk-liquid inventory (kg) | Outward steam-outlet liquid (kg/s) |
| ---: | ---: | ---: |
| 342,609 | 453.612 | 2.2080 |
| 679,970 | 455.409 | 1.5321 |
| 997,604 | 333.142 | 0.003623 |

![Liquid inventory and outlet flow across the three finer absorber-free meshes](../../../experiments/phase-08-storyline-reconstruction/stage-02-fine-mesh-simple/direct-student-342k/n3000/figures/matched-mesh-checkpoints.png)

*Figure 8. Bulk-liquid inventory and net outward outlet flow at saved checkpoints. All cases use pure split feed, SIMPLE and no absorber. Lines connect saved states; steady solver iterations are not physical time.*

On the 679,970-cell mesh, inventory reached 764.744 kg at iteration 4000, with 69.62% below $y=2$ m. Outlet liquid was 8.00 kg/s, or 6.84% of the feed. The next continuation failed after printed iteration 4211; its cause was not isolated.

The next studies used a liquid-selective source after unresolved full-geometry trials (Appendix A.13).

<!-- Evidence: [matched finer-mesh checkpoints](../../../experiments/phase-08-storyline-reconstruction/stage-02-fine-mesh-simple/direct-student-342k/n3000/results.md), [997k spatial result](../../../experiments/phase-08-storyline-reconstruction/stage-02-fine-mesh-simple/direct-student-997k/n3000/results.md), [680k accumulation and failed continuation](../../../experiments/phase-08-storyline-reconstruction/stage-02-fine-mesh-simple/direct-student-680k/n4000/results.md), [mixed-inlet Coupled account](../../../experiments/phase-08-storyline-reconstruction/stage-01-60k-storyline/f1-one-inlet/results.md) and [full-geometry scope decision](../../../experiments/phase-06-full-geometry-with-brine-pool/conclusion.md). -->

### 4.4. Reduced-feed development and inlet ramp

The startup and wall studies used the 60,964-cell split-inlet model, with full feed of 116.92 kg/s liquid and 80.69 kg/s steam.

At 25% feed with throughput collection, inventory fell only 0.30% over iterations 1080–1580, ending at 31.3571 kg (Figure 9). Minimum scaled continuity was $3.2056\times10^{-4}$.

The hold was unintended: a failed ramp command had left both inlet rates unchanged. A corrected, checked 2000-update ramp reached full feed at iteration 3580. Ramp continuity peaked at $1.1166\times10^{-2}$ and inventory reached 182.5178 kg. The hold revealed a useful startup route: develop reduced-feed fields before loading them.

![Residuals, bulk-liquid inventory and actual inlet loading during early development](../figures/results-described-early-development.png)

*Figure 9. Scaled bulk residuals, liquid inventory and reported liquid-inlet/absorber command. A: ramp start, iteration 1580. B: full feed and change to Coupled with Global Time Step, iteration 3580. C: EWF activation, iteration 5586. The inherited, unsolved inlet-report value at iteration 1 is omitted. Appendix A.15.1 records the stages.*

<!-- Evidence: [selected case history](../../../experiments/phase-07-2a-wall-liquid-routing/stage-02-combined-ewf-roughness/case-history-N45606.md), [carrier residuals](../../../../PyAnsys/output/phase72a-lineage-N45606/20261005/carrier-residuals.csv) and [liquid histories](../../../../PyAnsys/output/phase72a-lineage-N45606/20261005/selected-lineage-histories.csv). -->

### 4.5. Full-feed control and mass balance

The smooth-wall, EWF-off Coupled continuation became the iteration-5586 comparison parent. Continuity fell and inventory approached 296 kg, but residual oscillations, outlet reverse flow and turbulent-viscosity limiting persisted.

Applied absorber removal matched its 116.92 kg/s command, but another 24.3344 kg/s left through the steam outlet. The signed liquid boundary-plus-source remainder was therefore −24.3344 kg/s, or −20.81% of the feed. Source application was verified; conservation remained unresolved (Appendix A.15.2).

<!-- Evidence: [full-feed control continuation](../../../experiments/phase-07-1a-absorber-convergence/roughness-family/r0-smooth-control/results.md), [baseline handoff](../../../experiments/phase-07-2a-wall-liquid-routing/baseline-control-handoff.md), [aligned native full-feed control histories](../../../../PyAnsys/output/phase71a_r0_control_run4/report-histories-batched.json) and [full-feed control accounting audit](../../../experiments/phase-07b-full-geometry-liquid-removal/convergence-investigation/shuhei-audit.md). -->

### 4.6. Roughness response from the common parent

The roughness response was non-monotonic (Figure 10). At $C_s=0.5$, 0.05 mm raised mean outlet flow by 21.21%; 8 mm reduced it by 44.09%, from 24.3715 to 13.6253 kg/s. Increasing $C_s$ lowered flow at both fixed heights.

![Effect of roughness height and constant on bulk-liquid steam-outlet flow](../figures/results-described-roughness.png)

*Figure 10. Mean outward steam-outlet liquid flow with EWF off. Left: height sweep at $C_s=0.5$. Right: constant sweep at $k_s=0.5$ and 2 mm; dashed line: smooth continuation. All twelve cases ran 3000 updates from iteration 5586. Means use iterations 8087–8586; lines connect tested settings.*

The 8 mm case lost 187.109 kg of bulk liquid. Oscillations and incomplete balances prevented an efficiency claim. The later 0.045 mm continuation also changed bulk advancement and film stepping, so it did not isolate roughness (Appendix A.12).

<!-- Evidence for the material-reference continuation: [Commercial-steel results](../../../experiments/phase-07-2a-wall-liquid-routing/stage-04-ewf-wall-parameters/commercial-steel/results.md). The 0.045 mm value is a selected reference, not a measured separator finish or a matched roughness-only comparison. -->

<!-- Evidence: [roughness-screen results and sample standard deviations](../../../experiments/phase-07-2a-wall-liquid-routing/roughness-family/results.md#matched-tail-comparison) and [comparison figure and provenance](../../../observations/07-wall-liquid-interaction.md). The source's later statement identifying the lowest outlet conflicts with its table; the table values are used here. -->

### 4.7. Accretion-enabled wall-film response

From common smooth-wall fields with throughput collection, the EWF package reduced mean outlet liquid by 92.88%, from 24.369 to 1.735 kg/s over iterations 8087–8586 (Figure 11). Phase accretion and coupled film equations were on; momentum feedback was off. Earlier trials are in Appendix A.11.

![Bulk-liquid steam-outlet histories with EWF off and the accretion-enabled package](../figures/results-described-film-outlet.png)

*Figure 11. Outward bulk-liquid outlet flow over 3000 updates from the common full-feed parent. The EWF case uses a fixed 10 µs film step. All 3001 points are shown without smoothing; shading marks the final 500 updates.*

Bulk mass fell from 295.8536 to 63.0234 kg, while film mass reached only 3.1112 kg. The sections showed less liquid beside the wall (Figure 12). The film package changed liquid distribution, but changing inventories and an open combined liquid account prevent an efficiency claim.

![Matched bulk-liquid volume-fraction sections for the film-disabled continuation and accretion-enabled film case](../figures/bulk-comparison-described-film-treatment.png)

*Figure 12. Bulk-liquid fraction at iteration 8586. Left: EWF off. Right: accretion-enabled film case. Native X–Y centre sections at Z = 0 m use the same orthographic camera and 0–1 scale. Film thickness and drainage are separate quantities.*

<!-- Evidence: [film-disabled and accretion-enabled comparison](../../../observations/07-wall-liquid-interaction.md), [wall-film-screen results and native sections](../../../experiments/phase-07-2a-wall-liquid-routing/ewf-family/results.md#native-phase-2-volume-fraction-contours--2026-09-23), [paired contour provenance](../figures/bulk-comparison-described-film-treatment.provenance.json) and [selected endpoint histories](../../../../PyAnsys/output/phase72a-lineage-N45606/20261005/selected-lineage-histories.csv). The film-disabled continuation's mean is from its separate comparison run and is not substituted for the roughness screen's smooth-wall mean. -->

### 4.8. Contact collection and combined model development

Shorter depletion time reduced collector inventory but increased removal variability (Appendix A.4). The combined continuation applied 10 µs contact collection, 0.5 mm roughness and a 1 µs film step together; their effects were not isolated.

At iteration 45606, film mass was 6.3600 kg after 120.769 ms. Final-1000-update drainage remained 9.98% below accretion, so the film continued to fill. Appendix A.15.3 and the linked case history retain the endpoints and detailed film account.

<!-- Evidence: [contact-strength screens](../../../experiments/phase-07-2a-wall-liquid-routing/stage-02-combined-ewf-roughness/results.md#all-liquid-contact-absorber-trial), [complete selected case history](../../../experiments/phase-07-2a-wall-liquid-routing/stage-02-combined-ewf-roughness/case-history-N45606.md) and [corrected film ledger](../../../../PyAnsys/output/phase72a-lineage-N45606/20261005/corrected-film-development-summary.json). The short strength-screen branch is distinct from the original-field continuation retained in Appendix A.9. -->

### 4.9. Shortened startup with early wall-film activation

Shortened startup activated Coupled flow, contact collection, roughness and film in the reduced-feed fields. A 500-update activation hold preceded the 2000-update ramp and 1000-update full-feed hold. Ramp peaks were lower (Figure 13; Table 6).

![Historical and shortened startup at matched inlet-ramp progress](../figures/results-described-startup.png)

*Figure 13. Continuity with common normalisation, bulk + film inventory and native signed outlet liquid flux; negative is outwards. Orange: historical iterations 1581–4580. Blue: shortened iterations 2081–5080. The dashed line marks full feed after 2000 ramp updates; shading marks the following hold. The activation hold is excluded. All source points are shown without smoothing.*

*Table 6. Ramp peaks. Reductions are relative to the historical startup; the settings test a combined recipe.*

| Measure | Historical startup | Shortened startup | Reduction (%) |
| --- | ---: | ---: | ---: |
| Scaled continuity | 0.011166 | 0.0033336 | 70.15 |
| Bulk + film inventory (kg) | 182.518 | 53.9715 | 70.43 |
| Outward bulk-liquid steam-outlet flow (kg/s) | 8.99517 | 2.17887 | 75.78 |

The excluded activation hold had a continuity peak of 0.10593, exceeding the historical ramp peak. At iteration 5080, bulk and film masses were 61.0549 and 0.1645 kg. Almost all film input was still stored (Appendix A.15.4). All ramp updates met the recorded inner-film tolerance, but 15 of the final 100 hold updates failed it. The recipe reduced loading peaks without establishing complete startup convergence (Appendix A.9.4).

<!-- Evidence: [shortened-startup results](../../../experiments/phase-07-2a-wall-liquid-routing/stage-03-shortened-reconstruction/early-ewf-startup/results.md), [audited metrics, native source checks and normalisation](../../../../PyAnsys/output/phase72a-stage3-early-ewf-server1/20261005/analysis-summary.json) and [native final histories for Appendix A.15.4](../../../../PyAnsys/output/phase72a-stage3-early-ewf-server1/20261005/final-histories.json). -->

### 4.10. Film development under frozen bulk fields

Film mass increased from 0.1645 kg at 3.5 ms to 9.5444 kg at 500 ms (Figure 14). After iteration 5080, bulk equations were frozen, leaving bulk inventory at 61.0549 kg and outward bulk-liquid outlet flow at 3.4300 kg/s. These fixed values describe held forcing; reciprocal bulk depletion was not calculated.

![Film inventory, accretion and drainage against accepted film time through 500 ms](../figures/results-film-development-reference500ms.png)

*Figure 14. Reference-speed film mass and native accretion/drainage rates against accepted time since dry-film activation. Bulk fields are frozen. Markers locate Figure 15 snapshots and the 500 ms endpoint; shading marks the final 10 ms. Selected records are unsmoothed; rejected sibling continuations are excluded.*

The film spread and thickened over the lower and middle wall (Figure 15). Between 75.66 and 265.18 ms, wall area with thickness at least 0.10 mm increased from 40.34% to 61.98%; maximum thickness rose from 0.253 to 0.291 mm.

![Native wall-film thickness at three saved film times](../figures/wall-film-described-development.png)

*Figure 15. Film thickness at 5.90, 75.66 and 265.18 ms; film masses are 0.360, 3.864 and 6.688 kg. Views use the same orthographic camera and 0–0.30 mm scale. Native Fluent wall geometry and facet values are rendered without spatial interpolation.*

*Table 7. Endpoint film mass and mean late-window rates. The 265.184 ms rates use the latest complete 1000-update window; 500 ms rates use the final 10 ms with interval-overlap weighting. Storage is mass change divided by accepted film time.*

| Film time (ms) | Film mass (kg) | Accretion (kg/s) | Drainage (kg/s) | Storage (kg/s) | Drainage deficit (%) |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 265.184 | 6.6883 | 81.121 | 68.177 | 12.954 | 15.96 |
| 500.000 | 9.5444 | 81.121 | 69.600 | 11.528 | 14.20 |

Drainage remained below input (Table 7). At 500 ms, storage was still 11.528 kg/s, so the film was not stationary. Only the reference-speed arm reached this endpoint (Appendix A.9).

<!-- Evidence: [selected film-development results, spatial metrics and reporting windows](../../../experiments/phase-07-2a-wall-liquid-routing/stage-03-shortened-reconstruction/early-ewf-startup/film-development/results.md), [500 ms campaign results](../../../experiments/phase-07-2a-wall-liquid-routing/stage-03-shortened-reconstruction/early-ewf-startup/inlet-speed-500ms/results.md), [selected reference-speed CSV](../../../../PyAnsys/output/phase72a-stage3-speed-sensitivity-server1/20261006/selected-film-history-reference.csv) and [Figure 14 provenance](../figures/results-film-development-reference500ms-provenance.json). -->

### 4.11. Added film-release mechanisms and direct drainage

Later tests enabled stripping, splashing, droplet collection and edge separation, retaining film-to-flow momentum feedback off. After 4000 bulk updates, 50 ms of frozen-bulk development increased film mass from 0.2638 to 5.9070 kg. Final approximately 5 ms mean stripping and edge-separation rates were 64.56 and 51.87 kg/s, while storage was 80.81 kg/s. A separate splash contribution was unresolved.

Native film outflow was zero during that interval. Extending the film domain onto the lower wall then allowed a matched direct-sink test (Table 8). The sink removed 0.5088 kg and reduced lower-wall film mass by 70.32% with all bulk equations frozen.

*Table 8. Direct drainage over 15 ms from identical fields and initial film mass of 9.7526 kg. Both arms use the same expanded film domain; only the sink is switched.*

| Quantity | Drain OFF | Drain ON |
| --- | ---: | ---: |
| Final lower-wall film (kg) | 0.18752 | 0.05565 |
| Final total film (kg) | 11.1726 | 10.9829 |
| Direct sink removal (kg) | 0 | 0.5088 |
| Native film outflow (kg) | 0.5302 | 0.2111 |
| Direct sink plus native outflow (kg) | 0.5302 | 0.7199 |

In the longer continuation, lower film stayed near 0.056 kg while upper film grew. The complete 405 ms record, including the rejected tail, contains 15.16 kg of direct removal and a 27.58 kg increase in film inventory. Storage was positive before the Courant-guard crossing. Local drainage therefore did not stop accumulation elsewhere. These tests used different fields and forces from the early film study; particle release was internal transfer, while the sink removed liquid from the model (Appendix A.12).

<!-- Evidence: [release-mechanism continuation](../../../experiments/phase-07-2a-wall-liquid-routing/stage-04-ewf-wall-parameters/realism-continuation/feedback-off/results.md), [matched direct-drain test](../../../experiments/phase-07-2a-wall-liquid-routing/stage-04-ewf-wall-parameters/ewf-only-drain/results.md) and [long drain-ON development](../../../experiments/phase-07-2a-wall-liquid-routing/stage-04-ewf-wall-parameters/ewf-only-drain/long-development/results.md). -->

### 4.12. Numerical assessment of the selected development path

The shortened-startup contact source matched independently evaluated removal at all 3500 solved updates. A separate film-step test from identical fields showed that 20 µs passed local field and ledger checks over 2.5 ms, whereas 25 µs exceeded the 0.1% ledger-error limit.

These checks verified implementation and supported local step selection. Repeated inner-film failures, missing residual output from the alternative algorithm and continued storage prevented full convergence (Appendix A.9.4). The next comparison examines mesh sensitivity in the combined model.

<!-- Evidence: [combined-history residual checks](../../../experiments/phase-07-2a-wall-liquid-routing/stage-02-combined-ewf-roughness/case-history-N45606.md#ewf-residuals), [shortened-startup source audit](../../../experiments/phase-07-2a-wall-liquid-routing/stage-03-shortened-reconstruction/early-ewf-startup/results.md#film-evidence-and-numerical-limits), [matched-time film-step assessment](../../../experiments/phase-07-2a-wall-liquid-routing/stage-03-shortened-reconstruction/early-ewf-startup/film-development/results.md), [local screen criteria](../../../experiments/phase-07-2a-wall-liquid-routing/stage-03-shortened-reconstruction/early-ewf-startup/film-development/setup.md), [20 µs comparison JSON](../../../../PyAnsys/output/phase72a-stage3-film-development-server1/20261005/mid-film-sensitivity-20us.json) and [25 µs comparison JSON](../../../../PyAnsys/output/phase72a-stage3-film-development-server1/20261005/mid-film-sensitivity-25us.json). -->

### 4.13. Phase 9 — Final model and mesh sensitivity

> **Results pending — reserve four main-body pages.** This section will bring together the final wall-film, release and collection model across the supplied mesh resolutions. The slots below are reserved for verified results; no mesh-convergence conclusion is yet available.

#### 4.13.1. Comparison basis

The supplied meshes contain 60,964, 342,609, 679,970, 997,604 and 2,596,657 fluid cells. The selected plan combines split feed, Mixture/RNG bulk flow, wall-film momentum and accretion, droplet collection and release, and direct lower-wall drainage. Its nominal target is 200 ms film age, with bulk equations frozen during middle film development and active again over 195–200 ms.

The final comparison must confirm common geometry, inlet rates, wall treatment, physical models and collector scope from saved cases. Record any differences in film steps or numerical controls. Slit and ramp geometries answer separate design questions and are excluded from the refinement series.

#### 4.13.2. Liquid distribution across mesh resolution

> **Figure 16 reserved — spatial comparison.** Show matched bulk-liquid sections and wall-film thickness at a common accepted film age. Use the same view and colour range across meshes. Identify wall accumulation, film coverage and access to the lower collector. Retain incomplete or failed cases with their verified endpoints clearly marked.

#### 4.13.3. Development, drainage and mesh sensitivity

> **Figure 17 reserved — development and mesh response.** Plot film inventory, collection/removal rates, steam-outlet liquid and pressure difference against accepted film time. Mark bulk-active and frozen intervals, rejected updates and the common comparison window. Compare mesh endpoints only after assessing continued time development.

*Table 9. Reserved final mesh comparison. Use a common reporting window; retain bulk and film mass, direct drainage, bulk collector removal and signed balance remainders as separate quantities. Cell counts below are verified inputs, not completed result values.*

| Fluid cells | Accepted film age (ms) | Bulk / film mass (kg) | Outlet liquid (kg/s) | Bulk / direct-film removal (kg/s) | Balance remainder (kg/s) |
| ---: | --- | --- | --- | --- | --- |
| 60,964 | Pending | Pending | Pending | Pending | Pending |
| 342,609 | Pending | Pending | Pending | Pending | Pending |
| 679,970 | Pending | Pending | Pending | Pending | Pending |
| 997,604 | Pending | Pending | Pending | Pending | Pending |
| 2,596,657 | Pending | Pending | Pending | Pending | Pending |

**Finding to complete:** state which liquid distributions and rates persist across refinements, which remain sensitive, and whether film storage is still changing. Resolve particle transfers separately from external collection. If comparable fields or conservation evidence remain incomplete, report that specific limit without claiming mesh independence.

<!-- Phase 9 layout reservation: four main-body pages for the comparison basis, Figure 16, Figure 17, final summary table and evidence-based finding. Figure/table text above is a preparation instruction, not a completed caption or numerical result. Owners: [Phase 9 context](../../../experiments/phase-09-mesh-convergence/CONTEXT.md), [mesh/setup audit](../../../experiments/phase-09-mesh-convergence/setup.md), [EWF Plan v1](../../../experiments/phase-09-mesh-convergence/ewf-plan-v1.md), [680k lane setup](../../../experiments/phase-09-mesh-convergence/server1-680k/setup.md). The inherited preparation endpoints have unequal film ages; only matched verified development can support final refinement claims. -->
