## P4: Mondal & Sharma 2024 - Air-water annular flow CFD

**Full title:** Modeling and simulation of air-water upward annular flow characteristics in a vertical tube using CFD  
**Authors:** Anadi Mondal; Subash L. Sharma  
**Year:** 2024  
**Document type:** Research article  
**Source file:** `1-s2.0-S1738573324002365-main(1).pdf`  
**DOI / source URL:** https://doi.org/10.1016/j.net.2024.05.022

### Fast lookup summary

| Field | Quick note |
| --- | --- |
| Main topic | ANSYS Fluent CFD for upward annular air-water flow using DPM and Eulerian wall film |
| Best use | Use this when you need a detailed example of modelling annular flow with a gas core, droplet entrainment/deposition, and liquid wall film in Fluent. |
| Key methods/models | ANSYS Fluent 19.2; DPM for gas-core droplets; Eulerian Wall Film for wall film; SST k-omega; UDF entrainment correlations; transient two-way coupled simulation. |
| Important outputs | Liquid film thickness, film velocity, entrainment rate, deposition rate, entrainment fraction, and comparison with experimental data and literature correlations. |
| Relevance to your CFD / geothermal separator work | Very useful for conceptualising gas-core/liquid-film/droplet models and for explaining entrainment/deposition in two-phase flow. It is air-water and nuclear-oriented, so geothermal separator transfer needs careful qualification. |
| Cautions / limitations | The working fluids and operating context are not geothermal steam/brine, and the pipe annular-flow geometry differs from a BOC separator. |

### Detailed section dictionary

Use this section when you need to know exactly where to look inside the paper. Each entry gives the page range, what the section contains, the best search terms, what the section is useful for, and any limitations.

#### 1. Abstract / Article info

- **Pages:** p.1
- **Section type:** Front matter
- **What this section contains:** This section defines annular flow as liquid film on the wall, gas core in the centre, and droplets carried in the core. It states the paper's objective: use Fluent DPM and EWF models with entrainment correlations to predict film thickness, velocity, entrainment, deposition, and entrainment fraction.
- **Best search terms:** annular flow; DPM; EWF; entrainment fraction; deposition rate
- **Use this section when:** Use this for a concise overview of the paper's modelling objective and outputs.
- **Important figures/tables/equations:** Keywords; abstract
- **CFD/geothermal relevance:** Useful for entrainment/deposition framing.
- **Limitation note:** Air-water/nuclear context, not geothermal.

#### 2. 1. Introduction

- **Pages:** p.1-p.3
- **Section type:** Background / literature
- **What this section contains:** The introduction explains annular flow mechanisms, including Kelvin-Helmholtz instability, disturbance waves, liquid entrainment, droplet deposition, and dryout risk. It also reviews experimental measurement methods, entrainment-fraction definitions, and previous CFD studies using VOF, DPM, EWF, and correlations.
- **Best search terms:** Kelvin-Helmholtz; disturbance waves; entrainment; deposition; dryout; critical film Reynolds number
- **Use this section when:** Use this when writing theory/background for annular flow and droplet/film exchange.
- **Important figures/tables/equations:** Equation 1 film mass balance; entrainment fraction definition
- **CFD/geothermal relevance:** Strong conceptual source for two-phase annular mechanisms.
- **Limitation note:** Nuclear safety context differs from geothermal separator operation.

#### 3. 2. Methodology

- **Pages:** p.3
- **Section type:** Method umbrella
- **What this section contains:** This section introduces the simulation workflow and explains that the liquid film flow rate at the outlet can be used to calculate entrainment fraction once the flow is fully developed. It also lists simulation parameters from Sawant et al. used as the basis for the model.
- **Best search terms:** methodology; outlet liquid film flow; entrainment fraction; simulation parameters
- **Use this section when:** Use this as the navigation point for simulation domain, Fluent models, correlations, and results.
- **Important figures/tables/equations:** Equation 2 entrainment fraction; Table 1 simulation parameters
- **CFD/geothermal relevance:** Useful for connecting film-flow outputs to entrainment fraction.
- **Limitation note:** The header is brief; details are in subsections.

#### 4. 2.1. Simulation domain

- **Pages:** p.3-p.4
- **Section type:** Geometry / mesh
- **What this section contains:** This section describes the multi-block hexahedral mesh, injection zone, annular zone, wall refinement, and boundary layout. It explains that entrainment and deposition are modelled only in the annular zone and that the domain length is selected to reach fully developed annular flow.
- **Best search terms:** hexahedral mesh; injection zone; annular zone; boundary layer; fully developed flow
- **Use this section when:** Use this when designing a CFD annular-flow domain or explaining injection-zone logic.
- **Important figures/tables/equations:** Fig. 1 mesh cross-section; Fig. 2 tube boundaries
- **CFD/geothermal relevance:** Useful for Fluent domain/boundary explanation.
- **Limitation note:** Pipe domain is simpler than a separator.

#### 5. 2.2. ANSYS methods and models

- **Pages:** p.3-p.4
- **Section type:** Fluent model selection
- **What this section contains:** This section compares multiphase model options in ANSYS and states the chosen setup: DPM for gas-core droplets, EWF for liquid film, SST k-omega turbulence, transient simulation, coupled pressure-velocity solver, and UDF entrainment correlations. It is the key settings section for the paper.
- **Best search terms:** ANSYS Fluent 19.2; DPM; EWF; SST k-omega; UDF; transient
- **Use this section when:** Use this when extracting Fluent settings and justifying model choice.
- **Important figures/tables/equations:** Method description paragraphs
- **CFD/geothermal relevance:** Very useful for model-selection language.
- **Limitation note:** The model is for wall-film annular flow, not free-surface separator VOF.

#### 6. 2.2.1. Gas core simulation

- **Pages:** p.4
- **Section type:** Gas-core model theory
- **What this section contains:** This section explains the gas core as continuous gas plus dispersed droplets and compares Eulerian-Eulerian with Eulerian-Lagrangian modelling. It justifies trajectory-based droplet tracking when droplet volume fraction is low and the particle phase is dispersed.
- **Best search terms:** gas core; Eulerian-Lagrangian; droplet tracking; RANS; dispersed phase
- **Use this section when:** Use this when deciding how to model dispersed droplets in a gas core.
- **Important figures/tables/equations:** Conceptual method discussion
- **CFD/geothermal relevance:** Useful for explaining DPM assumptions.
- **Limitation note:** May not apply if your liquid phase forms large separated free surfaces.

#### 7. 2.2.2. Discrete phase model (DPM)

- **Pages:** p.4
- **Section type:** DPM equations
- **What this section contains:** This section gives the DPM governing equations and explains coupling between continuous gas and tracked liquid droplets. It discusses mass, momentum, drag, body force, and two-way coupling assumptions for droplet trajectories.
- **Best search terms:** DPM equations; two-way coupling; drag force; droplet source terms
- **Use this section when:** Use this when writing the mathematical basis for DPM.
- **Important figures/tables/equations:** Equations 3-9
- **CFD/geothermal relevance:** Good for droplet transport theory.
- **Limitation note:** DPM assumes dispersed droplets, not continuous liquid regions.

#### 8. 2.2.3. Eulerian Wall Film (EWF) model

- **Pages:** p.4-p.5
- **Section type:** Wall-film equations
- **What this section contains:** This section explains the EWF model as a thin two-dimensional film on a wall and lists the thin-film assumptions. It gives wall-film continuity and momentum equations, including entrainment and deposition source terms.
- **Best search terms:** Eulerian Wall Film; thin film; film continuity; film momentum; m_dep; m_ent
- **Use this section when:** Use this when you need equations for liquid film on walls in Fluent.
- **Important figures/tables/equations:** Equations 10-11
- **CFD/geothermal relevance:** Very useful for film/droplet exchange modelling.
- **Limitation note:** EWF assumes a thin wall film rather than a bulk separated water pool.

#### 9. 2.3. Film thickness correlations

- **Pages:** p.5
- **Section type:** Comparison correlations
- **What this section contains:** This section lists film-thickness correlations used to compare against CFD predictions. It explains that correlations depending on liquid/gas velocities and fluid properties are chosen because liquid film Reynolds number is not known before simulation.
- **Best search terms:** film thickness; Henstock-Hanratty; velocity-based correlations; comparison
- **Use this section when:** Use this to benchmark predicted liquid-film thickness.
- **Important figures/tables/equations:** Table 2 film thickness correlations
- **CFD/geothermal relevance:** Useful for validating annular-flow film predictions.
- **Limitation note:** Correlations are not embedded in the model; they are comparison references.

#### 10. 2.4. Film velocity correlations

- **Pages:** p.5
- **Section type:** Wave/film velocity correlations
- **What this section contains:** This section reviews correlations for wave or film velocity based on interfacial shear, liquid/gas velocities, inclination, and physical properties. It is a lookup area for comparing simulated film velocity to empirical predictions.
- **Best search terms:** film velocity; wave velocity; interfacial shear; Marmottant; Kumar; Ju
- **Use this section when:** Use this when you need external correlations for film/wave velocity.
- **Important figures/tables/equations:** Table 3 wave velocity correlations
- **CFD/geothermal relevance:** Useful for checking whether film motion is reasonable.
- **Limitation note:** Different correlations may apply to different regimes and geometries.

#### 11. 2.5. Entrainment correlations

- **Pages:** p.5-p.6
- **Section type:** Entrainment models
- **What this section contains:** This section explains three entrainment correlations and their experimental origins, with emphasis on Bertodano et al. for air-water annular flow and applicability to BWR-like conditions. It discusses critical film Reynolds number and why entrainment rate can be highly sensitive to the selected correlation.
- **Best search terms:** Bertodano; Okawa; entrainment rate; critical film Reynolds number; UDF
- **Use this section when:** Use this when choosing or comparing entrainment source models.
- **Important figures/tables/equations:** Equations/correlation table in text
- **CFD/geothermal relevance:** Very useful for entrainment/deposition discussions.
- **Limitation note:** Empirical correlations may not transfer directly to geothermal brine/steam.

#### 12. 2.6. Droplet size correlations

- **Pages:** p.6
- **Section type:** Droplet diameter input
- **What this section contains:** This section explains that droplet size affects deposition and entrainment fraction, but a fixed representative droplet size is used for simplicity. It reviews empirical droplet-size correlations based on annular-flow mechanisms such as Kelvin-Helmholtz breakup.
- **Best search terms:** droplet size; Sauter mean diameter; Kelvin-Helmholtz; deposition sensitivity
- **Use this section when:** Use this when specifying DPM particle diameter or discussing droplet-size uncertainty.
- **Important figures/tables/equations:** Droplet size correlation paragraphs
- **CFD/geothermal relevance:** Useful for sensitivity/assumption discussion.
- **Limitation note:** Fixed droplet size is a simplification of real polydisperse droplets.

#### 13. 3. Result & discussion

- **Pages:** p.6-p.11
- **Section type:** Results / validation
- **What this section contains:** This section presents the flow-map check, mesh independence, liquid film mass-flow comparisons, entrainment/deposition balance, film thickness, film velocity, droplet size, entrainment rate, and entrainment fraction results. It reports that Bertodano's correlation gives the best entrainment-fraction agreement, mostly within the cited experimental error band.
- **Best search terms:** flow map; mesh independence; liquid film; entrainment fraction; Bertodano; Okawa
- **Use this section when:** Use this when you need results figures or a worked example of validating EWF-DPM annular CFD.
- **Important figures/tables/equations:** Figs. 3-18; Table 4 mesh study
- **CFD/geothermal relevance:** Very useful as a results-section template for annular-flow CFD.
- **Limitation note:** Results are air-water and may be regime-dependent.

#### 14. 4. Conclusion

- **Pages:** p.11
- **Section type:** Takeaways
- **What this section contains:** The conclusion states that entrainment fraction is a crucial safety and heat-transfer parameter and that the EWF-DPM three-field model can predict entrainment fraction within ±30% when Bertodano's correlation is used. It also notes that other correlations underpredict entrainment fraction, likely due to the chosen critical film Reynolds number.
- **Best search terms:** conclusion; ±30%; Bertodano; entrainment fraction; critical film Reynolds number
- **Use this section when:** Use this for final summary statements and limitations.
- **Important figures/tables/equations:** Conclusion paragraphs
- **CFD/geothermal relevance:** Good source for high-level model performance.
- **Limitation note:** Caution needed when transferring correlations to geothermal separators.

### Keyword lookup table

| Keyword / phrase | Category | Location / section | Meaning in this paper | Synonyms / related search terms | Use cases |
| --- | --- | --- | --- | --- | --- |
| Annular flow | Flow regime | P4 Abstract; 1 | Gas-liquid regime with liquid film on the wall, gas in the core, and entrained droplets. | wall film flow; annular mist flow | Search for conceptual flow-regime background. |
| Discrete Phase Model (DPM) | Multiphase CFD | P4 2.2.1-2.2.2 | Eulerian-Lagrangian Fluent model used to track droplets in the gas core. | particle tracking; Lagrangian droplets | Search for droplet modelling details. |
| Eulerian Wall Film (EWF) | Wall-film model | P4 2.2.3 | Fluent model for thin liquid film on a wall, including source terms for entrainment/deposition. | thin film; wall film | Search for wall-film equations. |
| Entrainment fraction (EF) | Annular-flow metric | P4 Abstract; 1; 2; 3 | Fraction of total liquid entrained as droplets in the gas core. | droplet fraction; equilibrium entrainment fraction | Search for model output and validation comparison. |
| Bertodano correlation | Entrainment correlation | P4 2.5; 3; 4 | Empirical entrainment correlation that performed best in this paper's simulations. | Bertodano et al.; entrainment rate model | Search for the best-performing correlation. |
| Critical film Reynolds number | Correlation parameter | P4 1; 2.5; 4 | Threshold that controls whether entrainment starts and strongly affects entrainment predictions. | Relfc; onset of entrainment | Search when discussing why correlations differ. |
| Droplet size correlation | DPM input | P4 2.6; 3 | Empirical input for representative droplet diameter, affecting deposition and entrainment fraction. | particle diameter; SMD; droplet diameter | Search when defining DPM injection size. |
| Dryout | Safety/heat transfer | P4 1; 4 | Condition where the liquid film disappears and heat transfer deteriorates. | critical heat flux; film depletion | Search for motivation of annular-flow modelling. |

### Methods / model / data lookup

| Method / model / dataset | Details | Inputs | Outputs | Where discussed | Why useful | Caveats |
| --- | --- | --- | --- | --- | --- | --- |
| EWF-DPM annular-flow CFD | A transient Fluent model combines Eulerian Wall Film for wall liquid with DPM for droplets in the gas core. UDFs implement entrainment correlations and two-way coupling captures droplet/gas exchange. | Gas/liquid flow conditions, film injection, droplet size, entrainment correlation, mesh/domain. | Film thickness, film velocity, entrainment/deposition rates, entrainment fraction. | 2.1-2.6; 3 | Use for annular flow modelling with film-droplet coupling. | Air-water and pipe geometry, not geothermal separator. |
| Entrainment correlation assessment | Three entrainment models are tested, and Bertodano gives the best agreement with experimental entrainment fractions. The section highlights sensitivity to critical film Reynolds number. | Correlation parameters, film Reynolds number, air-water conditions. | Prediction error versus experiments; recommended correlation. | 2.5; 3; 4 | Use to discuss entrainment-correlation uncertainty. | Correlation transfer to geothermal conditions is uncertain. |

### Figure and table lookup

| Figure/Table | Page(s) | What it shows | Why useful | Related section | Search terms |
| --- | --- | --- | --- | --- | --- |
| Fig. 1 / Fig. 2 - Mesh and simulation tube | p.3-p.4 | Shows cross-section mesh and tube boundary sections with injection and annular zones. | Useful for understanding the CFD domain setup. | 2.1 | mesh; simulation domain |
| Table 1 - Simulation parameters | p.4 | Lists the simulation parameters taken from Sawant et al. for the annular-flow model. | Useful for identifying input cases. | 2 | simulation parameters |
| Tables 2-3 - Film thickness and wave velocity correlations | p.5 | Lists external correlations used to compare film thickness and film/wave velocity. | Useful as a correlation lookup. | 2.3-2.4 | film thickness; wave velocity |
| Fig. 5 - Simulation vs experimental entrainment fraction | p.7 | Compares predicted entrainment fraction against experimental data with error bars. | Important validation figure for the EWF-DPM model. | 3 | entrainment fraction; validation |
| Figs. 8-18 - Film/entrainment/droplet results | p.7-p.11 | Show film thickness, velocity, entrainment/deposition rates, droplet size, and EF trends. | Useful as results examples for annular flow. | 3 | film thickness; deposition; droplet size |

---

## P6: Skoog 2020 - Three-field annular-flow CFD thesis

**Full title:** CFD Annular Flow Modelling Based on a Three-Field Approach  
**Authors:** Erik Skoog  
**Year:** 2020  
**Document type:** Master's thesis  
**Source file:** `FULLTEXT02(1).pdf`  
**DOI / source URL:** No DOI found in uploaded PDF; Luleå University of Technology master's thesis

### Fast lookup summary

| Field | Quick note |
| --- | --- |
| Main topic | Three-field CFD modelling of annular flow with steam core, liquid film, and droplets |
| Best use | Use this for a long-form explanation of three-field annular-flow modelling, Fluent equations, DPM deposition, EWF film treatment, and how simulation results compare to Okawa correlations. |
| Key methods/models | ANSYS Fluent; Eulerian-Lagrangian approach; steam core, liquid film, liquid droplets; DPM; entrainment and deposition correlations; post-processing scripts. |
| Important outputs | Film/droplet/steam mass-flow evolution, deposition-rate comparisons, sensitivity to droplet fraction and transverse velocity, and suggested improvements. |
| Relevance to your CFD / geothermal separator work | Useful for building intuition about how liquid film and droplets interact in CFD, especially if you need to discuss entrainment/deposition mechanisms. Its nuclear BWR context and simplified pipe geometry must be translated carefully to geothermal separator work. |
| Cautions / limitations | This is a thesis rather than a peer-reviewed paper, and it is oriented to BWR annular flow rather than geothermal separator hardware. |

### Detailed section dictionary

Use this section when you need to know exactly where to look inside the paper. Each entry gives the page range, what the section contains, the best search terms, what the section is useful for, and any limitations.

#### 1. Abstract

- **Pages:** PDF p.2 / thesis p.1
- **Section type:** Front matter
- **What this section contains:** The abstract summarises a three-field annular-flow model in ANSYS Fluent for BWR-like flow, approximating the geometry as a cylindrical pipe. It states the core modelling choices: steam core, liquid film, droplets, Okawa entrainment, DPM deposition, and transverse droplet velocity to improve agreement.
- **Best search terms:** three-field approach; ANSYS Fluent; Okawa; DPM; liquid film; droplets
- **Use this section when:** Use this for a fast thesis overview.
- **Important figures/tables/equations:** Abstract
- **CFD/geothermal relevance:** Useful conceptual source for three-field modelling.
- **Limitation note:** Thesis context is nuclear BWR, not geothermal.

#### 2. Acknowledgements

- **Pages:** PDF p.3 / thesis p.2
- **Section type:** Non-technical front matter
- **What this section contains:** This section identifies the supervisors, industrial context, and support network behind the thesis. It does not contain technical content, but it tells you the work was connected to Westinghouse Electric Sweden and prior annular-flow modelling work.
- **Best search terms:** Westinghouse; supervisor; thesis context
- **Use this section when:** Use only if you need context about the institutional background.
- **Important figures/tables/equations:** Acknowledgements page
- **CFD/geothermal relevance:** Low technical relevance.
- **Limitation note:** Skip for modelling details.

#### 3. Contents / list of figures / nomenclature

- **Pages:** PDF p.4-p.7 / thesis p.3-p.6
- **Section type:** Navigation / symbols
- **What this section contains:** These pages provide the table of contents, list of figures, symbols, and abbreviations. They are useful as a quick map to equations, result figures, and terms such as DPM, LPT, UDF, deposition, entrainment, and film thickness.
- **Best search terms:** nomenclature; symbols; list of figures; DPM; LPT; UDF
- **Use this section when:** Use this when trying to locate a figure or decode a variable symbol.
- **Important figures/tables/equations:** List of figures and nomenclature
- **CFD/geothermal relevance:** Useful lookup aid for thesis navigation.
- **Limitation note:** Not an explanatory section.

#### 4. 1 Introduction

- **Pages:** PDF p.8-p.9 / thesis p.7-p.8
- **Section type:** Background / objectives
- **What this section contains:** The introduction explains why annular flow and dryout prediction matter in boiling water reactors and why 3D CFD can improve on restrictive 1D correlations. It also defines the three fields, the interactions between entrainment/deposition/vaporization, and the thesis objectives.
- **Best search terms:** BWR; dryout; annular flow; three fields; entrainment; deposition; Okawa correlations
- **Use this section when:** Use this when you need a clear conceptual explanation of three-field annular-flow CFD.
- **Important figures/tables/equations:** Introductory setup and objectives
- **CFD/geothermal relevance:** Useful for film/droplet modelling intuition.
- **Limitation note:** Application is BWR fuel-rod flow.

#### 5. 2 Background

- **Pages:** PDF p.9-p.10 / thesis p.8-p.9
- **Section type:** Background umbrella
- **What this section contains:** This section introduces boiling regimes and annular-flow properties before the theory chapter. It is useful for understanding the physical flow-regime context behind the simulation model.
- **Best search terms:** boiling regimes; annular flow properties; background
- **Use this section when:** Use this as the general background area before reading equations.
- **Important figures/tables/equations:** Fig. 1 flow regimes
- **CFD/geothermal relevance:** Useful physical background.
- **Limitation note:** Brief compared with theory/method sections.

#### 6. 2.1 Boiling Regimes

- **Pages:** PDF p.9 / thesis p.8
- **Section type:** Flow-regime explanation
- **What this section contains:** This subsection explains the sequence of boiling/flow regimes relevant to heated vertical channels and locates annular flow near the upper/core outlet region. It helps you visualise when liquid becomes a wall film and vapor dominates the core.
- **Best search terms:** bubbly flow; slug flow; churn flow; annular flow; dryout
- **Use this section when:** Use this when you need a simple explanation of how annular flow arises.
- **Important figures/tables/equations:** Fig. 1 flow regimes
- **CFD/geothermal relevance:** Good conceptual background for two-phase regime transitions.
- **Limitation note:** Not geothermal-specific.

#### 7. 2.2 Properties of Annular Flow

- **Pages:** PDF p.9-p.10 / thesis p.8-p.9
- **Section type:** Annular flow physics
- **What this section contains:** This subsection describes the steam core, wall film, and droplet field and explains deposition, entrainment, and vaporization. It is one of the best sections for building intuition about the mass exchange mechanisms that govern film survival or dryout.
- **Best search terms:** steam core; wall film; liquid droplets; deposition; entrainment; vaporization
- **Use this section when:** Use this when explaining the physical meaning of a three-field model.
- **Important figures/tables/equations:** Text description of fields/interactions
- **CFD/geothermal relevance:** Useful for interpreting annular-flow CFD variables.
- **Limitation note:** Pipe annular flow is not cyclone separator flow.

#### 8. 3 Theory

- **Pages:** PDF p.10-p.13 / thesis p.10-p.12
- **Section type:** Theory umbrella
- **What this section contains:** This chapter sets out the equations used in Fluent and the 1D correlations used for comparison. It is the main theory area for steam core, droplet, film, deposition, and entrainment equations.
- **Best search terms:** Fluent equations; 1D correlations; DPM; film equations
- **Use this section when:** Use this when you need mathematical support for the model.
- **Important figures/tables/equations:** Theory chapter equations
- **CFD/geothermal relevance:** Relevant to multiphase modelling framework.
- **Limitation note:** Some equations are simplified for the thesis case.

#### 9. 3.1 Equations in Fluent

- **Pages:** PDF p.10-p.11 / thesis p.10
- **Section type:** Fluent equation overview
- **What this section contains:** This subsection introduces the equations used by Fluent for the three fields. It separates the steam core, droplets, and liquid film so you can identify which equations belong to each phase representation.
- **Best search terms:** Fluent; steam core; droplets; liquid film; governing equations
- **Use this section when:** Use this as a map to the detailed phase-specific equations.
- **Important figures/tables/equations:** Subsections 3.1.1-3.1.3
- **CFD/geothermal relevance:** Useful for model documentation.
- **Limitation note:** Details are split into subsections.

#### 10. 3.1.1 Steam Core

- **Pages:** PDF p.10 / thesis p.10
- **Section type:** Continuous phase equations
- **What this section contains:** This subsection describes how the steam core is modelled as a continuous phase in Fluent. It is useful for understanding which conservation equations govern the vapour field and how source terms from droplets/film may enter.
- **Best search terms:** steam core; continuous phase; conservation equations
- **Use this section when:** Use this when documenting the continuous vapour phase.
- **Important figures/tables/equations:** Steam-core equations
- **CFD/geothermal relevance:** Useful for Eulerian part of the model.
- **Limitation note:** Specific to the thesis setup.

#### 11. 3.1.2 Liquid Droplets

- **Pages:** PDF p.10-p.11 / thesis p.10
- **Section type:** Droplet equations
- **What this section contains:** This subsection describes how liquid droplets are tracked with a Lagrangian particle approach. It is the place to look for droplet trajectory, force balance, and deposition-related modelling assumptions.
- **Best search terms:** liquid droplets; Lagrangian; particle tracking; DPM; deposition
- **Use this section when:** Use this when explaining DPM/particle tracking.
- **Important figures/tables/equations:** Droplet equations
- **CFD/geothermal relevance:** Useful for dispersed droplet modelling.
- **Limitation note:** Does not represent continuous liquid sheets or pools.

#### 12. 3.1.3 Liquid Film

- **Pages:** PDF p.11 / thesis p.11
- **Section type:** Film equations
- **What this section contains:** This subsection describes the liquid wall film and the equations controlling its mass and momentum. It is useful for identifying how film thickness and film flow respond to entrainment, deposition, and evaporation/source terms.
- **Best search terms:** liquid film; film thickness; wall film; mass source
- **Use this section when:** Use this when writing about wall-film conservation equations.
- **Important figures/tables/equations:** Film equations
- **CFD/geothermal relevance:** Useful for EWF-style film modelling.
- **Limitation note:** Not suitable for thick/stratified water regions.

#### 13. 3.2 1D-correlations

- **Pages:** PDF p.11-p.13 / thesis p.11-p.12
- **Section type:** Correlation framework
- **What this section contains:** This subsection introduces the one-dimensional correlations used as comparison benchmarks for CFD. It explains why 1D correlations are still useful even when the goal is a 3D CFD model: they provide expected trends and validation targets.
- **Best search terms:** 1D correlations; Okawa; benchmark; comparison
- **Use this section when:** Use this when comparing CFD outputs to empirical/analytical expectations.
- **Important figures/tables/equations:** Correlation equations
- **CFD/geothermal relevance:** Useful validation logic.
- **Limitation note:** Correlations have limited parameter ranges.

#### 14. 3.2.1 Deposition

- **Pages:** PDF p.12 / thesis p.12
- **Section type:** Deposition correlation
- **What this section contains:** This subsection explains the deposition correlation that estimates how droplets return from the gas core to the liquid film. It is important because deposition competes with entrainment and therefore controls film mass-flow evolution.
- **Best search terms:** deposition; droplets to film; mass transfer coefficient; Okawa
- **Use this section when:** Use this when modelling or explaining droplet deposition.
- **Important figures/tables/equations:** Deposition equations
- **CFD/geothermal relevance:** Relevant for annular-flow mass balance.
- **Limitation note:** Correlation may not apply to separator-scale droplets.

#### 15. 3.2.2 Entrainment

- **Pages:** PDF p.12-p.13 / thesis p.12
- **Section type:** Entrainment correlation
- **What this section contains:** This subsection explains the entrainment correlation that creates droplets from the liquid film. It is important because entrainment reduces film flow and increases droplet mass in the gas core, directly influencing dryout risk.
- **Best search terms:** entrainment; film to droplets; Okawa; critical film Reynolds number
- **Use this section when:** Use this when modelling source terms for droplet formation.
- **Important figures/tables/equations:** Entrainment equations
- **CFD/geothermal relevance:** Useful conceptual source for film-to-droplet transfer.
- **Limitation note:** Empirical constants are regime-specific.

#### 16. 4 Method

- **Pages:** PDF p.13-p.19 / thesis p.13-p.19
- **Section type:** Method umbrella
- **What this section contains:** This chapter describes how the Fluent model was implemented, improved, initialised, and post-processed. It is the best practical section if you want to understand workflow rather than just equations.
- **Best search terms:** method; Fluent implementation; initialization; post-processing
- **Use this section when:** Use this when looking for implementation details and modelling workflow.
- **Important figures/tables/equations:** Fig. 2 setup; Fig. 3 mesh; Fig. 4 injection wall
- **CFD/geothermal relevance:** Useful for CFD workflow reference.
- **Limitation note:** Geometry remains simplified.

#### 17. 4.1 Overview of previous work

- **Pages:** PDF p.13-p.15 / thesis p.13-p.15
- **Section type:** Prior model context
- **What this section contains:** This subsection summarises the prior thesis/model versions that this work builds on. It explains the existing geometry, mesh, injection strategy, and limitations that motivated later changes.
- **Best search terms:** previous work; Camacho; Raddino; model setup; geometry
- **Use this section when:** Use this when tracing the development of the three-field model.
- **Important figures/tables/equations:** Fig. 2 model sketch; Fig. 3 cross-sectional mesh
- **CFD/geothermal relevance:** Useful if you need modelling-history context.
- **Limitation note:** Not all prior work details are reproduced.

#### 18. 4.2 Changes and Improvements

- **Pages:** PDF p.15-p.19 / thesis p.15-p.18
- **Section type:** Model improvements
- **What this section contains:** This subsection introduces improvements made to the previous model, including liquid-film treatment, automation/initialization, and steam/particle handling. It is a practical troubleshooting area for reducing computation time and improving agreement with correlations.
- **Best search terms:** model improvements; automation; initialization; transverse velocity
- **Use this section when:** Use this when looking for practical modelling refinements.
- **Important figures/tables/equations:** Subsections 4.2.1-4.2.3
- **CFD/geothermal relevance:** Useful for understanding modelling iteration.
- **Limitation note:** Some improvements are specific to thesis scripts and setup.

#### 19. 4.2.1 Liquid Film

- **Pages:** PDF p.15-p.16 / thesis p.15-p.16
- **Section type:** Film implementation improvement
- **What this section contains:** This subsection discusses changes to the liquid-film implementation and how the film is injected or maintained. It is useful for understanding how film boundary conditions and numerical setup affect annular-flow stability.
- **Best search terms:** liquid film; injection; wall film; stability
- **Use this section when:** Use this when troubleshooting film setup or boundary conditions.
- **Important figures/tables/equations:** Fig. 4 injection wall
- **CFD/geothermal relevance:** Useful for wall-film modelling choices.
- **Limitation note:** Implementation details may depend on Fluent version.

#### 20. 4.2.2 Automation and Initialization

- **Pages:** PDF p.16-p.17 / thesis p.16
- **Section type:** Workflow automation
- **What this section contains:** This subsection explains how automation and initialization reduce manual work and improve repeatability. It is useful if you want to understand how many simulations or post-processing files were generated consistently.
- **Best search terms:** automation; initialization; TUI; scripts; repeatability
- **Use this section when:** Use this when designing a repeatable simulation workflow.
- **Important figures/tables/equations:** Workflow description
- **CFD/geothermal relevance:** Useful for good CFD practice.
- **Limitation note:** Not a scientific result by itself.

#### 21. 4.2.3 Steam and Particles

- **Pages:** PDF p.17-p.19 / thesis p.17-p.18
- **Section type:** Particle/steam treatment
- **What this section contains:** This subsection explains how steam and particle/droplet injection are handled, including the transverse velocity applied to droplets at entrainment. It is important because changing droplet initial direction can affect deposition and better match 1D correlations.
- **Best search terms:** steam; particles; transverse velocity; droplet injection; deposition
- **Use this section when:** Use this when thinking about DPM injection conditions and particle initial velocity.
- **Important figures/tables/equations:** Fig. 5 deposition-rate comparison
- **CFD/geothermal relevance:** Useful for DPM sensitivity discussion.
- **Limitation note:** Specific to annular-flow droplet injection, not separator inlet flow.

#### 22. 4.3 Post-Processing

- **Pages:** PDF p.19 / thesis p.19
- **Section type:** Post-processing
- **What this section contains:** This subsection describes how simulation data were extracted and averaged to compare with 1D calculations and experiments. It is useful for understanding how Fluent outputs are turned into film/droplet/steam mass-flow plots.
- **Best search terms:** post-processing; averaging; ASCII files; mass flow; Fluent output
- **Use this section when:** Use this when planning how to process CFD results.
- **Important figures/tables/equations:** Post-processing paragraphs
- **CFD/geothermal relevance:** Useful for results workflow.
- **Limitation note:** Script details may require thesis appendices.

#### 23. 4.4 Assumptions

- **Pages:** PDF p.19 / thesis p.19
- **Section type:** Assumptions
- **What this section contains:** This subsection states modelling assumptions that simplify the annular-flow problem. It is useful when you need to identify what is excluded or idealised before interpreting the results.
- **Best search terms:** assumptions; simplifications; uniform power; cylindrical pipe
- **Use this section when:** Use this when writing limitations.
- **Important figures/tables/equations:** Assumption list/paragraph
- **CFD/geothermal relevance:** Useful for critical evaluation.
- **Limitation note:** Assumptions limit transfer to separator geometry.

#### 24. 5 Results

- **Pages:** PDF p.19-p.26 / thesis p.19-p.26
- **Section type:** Results
- **What this section contains:** This chapter presents the comparison of 1D calculations, CFD results, experimental data, film thickness, droplet mass flow, and field mass-flow evolution for different total mass fluxes. It is the primary lookup area for what the model predicts and how sensitive it is to inlet mass flow, droplet fraction, and transverse velocity.
- **Best search terms:** results; mass flux; film thickness; droplet mass flow; deposition rate; Okawa
- **Use this section when:** Use this when looking for plots, trend explanations, or model-performance discussion.
- **Important figures/tables/equations:** Figs. 6-15
- **CFD/geothermal relevance:** Useful as an annular-flow results template.
- **Limitation note:** Results are for pipe/BWR conditions.

#### 25. 6 Conclusions

- **Pages:** PDF p.26-p.27 / thesis p.26
- **Section type:** Takeaways
- **What this section contains:** The conclusions summarise whether the modified model improved agreement with Okawa correlations and experimental trends. It also comments on sensitivity, computational practicality, and where the model still needs improvement.
- **Best search terms:** conclusions; model accuracy; transverse velocity; deposition; Okawa
- **Use this section when:** Use this for final thesis findings.
- **Important figures/tables/equations:** Conclusion section
- **CFD/geothermal relevance:** Good high-level model evaluation.
- **Limitation note:** Conclusions should be checked against the detailed results.

#### 26. 7 Future Work

- **Pages:** PDF p.27-p.28 / thesis p.27
- **Section type:** Future improvements
- **What this section contains:** This section suggests further model development and improvements that were not completed. It is useful if you are looking for limitations, possible extensions, or research-gap wording.
- **Best search terms:** future work; model improvements; extensions; limitations
- **Use this section when:** Use this when writing a research-gap or future-work paragraph.
- **Important figures/tables/equations:** Future work section
- **CFD/geothermal relevance:** Useful for identifying open modelling issues.
- **Limitation note:** Suggestions are thesis-specific.

#### 27. 8 Appendix A

- **Pages:** PDF p.28-p.34 / thesis p.28-p.34
- **Section type:** Appendix / supporting detail
- **What this section contains:** Appendix A contains supporting material, likely including code, configuration, or additional derivations/data for the model. It is a lookup area for implementation details that are too detailed for the main method chapter.
- **Best search terms:** appendix; implementation; code; supporting data
- **Use this section when:** Use this when main text does not give enough setup detail.
- **Important figures/tables/equations:** Appendix A
- **CFD/geothermal relevance:** Potentially useful for reproducing workflow.
- **Limitation note:** May require careful reading because it is not summarised like the main text.

#### 28. 9 Appendix B

- **Pages:** PDF p.35-p.41 / thesis p.35-p.41
- **Section type:** Appendix / supporting detail
- **What this section contains:** Appendix B contains additional supporting material that complements the main modelling and results chapters. It is useful as a backup lookup area for scripts, output processing, or parameter details not found elsewhere.
- **Best search terms:** appendix; scripts; output; supporting data
- **Use this section when:** Use this for deeper reproduction or debugging details.
- **Important figures/tables/equations:** Appendix B
- **CFD/geothermal relevance:** Potentially useful for implementation.
- **Limitation note:** Not the quickest place for conceptual understanding.

### Keyword lookup table

| Keyword / phrase | Category | Location / section | Meaning in this paper | Synonyms / related search terms | Use cases |
| --- | --- | --- | --- | --- | --- |
| Three-field approach | Model architecture | P6 Abstract; 1; 3-4 | Model with steam core, liquid film, and liquid droplets represented separately. | three fields; steam-film-droplet model | Search for overall CFD modelling philosophy. |
| Okawa correlations | Correlation set | P6 Abstract; 1; 3.2; 5 | 1D correlations used for entrainment and deposition benchmarks. | Okawa et al.; 1D correlations | Search for comparison model equations. |
| Transverse droplet velocity | Model improvement | P6 Abstract; 4.2.3; 5-6 | Additional droplet velocity component applied at entrainment to improve deposition behaviour and correlation agreement. | radial velocity; particle initial velocity | Search for DPM injection sensitivity. |
| Liquid film mass flow | Output variable | P6 2.2; 5 | Mass flow carried in the wall film; central variable for dryout and entrainment/deposition balance. | film flow rate; Wlf | Search for results plots and post-processing. |
| Deposition rate | Mass exchange | P6 3.2.1; 4.2.3; 5 | Rate at which droplets return from gas core to the film. | m_dep; droplet deposition | Search for droplet-wall interaction. |
| Entrainment rate | Mass exchange | P6 3.2.2; 5 | Rate at which liquid leaves the film and becomes droplets. | m_ent; droplet creation | Search for film-to-droplet source terms. |
| Lagrangian Particle Tracking (LPT) | Numerical method | P6 Nomenclature; 3.1.2; 4 | Trajectory-based droplet modelling method linked with DPM. | particle tracking; DPM | Search for droplet movement modelling. |
| Post-processing scripts | Workflow | P6 4.3; Appendices | Scripts/files used to average and process Fluent outputs for comparison plots. | automation; ASCII files; processing | Search for implementation workflow ideas. |

### Methods / model / data lookup

| Method / model / dataset | Details | Inputs | Outputs | Where discussed | Why useful | Caveats |
| --- | --- | --- | --- | --- | --- | --- |
| Three-field annular-flow CFD model | The thesis models steam core, wall film, and droplets as separate fields in Fluent. Entrainment is based on Okawa 1D correlations and deposition is calculated through DPM particle trajectories. | Mass flux, quality, geometry, film/droplet initial conditions, correlations. | Mass flow rates for steam/film/droplets, deposition rate, film thickness, comparison with experiments. | 1; 3; 4; 5 | Use for intuition about three-field mass exchange. | BWR pipe model, not geothermal separator. |
| DPM transverse velocity sensitivity | The thesis applies transverse velocity to droplets at entrainment to improve match with the Okawa deposition trend. This shows droplet initial conditions can strongly affect deposition behaviour. | Droplet injection velocity/direction, gas/film conditions. | Changed deposition rate and better correlation agreement. | 4.2.3; 5; 6 | Use when discussing DPM sensitivity to injection assumptions. | Implementation-specific and needs validation for other geometries. |

### Figure and table lookup

| Figure/Table | Page(s) | What it shows | Why useful | Related section | Search terms |
| --- | --- | --- | --- | --- | --- |
| Fig. 1 - Different flow regimes | PDF p.8 | Shows typical flow regimes including annular flow. | Useful for simple visual explanation of regime transition. | 2.1 | flow regimes; annular |
| Fig. 2 / Fig. 3 - Model setup and mesh | PDF p.14-p.15 | Shows the simplified model setup and cross-sectional mesh. | Useful for understanding the thesis CFD geometry. | 4.1 | setup; mesh |
| Fig. 5 - Deposition rate injection comparison | PDF p.17 | Compares deposition rate for different particle injection approaches. | Useful for showing sensitivity to droplet injection method. | 4.2.3 | deposition; particle injection |
| Figs. 6-15 - Results plots | PDF p.20-p.25 | Show 1D calculations, experimental comparisons, mass flow rates of three fields, film thickness, and deposition-rate comparisons. | Useful for trend extraction and results narrative. | 5 | mass flow; film thickness; deposition |

---
