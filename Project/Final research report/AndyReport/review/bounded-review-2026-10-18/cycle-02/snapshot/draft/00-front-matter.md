# Geothermal steam-water separator design CFD modelling and optimising

## Title page information

| Field | Information |
| --- | --- |
| Author | Andy Tran |
| Co-worker | Shuhei Yokkaichi |
| Supervisors | Sadiq Zarrouk and Maedeh Amirpour |
| Institution | The University of Auckland |
| Report | Part IV Research Project Report |
| UPI | qtra338 |
| Draft | Revised 17 October 2026 |

## Abstract

This project investigated how two-phase inlet conditions affect geothermal steam–water separator predictions, building on an inherited computational fluid dynamics model. An imposed stratified inlet placed liquid on the outer-wall side and steam in the remaining area. During baseline mesh assessment, continuing changes in liquid inventory and pressure exposed the need to assess liquid removal before interpreting separation performance. The work therefore examined numerical liquid removal, an explicit brine outlet and wall-film drainage, supported by mass-balance checks, numerical sensitivity tests and droplet tracking. A later comparison on the same mesh found about 37% more retained liquid with the split inlet than with a mixed inlet at matched 10,000-iteration endpoints. Both still sent nearly all incoming bulk liquid through the steam outlet, so this was a sensitivity result rather than a demonstrated improvement in separation.

Several useful capabilities were established. Low-feed preparation, inlet ramping and Coupled pressure–velocity treatment reduced continuity residuals to approximately 0.002–0.005 at full feed. However, the reported full-feed state still had excess liquid removal equivalent to 20.81% of liquid feed. Later wall-film calculations passed selected local balance checks with the bulk equations active. A matched direct-drain test reduced the lower-wall store by 70.32%, but total film by only 1.70% relative to the undrained case. Four simple outlet-resistance tests reproduced the analytical pressure–flow relation and passed their numerical checks. These verified specific treatments without establishing a stationary separator operating state. Longer film calculations retained storage, while full-geometry and mesh studies remained sensitive to iteration, starting state and numerical controls.

When unfinished particle tracks were counted as separated, reconstructed efficiency estimates agreed with earlier project estimates within 0.019 percentage points. However, 16.78–33.29% of injected particle mass had no resolved final destination. Increasing the tracking allowance tenfold more than doubled the small escaped-mass estimate. Agreement in the reported efficiency estimate therefore did not demonstrate reliable particle separation.

The project established liquid-removal and wall-film modelling capabilities and identified the checks needed to interpret them. A complete, stationary, mesh-independent and physically validated separator solution was not established. Further work should combine the verified components with consistent mass accounting, confirmed geometry and downstream conditions, and resolved particle fates before using the model for performance optimisation.

## Declaration

*Unsigned draft. The author must review and complete this declaration before submission.*

**Student**

I hereby declare that:

1.  This report is the result of the final year project work carried out by my project partner (see cover page) and I under the guidance of our supervisor (see cover page) in the 2026 academic year at the Department Engineering Science and Biomedical Engineering, Faculty of Engineering, University of Auckland.

2.  This report is not the outcome of work done previously.

3.  This report is not the outcome of work done in collaboration, except that with a potential project sponsor (if any) as stated in the text.

4.  This report is not the same as any report, thesis, conference article or journal paper, or any other publication or unpublished work in any format.

**Continuing-project statement.** This work builds on an inherited separator model and published separator CFD. The report presents the project’s reconstruction, liquid-removal, wall-film and numerical-assessment work. Reused figures identify their source and creator. The author must review this statement with the declaration before submission.

**Use of generative AI.** Draft disclosure for author review: OpenAI Codex assisted with coding, evidence analysis and report drafting. The author must confirm the complete description of tools and uses before signing.

**Prior report material.** The literature review is reproduced from the author’s earlier project report, as requested. Its source and unchanged-text copy are retained in the drafting records.

**Word count:** approximately 11,600 words from Introduction through Conclusions, including headings, captions and tables.

**Signature and date:** to be completed by the author.

## Table of contents

1. Introduction
2. Literature review
3. Model and methods
4. Verification and validation assessment
5. Results
6. Discussion
7. Conclusions and future work
8. References
9. Appendices

Page references are generated in the LaTeX review export.

## Acknowledgements

[Author to complete acknowledgements of supervisors, collaborator and other support.]

## Glossary of terms and symbols

| **Term** | **Meaning** |
|:---|:---|
| BOC | Bottom-outlet cyclone separator |
| CFD | Computational fluid dynamics |
| DPM | Discrete Phase Model (droplet tracking) |
| EWF | Eulerian Wall Film (surface liquid transport) |
| RANS | Reynolds-averaged Navier–Stokes equations |
| RNG | Renormalisation group (turbulence model) |
| VOF | Volume of Fluid (interface model) |
| Carrier field | Bulk flow used for droplet tracking |
| Active bulk | Bulk flow equations continue to update |
| Frozen bulk | Bulk fields held fixed while other models advance |
| Film accretion | Liquid transferred into the wall-film model |
| Incomplete trajectory | Particle track without a resolved final destination |
| Collector | Numerical region that removes liquid through a source |
| Stationary inventory | Retained liquid mass within stated change limits |
| Numerical acceptance | Meeting the stated checks for an individual test and observation window |
| Liquid inventory | Liquid mass retained within the vessel or wall film |
| Residual | Scaled measure of how well a discretised equation is satisfied |
| Outlet dryness | Vapour mass fraction in flow through the steam outlet |
| Sink | Negative source term used to remove mass numerically |
| Film age | Time accumulated by the film equations; not necessarily physical elapsed time of the whole flow |
| Inner film iterations | Iterations used to solve the film equations within one film timestep |
| RMS | Root-mean-square measure used here for spatial velocity differences |
| Validation | Assessment against physical evidence for an intended use |

### Symbols 

|  |  |
|:---|:---|
| $\alpha_L$ | Liquid volume fraction |
| $\rho_L$ | Liquid density (kg/m$^{3}$) |
| $\dot m$ | Mass flow rate (kg/s) |
| $M_L$ | Retained liquid mass (kg) |
| $M_f$ | Retained wall-film mass (kg) |
| $R_L$ | Signed liquid balance remainder (kg/s) |
| $S_L$ | Liquid mass source per unit volume (kg/(m$^{3}$·s)) |
| $\tau$ | Collector depletion time (s) |
| $K$ | Dimensionless outlet-resistance coefficient |
| $\eta_{\mathrm{assumed}}$ | Efficiency estimate assuming incomplete particles are separated (%) |

