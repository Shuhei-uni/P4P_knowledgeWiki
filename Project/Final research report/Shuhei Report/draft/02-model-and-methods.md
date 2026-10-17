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

A pressure-based solver with the Mixture model in Ansys Fluent 2025 R2 was used for bulk continuity, momentum, liquid fraction and algebraic slip. Steam was the primary phase and water the secondary phase. The RNG $k$–$\varepsilon$ model included swirl treatment and standard wall functions; gravity acted downwards. The energy equation was disabled; flashing, condensation and temperature-dependent properties were excluded. Table 1 gives the material values; Appendix A.1 records the controls ([Ansys, Inc., 2025d](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_th/flu_th_sec_multiphase_mixture.html)).

*Table 1. Fixed material properties verified for the throughput-controlled absorber model.*

| Phase | Density (kg/m³) | Dynamic viscosity (Pa·s) |
| --- | ---: | ---: |
| Vapour | 5.79743 | $1.52062\times10^{-5}$ |
| Liquid water | 881.211 | $1.45544\times10^{-4}$ |

The full-feed parent, combined contact endpoint and shortened-startup endpoint used Manninen slip, Schiller–Naumann drag and a liquid-phase diameter of 10 µm. This local-equilibrium slip model was held fixed during wall comparisons; its accuracy for concentrated wall liquid remained unverified. The liquid-phase diameter controls continuum slip, separately from DPM droplets and film (Appendix A.1).

#### 3.2.2. Wall roughness and wall-film representation

Wall roughness was included in the wall-friction treatment through the equivalent sand-grain height $k_s$ and roughness constant $C_s$ ([Ansys, Inc., 2025k](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_th/x1-5720008.164.html)). The tested values were sensitivity inputs, not measured surface properties. The wall treatment and unresolved settings are documented in Appendix A.10.

The Eulerian Wall Film (EWF) model solved surface mass and momentum equations, with accretion transferring bulk liquid into the film. Throughout the 500 ms reference run, the film momentum equation included gravity, gas shear, wall viscosity and momentum advection; native film-edge outflow provided the drainage route. Additional film forces and droplet interactions were disabled (Appendix A.9) ([Ansys, Inc., 2025e](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/flu_ug_ewf_sec_options.html)).

Later tests added pressure-gradient, spreading and surface-tension forces, droplet collection, splashing, stripping and edge separation. Particle impacts can cause splashing, while stripping and edge separation release film liquid as droplets. Changes in the bulk fields in these tests prevent the effects from being attributed to any single mechanism. Film-to-bulk momentum feedback was disabled in the selected continuations; this setting was distinct from numerical coupling of the film equations (Appendix A.12) ([Ansys, Inc., 2025b](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_th/flu_th_ewf_sec_film_submodels.html)).

### 3.3. Boundary conditions and liquid collection

#### 3.3.1. Enthalpy and the inlet phase mass flows

The reference feed had a mass flow rate of 197.61 kg/s, an enthalpy of 1600 kJ/kg and a pressure of 11.2 bar absolute. A calculation using saturated enthalpies gave a vapour quality of 0.408323. The inlet commands retained Purnanto's rounded phase mass flow rates in Table 2; Appendix A.7 gives the thermodynamic calculation ([Purnanto et al., 2013](https://www.researchgate.net/publication/269519626_CFD_MODELLING_OF_TWO-PHASE_FLOW_INSIDE_GEOTHERMAL_STEAM-WATER_SEPARATORS)).

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

Here, $\rho_L$, $\alpha_L$ and $\tau$ denote liquid density, liquid volume fraction and depletion time, respectively; $S_L$ has units of kg/(m³·s). The associated momentum and turbulence sources represented one-way capture. Appendices A.3–A.5 describe the implementation, source checks, depletion-time sensitivity and earlier throughput-controlled law ([Ansys, Inc., 2025a](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/flu_ug_bcs_sec_cell_zones.html)).

Bulk removal, film drainage and diagnostic-particle escape were separate routes. Early film drained where the active EWF wall ended. A later test extended EWF onto the lower wall and added a direct film mass sink with matching momentum removal and an assumed capture time of 1.5 ms. An isolated source check and matched 15 ms OFF/ON runs tested this sink with all bulk equations frozen (Appendix A.12).

### 3.4. Mesh and spatial discretisation

Fluent Meshing produced polyhedral–hexahedral meshes with wall-following layers for the expected liquid path. Reduced numerical diffusion remained a hypothesis dependent on resolution, alignment and discretisation ([Ansys, Inc., 2025c](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/flu_ug_GridTypes.html)).

The main mesh contained 60,964 cells. Appendix A.6 gives the spatial schemes, and Appendix A.10 gives the connectivity and wall fields. The mean main-wall $y^+$ ranged from approximately $2.0\times10^4$ to $3.4\times10^4$ across three saved states, so the wall-following topology did not establish fine wall resolution. Layer dimensions and solver mesh-quality measures remain unverified. Section 3.6 defines the separate mesh comparisons.

### 3.5. Numerical solution procedure

The original startup used Hybrid Initialisation with smooth walls, EWF disabled and throughput-controlled collection. A failed command kept the feed at 25% of full feed until iteration 1580. After the corrected 2000-update ramp, the solver was switched from SIMPLE to Coupled with Global Time Step. Warm-up and a 1000-update control produced the parent checkpoint at iteration 5586 (Appendix A.5).

The **developed parent** was a saved full-feed field selected following a review of residuals, inventories, flows and sources. It supplied common initial fields for wall comparisons, but retained a substantial liquid-balance error and did not establish convergence. For shortened startup, fields from iteration 1580 were reused without reinitialisation, and contact collection, 0.5 mm roughness, Coupled flow and EWF were enabled together, with the film initialised dry (Appendix A.16).

The Coupled algorithm solved pressure and momentum corrections together, while the Mixture volume fraction was solved separately. The coupling and pseudo-time settings changed together, so their individual effects were not isolated. In later film runs, bulk flow, turbulence, volume fraction and relative motion were frozen. Fluent's steady EWF procedure assumes a converged, frozen carrier flow; here, freezing the bulk allowed film development under fixed forcing without established bulk convergence ([Ansys, Inc., 2025i](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/flu_ug_sec_uns_solve_pvel_1.html); [2025j](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/flu_ug_sec_multiphase_solution.html); [2025g](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_th/flu_th_ewf_sec_sol_alg.html)).

The implicit beta algorithm did not provide inner residual reports. Equal-time fields and mass accounts provided local checks, but the absence of residual reports was not treated as evidence of convergence. Settings were also checked by saving and reopening (Appendix A.9).

### 3.6. Comparison design

Exploratory inlet, droplet and film tests guided later controlled comparisons (Appendix A.13). Wall screens started from a common parent. Startup and combined continuations tested procedures while changing several settings together (Appendix A.16). Roughness ranged from 0 to 8 mm; Appendix A.5 gives the $C_s$ variations and reporting windows.

The common parent provided the same inherited flow field at the start of each wall screen, reducing the influence of different preparation histories. Equal update horizons and reporting windows allowed the responses to the selected treatments to be compared. Because the parent was still developing, the comparison assessed those responses rather than equilibrium performance. The startup study asked a different question: whether the combined model could reach full feed with smaller loading disturbances. Matching ramp progress aligned inlet loading, while the activation hold provided a separate window to assess the disturbance from introducing the additional models.

The absorber-free mixed/split Coupled reconstructions held the mesh, feed and controls fixed, used fresh initialisation and ran for 10,000 updates. The historical tetrahedral comparison changed the mesh, inlet and preparation. The SIMPLE/Coupled reconstruction comparisons also changed pseudo-time and the $k$ scheme, so neither these comparisons nor the historical tetrahedral comparison isolated a single cause.

Finer absorber-free SIMPLE diagnostics compared 342,609-, 679,970- and 997,604-cell fields at iteration 3000. These developing solutions did not constitute a converged mesh study (Appendix A.2).

The final mesh study examined whether film distribution, storage and drainage persisted across resolutions after the combined wall-film and collection model had been introduced. The model used 0.045 mm roughness with film-to-flow momentum feedback disabled. Approximately 200 ms was chosen as a practical observation time because drainage on the 60k mesh had begun to level out in the author's assessment, although film inventory was still increasing. In Figure 7, the orange drainage curve changes slowly around 200 ms, but remains below the teal input curve. The purple accumulation rate stays above zero: liquid is still being added to the film inventory even though drainage is changing slowly. This distinction made approximately 200 ms a useful time to inspect the developing state, rather than a test of steady film. This choice provided a common film age for inspecting developing states; it did not assume film equilibrium. The earlier run used a different film configuration from Phase 9, so its drainage level and development timescale were a practical reference, not assumed transferable results.

![Earlier 60k film input, drainage and accumulation rates used to inform the observation-time choice](../figures/methods-coarse-film-time-reference.png)

*Figure 7. Coarse-mesh film behaviour behind the observation-time choice. Drainage rises rapidly and then changes more slowly around 200 ms, while positive accumulation indicates continued film storage. The earlier Stage 3 reference run used frozen bulk fields and different film settings from Phase 9. The dotted line marks the earlier 265.184 ms checkpoint, not the selected 195 ms comparison time. Reproduced from the working poster; Section 4.10 gives the associated film-development results.*

<!-- Source: working poster ppt/media/image18.png; original generator PyAnsys/scripts/analysis/build_wall_film_poster_card.py; selected Stage 3 nominal-speed history PyAnsys/output/phase72a-stage3-speed-sensitivity-server1/20261006/selected-film-history-reference.csv. Accumulation is the film-mass change divided by each film interval. The author supplied the approximately 200 ms selection rationale; no formal plateau criterion is claimed. -->

The approximate 200 ms rationale and the exact saved endpoint are distinct: the final Phase 9 comparison selected 195 ms, with bulk equations still frozen. All four completed meshes—60,964, 342,609, 679,970 and 997,604 cells—were compared at that film age (Section 4.13). Here, frozen bulk means that the surrounding steam–liquid flow field was held fixed while the wall film continued to evolve. Each film therefore developed under the retained flow field for its own mesh, rather than under one identical field shared by all meshes. Starting ages ranged from 0.700 to 0.900 ms. The 342k reference preceded its bulk-active adjustment, whereas the other three references were at the bulk-freeze boundary. The 2,596,657-cell mesh supplied only an initial-bulk reference with provisional film settings. Differences in preparation and retained fields prevent the comparison from isolating spatial discretisation error. The blocker and ramp address separate geometry questions.

<!-- Evidence: [mesh-study setup](../../../experiments/phase-09-mesh-convergence/setup.md); [wall-film plan](../../../experiments/phase-09-mesh-convergence/ewf-plan-v1.md). The observation-time rationale was supplied by the author during report revision on 17 October 2026; it is not a quantified plateau test. Selected endpoint evidence is recorded in the Phase 9 results dated 17 October 2026. -->

### 3.7. Data reduction and numerical assessment

Each reported value remained associated with its case, active equations and reporting window. Endpoints, means and residual minima were treated as distinct quantities. Inventories, outlet flows, collection and film-transfer rates were assessed alongside residuals and source checks. A fixed iteration horizon did not establish convergence. Appendix A.9 defines the numerical criteria and integration methods.

Fluent fluxes used a positive sign for flow into the domain. With EWF disabled and no other liquid transfer, the signed remainder (kg/s) was

$$
R_L=\sum_b\dot m_{L,b}+\dot m_{L,\mathrm{source,applied}}.
$$

The liquid source retained its negative sign for removal. The evaluated and applied removal represented the same sink, so the balance included only one removal term. Bulk-to-film accretion cancelled only in compatible combined accounts. Native mixture and phase-summed reports were assessed separately.

The early film balance compared integrated accretion with the sum of drainage and inventory change over accepted film time; Appendix A.9 defines the integration and normalised error. Later release mechanisms required separate transfer terms (Appendix A.12). When the bulk was frozen, reciprocal bulk depletion did not advance, so agreement within the film account could not establish conservation across the bulk and film.

Wall-screen comparisons used arithmetic means over the final 500 bulk updates; the 500 ms film run used overlap-weighted rates over the final 10 ms. The bulk-liquid outlet ratio used liquid feed as its denominator, whereas outlet dryness used total outlet flow (Section 2.2). Neither pathlines nor diagnostic-droplet fates replaced bulk-liquid fluxes. Residual scaling was checked for startup comparisons; residuals were not percentage mass imbalances ([NASA, 2021a](https://www.grc.nasa.gov/www/wind/valid/tutorial/iterconv.html)).

### 3.8. Experiment workflow and use of automation

The agent-assisted workflow made rapid, repeated experimentation a practical part of this project. OpenAI Codex, an AI coding assistant, helped translate proposed comparisons into case changes, Fluent runs and analysis. This depended on the research environment built around the agent: a connected knowledge base, durable experiment records, task-specific instructions called skills, and tools for controlling Fluent. Together, these formed the agent harness. They allowed each experiment to build on earlier work while I retained responsibility for scientific direction and interpretation.

**Scale and reuse.** The workflow enabled us to run 387 simulation cases across the project, covering outlet conditions, liquid removal, turbulence, wall roughness and wall-film behaviour.

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
