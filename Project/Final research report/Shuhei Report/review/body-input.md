<!-- Source: Project/Final research report/Shuhei Report/draft/01-introduction-and-literature-review.md -->
# Part 1 — Introduction and literature review

<!-- Research framing: credible liquid transport and collection, developed through mesh/inlet assessment, absorber and startup procedures, and wall-film studies. Internal evidence links are traceability notes. -->

## 1. Introduction

### 1.1. Engineering problem

Geothermal steam–water separators supply dry steam to turbines. Liquid carryover can cause erosion and transport minerals that form deposits. Design must therefore consider separation efficiency, pressure drop and operating pressure. ([Zarrouk & Purnanto, 2015](https://doi.org/10.1016/j.geothermics.2014.05.009))

This study develops an inherited computational fluid dynamics (CFD) model of a vertical bottom-outlet cyclone with a spiral inlet. It follows liquid from inlet placement through wall transport and collection.

<!-- Evidence: [Study scope](../../../scope.md); [inlet-development interpretation](../../../experiments/phase-01-purnanto-baseline-and-inlet-exploration/interpretation.md); [author's development context and meeting sources](../Shuhei-Context.md#how-the-project-understanding-developed); [absorber-development context](../../../experiments/phase-07-1a-absorber-convergence/CONTEXT.md). -->

### 1.2. Problem in the inherited model

The simplified geometry omits the lower brine-discharge path. A closed bottom gives liquid no intended exit; opening the whole lower boundary can also let steam escape there. The model needs a collection treatment that preserves the steam route.

Liquid reaching the wall is only one stage of separation. A lower liquid flow through the steam outlet can accompany greater collection, continued storage or transfer into a wall film. The model must therefore follow liquid destinations alongside outlet flow to assess what each change achieves.

<!-- Evidence: [Model boundary](../../../model.md). -->

A virtual collector, termed an absorber, and reduced-feed startup enabled roughness and Eulerian Wall Film (EWF) studies after unsuccessful full-geometry drainage trials.

<!-- Evidence: [Verified early absorber](../../../experiments/phase-07-1a-absorber-convergence/baseline-v2-virtual-liquid-outlet/results.md); [selected case history](../../../experiments/phase-07-2a-wall-liquid-routing/stage-02-combined-ewf-roughness/case-history-N45606.md); [full-geometry scope decision](../../../experiments/phase-06-full-geometry-with-brine-pool/conclusion.md); historical lower-boundary dilemma in [29 April, 04:04–06:36](../../../meetings/otter/2026-04-29-wk-7-steam-liquid-separator-analysis.md). -->

<!-- Evidence: [R0 control](../../../experiments/phase-07-1a-absorber-convergence/roughness-family/r0-smooth-control/results.md); [source-inclusive R0 accounting assessment](../../../experiments/phase-07b-full-geometry-liquid-removal/convergence-investigation/shuhei-audit.md). -->

### 1.3. Research aim and questions

The aim is to develop and assess the separator model's liquid-transport and collection paths. Predicting separation efficiency and pressure drop is the longer-term purpose. The present work addresses four questions:

1. How do mesh representation and inlet phase placement affect liquid distribution and retention near the wall?
2. How can numerical collection and staged startup provide starting fields for wall studies?
3. How do wall roughness and wall-film modelling affect liquid transport, storage, release and collection?
4. What numerical and liquid-accounting evidence supports these predictions, and what remains necessary for field validation?

### 1.4. Scope and contribution

The study mainly uses the simplified primary separator. Mesh and inlet comparisons lead into collector development, startup and wall-treatment studies. Later cases examine film development to 500 ms, release mechanisms and direct drainage. Downstream equipment, mineral chemistry and optimum operating pressure are outside the simulated scope.

<!-- Evidence: [Study overview](../../../index.md); [selected case history](../../../experiments/phase-07-2a-wall-liquid-routing/stage-02-combined-ewf-roughness/case-history-N45606.md). -->

The contribution combines checked collection and startup procedures with evidence of how model choices affect liquid delivery, storage and removal. The comparisons assess model development rather than validated separator performance; refinement of the combined model remains incomplete. Appendix A.2 defines the controlled reconstructions.

Figure 1 maps the liquid destinations examined across separate configurations. Transfer into film or droplets changes the liquid representation within the vessel; collector and drain treatments remove it from the model. Released-droplet destinations require tracking. During frozen-bulk film tests, reciprocal depletion of the bulk liquid is not advanced.

![Conceptual overview of bulk liquid, wall-film storage, released droplets and external removal routes](../figures/report-liquid-destinations-overview.png)

*Figure 1. Liquid destinations examined in separate model configurations. Wall capture can lead to storage, release or removal. Numerical sinks and native film-edge outflow are distinct; this is a conceptual map, not a measured balance.*

<!-- Overview basis: Sections 3.2–3.3, 4.7, 4.10–4.11 and 5.3–5.6; [editable figure and source record](../figures/report-liquid-destinations-overview.provenance.json). No arrow represents a measured rate or proven final droplet fate. -->

Section 3 describes the model and comparisons. Section 4 asks how liquid reaches the wall, where it can go and what wall treatment changes. Sections 5–6 connect these findings to collection and the evidence needed for performance prediction.

## 2. Literature review

### 2.1. How a geothermal steam–water separator works

A vertical bottom-outlet cyclone (BOC) uses a tangential or spiral inlet to rotate the incoming steam and brine. Liquid moves towards the wall while steam occupies the central region. An internal pipe carries steam out through the bottom; brine leaves separately. *Bottom outlet* refers to the steam-pipe arrangement. ([Zarrouk & Purnanto, 2015](https://doi.org/10.1016/j.geothermics.2014.05.009))

Liquid at the wall can form a film that drains towards the brine discharge or releases droplets back into the steam (Figure 2). The schematic also distinguishes brine discharge from downstream liquid collection and condensation.

![Published conceptual BOC flow diagram showing the wall film, steam pipe, brine discharge and downstream drain](../figures/literature/rizaldy-2016-figure-5-operation.png)

*Figure 2. Conceptual separator liquid paths: wall film, carryover, brine discharge ($\dot m_l$) and downstream collection ($\dot m_b$). Source: [Rizaldy et al. (2016)](https://www.researchgate.net/publication/310818568_LIQUID_CARRYOVER_IN_GEOTHERMAL_STEAM-WATER_SEPARATORS), fig. 5.*

<!-- Evidence: [Model boundary](../../../model.md). Figure source: [primary carryover paper](../../../../CFD_wiki/raw/053_Rizaldy_Final.pdf), PDF page 3, original fig. 5; symbol interpretation checked against PDF pages 3–4. [Full-page source preview](../figures/literature-candidates/wall-film/rizaldy-2016-pdf-page-03.png). The inserted panel was rendered directly from the local PDF; its labels and arrows are unchanged. -->

### 2.2. Internal flow physics and performance measures

Rotation produces a low-pressure core, with inward acceleration scaling as $u_\theta^2/r$ for tangential velocity $u_\theta$ and radius $r$. Density-dependent responses to pressure and drag allow outward liquid transport. Fine droplets can follow steam; larger droplets reach collection surfaces more readily. Uncertain inlet sizes and continued droplet generation complicate prediction. ([Pointon et al., 2009](https://publications.mygeoenergynow.org/grc/1028587.pdf))

Higher velocity can strengthen outward transport but also increase entrainment by steam shear. Empirical data show rapid wetness increases at different velocities for different separators (Figure 3). Thus, greater swirl alone does not establish better separation. ([Zarrouk & Purnanto, 2015](https://doi.org/10.1016/j.geothermics.2014.05.009))

![Published empirical outlet wetness and steam-quality curves versus inlet steam velocity for three separator datasets](../figures/literature/zarrouk-purnanto-2015-figure-12-breakdown.png)

*Figure 3. Outlet wetness rises at different inlet velocities across three datasets. Right axis: steam quality. Source: [Zarrouk and Purnanto (2015)](https://doi.org/10.1016/j.geothermics.2014.05.009), fig. 12, using Bangma (1960) and Lazalde-Crabtree (1984) data.*

<!-- Figure source: [primary design review](<../../../../CFD_wiki/raw/Zarrouk and Purnanto 2014.pdf>), PDF page 12 / printed page 247; [full-page source preview](../figures/literature-candidates/design-overview/zarrouk-purnanto-2015-page-12.png). The published axes, curves, points and legend are unchanged. -->

Outlet steam quality is

$$
x_{\mathrm{out}}=
\frac{\dot m_{v,\mathrm{out}}}
{\dot m_{v,\mathrm{out}}+\dot m_{l,\mathrm{out}}},
$$

where the terms are outward vapour and liquid mass-flow rates through the steam outlet. Purnanto et al. (2013) used this measure. It differs from liquid-capture fraction, which compares collected liquid with inlet liquid; their denominators are not interchangeable. ([Purnanto et al., 2013](https://www.researchgate.net/publication/269519626_CFD_MODELLING_OF_TWO-PHASE_FLOW_INSIDE_GEOTHERMAL_STEAM-WATER_SEPARATORS))

Steam purity concerns contamination. Chemical carryover estimates are affected by condensation and drain-pot collection, so field comparisons need matching definitions and sampling locations. ([Rizaldy et al., 2016](https://www.researchgate.net/publication/310818568_LIQUID_CARRYOVER_IN_GEOTHERMAL_STEAM-WATER_SEPARATORS))

Internal pressure drop requires defined inlet/outlet locations and a stated static or total pressure measure. It differs from selecting optimum operating pressure, which also involves flashing and plant conditions. The present no-flashing model addresses internal flow at prescribed phase conditions. ([Pointon et al., 2009](https://publications.mygeoenergynow.org/grc/1028587.pdf); [Zarrouk & Purnanto, 2015](https://doi.org/10.1016/j.geothermics.2014.05.009))

### 2.3. Established design methods and geothermal CFD

Empirical geothermal design methods provide reference points for CFD. However, CFD's additional flow detail must be assessed against its assumptions and comparison evidence. ([Zarrouk & Purnanto, 2015](https://doi.org/10.1016/j.geothermics.2014.05.009))

Pointon et al. (2009) used Fluent's Discrete Phase Model (DPM) with assumed droplet feed and wall/baffle collection. Predicted efficiencies were 99.96% for scrolled and 99.93% for tangential entry; an empirical design method gave 99.955%. Scrolled entry also gave higher mean tangential velocities, 34.1 rather than 32.5 m/s (Figure 4). Empirical agreement did not independently test the feed or collection assumptions. ([Pointon et al., 2009](https://publications.mygeoenergynow.org/grc/1028587.pdf))

*(a) Inlet configurations.*

![Published scrolled or lemniscate inlet on the left and tangential inlet on the right](../figures/literature/pointon-2009-figure-5-inlets.png)

*(b) Calculated tangential-velocity distributions.*

![Published tangential-velocity fields for the scrolled and tangential inlet configurations](../figures/literature/pointon-2009-figure-7-velocity.png)

*Figure 4. Scrolled entry gives higher calculated tangential velocity. (a) Geometries; (b) velocity fields. Scrolled: left; tangential: right. Source: [Pointon et al. (2009)](https://publications.mygeoenergynow.org/grc/1028587.pdf), figs. 5 and 7.*

<!-- Figure source: [primary Pointon paper](../../../../CFD_wiki/raw/1028587.pdf), PDF pages 5–6 / printed pages 946–947; [geometry source page](../figures/literature-candidates/pointon/page-5.png); [velocity source page](../figures/literature-candidates/pointon/page-6.png). Both published panels, the velocity legend and mean annotations are unchanged. The report adds the (a)/(b) labels outside the images. -->

Purnanto et al. (2013) compared three BOC configurations using a steady Mixture model and DPM outlet-quality calculation. Changed vessel proportions prevented isolation of inlet shape. Counting incomplete droplet tracks as separated improved empirical agreement, but the authors called that assumption non-rigorous. The inherited modelling basis therefore requires explicit treatment of unresolved droplet fate. ([Purnanto et al., 2013](https://www.researchgate.net/publication/269519626_CFD_MODELLING_OF_TWO-PHASE_FLOW_INSIDE_GEOTHERMAL_STEAM-WATER_SEPARATORS))

Both studies used renormalisation-group (RNG) k–ε turbulence modelling. Pointon's swirl modification and lower-cost rationale offer a starting point, not a detailed turbulence-model comparison. Accuracy in the present swirling and near-wall flow remains to be assessed. ([Pointon et al., 2009](https://publications.mygeoenergynow.org/grc/1028587.pdf); [Purnanto et al., 2013](https://www.researchgate.net/publication/269519626_CFD_MODELLING_OF_TWO-PHASE_FLOW_INSIDE_GEOTHERMAL_STEAM-WATER_SEPARATORS))

Appendix B.2 compares the methods and assumptions carried into this study.


### 2.4. Wall–liquid transport and carryover

Film motion depends on gravity, pressure and shear. Deposition adds liquid; drainage removes it; entrainment returns droplets to the steam. More wall deposition can therefore increase storage or later release without increasing external collection.

Rizaldy et al. (2016) predict entrainment sensitivity to loading, film thickness and velocity. Figure 5 shows undercut and roll-wave release, associated with lower and higher film Reynolds numbers, respectively. Film Reynolds number compares inertia with viscosity using liquid velocity and film thickness. Missing brine-flow data prevented the required comparison with Wairakei drain-pot measurements, leaving quantitative field agreement unresolved. ([Rizaldy et al., 2016](https://www.researchgate.net/publication/310818568_LIQUID_CARRYOVER_IN_GEOTHERMAL_STEAM-WATER_SEPARATORS))

![Published conceptual undercut and roll-wave droplet-entrainment mechanisms at a liquid film](../figures/literature/rizaldy-2016-figure-9-entrainment.png)

*Figure 5. Steam shear releases film droplets through (a) undercut and (b) roll-wave entrainment. Source: [Rizaldy et al. (2016)](https://www.researchgate.net/publication/310818568_LIQUID_CARRYOVER_IN_GEOTHERMAL_STEAM-WATER_SEPARATORS), fig. 9, crediting Ishii and Grolmes (1975).*

<!-- Figure source: [primary carryover paper](../../../../CFD_wiki/raw/053_Rizaldy_Final.pdf), PDF page 5; [full-page source preview and original attribution](../figures/literature-candidates/wall-film/rizaldy-2016-pdf-page-05.png). The two published mechanism panels and labels are unchanged. -->

Fluent roughness changes near-wall momentum transfer; it does not add a film store or drain. EWF instead adds surface storage and transport. Their outlet-flow responses must be read alongside retained mass and collection. ([Ansys, Inc., 2025k](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_th/x1-5720008.164.html))

### 2.5. Representing liquid and its collection

The Mixture model represents bulk liquid through secondary-phase volume fraction. Algebraic slip estimates relative phase velocity using local equilibrium. Liquid volume fraction does not directly resolve film thickness or droplet-size distribution. ([Ansys, Inc., 2025d](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_th/flu_th_sec_drift_oview.html))

DPM follows size-dependent droplet trajectories. Its interpretation requires defined injection and boundary treatments, with every tracked fate counted, including incomplete trajectories.

Skoog (2020) combined EWF surface transport, DPM deposition and entrainment in a reactor-channel approximation. Film/droplet flows were compared with one-dimensional calculations using experimentally based Okawa correlations. Inlet allocation and transverse droplet velocity affected the result. The separate liquid accounts provide a precedent; reactor conditions and correlations still need justification for a cyclone. ([Skoog, 2020](https://www.diva-portal.org/smash/get/diva2:1452100/FULLTEXT02.pdf); [Ansys, Inc., 2025e](https://ansyshelp.ansys.com/public/views/secured/corp/v252/en/flu_ug/flu_ug_models_wallfilm.html))

Bulk-to-film transfer moves liquid within the domain; the absorber removes it. Droplet injection must not duplicate another liquid feed. Fluent permits cell-zone mass and associated transport sources, but their law and effect require assessment. Section 3 describes the contact-based absorber. ([Ansys, Inc., 2025a](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/flu_ug_bcs_sec_cell_zones.html))

<!-- Evidence: [Audited model basis](../../../model.md); [liquid-accounting guardrails and application of Skoog](../../../technical/skoog-application-guardrails.md); [absorber-development context](../../../experiments/phase-07-1a-absorber-convergence/CONTEXT.md). -->

### 2.6. Numerical startup, convergence and validation

A steady calculation's iterations and pseudo-time describe numerical development, not physical filling time. The National Aeronautics and Space Administration (NASA) recommends monitoring residuals and relevant outputs, with convergence criteria tied to acceptable output error. ([NASA, 2021a](https://www.grc.nasa.gov/www/wind/valid/tutorial/iterconv.html))

Fluent permits flow development before film initialisation. Reduced-feed startup and ramp choices remain case-specific procedures requiring assessment. ([Ansys, Inc., 2025h](https://ansyshelp.ansys.com/public/views/secured/corp/v252/en/flu_ug/flu_ug_ewf_sec_overview.html))

Implementation checks, iterative convergence, mass accounting and numerical sensitivity answer separate questions. Mesh and time-step studies require a fixed model; roughness or absorber changes instead test model sensitivity. ([NASA, 2021c](https://www.grc.nasa.gov/www/wind/valid/tutorial/verassess.html))

Physical validation requires relevant measurements and uncertainty assessment. Here, field comparison must examine the assumed collection route and outlet predictions within the tested operating range. ([NASA, 2021b](https://www.grc.nasa.gov/www/wind/valid/tutorial/valassess.html))

<!-- Evidence: [Verification and validation limits](../../../vnv.md). -->

### 2.7. Remaining model uncertainties and research direction

The literature makes the definition of collection central to the research problem. A droplet that reaches a collecting boundary has a terminal fate in Pointon's model, whereas the film literature allows captured liquid to return to the steam. Purnanto's incomplete tracks expose a further distinction between a calculated destination and an assumed one. Agreement in an outlet measure therefore leaves the internal liquid path unresolved when feed, capture or final fate is imposed.

The inherited model adds a specific difficulty: its truncated domain omits brine discharge. Mesh and inlet comparisons can change delivery to the wall, but cannot supply the missing exit. This study therefore connects those comparisons to collector development and then to film storage, release and drainage. The separate bulk, film and droplet accounts make it possible to ask whether a lower bulk-liquid outlet rate accompanies external collection, internal transfer or continued storage. That distinction determines what each result contributes towards performance prediction.


<!-- Source: Project/Final research report/Shuhei Report/draft/02-model-and-methods.md -->
# Part 2 — Model and methods

## 3. Model and methods

### 3.1. Computational domain and modelling scope

The model represented the upper separation region of a vertical cyclone: spiral inlet, vessel walls and steam outlet. It omitted the brine pool and discharge. The bottom remained a wall, so uncollected liquid could accumulate or leave through the steam outlet.

A numerical collector represented transfer into the omitted pool without opening a steam exit at the base. Full-geometry trials had not established stable drainage and pool control (Appendix A.13). Pool motion and downstream discharge remained outside the model. Absorber-free cases disabled collection in the same domain.

![Saved computational domain and pure-phase inlet split](../figures/model-domain-overview.png)

*Figure 6. Solved 60,964-cell domain (a) and 6.754 mm wall-side inlet strip (b). The lower collector is a numerical sink; the brine pool and discharge are omitted.*

The mesh uses vertical $y$, with the bottom near $y=0$ (exact bounds in Appendix A.1). The collector contains 715 cells selected by centroid position, $y\leq0.10$ m; their nodes extend to about $y=0.185$ m. The full-feed parent, combined contact endpoint and shortened-startup endpoint share coordinates and connectivity. The steam-outlet label marks the computational boundary at the central pipe opening. Bulk flow used a steady formulation, while film evolved on a separate clock. Bulk startup described numerical development through iterations, not physical startup time.

### 3.2. Physical model and assumptions

#### 3.2.1. Bulk steam–liquid flow

Ansys Fluent 2025 R2 used a pressure-based Mixture solver for bulk continuity, momentum, liquid fraction and algebraic slip. Steam was primary and water secondary. RNG $k$–$\varepsilon$ included swirl treatment and standard wall functions; gravity acted downwards. Energy was disabled, excluding flashing, condensation and temperature-dependent properties. Table 1 gives material values; Appendix A.1 records the controls. ([Ansys, Inc., 2025d](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_th/flu_th_sec_multiphase_mixture.html))

*Table 1. Fixed material properties verified for the throughput-controlled absorber model.*

| Phase | Density (kg/m³) | Dynamic viscosity (Pa·s) |
| --- | ---: | ---: |
| Vapour | 5.79743 | $1.52062\times10^{-5}$ |
| Liquid water | 881.211 | $1.45544\times10^{-4}$ |

These three saved states used Manninen slip, Schiller–Naumann drag and 10 µm liquid-phase diameter. This local-equilibrium slip model was held fixed during wall comparisons; its accuracy for concentrated wall liquid remained unverified. The diameter controls continuum slip, separately from DPM droplets and film (Appendix A.1).

#### 3.2.2. Wall roughness and wall-film representation

Roughness changed wall friction through equivalent sand-grain height $k_s$ and constant $C_s$. Tested values were sensitivity inputs, not measured surface properties. The wall treatment and unresolved settings are documented in Appendix A.10. ([Ansys, Inc., 2025k](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_th/x1-5720008.164.html))

Eulerian Wall Film (EWF) solved surface mass and momentum, with accretion transferring bulk liquid into the film. Through the 500 ms reference, gravity, gas shear, wall viscosity and momentum advection drove transport; native film-edge outflow supplied drainage. Additional film forces and droplet interactions were disabled (Appendix A.9). ([Ansys, Inc., 2025e](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/flu_ug_ewf_sec_options.html))

Later tests added pressure-gradient, spreading and surface-tension forces, droplet collection, splashing, stripping and edge separation. The last three mechanisms return film liquid to droplets. Changed bulk fields prevent attribution to one mechanism. Film-to-bulk momentum feedback stayed off, separately from numerical coupling of the film equations (Appendix A.12). ([Ansys, Inc., 2025b](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_th/flu_th_ewf_sec_film_submodels.html))

### 3.3. Boundary conditions and liquid collection

#### 3.3.1. Enthalpy and the inlet phase mass flows

The reference feed was 197.61 kg/s at 1600 kJ/kg and 11.2 bar absolute. Saturated enthalpies gave vapour quality 0.408323. Inlet commands retained Purnanto's rounded phase flows in Table 2; Appendix A.7 gives the thermodynamic calculation. ([Purnanto et al., 2013](https://www.researchgate.net/publication/269519626_CFD_MODELLING_OF_TWO-PHASE_FLOW_INSIDE_GEOTHERMAL_STEAM-WATER_SEPARATORS))

#### 3.3.2. Volumetric flow, inlet split and velocity

The 0.724 m square inlet assigned about 0.933% of its area to a 6.754 mm liquid strip, sized from phase volume flows under an assumed common velocity. Appendix A.7 distinguishes the design properties from the solved densities and resulting phase velocities.

The strip replaced an exploratory inlet that mixed liquid and steam over half the opening. Upstream pipe films support testing liquid entry beside the wall; complete segregation remained imposed. The matched mixed/split comparison tested its consequences. ([Pointon et al., 2009](https://publications.mygeoenergynow.org/grc/1028587.pdf))

#### 3.3.3. Fluent boundary implementation

The wall-treatment calculations admitted pure liquid and vapour normal to their respective inlets (Table 2). Operating pressure was 0 Pa, so outlet gauge pressure equalled absolute pressure; inlet pressure was calculated. Appendices A.6 and A.2 give turbulence/backflow inputs and reconstruction differences.

*Table 2. Main boundary conditions. Reduced feed was 25% of full feed, with the phase mass ratio retained.*

| Boundary | Condition | Full feed | Reduced feed |
| --- | --- | ---: | ---: |
| Liquid inlet | Liquid mass-flow inlet | 116.9200 kg/s | 29.2300 kg/s |
| Vapour inlet | Vapour mass-flow inlet | 80.6900 kg/s | 20.1725 kg/s |
| Steam outlet | Gauge pressure | 1.120 MPa | Same |
| Vessel and bottom | Stationary, no-slip walls | Selected roughness/film treatment | As defined for startup |

#### 3.3.4. Contact-based absorber

The early absorber prescribed total removal from inlet throughput, distributed by the liquid present in the collector. The later contact absorber instead responded to local liquid inventory, without an inlet-throughput cap or direct vapour mass sink:

$$
S_L=-\frac{\rho_L\alpha_L}{\tau},\qquad \tau=10^{-5}\ \mathrm{s}.
$$

Here, $\rho_L$, $\alpha_L$ and $\tau$ are liquid density, volume fraction and depletion time; $S_L$ has units kg/(m³·s). Associated momentum and turbulence sources represented one-way capture. Appendices A.3–A.5 give the implementation, source checks, depletion-time sensitivity and earlier throughput-controlled law. ([Ansys, Inc., 2025a](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/flu_ug_bcs_sec_cell_zones.html))

Bulk removal, film drainage and diagnostic-particle escape were separate routes. Early film drained where the active EWF wall ended. A later test extended EWF onto the lower wall and added a direct film mass sink with matching momentum removal and assumed 1.5 ms capture time. An isolated source check and matched 15 ms OFF/ON runs tested it with all bulk equations frozen (Appendix A.12).

### 3.4. Mesh and spatial discretisation

Fluent Meshing produced polyhedral–hexahedral meshes with wall-following layers for the expected liquid path. Reduced numerical diffusion remained a hypothesis dependent on resolution, alignment and discretisation. ([Ansys, Inc., 2025c](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/flu_ug_GridTypes.html))

The main mesh contained 60,964 cells. Appendix A.6 gives spatial schemes; Appendix A.10 gives connectivity and wall fields. Mean main-wall $y^+$ was approximately $2.0\times10^4$–$3.4\times10^4$ across three saved states, so wall-following topology did not establish fine wall resolution. Layer dimensions and solver mesh-quality measures remain unverified. Section 3.6 defines the separate mesh comparisons.

### 3.5. Numerical solution procedure

Original startup used Hybrid Initialisation, smooth walls, EWF off and throughput-controlled collection. A failed command left 25% feed to iteration 1580. The corrected 2000-update ramp preceded the change from SIMPLE to Coupled with Global Time Step. Warm-up and a 1000-update control supplied the iteration-5586 parent (Appendix A.5).

The **developed parent** was a saved full-feed field selected after reviewing residuals, inventories, flows and sources. It supplied common initial fields for wall comparisons, but retained a substantial liquid-balance error and did not establish convergence. Shortened startup reused iteration-1580 fields without reinitialisation and enabled contact collection, 0.5 mm roughness, Coupled flow and dry film together (Appendix A.16).

Coupled solved pressure and momentum corrections together, with Mixture volume fraction solved separately. Coupling and pseudo-time changed together, so their individual effects were not isolated. Later film runs froze bulk flow, turbulence, volume fraction and relative motion. Fluent's steady EWF procedure assumes a converged frozen carrier; here the freeze allowed development under fixed forcing before bulk convergence was established. ([Ansys, Inc., 2025i](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/flu_ug_sec_uns_solve_pvel_1.html); [2025j](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/flu_ug_sec_multiphase_solution.html); [2025g](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_th/flu_th_ewf_sec_sol_alg.html))

The implicit beta algorithm lacked inner residual reports. Equal-time fields and mass accounts supplied local checks; missing residuals were not passes. Save/reopen checked settings (Appendix A.9).

### 3.6. Comparison design

Exploratory inlet, droplet and film tests guided later controlled comparisons (Appendix A.13). Wall screens started from a common parent. Startup and combined continuations changed several settings together and tested procedures (Appendix A.16). Roughness ranged from 0 to 8 mm; $C_s$ variations and reporting windows are given in Appendix A.5.

The common parent held the inherited flow field fixed at the start of each wall screen, reducing the influence of different preparation histories. Equal update horizons and reporting windows then compared the response to the selected treatment. Because the parent was still developing, the comparison assessed that response rather than equilibrium performance. The startup study asked a different question: whether the combined model could reach full feed with smaller loading disturbances. Its matched ramp progress aligned inlet loading, while the separate activation hold retained the disturbance caused by introducing the additional models.

Absorber-free mixed/split Coupled reconstructions held mesh, feed and controls fixed, with fresh initialisation and 10,000 updates. The historical tetrahedral comparison changed mesh, inlet and preparation. SIMPLE/Coupled reconstruction comparisons also changed pseudo-time and the $k$ scheme, so neither isolated one cause.

Finer absorber-free SIMPLE diagnostics compared 342,609-, 679,970- and 997,604-cell fields at iteration 3000. These developing solutions were not a converged mesh study (Appendix A.2).

The final mesh study compares five resolutions with the combined wall-film and collection model, 0.045 mm roughness and film-to-flow momentum feedback off (Section 4.13). The blocker and ramp address separate geometry questions. Mesh independence remains unresolved.

<!-- Evidence: [mesh-study setup](../../../experiments/phase-09-mesh-convergence/setup.md); [wall-film plan](../../../experiments/phase-09-mesh-convergence/ewf-plan-v1.md). Reconcile final settings and executed endpoints before completing the reserved result. -->

### 3.7. Data reduction and numerical assessment

Each value retained its case, active equations and reporting window. Endpoints, means and residual minima were distinct. Inventories, outlet flows, collection and film-transfer rates were assessed with residuals and source checks. A fixed iteration horizon did not establish convergence. Appendix A.9 defines the numerical criteria and integration methods.

Fluent fluxes were positive into the domain. With EWF off and no other liquid transfer, the signed remainder (kg/s) was

$$
R_L=\sum_b\dot m_{L,b}+\dot m_{L,\mathrm{source,applied}}.
$$

The source retained its negative removal sign. Evaluated and applied removal described the same sink, so only one entered the balance. Bulk-to-film accretion cancelled only in compatible combined accounts. Native mixture and phase-summed reports were assessed separately.

The early film balance compared integrated accretion with drainage plus inventory change over accepted film time; Appendix A.9 defines the integration and normalised error. Later release mechanisms required separate transfer terms (Appendix A.12). With bulk frozen, reciprocal bulk depletion did not advance, so film-account agreement could not establish combined conservation.

Wall screens used final-500 arithmetic means; the 500 ms film run used overlap-weighted final-10-ms rates. The bulk-liquid outlet ratio used liquid feed as denominator; outlet dryness used total outlet flow (Section 2.2). Neither pathlines nor diagnostic-droplet fates replaced bulk-liquid fluxes. Residual scaling was checked for startup comparisons; residuals were not percentage mass imbalances. ([NASA, 2021a](https://www.grc.nasa.gov/www/wind/valid/tutorial/iterconv.html))

### 3.8. Experiment workflow and use of automation

The cycle was question → bounded comparison → implementation check → Fluent solve → interpretation → next question. The researcher set scientific scope and interpreted findings. Task-specific agent instructions, Python and PyFluent supported execution. Native reports, transcripts and reopened case/data pairs recorded what ran. This workflow supported repeatable tests and recovery; numerical and physical assessments remained separate. Appendix B links the records.


<!-- Source: Project/Final research report/Shuhei Report/draft/03-results.md -->
# Part 3 — Results

<!-- Findings follow the physical model-development questions, rather than experiment date. -->

## 4. Results

Mesh and inlet comparisons first assess liquid delivery and retention. Collector and startup studies then supply fields for wall comparisons. Film histories finally test whether captured liquid drains, remains stored or returns to droplets. Earlier exploratory studies are retained in Appendix A.13.

Each comparison uses its stated mesh and settings. Outlet liquid flow is positive outwards unless a signed value is given. Steady iteration describes numerical development; accepted film time describes the transient film calculation.

### 4.1. Mesh development and the wall-liquid field

The polyhedral–hexahedral mesh had larger interior cells, polyhedral transitions and thin layers along the wall (Figure 7). The workflow gave control over the mesh near the expected liquid path; Section 3.4 gives its near-wall resolution.

At iteration 10,000, the historical tetrahedral field showed thin wall-side liquid enrichment. The 60,964-cell SIMPLE reconstruction showed a broader region with a higher liquid fraction. Inlet representation and preparation also differed, and the coarse SIMPLE state had a large mass-balance error. The comparison shows changed fields; reduced numerical diffusion remains a possible explanation, not a measured accuracy gain.

![Native mesh sections and liquid-fraction fields for the historical tetrahedral case and polyhedral–hexahedral reconstruction](../figures/results-mesh-spatial-comparison.png)

*Figure 7. Mesh sections (a–b) and liquid-fraction fields (c–d) at iteration 10,000. The reconstructed case shows broader wall enrichment; mesh, inlet and preparation differ, so the comparison does not isolate a mesh effect.*

<!-- Evidence: [native mesh and liquid-field comparison, source pairs and export manifests](../../../Poster/poster-sections/mesh-and-volume-fraction-comparison.md); solved 60k topology and wall-resolution evidence in Appendix A.10. The separate 342k mesh illustration used elsewhere is not substituted for the 60k contour's mesh here. -->

### 4.2. Two-phase inlet and wall-side liquid placement

Split feed produced a more continuous liquid-rich wall band and deeper lower-region enrichment than mixed feed (Figure 8). At nominal 26.81 m/s, iteration-10,000 bulk-liquid inventory increased from 1262.6 to 1734.5 kg: a difference of 471.9 kg, or 37.4%. Split feed retained more liquid at all five tested speeds, 20.11–32.14 m/s.

Both cases used the same 60,964-cell mesh, total phase feed, Coupled settings, initialisation and 10,000-update horizon. Mixed feed supplied both phases across both inlet faces; split feed supplied liquid through the wall-side strip. Complete phase segregation was an assumed profile (Section 3.3). Over iterations 9500–10,000, outward steam-outlet liquid averaged 99.671% of the 116.9387 kg/s liquid feed for mixed feed and 99.404% for split feed. The inventory difference therefore accompanied almost complete liquid discharge through the steam outlet, rather than a separate collection route.

![Bulk-liquid fraction at inlet height and through the vessel height with mixed and wall-side split feed](../figures/results-inlet-spatial-comparison.png)

*Figure 8. Wall-side split feed produces a more continuous liquid-rich wall band than mixed feed. Matched iteration-10,000 sections use a shared 0–1 scale; both cases have no collector or EWF.*

<!-- Evidence: [matched inlet setup and numerical basis](../../../experiments/phase-08-storyline-reconstruction/stage-01-60k-storyline/baseline-lineage-audit.md), [mixed-feed results](../../../experiments/phase-08-storyline-reconstruction/stage-01-60k-storyline/f1-one-inlet/results.md), [split-feed inventory and spatial findings](../../../experiments/phase-08-storyline-reconstruction/stage-01-60k-storyline/f2-split-inlet/results.md), and [native inlet-plane exports](../../../Poster/poster-sections/mesh-and-volume-fraction-comparison.md). Percentage inventory change is calculated from the rounded published endpoint values. -->

### 4.3. Liquid accumulation and the need for collection

Saved fields from the three finer split-inlet SIMPLE cases placed liquid near the wall and base. Their inventory and outlet histories show accumulation with little discharge through the steam outlet (Figure 9). At iteration 3000, the 342,609- and 679,970-cell inventories were both about 454–455 kg, whereas the 997,604-cell case held 333.142 kg. The latter discharged only 0.003623 kg/s through the steam outlet and held 69.16% of its liquid below $y=1$ m. These developing checkpoints do not form a mesh-convergence result; Appendix A.17 retains their exact values.

![Liquid inventory and outlet flow across the three finer absorber-free meshes](../../../experiments/phase-08-storyline-reconstruction/stage-02-fine-mesh-simple/direct-student-342k/n3000/figures/matched-mesh-checkpoints.png)

*Figure 9. Liquid accumulates while outlet flow remains small in the finer absorber-free SIMPLE cases. Lines connect saved checkpoints; solver iterations are not physical time.*

On the 679,970-cell mesh, inventory reached 764.744 kg at iteration 4000, with 69.62% below $y=2$ m. Outlet liquid was 8.00 kg/s, or 6.84% of the feed. The next continuation failed after printed iteration 4211; its cause was not isolated.

The inlet and mesh studies changed delivery and retention but supplied no separate collection route. The next studies introduced a liquid-selective source after unresolved full-geometry drainage trials (Appendix A.13), then tested startup before comparing wall treatments.

<!-- Evidence: [matched finer-mesh checkpoints](../../../experiments/phase-08-storyline-reconstruction/stage-02-fine-mesh-simple/direct-student-342k/n3000/results.md), [997k spatial result](../../../experiments/phase-08-storyline-reconstruction/stage-02-fine-mesh-simple/direct-student-997k/n3000/results.md), [680k accumulation and failed continuation](../../../experiments/phase-08-storyline-reconstruction/stage-02-fine-mesh-simple/direct-student-680k/n4000/results.md), [mixed-inlet Coupled account](../../../experiments/phase-08-storyline-reconstruction/stage-01-60k-storyline/f1-one-inlet/results.md) and [full-geometry scope decision](../../../experiments/phase-06-full-geometry-with-brine-pool/conclusion.md). -->

### 4.4. Reduced-feed development and inlet ramp

The startup and wall studies used the 60,964-cell split-inlet model, with full feed of 116.92 kg/s liquid and 80.69 kg/s steam.

At 25% feed with throughput collection, inventory fell only 0.30% over iterations 1080–1580, ending at 31.3571 kg (Figure 10). Minimum scaled continuity was $3.2056\times10^{-4}$.

A failed ramp command had left the model at reduced feed until iteration 1580. The corrected 2000-update ramp reached full feed at iteration 3580. Ramp continuity peaked at $1.1166\times10^{-2}$ and inventory reached 182.5178 kg.

![Residuals, bulk-liquid inventory and actual inlet loading during early development](../figures/results-described-early-development.png)

*Figure 10. Reduced-feed hold, loading ramp and full-feed development. A: ramp start; B: full feed and Coupled activation; C: EWF activation. Residuals, inventory and inlet loading are shown against solver iteration.*

<!-- Evidence: [selected case history](../../../experiments/phase-07-2a-wall-liquid-routing/stage-02-combined-ewf-roughness/case-history-N45606.md), [carrier residuals](../../../../PyAnsys/output/phase72a-lineage-N45606/20261005/carrier-residuals.csv) and [liquid histories](../../../../PyAnsys/output/phase72a-lineage-N45606/20261005/selected-lineage-histories.csv). -->

### 4.5. Full-feed control and mass balance

The smooth-wall, EWF-off Coupled continuation became the iteration-5586 comparison parent. Continuity fell and inventory approached 296 kg, but residual oscillations, outlet reverse flow and turbulent-viscosity limiting persisted.

Applied throughput-controlled absorber removal matched its 116.92 kg/s command, but another 24.3344 kg/s left through the steam outlet. The signed liquid boundary-plus-source remainder was therefore −24.3344 kg/s, or −20.81% of the feed. Source application was verified; conservation remained unresolved (Appendix A.15.2).

This developing field supplied a common parent for the following wall comparisons. Outlet-flow changes must be read with inventory and removal because the parent did not establish a closed liquid account.

<!-- Evidence: [full-feed control continuation](../../../experiments/phase-07-1a-absorber-convergence/roughness-family/r0-smooth-control/results.md), [baseline handoff](../../../experiments/phase-07-2a-wall-liquid-routing/baseline-control-handoff.md), [aligned native full-feed control histories](../../../../PyAnsys/output/phase71a_r0_control_run4/report-histories-batched.json) and [full-feed control accounting audit](../../../experiments/phase-07b-full-geometry-liquid-removal/convergence-investigation/shuhei-audit.md). -->

### 4.6. Roughness response from the common parent

The roughness response was non-monotonic (Figure 11). At $C_s=0.5$, 0.05 mm raised mean outlet flow by 21.21%; 8 mm reduced it by 44.09%, from 24.3715 to 13.6253 kg/s. Increasing $C_s$ lowered flow at both fixed heights.

![Effect of roughness height and constant on bulk-liquid steam-outlet flow](../figures/results-described-roughness.png)

*Figure 11. Roughness height gives a non-monotonic outlet response; the 8 mm case also loses bulk inventory. EWF is off. Means use iterations 8087–8586; dashed lines mark the smooth-wall reference.*

The 8 mm case lost 187.109 kg of bulk liquid. Oscillations and incomplete balances prevented an efficiency claim. The later 0.045 mm continuation also changed bulk advancement and film stepping, so it did not isolate roughness (Appendix A.12).

<!-- Evidence for the material-reference continuation: [Commercial-steel results](../../../experiments/phase-07-2a-wall-liquid-routing/stage-04-ewf-wall-parameters/commercial-steel/results.md). The 0.045 mm value is a selected reference, not a measured separator finish or a matched roughness-only comparison. -->

<!-- Evidence: [roughness-screen results and sample standard deviations](../../../experiments/phase-07-2a-wall-liquid-routing/roughness-family/results.md#matched-tail-comparison) and [comparison figure and provenance](../../../observations/07-wall-liquid-interaction.md). The source's later statement identifying the lowest outlet conflicts with its table; the table values are used here. -->

### 4.7. Accretion-enabled wall-film response

From common smooth-wall fields with throughput collection, the EWF package reduced mean outlet liquid by 92.88%, from 24.369 to 1.735 kg/s over iterations 8087–8586 (Figure 12). Phase accretion and coupled film equations were on; momentum feedback was off. Earlier trials are in Appendix A.11.

![Bulk-liquid steam-outlet histories with EWF off and the accretion-enabled package](../figures/results-described-film-outlet.png)

*Figure 12. Accretion reduces bulk-liquid outlet flow; changing inventories prevent a collection claim. Smooth-wall cases share the full-feed parent. Shading marks the final 500 updates; the film step is 10 µs.*

Bulk mass fell from 295.8536 to 63.0234 kg, while film mass reached only 3.1112 kg. The sections showed less liquid beside the wall (Figure 13). The film package changed liquid distribution, but changing inventories and an open combined liquid account prevent an efficiency claim.

![Matched bulk-liquid volume-fraction sections for the film-disabled continuation and accretion-enabled film case](../figures/bulk-comparison-described-film-treatment.png)

*Figure 13. Less bulk liquid remains beside the wall with accretion enabled. Both iteration-8586 centre sections use a shared 0–1 scale. Film storage and drainage are assessed separately.*

<!-- Evidence: [film-disabled and accretion-enabled comparison](../../../observations/07-wall-liquid-interaction.md), [wall-film-screen results and native sections](../../../experiments/phase-07-2a-wall-liquid-routing/ewf-family/results.md#native-phase-2-volume-fraction-contours--2026-09-23), [paired contour provenance](../figures/bulk-comparison-described-film-treatment.provenance.json) and [selected endpoint histories](../../../../PyAnsys/output/phase72a-lineage-N45606/20261005/selected-lineage-histories.csv). The film-disabled continuation's mean is from its separate comparison run and is not substituted for the roughness screen's smooth-wall mean. -->

The following tests changed collection and startup, then extended film development to examine drainage and storage.

### 4.8. Contact collection and combined model development

Shorter depletion time reduced collector inventory but increased removal variability (Appendix A.4). The combined continuation applied 10 µs contact collection, 0.5 mm roughness and a 1 µs film step together; their effects were not isolated.

At iteration 45606, film mass was 6.3600 kg after 120.769 ms. Final-1000-update drainage remained 9.98% below accretion, so the film continued to fill. Appendix A.15.3 and the linked case history retain the endpoints and detailed film account.

The shortened-startup comparison below tests whether introducing these treatments before loading reduces the ramp disturbance.

<!-- Evidence: [contact-strength screens](../../../experiments/phase-07-2a-wall-liquid-routing/stage-02-combined-ewf-roughness/results.md#all-liquid-contact-absorber-trial), [complete selected case history](../../../experiments/phase-07-2a-wall-liquid-routing/stage-02-combined-ewf-roughness/case-history-N45606.md) and [corrected film ledger](../../../../PyAnsys/output/phase72a-lineage-N45606/20261005/corrected-film-development-summary.json). The short strength-screen branch is distinct from the original-field continuation retained in Appendix A.9. -->

### 4.9. Shortened startup with early wall-film activation

Shortened startup introduced the combined wall and collection treatment before loading. Relative to the historical ramp, peak continuity fell by 70.15%, peak bulk + film inventory by 70.43%, and peak outward outlet liquid by 75.78% (Figure 14). Appendix A.17 retains the peak values.

![Historical and shortened startup at matched inlet-ramp progress](../figures/results-described-startup.png)

*Figure 14. Shortened startup reduces ramp peaks. (a) Continuity; (b) bulk + film inventory; (c) signed outlet liquid flow, negative outwards. The larger activation disturbance is excluded; dashed line: full feed; shading: subsequent hold.*

The excluded activation hold had a continuity peak of 0.10593, exceeding the historical ramp peak. At iteration 5080, bulk and film masses were 61.0549 and 0.1645 kg. Almost all film input was still stored (Appendix A.15.4). All ramp updates met the recorded inner-film tolerance, but 15 of the final 100 hold updates failed it. The recipe reduced loading peaks without establishing complete startup convergence (Appendix A.9.4).

The film was still young at full feed. The following continuation held the bulk fields fixed to examine its development under unchanged forcing.

<!-- Evidence: [shortened-startup results](../../../experiments/phase-07-2a-wall-liquid-routing/stage-03-shortened-reconstruction/early-ewf-startup/results.md), [audited metrics, native source checks and normalisation](../../../../PyAnsys/output/phase72a-stage3-early-ewf-server1/20261005/analysis-summary.json) and [native final histories for Appendix A.15.4](../../../../PyAnsys/output/phase72a-stage3-early-ewf-server1/20261005/final-histories.json). -->

### 4.10. Film development under frozen bulk fields

Film mass increased from 0.1645 kg at 3.5 ms to 9.5444 kg at 500 ms (Figure 15). After iteration 5080, bulk equations were frozen, leaving bulk inventory at 61.0549 kg and outward bulk-liquid outlet flow at 3.4300 kg/s. These fixed values describe held forcing; reciprocal bulk depletion was not calculated.

![Film inventory, accretion and drainage against accepted film time through 500 ms](../figures/results-film-development-reference500ms.png)

*Figure 15. Drainage develops while film inventory keeps rising under frozen bulk forcing. (a) Film mass; (b) input and drainage. Shading marks the final 10 ms; markers locate the Figure 16 snapshots and endpoint.*

The film spread and thickened over the lower and middle wall (Figure 16). Between 75.66 and 265.18 ms, wall area with thickness at least 0.10 mm increased from 40.34% to 61.98%; maximum thickness rose from 0.253 to 0.291 mm.

![Native wall-film thickness at three saved film times](../figures/wall-film-described-development.png)

*Figure 16. Film spreads and thickens over the lower and middle wall. Saved times and masses are labelled; all three views use the same camera and 0–0.30 mm scale, with bulk fields frozen.*

Over the final 10 ms at 500 ms, mean accretion was 81.121 kg/s and drainage was 69.600 kg/s, a 14.20% drainage deficit. Film storage, calculated from mass change divided by accepted film time, remained 11.528 kg/s. The late mass curve therefore continued to rise despite increasing drainage. Rates use interval-overlap weighting; Appendix A.17 retains the earlier 265.184 ms result and its different 1000-update window. Only the reference-speed arm reached the 500 ms endpoint (Appendix A.9).

Continued storage motivated tests of two further destinations: release back to droplets and direct removal from the lower wall.

<!-- Evidence: [selected film-development results, spatial metrics and reporting windows](../../../experiments/phase-07-2a-wall-liquid-routing/stage-03-shortened-reconstruction/early-ewf-startup/film-development/results.md), [500 ms campaign results](../../../experiments/phase-07-2a-wall-liquid-routing/stage-03-shortened-reconstruction/early-ewf-startup/inlet-speed-500ms/results.md), [selected reference-speed CSV](../../../../PyAnsys/output/phase72a-stage3-speed-sensitivity-server1/20261006/selected-film-history-reference.csv) and [Figure 15 provenance](../figures/results-film-development-reference500ms-provenance.json). -->

### 4.11. Added film-release mechanisms and direct drainage

A separate configuration enabled stripping, splashing, droplet collection and edge separation, retaining film-to-flow momentum feedback off. Its bulk fields and film forces differed from the 500 ms reference. After 4000 bulk updates, 50 ms of frozen-bulk development increased film mass from 0.2638 to 5.9070 kg. Final approximately 5 ms mean stripping and edge-separation rates were 64.56 and 51.87 kg/s, while storage was 80.81 kg/s. A separate splash contribution was unresolved.

Native film outflow was zero during that interval. Extending the film domain onto the lower wall then allowed a matched direct-sink test (Figure 17). Drain OFF and ON started from identical fields and 9.7526 kg total film, with the same expanded film domain and all bulk equations frozen. Over 15 ms, the sink reduced final lower-wall film by 70.32%. Native outflow also fell, so the 0.5088 kg direct removal increased combined external removal by only 0.1897 kg.

![Matched lower-wall film inventories and cumulative external removal with the direct drain off and on](../figures/results-direct-film-drain.png)

*Figure 17. Direct drainage reduces lower-wall film but partly replaces native outflow. Matched 15 ms OFF/ON test with bulk frozen: (a) lower-wall mass; (b) native outflow and direct removal.*

In the longer continuation, lower film stayed near 0.056 kg while upper film grew. The complete 405 ms record, including the rejected tail, contains 15.16 kg of direct removal and a 27.58 kg increase in film inventory. Storage was positive before the Courant-guard crossing. Local drainage therefore did not stop accumulation elsewhere. Particle release was internal transfer, while the sink removed liquid from the model (Appendix A.12).

The following numerical checks assess source application and film-step selection. The final mesh comparison addresses resolution separately.

<!-- Evidence: [release-mechanism continuation](../../../experiments/phase-07-2a-wall-liquid-routing/stage-04-ewf-wall-parameters/realism-continuation/feedback-off/results.md), [matched direct-drain test](../../../experiments/phase-07-2a-wall-liquid-routing/stage-04-ewf-wall-parameters/ewf-only-drain/results.md) and [long drain-ON development](../../../experiments/phase-07-2a-wall-liquid-routing/stage-04-ewf-wall-parameters/ewf-only-drain/long-development/results.md). -->

### 4.12. Numerical assessment of the selected development path

The shortened-startup contact source matched independently evaluated removal at all 3500 solved updates. A separate film-step test from identical fields showed that 20 µs passed local field and ledger checks over 2.5 ms, whereas 25 µs exceeded the 0.1% ledger-error limit.

These checks supported implementation and local step selection. Inner-film failures, unavailable residuals and continued storage prevented a convergence claim (Appendix A.9.4).

<!-- Evidence: [combined-history residual checks](../../../experiments/phase-07-2a-wall-liquid-routing/stage-02-combined-ewf-roughness/case-history-N45606.md#ewf-residuals), [shortened-startup source audit](../../../experiments/phase-07-2a-wall-liquid-routing/stage-03-shortened-reconstruction/early-ewf-startup/results.md#film-evidence-and-numerical-limits), [matched-time film-step assessment](../../../experiments/phase-07-2a-wall-liquid-routing/stage-03-shortened-reconstruction/early-ewf-startup/film-development/results.md), [local screen criteria](../../../experiments/phase-07-2a-wall-liquid-routing/stage-03-shortened-reconstruction/early-ewf-startup/film-development/setup.md), [20 µs comparison JSON](../../../../PyAnsys/output/phase72a-stage3-film-development-server1/20261005/mid-film-sensitivity-20us.json) and [25 µs comparison JSON](../../../../PyAnsys/output/phase72a-stage3-film-development-server1/20261005/mid-film-sensitivity-25us.json). -->

### 4.13. Final-model mesh sensitivity

The combined wall-film and collection model is being assessed on meshes containing 60,964, 342,609, 679,970, 997,604 and 2,596,657 fluid cells. The comparison asks whether wall-liquid distribution, film storage and removal change with resolution. A completed comparison at matched film ages and bulk-development states is not yet available; mesh independence remains unresolved.

> **Figure 18 reserved — one combined mesh comparison.** Present the most informative bulk-liquid or film-thickness views at shared scales, with a compact panel for the corresponding storage and removal response. Use common geometry, loading, wall treatment and reporting windows. Identify any unmatched or incomplete cases.

The final finding will distinguish spatial changes from continued film development and quantify their effect on liquid storage, collection and steam-outlet flow. Detailed case settings and balance terms belong in the supporting records. The vertical blocker and angled ramp change geometry and are assessed separately.

<!-- Layout allowance: one body page for this concise mesh comparison, one combined figure and its evidence-based finding. No result is assumed. Owners: [mesh-study context](../../../experiments/phase-09-mesh-convergence/CONTEXT.md), [mesh/model audit](../../../experiments/phase-09-mesh-convergence/setup.md), [wall-film plan](../../../experiments/phase-09-mesh-convergence/ewf-plan-v1.md), [680k continuation](../../../experiments/phase-09-mesh-convergence/server1-680k/setup.md). Reconcile final settings, accepted film ages and bulk-development states before selecting comparisons. -->


<!-- Source: Project/Final research report/Shuhei Report/draft/04-discussion-conclusions-and-future-work.md -->
# Part 4 — Discussion, conclusions and future work

## 5. Discussion

The results identify three linked model sensitivities: delivery to the wall, transfer into film and removal from the vessel. The discussion connects those responses to the collection question and examines the explanations that remain unresolved.

### 5.1. Mesh development changed the wall-liquid representation

The polyhedral–hexahedral workflow made wall refinement and coarse local testing more practical. This matters because the liquid path of interest occupies the wall region, where fine cross-wall spacing is needed to represent steep liquid-fraction gradients. The wall layers gave control over that spacing, with larger interior cells supporting less costly exploratory calculations. Reduced numerical smearing remains a hypothesis because transport error also depends on resolution, alignment and discretisation. ([Ansys, Inc., 2025c, §7.1.3.3](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/flu_ug_GridTypes.html))

The broader liquid-rich region in Figure 7 suggested that wall liquid was being represented differently. The finer absorber-free fields then placed much of the retained liquid near the wall and base while sending little through the steam outlet (Figure 9). These observations support the concern that a model which retains liquid away from steam also needs a route for its collection. Their later failure did not establish greater mesh accuracy or identify the cause of numerical breakdown.

Historical comparisons also changed inlet representation and preparation, and lacked matched inventory histories. The combined-model mesh study will test whether the wall-liquid fields, storage and removal rates persist across resolutions under one common model (Section 4.13). Residual reduction alone would not answer that question.

### 5.2. Inlet phase placement changes the wall-liquid starting condition

The thin liquid strip made the wall-rich feed assumption reproducible. Films in upstream piping provide a physical reason to test that placement, but do not establish the actual inlet profile. ([Pointon et al., 2009](https://publications.mygeoenergynow.org/grc/1028587.pdf))

With feed, mesh and controls fixed, wall-side placement increased retained liquid by 37.4%. Figure 8 also showed a more continuous liquid-rich wall band and deeper lower-region enrichment. This establishes that inlet placement changes the liquid distribution presented to the wall before EWF is added. Almost all supplied liquid still left through the steam outlet, so greater retention did not establish better collection. Later wall comparisons must preserve inlet placement to separate wall-treatment effects from a changed starting distribution, then follow that liquid through storage and removal.

<!-- Evidence for the development rationale: [Inlet interpretation](../../../experiments/phase-01-purnanto-baseline-and-inlet-exploration/interpretation.md); [author's inlet context](../Shuhei-Context.md#4-two-phase-inlet-make-the-assumed-liquid-arrangement-explicit). -->

### 5.3. The central development problem was the liquid collection route

The closed-bottom model's only exit was the steam outlet. Its liquid either accumulated or left with steam, whereas separator operation requires outward transport followed by brine discharge. Rising inventory was consistent with the missing drain, but changes over steady iterations did not give a physical filling rate. ([Zarrouk & Purnanto, 2015](https://doi.org/10.1016/j.geothermics.2014.05.009))

The absorber-free Coupled cases discharged 99.4–99.7% of liquid feed through the steam outlet. Their smaller mass imbalance accompanied an unsuitable liquid exit route. In a stationary closed-bottom calculation without another sink, conservation would require incoming liquid to leave through that outlet. Closure can therefore be numerically desirable while the available boundary routes remain inadequate for the separator question. This distinction explains why Coupled remained useful after a collector was added.

Opening the lower boundary let steam leave below. Full-geometry trials exposed dependence on a liquid seal and outlet control; neither an initially patched pool nor the tested pressure feedback established a maintained pool. Explicit collection in the truncated vessel allowed wall studies to continue. It represents transfer to an omitted pool without predicting its pressure, level or discharge response.

<!-- Evidence: [Full-geometry closure](../../../experiments/phase-06-full-geometry-with-brine-pool/conclusion.md); [initial-pool interpretation](../../../experiments/phase-01-purnanto-baseline-and-inlet-exploration/interpretation.md); historical boundary and water-seal discussion in [29 April, 04:04–06:36](../../../meetings/otter/2026-04-29-wk-7-steam-liquid-separator-analysis.md) and [17 August, 02:59–11:29](../../../meetings/otter/2026-08-17-fluid-dynamics-modeling-meeting.md). -->

### 5.4. Contact removal and staged startup made the model easier to develop

The contact absorber tied removal of mass and momentum to liquid present in the collector. This better matched transfer to the omitted pool than prescribing removal from inlet throughput alone.

Reduced feed allowed flow and collection to develop before full loading. The useful hold arose after a ramp command failed; the checked ramp turned that observation into a repeatable procedure. Activating the later contact and film treatments before loading reduced ramp peaks in continuity residual, combined bulk + film inventory and outlet flow by about 70%, 70% and 76%.

The shorter procedure supported finer-mesh repeats, but changed several settings together. The larger activation disturbance occurred before the ramp comparison, so the smaller ramp peaks do not describe the whole startup. The causes of that disturbance and later film-solver failures remain unresolved. Comparable starts require checked fields and film ages.

### 5.5. Wall treatment strongly controls the calculated liquid state

The non-monotonic roughness response in Figure 11 shows that increasing the roughness input did not consistently reduce outlet liquid. Small heights raised outlet liquid flow, while the largest tested height reduced it by 44.09%. Roughness changes the modelled near-wall momentum transfer; it does not supply a new liquid store or drain. ([Ansys, Inc., 2025k](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_th/x1-5720008.164.html)) One possible explanation is changed liquid transport or residence near the wall. A competing explanation is reduced liquid availability after bulk inventory depletion. The 8 mm case lost 187.109 kg during the continuation, so the latter explanation cannot be dismissed because the final outlet history became comparatively level. The wall-surface velocity report sampled the no-slip boundary and could not resolve the near-wall transport needed to distinguish these explanations.

The accretion-enabled film package changed the representation itself by adding surface storage and transport. Mean bulk-liquid outlet flow fell from 24.369 to 1.735 kg/s, and Figure 13 showed less bulk liquid beside the wall. However, bulk mass fell from 295.854 to 63.023 kg while film mass reached only 3.111 kg. The lower outlet flux and the new film inventory therefore do not account for the liquid destination by themselves. The unresolved bulk, source and film account prevents an efficiency interpretation.

These screens identify wall treatment as a major model sensitivity. A useful follow-up must distinguish increased delivery to the collector from depletion, surface storage and transfer back to droplets. It needs wall-adjacent fields and separate inventories and removal histories, rather than an outlet ranking alone. The 8 mm screen and later 0.045 mm material-reference continuation also used different bulk advancement and film stepping. Neither identified an optimum surface finish.

<!-- Evidence: [roughness inventory changes, competing depletion interpretation and wall-velocity report limit](../../../experiments/phase-07-2a-wall-liquid-routing/roughness-family/results.md#matched-tail-comparison); [selected wall-treatment comparison](../../../observations/07-wall-liquid-interaction.md). -->

### 5.6. Film development, release and drainage answer different parts of the same question

Longer histories answered the earlier question about patchy initial films by showing continued spreading and thickening. Between 75.66 and 265.18 ms, appreciable film coverage increased as well as maximum thickness (Figure 16). By 500 ms, drainage had developed to 69.60 kg/s, but input remained 81.12 kg/s and storage was still 11.53 kg/s over the final 10 ms (Figure 15). A wider visible film and substantial drainage can therefore coexist with continuing accumulation.

The bulk fields were frozen during this development, so the film responded to held forcing. Constant bulk inventory and outlet flux were imposed by that choice; reciprocal bulk depletion was not advanced. The run reveals how the film develops under those fields, while sustained coupled collection remains a separate question.

Later runs used different fields and film forces. Stripping and edge-separation records showed film liquid returning to droplets. Splashing was enabled but not measured separately. Release reduces film mass without necessarily removing liquid from the vessel: droplets may return to the wall, enter the collector or leave with steam. This reflects the film-entrainment problem in the literature and explains why wall capture alone cannot establish permanent collection. ([Rizaldy et al., 2016](https://www.researchgate.net/publication/310818568_LIQUID_CARRYOVER_IN_GEOTHERMAL_STEAM-WATER_SEPARATORS); [Ansys, Inc., 2025b](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_th/flu_th_ewf_sec_film_submodels.html))

The matched direct-drain test proved local film removal with bulk equations frozen (Figure 17). Lower-wall inventory fell by 70.32%, but the 0.5088 kg direct sink partly replaced native film outflow, which fell from 0.5302 to 0.2111 kg. Combined removal increased by only 0.1897 kg, close to the reduction in total film inventory. The sink changed the division between removal routes as well as adding removal. Its rate alone would therefore overstate the gain relative to the drain-OFF arm.

In the longer continuation, lower inventory stayed near 0.056 kg while almost all film growth occurred above it. Removal was active, yet input still exceeded the combined losses; upper storage was positive before the later Courant-guard failure. This supports a transport question as well as a local-drain question. It does not establish that downward motion was absent or isolate the cause of upper accumulation. Features that intercept circulating film or guide it towards the collector are specific design hypotheses. Their assessment must follow collection, steam-outlet liquid, storage and pressure loss together, because lower film mass could also result from greater release into steam.

<!-- Evidence: [identical-parent drain comparison and separate native outflow/direct sink account](../../../experiments/phase-07-2a-wall-liquid-routing/stage-04-ewf-wall-parameters/ewf-only-drain/results.md); [lower-region inventory, upper storage and pre-guard assessment](../../../experiments/phase-07-2a-wall-liquid-routing/stage-04-ewf-wall-parameters/ewf-only-drain/long-development/results.md). -->

<!-- Evidence for the early questions: [Initial EWF interpretation](../../../experiments/phase-04-ewf-wall-film-mechanisms/interpretation.md); [3 June, 12:29–13:29](../../../meetings/otter/2026-06-03-droplet-injection-simulation-review.md); [22 July, 06:40–07:58](../../../meetings/otter/2026-07-22-geothermal-simulation-analysis.md). -->

### 5.7. Contribution and the evidence needed for performance prediction

The contribution is a model-development approach that follows liquid through inlet placement, wall transport and collection. Checked collection and startup procedures enabled the comparisons; longer histories distinguished storage, release and drainage. Appendix B summarises the supported answers in Table B2.

Bulk-liquid flux, outlet quality and DPM escape fractions measure different quantities. Exact absorber tracking did not close the early balance, and a small film-ledger error did not establish whole-separator conservation. Each transfer must be followed and counted once.

High saved wall $y^+$ values, incomplete refinement assessment and omitted pool response limit performance prediction. Physical validation still requires matched operating conditions, measurement locations and uncertainty. ([NASA, 2021b](https://www.grc.nasa.gov/www/wind/valid/tutorial/valassess.html))

<!-- Add the final mesh-sensitivity finding from Section 4.13 here, in Table B2 and in the conclusions when verified. State which fields and rates changed with refinement and which mesh supports the intended use. No outcome is assumed. -->

## 6. Conclusions and future work

### 6.1. Conclusions

Liquid reaching the wall did not by itself establish collection. This study developed a geothermal separator CFD model by following where liquid enters, accumulates, transfers and leaves. Mesh and inlet investigations showed that the predicted wall-liquid distribution depended on its representation. In the matched inlet comparison, placing liquid beside the wall increased retained mass by 37.4%. Absorber-free cases exposed the missing collection route through accumulation or almost complete liquid discharge through the steam outlet.

A liquid-selective absorber and staged loading supplied common fields for wall studies. The contact treatment represented transfer of liquid mass and momentum to the omitted brine pool. The later combined startup reduced the peak continuity residual during the ramp by 70.15%, while retaining a separate activation disturbance.

Wall treatment strongly changed the predicted liquid state. The selected accretion-enabled film package reduced mean bulk-liquid outlet flow from 24.369 to 1.735 kg/s, alongside a large inventory change. Film calculations showed spreading, thickening and drainage, with storage still averaging 11.53 kg/s over the final 10 ms at 500 ms. The direct drain removed 0.5088 kg but increased combined external removal by only 0.1897 kg because it partly replaced native film outflow. Its removal alone therefore overstated the additional collection. Lower-wall collection could operate while film continued to accumulate above it.

The completed work establishes model sensitivity and checked collection and startup procedures. It also gives a specific reason to test designs that redirect wall liquid towards collection. Mesh sensitivity of the combined model remains unresolved. Sustained liquid accounting and physical validation are still needed before claiming improved separation efficiency or pressure-drop accuracy.

### 6.2. Future work

The next comparisons should test the explanations established here:

1. **Complete the mesh-sensitivity assessment.** Compare liquid distributions and rates using fixed geometry and model settings at matched film ages and bulk-development states. Follow up quantities that remain resolution-dependent.
2. **Complete the coupled liquid account.** Advance the bulk equations and track bulk, film and droplet transfers together. Separate external removal from internal transfers and repeat developed-film step checks.
3. **Separate startup and model effects.** Compare loading sequence, collector law and solver controls individually from common fields.
4. **Compare with measurements.** Match feed conditions and pressure and liquid-sampling locations to assess the model's use for design.

Initial design work now applies the wall-film findings to two features. A **vertical film blocker** is intended to intercept circulating liquid before it meets incoming steam. An **angled film ramp** is intended to guide that liquid towards lower collection. Both calculations have reached 150 ms film age; their final 100 ms used matching basic wall-film settings and 10 µs steps with bulk fields held fixed (Appendix A.14). Their meshes, initial flow fields and earlier film histories differ, so the results do not yet isolate a geometry effect or establish improved separation. The next comparison should follow collection, steam-outlet liquid, film storage and pressure loss from controlled baselines. Including film-release mechanisms will also test whether interception reduces renewed entrainment. Lower film inventory alone cannot distinguish collection from release into steam.

<!-- Design evidence: [vertical basic-film continuation](../../../experiments/phase-10-proposed-design/vertical-slit154k/basic-ewf-10us/results.md#150-ms-endpoint--13-october-2026), [angled-ramp continuation](../../../experiments/phase-10-proposed-design/angled-slit213k/results.md#150-ms-endpoint--13-october-2026), and [comparison controls and limits](../../../experiments/phase-10-proposed-design/setup.md). The earlier enhanced-film vertical endpoint is a separate calculation. -->
