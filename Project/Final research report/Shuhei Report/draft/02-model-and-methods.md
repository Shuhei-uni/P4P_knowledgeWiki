# Part 2 — Model and methods

## 3. Model and methods

### 3.1. Computational domain and modelling scope

The model represented the upper separation region of a vertical cyclone: spiral inlet, vessel walls and steam outlet. It omitted the brine pool and discharge. The bottom remained a wall, so uncollected liquid could accumulate or leave through the steam outlet.

A numerical collector represented transfer into the omitted pool without opening a steam exit at the base. Full-geometry trials had not established stable drainage and pool control (Appendix A.13). Pool motion and downstream discharge remained outside the model. Absorber-free cases disabled collection in the same domain.

![Saved computational domain and pure-phase inlet split](../figures/model-domain-overview.png)

*Figure 5. Saved 60,964-cell domain (a) and inlet split (b). The 6.754 mm liquid strip lies beside the vessel wall. The 715-cell collector was selected by centroid position, $y\leq0.10$ m; its nodes extend to approximately $y=0.185$ m. Colours identify boundaries and the collector. The full-feed parent, combined contact endpoint and shortened-startup endpoint share coordinates and connectivity.*

The mesh uses vertical $y$, with the bottom near $y=0$ (exact bounds in Appendix A.1). The steam-outlet label marks the computational boundary at the central pipe opening. Bulk flow used a steady formulation, while film evolved on a separate clock. Bulk startup described numerical development through iterations, not physical startup time.

### 3.2. Physical model and assumptions

#### 3.2.1. Bulk steam–liquid flow

Ansys Fluent 2025 R2 used a pressure-based solver with absolute velocity. Steam was primary and liquid water secondary. Mixture solved bulk continuity and momentum, transported liquid volume fraction and calculated relative phase motion through algebraic slip. RNG $k$–$\varepsilon$ used differential-viscosity and swirl options with standard wall functions. Gravity acted in negative $y$ at 9.81 m/s². Energy was disabled, excluding flashing, condensation and temperature-dependent properties. Table 2 gives material values. ([Ansys, Inc., 2025d](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_th/flu_th_sec_multiphase_mixture.html))

*Table 2. Fixed material properties verified for the throughput-controlled absorber model.*

| Phase | Density (kg/m³) | Dynamic viscosity (Pa·s) |
| --- | ---: | ---: |
| Vapour | 5.79743 | $1.52062\times10^{-5}$ |
| Liquid water | 881.211 | $1.45544\times10^{-4}$ |

The three states identified in Figure 5 used Manninen slip, Schiller–Naumann drag and 10 µm liquid-phase diameter. This local-equilibrium slip model was held fixed during wall comparisons; its accuracy for concentrated wall liquid remained unverified. The diameter controls continuum slip, separately from DPM droplets and film (Appendix A.1).

#### 3.2.2. Wall roughness and wall-film representation

Roughness changed wall friction through equivalent sand-grain height $k_s$ and constant $C_s$. Tested values were sensitivity inputs, not measured surface properties. The wall treatment and unresolved settings are documented in Appendix A.10. ([Ansys, Inc., 2025k](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_th/x1-5720008.164.html))

Eulerian Wall Film (EWF) solved film mass and momentum on selected walls. Phase accretion transferred bulk liquid into the film. Early cases, including development to 500 ms, included gravity, gas shear, wall-viscous resistance and momentum advection. Film pressure-gradient, spreading and surface-tension forces were off, as were droplet collection, splashing, stripping and droplet edge separation. Native film-edge outflow remained active. ([Ansys, Inc., 2025e](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/flu_ug_ewf_sec_options.html))

Later tests enabled those forces and droplet mechanisms. Stripping releases film liquid under gas forcing; splashing creates secondary droplets on impact; edge separation releases liquid at wall edges. These tests used different developed bulk fields, so their comparison with the early run did not isolate one mechanism. Film-to-bulk momentum feedback stayed off. Coupling the film equations was a separate numerical choice (Appendices A.9 and A.12). ([Ansys, Inc., 2025b](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_th/flu_th_ewf_sec_film_submodels.html))

### 3.3. Boundary conditions and liquid collection

#### 3.3.1. Enthalpy and the inlet phase mass flows

The reference feed was 197.61 kg/s at 1600 kJ/kg and 11.2 bar absolute. Saturated enthalpies gave vapour quality $x_V=(h-h_{L,\mathrm{sat}})/(h_{V,\mathrm{sat}}-h_{L,\mathrm{sat}})=0.408323$. Fixed inlet commands retained Purnanto's rounded **80.69 kg/s vapour and 116.92 kg/s liquid**. Appendix A.7 gives the calculation and properties. ([Purnanto et al., 2013](https://www.researchgate.net/publication/269519626_CFD_MODELLING_OF_TWO-PHASE_FLOW_INSIDE_GEOTHERMAL_STEAM-WATER_SEPARATORS))

#### 3.3.2. Volumetric flow, inlet split and velocity

The 0.724 m square inlet assigned about 0.933% of its area to a 6.754 mm liquid strip. It was sized from phase volume flows under an assumed common velocity. With Table 2's densities, the retained mass commands gave mean normal velocities of approximately 27.134 m/s for liquid and 26.803 m/s for vapour. Appendix A.7 distinguishes the original design densities from the solved material values.

The strip replaced an exploratory inlet that mixed liquid and steam over half the opening. Upstream pipe films support testing liquid entry beside the wall; complete segregation remained imposed. The matched mixed/split comparison tested its consequences. ([Pointon et al., 2009](https://publications.mygeoenergynow.org/grc/1028587.pdf))

#### 3.3.3. Fluent boundary implementation

The main wall-treatment calculations admitted pure liquid at `liquidinlet` and pure vapour at `steaminlet`, normal to both boundaries (Table 3). Operating pressure was 0 Pa; outlet gauge pressure therefore equalled absolute pressure. Inlet pressure was calculated. Turbulence used intensity and hydraulic diameter, with 2.11% intensity. Appendix A.6 gives diameters/backflow inputs and Appendix A.2 reconstruction differences.

*Table 3. Main boundary conditions. Reduced feed was 25% of full feed, with the phase mass ratio retained.*

| Boundary | Condition | Full feed | Reduced feed |
| --- | --- | ---: | ---: |
| Liquid inlet | Liquid mass-flow inlet | 116.9200 kg/s | 29.2300 kg/s |
| Vapour inlet | Vapour mass-flow inlet | 80.6900 kg/s | 20.1725 kg/s |
| Steam outlet | Gauge pressure | 1.120 MPa | Same |
| Vessel and bottom | Stationary, no-slip walls | Selected roughness/film treatment | As defined for startup |

#### 3.3.4. Contact-based absorber

The later contact absorber removed liquid present in collector cells without an inlet-throughput cap or direct vapour mass sink:

$$
S_L=-\frac{\rho_L\alpha_L}{\tau},\qquad \tau=10^{-5}\ \mathrm{s}.
$$

Here, $\rho_L$, $\alpha_L$ and $\tau$ are liquid density, volume fraction and depletion time; $S_L$ has units kg/(m³·s). The compiled source used $\max(\alpha_L,0)$. Momentum removal used $S_L\boldsymbol u_L$ at liquid velocity; turbulence sources used $S_Lk$ and $S_L\varepsilon$. These separate transport sources represented one-way capture. Appendix A.3 gives hooks, derivatives and applied-source checks; A.4 gives depletion-time sensitivity. Earlier screens used the throughput-controlled law in A.5. ([Ansys, Inc., 2025a](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/flu_ug_bcs_sec_cell_zones.html))

Bulk removal, film drainage and diagnostic-particle escape were separate routes. Early film drained where the active EWF wall ended. A later test extended EWF onto the lower wall and added a direct film mass sink with matching momentum removal and assumed 1.5 ms capture time. An isolated source check and matched 15 ms OFF/ON runs tested it with all bulk equations frozen (Appendix A.12).

### 3.4. Mesh and spatial discretisation

Fluent Meshing produced polyhedral–hexahedral meshes with wall-following layers for the expected liquid path. Reduced numerical diffusion remained a hypothesis dependent on resolution, alignment and discretisation. ([Ansys, Inc., 2025c](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/flu_ug_GridTypes.html))

The main mesh contained 60,964 cells. Appendix A.6 gives spatial schemes; Appendix A.10 gives connectivity and wall fields. Mean main-wall $y^+$ was approximately $2.0\times10^4$–$3.4\times10^4$ across three saved states, so wall-following topology did not establish fine wall resolution. Layer dimensions and solver mesh-quality measures remain unverified. Section 3.6 defines the separate mesh comparisons.

### 3.5. Numerical solution procedure

Original startup used Hybrid Initialisation, smooth walls, EWF off and throughput-controlled collection. A failed command left 25% feed to iteration 1580. The corrected procedure increased both phase commands over 2000 updates. At full feed, SIMPLE changed to Coupled with Global Time Step. After warm-up, a separate 1000-update control supplied the iteration-5586 parent (Appendix A.5).

The **developed parent** was selected after reviewing residuals, inventories, flows and sources, without claiming convergence. Shortened startup reused iteration-1580 fields without reinitialisation and enabled contact collection, 0.5 mm roughness, Coupled flow and dry film together (Appendix A.16).

Coupled solved pressure and momentum corrections together, with Mixture volume fraction solved separately. Coupling and pseudo-time changed together, so their individual effects were not isolated. Later film runs froze bulk flow, turbulence, volume fraction and relative motion. Fluent's steady EWF procedure assumes a converged frozen carrier; here the freeze allowed development under fixed forcing before bulk convergence was established. ([Ansys, Inc., 2025i](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/flu_ug_sec_uns_solve_pvel_1.html); [2025j](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/flu_ug_sec_multiphase_solution.html); [2025g](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_th/flu_th_ewf_sec_sol_alg.html))

The implicit beta algorithm lacked inner residual reports. Equal-time fields and mass accounts supplied local checks; missing residuals were not passes. Save/reopen checked settings (Appendix A.9).

### 3.6. Comparison design

Exploratory inlet, droplet and film tests guided later controlled comparisons (Appendix A.13). Wall screens started from a common parent. Startup and combined continuations changed several settings together and tested procedures (Appendix A.16). Roughness ranged from 0 to 8 mm; $C_s$ variations and reporting windows are given in Appendix A.5.

Absorber-free mixed/split Coupled reconstructions held mesh, feed and controls fixed, with fresh initialisation and 10,000 updates. The historical tetrahedral comparison changed mesh, inlet and preparation. SIMPLE/Coupled reconstruction comparisons also changed pseudo-time and the $k$ scheme, so neither isolated one cause.

Finer absorber-free SIMPLE diagnostics compared 342,609-, 679,970- and 997,604-cell fields at iteration 3000. These developing solutions were not a converged mesh study (Appendix A.2).

Phase 9 compares the combined model, with 0.045 mm roughness and momentum feedback off, across five baseline resolutions. Section 4.13 specifies the planned film-age and bulk-development comparison. Blocker and ramp geometries address separate design questions; mesh independence remains unresolved.

<!-- Evidence: [Phase 9 setup](../../../experiments/phase-09-mesh-convergence/setup.md); [EWF Plan v1](../../../experiments/phase-09-mesh-convergence/ewf-plan-v1.md). Reconcile final settings and executed endpoints before completing the reserved result. -->

### 3.7. Data reduction and numerical assessment

Each value retained its case, active equations and reporting window. Endpoints, means and residual minima were distinct. Inventories, outlet flows, collection and film-transfer rates were assessed with residuals and source checks. A fixed iteration horizon did not establish convergence. Appendix A.9 defines the numerical criteria and integration methods.

Fluent fluxes were positive into the domain. With EWF off and no other liquid transfer, the signed remainder (kg/s) was

$$
R_L=\sum_b\dot m_{L,b}+\dot m_{L,\mathrm{source,applied}}.
$$

The source retained its negative removal sign. Evaluated and applied removal described the same sink, so only one entered the balance. Bulk-to-film accretion cancelled only in compatible combined accounts. Native mixture and phase-summed reports were assessed separately.

Early film cases had only accretion input: rate $A_i$ over accepted increment $\Delta t_i$. With outflow increment $\Delta D_f$ and inventory change $\Delta M_f$, the film remainder and percentage error were

$$
E_f=\Delta M_f+\Delta D_f-\sum_i A_i\Delta t_i,\qquad
e_f=100\frac{|E_f|}{\left|\sum_i A_i\Delta t_i\right|}.
$$

Later mechanisms required extra terms (Appendix A.12). With bulk frozen, reciprocal bulk depletion did not advance; film-account agreement could not establish combined conservation.

Wall screens used final-500 arithmetic means; the 500 ms film run used overlap-weighted final-10-ms rates. The bulk-liquid outlet ratio used liquid feed as denominator; outlet dryness used total outlet flow (Section 2.2). Neither pathlines nor diagnostic-droplet fates replaced bulk-liquid fluxes. Residual scaling was checked for startup comparisons; residuals were not percentage mass imbalances. ([NASA, 2021a](https://www.grc.nasa.gov/www/wind/valid/tutorial/iterconv.html))

### 3.8. Experiment workflow and use of automation

The cycle was question → bounded comparison → implementation check → Fluent solve → interpretation → next question. The researcher set scientific scope and interpreted findings. Task-specific agent instructions, Python and PyFluent supported execution. Native reports, transcripts and reopened case/data pairs recorded what ran. This workflow supported repeatable tests and recovery; numerical and physical assessments remained separate. Appendix B links the records.
