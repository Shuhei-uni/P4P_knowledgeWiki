# Part 3 — Results

<!-- Findings follow the physical model-development questions, rather than experiment date. -->

## 4. Results

Mesh and inlet comparisons first assess liquid delivery and retention. Collector and startup studies then provide fields for wall comparisons. Finally, film histories test whether captured liquid drains, remains stored or returns to droplets. Earlier exploratory studies are retained in Appendix A.13.

Each comparison uses its stated mesh and settings. Outlet liquid flow is reported as positive outwards unless a signed value is given. Steady-solver iterations track numerical development; accepted film time tracks the transient film calculation.

### 4.1. Mesh development and the wall-liquid field

The polyhedral–hexahedral mesh had larger interior cells, polyhedral transitions and thin layers along the wall (Figure 8). The mesh workflow provided control near the expected liquid path; Section 3.4 gives the near-wall resolution.

At iteration 10,000, the historical tetrahedral case showed a thin region of liquid enrichment near the wall. The 60,964-cell SIMPLE reconstruction showed a broader region with a higher liquid fraction. However, inlet representation and preparation also differed, and the coarse SIMPLE state had a large mass-balance error. These differences do not establish a mesh effect: reduced numerical diffusion remains a possible explanation, not a measured gain in accuracy.

![Native mesh sections and liquid-fraction fields for the historical tetrahedral case and polyhedral–hexahedral reconstruction](../figures/results-mesh-spatial-comparison.png)

*Figure 8. Mesh sections (a–b) and bulk-liquid volume-fraction fields at iteration 10,000 (c–d). The reconstructed case shows broader wall enrichment; the mesh, inlet and preparation differ between cases, so the comparison does not isolate a mesh effect.*

<!-- Evidence: [native mesh and liquid-field comparison, source pairs and export manifests](../../../Poster/poster-sections/mesh-and-volume-fraction-comparison.md); solved 60k topology and wall-resolution evidence in Appendix A.10. The separate 342k mesh illustration used elsewhere is not substituted for the 60k contour's mesh here. -->

### 4.2. Two-phase inlet and wall-side liquid placement

Split feed produced a more continuous liquid-rich wall band and deeper lower-region enrichment than mixed feed (Figure 9). At a nominal speed of 26.81 m/s, the bulk-liquid inventory at iteration 10,000 was 1262.6 kg with mixed feed and 1734.5 kg with split feed, a difference of 471.9 kg, or 37.4%. Split feed had a larger bulk-liquid inventory at all five tested speeds in the range 20.11–32.14 m/s.

Both cases used the same 60,964-cell mesh, total phase feed, Coupled settings, initialisation and 10,000-update horizon. Mixed feed supplied both phases across both inlet faces; split feed supplied liquid through the wall-side strip. Complete phase segregation was an assumed profile (Section 3.3). Over iterations 9500–10,000, the outward liquid flow through the steam outlet averaged 99.671% of the 116.9387 kg/s liquid feed for mixed feed and 99.404% for split feed. The inventory difference therefore accompanied almost complete liquid discharge through the steam outlet, rather than discharge through a separate collection route.

![Bulk-liquid fraction at inlet height and through the vessel height with mixed and wall-side split feed](../figures/results-inlet-spatial-comparison.png)

*Figure 9. Bulk-liquid volume fraction with mixed and wall-side split feed at inlet height (a, b) and through the vessel centre (c, d). Matched sections at iteration 10,000 use a shared 0–1 scale; neither case includes a collector or EWF.*

<!-- Evidence: [matched inlet setup and numerical basis](../../../experiments/phase-08-storyline-reconstruction/stage-01-60k-storyline/baseline-lineage-audit.md), [mixed-feed results](../../../experiments/phase-08-storyline-reconstruction/stage-01-60k-storyline/f1-one-inlet/results.md), [split-feed inventory and spatial findings](../../../experiments/phase-08-storyline-reconstruction/stage-01-60k-storyline/f2-split-inlet/results.md), and [native inlet-plane exports](../../../Poster/poster-sections/mesh-and-volume-fraction-comparison.md). Percentage inventory change is calculated from the rounded published endpoint values. -->

### 4.3. Liquid accumulation and the need for collection

Saved fields from the three finer split-inlet SIMPLE cases showed liquid near the wall and base. Their inventory and outlet histories show accumulation with little discharge through the steam outlet relative to the liquid feed (Figure 10). At iteration 3000, the liquid inventories in the 342,609- and 679,970-cell cases were each about 454–455 kg, whereas the 997,604-cell case held 333.142 kg. The latter case discharged only 0.003623 kg/s through the steam outlet and held 69.16% of its liquid below $y=1$ m. These developing checkpoints do not constitute a mesh-convergence result; Appendix A.17 retains their exact values.

![Liquid inventory and outlet flow across the three finer absorber-free meshes](../../../experiments/phase-08-storyline-reconstruction/stage-02-fine-mesh-simple/direct-student-342k/n3000/figures/matched-mesh-checkpoints.png)

*Figure 10. Liquid inventory (left) and net outlet liquid flow (right) in the finer absorber-free SIMPLE cases. Liquid accumulates while outlet flow remains small relative to the liquid feed. Lines connect saved checkpoints; solver iterations are not physical time.*

On the 679,970-cell mesh, liquid inventory reached 764.744 kg at iteration 4000, with 69.62% below $y=2$ m. Outlet liquid flow was 8.00 kg/s, or 6.84% of the feed. The next continuation failed after printed iteration 4211; its cause was not isolated.

The inlet and mesh studies changed delivery and retention but provided no separate collection route. The subsequent studies introduced a liquid-selective source after unresolved full-geometry drainage trials (Appendix A.13), then tested startup before comparing wall treatments.

<!-- Evidence: [matched finer-mesh checkpoints](../../../experiments/phase-08-storyline-reconstruction/stage-02-fine-mesh-simple/direct-student-342k/n3000/results.md), [997k spatial result](../../../experiments/phase-08-storyline-reconstruction/stage-02-fine-mesh-simple/direct-student-997k/n3000/results.md), [680k accumulation and failed continuation](../../../experiments/phase-08-storyline-reconstruction/stage-02-fine-mesh-simple/direct-student-680k/n4000/results.md), [mixed-inlet Coupled account](../../../experiments/phase-08-storyline-reconstruction/stage-01-60k-storyline/f1-one-inlet/results.md) and [full-geometry scope decision](../../../experiments/phase-06-full-geometry-with-brine-pool/conclusion.md). -->

### 4.4. Reduced-feed development and inlet ramp

The startup and wall studies used the 60,964-cell split-inlet model, with a full feed of 116.92 kg/s liquid and 80.69 kg/s steam.

At 25% feed with throughput collection, bulk-liquid inventory fell only 0.30% over iterations 1080–1580, ending at 31.3571 kg (Figure 11). The minimum scaled continuity residual was $3.2056\times10^{-4}$.

A failed ramp command had left the model at reduced feed until iteration 1580. The corrected 2000-update ramp reached full feed at iteration 3580. During the ramp, the scaled continuity residual peaked at $1.1166\times10^{-2}$ and bulk-liquid inventory reached 182.5178 kg.

![Residuals, bulk-liquid inventory and actual inlet loading during early development](../figures/results-described-early-development.png)

*Figure 11. Reduced-feed hold, loading ramp and full-feed development. The panels show scaled residuals, bulk-liquid inventory and the liquid-feed command against solver iteration. Dashed markers indicate A: ramp start; B: full feed and Coupled activation; C: EWF activation.*

<!-- Evidence: [selected case history](../../../experiments/phase-07-2a-wall-liquid-routing/stage-02-combined-ewf-roughness/case-history-N45606.md), [carrier residuals](../../../../PyAnsys/output/phase72a-lineage-N45606/20261005/carrier-residuals.csv) and [liquid histories](../../../../PyAnsys/output/phase72a-lineage-N45606/20261005/selected-lineage-histories.csv). -->

### 4.5. Full-feed control and mass balance

The smooth-wall, EWF-off Coupled continuation became the iteration-5586 comparison parent. The continuity residual fell and inventory approached 296 kg, but residual oscillations, outlet reverse flow and turbulent-viscosity limiting persisted.

The applied throughput-controlled absorber removal matched its 116.92 kg/s command, but an additional 24.3344 kg/s left through the steam outlet. The signed liquid boundary-plus-source remainder was therefore −24.3344 kg/s, or −20.81% of the feed. Source application was verified; conservation remained unresolved (Appendix A.15.2).

This developing field supplied a common parent for the following wall comparisons. Changes in outlet flow must be interpreted alongside inventory and removal because the parent did not establish a closed liquid account.

<!-- Evidence: [full-feed control continuation](../../../experiments/phase-07-1a-absorber-convergence/roughness-family/r0-smooth-control/results.md), [baseline handoff](../../../experiments/phase-07-2a-wall-liquid-routing/baseline-control-handoff.md), [aligned native full-feed control histories](../../../../PyAnsys/output/phase71a_r0_control_run4/report-histories-batched.json) and [full-feed control accounting audit](../../../experiments/phase-07b-full-geometry-liquid-removal/convergence-investigation/shuhei-audit.md). -->

### 4.6. Roughness response from the common parent

The mean bulk-liquid outlet flow varied non-monotonically with roughness height (Figure 12). At $C_s=0.5$, a roughness height of 0.05 mm raised the mean outlet flow by 21.21% relative to the smooth-wall reference, whereas a height of 8 mm reduced it by 44.09%, from 24.3715 to 13.6253 kg/s. Increasing $C_s$ lowered the flow at both fixed roughness heights.

![Effect of roughness height and constant on bulk-liquid steam-outlet flow](../figures/results-described-roughness.png)

*Figure 12. Mean bulk-liquid outlet flow as a function of (a) roughness height and (b) roughness constant at fixed heights. The height response is non-monotonic; the 8 mm case also loses bulk inventory. EWF is off. Means are calculated over iterations 8087–8586; dashed lines mark the smooth-wall reference.*

The 8 mm case lost 187.109 kg of bulk liquid. Oscillations and incomplete balances prevented an efficiency claim. The later 0.045 mm continuation also changed bulk advancement and film stepping, so it did not isolate the effect of roughness (Appendix A.12).

<!-- Evidence for the material-reference continuation: [Commercial-steel results](../../../experiments/phase-07-2a-wall-liquid-routing/stage-04-ewf-wall-parameters/commercial-steel/results.md). The 0.045 mm value is a selected reference, not a measured separator finish or a matched roughness-only comparison. -->

<!-- Evidence: [roughness-screen results and sample standard deviations](../../../experiments/phase-07-2a-wall-liquid-routing/roughness-family/results.md#matched-tail-comparison) and [comparison figure and provenance](../../../observations/07-wall-liquid-interaction.md). The source's later statement identifying the lowest outlet conflicts with its table; the table values are used here. -->

### 4.7. Accretion-enabled wall-film response

With common smooth-wall starting fields and throughput collection, the EWF package reduced mean outlet liquid flow by 92.88%, from 24.369 kg/s in the film-disabled continuation to 1.735 kg/s in the accretion-enabled case over iterations 8087–8586 (Figure 13). Phase accretion and the coupled film equations were enabled; momentum feedback was disabled. Earlier trials are documented in Appendix A.11.

![Bulk-liquid steam-outlet histories with EWF off and the accretion-enabled package](../figures/results-described-film-outlet.png)

*Figure 13. The accretion-enabled EWF package reduces bulk-liquid outlet flow; changing inventories prevent a collection claim. The smooth-wall cases share the full-feed parent. Shading marks the final 500 iterations; the film step is 10 µs.*

During the accretion-enabled continuation, bulk mass fell from 295.8536 to 63.0234 kg, while film mass reached only 3.1112 kg. The centre sections show less bulk liquid beside the wall in the accretion-enabled case (Figure 14). The film package changed the liquid distribution, but changing inventories and incomplete combined liquid accounting prevent an efficiency claim.

![Matched bulk-liquid volume-fraction sections for the film-disabled continuation and accretion-enabled film case](../figures/bulk-comparison-described-film-treatment.png)

*Figure 14. Less bulk liquid remains beside the wall in the accretion-enabled film case (right) than in the film-disabled continuation (left). Both centre sections are shown at iteration 8586 on a shared 0–1 liquid-volume-fraction scale. Film storage and drainage are assessed separately.*

<!-- Evidence: [film-disabled and accretion-enabled comparison](../../../observations/07-wall-liquid-interaction.md), [wall-film-screen results and native sections](../../../experiments/phase-07-2a-wall-liquid-routing/ewf-family/results.md#native-phase-2-volume-fraction-contours--2026-09-23), [paired contour provenance](../figures/bulk-comparison-described-film-treatment.provenance.json) and [selected endpoint histories](../../../../PyAnsys/output/phase72a-lineage-N45606/20261005/selected-lineage-histories.csv). The film-disabled continuation's mean is from its separate comparison run and is not substituted for the roughness screen's smooth-wall mean. -->

The following tests changed the collection and startup settings, then extended film development to examine drainage and storage.

### 4.8. Contact collection and combined model development

A shorter depletion time reduced collector inventory but increased removal variability (Appendix A.4). The combined continuation used contact collection with a 10 µs depletion time, 0.5 mm roughness and a 1 µs film step simultaneously; the effects of these settings were not isolated.

At iteration 45606, film mass was 6.3600 kg after 120.769 ms. Over the final 1000 updates, drainage remained 9.98% below accretion, so liquid continued to accumulate in the film during this interval. Appendix A.15.3 and the linked case history retain the endpoints and detailed film account.

The shortened-startup comparison below tests whether introducing these treatments before loading reduces the ramp disturbance.

<!-- Evidence: [contact-strength screens](../../../experiments/phase-07-2a-wall-liquid-routing/stage-02-combined-ewf-roughness/results.md#all-liquid-contact-absorber-trial), [complete selected case history](../../../experiments/phase-07-2a-wall-liquid-routing/stage-02-combined-ewf-roughness/case-history-N45606.md) and [corrected film ledger](../../../../PyAnsys/output/phase72a-lineage-N45606/20261005/corrected-film-development-summary.json). The short strength-screen branch is distinct from the original-field continuation retained in Appendix A.9. -->

### 4.9. Shortened startup with early wall-film activation

The shortened startup introduced the combined wall and collection treatment before loading. Relative to the historical inlet ramp, the peak continuity residual fell by 70.15%, peak bulk + film inventory by 70.43%, and peak outward outlet liquid flow by 75.78% (Figure 15). Appendix A.17 lists the peak values.

![Historical and shortened startup at matched inlet-ramp progress](../figures/results-described-startup.png)

*Figure 15. Shortened startup had lower ramp peaks than historical startup. (a) Continuity residual; (b) bulk + film inventory; (c) signed outlet liquid flow, with negative values indicating outward flow. The larger activation disturbance is excluded; the dashed line marks full feed, and shading indicates the subsequent hold.*

The excluded activation hold had a continuity residual peak of 0.10593, exceeding the historical ramp peak. At iteration 5080, bulk and film masses were 61.0549 and 0.1645 kg, respectively. Almost all film input was still stored (Appendix A.15.4). All ramp updates met the recorded inner-film tolerance, but 15 of the final 100 hold updates failed to meet it. The startup procedure reduced loading peaks without establishing complete startup convergence (Appendix A.9.4).

The film was still young at full feed. The following continuation held the bulk fields fixed to examine its development under unchanged forcing.

<!-- Evidence: [shortened-startup results](../../../experiments/phase-07-2a-wall-liquid-routing/stage-03-shortened-reconstruction/early-ewf-startup/results.md), [audited metrics, native source checks and normalisation](../../../../PyAnsys/output/phase72a-stage3-early-ewf-server1/20261005/analysis-summary.json) and [native final histories for Appendix A.15.4](../../../../PyAnsys/output/phase72a-stage3-early-ewf-server1/20261005/final-histories.json). -->

### 4.10. Film development under frozen bulk fields

Film mass increased from 0.1645 kg at 3.5 ms to 9.5444 kg at 500 ms (Figure 16). After iteration 5080, the bulk equations were frozen, holding the bulk inventory at 61.0549 kg and the outward bulk-liquid outlet flow at 3.4300 kg/s. These fixed values describe the held forcing; reciprocal bulk depletion was not calculated.

![Film inventory, accretion and drainage against accepted film time through 500 ms](../figures/results-film-development-reference500ms.png)

*Figure 16. Drainage develops while film inventory keeps rising under frozen bulk forcing. (a) Film mass; (b) film input and drainage. Shading marks the final 10 ms; markers in (a) locate the Figure 17 snapshots and the endpoint.*

The film spread and thickened over the lower and middle wall (Figure 17). Between 75.66 and 265.18 ms, the proportion of wall area with a film thickness of at least 0.10 mm increased from 40.34% to 61.98%; the maximum thickness rose from 0.253 to 0.291 mm.

![Native wall-film thickness at three saved film times](../figures/wall-film-described-development.png)

*Figure 17. Wall-film thickness at three saved times with bulk fields frozen. Film times and masses are labelled; all three views use the same camera and a 0–0.30 mm colour scale.*

Over the final 10 ms ending at 500 ms, mean accretion was 81.121 kg/s and drainage was 69.600 kg/s, a 14.20% drainage deficit. The film storage rate, calculated from mass change divided by elapsed accepted film time over this window, was 11.528 kg/s. The film mass curve therefore continued to rise late in the run despite increasing drainage. Rates use interval-overlap weighting; Appendix A.17 retains the earlier 265.184 ms result and its different 1000-update window. Only the reference-speed arm reached the 500 ms endpoint (Appendix A.9).

Continued storage motivated tests of two further destinations: release back to droplets and direct removal from the lower wall.

<!-- Evidence: [selected film-development results, spatial metrics and reporting windows](../../../experiments/phase-07-2a-wall-liquid-routing/stage-03-shortened-reconstruction/early-ewf-startup/film-development/results.md), [500 ms campaign results](../../../experiments/phase-07-2a-wall-liquid-routing/stage-03-shortened-reconstruction/early-ewf-startup/inlet-speed-500ms/results.md), [selected reference-speed CSV](../../../../PyAnsys/output/phase72a-stage3-speed-sensitivity-server1/20261006/selected-film-history-reference.csv) and [Figure 16 provenance](../figures/results-film-development-reference500ms-provenance.json). -->

### 4.11. Added film-release mechanisms and direct drainage

A separate configuration enabled stripping, splashing, droplet collection and edge separation while keeping film-to-flow momentum feedback off. Its bulk fields and film forces differed from those of the 500 ms reference. After 4000 bulk updates, 50 ms of frozen-bulk development increased film mass from 0.2638 to 5.9070 kg. Over the final approximately 5 ms, the mean stripping and edge-separation rates were 64.56 and 51.87 kg/s, respectively, while the storage rate was 80.81 kg/s. A separate splash contribution remained unresolved.

Native film outflow was zero during that final averaging window. Extending the film domain onto the lower wall then allowed a matched direct-sink test (Figure 18). The Drain OFF and Drain ON cases started from identical fields and a total film mass of 9.7526 kg, with the same expanded film domain and all bulk equations frozen. Over 15 ms, the sink reduced the final lower-wall film mass by 70.32% relative to Drain OFF. Native outflow was also lower with the drain on, so the 0.5088 kg of direct removal increased combined external removal by only 0.1897 kg.

![Matched lower-wall film inventories and cumulative external removal with the direct drain off and on](../figures/results-direct-film-drain.png)

*Figure 18. Direct drainage reduces lower-wall film but partly replaces native outflow. Matched 15 ms OFF/ON test with all bulk equations frozen: (a) lower-wall film mass at the endpoint; (b) cumulative native outflow and direct removal.*

In the longer continuation, the lower film mass stayed near 0.056 kg while the upper film mass grew. The complete 405 ms record, including the rejected tail, contains 15.16 kg of direct removal and a 27.58 kg increase in film inventory. Film inventory was already increasing before the Courant-guard crossing. Local drainage therefore did not stop accumulation elsewhere. Particle release was internal transfer, while the sink removed liquid from the model (Appendix A.12).

The following numerical checks assess source application and film-step selection. The final mesh comparison addresses resolution separately.

<!-- Evidence: [release-mechanism continuation](../../../experiments/phase-07-2a-wall-liquid-routing/stage-04-ewf-wall-parameters/realism-continuation/feedback-off/results.md), [matched direct-drain test](../../../experiments/phase-07-2a-wall-liquid-routing/stage-04-ewf-wall-parameters/ewf-only-drain/results.md) and [long drain-ON development](../../../experiments/phase-07-2a-wall-liquid-routing/stage-04-ewf-wall-parameters/ewf-only-drain/long-development/results.md). -->

### 4.12. Numerical assessment of the selected development path

The shortened-startup contact source matched independently evaluated removal at all 3500 solved updates. A separate film-step test starting from identical fields showed that a 20 µs film step passed local field and ledger checks over 2.5 ms, whereas a 25 µs film step exceeded the 0.1% ledger-error limit.

These checks supported implementation and local step selection. Inner-film failures and unavailable residuals prevented a numerical convergence claim, while continued storage prevented a stationary-film claim (Appendix A.9.4).

<!-- Evidence: [combined-history residual checks](../../../experiments/phase-07-2a-wall-liquid-routing/stage-02-combined-ewf-roughness/case-history-N45606.md#ewf-residuals), [shortened-startup source audit](../../../experiments/phase-07-2a-wall-liquid-routing/stage-03-shortened-reconstruction/early-ewf-startup/results.md#film-evidence-and-numerical-limits), [matched-time film-step assessment](../../../experiments/phase-07-2a-wall-liquid-routing/stage-03-shortened-reconstruction/early-ewf-startup/film-development/results.md), [local screen criteria](../../../experiments/phase-07-2a-wall-liquid-routing/stage-03-shortened-reconstruction/early-ewf-startup/film-development/setup.md), [20 µs comparison JSON](../../../../PyAnsys/output/phase72a-stage3-film-development-server1/20261005/mid-film-sensitivity-20us.json) and [25 µs comparison JSON](../../../../PyAnsys/output/phase72a-stage3-film-development-server1/20261005/mid-film-sensitivity-25us.json). -->

### 4.13. Mesh sensitivity of film development and drainage

After introducing film formation, release and lower-wall removal, the next question was whether the predicted liquid paths persisted across mesh resolutions. Figure 7 shows why approximately 200 ms was chosen: the orange drainage curve was becoming flatter, although the positive purple accumulation rate showed that film mass was still rising. The expectation was that this interval would also provide a useful view of developing drainage on the finer meshes. The exact selected endpoint was 195 ms, before any bulk reactivation (Section 3.6). Comparing the selected states at 195 ms tested what each calculation predicted at the same film age, before any claim of equilibrium collection.

Figure 19 unfolds the cylindrical vessel wall into a flat map: height runs vertically and angle around the vessel runs horizontally. Each column is one mesh, with its starting state above and its 195 ms state below. The white opening locates the inlet. Purple denotes film near the bottom of the thickness scale, not necessarily a dry wall; green and yellow indicate thicker film. This view allows the reader to compare the extent and path of the film at the same age.

![Wall-film thickness at the selected starting states and at 195 ms for four mesh resolutions](../../../experiments/phase-09-mesh-convergence/figures/selected-film-thickness.png)

*Figure 19. At 195 ms, the 60k case has broad regions of appreciable film thickness; the finer cases retain more distinct paths and less extensive coverage, particularly above the inlet. All panels use the same 0–0.30 mm scale; larger thicknesses are saturated. White arrows show direction, not speed. The lower collector and inlet extension are excluded from these wall maps.*

In the lower row of Figure 19, the 60k film extended over much of the displayed wall at appreciable thickness. The 342k and 680k states had similar spatial patterns, with thinner upper-wall regions and more distinct film paths. The 997k state showed a less extensive region of appreciable thickness above the inlet. These maps establish a difference in film distribution at the same age; they do not measure propagation speed.

The spatial comparison raises two related questions: how much liquid remains in the film, and how much is being removed at the lower wall? Figure 20(c) shows the stored mass in kilograms; Figure 20(d) shows the instantaneous removal rate in kilograms per second. Panels (a–b) retain the bulk-flow context. Because the bulk was frozen, overlapping starting and final points in those panels are expected and are not evidence of a settled whole-separator flow.

![Saved-state bulk-liquid outflow, bulk inventory, film inventory and lower-wall film-drain rate across the Phase 9 meshes](../../../experiments/phase-09-mesh-convergence/figures/selected-mesh-response.png)

*Figure 20. Film storage and lower-wall drainage differ across the selected mesh states at 195 ms. Points are saved snapshots, not history means. Bulk fields were frozen during film development; the 342k starting reference precedes an additional bulk-active adjustment. The 2.6M reference has provisional settings and no 195 ms endpoint. Bulk outlet flow excludes internal sources; film-drain values are endpoint sink rates, not cumulative collection.*

Total film mass at 195 ms was 7.490 kg on the 60k mesh, compared with 2.821, 2.950 and 2.056 kg on the 342k, 680k and 997k meshes. Lower-wall film-drain rates decreased across this sequence from 22.716 to 7.168, 6.778 and 4.587 kg/s (Figure 20). Although the two intermediate film inventories differed by only 4.6% relative to 342k, the 997k state contained 30.3% less film and had a 32.3% lower drain rate than 680k. Intermediate agreement therefore did not persist on the finest completed mesh.

The lower-wall film inventories were 34.07, 10.75, 10.17 and 6.88 g, respectively. The removal law converts liquid present in the lower-wall region into a drain rate:

$$
\dot m_{\mathrm{drain}}=\frac{M_{\mathrm{film,lower}}}{\tau_f},\qquad \tau_f=1.5\times10^{-3}\ \mathrm{s}.
$$

For example, the 60k lower-wall inventory of 0.03407 kg gives approximately 22.72 kg/s. The small inventory and large rate are consistent with the short prescribed removal timescale; the rate is not the mass already collected. Lower drainage was therefore directly associated with less film in the removal region under the same drain law, rather than independently demonstrating reduced effectiveness of that law.

The common observation time did not produce equivalent film distributions. The maps are consistent with slower film propagation on the finer meshes, but lower supply or greater release could also reduce the visible coverage and inventory. Section 5.1 discusses these alternatives. Continuous selected-run inventory, flux and film-source histories were unavailable in the shared evidence, and saved bulk residuals were partly decimated. Unchanged bulk quantities during the frozen stage follow from the procedure and do not demonstrate convergence. These endpoints establish neither mesh independence nor stationary film storage, a complete liquid balance or total separator efficiency.

<!-- Evidence: [selected-state results and history availability](../../../experiments/phase-09-mesh-convergence/results.md#selected-starting-and-195-ms-states--17-october-2026), [endpoint CSV](../../../../PyAnsys/output/phase9-selected-results/20261017/endpoint-results.csv), [history audit](../../../../PyAnsys/output/phase9-selected-results/20261017/history-audit.json), [film-map provenance](../../../experiments/phase-09-mesh-convergence/figures/selected-film-thickness.provenance.json), and [endpoint-figure provenance](../../../experiments/phase-09-mesh-convergence/figures/selected-mesh-response.provenance.json). Percentages use unrounded endpoint values. The author supplied the observation-time rationale on 17 October 2026. -->
