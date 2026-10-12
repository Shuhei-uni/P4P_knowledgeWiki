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
| Draft date | 11 October 2026 |
| Student identification | To be entered by the author |
| Submission date | To be entered by the author |

<!-- Names follow the supplied working poster. The supplied ESB title-page template includes supervisors and co-worker; this takes precedence here over the generic structuring handout's different cover-page advice. -->

## Abstract

Geothermal separators must move liquid away from steam and provide a route for its collection and discharge. This study developed an existing computational fluid dynamics model of a vertical steam–water separator, focusing on how liquid moves between the bulk flow, vessel wall and collector. The simplified geometry omitted the lower brine-discharge path. A polyhedral–hexahedral mesh, explicit inlet phase placement, numerical liquid collection and staged startup supported successive investigations of wall roughness and Eulerian Wall Film.

The revised mesh provided wall-following refinement and showed changed wall-liquid fields. With the same mesh and numerical package, wall-side inlet placement increased retained liquid by 37.4% relative to mixed feed. Absorber-free calculations exposed the collection problem through increasing lower-vessel liquid inventory or discharge of almost the entire liquid feed through the steam outlet. A liquid-selective collector and reduced-feed startup then supplied common fields for wall-treatment comparisons. A later combined startup reduced the ramp continuity peak by 70.15%. Wall treatment strongly changed the calculated liquid state: the selected accretion-enabled film package reduced mean bulk-liquid steam-outlet flow from 24.369 to 1.735 kg/s, alongside substantial inventory changes.

Under prescribed bulk forcing, film spread and thickened over the lower and middle wall. At 500 ms, film input and drainage were 81.12 and 69.60 kg/s, with continued storage of 11.53 kg/s. Later configurations added stripping, splashing and edge separation. A matched direct-film-drain test reduced lower-wall film inventory by 70.32%, while a longer continuation showed continuing upper-wall accumulation despite active removal below.

The study establishes a collection and startup method and shows why wall capture, film release and drainage must be considered together. These findings guide further model development and proposed features that direct wall liquid towards collection. Open combined balances, developing fields and incomplete resolution and physical assessment limit the results to model-development evidence; validated efficiency and pressure-loss predictions remain future work.

## Declaration

*Unsigned draft using the supplied University template. The author must review and sign the declaration before submission.*

**Student**

I hereby declare that:

1. This report is the result of the final year project work carried out by my project partner (see cover page) and I under the guidance of our supervisor (see cover page) in the 2026 academic year at the Department Engineering Science and Biomedical Engineering, Faculty of Engineering, University of Auckland.
2. This report is not the outcome of work done previously.
3. This report is not the outcome of work done in collaboration, except that with a potential project sponsor (if any) as stated in the text.
4. This report is not the same as any report, thesis, conference article or journal paper, or any other publication or unpublished work in any format.

**Continuing-project statement.** The work builds on an inherited separator model and the published work of Purnanto et al. (2013). The present investigation developed liquid-collection and startup procedures, examined mesh and inlet assumptions, and studied wall roughness, film transport, release and drainage. The starting geometry and bulk modelling approach are identified as inherited work.

**Use of generative AI.** OpenAI Codex assisted with literature retrieval, coding and checking Fluent/PyFluent workflows, execution and recovery support, analysis, figure preparation and report drafting. Fluent performed the numerical calculations. The researcher directed the scientific scope and supplied the physical interpretation. Appendix D describes the division of work and the report's evidence records.

**Report word count:** to be inserted from the final assembled report.

**Signature and date:** to be completed by the author.

<!-- Prescribed wording: ../ESB_part_IV_latex_report_template_v2/Declaration/ESB_declaration_online.tex. The declaration is not signed or represented as approved by this draft. -->

## Table of contents

| Report section | Draft location |
| --- | --- |
| 1. Introduction | [Part 1](01-introduction-and-literature-review.md#1-introduction) |
| 2. Literature review | [Part 1](01-introduction-and-literature-review.md#2-literature-review) |
| 3. Model and methods | [Part 2](02-model-and-methods.md#3-model-and-methods) |
| 4. Results | [Part 3](03-results.md#4-results) |
| 5. Discussion | [Part 4](04-discussion-conclusions-and-future-work.md#5-discussion) |
| 6. Conclusions and future work | [Part 4](04-discussion-conclusions-and-future-work.md#6-conclusions-and-future-work) |
| References | [References](05-references-and-appendices.md#references) |
| Appendix A. Method detail and reproducibility | [Appendix A](05-references-and-appendices.md#appendix-a-method-detail-and-reproducibility) |
| Appendix B. Evidence routes and source limits | [Appendix B](05-references-and-appendices.md#appendix-b-evidence-routes-and-source-limits) |
| Appendix C. Figure register | [Appendix C](05-references-and-appendices.md#appendix-c-figure-register) |
| Appendix D. Author contribution | [Appendix D](05-references-and-appendices.md#appendix-d-author-contribution) |

Page references will be generated during document layout.

## List of figures

| Figure | Subject |
| --- | --- |
| 1 | Separator operation and liquid routes |
| 2 | Empirical wetness and inlet velocity |
| 3 | Inlet geometries and tangential-velocity fields |
| 4 | Wall-film droplet entrainment |
| 5 | Actual solved domain and split inlet |
| 6 | Mesh structure and wall-liquid fields |
| 7 | Effect of inlet phase placement on liquid distribution |
| 8 | Liquid inventory and outlet flow on three finer meshes |
| 9 | Early startup and carrier development |
| 10 | Roughness response |
| 11 | Film-disabled/accretion-enabled outlet histories |
| 12 | Film-disabled/accretion-enabled bulk-liquid spatial comparison |
| 13 | Shortened-startup ramp comparison |
| 14 | Selected film development through 500 ms |
| 15 | Film-thickness views |
| A1 | Complete contact chronology |
| A2 | Shortened-startup and film chronology to iteration 25815 |
| A3 | Native inlet mesh section |
| A4 | Original twelve-case full-geometry outlet screen |
| A5 | Earlier cell-zone absorber and reference |
| A6 | Long pool-control trial and scope decision |

## List of main tables

| Table | Subject |
| --- | --- |
| 1 | Context and evidence for transferring liquid-transport and collection methods to the present separator model |
| 2 | Fixed material properties verified for the throughput-controlled absorber model |
| 3 | Boundary conditions for the main startup and wall-treatment lineage |
| 4 | Model and control changes for the principal reported comparisons |
| 5 | Procedures used to assess implementation and numerical credibility |
| 6 | Quantities used in the model assessment |
| 7 | Matched inlet-placement results at nominal 26.81 m/s |
| 8 | Developing absorber-free fields under the same reduced-relaxation SIMPLE package at iteration 3000 |
| 9 | Successive stages of carrier development |
| 10 | Source-inclusive mass-balance remainders at iteration 5586 |
| 11 | Selected endpoints on the combined field history |
| 12 | Peak values during the matched inlet ramp |
| 13 | Shortened-startup liquid-account terms over the final 500 full-feed updates, iterations 4581–5080 |
| 14 | Film inventory and late-window rates under frozen bulk fields |
| 15 | Direct lower-wall film drainage over 15 ms from identical fields |
| 16 | Answers to the research questions and the next evidence needed |

Appendix tables retain the detailed settings, checks and evidence registers.

## Acknowledgements

I thank Sadiq Zarrouk and Maedeh Amirpour for their supervision of this project, and Andy Tran for his collaboration as my project partner.

## Glossary of terms and abbreviations

| Term | Meaning in this report |
| --- | --- |
| BOC | Bottom-outlet cyclone |
| CFD | Computational fluid dynamics |
| Carrier | The Eulerian vapour and bulk-liquid flow fields through which discrete droplets are tracked |
| DPM | Discrete Phase Model; the Lagrangian representation of droplets |
| EWF | Eulerian Wall Film; the wall-based representation of liquid-film transport |
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
