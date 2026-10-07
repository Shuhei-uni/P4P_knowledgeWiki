# Development of a geothermal separator CFD model: startup, liquid removal and wall-film behaviour

*Working title. Markdown draft revised after the author's review on 7 October 2026.*

## Title page information

| Field | Draft information |
| --- | --- |
| Author | Shuhei Yokkaichi |
| Programme | Bachelor of Engineering (Honours), Engineering Science |
| Institution | The University of Auckland |
| Report type | Part IV Research Project Report |
| Supervisors | [TO COMPLETE: names and titles] |
| Co-worker | [TO COMPLETE: required name and contribution information] |
| Student identification | [TO COMPLETE] |
| Report date | [TO COMPLETE: submission date] |

## Abstract

This study developed a computational fluid dynamics model of a vertical geothermal steam–water separator. Continuity and mass imbalance were major barriers to extending the model. The work therefore centred on liquid removal and a startup sequence that developed the flow at reduced feed before increasing the load. The simplified model used a 60,964-cell mesh with no resolved lower liquid-discharge path. Earlier absorbers supported startup development; the final contact treatment supplied local bulk-liquid depletion with associated transport sources and separate film and droplet collection routes.

During the 25% feed hold, scaled continuity reached $3.21\times10^{-4}$ and bulk-liquid inventory settled near 31.36 kg. A verified 2000-update ramp, followed by Coupled flow with Global Time Step, produced the developed full-feed parent used for the subsequent wall experiments. This sequence was the main project turning point: it established a sustained calculation from which roughness and film effects could be compared. It improved numerical behaviour while leaving a material full-feed mass-balance error.

The enabled wall experiments showed large changes in the represented liquid state. With film accretion, mean bulk-liquid steam-outlet flow fell from 24.369 to 1.735 kg/s, alongside a substantial change in inventory. A later combined startup recipe reduced the ramp continuity peak by 70.15%, although an activation spike remained. Subsequent film development used frozen bulk fields and continued to store liquid. The contribution is an absorber and startup development approach that enabled more detailed studies, with defined limits on the resulting predictions. Complete mass closure, mesh qualification and validated separator performance remain open.

## Declaration

[TO COMPLETE: insert the required University declaration. Retain the prescribed wording and complete it with the author's details.]

## Table of contents

| Report section | Draft location |
| --- | --- |
| 1. Introduction | [Part 1](01-introduction-and-literature-review.md) |
| 2. Literature review | [Part 1](01-introduction-and-literature-review.md) |
| 3. Model and methods | [Part 2](02-model-and-methods.md) |
| 4. Results | [Part 3](03-results.md) |
| 5. Discussion | [Part 4](04-discussion-conclusions-and-future-work.md) |
| 6. Conclusions and future work | [Part 4](04-discussion-conclusions-and-future-work.md) |
| References | [References and appendices](05-references-and-appendices.md) |
| Appendices | [References and appendices](05-references-and-appendices.md) |

Lists of figures and tables will use the final selected displays and numbering.

## Acknowledgements

[TO COMPLETE: acknowledge the people and organisations that supported the work. Use only the author's confirmed contributions and names.]

## Glossary of terms and abbreviations

| Term | Meaning in this report |
| --- | --- |
| BOC | Bottom-outlet cyclone |
| CFD | Computational fluid dynamics |
| Carrier | The Eulerian vapour and bulk-liquid flow fields through which discrete droplets are tracked |
| DPM | Discrete Phase Model; the Lagrangian representation of droplets |
| EWF | Eulerian Wall Film; the wall-based representation of liquid-film transport |
| RNG | Renormalisation group; used here in the RNG k–ε turbulence model |
| SIMPLE | Semi-Implicit Method for Pressure-Linked Equations |
| Bulk liquid | Liquid represented by the Eulerian secondary phase; excludes EWF inventory and discrete droplets |
| Phase 1 / phase 2 | The vapour / bulk-liquid phases in the selected Fluent carrier models |
| Accretion | Transfer of represented bulk liquid into the wall film |
| Incomplete trajectory | A tracked droplet with no completed terminal fate under the stated tracking controls |
| Absorber / virtual collector | A numerical liquid-removal treatment inside the truncated model; the two terms refer to the same model role |
| Native iteration, N | Fluent's recorded solver-update coordinate; it is not physical carrier-flow time |
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
