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
| Draft date | 12 October 2026 |
| Student identification | To be entered by the author |
| Submission date | To be entered by the author |

<!-- Names follow the supplied working poster. The supplied ESB title-page template includes supervisors and co-worker; this takes precedence here over the generic structuring handout's different cover-page advice. -->

## Abstract

Geothermal separators must move liquid away from steam, collect it and provide a discharge route. This study developed an existing computational fluid dynamics model of a vertical steam–water separator by following liquid through the bulk flow, vessel wall and collector. The simplified geometry omitted the lower brine discharge. Mesh development, separate steam and liquid inlet regions, a numerical collector and staged startup enabled studies of wall roughness and Eulerian Wall Film.

The revised mesh provided wall-following refinement and showed changed liquid distributions. With mesh, feed and numerical controls held fixed, placing inlet liquid beside the wall increased retained mass by 37.4%. Without a collector, liquid accumulated in the lower vessel or almost entirely left through the steam outlet. Collection and reduced-feed startup then supplied common fields for wall comparisons. The later combined startup reduced the peak continuity residual during loading by 70.15%. The selected film treatment reduced mean bulk-liquid steam-outlet flow from 24.369 to 1.735 kg/s, alongside a large inventory change.

With bulk flow fields held fixed, film spread and thickened over the lower and middle wall. At 500 ms, input and drainage averaged 81.12 and 69.60 kg/s over the final 10 ms, with storage of 11.53 kg/s. Later configurations added droplet release and impact mechanisms. A matched direct film-drain test reduced lower-wall film inventory by 70.32%. A longer continuation showed that upper-wall liquid could still accumulate while the lower drain operated.

The study connects inlet and wall assumptions to liquid destinations and supplies checked collection and startup procedures. Wall capture, release and drainage must be assessed together when judging design changes. Developing fields, incomplete mass balances and unresolved numerical sensitivity limit the findings to model development. Physical validation is still needed before predicting separation efficiency or pressure loss.

> **Draft completion note.** Section 4.13 reserves the final Phase 9 mesh results. Update this abstract with their main finding when those results are selected; no outcome is assumed here.

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
| 16 | Phase 9 liquid and film fields across mesh resolutions — reserved |
| 17 | Phase 9 collection, outlet flow and storage versus mesh resolution — reserved |
| A1 | Complete contact chronology |
| A2 | Shortened-startup and film chronology to iteration 25815 |
| A3 | Native inlet mesh section |
| A4 | Original twelve-case full-geometry outlet screen |
| A5 | Earlier cell-zone absorber and reference |
| A6 | Long pool-control trial and scope decision |

## List of main tables

| Table | Subject |
| --- | --- |
| 1 | Selected literature and implications for the separator model |
| 2 | Fixed material properties |
| 3 | Main boundary conditions |
| 4 | Matched inlet-placement results |
| 5 | Developing absorber-free fields at iteration 3000 |
| 6 | Peaks during the matched inlet ramp |
| 7 | Film inventory and late-window rates under frozen bulk fields |
| 8 | Matched direct lower-wall film-drain test |
| 9 | Phase 9 final mesh comparison — reserved |

Appendix tables retain comparison designs, detailed settings, criteria, histories, balance results and the supported research answers.

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
