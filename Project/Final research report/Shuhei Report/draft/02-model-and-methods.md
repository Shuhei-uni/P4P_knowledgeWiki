# Part 2 — Model and methods

## 3. Model and methods

### 3.1. Computational domain and modelling scope

The model represented the upper separation region of a vertical cyclone: the spiral inlet, vessel walls and steam outlet. It omitted the brine pool and discharge. The bottom boundary remained a wall, so uncollected liquid could accumulate or leave through the steam outlet.

A numerical collector represented transfer into the omitted pool without opening a steam exit at the base. Full-geometry trials had not established stable drainage and pool control (Appendix A.13). Pool motion and downstream discharge remained outside the model. In absorber-free cases, collection was disabled in the same domain.

![Saved computational domain and pure-phase inlet split](../figures/model-domain-overview.png)

*Figure 6. Solved 60,964-cell domain (a) and pure-phase inlet split with a 6.754 mm wall-side liquid strip (b). The lower collector is a numerical sink; the brine pool and its discharge path are omitted.*

The mesh uses $y$ as the vertical coordinate, with the bottom near $y=0$ (exact bounds are given in Appendix A.1). The collector contains 715 cells selected by the centroid criterion $y\leq0.10$ m; the nodes of these cells extend to about $y=0.185$ m. The full-feed parent, combined contact endpoint and shortened-startup endpoint share mesh coordinates and connectivity. The steam-outlet label marks the computational boundary at the central pipe opening. Bulk flow used a steady formulation, while the film evolved on a separate clock. Bulk startup refers to numerical development through iterations, rather than physical startup time.

### 3.2. Physical model and assumptions

#### 3.2.1. Bulk steam–liquid flow

A pressure-based solver with the Mixture model in Ansys Fluent 2025 R2 was used for bulk continuity, momentum, liquid fraction and algebraic slip. Steam was the primary phase and water the secondary phase. The RNG $k$–$\varepsilon$ model included swirl treatment and standard wall functions; gravity acted downwards. The energy equation was disabled; flashing, condensation and temperature-dependent properties were excluded. Table 1 gives the material values; Appendix A.1 records the controls. ([Ansys, Inc., 2025d](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_th/flu_th_sec_multiphase_mixture.html))

*Table 1. Fixed material properties verified for the throughput-controlled absorber model.*

| Phase | Density (kg/m³) | Dynamic viscosity (Pa·s) |
| --- | ---: | ---: |
| Vapour | 5.79743 | $1.52062\times10^{-5}$ |
| Liquid water | 881.211 | $1.45544\times10^{-4}$ |

The full-feed parent, combined contact endpoint and shortened-startup endpoint used Manninen slip, Schiller–Naumann drag and a liquid-phase diameter of 10 µm. This local-equilibrium slip model was held fixed during wall comparisons; its accuracy for concentrated wall liquid remained unverified. The liquid-phase diameter controls continuum slip, separately from DPM droplets and film (Appendix A.1).

#### 3.2.2. Wall roughness and wall-film representation

Wall roughness was included in the wall-friction treatment through the equivalent sand-grain height $k_s$ and roughness constant $C_s$ ([Ansys, Inc., 2025k](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_th/x1-5720008.164.html)). The tested values were sensitivity inputs, not measured surface properties. The wall treatment and unresolved settings are documented in Appendix A.10.

The Eulerian Wall Film (EWF) model solved surface mass and momentum equations, with accretion transferring bulk liquid into the film. Throughout the 500 ms reference run, the film momentum equation included gravity, gas shear, wall viscosity and momentum advection; native film-edge outflow provided the drainage route. Additional film forces and droplet interactions were disabled (Appendix A.9). ([Ansys, Inc., 2025e](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/flu_ug_ewf_sec_options.html))

Later tests added pressure-gradient, spreading and surface-tension forces, droplet collection, splashing, stripping and edge separation. Particle impacts can cause splashing, while stripping and edge separation release film liquid as droplets. Changes in the bulk fields in these tests prevent the effects from being attributed to any single mechanism. Film-to-bulk momentum feedback was disabled in the selected continuations; this setting was distinct from numerical coupling of the film equations (Appendix A.12). ([Ansys, Inc., 2025b](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_th/flu_th_ewf_sec_film_submodels.html))

### 3.3. Boundary conditions and liquid collection

#### 3.3.1. Enthalpy and the inlet phase mass flows

The reference feed had a mass flow rate of 197.61 kg/s, an enthalpy of 1600 kJ/kg and a pressure of 11.2 bar absolute. A calculation using saturated enthalpies gave a vapour quality of 0.408323. The inlet commands retained Purnanto's rounded phase mass flow rates in Table 2; Appendix A.7 gives the thermodynamic calculation. ([Purnanto et al., 2013](https://www.researchgate.net/publication/269519626_CFD_MODELLING_OF_TWO-PHASE_FLOW_INSIDE_GEOTHERMAL_STEAM-WATER_SEPARATORS))

#### 3.3.2. Volumetric flow, inlet split and velocity

About 0.933% of the area of the 0.724 m square inlet was assigned to a 6.754 mm liquid strip. The strip was sized from the phase volumetric flow rates under an assumed common velocity. Appendix A.7 distinguishes the design properties from the solved densities and resulting phase velocities.

The strip replaced an exploratory inlet that mixed liquid and steam over half the opening. Liquid films in upstream pipes support testing liquid entry beside the wall ([Pointon et al., 2009](https://publications.mygeoenergynow.org/grc/1028587.pdf)), but complete segregation remained an imposed condition. The matched mixed/split comparison tested the consequences of the inlet split.

#### 3.3.3. Fluent boundary implementation

In the wall-treatment calculations, pure liquid and vapour entered normal to their respective inlets (Table 2). The operating pressure was 0 Pa, so the outlet gauge pressure equalled the absolute pressure; the inlet pressure was calculated. Appendices A.6 and A.2 give the turbulence and backflow inputs and the reconstruction differences.

*Table 2. Main boundary conditions. Reduced feed was 25% of full feed, with the phase mass ratio retained.*

| Boundary | Condition | Full feed | Reduced feed |
| --- | --- | ---: | ---: |
| Liquid inlet | Liquid mass-flow inlet | 116.9200 kg/s | 29.2300 kg/s |
| Vapour inlet | Vapour mass-flow inlet | 80.6900 kg/s | 20.1725 kg/s |
| Steam outlet | Gauge pressure | 1.120 MPa | Same |
| Vessel and bottom | Stationary, no-slip walls | Selected roughness/film treatment | As defined for startup |

#### 3.3.4. Contact-based absorber

The early absorber prescribed a total removal rate based on inlet throughput and distributed that removal according to the liquid present in the collector. The later contact absorber instead responded to local liquid inventory, without an inlet-throughput cap or a direct vapour mass sink:

$$
S_L=-\frac{\rho_L\alpha_L}{\tau},\qquad \tau=10^{-5}\ \mathrm{s}.
$$

Here, $\rho_L$, $\alpha_L$ and $\tau$ denote liquid density, liquid volume fraction and depletion time, respectively; $S_L$ has units of kg/(m³·s). The associated momentum and turbulence sources represented one-way capture. Appendices A.3–A.5 describe the implementation, source checks, depletion-time sensitivity and earlier throughput-controlled law. ([Ansys, Inc., 2025a](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/flu_ug_bcs_sec_cell_zones.html))

Bulk removal, film drainage and diagnostic-particle escape were separate routes. Early film drained where the active EWF wall ended. A later test extended EWF onto the lower wall and added a direct film mass sink with matching momentum removal and an assumed capture time of 1.5 ms. An isolated source check and matched 15 ms OFF/ON runs tested this sink with all bulk equations frozen (Appendix A.12).

### 3.4. Mesh and spatial discretisation

Fluent Meshing produced polyhedral–hexahedral meshes with wall-following layers for the expected liquid path. Reduced numerical diffusion remained a hypothesis dependent on resolution, alignment and discretisation. ([Ansys, Inc., 2025c](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/flu_ug_GridTypes.html))

The main mesh contained 60,964 cells. Appendix A.6 gives the spatial schemes, and Appendix A.10 gives the connectivity and wall fields. The mean main-wall $y^+$ ranged from approximately $2.0\times10^4$ to $3.4\times10^4$ across three saved states, so the wall-following topology did not establish fine wall resolution. Layer dimensions and solver mesh-quality measures remain unverified. Section 3.6 defines the separate mesh comparisons.

### 3.5. Numerical solution procedure

The original startup used Hybrid Initialisation with smooth walls, EWF disabled and throughput-controlled collection. A failed command kept the feed at 25% of full feed until iteration 1580. After the corrected 2000-update ramp, the solver was switched from SIMPLE to Coupled with Global Time Step. Warm-up and a 1000-update control produced the parent checkpoint at iteration 5586 (Appendix A.5).

The **developed parent** was a saved full-feed field selected following a review of residuals, inventories, flows and sources. It supplied common initial fields for wall comparisons, but retained a substantial liquid-balance error and did not establish convergence. For shortened startup, fields from iteration 1580 were reused without reinitialisation, and contact collection, 0.5 mm roughness, Coupled flow and EWF were enabled together, with the film initialised dry (Appendix A.16).

The Coupled algorithm solved pressure and momentum corrections together, while the Mixture volume fraction was solved separately. The coupling and pseudo-time settings changed together, so their individual effects were not isolated. In later film runs, bulk flow, turbulence, volume fraction and relative motion were frozen. Fluent's steady EWF procedure assumes a converged, frozen carrier flow; here, freezing the bulk allowed film development under fixed forcing without established bulk convergence. ([Ansys, Inc., 2025i](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/flu_ug_sec_uns_solve_pvel_1.html); [2025j](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/flu_ug_sec_multiphase_solution.html); [2025g](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_th/flu_th_ewf_sec_sol_alg.html))

The implicit beta algorithm did not provide inner residual reports. Equal-time fields and mass accounts provided local checks, but the absence of residual reports was not treated as evidence of convergence. Settings were also checked by saving and reopening (Appendix A.9).

### 3.6. Comparison design

Exploratory inlet, droplet and film tests guided later controlled comparisons (Appendix A.13). Wall screens started from a common parent. Startup and combined continuations tested procedures while changing several settings together (Appendix A.16). Roughness ranged from 0 to 8 mm; Appendix A.5 gives the $C_s$ variations and reporting windows.

The common parent provided the same inherited flow field at the start of each wall screen, reducing the influence of different preparation histories. Equal update horizons and reporting windows allowed the responses to the selected treatments to be compared. Because the parent was still developing, the comparison assessed those responses rather than equilibrium performance. The startup study asked a different question: whether the combined model could reach full feed with smaller loading disturbances. Matching ramp progress aligned inlet loading, while the activation hold provided a separate window to assess the disturbance from introducing the additional models.

The absorber-free mixed/split Coupled reconstructions held the mesh, feed and controls fixed, used fresh initialisation and ran for 10,000 updates. The historical tetrahedral comparison changed the mesh, inlet and preparation. The SIMPLE/Coupled reconstruction comparisons also changed pseudo-time and the $k$ scheme, so neither these comparisons nor the historical tetrahedral comparison isolated a single cause.

Finer absorber-free SIMPLE diagnostics compared 342,609-, 679,970- and 997,604-cell fields at iteration 3000. These developing solutions did not constitute a converged mesh study (Appendix A.2).

The final mesh study is designed to compare five resolutions using the combined wall-film and collection model, with 0.045 mm roughness and film-to-flow momentum feedback disabled (Section 4.13). The blocker and ramp address separate geometry questions. Mesh independence remains unresolved.

<!-- Evidence: [mesh-study setup](../../../experiments/phase-09-mesh-convergence/setup.md); [wall-film plan](../../../experiments/phase-09-mesh-convergence/ewf-plan-v1.md). Reconcile final settings and executed endpoints before completing the reserved result. -->

### 3.7. Data reduction and numerical assessment

Each reported value remained associated with its case, active equations and reporting window. Endpoints, means and residual minima were treated as distinct quantities. Inventories, outlet flows, collection and film-transfer rates were assessed alongside residuals and source checks. A fixed iteration horizon did not establish convergence. Appendix A.9 defines the numerical criteria and integration methods.

Fluent fluxes used a positive sign for flow into the domain. With EWF disabled and no other liquid transfer, the signed remainder (kg/s) was

$$
R_L=\sum_b\dot m_{L,b}+\dot m_{L,\mathrm{source,applied}}.
$$

The liquid source retained its negative sign for removal. The evaluated and applied removal represented the same sink, so the balance included only one removal term. Bulk-to-film accretion cancelled only in compatible combined accounts. Native mixture and phase-summed reports were assessed separately.

The early film balance compared integrated accretion with the sum of drainage and inventory change over accepted film time; Appendix A.9 defines the integration and normalised error. Later release mechanisms required separate transfer terms (Appendix A.12). When the bulk was frozen, reciprocal bulk depletion did not advance, so agreement within the film account could not establish conservation across the bulk and film.

Wall-screen comparisons used arithmetic means over the final 500 bulk updates; the 500 ms film run used overlap-weighted rates over the final 10 ms. The bulk-liquid outlet ratio used liquid feed as its denominator, whereas outlet dryness used total outlet flow (Section 2.2). Neither pathlines nor diagnostic-droplet fates replaced bulk-liquid fluxes. Residual scaling was checked for startup comparisons; residuals were not percentage mass imbalances. ([NASA, 2021a](https://www.grc.nasa.gov/www/wind/valid/tutorial/iterconv.html))

### 3.8. Experiment workflow and use of automation

The experimental workflow followed the cycle question → bounded comparison → implementation check → Fluent solve → interpretation → next question. The researcher set the scientific scope and interpreted the findings. Task-specific agent instructions, Python and PyFluent supported execution. Native reports, transcripts and reopened case/data pairs recorded what ran. This workflow supported repeatable tests and recovery; numerical and physical assessments remained separate. Appendix B links these records.