# Model basis, development methods and results

## 3. Inherited model and operating basis

The project continued the Purnanto-based separator geometry, bulk-flow formulation and reference operating condition. These provide the starting basis for the work. Section 4 introduces the project’s mesh, inlet, collection and wall-treatment methods as each becomes relevant, followed by the findings and the question carried into the next investigation.

The development account retains the investigation order below. Later reconstructions are identified where they revisit earlier assumptions; they support the explanation without implying that every displayed comparison preceded the next method choice.

### 3.1. Computational domain and modelling scope

Building on the model limitations identified in the literature review, this study used the inherited separator geometry based on Purnanto et al. (2013).

The simplified domain retained the spiral inlet, cylindrical separation vessel and internal steam outlet pipe needed to study liquid transport through the active separation region (Figure 6). The inlet guided the incoming mixture into the vessel, while the internal pipe provided the steam exit. The lower brine pool and its discharge pipe were omitted, leaving a closed bottom wall.

![Saved computational domain and pure-phase inlet split](../figures/model-domain-overview.png)

*Figure 6. Simplified computational domain and inlet arrangement: (a) spiral inlet, vessel and internal steam outlet; (b) wall-side liquid strip and adjacent vapour inlet. The brine pool and discharge pipe are omitted. Panel (b) shows the split inlet introduced in Section 4.2; the collector is introduced in Section 4.3.*

The closed base supplied no physical liquid exit. Section 4 follows the inlet, mesh and collection changes used to investigate liquid transport in this domain.

### 3.2. Bulk-flow model and retained assumptions

The Mixture model provided a computationally economical continuation of Purnanto's separator model. Its algebraic-slip formulation was consistent with the small-Stokes-number argument used in that study: sufficiently small dispersed droplets respond rapidly relative to the characteristic flow timescale ([Purnanto et al., 2013](https://www.researchgate.net/publication/269519626_CFD_MODELLING_OF_TWO-PHASE_FLOW_INSIDE_GEOTHERMAL_STEAM-WATER_SEPARATORS)). Solving mixture momentum with algebraic slip requires fewer equations than a full Eulerian formulation, making repeated inlet and wall-treatment investigations more practical ([Ansys, Inc., 2025d](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_th/flu_th_sec_drift_oview.html)). VOF and alternative turbulence treatments were also explored, but these trials did not establish a suitable replacement. Mixture with RNG $k$–$\varepsilon$ was therefore retained as the simplest practical basis for continuing the investigation, without excluding other formulations.

<!-- Basis: [recorded baseline rationale](../../../experiments/phase-01-purnanto-baseline-and-inlet-exploration/purnanto-00-reference-spiral-boc/setup.md); [executed VOF trial](../../../experiments/phase-01-purnanto-baseline-and-inlet-exploration/purnanto-02b-vof-split-inlet-transient/setup.md); [turbulence screening](../../../experiments/phase-07-1a-absorber-convergence/turbulence-family/README.md). The small-Stokes-number rationale concerns dispersed liquid; it does not establish validity for concentrated wall liquid. -->

A pressure-based solver with the Mixture model in Ansys Fluent 2025 R2 was used for bulk continuity, momentum, liquid fraction and algebraic slip. Steam was the primary phase and water the secondary phase. The RNG $k$–$\varepsilon$ model included swirl treatment and standard wall functions; gravity acted downwards. The energy equation was disabled; flashing, condensation and temperature-dependent properties were excluded. Table 1 gives the material values; Appendix A.1 records the controls ([Ansys, Inc., 2025d](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_th/flu_th_sec_multiphase_mixture.html)).

*Table 1. Fixed material properties verified for the throughput-controlled absorber model.*

| Phase | Density (kg/m³) | Dynamic viscosity (Pa·s) |
| --- | ---: | ---: |
| Vapour | 5.79743 | $1.52062\times10^{-5}$ |
| Liquid water | 881.211 | $1.45544\times10^{-4}$ |

The full-feed parent, combined contact endpoint and shortened-startup endpoint used Manninen slip, Schiller–Naumann drag and a liquid-phase diameter of 10 µm. This local-equilibrium slip model was held fixed during wall comparisons; its accuracy for concentrated wall liquid remained unverified. The liquid-phase diameter controls continuum slip, separately from DPM droplets and film (Appendix A.1).

### 3.3. Reference feed and boundary conditions

The reference feed condition was retained from Purnanto to provide a common operating basis for the model-development comparisons: 197.61 kg/s at 1600 kJ/kg and 11.2 bar absolute. At this pressure, saturated liquid and vapour enthalpies, $h_f$ and $h_g$, gave the vapour mass fraction as $x=(h-h_f)/(h_g-h_f)=0.408323$. The steam and liquid feeds followed from $x\dot m_{\mathrm{tot}}$ and $(1-x)\dot m_{\mathrm{tot}}$, linking the phase loading to the reference thermodynamic condition. The inlet commands retained Purnanto's rounded phase mass flows of 116.92 kg/s liquid and 80.69 kg/s vapour; Appendix A.7 gives the calculation ([Purnanto et al., 2013](https://www.researchgate.net/publication/269519626_CFD_MODELLING_OF_TWO-PHASE_FLOW_INSIDE_GEOTHERMAL_STEAM-WATER_SEPARATORS)). Enthalpy defined the supplied composition; flashing was not solved within the domain.

The boundary setup retained the Purnanto-based model’s prescribed-feed and pressure-outlet approach. The steam outlet supplied the pressure boundary condition, allowing inlet pressure to emerge from the solution. The operating pressure was 0 Pa, so outlet gauge and absolute pressures were equal. Stationary, no-slip walls confined the flow. The project’s revised inlet distribution and numerical collection treatments are introduced in Sections 4.2–4.4. Appendices A.6 and A.2 give the turbulence and backflow inputs and the reconstruction differences.

## 4. Model development and results

The investigation first examined liquid delivery and retention, then developed a collection route and a startup procedure for wall-treatment comparisons. Film development subsequently exposed the distinction between wall capture, storage, release and external removal. Each method is introduced with the problem it addressed and the evidence obtained from it. Section 4.14 describes the workflow that supported these repeated investigations.

Each comparison uses its stated mesh and settings. Outlet liquid flow is reported as positive outwards unless a signed value is given. Steady-solver iterations track numerical development; accepted film time tracks the transient film calculation. Detailed settings and supporting trials remain in the appendices.

### 4.1. Mesh development and the wall-liquid field

Poly-hexcore meshing was selected to combine wall-following layers along the expected liquid path with an economical hexahedral core and polyhedral transition cells. Ansys describes this arrangement as a way to retain boundary-layer structure while controlling cell count and computational cost ([Ansys, Inc., 2020](https://www.ansys.com/content/dam/resource-center/white-paper/ansys-fluent-mosaic-technology-wp.pdf)). Manageable mesh sizes supported repeated model-development experiments before examining resolution sensitivity. This was a practical selection rationale, rather than proof of greater accuracy than tetrahedral meshing. Numerical diffusion still depended on resolution, discretisation and local flow alignment, which could not be assumed throughout the swirling flow ([Ansys, Inc., 2025c](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/flu_ug_GridTypes.html)).

<!-- Development rationale: [17 August discussion of wall layers and coarse-mesh experimentation](../../../meetings/otter/2026-08-17-fluid-dynamics-modeling-meeting.md). That discussion concerns earlier full-geometry work, not a measured speed or accuracy comparison for the final simplified mesh. -->

The main mesh contained 60,964 cells. Appendix A.6 gives the spatial schemes, and Appendix A.10 gives the connectivity and wall fields. The mean main-wall $y^+$ ranged from approximately $2.0\times10^4$ to $3.4\times10^4$ across three saved states, so the wall-following topology did not establish fine wall resolution. Layer dimensions and solver mesh-quality measures remain unverified. The developing mesh comparisons are presented below and in Sections 4.2–4.3; Section 4.13 returns to resolution after introducing film and collection.

The historical tetrahedral comparison changed the mesh, inlet and preparation. The SIMPLE/Coupled reconstruction comparisons also changed pseudo-time and the $k$ scheme, so neither these comparisons nor the historical tetrahedral comparison isolated a single cause.

The polyhedral–hexahedral mesh had larger interior cells, polyhedral transitions and thin layers along the wall (Figure 7). The mesh workflow provided control near the expected liquid path, although the wall-resolution limits above remained.

At iteration 10,000, the historical tetrahedral case showed a thin region of liquid enrichment near the wall. The 60,964-cell SIMPLE reconstruction showed a broader region with a higher liquid fraction. However, inlet representation and preparation also differed, and the coarse SIMPLE state had a large mass-balance error. These differences do not establish a mesh effect: reduced numerical diffusion remains a possible explanation, not a measured gain in accuracy.

![Native mesh sections and liquid-fraction fields for the historical tetrahedral case and polyhedral–hexahedral reconstruction](../figures/results-mesh-spatial-comparison.png)

*Figure 7. Mesh sections (a–b) and bulk-liquid volume-fraction fields at iteration 10,000 (c–d). The reconstructed case shows broader wall enrichment; the mesh, inlet and preparation differ between cases, so the comparison does not isolate a mesh effect.*

These reconstructions showed that the predicted wall-liquid field depended on the numerical and inlet package, but they did not isolate the cause. The matched inlet comparison below examined phase placement while holding the mesh and numerical controls fixed.

<!-- Evidence: [native mesh and liquid-field comparison, source pairs and export manifests](../../../Poster/poster-sections/mesh-and-volume-fraction-comparison.md); solved 60k topology and wall-resolution evidence in Appendix A.10. The separate 342k mesh illustration used elsewhere is not substituted for the 60k contour's mesh here. -->

### 4.2. Two-phase inlet and wall-side liquid placement

The inlet split represented the expected concentration of liquid towards the outer wall as the upstream flow turned into the separator. Liquid entered through the wall-side strip and steam through the remaining area, allowing the phases to mix within the domain. This placement provided a defined liquid supply for studying wall-film formation and drainage. The pure-phase inlets simplified this expected distribution; complete phase separation at entry was assumed, not measured.

The strip area was sized from the phase volumetric flows under an assumed common inlet velocity, rather than from the mass fractions alone. About 0.933% of the 0.724 m square inlet area was assigned to a 6.754 mm liquid strip. Appendix A.7 distinguishes the design properties from the solved densities and resulting phase velocities.

<!-- Rationale: [22 April spiral-inlet discussion, 03:41–04:39](../../../meetings/otter/2026-04-22-wk-6-spiral-inlet-design-meeting.md); [11 March initial two-phase inlet proposal, 02:08](../../../meetings/otter/2026-03-11-two-phase-fluid-modeling-meeting.md). Meeting records establish design intent, not measured inlet phase distributions. -->

Separate phase mass-flow inlets implemented the revised distribution while retaining the reference loading; liquid and vapour entered normal to their respective faces. The absorber-free mixed/split Coupled reconstructions held the mesh, feed and controls fixed, used fresh initialisation and ran for 10,000 updates.

Both cases used the same 60,964-cell mesh, total phase feed, Coupled settings, initialisation and 10,000-update horizon. Mixed feed supplied both phases across both inlet faces; split feed supplied liquid through the wall-side strip. Complete phase segregation was an assumed profile, as defined above.

Split feed produced a more continuous liquid-rich wall band and deeper lower-region enrichment than mixed feed (Figure 8). At a nominal speed of 26.81 m/s, the bulk-liquid inventory at iteration 10,000 was 1262.6 kg with mixed feed and 1734.5 kg with split feed, a difference of 471.9 kg, or 37.4%. Split feed had a larger bulk-liquid inventory at all five tested speeds in the range 20.11–32.14 m/s.

Over iterations 9500–10,000, the outward liquid flow through the steam outlet averaged 99.671% of the 116.9387 kg/s liquid feed for mixed feed and 99.404% for split feed. The inventory difference therefore accompanied almost complete liquid discharge through the steam outlet, rather than discharge through a separate collection route.

![Bulk-liquid fraction at inlet height and through the vessel height with mixed and wall-side split feed](../figures/results-inlet-spatial-comparison.png)

*Figure 8. Bulk-liquid volume fraction with mixed and wall-side split feed at inlet height (a, b) and through the vessel centre (c, d). Matched sections at iteration 10,000 use a shared 0–1 scale; neither case includes a collector or EWF.*

Wall-side liquid placement increased the retained inventory, but neither configuration supplied a separate collection route. The finer-mesh checkpoints below examine the related problem of liquid retention in a domain with a closed base.

<!-- Evidence: [matched inlet setup and numerical basis](../../../experiments/phase-08-storyline-reconstruction/stage-01-60k-storyline/baseline-lineage-audit.md), [mixed-feed results](../../../experiments/phase-08-storyline-reconstruction/stage-01-60k-storyline/f1-one-inlet/results.md), [split-feed inventory and spatial findings](../../../experiments/phase-08-storyline-reconstruction/stage-01-60k-storyline/f2-split-inlet/results.md), and [native inlet-plane exports](../../../Poster/poster-sections/mesh-and-volume-fraction-comparison.md). Percentage inventory change is calculated from the rounded published endpoint values. -->

### 4.3. Liquid accumulation and the need for collection

Finer absorber-free SIMPLE diagnostics compared 342,609-, 679,970- and 997,604-cell fields at iteration 3000. These developing solutions did not constitute a converged mesh study (Appendix A.2).

Saved fields from the three finer split-inlet SIMPLE cases showed liquid near the wall and base. Their inventory and outlet histories show accumulation with little discharge through the steam outlet relative to the liquid feed (Figure 9). At iteration 3000, the liquid inventories in the 342,609- and 679,970-cell cases were each about 454–455 kg, whereas the 997,604-cell case held 333.142 kg. The latter case discharged only 0.003623 kg/s through the steam outlet and held 69.16% of its liquid below $y=1$ m. These developing checkpoints do not constitute a mesh-convergence result; Appendix A.17 retains their exact values.

![Liquid inventory and outlet flow across the three finer absorber-free meshes](../../../experiments/phase-08-storyline-reconstruction/stage-02-fine-mesh-simple/direct-student-342k/n3000/figures/matched-mesh-checkpoints.png)

*Figure 9. Liquid inventory (left) and net outlet liquid flow (right) in the finer absorber-free SIMPLE cases. Liquid accumulates while outlet flow remains small relative to the liquid feed. Lines connect saved checkpoints; solver iterations are not physical time.*

On the 679,970-cell mesh, liquid inventory reached 764.744 kg at iteration 4000, with 69.62% below $y=2$ m. Outlet liquid flow was 8.00 kg/s, or 6.84% of the feed. The next continuation failed after printed iteration 4211; its cause was not isolated.

The inlet and mesh studies changed delivery and retention but provided no separate collection route. Earlier trials included the lower geometry to represent the brine pool and discharge directly. However, the tested outlet conditions and pool-control treatments did not establish a sufficiently stable and mass-balanced operating state (Appendix A.13). The investigation therefore returned to the simplified domain so that liquid transport and collection could be studied without also resolving pool behaviour and discharge control. This decision limited the model's scope; it did not establish that full-geometry modelling was infeasible.

The absorber and closed bottom wall together represented the two functions of the omitted brine pool needed for this study. The absorber captured liquid reaching the lower region, representing its transfer into the pool. For the steam, the bottom wall acted as an idealised stationary pool surface: it prevented downward passage and diverted the flow within the vessel towards the steam outlet. This was the basis for selecting the simplified model for liquid-transport and collection studies: it retained liquid capture and steam diversion without resolving pool motion, level control or discharge. The rigid, no-slip surface remained an approximation to the real steam–brine interface.

<!-- Modelling rationale: [Phase 7A interpretation](../../../experiments/phase-07a-simplified-purnanto-liquid-removal/interpretation.md). -->

The first simplified collection studies used a throughput-controlled liquid sink. Its loading and source account are examined in Sections 4.4–4.5; Section 4.8 introduces the later contact-dependent law. The later absorber-free reconstructions revisit the collection problem and provide supporting evidence for this development sequence.

<!-- Evidence: [matched finer-mesh checkpoints](../../../experiments/phase-08-storyline-reconstruction/stage-02-fine-mesh-simple/direct-student-342k/n3000/results.md), [997k spatial result](../../../experiments/phase-08-storyline-reconstruction/stage-02-fine-mesh-simple/direct-student-997k/n3000/results.md), [680k accumulation and failed continuation](../../../experiments/phase-08-storyline-reconstruction/stage-02-fine-mesh-simple/direct-student-680k/n4000/results.md), [mixed-inlet Coupled account](../../../experiments/phase-08-storyline-reconstruction/stage-01-60k-storyline/f1-one-inlet/results.md) and [full-geometry scope decision](../../../experiments/phase-06-full-geometry-with-brine-pool/conclusion.md). -->

### 4.4. Reduced-feed development and inlet ramp

The simplified collection model was developed first at reduced feed, before increasing the inlet loading to the reference condition. Table 2 gives the full and reduced commands used for these startup and wall studies.

*Table 2. Main boundary conditions. Reduced feed was 25% of full feed, with the phase mass ratio retained.*

| Boundary | Condition | Full feed | Reduced feed |
| --- | --- | ---: | ---: |
| Liquid inlet | Liquid mass-flow inlet | 116.9200 kg/s | 29.2300 kg/s |
| Vapour inlet | Vapour mass-flow inlet | 80.6900 kg/s | 20.1725 kg/s |
| Steam outlet | Gauge pressure | 1.120 MPa | Same |
| Vessel and bottom | Stationary, no-slip walls | Selected roughness/film treatment | As defined for startup |

Inlet loading was increased gradually so that each loading stage could start from an already developed field. This was consistent with Fluent guidance that gradual increases in inlet swirl or rotational speed can improve solution stability in swirling flows ([Ansys, Inc., 2025l](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/flu_ug_uns_sec_models_swirl.html)). Staged loading was used as a practical solution strategy; its independent contribution was not isolated from the other numerical changes.

The original startup used Hybrid Initialisation, smooth walls, EWF disabled and throughput-controlled collection. The corrected ramp was followed by Coupled pressure–velocity solution with Global Time Step pseudo-time. The saved full-feed field, termed the **developed parent**, supplied common starting conditions for wall comparisons, although its residuals and liquid balance did not establish convergence. Appendix A.5 retains the iteration history.

The startup and wall studies used the 60,964-cell split-inlet model, with a full feed of 116.92 kg/s liquid and 80.69 kg/s steam.

At 25% feed with throughput collection, bulk-liquid inventory fell only 0.30% over iterations 1080–1580, ending at 31.3571 kg (Figure 10). The minimum scaled continuity residual was $3.2056\times10^{-4}$.

A failed ramp command had left the model at reduced feed until iteration 1580. The corrected 2000-update ramp reached full feed at iteration 3580. During the ramp, the scaled continuity residual peaked at $1.1166\times10^{-2}$ and bulk-liquid inventory reached 182.5178 kg.

![Residuals, bulk-liquid inventory and actual inlet loading during early development](../figures/results-described-early-development.png)

*Figure 10. Reduced-feed hold, loading ramp and full-feed development. The panels show scaled residuals, bulk-liquid inventory and the liquid-feed command against solver iteration. Dashed markers indicate A: ramp start; B: full feed and Coupled activation; C: EWF activation.*

The ramp reached the intended loading, but this alone did not establish a suitable reference state. The full-feed control below assessed the inventory, outlet flow and removal account before using the field for wall comparisons.

<!-- Evidence: [selected case history](../../../experiments/phase-07-2a-wall-liquid-routing/stage-02-combined-ewf-roughness/case-history-N45606.md), [carrier residuals](../../../../PyAnsys/output/phase72a-lineage-N45606/20261005/carrier-residuals.csv) and [liquid histories](../../../../PyAnsys/output/phase72a-lineage-N45606/20261005/selected-lineage-histories.csv). -->

### 4.5. Full-feed control and mass balance

Before using the full-feed field for comparisons, its liquid account was assessed alongside the residual and inventory histories.

Liquid collection could not be judged from outlet carryover alone: a lower outlet flow could accompany external collection, continued storage or depletion of previously stored liquid. Outlet flows were therefore assessed alongside bulk and film inventories, collection rates and mass balances. Residuals supplied a separate check on numerical behaviour; a fixed iteration horizon did not establish convergence. Each reported value retained its case, active equations and reporting window, with endpoints and means treated separately. Appendix A.9 defines the numerical criteria and integration methods.

Fluent fluxes used a positive sign for flow into the domain. With EWF disabled and no other liquid transfer, the signed remainder (kg/s) was

$$
R_L=\sum_b\dot m_{L,b}+\dot m_{L,\mathrm{source,applied}}.
$$

The liquid source retained its negative sign for removal. The evaluated and applied removal represented the same sink, so the balance included only one removal term. Bulk-to-film accretion cancelled only in compatible combined accounts. Native mixture and phase-summed reports were assessed separately.

The bulk-liquid outlet ratio used liquid feed as its denominator, whereas outlet dryness used total outlet flow (Section 2.2). Neither pathlines nor diagnostic-droplet fates replaced bulk-liquid fluxes. Residual scaling was checked for startup comparisons; residuals were not percentage mass imbalances ([NASA, 2021a](https://www.grc.nasa.gov/www/wind/valid/tutorial/iterconv.html)).

The smooth-wall, EWF-off Coupled continuation became the iteration-5586 comparison parent. The continuity residual fell and inventory approached 296 kg, but residual oscillations, outlet reverse flow and turbulent-viscosity limiting persisted.

The applied throughput-controlled absorber removal matched its 116.92 kg/s command, but an additional 24.3344 kg/s left through the steam outlet. The signed liquid boundary-plus-source remainder was therefore −24.3344 kg/s, or −20.81% of the feed. Source application was verified; conservation remained unresolved (Appendix A.15.2).

This developing field supplied a common parent for the following wall comparisons. Changes in outlet flow must be interpreted alongside inventory and removal because the parent did not establish a closed liquid account.

<!-- Evidence: [full-feed control continuation](../../../experiments/phase-07-1a-absorber-convergence/roughness-family/r0-smooth-control/results.md), [baseline handoff](../../../experiments/phase-07-2a-wall-liquid-routing/baseline-control-handoff.md), [aligned native full-feed control histories](../../../../PyAnsys/output/phase71a_r0_control_run4/report-histories-batched.json) and [full-feed control accounting audit](../../../experiments/phase-07b-full-geometry-liquid-removal/convergence-investigation/shuhei-audit.md). -->

### 4.6. Roughness response from the common parent

Early contours showed liquid travelling along the wall and spiralling towards the steam outlet rather than draining towards collection. The substantial predicted liquid carryover was inconsistent with the small carryover expected from effective separator operation. This discrepancy motivated investigation of liquid behaviour after liquid reached the wall. Roughness tested whether increased near-wall momentum loss changed the liquid route, while EWF represented deposited liquid as a film with its own storage, transport and drainage. The initial roughness comparisons kept EWF disabled, and the initial film comparison used smooth walls, separating the two treatments before combined cases were examined.

Wall roughness was included in the wall-friction treatment through the equivalent sand-grain height $k_s$ and roughness constant $C_s$ ([Ansys, Inc., 2025k](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_th/x1-5720008.164.html)). The tested values were sensitivity inputs, not measured surface properties. The wall treatment and unresolved settings are documented in Appendix A.10.

The comparisons were designed to distinguish changes in liquid routing from differences caused by model preparation. Wall-treatment screens therefore started from a common saved field and used equal update horizons and reporting windows. Because the parent was still developing, these comparisons assessed responses to the treatments rather than equilibrium performance. Exploratory inlet, droplet and film tests informed the selected comparisons (Appendix A.13).

Roughness ranged from 0 to 8 mm; Appendix A.5 gives the $C_s$ variations and reporting windows. Wall-screen comparisons used arithmetic means over the final 500 bulk updates.

<!-- Motivation: [early outlet-flow record](../../../experiments/phase-07-1a-absorber-convergence/v2-inlet-loading-ramp/results.md); [roughness hypothesis](../../../experiments/phase-07-1a-absorber-convergence/roughness-family/index.md); [film hypothesis](../../../experiments/phase-07-1a-absorber-convergence/ewf-family/index.md); [5 October wall-liquid discussion](../../../meetings/otter/2026-10-05-separator-liquid-film-and-roughness-analysis.md). -->

The mean bulk-liquid outlet flow varied non-monotonically with roughness height (Figure 11). At $C_s=0.5$, a roughness height of 0.05 mm raised the mean outlet flow by 21.21% relative to the smooth-wall reference, whereas a height of 8 mm reduced it by 44.09%, from 24.3715 to 13.6253 kg/s. Increasing $C_s$ lowered the flow at both fixed roughness heights.

![Effect of roughness height and constant on bulk-liquid steam-outlet flow](../figures/results-described-roughness.png)

*Figure 11. Mean bulk-liquid outlet flow as a function of (a) roughness height and (b) roughness constant at fixed heights. The height response is non-monotonic; the 8 mm case also loses bulk inventory. EWF is off. Means are calculated over iterations 8087–8586; dashed lines mark the smooth-wall reference.*

The 8 mm case lost 187.109 kg of bulk liquid. Oscillations and incomplete balances prevented an efficiency claim. The later 0.045 mm continuation also changed bulk advancement and film stepping, so it did not isolate the effect of roughness (Appendix A.12).

<!-- Evidence for the material-reference continuation: [Commercial-steel results](../../../experiments/phase-07-2a-wall-liquid-routing/stage-04-ewf-wall-parameters/commercial-steel/results.md). The 0.045 mm value is a selected reference, not a measured separator finish or a matched roughness-only comparison. -->

<!-- Evidence: [roughness-screen results and sample standard deviations](../../../experiments/phase-07-2a-wall-liquid-routing/roughness-family/results.md#matched-tail-comparison) and [comparison figure and provenance](../../../observations/07-wall-liquid-interaction.md). The source's later statement identifying the lowest outlet conflicts with its table; the table values are used here. -->

The roughness response showed that lower outlet liquid flow could accompany inventory loss. It could not establish successful collection. A separate smooth-wall branch tested an explicit film representation from the same parent, allowing film storage and drainage to be examined. This was an alternative wall-treatment comparison, rather than a continuation of the roughest case.

### 4.7. Accretion-enabled wall-film response

The separate smooth-wall comparison introduced the Eulerian Wall Film (EWF) model. It solved surface mass and momentum equations, with accretion transferring bulk liquid into the film ([Ansys, Inc., 2025e](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/flu_ug_ewf_sec_options.html)). This added explicit film storage and transport to the bulk-liquid calculation.

With common smooth-wall starting fields and throughput collection, the EWF package reduced mean outlet liquid flow by 92.88%, from 24.369 kg/s in the film-disabled continuation to 1.735 kg/s in the accretion-enabled case over iterations 8087–8586 (Figure 12). Phase accretion and the coupled film equations were enabled; momentum feedback was disabled. Earlier trials are documented in Appendix A.11.

![Bulk-liquid steam-outlet histories with EWF off and the accretion-enabled package](../figures/results-described-film-outlet.png)

*Figure 12. The accretion-enabled EWF package reduces bulk-liquid outlet flow; changing inventories prevent a collection claim. The smooth-wall cases share the full-feed parent. Shading marks the final 500 iterations; the film step is 10 µs.*

During the accretion-enabled continuation, bulk mass fell from 295.8536 to 63.0234 kg, while film mass reached only 3.1112 kg. The centre sections show less bulk liquid beside the wall in the accretion-enabled case (Figure 13). The film package changed the liquid distribution, but changing inventories and incomplete combined liquid accounting prevent an efficiency claim.

![Matched bulk-liquid volume-fraction sections for the film-disabled continuation and accretion-enabled film case](../figures/bulk-comparison-described-film-treatment.png)

*Figure 13. Less bulk liquid remains beside the wall in the accretion-enabled film case (right) than in the film-disabled continuation (left). Both centre sections are shown at iteration 8586 on a shared 0–1 liquid-volume-fraction scale. Film storage and drainage are assessed separately.*

<!-- Evidence: [film-disabled and accretion-enabled comparison](../../../observations/07-wall-liquid-interaction.md), [wall-film-screen results and native sections](../../../experiments/phase-07-2a-wall-liquid-routing/ewf-family/results.md#native-phase-2-volume-fraction-contours--2026-09-23), [paired contour provenance](../figures/bulk-comparison-described-film-treatment.provenance.json) and [selected endpoint histories](../../../../PyAnsys/output/phase72a-lineage-N45606/20261005/selected-lineage-histories.csv). The film-disabled continuation's mean is from its separate comparison run and is not substituted for the roughness screen's smooth-wall mean. -->

The film comparison exposed the need to distinguish reduced bulk carryover from external collection. The following tests combined contact-based collection with wall treatment, then examined whether the model could be started more directly and developed long enough to assess film drainage and storage.

### 4.8. Contact collection and combined model development

The throughput-controlled collector used in the initial wall screens did not make removal depend solely on liquid reaching the collection region. Contact collection supplied that local dependence through the removal law below. The next comparisons examined its strength and its use with roughness and film treatment.

To make collection depend on liquid actually reaching the lower region, the contact absorber removed bulk liquid in response to the local inventory, without an inlet-throughput cap or a direct vapour mass sink:

$$
S_L=-\frac{\rho_L\alpha_L}{\tau},\qquad \tau=10^{-5}\ \mathrm{s}.
$$

Here, $\rho_L$, $\alpha_L$ and $\tau$ denote liquid density, liquid volume fraction and depletion time, respectively; $S_L$ has units of kg/(m³·s). The associated momentum and turbulence sources represented one-way capture. Appendices A.3–A.5 describe the implementation, source checks, depletion-time sensitivity and earlier throughput-controlled law ([Ansys, Inc., 2025a](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/flu_ug_bcs_sec_cell_zones.html)).

A shorter depletion time reduced collector inventory but increased removal variability (Appendix A.4). The combined continuation used contact collection with a 10 µs depletion time, 0.5 mm roughness and a 1 µs film step simultaneously; the effects of these settings were not isolated.

At iteration 45606, film mass was 6.3600 kg after 120.769 ms. Over the final 1000 updates, drainage remained 9.98% below accretion, so liquid continued to accumulate in the film during this interval. Appendix A.15.3 and the linked case history retain the endpoints and detailed film account.

The shortened-startup comparison below tests whether introducing these treatments before loading reduces the ramp disturbance.

<!-- Evidence: [contact-strength screens](../../../experiments/phase-07-2a-wall-liquid-routing/stage-02-combined-ewf-roughness/results.md#all-liquid-contact-absorber-trial), [complete selected case history](../../../experiments/phase-07-2a-wall-liquid-routing/stage-02-combined-ewf-roughness/case-history-N45606.md) and [corrected film ledger](../../../../PyAnsys/output/phase72a-lineage-N45606/20261005/corrected-film-development-summary.json). The short strength-screen branch is distinct from the original-field continuation retained in Appendix A.9. -->

### 4.9. Shortened startup with early wall-film activation

The startup study asked a different question: whether the combined model could reach full feed with smaller loading disturbances. Matching ramp progress aligned inlet loading, while the activation hold provided a separate window to assess the disturbance from introducing the additional models. Several settings changed together, so this comparison tested the combined procedure rather than isolating each contribution (Appendix A.16).

The shortened procedure reused the reduced-feed field without reinitialisation and activated contact collection, roughness, Coupled flow and a dry-initialised film before increasing the feed (Appendix A.16).

The shortened startup introduced the combined wall and collection treatment before loading. Relative to the historical inlet ramp, the peak continuity residual fell by 70.15%, peak bulk + film inventory by 70.43%, and peak outward outlet liquid flow by 75.78% (Figure 14). Appendix A.17 lists the peak values.

![Historical and shortened startup at matched inlet-ramp progress](../figures/results-described-startup.png)

*Figure 14. Shortened startup had lower ramp peaks than historical startup. (a) Continuity residual; (b) bulk + film inventory; (c) signed outlet liquid flow, with negative values indicating outward flow. The larger activation disturbance is excluded; the dashed line marks full feed, and shading indicates the subsequent hold.*

The excluded activation hold had a continuity residual peak of 0.10593, exceeding the historical ramp peak. At iteration 5080, bulk and film masses were 61.0549 and 0.1645 kg, respectively. Almost all film input was still stored (Appendix A.15.4). All ramp updates met the recorded inner-film tolerance, but 15 of the final 100 hold updates failed to meet it. The startup procedure reduced loading peaks without establishing complete startup convergence (Appendix A.9.4).

The film was still young at full feed. The following continuation held the bulk fields fixed to examine its development under unchanged forcing.

<!-- Evidence: [shortened-startup results](../../../experiments/phase-07-2a-wall-liquid-routing/stage-03-shortened-reconstruction/early-ewf-startup/results.md), [audited metrics, native source checks and normalisation](../../../../PyAnsys/output/phase72a-stage3-early-ewf-server1/20261005/analysis-summary.json) and [native final histories for Appendix A.15.4](../../../../PyAnsys/output/phase72a-stage3-early-ewf-server1/20261005/final-histories.json). -->

### 4.10. Film development under frozen bulk fields

The longer film-development calculation retained gravity, gas shear, wall viscosity and momentum advection in the film momentum equation. Native film-edge outflow provided the drainage route; additional film forces and droplet interactions were disabled (Appendix A.9).

Bulk freezing initially tested whether changing bulk forcing caused film-solver disturbances. It subsequently allowed film development to be examined under fixed forcing, with bulk flow, turbulence, volume fraction and relative motion held constant. This did not establish bulk convergence or prove that freezing stabilised the film. Film development was assessed in physical film time, separately from steady bulk iterations. Fluent's frozen-carrier EWF procedure assumes a converged bulk field; that condition remained unestablished here ([Ansys, Inc., 2025g](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_th/flu_th_ewf_sec_sol_alg.html); [2025j](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/flu_ug_sec_multiphase_solution.html)).

Film balances used accepted physical film time because steady bulk iterations did not represent elapsed filling time. The early film balance compared integrated accretion with the sum of drainage and inventory change over this interval; Appendix A.9 defines the integration and normalised error. Later release mechanisms required separate transfer terms (Appendix A.12). When the bulk was frozen, reciprocal bulk depletion did not advance, so agreement within the film account could not establish conservation across the bulk and film.

The 500 ms film run used overlap-weighted rates over the final 10 ms, so only the part of each sampled interval inside that window contributed to the reported rate.

Film mass increased from 0.1645 kg at 3.5 ms to 9.5444 kg at 500 ms (Figure 15). After iteration 5080, the bulk equations were frozen, holding the bulk inventory at 61.0549 kg and the outward bulk-liquid outlet flow at 3.4300 kg/s. These fixed values describe the held forcing; reciprocal bulk depletion was not calculated.

![Film inventory, accretion and drainage against accepted film time through 500 ms](../figures/results-film-development-reference500ms.png)

*Figure 15. Drainage develops while film inventory keeps rising under frozen bulk forcing. (a) Film mass; (b) film input and drainage. Shading marks the final 10 ms; markers in (a) locate the Figure 16 snapshots and the endpoint.*

The film spread and thickened over the lower and middle wall (Figure 16). Between 75.66 and 265.18 ms, the proportion of wall area with a film thickness of at least 0.10 mm increased from 40.34% to 61.98%; the maximum thickness rose from 0.253 to 0.291 mm.

![Native wall-film thickness at three saved film times](../figures/wall-film-described-development.png)

*Figure 16. Wall-film thickness at three saved times with bulk fields frozen. Film times and masses are labelled; all three views use the same camera and a 0–0.30 mm colour scale.*

Over the final 10 ms ending at 500 ms, mean accretion was 81.121 kg/s and drainage was 69.600 kg/s, a 14.20% drainage deficit. The film storage rate, calculated from mass change divided by elapsed accepted film time over this window, was 11.528 kg/s. The film mass curve therefore continued to rise late in the run despite increasing drainage. Rates use interval-overlap weighting; Appendix A.17 retains the earlier 265.184 ms result and its different 1000-update window. Only the reference-speed arm reached the 500 ms endpoint (Appendix A.9).

Continued storage motivated tests of two further destinations: release back to droplets and direct removal from the lower wall.

<!-- Evidence: [selected film-development results, spatial metrics and reporting windows](../../../experiments/phase-07-2a-wall-liquid-routing/stage-03-shortened-reconstruction/early-ewf-startup/film-development/results.md), [500 ms campaign results](../../../experiments/phase-07-2a-wall-liquid-routing/stage-03-shortened-reconstruction/early-ewf-startup/inlet-speed-500ms/results.md), [selected reference-speed CSV](../../../../PyAnsys/output/phase72a-stage3-speed-sensitivity-server1/20261006/selected-film-history-reference.csv) and [Figure 15 provenance](../figures/results-film-development-reference500ms-provenance.json). -->

### 4.11. Added film-release mechanisms and direct drainage

Later tests added pressure-gradient, spreading and surface-tension forces, droplet collection, splashing, stripping and edge separation. Particle impacts can cause splashing, while stripping and edge separation release film liquid as droplets. Changes in the bulk fields in these tests prevent the effects from being attributed to any single mechanism. Film-to-bulk momentum feedback was disabled in the selected continuations; this setting was distinct from numerical coupling of the film equations (Appendix A.12) ([Ansys, Inc., 2025b](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_th/flu_th_ewf_sec_film_submodels.html)).

A separate configuration enabled stripping, splashing, droplet collection and edge separation while keeping film-to-flow momentum feedback off. Its bulk fields and film forces differed from those of the 500 ms reference. After 4000 bulk updates, 50 ms of frozen-bulk development increased film mass from 0.2638 to 5.9070 kg. Over the final approximately 5 ms, the mean stripping and edge-separation rates were 64.56 and 51.87 kg/s, respectively, while the storage rate was 80.81 kg/s. A separate splash contribution remained unresolved.

Native film outflow was zero during that final averaging window. The film domain was therefore extended onto the lower wall to test direct removal of liquid reaching that region.

For wall-film liquid, the same collection concept was implemented through a separate mass sink on the lower wall. It removed local film mass and the corresponding momentum at the film velocity, using an assumed capture time of 1.5 ms. Removal depended on the liquid already in the film, independently of inlet throughput and bulk-liquid inventory, and was accounted for separately from native film-edge outflow (Appendix A.12).

A matched direct-sink test compared Drain OFF and Drain ON (Figure 17). Both cases started from identical fields and a total film mass of 9.7526 kg, with the same expanded film domain and all bulk equations frozen. Over 15 ms, the sink reduced the final lower-wall film mass by 70.32% relative to Drain OFF. Native outflow was also lower with the drain on, so the 0.5088 kg of direct removal increased combined external removal by only 0.1897 kg.

![Matched lower-wall film inventories and cumulative external removal with the direct drain off and on](../figures/results-direct-film-drain.png)

*Figure 17. Direct drainage reduces lower-wall film but partly replaces native outflow. Matched 15 ms OFF/ON test with all bulk equations frozen: (a) lower-wall film mass at the endpoint; (b) cumulative native outflow and direct removal.*

In the longer continuation, the lower film mass stayed near 0.056 kg while the upper film mass grew. The complete 405 ms record, including the rejected tail, contains 15.16 kg of direct removal and a 27.58 kg increase in film inventory. Film inventory was already increasing before the Courant-guard crossing. Local drainage therefore did not stop accumulation elsewhere. Particle release was internal transfer, while the sink removed liquid from the model (Appendix A.12).

Local lower-wall removal did not prevent upper-film accumulation. Before comparing resolutions, the numerical assessment below distinguishes verified source application and local film-step checks from unresolved convergence. The final mesh comparison then examines whether the predicted storage and drainage persist across resolutions.

<!-- Evidence: [release-mechanism continuation](../../../experiments/phase-07-2a-wall-liquid-routing/stage-04-ewf-wall-parameters/realism-continuation/feedback-off/results.md), [matched direct-drain test](../../../experiments/phase-07-2a-wall-liquid-routing/stage-04-ewf-wall-parameters/ewf-only-drain/results.md) and [long drain-ON development](../../../experiments/phase-07-2a-wall-liquid-routing/stage-04-ewf-wall-parameters/ewf-only-drain/long-development/results.md). -->

### 4.12. Numerical assessment of the selected development path

The implicit beta algorithm did not provide inner residual reports. Equal-time fields and mass accounts provided local checks, but the absence of residual reports was not treated as evidence of convergence. Settings were also checked by saving and reopening (Appendix A.9).

The shortened-startup contact source matched independently evaluated removal at all 3500 solved updates. A separate film-step test starting from identical fields showed that a 20 µs film step passed local field and ledger checks over 2.5 ms, whereas a 25 µs film step exceeded the 0.1% ledger-error limit.

These checks supported implementation and local step selection. Inner-film failures and unavailable residuals prevented a numerical convergence claim, while continued storage prevented a stationary-film claim (Appendix A.9.4).

Implementation checks therefore supported use of the selected procedures, while leaving numerical and physical limits in place. The final comparison tests the sensitivity of the developing film state to mesh resolution; it does not use those checks as proof of mesh independence.

<!-- Evidence: [combined-history residual checks](../../../experiments/phase-07-2a-wall-liquid-routing/stage-02-combined-ewf-roughness/case-history-N45606.md#ewf-residuals), [shortened-startup source audit](../../../experiments/phase-07-2a-wall-liquid-routing/stage-03-shortened-reconstruction/early-ewf-startup/results.md#film-evidence-and-numerical-limits), [matched-time film-step assessment](../../../experiments/phase-07-2a-wall-liquid-routing/stage-03-shortened-reconstruction/early-ewf-startup/film-development/results.md), [local screen criteria](../../../experiments/phase-07-2a-wall-liquid-routing/stage-03-shortened-reconstruction/early-ewf-startup/film-development/setup.md), [20 µs comparison JSON](../../../../PyAnsys/output/phase72a-stage3-film-development-server1/20261005/mid-film-sensitivity-20us.json) and [25 µs comparison JSON](../../../../PyAnsys/output/phase72a-stage3-film-development-server1/20261005/mid-film-sensitivity-25us.json). -->

### 4.13. Mesh sensitivity of film development and drainage

The coarse-mesh film history showed that drainage developed while storage continued (Section 4.10). Together with the later removal tests, this raised a further question: did the predicted film distribution, storage and drainage persist across mesh resolutions? The final comparison therefore used a common film age, with the observation time informed by the earlier film history.

The mesh study used 0.045 mm roughness with film-to-flow momentum feedback disabled. A common film age close to 200 ms was selected because earlier coarse-mesh drainage had begun to change more slowly, although film inventory was still increasing (Figure 18). This was a practical observation time for developing films, rather than a test of equilibrium. The earlier run used different film settings, so its drainage level and development timescale were not assumed transferable to the mesh study.

![Earlier 60k film input, drainage and accumulation rates used to inform the observation-time choice](../figures/methods-coarse-film-time-reference.png)

*Figure 18. Coarse-mesh film behaviour behind the observation-time choice. Drainage rises rapidly and then changes more slowly around 200 ms, while positive accumulation indicates continued film storage. The earlier Stage 3 reference run used frozen bulk fields and different film settings from Phase 9. The dotted line marks the earlier 265.184 ms checkpoint, not the selected 195 ms comparison time. Reproduced from the working poster; Section 4.10 gives the associated film-development results.*

<!-- Source: working poster ppt/media/image18.png; original generator PyAnsys/scripts/analysis/build_wall_film_poster_card.py; selected Stage 3 nominal-speed history PyAnsys/output/phase72a-stage3-speed-sensitivity-server1/20261006/selected-film-history-reference.csv. Accumulation is the film-mass change divided by each film interval. The author supplied the approximately 200 ms selection rationale; no formal plateau criterion is claimed. -->

The approximate 200 ms rationale and the exact saved endpoint are distinct: the final Phase 9 comparison selected 195 ms, with bulk equations still frozen. All four completed meshes—60,964, 342,609, 679,970 and 997,604 cells—were compared at that film age (Section 4.13). Here, frozen bulk means that the surrounding steam–liquid flow field was held fixed while the wall film continued to evolve. Each film therefore developed under the retained flow field for its own mesh, rather than under one identical field shared by all meshes. Starting ages ranged from 0.700 to 0.900 ms. The 342k reference preceded its bulk-active adjustment, whereas the other three references were at the bulk-freeze boundary. The 2,596,657-cell mesh supplied only an initial-bulk reference with provisional film settings. Differences in preparation and retained fields prevent the comparison from isolating spatial discretisation error. The blocker and ramp address separate geometry questions.

<!-- Evidence: [mesh-study setup](../../../experiments/phase-09-mesh-convergence/setup.md); [wall-film plan](../../../experiments/phase-09-mesh-convergence/ewf-plan-v1.md). The observation-time rationale was supplied by the author during report revision on 17 October 2026; it is not a quantified plateau test. Selected endpoint evidence is recorded in the Phase 9 results dated 17 October 2026. -->

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

### 4.14. Experiment workflow and use of automation

The model-development sequence above required continuity of the scientific question, starting state and evidence across runs and sessions. The agent-assisted workflow combined reusable knowledge, verified cases and code with a recorded experiment scope. OpenAI Codex, an AI coding assistant, helped carry out setup, execution and evidence handling, while I retained responsibility for scientific direction and interpretation. The connected knowledge base, durable records, task-specific instructions called skills, and Fluent-control tools together formed the agent harness. These supported continued experimentation; they did not establish numerical convergence or physical validity.

**Scale and reuse.** The retained project records identify 387 executed configurations across both authors, including failed and partial trials, covering outlet conditions, liquid removal, turbulence, wall roughness and wall-film behaviour. This count describes the breadth of work rather than a measured speed-up from automation. Reusing cases, code and analysis procedures gave later tests traceable starting points without rebuilding each procedure.

The workflow diagram shows how knowledge and implementation could be reused throughout the experiment cycle. On the left, literature, Fluent guidance and previous results informed discussion of the next question. On the right, the recorded question and setup guided case creation, verification, execution and analysis. Checked code, saved parent cases and analysis procedures provided starting points for later comparisons. Remote control supported work on separate Fluent sessions, each with one agent responsible for commands. Checkpoints, transcripts, OneDrive sharing and background monitoring allowed long runs to continue beyond an active chat. Findings then returned to the project record to inform the next test.

![Repository workflow linking research discussion and reusable knowledge to recorded intent, case verification, remote Fluent execution, analysis and the next experiment.](../../../../assets/readme/experiment-workflow.png)

*Experiment workflow. Recorded scientific intent guides execution, and the resulting evidence informs the next decision. Reproduced unchanged from the repository README. “Auto Loop” and “Result.md” are older labels for the current `phase-loop` workflow and `results.md` records. The diagram shows the developed workflow; earlier experiments did not all use the same implementation.*

**Keeping the agent on task.** Durable records gave the agent a defined problem to return to after a long conversation or a failed calculation. `CONTEXT.md` held the scientific question and permitted scope; `setup.md` specified the starting case, controlled change, fixed settings and required evidence. Findings and limitations were stored in `results.md`, while `phase-state.yaml` recorded the state needed to resume work. These files preserved earlier decisions without relying on conversation memory or repeatedly asking me to reconstruct them.

The directory structure made this information easier to find. `Project/` held project facts, `CFD_wiki/` held reusable literature and methods, `PyAnsys/` held executable code and machine evidence, and `.agents/skills/` held procedures. Each fact had one authoritative record, linked from other locations. Focused entry points directed the agent to relevant material. This reduced repeated searches for commands, methods and sources, and helped keep implementation tied to the current question. The structure was intended to limit unsupported assumptions, repeated debugging and irrelevant work, although these problems still occurred.

**Making progress verifiable.** Custom skills turned broad requests into concrete steps: identify the uncertainty, define a controlled test, inspect the starting case, apply settings in the required order, read back critical values, save and reopen the case, and check a short run before longer execution. Analysis then had to connect the observed fields and histories to the original question. These steps gave the agent observable completion criteria, so a plausible explanation or successful command alone was insufficient.

The custom Model Context Protocol (MCP) integration gave the agent tools to inspect and control Fluent through PyFluent. It extended Ansys's Fluent MCP with controls for attaching to existing sessions, checking generated code and preserving Fluent when the tool connection closed. Reviewed Python/PyFluent scripts handled longer calculations and specialised data extraction. Native solver state, transcripts and paired case/data files provided evidence of what had actually run.

This approach has a parallel in the work of Lauren Tan, a member of technical staff at Cursor, which develops AI coding tools. Her workshop describes the agent-skills framework used within Cursor and released as pstack ([Tan, 2026](https://maven.com/p/e23d9c/how-cursor-turned-ai-agents-into-better-engineers)). Her published verification example gives agents explicit navigation steps and observable evidence checks ([Tan, n.d.](https://github.com/poteto/verification-skill-example)). This provides a practical software-engineering example of making verification part of the agent's task. In CFD, however, verifying execution remains separate from establishing numerical convergence or physical validity.

**Human judgement and the research opportunity.** Faster execution did not ensure that the next experiment was useful. I was also learning Fluent and CFD, and my limited experience made it harder to recognise which uncertainties mattered. I spent time on investigations that later proved peripheral to the central liquid-routing question. Although the agent could propose and implement tests, I still needed to judge their relevance, interpret unexpected behaviour and decide when to change direction.

I expect that an experienced CFD researcher would use the same harness more effectively by asking sharper questions and recognising unproductive directions earlier. This is my reflection on the project, rather than a measured comparison between users. The experience suggests a promising direction for research: agents can take on more of the repeated implementation, execution and evidence-handling work, allowing researchers to explore more alternatives. Clear human direction and informed interpretation remain essential. The value of faster experimentation depends on the quality of the questions it serves.

<!-- Scale-count audit, 17 October 2026: all 166 exact setup.md files in the 15 Project/experiments campaign folders were read, together with linked results, historical/deferred setup records and execution evidence. Count distinct executed experimental conditions/protocols across BOTH authors. Multiple cases inside one setup count separately. Deliberately tested numerical-setting changes and standalone DPM comparisons count; failed/partial trials count if solver execution is evidenced. Exclude unchanged continuations, checkpoints, repeated identical conditions, routine implementation/seeded verification probes, pre-solve blocks, prepared-only cases, and scheduled controls never reached. Do not count every ramp step or individual particle track.
Campaign | setup.md files | distinct executed configurations
phase-01-purnanto-baseline-and-inlet-exploration | 7 | 22
phase-02-parity-reset-and-pre-v2-qualification | 5 | 15
phase-03-dpm-carryover-and-coupling | 5 | 28 (includes 12 Andy historical cases)
phase-04-ewf-wall-film-mechanisms | 7 | 7
phase-05-full-geometry-v2 | 8 | 52
phase-06-full-geometry-with-brine-pool | 8 | 8
phase-07a-simplified-purnanto-liquid-removal | 32 | 24
phase-07b-full-geometry-liquid-removal | 12 | 12
phase-07-1a-absorber-convergence | 1 | 9
phase-07-2a-wall-liquid-routing | 41 | 98
phase-08-storyline-reconstruction | 13 | 49
phase-09-mesh-convergence | 9 | 15
phase-09-steady-vof-pool | 8 | 23
phase-10-proposed-design | 9 | 10
phase-10-single-inlet-mesh-convergence | 1 | 15
TOTAL | 166 | 387 = 358 bulk/film/numerical conditions + 29 standalone particle-tracking comparisons.
Cross-phase deduplication: 7.2A R0/E0 counted once under 7.1A; 7.2A inherited 60k N8000 baseline counted under Phase 9 mesh; historical F1 SIMPLE/F0 alias counted once; Phase 6 S1-R/F11, D04/S3-C and S6/S4-C repeats excluded; Phase 6 D01/D02 pressure cases count once despite references in missing Phase 5 Stage 5; current matched 2025 R2 tet benchmark differs from historical 2024 R2 protocol. Same-control restarts and endpoint fractional timesteps are not extra cases.
Evidence limit: this is an exact sum of identified configurations in retained records, not a proven complete all-time total. Missing Phase 5 Stage 5 Realizable/RSM/SST detail, unidentifiable early Student/anthracite tests, a poorly identified failed stripping test and uncertain corrupt G025 execution were excluded. No simultaneous-computer count or measured speed-up is claimed. Detailed read-only subagent ledgers were produced in the operating-system temporary directory, consolidated as cfd-case-audit-consolidated.md; the campaign files above and their linked results own the evidence. -->

<!-- Workflow sources: [repository overview](../../../../README.md#experiment-workflow); [phase-loop procedure](../../../../.agents/skills/phase-loop/SKILL.md); [MCP session controls](../../../../PyAnsys/src/pyansys_fluent/mcp_server.py); [run-control procedure](../../../../.agents/skills/pyansys-workflow/references/run-control.md). The reflection on learning CFD, peripheral work and expert judgement comes from the author's direction on 17 October 2026. No measured reduction in hallucination or task drift is claimed. -->
