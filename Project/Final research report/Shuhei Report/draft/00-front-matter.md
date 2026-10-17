# Development of a geothermal separator CFD model: liquid transport, collection and wall-film behaviour

## Title page information

| Field | Information |
| --- | --- |
| Author | Shuhei Yokkaichi |
| Programme | Bachelor of Engineering (Honours), Engineering Science |
| Institution | The University of Auckland |
| Report type | Part IV Research Project Report |
| Supervisors | Sadiq Zarrouk and Maedeh Amirpour |
| Co-worker | Andy Tran |
| Draft date | 14 October 2026 |
| Student identification | 302558861; UPI: syok443 |
| Submission date | 18 October 2026 |

<!-- Names follow the supplied working poster. The supplied ESB title-page template includes supervisors and co-worker; this takes precedence here over the generic structuring handout's different cover-page advice. -->

## Abstract

Geothermal steam–water separators must collect liquid without allowing it to return to the steam. This study developed an existing computational fluid dynamics (CFD) model to examine how liquid moves through a separator and inform design improvements. The original model had no separate liquid discharge route and did not explicitly track the liquid film along the walls. Changes to inlet conditions, mesh resolution and startup procedures, together with added liquid removal and wall-film modelling, enabled these processes to be investigated.

Liquid-distribution plots revealed changes near the wall that were not apparent from outlet flow rates alone. Without a collection route, liquid continued to accumulate, showing that low liquid discharge through the steam outlet did not necessarily mean successful separation. Adding liquid removal and initially reducing the inlet flow produced a reported scaled continuity residual about 650 times lower and a retained liquid mass about 93% lower than an earlier case without removal. The residual comparison has unverified scaling equivalence, and the inventory contrast also reflects different inlet flow and mesh resolution. The lower residual levels and small inventory change during the reduced-feed hold supported further studies of wall roughness, film movement and drainage.

With the surrounding flow held fixed, the wall film was simulated for 500 ms. It spread across much of the separator and drainage became fairly steady, but stored liquid continued to increase. Removing film near the base reduced local accumulation while liquid still built up higher on the wall. Finer meshes showed more distinct film paths and less stored liquid and drainage, leaving the effect of mesh resolution unresolved.

These findings guided two design proposals: a vertical barrier to interrupt circulating wall liquid and an inclined ramp to guide it downwards. Predicted flow directions showed encouraging local changes, but improved liquid collection has not been demonstrated. Computational cost limited the simulated duration. The model now supports more detailed investigation of liquid collection; the next priorities are to establish whether film accumulation stops and whether the proposed designs improve drainage. A complete liquid mass balance and comparison with measurements remain necessary before using the model to predict separator performance.

## Declaration

*Unsigned draft using the supplied University template. The author must review and sign the declaration before submission.*

**Student**

I hereby declare that:

1. This report is the result of the final year project work carried out by my project partner (see cover page) and I under the guidance of our supervisor (see cover page) in the 2026 academic year at the Department Engineering Science and Biomedical Engineering, Faculty of Engineering, University of Auckland.
2. This report is not the outcome of work done previously.
3. This report is not the outcome of work done in collaboration, except that with a potential project sponsor (if any) as stated in the text.
4. This report is not the same as any report, thesis, conference article or journal paper, or any other publication or unpublished work in any format.

**Continuing-project statement.** The work builds on an inherited separator model and the published work of Purnanto et al. (2013). The present investigation developed liquid-collection and startup procedures, examined mesh and inlet assumptions, and studied wall roughness, film transport, release and drainage. The starting geometry and bulk modelling approach are identified as inherited work.

**Use of generative AI.** OpenAI Codex assisted with literature retrieval, coding and checking Fluent/PyFluent workflows, execution and recovery support, analysis, figure preparation and report drafting. Fluent performed the numerical calculations. The researcher directed the scientific scope and supplied the physical interpretation. Appendix B describes the division of work.

**Report word count:** to be inserted from the final assembled report.

**Signature and date:** to be completed by the author.

<!-- Prescribed wording: ../../ESB_part_IV_latex_report_template_v2/Declaration/ESB_declaration_online.tex. The declaration is not signed or represented as approved by this draft. -->

## Table of contents

| Report section | Draft location |
| --- | --- |
| 1. Introduction | [Part 1](01-introduction-and-literature-review.md#1-introduction) |
| 2. Literature review | [Part 1](01-introduction-and-literature-review.md#2-literature-review) |
| 3. Inherited model and operating basis | [Combined draft](02-03-model-development-methods-and-results.md#3-inherited-model-and-operating-basis) |
| 4. Model development and results | [Combined draft](02-03-model-development-methods-and-results.md#4-model-development-and-results) |
| 5. Discussion | [Part 4](04-discussion-conclusions-and-future-work.md#5-discussion) |
| 6. Conclusions and future work | [Part 4](04-discussion-conclusions-and-future-work.md#6-conclusions-and-future-work) |
| References | [References](05-references-and-appendices.md#references) |
| Appendix A. Supporting calculations and numerical checks | [Appendix A](05-references-and-appendices.md#appendix-a-supporting-calculations-and-numerical-checks) |
| Appendix B. Author contribution | [Appendix B](05-references-and-appendices.md#appendix-b-author-contribution) |

Page references will be generated during document layout.

## List of figures

| Figure | Subject |
| --- | --- |
| 1 | Single-flash geothermal plant |
| 2 | Conceptual liquid pathways examined in separate model configurations |
| 3 | Conceptual schematic of separator liquid paths: wall film, carryover, brine discharge ($\dot m_l$) and downstream brine collection ($\dot m_b$) |
| 4 | Outlet wetness and steam quality versus inlet steam velocity for three separator datasets. Left axis: outlet wetness; right axis: steam quality |
| 5 | Scrolled entry gives a higher calculated mean tangential velocity than tangential entry. (a) Inlet geometries; (b) tangential-velocity fields. Scrolled entry (labelled “lemniscate entrance” in the source) is on the left; tangential entry is on the right |
| 6 | Conceptual mechanisms by which steam shear releases droplets from a liquid film: (a) undercut and (b) roll-wave entrainment |
| 7 | Simplified computational domain and inlet arrangement: (a) spiral inlet, vessel and internal steam outlet; (b) wall-side liquid strip and adjacent vapour inlet. The brine pool and discharge pipe are omitted. Panel (b) shows the split inlet introduced in Section 4.1; the collector is introduced in Section 4.3 |
| 8 | Liquid volume fraction with mixed (a, c) and pure-split feed (b, d), at inlet height (a, b) and through the vessel centre (c, d) |
| 9 | Liquid inventory (left) and outlet liquid flow (right) on the 342k, 680k and 997k meshes |
| 10 | Historical tetrahedral and polyhedral–hexahedral mesh sections (a–b) and liquid-volume-fraction fields (c–d) |
| 11 | Residuals, liquid inventory and inlet loading during the reduced-feed hold, ramp and subsequent development |
| 12 | Liquid volume fraction and velocity vectors in an earlier absorber trial |
| 13 | Mean outlet liquid flow versus (a) roughness height and (b) roughness constant |
| 14 | Outlet liquid flow with EWF disabled and accretion enabled |
| 15 | Historical and shortened startup: (a) continuity residual, (b) liquid inventory and (c) outlet liquid flow |
| 16 | Film inventory, input and drainage through 500 ms |
| 17 | Wall-film thickness during development under fixed bulk forcing |
| 18 | Drain OFF/ON comparison: (a) lower-wall film mass and (b) external liquid removal |
| 19 | Wall-film thickness before development (top) and at 195 ms (bottom) |
| 20 | Bulk-liquid quantities, film inventory and lower-wall drain rate across meshes |
| 21 | Preliminary mixture-velocity vectors around (a) the vertical film blocker and (b) the angled film ramp |
| A1 | Pool inventory and bounded outlet-pressure control |

## List of main tables

| Table | Subject |
| --- | --- |
| 1 | Fixed material properties |
| 2 | Main boundary conditions |

Appendix tables retain the comparison controls, inlet calculation, mass-account checks, local film-step results and selected mesh values used to qualify the findings.

## Acknowledgements

I thank Sadiq Zarrouk and Maedeh Amirpour for their supervision and feedback as the modelling questions developed. Discussions with Sadiq also helped shape the wall-liquid design concepts. I thank Andy Tran for his collaboration as my project partner.

## Glossary of terms and abbreviations

| Term | Meaning in this report |
| --- | --- |
| BOC | Bottom-outlet cyclone |
| CFD | Computational fluid dynamics |
| Carrier | The Eulerian vapour and bulk-liquid flow fields through which discrete droplets are tracked |
| DPM | Discrete Phase Model; the Lagrangian representation of droplets |
| EWF | Eulerian Wall Film; the wall-based representation of liquid-film transport |
| IAPWS | International Association for the Properties of Water and Steam |
| IF97 | IAPWS industrial formulation for equilibrium water and steam properties |
| PyFluent | Python interface used to configure and command Ansys Fluent |
| Agent harness | Recorded workflow linking research questions, agent instructions, solver execution and analysis |
| RNG | Renormalisation group; used here in the RNG k–ε turbulence model |
| SIMPLE | Semi-Implicit Method for Pressure-Linked Equations |
| Bulk liquid | Liquid represented by the Eulerian secondary phase; excludes EWF inventory and discrete droplets |
| Vapour / bulk liquid | The primary vapour and secondary bulk-liquid phases in the selected Fluent carrier models |
| Accretion | Transfer of represented bulk liquid into the wall film |
| Stripping | Release of liquid from a film under gas forcing |
| Splashing | Production of secondary droplets during droplet impact on a film |
| Edge separation | Release of film liquid at a wall edge |
| Direct film drain | Local mass and momentum sink acting on lower-wall film storage |
| Incomplete trajectory | A tracked droplet with no completed terminal fate under the stated tracking controls |
| Absorber / virtual collector | A numerical liquid-removal treatment inside the truncated model; the two terms refer to the same model role |
| Native iteration | Fluent's recorded solver-update coordinate; it is not physical carrier-flow time |
| Film time | Time accumulated from the accepted EWF steps |
| Source term | A rate added to a transport equation; a negative mass source removes mass |
| Implicit source linearisation | Use of source derivatives within an equation solve to represent source dependence on the solved variable |
| Numerical stability | Observed finite and controlled behaviour over the stated calculation window |
| Iterative convergence | Active equations and relevant outputs meeting their declared settling conditions |
| Numerical accuracy | Accuracy of the computed solution of the stated model, assessed through numerical error and resolution evidence |
| Stiff source | A source with strong sensitivity to the solved variable, which can make an equation harder to solve |
| Numerical qualification | Assessment of a calculation against declared numerical, accounting and stationarity checks |
| Physical validation | Assessment against relevant physical observations for a stated use |

## Symbols

| Symbol | Meaning | Unit |
| --- | --- | --- |
| $\dot m$ | Mass-flow rate | kg/s |
| $M_b, M_f$ | Bulk-liquid and film inventories | kg |
| $M_c$ | Liquid mass in the collector | kg |
| $k_s$ | Modelled roughness height | m |
| $C_s$ | Roughness constant | — |
| $\alpha_L$ | Bulk-liquid volume fraction | — |
| $\rho_L$ | Liquid density | kg/m³ |
| $\boldsymbol u_L$ | Liquid velocity vector | m/s |
| $\boldsymbol u_m$ | Mixture velocity vector | m/s |
| $k$ | Shared turbulent kinetic energy | m²/s² |
| $\epsilon$ | Shared turbulence dissipation rate | m²/s³ |
| $S_L$ | Volumetric liquid mass source | kg/(m³·s) |
| $V_c$ | Collector region / its geometric volume | m³ |
| $\tau$ | Prescribed depletion time in the contact law | s |
| $h_f$ | Film thickness | m |
| $\tau_f$ | Direct film-drain capture time | s |
| $K_d$ | Direct film-drain removal coefficient | s⁻¹ |
