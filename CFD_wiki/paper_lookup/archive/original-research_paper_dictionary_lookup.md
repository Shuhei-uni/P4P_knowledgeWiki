# Research Paper Dictionary and Lookup Table

This Markdown file is designed as a fast lookup guide for the uploaded research papers. Each paper has a high-level summary, a detailed section dictionary, keyword lookup table, method/data lookup, and figure/table lookup so you can quickly find where useful information is located.

## Contents

- [Paper index](#paper-index)
- [Quick topic map](#quick-topic-map)
- [P1: Montesdeoca-Martínez et al. 2026 - Two-phase geothermal ORC techno-economics](#p1-montesdeoca-martnez-et-al-2026-two-phase-geothermal-orc-techno-economics)
- [P2: Mubarok et al. 2020 - CFD pressure differential flow meters](#p2-mubarok-et-al-2020-cfd-pressure-differential-flow-meters)
- [P3: Merbecks et al. 2025 - GeoProp geofluid property framework](#p3-merbecks-et-al-2025-geoprop-geofluid-property-framework)
- [P4: Mondal & Sharma 2024 - Air-water annular flow CFD](#p4-mondal-sharma-2024-air-water-annular-flow-cfd)
- [P5: Rivas-Cruz et al. 2015 - Geothermal steam separator review](#p5-rivas-cruz-et-al-2015-geothermal-steam-separator-review)
- [P6: Skoog 2020 - Three-field annular-flow CFD thesis](#p6-skoog-2020-three-field-annular-flow-cfd-thesis)
- [Combined methods and data lookup](#combined-methods-and-data-lookup)
- [Combined figure and table lookup](#combined-figure-and-table-lookup)
- [Combined keyword index](#combined-keyword-index)

---

## Paper index

| Paper ID | Short name | Year | Main topic | Best use | Key methods/models | Important outputs | Cautions / limitations | Source file |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P1 | Montesdeoca-Martínez et al. 2026 - Two-phase geothermal ORC techno-economics | 2026 | ORC/binary power plant design for two-phase geothermal fluids | Use this as the main source for plant-level thermodynamic modelling, ORC component definitions, working-fluid selection, and techno-economic comparison. | EES model; well/two-phase production model; ORC energy balances; parametric study; cost correlations and CAPEX comparison. | Net power output, specific power output, thermal/utilization efficiency, heat exchanger sizing/cost, CAPEX comparison with single-flash and flash-binary systems. | This is a system-level model rather than a CFD separator paper, so it abstracts the separator and focuses on energy conversion performance. | 1-s2.0-S0196890426000191-main(1).pdf |
| P2 | Mubarok et al. 2020 - CFD pressure differential flow meters | 2020 | ANSYS Fluent CFD for two-phase geothermal flow through pressure-differential meters | Use this as the most directly relevant ANSYS Fluent geothermal CFD reference among the uploaded papers, especially for model settings, validation workflow, mesh refinement, and result contours. | 3D CFD in ANSYS Fluent; mixture model; SST k-omega turbulence; energy equation; steady/transient comparison; field validation. | Pressure drop, velocity fields, turbulent kinetic energy, mass flow rate, temperature, enthalpy, entropy, and comparison across six meter geometries. | The geometry is pipeline flow-meter geometry, so separation objectives differ from steam-water separator design. | 1-s2.0-S0375650519304328-main(1).pdf |
| P3 | Merbecks et al. 2025 - GeoProp geofluid property framework | 2025 | Thermophysical property and phase-partition modelling for geothermal geofluids | Use this when you need to justify why fluid properties, brine salinity, NCGs, phase partitioning, enthalpy, density, viscosity, and heat content matter for geothermal simulations. | Framework coupling Reaktoro, CoolProp, and ThermoFun; comparison of pure-fluid, binary-fluid, reactive, and empirical geofluid models; validation against brine data. | Validated property predictions for brines/geofluids, comparison of heat-release curves, and architecture for coupling partition and property calculations. | This is a modelling-framework paper, not a CFD paper, so use it for property modelling rather than mesh or boundary-condition decisions. | 1-s2.0-S0375650524002323-main(1).pdf |
| P4 | Mondal & Sharma 2024 - Air-water annular flow CFD | 2024 | ANSYS Fluent CFD for upward annular air-water flow using DPM and Eulerian wall film | Use this when you need a detailed example of modelling annular flow with a gas core, droplet entrainment/deposition, and liquid wall film in Fluent. | ANSYS Fluent 19.2; DPM for gas-core droplets; Eulerian Wall Film for wall film; SST k-omega; UDF entrainment correlations; transient two-way coupled simulation. | Liquid film thickness, film velocity, entrainment rate, deposition rate, entrainment fraction, and comparison with experimental data and literature correlations. | The working fluids and operating context are not geothermal steam/brine, and the pipe annular-flow geometry differs from a BOC separator. | 1-s2.0-S1738573324002365-main(1).pdf |
| P5 | Rivas-Cruz et al. 2015 - Geothermal steam separator review | 2015 | State-of-art review of geothermal steam-water separators, Webre separators, dryers, Bangma BOC, and Lazalde-Crabtree methods | Use this as the main lookup source for geothermal separator design history, separator types, Webre-type separators, Lazalde-Crabtree design logic, and Cerro Prieto separator evaluation context. | Literature review; design/evaluation comparison matrix; discussion of separator/dryer design methods and software tools. | Design-history summary, key references, separator/dryer methodology comparison, and conclusions about Webre-type separator performance and Lazalde-Crabtree methodology. | Because it is a review, it often summarizes older sources rather than presenting new experiments or CFD data. | 1032231(1).pdf |
| P6 | Skoog 2020 - Three-field annular-flow CFD thesis | 2020 | Three-field CFD modelling of annular flow with steam core, liquid film, and droplets | Use this for a long-form explanation of three-field annular-flow modelling, Fluent equations, DPM deposition, EWF film treatment, and how simulation results compare to Okawa correlations. | ANSYS Fluent; Eulerian-Lagrangian approach; steam core, liquid film, liquid droplets; DPM; entrainment and deposition correlations; post-processing scripts. | Film/droplet/steam mass-flow evolution, deposition-rate comparisons, sensitivity to droplet fraction and transverse velocity, and suggested improvements. | This is a thesis rather than a peer-reviewed paper, and it is oriented to BWR annular flow rather than geothermal separator hardware. | FULLTEXT02(1).pdf |

---

## Quick topic map

| Task / question | Recommended papers and sections | Why go there first | Search terms |
| --- | --- | --- | --- |
| I need a quick geothermal separator design literature source | P5 Section 2, especially Bangma/BOC and Lazalde-Crabtree rows | It is the only uploaded paper directly reviewing geothermal steam separators and dryers. | BOC; Webre; Lazalde-Crabtree; steam quality |
| I need ANSYS Fluent settings for two-phase geothermal CFD | P2 Sections 3.2-3.4 and Table 2 | P2 gives solver, multiphase, turbulence, energy, discretisation, mesh, and validation details for geothermal two-phase flow. | Fluent settings; mixture model; SST; energy equation |
| I need an example of mesh convergence analysis | P2 Section 3.4; P4 Section 3; P6 Method/Results | P2 explicitly uses Richardson extrapolation and reports mesh error, while P4 uses mesh independence for annular flow. | mesh refinement; Richardson; mesh study |
| I need pressure/velocity/TKE contour interpretation | P2 Sections 4.2.2-4.2.4 | P2 explains how restrictions create pressure loss, vena contracta, separation, and turbulence hotspots. | pressure contour; velocity; TKE |
| I need liquid film, droplet, entrainment and deposition theory | P4 Sections 1, 2.2.2-2.5; P6 Sections 2.2, 3.1-3.2 | P4 and P6 both explain annular film-droplet mass exchange using DPM/EWF/1D correlations. | annular flow; entrainment; deposition; EWF; DPM |
| I need to justify thermophysical property choices | P3 Sections 2-6 | P3 explains why brine, NCGs, phase behaviour, enthalpy, density, viscosity, and heat content matter. | GeoProp; brine; NCG; thermophysical properties |
| I need ORC/binary plant equations and economics | P1 Sections 2.1-2.3 and 4 | P1 contains ORC layout, energy balances, performance metrics, cost equations, parametric results, and plant comparisons. | ORC; CAPEX; net power; specific power |
| I need citation-ready headline results | P1 Section 5; P2 Section 5; P4 Section 4; P5 Section 3; P6 Section 6; P3 Section 7 | Conclusion sections are the fastest places to extract final claims and limitations. | conclusion; results; takeaways |
| I need BOC/spiral inlet historical details | P5 Section 2 - Bangma / BOC | P5 summarises Bangma's BOC work, including spiral versus tangential inlet testing and dimensions relative to inlet diameter. | Bangma; spiral inlet; BOC |
| I need to decide whether VOF, mixture, DPM or EWF is suitable | P2 Section 3.2; P4 Sections 2.2.1-2.2.3; P6 Theory | P2 shows a geothermal mixture-model case, while P4/P6 show DPM/EWF annular-flow cases. | VOF; mixture; DPM; EWF; multiphase model |

---

## P1: Montesdeoca-Martínez et al. 2026 - Two-phase geothermal ORC techno-economics

**Full title:** Techno-economic modeling and assessment of a binary power plant for the utilization of two-phase geothermal fluids  
**Authors:** Fernando Montesdeoca-Martínez; Sergio Velázquez-Medina; Stefan Kranz  
**Year:** 2026  
**Document type:** Research article  
**Source file:** `1-s2.0-S0196890426000191-main(1).pdf`  
**DOI / source URL:** https://doi.org/10.1016/j.enconman.2026.121050

### Fast lookup summary

| Field | Quick note |
| --- | --- |
| Main topic | ORC/binary power plant design for two-phase geothermal fluids |
| Best use | Use this as the main source for plant-level thermodynamic modelling, ORC component definitions, working-fluid selection, and techno-economic comparison. |
| Key methods/models | EES model; well/two-phase production model; ORC energy balances; parametric study; cost correlations and CAPEX comparison. |
| Important outputs | Net power output, specific power output, thermal/utilization efficiency, heat exchanger sizing/cost, CAPEX comparison with single-flash and flash-binary systems. |
| Relevance to your CFD / geothermal separator work | Good for connecting separator/two-phase geothermal production to the downstream power plant and economics. Less useful for detailed separator CFD geometry or internal phase-separation physics. |
| Cautions / limitations | This is a system-level model rather than a CFD separator paper, so it abstracts the separator and focuses on energy conversion performance. |

### Detailed section dictionary

Use this section when you need to know exactly where to look inside the paper. Each entry gives the page range, what the section contains, the best search terms, what the section is useful for, and any limitations.

#### 1. Abstract / Article info

- **Pages:** p.1
- **Section type:** Front matter
- **What this section contains:** This section gives the fastest overview of the proposed binary plant concept for two-phase geothermal fluids. It states the main novelty: separated geothermal steam is condensed in an additional evaporator, and it summarizes the maximum net power result and economic comparison.
- **Best search terms:** binary plant; two-phase geofluid; additional evaporator; n-pentane; CAPEX
- **Use this section when:** Use this for a quick high-level summary, key numbers, keywords, and the paper's main contribution.
- **Important figures/tables/equations:** Keywords; abstract result paragraph
- **CFD/geothermal relevance:** Plant-level relevance; not detailed separator physics.
- **Limitation note:** Use for framing, not for CFD setup.

#### 2. 1. Introduction

- **Pages:** p.1-p.3
- **Section type:** Background / motivation
- **What this section contains:** The introduction explains why geothermal energy is valuable for island grids and why ORC/binary plants are attractive for reliable baseload power. It then reviews ORC studies, flash-binary systems, and existing steam-condensing binary plant concepts such as Ribeira Grande, Pico Vermelho, Olkaria III, and Cerro Pabellón.
- **Best search terms:** island energy; ORC; flash-binary; steam-condensing binary; high-temperature liquid-dominated reservoir
- **Use this section when:** Use this when writing literature-review motivation or explaining why a hybrid two-phase geothermal plant is needed.
- **Important figures/tables/equations:** Global technology shares and plant examples in text
- **CFD/geothermal relevance:** Helpful for literature-review context around liquid-dominated geothermal resources.
- **Limitation note:** It is broad and literature-focused; detailed equations start later.

#### 3. 2. Method

- **Pages:** p.3
- **Section type:** Method umbrella
- **What this section contains:** This short section acts as the header for the modelling workflow and tells you where the system design, equations, techno-economics, and comparison procedure are located. It is mostly a navigation section rather than a detailed technical section.
- **Best search terms:** method; modelling workflow; ORC simulation
- **Use this section when:** Use this as an anchor when navigating the structure of the paper.
- **Important figures/tables/equations:** Section hierarchy
- **CFD/geothermal relevance:** Useful map of where model details are located.
- **Limitation note:** Not much standalone content.

#### 4. 2.1. System description

- **Pages:** p.3-p.5
- **Section type:** System architecture
- **What this section contains:** This section describes the layout of the proposed ORC system and the stream-by-stream role of the separator, additional evaporator, preheater, evaporator, recuperator, condenser, pumps, turbine, dry cooler, and cooling-water loop. It is the best place to understand how separated steam and brine/condensate are used differently to evaporate and preheat the organic working fluid.
- **Best search terms:** system layout; separator; additional evaporator; recuperative ORC; stream numbers
- **Use this section when:** Use this when you need to explain the proposed plant configuration or identify where the separator appears in the process.
- **Important figures/tables/equations:** Fig. 1 plant layout; Fig. 2 T-s diagram
- **CFD/geothermal relevance:** Good for connecting separator outlet streams to power-cycle heat exchangers.
- **Limitation note:** The separator is included as a process component, not modelled internally.

#### 5. 2.2. System modelling and simulation

- **Pages:** p.5
- **Section type:** Model overview
- **What this section contains:** This section states that the model is implemented in Engineering Equation Solver and combines a two-phase geofluid/well model with aboveground ORC component models. It also lists global assumptions such as steady-state operation, adiabatic components, negligible kinetic/potential changes, negligible NCGs, and reinjection of geothermal fluid.
- **Best search terms:** EES; steady state; assumptions; two-phase model; aboveground model
- **Use this section when:** Use this when summarising modelling assumptions and explaining the boundary between subsurface/well modelling and plant modelling.
- **Important figures/tables/equations:** Fig. 3 methodology; Table 1 component efficiencies
- **CFD/geothermal relevance:** Useful for showing how a geothermal model can be modularised.
- **Limitation note:** Assumptions may oversimplify real separator and brine chemistry behaviour.

#### 6. 2.2.1. Two-phase fluid modelling

- **Pages:** p.5-p.6
- **Section type:** Geofluid / well model
- **What this section contains:** This section defines the productivity-index approach and pressure-drop logic used to estimate two-phase geofluid output from reservoir to wellhead. It also explains how flashing, phase state, steam/brine split, mass flow, and related thermodynamic states are handled before the fluid enters the aboveground plant.
- **Best search terms:** productivity index; wellhead pressure; flashing; vapor quality; two-phase mass flow
- **Use this section when:** Use this when you need equations for converting reservoir/wellhead assumptions into two-phase geofluid conditions.
- **Important figures/tables/equations:** Productivity-index equations; Fig. 4 flashing T-s diagram
- **CFD/geothermal relevance:** Relevant to estimating separator inlet quality and mass flow.
- **Limitation note:** It is 1D/system-level, not a CFD flow-field model.

#### 7. 2.2.2. Aboveground system modelling

- **Pages:** p.6
- **Section type:** ORC component equations
- **What this section contains:** This section gives the energy-balance equations for the turbine, pump, evaporators, preheater, recuperator, condenser, dry cooler, and cooling-water loop. It is the main equation lookup area for how mass flow rates, enthalpy changes, component efficiencies, heat transfer, and power consumption are calculated.
- **Best search terms:** turbine power; pump power; heat exchanger balance; dry cooler; recuperator
- **Use this section when:** Use this for thermodynamic equations and component-level process modelling.
- **Important figures/tables/equations:** Equations for turbine, pump, heat exchangers, dry cooler
- **CFD/geothermal relevance:** Useful if your separator work needs to connect to downstream heat/power calculations.
- **Limitation note:** It does not contain CFD boundary-condition details.

#### 8. 2.2.3. Thermodynamic analysis

- **Pages:** p.6-p.7
- **Section type:** Performance metrics
- **What this section contains:** This section defines the key performance indicators used to evaluate the ORC system, including thermal efficiency, net power output, utilization efficiency, specific power output, and exergy destruction. It is useful when you need consistent definitions for comparing geothermal plant configurations.
- **Best search terms:** thermal efficiency; net power; utilization efficiency; specific power output; exergy destruction
- **Use this section when:** Use this when extracting KPIs or writing a performance-analysis paragraph.
- **Important figures/tables/equations:** Equations 20 onward; exergy relations
- **CFD/geothermal relevance:** Good for plant-level comparison metrics.
- **Limitation note:** These metrics are not separator-specific efficiency metrics.

#### 9. 2.2.4. Economic analysis

- **Pages:** p.7-p.8
- **Section type:** Cost / economic model
- **What this section contains:** This section explains how purchased equipment costs are calculated and escalated with CEPCI to estimate capital expenditure. It includes equipment cost equations for major ORC components and describes how plant cost is compared across configurations.
- **Best search terms:** PEC; CEPCI; CAPEX; heat exchanger cost; dry cooler cost
- **Use this section when:** Use this when looking for economic assumptions or cost-equation references.
- **Important figures/tables/equations:** Table 2 cost equations; Table 3 U-value ranges
- **CFD/geothermal relevance:** Useful if you need to mention techno-economic consequences of design choices.
- **Limitation note:** Costs are correlation-based and case-specific.

#### 10. 2.2.5. Parametric study

- **Pages:** p.8
- **Section type:** Parameter selection
- **What this section contains:** This section identifies which variables are changed in the simulation and why they matter to plant performance. It covers turbine inlet temperature, wellhead pressure, preheater pinch-point temperature difference, and dry-cooler approach temperature difference.
- **Best search terms:** parametric study; TIT; wellhead pressure; pinch point; approach temperature
- **Use this section when:** Use this when you need to list independent variables or justify sensitivity-analysis choices.
- **Important figures/tables/equations:** Table 4 variable bounds
- **CFD/geothermal relevance:** Useful model-design reference for sensitivity studies.
- **Limitation note:** The parameter set is tailored to the proposed plant, not generic CFD.

#### 11. 2.2.6. Selected working fluids

- **Pages:** p.8
- **Section type:** Working-fluid choice
- **What this section contains:** This section explains why n-pentane, isopentane, and n-butane were selected as ORC candidates. It compares technical, environmental, health, and safety properties so you can see how working-fluid choice links to plant performance and constraints.
- **Best search terms:** n-pentane; isopentane; n-butane; ORC working fluid; GWP; ODP
- **Use this section when:** Use this when discussing ORC working-fluid selection or comparing dry organic fluids.
- **Important figures/tables/equations:** Table 5 fluid properties
- **CFD/geothermal relevance:** Useful for downstream plant modelling, not separator geometry.
- **Limitation note:** Fluid choice affects ORC results but not the geothermal phase separation directly.

#### 12. 2.2.7. Validation

- **Pages:** p.8
- **Section type:** Model validation
- **What this section contains:** This section validates the model against a reference geothermal system using published plant data. It lists validation inputs such as separator inlet enthalpy, temperature, pressure, steam/brine mass flow rates, ambient conditions, reservoir temperature, and reference performance.
- **Best search terms:** validation; reference geothermal system; separator inlet; model behaviour
- **Use this section when:** Use this when you need to show that the system model has been checked against literature data.
- **Important figures/tables/equations:** Table 6 validation results
- **CFD/geothermal relevance:** Good example of validating a thermodynamic model against a plant case.
- **Limitation note:** Validation is for plant performance, not separator CFD flow patterns.

#### 13. 2.3. Techno-economic comparison

- **Pages:** p.8-p.9
- **Section type:** Comparative scenarios
- **What this section contains:** This section defines the reference systems used to compare the proposed ORC concept: single-flash and flash-binary systems under the same resource conditions. It explains the optimization variables and constraints used to make the comparison fair across different plant types.
- **Best search terms:** single-flash; flash-binary; comparative study; optimization bounds
- **Use this section when:** Use this when you need to compare geothermal power plant architectures.
- **Important figures/tables/equations:** Comparison setup tables and constraints
- **CFD/geothermal relevance:** Useful for broader geothermal system trade-off discussion.
- **Limitation note:** Not intended for detailed mechanical design.

#### 14. 3. Case study description

- **Pages:** p.9-p.10
- **Section type:** Case context
- **What this section contains:** This section introduces Tenerife as the case-study location and describes the island grid, geothermal target, reservoir assumptions, production wells, ambient temperature, drilling cost context, and expected well conditions. It is where you find the real-world case assumptions used later in the results.
- **Best search terms:** Tenerife; Canary Islands; reservoir temperature; production wells; drilling target
- **Use this section when:** Use this when you need case-study data, site context, or resource assumptions.
- **Important figures/tables/equations:** Fig. 5 map; Table 7 geofluid properties
- **CFD/geothermal relevance:** Provides context for why geothermal baseload power matters on islands.
- **Limitation note:** Values are site-specific and may not transfer to New Zealand/geothermal separator work.

#### 15. 4. Results and discussion

- **Pages:** p.10-p.14
- **Section type:** Results / interpretation
- **What this section contains:** This section presents the main parametric results, including productivity curves, working-fluid comparisons, and the effects of turbine inlet temperature, wellhead pressure, pinch point, and dry-cooler approach temperature. It also reports the best-performing case and compares CAPEX and specific power output against single-flash and flash-binary systems.
- **Best search terms:** net power output; n-pentane; parametric results; CAPEX; specific power output
- **Use this section when:** Use this when you need numerical results, trend explanations, or final comparison figures.
- **Important figures/tables/equations:** Figs. 6-11; Tables 8-13
- **CFD/geothermal relevance:** Useful for extracting headline metrics for a literature-review table.
- **Limitation note:** Results depend heavily on the chosen case and assumptions.

#### 16. 5. Conclusions

- **Pages:** p.14-p.15
- **Section type:** Takeaways
- **What this section contains:** The conclusion restates the non-standard ORC design and gives the main numerical findings, including the best n-pentane case and the thermodynamic/economic improvements over reference systems. It is the quickest place to find the final message and limitations of the proposed plant concept.
- **Best search terms:** conclusions; 13.59 MW; utilization efficiency; specific power improvement; CAPEX
- **Use this section when:** Use this for final results and concise citation-ready takeaways.
- **Important figures/tables/equations:** Final bullet-like conclusion paragraphs
- **CFD/geothermal relevance:** Good for summarising plant-level benefits.
- **Limitation note:** Do not use it as a substitute for methods if you need assumptions or equations.

### Keyword lookup table

| Keyword / phrase | Category | Location / section | Meaning in this paper | Synonyms / related search terms | Use cases |
| --- | --- | --- | --- | --- | --- |
| Organic Rankine Cycle (ORC) | Plant cycle | P1 Abstract; 1; 2.1-2.2 | Closed-loop binary cycle used to convert geothermal heat into electricity via a secondary organic working fluid. | binary cycle; recuperative ORC; subcritical ORC | Search when you need plant layout, component equations, or working-fluid discussion. |
| Additional evaporator | Plant component | P1 2.1; 2.2.2; 4 | Novel component where separated geothermal steam condenses to partially evaporate the ORC working fluid. | steam condenser evaporator; EA; steam-condensing binary | Search when explaining the paper's main novelty. |
| Specific power output (SPO) | Performance metric | P1 2.2.3; 4; 5 | Power produced per unit geothermal fluid flow/resource input; used to compare plant technologies. | specific output; net power per geofluid flow | Search when comparing proposed system with flash-binary or single-flash. |
| Turbine inlet temperature (TIT) | Parameter | P1 2.2.5; 4 | ORC design variable that strongly affects thermal efficiency and net power output. | inlet temperature; expander inlet temperature | Search when discussing sensitivity analysis. |
| Wellhead pressure | Resource/well parameter | P1 2.2.1; 2.2.5; 4 | Operating variable that affects mass flow, flashing, and geothermal fluid quality at the surface. | separator inlet pressure; production pressure | Search when connecting well performance to plant output. |
| n-pentane / isopentane / n-butane | Working fluids | P1 2.2.6; 4 | Candidate dry organic fluids compared for ORC performance and environmental/safety properties. | ORC fluids; hydrocarbons; dry fluids | Search when justifying fluid selection. |
| CAPEX | Economics | P1 2.2.4; 4; 5 | Capital expenditure estimated from equipment costs and used to compare system economics. | capital investment; purchased equipment cost; PEC | Search when writing techno-economic analysis. |
| Flash-binary system | Comparator system | P1 Introduction; 2.3; 4 | Reference hybrid geothermal plant that combines flash and binary units. | single flash-ORC; flash-binary cycle | Search when comparing plant architectures. |

### Methods / model / data lookup

| Method / model / dataset | Details | Inputs | Outputs | Where discussed | Why useful | Caveats |
| --- | --- | --- | --- | --- | --- | --- |
| EES thermodynamic plant model | A system-level model couples a two-phase geofluid/well model with aboveground ORC component equations. It calculates states, component heat duties, power, efficiency, and economic indicators. | Reservoir conditions, productivity index, wellhead pressure, ambient temperature, component efficiencies, working-fluid properties. | Net power, efficiency, specific power, heat duties, CAPEX, component sizing/costs. | 2.2. System modelling; 2.2.2; 2.2.3; 2.2.4 | Use as a template for plant-level analysis and ORC equations. | Not a CFD or separator-internal model. |
| Parametric techno-economic comparison | TIT, wellhead pressure, heat-exchanger pinch/approach temperatures, and working fluid are varied to identify performance optima. The proposed plant is compared against single-flash and flash-binary references. | Variable bounds, working fluids, geothermal case assumptions. | Performance trends, optimal cases, CAPEX and specific-power comparisons. | 2.2.5; 2.3; 4 | Use when showing how design variables affect plant performance. | Case-specific and relies on cost correlations. |

### Figure and table lookup

| Figure/Table | Page(s) | What it shows | Why useful | Related section | Search terms |
| --- | --- | --- | --- | --- | --- |
| Fig. 1 - Layout of the geothermal power plant | p.4 | Shows proposed plant layout with separator, additional evaporator, ORC loop, cooling-water loop, and dry cooler. | Best visual for understanding the proposed process architecture. | 2.1 | plant layout; additional evaporator; separator |
| Fig. 2 - ORC temperature-entropy diagram | p.4 | Shows the subcritical ORC with dry/retrograde working fluid behaviour. | Useful for explaining working-fluid thermodynamic path. | 2.1 | T-s diagram; ORC |
| Fig. 3 - Methodology schematic | p.5 | Maps modelling assumptions, two-phase geofluid model, and aboveground system model. | Useful for quickly explaining the modelling workflow. | 2.2 | methodology; simulation workflow |
| Fig. 6 - Productivity curve and quality | p.10 | Shows well mass flow and quality as a function of wellhead pressure. | Useful for linking wellhead pressure to separator inlet conditions. | 4 | productivity curve; quality |
| Tables 8-13 - Results/cost comparison | p.10-p.14 | Provide working-fluid results, heat transfer data, cooling system data, and comparison with reference systems. | Useful for extracting headline numbers and economic comparisons. | 4 | net power; CAPEX; specific power |

---

## P2: Mubarok et al. 2020 - CFD pressure differential flow meters

**Full title:** Comparative CFD modelling of pressure differential flow meters for measuring two-phase geothermal fluid flow  
**Authors:** Mohamad Husni Mubarok; John E. Cater; Sadiq J. Zarrouk  
**Year:** 2020  
**Document type:** Research article  
**Source file:** `1-s2.0-S0375650519304328-main(1).pdf`  
**DOI / source URL:** https://doi.org/10.1016/j.geothermics.2020.101801

### Fast lookup summary

| Field | Quick note |
| --- | --- |
| Main topic | ANSYS Fluent CFD for two-phase geothermal flow through pressure-differential meters |
| Best use | Use this as the most directly relevant ANSYS Fluent geothermal CFD reference among the uploaded papers, especially for model settings, validation workflow, mesh refinement, and result contours. |
| Key methods/models | 3D CFD in ANSYS Fluent; mixture model; SST k-omega turbulence; energy equation; steady/transient comparison; field validation. |
| Important outputs | Pressure drop, velocity fields, turbulent kinetic energy, mass flow rate, temperature, enthalpy, entropy, and comparison across six meter geometries. |
| Relevance to your CFD / geothermal separator work | Very useful for your Fluent setup, convergence/mesh logic, and how to present pressure/velocity/TKE/temperature/enthalpy contours for two-phase geothermal flow. It is not a separator paper, but its CFD workflow transfers well to separator inlet/outlet studies. |
| Cautions / limitations | The geometry is pipeline flow-meter geometry, so separation objectives differ from steam-water separator design. |

### Detailed section dictionary

Use this section when you need to know exactly where to look inside the paper. Each entry gives the page range, what the section contains, the best search terms, what the section is useful for, and any limitations.

#### 1. Abstract / Article info

- **Pages:** p.1
- **Section type:** Front matter
- **What this section contains:** This section gives a concise overview of the CFD comparison of six pressure differential flow meters for two-phase geothermal flow. It names the key outputs: pressure drop, velocity, turbulent kinetic energy, mass flow rate, temperature, enthalpy, and entropy.
- **Best search terms:** pressure differential; geothermal flow; CFD; mass flow; enthalpy
- **Use this section when:** Use this for a quick overview of the paper and its main output variables.
- **Important figures/tables/equations:** Keywords; abstract
- **CFD/geothermal relevance:** Very useful for identifying the CFD variables worth plotting.
- **Limitation note:** No method details beyond the overview.

#### 2. 1. Introduction

- **Pages:** p.1-p.2
- **Section type:** Background / gap
- **What this section contains:** The introduction explains why real-time two-phase geothermal mass-flow measurement is difficult and why pressure-differential meters are attractive alternatives to costly well-testing methods. It reviews prior CFD/orifice studies and identifies the gap: previous validated geothermal orifice CFD did not include the energy equation needed for temperature and heat-transfer behaviour.
- **Best search terms:** two-phase measurement; orifice plate; real-time monitoring; energy equation
- **Use this section when:** Use this when writing the research gap or justification for geothermal two-phase CFD.
- **Important figures/tables/equations:** Literature review paragraphs
- **CFD/geothermal relevance:** Highly relevant for a CFD methodology background section.
- **Limitation note:** Focused on metering rather than separation.

#### 3. 2. Field experiment setup

- **Pages:** p.2-p.4
- **Section type:** Experimental validation data
- **What this section contains:** This section describes the Indonesian field experiments at Ulubelu, Sibayak, Lahendong, and Bukit Daun wells and explains how mass flow was measured using lip-pressure and separator methods. It also specifies the sharp-edge concentric orifice installation, pipe diameters, beta ratio, flange taps, and measured pressure/enthalpy data used for CFD validation.
- **Best search terms:** field experiment; geothermal wells; lip pressure; separator method; flange taps
- **Use this section when:** Use this when you need validation data, operating conditions, or experimental geometry for geothermal two-phase flow.
- **Important figures/tables/equations:** Fig. 1 field setup; pressure tap schematic
- **CFD/geothermal relevance:** Excellent validation workflow reference for geothermal CFD.
- **Limitation note:** Experimental data only validate the concentric orifice directly.

#### 4. 3. Numerical modelling of geothermal two-phase flow

- **Pages:** p.4
- **Section type:** Numerical model umbrella
- **What this section contains:** This heading introduces the numerical model that is then broken down into geometry, governing equations, solver settings, and mesh refinement. It is mostly a signpost, but it marks the part of the paper you should use for ANSYS Fluent setup details.
- **Best search terms:** numerical modelling; ANSYS Fluent; two-phase flow
- **Use this section when:** Use this to navigate to the detailed modelling subsections.
- **Important figures/tables/equations:** Section 3 subsections
- **CFD/geothermal relevance:** Main reference area for Fluent setup.
- **Limitation note:** The header itself is brief.

#### 5. 3.1. Geometry of computational model

- **Pages:** p.4-p.5
- **Section type:** Geometry / computational domain
- **What this section contains:** This section describes the 3D ANSYS DesignModeler geometries for the concentric orifice and the other flow meters. It gives pipe lengths, beta ratio, bevel angle, approximate domain length, and special dimensions such as the longer Venturi geometry.
- **Best search terms:** DesignModeler; geometry; beta ratio; pipe length; Venturi; orifice
- **Use this section when:** Use this when you need geometry/domain dimensions or a precedent for upstream/downstream pipe length.
- **Important figures/tables/equations:** Fig. 2 geometry; Fig. 3 flow-meter domains; Table 1 dimensions
- **CFD/geothermal relevance:** Useful for explaining computational-domain design and geometry comparison.
- **Limitation note:** Geometry is a flow meter, not a separator.

#### 6. 3.2. Governing equations

- **Pages:** p.4-p.6
- **Section type:** Equations / physics model
- **What this section contains:** This section presents the continuity, RANS, mixture-model, energy, turbulence, and phase-related equations used in the CFD model. It is the equation lookup area for justifying the mixture model, SST k-omega turbulence model, energy equation, and how enthalpy and phase quantities are represented.
- **Best search terms:** RANS; mixture model; SST k-omega; energy equation; volume fraction
- **Use this section when:** Use this when writing the theoretical basis of the Fluent model.
- **Important figures/tables/equations:** Governing equations; Table 2 model settings nearby
- **CFD/geothermal relevance:** Very useful for a methodology section on two-phase geothermal CFD.
- **Limitation note:** May not match VOF/separator physics exactly if you choose a different multiphase model.

#### 7. 3.3. Numerical method

- **Pages:** p.6-p.7
- **Section type:** Solver settings
- **What this section contains:** This section specifies the solver choices and discretisation settings, including pressure-based solver, steady/transient modes, gravity, mixture flow, volume fraction, turbulence, energy, Courant number, and initialization. It also lists measured operating parameters and input data used in simulations.
- **Best search terms:** coupled solver; second-order upwind; first-order upwind; Courant number; initialization
- **Use this section when:** Use this when building a Fluent settings table for your report.
- **Important figures/tables/equations:** Table 2 modelling parameters; Table 3 measured operating parameters; Table 4 CFD input parameters
- **CFD/geothermal relevance:** Strong reference for ANSYS setup and reporting format.
- **Limitation note:** Settings are optimized for flow meters and may need adaptation for BOC separators.

#### 8. 3.4. Mesh generation and refinement study

- **Pages:** p.7
- **Section type:** Mesh independence
- **What this section contains:** This section explains the unstructured mesh, curvature refinement, transition ratio, growth rate, boundary layers, and Richardson extrapolation mesh-refinement study. It compares pressure drop, enthalpy, and mass-flow error across six mesh densities and selects the mesh with errors below 1%.
- **Best search terms:** mesh refinement; Richardson extrapolation; boundary layer; mesh independence
- **Use this section when:** Use this when writing mesh convergence or grid independence analysis.
- **Important figures/tables/equations:** Fig. 5 mesh refinement; Table 5 mesh study
- **CFD/geothermal relevance:** Very useful as a template for your mesh convergence section.
- **Limitation note:** The mesh metric targets are flow-meter outputs rather than separator efficiency.

#### 9. 4. Results and discussion

- **Pages:** p.7
- **Section type:** Results umbrella
- **What this section contains:** This section states that 59 CFD simulation cases are analysed and that a transient model is used as a benchmark for steady-state results. It identifies the main contour outputs: pressure, velocity, turbulent kinetic energy, temperature, and enthalpy.
- **Best search terms:** 59 CFD cases; contour analysis; steady-state validation
- **Use this section when:** Use this as an overview of how the results section is organised.
- **Important figures/tables/equations:** Contour variables list
- **CFD/geothermal relevance:** Useful for deciding which plots to include in your CFD report.
- **Limitation note:** Details are in the subsections.

#### 10. 4.1. Concentric sharp-edge orifice flow meter models

- **Pages:** p.7-p.8
- **Section type:** Validation results
- **What this section contains:** This section compares CFD predictions with field measurements for the concentric orifice flow meter. It reports that predicted pressure drop, mass flow rate, and enthalpy agree well with the experimental data, supporting the later geometry comparison.
- **Best search terms:** concentric orifice; field validation; pressure drop; enthalpy; mass flow
- **Use this section when:** Use this when you need an example of validating CFD against field data.
- **Important figures/tables/equations:** Table 6 experimental vs simulated values; Fig. 7 comparison plot
- **CFD/geothermal relevance:** Strong validation precedent for geothermal two-phase CFD.
- **Limitation note:** Only the concentric orifice has direct field validation.

#### 11. 4.2. Other pressure differential flow meter results

- **Pages:** p.8
- **Section type:** Comparative model transfer
- **What this section contains:** This section explains that the validated concentric-orifice mesh parameters and boundary conditions are transferred to top eccentric, bottom eccentric, segmental, Nozzle, and Venturi models. It is useful because it shows how a validated CFD setup can be extended to related geometries.
- **Best search terms:** top eccentric; bottom eccentric; segmental; Nozzle; Venturi; model transfer
- **Use this section when:** Use this when explaining how validated settings can be reused across design alternatives.
- **Important figures/tables/equations:** Intro to Sections 4.2.1-4.2.5
- **CFD/geothermal relevance:** Useful for design-comparison workflow logic.
- **Limitation note:** The transfer assumes comparable physics and requires caution.

#### 12. 4.2.1. Transient model analysis

- **Pages:** p.8-p.9
- **Section type:** Steady vs transient check
- **What this section contains:** This section uses a transient Nozzle simulation as a benchmark to validate/refine the steady-state model when field data are unavailable. It gives timestep, total simulation time, Courant number, convergence expectation, and the comparison of first- and second-order momentum discretisation.
- **Best search terms:** transient benchmark; steady-state validation; timestep; Courant number; Nozzle
- **Use this section when:** Use this when deciding whether your steady separator simulation needs a transient check.
- **Important figures/tables/equations:** Table 7 transient/steady comparison; Fig. 8 velocity stability
- **CFD/geothermal relevance:** Useful for convergence and solver-choice justification.
- **Limitation note:** A 0.075 s benchmark may not capture slow separator transients.

#### 13. 4.2.2. Pressure distribution and net pressure drop

- **Pages:** p.9-p.12
- **Section type:** Pressure results
- **What this section contains:** This section compares pressure contours and net pressure drop across all six meter geometries. It shows that Venturi and Nozzle designs produce lower net pressure losses than orifice types, while local restrictions create strong pressure minima and recovery behaviour.
- **Best search terms:** pressure contour; pressure drop; pressure recovery; Venturi; Nozzle
- **Use this section when:** Use this when describing how geometry affects pressure loss in two-phase CFD.
- **Important figures/tables/equations:** Fig. 9 pressure contours; Fig. 10 net pressure drop
- **CFD/geothermal relevance:** Good reference for pressure-contour interpretation.
- **Limitation note:** Flow-meter pressure loss is not the same as separator separation efficiency.

#### 14. 4.2.3. Two-phase fluid velocity

- **Pages:** p.12
- **Section type:** Velocity results
- **What this section contains:** This section analyses velocity distributions and identifies vena contracta and separated-flow regions downstream of restrictions. It explains how different geometries shape high-velocity zones and recirculation, including the anomalous segmental-orifice behaviour.
- **Best search terms:** velocity contour; vena contracta; separated flow; recirculation; segmental orifice
- **Use this section when:** Use this when interpreting velocity contours and geometry-induced flow acceleration.
- **Important figures/tables/equations:** Fig. 11 velocity distributions; Fig. 12 segmental comparison
- **CFD/geothermal relevance:** Useful for thinking about inlet/spiral geometry effects in separators.
- **Limitation note:** Geometry-specific conclusions should not be copied directly to separator designs.

#### 15. 4.2.4. Turbulent kinetic energy

- **Pages:** p.12-p.13
- **Section type:** Turbulence results
- **What this section contains:** This section links turbulent kinetic energy to flow separation and fluctuating processes near restrictions. It shows that Venturi and Nozzle designs have lower TKE than orifice geometries, which helps explain why their pressure losses are smaller.
- **Best search terms:** turbulent kinetic energy; TKE; SST; separation zone; flow fluctuations
- **Use this section when:** Use this when explaining TKE contour patterns and turbulence intensity hotspots.
- **Important figures/tables/equations:** Fig. 13 TKE contours
- **CFD/geothermal relevance:** Very useful for your Fluent post-processing narrative.
- **Limitation note:** TKE patterns in a cyclone separator may be intentionally high and swirling, so interpret carefully.

#### 16. 4.2.5. Thermodynamic results

- **Pages:** p.13-p.14
- **Section type:** Temperature/enthalpy/entropy results
- **What this section contains:** This section analyses temperature, enthalpy, and entropy changes caused by pressure losses and geometry. It notes small temperature and enthalpy decreases downstream of meters and discusses scaling risk where local temperatures drop.
- **Best search terms:** temperature contour; enthalpy contour; entropy; silica scaling; thermodynamic loss
- **Use this section when:** Use this when discussing energy-equation outputs and thermodynamic interpretation of CFD results.
- **Important figures/tables/equations:** Fig. 14 temperature; Fig. 15 enthalpy; Fig. 16 entropy
- **CFD/geothermal relevance:** Useful if you include thermal fields in your separator simulation.
- **Limitation note:** The paper treats adiabatic changes in metering devices, not separator heat transfer.

#### 17. 5. Conclusions

- **Pages:** p.14-p.15
- **Section type:** Takeaways
- **What this section contains:** The conclusion states that the validated concentric-orifice CFD predicted pressure drop, mass flow rate, and enthalpy within small relative error, and that Nozzle/Venturi meters showed much lower net pressure drops. It also summarizes geometry effects on velocity/TKE and recommends Nozzle and Venturi as promising for two-phase geothermal measurement.
- **Best search terms:** conclusions; validation error; Nozzle; Venturi; geothermal measurement
- **Use this section when:** Use this for final findings and shortlist recommendations.
- **Important figures/tables/equations:** Numbered conclusion list
- **CFD/geothermal relevance:** Good source for summarised comparative results.
- **Limitation note:** Recommendations are specific to flow metering.

### Keyword lookup table

| Keyword / phrase | Category | Location / section | Meaning in this paper | Synonyms / related search terms | Use cases |
| --- | --- | --- | --- | --- | --- |
| Pressure differential flow meter | Instrumentation/CFD | P2 Abstract; 1; 3-4 | Device that estimates flow from pressure difference, including orifice, Nozzle, and Venturi meters. | DP meter; differential pressure device | Search for geothermal two-phase measurement geometry and results. |
| Mixture model | Multiphase CFD | P2 3.2; 3.3 | ANSYS multiphase approach used to represent water-vapour/steam and liquid water/brine phases as interpenetrating mixture fields. | mixture method; Eulerian mixture | Search when comparing Fluent multiphase model choices. |
| SST k-omega | Turbulence model | P2 3.2; 3.3; 5 | Turbulence model selected for the two-phase geothermal flow simulations. | k-omega SST; shear stress transport | Search for turbulence-model justification. |
| Energy equation | Thermal CFD | P2 1; 3.2; 4.2.5 | Equation added so temperature, enthalpy, and entropy changes can be analysed, unlike earlier geothermal orifice CFD. | enthalpy; temperature; thermodynamics | Search when justifying thermal field simulation. |
| Richardson extrapolation | Mesh convergence | P2 3.4 | Method used to assess mesh refinement error across six mesh densities. | mesh refinement; grid convergence; extrapolated error | Search when writing mesh independence/convergence. |
| Venturi | Flow-meter geometry | P2 3.1; 4.2 | Flow meter geometry that produced low pressure drop and low TKE compared with orifice geometries. | Venturi tube; pressure recovery | Search when comparing geometries. |
| Nozzle | Flow-meter geometry | P2 3.1; 4.2.1-4.2.5 | Flow meter geometry used for transient benchmark and shown to have lower pressure drop than orifice meters. | nozzle meter; convergent throat | Search when reviewing transient vs steady validation. |
| Turbulent kinetic energy (TKE) | CFD result variable | P2 4.2.4 | Result variable used to evaluate fluctuations and separation zones downstream of restrictions. | k; turbulence contour | Search for interpretation of turbulence contours. |

### Methods / model / data lookup

| Method / model / dataset | Details | Inputs | Outputs | Where discussed | Why useful | Caveats |
| --- | --- | --- | --- | --- | --- | --- |
| ANSYS Fluent two-phase geothermal CFD | Steady and transient 3D simulations of geothermal steam-water/brine flow through differential pressure meter geometries. The model uses mixture multiphase physics, energy equation, and SST k-omega turbulence. | Mass flow, steam/liquid mass split, enthalpy, pressure, temperature, geometry dimensions, wall roughness. | Pressure drop, velocity, TKE, temperature, enthalpy, entropy, mass-flow prediction. | 3.1-3.4; 4 | Use as the strongest uploaded template for Fluent settings and result presentation. | Meter geometries differ from separator geometry. |
| Field validation with Indonesian geothermal wells | The concentric orifice model is validated against field data from four wells using lip-pressure and separator testing methods. Agreement is assessed for pressure drop, mass flow, and enthalpy. | Well test data, pressure taps, orifice dimensions, operating pressure/enthalpy. | Validation error and confidence in CFD workflow. | 2; 4.1; Table 6; Fig. 7 | Use as an example of grounding CFD in measurements. | Only validates the concentric orifice directly. |
| Richardson extrapolation mesh study | Six mesh densities are compared using pressure drop, enthalpy, and mass flow as target outputs. The selected mesh has extrapolated errors under 1% for the reported outputs. | Mesh sizes/cell counts and CFD output variables. | Estimated numerical error and selected grid. | 3.4; Fig. 5; Table 5 | Use for mesh convergence/reporting structure. | Mesh convergence targets should be adapted for separator objectives. |

### Figure and table lookup

| Figure/Table | Page(s) | What it shows | Why useful | Related section | Search terms |
| --- | --- | --- | --- | --- | --- |
| Fig. 1 - Field testing facilities and tapings | p.3 | Shows field-test layout and pressure tap/instrumentation connections. | Best visual for validation setup and measurement logic. | 2 | field test; pressure taps |
| Fig. 3 - Flow-meter geometries | p.5 | Shows computational domains for concentric/eccentric/segmental orifice, Nozzle, and Venturi meters. | Useful for comparing geometry shapes in CFD. | 3.1 | geometry; computational domain |
| Table 2 - CFD modelling parameters | p.6 | Lists solver type, simulation type, gravity, equations, phases, discretisation, Courant number, and initialization. | Most useful Fluent settings table in the uploaded files. | 3.3 | Fluent settings; solver parameters |
| Fig. 5 / Table 5 - Mesh refinement study | p.7 | Shows mesh refinement and error comparison for pressure drop, enthalpy, and mass flow. | Useful template for mesh convergence analysis. | 3.4 | mesh refinement; Richardson extrapolation |
| Figs. 9-16 - Pressure/velocity/TKE/thermal contours | p.9-p.14 | Show contour results for pressure, velocity, turbulent kinetic energy, temperature, enthalpy, and entropy. | Useful as a result-presentation template for Fluent CFD. | 4.2 | contours; pressure; velocity; TKE; enthalpy |

---

## P3: Merbecks et al. 2025 - GeoProp geofluid property framework

**Full title:** GeoProp: A thermophysical property modelling framework for single and two-phase geothermal geofluids  
**Authors:** Tristan Merbecks; Allan M. M. Leal; Paola Bombarda; Paolo Silva; Dario Alfani; Martin O. Saar  
**Year:** 2025  
**Document type:** Research article  
**Source file:** `1-s2.0-S0375650524002323-main(1).pdf`  
**DOI / source URL:** https://doi.org/10.1016/j.geothermics.2024.103146

### Fast lookup summary

| Field | Quick note |
| --- | --- |
| Main topic | Thermophysical property and phase-partition modelling for geothermal geofluids |
| Best use | Use this when you need to justify why fluid properties, brine salinity, NCGs, phase partitioning, enthalpy, density, viscosity, and heat content matter for geothermal simulations. |
| Key methods/models | Framework coupling Reaktoro, CoolProp, and ThermoFun; comparison of pure-fluid, binary-fluid, reactive, and empirical geofluid models; validation against brine data. |
| Important outputs | Validated property predictions for brines/geofluids, comparison of heat-release curves, and architecture for coupling partition and property calculations. |
| Relevance to your CFD / geothermal separator work | Useful background for setting realistic water/steam/brine properties and explaining the limits of pure-water assumptions. It does not provide Fluent separator settings, but it helps justify property choices and thermodynamic assumptions. |
| Cautions / limitations | This is a modelling-framework paper, not a CFD paper, so use it for property modelling rather than mesh or boundary-condition decisions. |

### Detailed section dictionary

Use this section when you need to know exactly where to look inside the paper. Each entry gives the page range, what the section contains, the best search terms, what the section is useful for, and any limitations.

#### 1. Abstract / Article info

- **Pages:** p.1
- **Section type:** Front matter
- **What this section contains:** This section summarises the GeoProp framework and states the core problem: geothermal techno-economic evaluation depends on accurate thermophysical properties, but universal geofluid models are lacking. It explains that GeoProp couples phase-partitioning tools such as Reaktoro with property engines such as CoolProp and ThermoFun.
- **Best search terms:** GeoProp; thermophysical properties; phase behaviour; Reaktoro; CoolProp
- **Use this section when:** Use this for a concise statement of the paper's problem and contribution.
- **Important figures/tables/equations:** Keywords; abstract
- **CFD/geothermal relevance:** Useful for property-modelling justification.
- **Limitation note:** No detailed equations here.

#### 2. 1. Introduction

- **Pages:** p.1-p.3
- **Section type:** Background / motivation
- **What this section contains:** The introduction frames geothermal energy as dispatchable renewable heat and power and explains why binary ORC plants are important for lower-enthalpy resources. It also explains why geofluid composition, brines, NCGs, scaling/corrosion, and thermophysical properties affect power-plant design and resource evaluation.
- **Best search terms:** geofluid; ORC; brine; NCG; scaling; thermophysical properties
- **Use this section when:** Use this when writing background on why pure-water assumptions can be risky.
- **Important figures/tables/equations:** Fig. 1 ORC schematic
- **CFD/geothermal relevance:** Helpful for connecting geofluid properties to plant design.
- **Limitation note:** It is not a Fluent CFD setup section.

#### 3. 2. Scope

- **Pages:** p.3
- **Section type:** Problem definition
- **What this section contains:** This section defines the modelling scope: geothermal system simulations require density, enthalpy, entropy, viscosity, thermal conductivity, phase behaviour, and composition-specific properties over site-specific temperature/pressure ranges. It clarifies what kinds of geofluids and operating conditions property models must handle.
- **Best search terms:** density; enthalpy; viscosity; salinity; site-specific geofluid
- **Use this section when:** Use this when listing required fluid properties for simulation or techno-economic analysis.
- **Important figures/tables/equations:** Scope paragraphs
- **CFD/geothermal relevance:** Very useful for explaining property input needs before CFD/ORC modelling.
- **Limitation note:** It sets scope rather than giving final data.

#### 4. 3. Modelling approaches

- **Pages:** p.3
- **Section type:** Approach overview
- **What this section contains:** This section introduces the four broad modelling approaches reviewed in the paper: pure fluids, incompressible binary fluids, chemically reactive systems, and empirical geofluid models. It is a map for choosing the right subsection depending on the fluid-composition complexity.
- **Best search terms:** pure fluid; binary brine; reactive system; empirical model
- **Use this section when:** Use this as the navigation point for property-modelling options.
- **Important figures/tables/equations:** Subsection structure
- **CFD/geothermal relevance:** Helpful lookup structure for property models.
- **Limitation note:** The header is mainly organisational.

#### 5. 3.1. Pure fluids

- **Pages:** p.3
- **Section type:** Pure-fluid property models
- **What this section contains:** This section explains when geofluids can be approximated as pure water or another dominant pure component. It references high-fidelity equations of state such as Wagner-Pruß for water and notes that pure-component models can work well only when compositional effects are negligible.
- **Best search terms:** pure water; Wagner-Pruß; IAPWS; equation of state; EOS
- **Use this section when:** Use this when considering whether a water/steam property model is sufficient.
- **Important figures/tables/equations:** Pure water specific volume and saturation figures later
- **CFD/geothermal relevance:** Useful for discussing simplified CFD water/steam assumptions.
- **Limitation note:** Pure-fluid approximation can miss brine and NCG effects.

#### 6. 3.2. Incompressible binary fluids

- **Pages:** p.3
- **Section type:** Binary-fluid property models
- **What this section contains:** This section reviews EOS/property models for industrial binary fluids such as seawater, lithium bromide, calcium chloride, and potassium carbonate solutions. It highlights that these models have limited applicability ranges and usually cannot represent mixtures of multiple brines and gases.
- **Best search terms:** seawater; NaCl; lithium bromide; incompressible; CoolProp
- **Use this section when:** Use this when looking for brine-property modelling options and limitations.
- **Important figures/tables/equations:** Table 1 binary EOS applicability range
- **CFD/geothermal relevance:** Useful if your geothermal fluid is approximated as a saline brine.
- **Limitation note:** Not general enough for complex geothermal fluids.

#### 7. 3.3. Chemically reactive systems

- **Pages:** p.3-p.6
- **Section type:** Reactive equilibrium modelling
- **What this section contains:** This section treats the geofluid as a reactive chemical system where species can partition into gas, aqueous, and solid/mineral phases. It explains Gibbs-energy minimisation, phase/species amounts, Reaktoro, ThermoFun, and why reactive modelling is powerful but computationally heavier.
- **Best search terms:** chemical equilibrium; Gibbs minimisation; Reaktoro; ThermoFun; aqueous phase; mineral phase
- **Use this section when:** Use this when explaining phase partitioning, mineral scaling risk, or chemically realistic geofluid modelling.
- **Important figures/tables/equations:** Fig. 2 reactive system; Figs. 3-4 EOS comparisons
- **CFD/geothermal relevance:** Useful for justifying NCG/brine/phase partition assumptions.
- **Limitation note:** May be too complex for a basic Fluent material setup.

#### 8. 3.4. Empirical models for geofluids

- **Pages:** p.6
- **Section type:** Empirical geofluid models
- **What this section contains:** This section reviews empirical models for mixtures such as water-CO2-salt systems, especially Spycher-Pruess models. It explains that these models can estimate equilibrium phase compositions but often do not directly provide full thermophysical properties.
- **Best search terms:** Spycher-Pruess; CO2; salinity correction; empirical phase partitioning
- **Use this section when:** Use this when discussing CO2/NCG partitioning or empirical geofluid models.
- **Important figures/tables/equations:** Model descriptions
- **CFD/geothermal relevance:** Useful for geofluid phase behaviour background.
- **Limitation note:** Empirical assumptions can restrict generality.

#### 9. 4. GeoProp

- **Pages:** p.6-p.7
- **Section type:** Framework architecture
- **What this section contains:** This section presents GeoProp as a framework that couples partition models with property models through a shared Fluid data structure. It explains the architecture, how species and phases are stored, and how calculation engines can be swapped or chained.
- **Best search terms:** GeoProp architecture; Fluid data structure; partition model; property model; engine coupling
- **Use this section when:** Use this when explaining how phase equilibrium and property calculation can be linked.
- **Important figures/tables/equations:** Fig. 5 GeoProp architecture
- **CFD/geothermal relevance:** Useful if you want to mention modern geofluid-property workflows.
- **Limitation note:** Not directly implementable in Fluent without additional coupling.

#### 10. 5. Validation

- **Pages:** p.7-p.8
- **Section type:** Validation
- **What this section contains:** This section validates GeoProp against field geofluid samples from Dagestan and synthetic datasets such as seawater and lithium bromide. It compares predicted density and enthalpy against measured or established model data across temperature ranges.
- **Best search terms:** validation; Dagestan brines; density; speed of sound; specific enthalpy
- **Use this section when:** Use this when you need evidence that property calculations were checked against data.
- **Important figures/tables/equations:** Table 2 composition; Figs. 6-7 density/enthalpy comparisons
- **CFD/geothermal relevance:** Good for discussing uncertainty in property modelling.
- **Limitation note:** Validation covers selected brines and does not validate CFD.

#### 11. 6. Case study

- **Pages:** p.8
- **Section type:** Heat-content case study
- **What this section contains:** This section compares heat released by four geofluids in a binary ORC primary heat exchanger: water, brine, water with NCG, and brine with NCG. It shows that salts and NCGs can change phase behaviour, heat-release curves, vapour quality, and apparent resource potential.
- **Best search terms:** heat content; TQ curve; brine; NCG; binary ORC; vapour quality
- **Use this section when:** Use this when arguing that fluid composition changes usable heat and plant design.
- **Important figures/tables/equations:** Fig. 8 TQ curves; Tables 3-4 geofluid compositions/inlet conditions
- **CFD/geothermal relevance:** Useful for thermodynamic context around separator inlet conditions.
- **Limitation note:** The example is property-focused, not a detailed separator simulation.

#### 12. 7. Conclusions

- **Pages:** p.8-p.9
- **Section type:** Takeaways
- **What this section contains:** The conclusion states that existing models often handle either phase partitioning or property calculation, while GeoProp links both. It emphasises that accurate geofluid properties are needed to quantify resource potential and optimise geothermal power plants.
- **Best search terms:** conclusion; coupled property modelling; geothermal resource potential
- **Use this section when:** Use this for final takeaways and broad justification.
- **Important figures/tables/equations:** Final paragraphs
- **CFD/geothermal relevance:** Good final citation for property-model importance.
- **Limitation note:** Conclusions are high-level.

#### 13. Appendix A. Chemical equilibrium

- **Pages:** p.9
- **Section type:** Appendix / theory
- **What this section contains:** This appendix gives the thermodynamic formulation of chemical equilibrium using Gibbs free energy minimisation under isothermobaric conditions. It is useful when you need the mathematical foundation behind reactive phase-partition calculations.
- **Best search terms:** Gibbs free energy; chemical potential; equilibrium; constraints
- **Use this section when:** Use this for deeper theory or equations behind Reaktoro-style equilibrium.
- **Important figures/tables/equations:** Equations 14 onward
- **CFD/geothermal relevance:** Useful for property/phase partition theory.
- **Limitation note:** Probably too detailed for a basic literature review.

#### 14. Appendix B. Spycher-Pruss 2009 phase partitioning model

- **Pages:** p.9-p.10
- **Section type:** Appendix / empirical model
- **What this section contains:** This appendix summarises the Spycher-Pruss 2009 phase-partitioning model for CO2-water systems. It is a targeted lookup area for the empirical assumptions and equations behind that model.
- **Best search terms:** Spycher-Pruss 2009; CO2-water; VLE; phase partition
- **Use this section when:** Use this when you specifically need the details of the Spycher-Pruss model.
- **Important figures/tables/equations:** Appendix equations
- **CFD/geothermal relevance:** Useful for CO2/NCG equilibrium discussion.
- **Limitation note:** Specialised model with limited scope.

### Keyword lookup table

| Keyword / phrase | Category | Location / section | Meaning in this paper | Synonyms / related search terms | Use cases |
| --- | --- | --- | --- | --- | --- |
| GeoProp | Framework | P3 Abstract; 4 | Framework coupling geofluid phase partitioning and property calculations. | geofluid property framework; property engine coupling | Search for the paper's main contribution. |
| Reaktoro | Software/model engine | P3 Abstract; 3.3; 4 | Chemical equilibrium and phase-partitioning engine used in GeoProp. | reactive transport; equilibrium solver | Search when discussing phase partitioning. |
| CoolProp | Property engine | P3 Abstract; 3.1-3.2; 4 | Thermophysical property library used for pure and binary/incompressible fluids. | fluid property library; EOS | Search for property model sources. |
| ThermoFun | Property engine | P3 Abstract; 3.3; 4 | Thermodynamic database/property tool used for chemically reactive systems. | thermodynamic data; aqueous species | Search when discussing reactive geofluid properties. |
| Non-condensable gases (NCG) | Geofluid chemistry | P3 1; 6 | Gases such as CO2 that affect phase behaviour and heat content in geothermal systems. | CO2; gas impurities; dissolved gas | Search when explaining why pure water is insufficient. |
| Vapour-liquid equilibrium (VLE) | Phase behaviour | P3 3.3; Appendix B | Equilibrium calculation defining how components distribute between vapour and liquid phases. | phase partition; flash calculation | Search when discussing two-phase geofluid properties. |
| Brine salinity | Geofluid property | P3 3.2; 5; 6 | Dissolved salts change density, enthalpy, phase behaviour, and heat-release curves. | NaCl; seawater; dissolved salts | Search when justifying brine versus pure-water modelling. |
| TQ curve / heat content | Thermodynamic result | P3 6 | Temperature-heat release curve used to compare usable heat from different geofluids. | heat released; primary heat exchanger; heat-content curve | Search when linking properties to ORC heat exchange. |

### Methods / model / data lookup

| Method / model / dataset | Details | Inputs | Outputs | Where discussed | Why useful | Caveats |
| --- | --- | --- | --- | --- | --- | --- |
| GeoProp coupled property framework | GeoProp links phase partitioning engines with property engines through a shared Fluid data structure. It allows complex geofluid composition and phase behaviour to be combined with thermophysical property calculation. | Fluid composition, T-P conditions, selected partition model, selected property model. | Phase amounts, compositions, density, enthalpy, heat content, property curves. | 4; Fig. 5 | Use to justify realistic geofluid-property modelling. | Not directly a CFD solver. |
| Brine/NCG heat-content case study | The paper compares water, brine, water+NCG, and brine+NCG in a binary ORC primary heat exchanger. It demonstrates how composition changes TQ curves and vapour quality. | Compositions, inlet T-P/heat content, reinjection temperature. | Heat-release curves, vapour quality trends, property differences. | 6; Fig. 8; Tables 3-4 | Use to explain why pure-water assumptions can mislead geothermal plant analysis. | Case is illustrative rather than a separator CFD validation. |

### Figure and table lookup

| Figure/Table | Page(s) | What it shows | Why useful | Related section | Search terms |
| --- | --- | --- | --- | --- | --- |
| Fig. 1 - Binary ORC schematic | p.2 | Shows the geothermal geofluid loop, working-fluid loop, and primary heat exchanger arrangement. | Useful for explaining how geofluid properties affect ORC heat input. | 1 | ORC schematic; geofluid |
| Table 1 - EOS applicability range | p.3 | Lists temperature/composition ranges for binary incompressible fluid EOS. | Useful for showing limits of brine-property models. | 3.2 | EOS; brine; applicability |
| Fig. 5 - GeoProp architecture | p.6 | Shows how partitioning and property models are coupled through GeoProp. | Best visual for the framework architecture. | 4 | GeoProp; architecture |
| Figs. 6-7 - Density and enthalpy validation | p.7-p.8 | Compare property predictions against data for brines and synthetic fluids. | Useful for validation discussion. | 5 | density; enthalpy; validation |
| Fig. 8 - TQ curves and vapour quality | p.8 | Compares heat release and vapour quality for water/brine/NCG cases. | Useful for explaining why fluid composition matters. | 6 | TQ curve; heat content; vapour quality |

---

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

## P5: Rivas-Cruz et al. 2015 - Geothermal steam separator review

**Full title:** Design and Evaluation of Geothermal Steam Separators: A Review of the State of Art  
**Authors:** Fernando Rivas-Cruz; Alfonso García-Gutiérrez; Juan I. Martínez-Estrella; Ángel A. Ortiz-Bolaños  
**Year:** 2015  
**Document type:** Review article / conference transaction  
**Source file:** `1032231(1).pdf`  
**DOI / source URL:** No DOI found in uploaded PDF; GRC Transactions Vol. 39, 2015

### Fast lookup summary

| Field | Quick note |
| --- | --- |
| Main topic | State-of-art review of geothermal steam-water separators, Webre separators, dryers, Bangma BOC, and Lazalde-Crabtree methods |
| Best use | Use this as the main lookup source for geothermal separator design history, separator types, Webre-type separators, Lazalde-Crabtree design logic, and Cerro Prieto separator evaluation context. |
| Key methods/models | Literature review; design/evaluation comparison matrix; discussion of separator/dryer design methods and software tools. |
| Important outputs | Design-history summary, key references, separator/dryer methodology comparison, and conclusions about Webre-type separator performance and Lazalde-Crabtree methodology. |
| Relevance to your CFD / geothermal separator work | Very important for your BOC/geothermal separator literature review because it directly references Bangma BOC dimensions and separator efficiency/steam quality targets. It is less detailed on CFD implementation. |
| Cautions / limitations | Because it is a review, it often summarizes older sources rather than presenting new experiments or CFD data. |

### Detailed section dictionary

Use this section when you need to know exactly where to look inside the paper. Each entry gives the page range, what the section contains, the best search terms, what the section is useful for, and any limitations.

#### 1. Abstract

- **Pages:** p.1
- **Section type:** Front matter
- **What this section contains:** The abstract states that the paper compiles and reviews theoretical and practical aspects of geothermal steam separator design and evaluation up to 2014. It also explains that the review is intended to support development of computational tools for new separator design and long-term performance evaluation, especially for Cerro Prieto.
- **Best search terms:** steam separators; design; evaluation; software; Lazalde-Crabtree; Cerro Prieto
- **Use this section when:** Use this for a concise statement of the review's purpose.
- **Important figures/tables/equations:** Keywords; abstract
- **CFD/geothermal relevance:** Directly relevant to geothermal separator literature review.
- **Limitation note:** It is a review rather than a new CFD study.

#### 2. 1. Introduction

- **Pages:** p.1
- **Section type:** Separator motivation
- **What this section contains:** The introduction explains that most geothermal fields are liquid-dominated and produce steam-water mixtures that must be separated before turbine admission. It identifies separator purpose, steam purity, turbine scaling/corrosion risk, mixture inlet speed, equipment geometry, and the need to check whether existing separators still operate in their design range.
- **Best search terms:** liquid-dominated field; steam-water separator; steam purity; scaling; corrosion; Webre
- **Use this section when:** Use this when writing why separators are necessary in geothermal plants.
- **Important figures/tables/equations:** Introductory paragraphs
- **CFD/geothermal relevance:** Very relevant for separator motivation and problem framing.
- **Limitation note:** Short section, so detailed design data are in the review.

#### 3. 2. Literature Review - overview

- **Pages:** p.1-p.2
- **Section type:** Review map
- **What this section contains:** This section explains that the authors selected and analysed literature on liquid-dominated geothermal separators, especially Webre-type separators and dryers. It acts as the main reference map for theories, procedures, efficiency assessment, and software tools used in geothermal separator design.
- **Best search terms:** literature review; Webre separator; dryer; design methods; efficiency assessment
- **Use this section when:** Use this as the central location for older separator references and design-method summaries.
- **Important figures/tables/equations:** Table 1 comparison matrix
- **CFD/geothermal relevance:** Best uploaded source for separator design literature.
- **Limitation note:** It summarizes earlier papers, so cite original works when possible.

#### 4. 2. Literature Review - Bangma 1961 / BOC separator

- **Pages:** p.2
- **Section type:** Review subtopic
- **What this section contains:** This part summarises Bangma's bottom outlet cyclone separator work and contrasts BOC advantages with top-outlet cyclone designs. It reports pilot-test insights, the importance of steam-water ratio and inlet speed, and design-dimension relationships relative to inlet diameter.
- **Best search terms:** Bangma; BOC; bottom outlet cyclone; spiral inlet; tangential inlet; inlet speed
- **Use this section when:** Use this when you need BOC separator dimensions, advantages, or historical design basis.
- **Important figures/tables/equations:** Fig. 1 TOC/BOC schematic; Bangma dimension ratios
- **CFD/geothermal relevance:** Highly relevant to your BOC separator geometry and literature review.
- **Limitation note:** Because it is a summary, locate Bangma's original paper for exact graphs if needed.

#### 5. 2. Literature Review - Lazalde-Crabtree and Webre-type design

- **Pages:** p.2-p.3
- **Section type:** Review subtopic
- **What this section contains:** This part summarises Lazalde-Crabtree's geothermal separator and dryer design methodology, including process design, recommended parameters, efficiency, pressure drop, and steam quality targets. It states that the Webre-type separator is considered best for geothermal applications and that the method aims at high steam quality with economical pressure drop.
- **Best search terms:** Lazalde-Crabtree; Webre-type; steam quality; pressure drop; separator efficiency
- **Use this section when:** Use this when discussing empirical separator design or steam quality targets such as 99.95% or 99.9%.
- **Important figures/tables/equations:** Fig. 2 separator/dryer schematic; discussion of design methodology
- **CFD/geothermal relevance:** Very relevant to geothermal separator design/evaluation.
- **Limitation note:** The review does not reproduce every calculation detail.

#### 6. 2. Literature Review - Cerro Prieto and evaluation software

- **Pages:** p.3-p.6
- **Section type:** Review subtopic
- **What this section contains:** This part reviews studies and software tools used to evaluate long-running separators and dryers, especially in the Cerro Prieto Geothermal Field. It is useful for finding references that connect design methods, plant operation, measured steam quality, and performance checking.
- **Best search terms:** Cerro Prieto; separator software; dryer evaluation; long-term performance; operating conditions
- **Use this section when:** Use this when you want examples of field separator evaluation or software-assisted design/evaluation.
- **Important figures/tables/equations:** Table 1 matrix comparing references
- **CFD/geothermal relevance:** Useful for practical separator evaluation framing.
- **Limitation note:** Tool details vary by referenced source and may be outdated.

#### 7. 3. Conclusion

- **Pages:** p.6
- **Section type:** Takeaways
- **What this section contains:** The conclusion states that Webre-type separators and dryers are widely used in geothermal plants and that Lazalde-Crabtree is the most popular empirical methodology for design and evaluation. It also states that properly designed separators/dryers can achieve steam quality greater than 99.95%, supporting geothermal turbine operation.
- **Best search terms:** Webre-type; Lazalde-Crabtree; steam quality; 99.95%; conclusion
- **Use this section when:** Use this for final separator-design takeaways and concise claims.
- **Important figures/tables/equations:** Conclusion paragraph
- **CFD/geothermal relevance:** Strong literature-review conclusion for separator design background.
- **Limitation note:** Needs support from original references for detailed calculations.

### Keyword lookup table

| Keyword / phrase | Category | Location / section | Meaning in this paper | Synonyms / related search terms | Use cases |
| --- | --- | --- | --- | --- | --- |
| Webre-type separator | Separator type | P5 1; 2; 3 | Common geothermal steam-water separator/dryer type reviewed as widely used and effective. | Webre separator; centrifugal separator | Search for geothermal separator design context. |
| Bottom outlet cyclone (BOC) | Separator type | P5 2 - Bangma discussion | Cyclone separator with vapor discharge at the bottom, noted for simplicity and reduced corrosion/erosion problems. | Bangma separator; bottom outlet separator | Search for BOC design history and dimension ratios. |
| Lazalde-Crabtree methodology | Design method | P5 Abstract; 2; 3 | Empirical design/evaluation method widely used for geothermal separators and dryers. | separator efficiency method; empirical separator design | Search for design/evaluation method references. |
| Steam quality | Performance metric | P5 1; 2; 3 | Percent vapour purity after separation; target values around 99.95% are discussed for turbine operation. | vapor quality; separator purity | Search for separator performance targets. |
| Cerro Prieto Geothermal Field | Case context | P5 Abstract; 1; 2 | Mexican geothermal field used as a motivating case for separator/dryer evaluation tools. | CPGF; Cerro Prieto | Search for field separator evaluation context. |
| Spiral inlet | Separator geometry | P5 2 - Bangma discussion | Inlet geometry compared against tangential inlet in Bangma's BOC tests. | spiral entry; inlet geometry | Search for inlet geometry effects. |
| Dryer | Separator auxiliary equipment | P5 1; 2; 3 | Equipment used with separators to further improve steam quality before turbines. | steam dryer; moisture removal | Search when discussing turbine protection. |
| Design/evaluation software | Tools | P5 Abstract; 2 | Computational tools mentioned for separator/dryer design and performance evaluation. | computer program; separator evaluation tool | Search for software-oriented review material. |

### Methods / model / data lookup

| Method / model / dataset | Details | Inputs | Outputs | Where discussed | Why useful | Caveats |
| --- | --- | --- | --- | --- | --- | --- |
| Geothermal separator literature review | The paper synthesises prior work on separator/dryer design, evaluation, Bangma BOC tests, Webre separators, and Lazalde-Crabtree methodology. It also provides a comparison matrix of reviewed references. | Published separator studies, design methods, performance/evaluation tools. | Summary of methods, separator types, steam quality targets, design/evaluation features. | 2; Table 1 | Use as the primary separator literature map. | Second-hand summaries should be traced to originals when exact values matter. |
| Lazalde-Crabtree empirical design/evaluation method | The review identifies Lazalde-Crabtree as a widely used method for geothermal separator and dryer design/evaluation. It links the method to high steam quality and economical pressure drop. | Separator flow conditions, geometry, particle/drop behaviour, steam quality target. | Design dimensions, efficiency, pressure drop, steam quality. | 2; 3 | Use for empirical geothermal separator design context. | Original method details are not fully reproduced. |

### Figure and table lookup

| Figure/Table | Page(s) | What it shows | Why useful | Related section | Search terms |
| --- | --- | --- | --- | --- | --- |
| Fig. 1 - TOC and BOC schematic | p.2 | Shows top outlet cyclone and bottom outlet cyclone separator concepts. | Best visual for BOC/TOC conceptual comparison. | 2 | BOC; TOC; cyclone separator |
| Fig. 2 - Steam-water separator and steam dryer | p.2 | Shows geothermal separator and dryer schematic arrangements from Lazalde-Crabtree discussion. | Useful for explaining separator/dryer equipment roles. | 2 | separator; dryer |
| Table 1 - Matrix comparing references | p.5-p.6 | Compares reviewed works by separator type, design, evaluation, software, plant, and methodology features. | Key lookup table for literature-review planning. | 2 | comparison matrix; references |

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

## Combined methods and data lookup

| Paper ID | Method / model / dataset | Details | Inputs | Outputs | Where discussed | Why useful | Caveats |
| --- | --- | --- | --- | --- | --- | --- | --- |
| P1 | EES thermodynamic plant model | A system-level model couples a two-phase geofluid/well model with aboveground ORC component equations. It calculates states, component heat duties, power, efficiency, and economic indicators. | Reservoir conditions, productivity index, wellhead pressure, ambient temperature, component efficiencies, working-fluid properties. | Net power, efficiency, specific power, heat duties, CAPEX, component sizing/costs. | 2.2. System modelling; 2.2.2; 2.2.3; 2.2.4 | Use as a template for plant-level analysis and ORC equations. | Not a CFD or separator-internal model. |
| P1 | Parametric techno-economic comparison | TIT, wellhead pressure, heat-exchanger pinch/approach temperatures, and working fluid are varied to identify performance optima. The proposed plant is compared against single-flash and flash-binary references. | Variable bounds, working fluids, geothermal case assumptions. | Performance trends, optimal cases, CAPEX and specific-power comparisons. | 2.2.5; 2.3; 4 | Use when showing how design variables affect plant performance. | Case-specific and relies on cost correlations. |
| P2 | ANSYS Fluent two-phase geothermal CFD | Steady and transient 3D simulations of geothermal steam-water/brine flow through differential pressure meter geometries. The model uses mixture multiphase physics, energy equation, and SST k-omega turbulence. | Mass flow, steam/liquid mass split, enthalpy, pressure, temperature, geometry dimensions, wall roughness. | Pressure drop, velocity, TKE, temperature, enthalpy, entropy, mass-flow prediction. | 3.1-3.4; 4 | Use as the strongest uploaded template for Fluent settings and result presentation. | Meter geometries differ from separator geometry. |
| P2 | Field validation with Indonesian geothermal wells | The concentric orifice model is validated against field data from four wells using lip-pressure and separator testing methods. Agreement is assessed for pressure drop, mass flow, and enthalpy. | Well test data, pressure taps, orifice dimensions, operating pressure/enthalpy. | Validation error and confidence in CFD workflow. | 2; 4.1; Table 6; Fig. 7 | Use as an example of grounding CFD in measurements. | Only validates the concentric orifice directly. |
| P2 | Richardson extrapolation mesh study | Six mesh densities are compared using pressure drop, enthalpy, and mass flow as target outputs. The selected mesh has extrapolated errors under 1% for the reported outputs. | Mesh sizes/cell counts and CFD output variables. | Estimated numerical error and selected grid. | 3.4; Fig. 5; Table 5 | Use for mesh convergence/reporting structure. | Mesh convergence targets should be adapted for separator objectives. |
| P3 | GeoProp coupled property framework | GeoProp links phase partitioning engines with property engines through a shared Fluid data structure. It allows complex geofluid composition and phase behaviour to be combined with thermophysical property calculation. | Fluid composition, T-P conditions, selected partition model, selected property model. | Phase amounts, compositions, density, enthalpy, heat content, property curves. | 4; Fig. 5 | Use to justify realistic geofluid-property modelling. | Not directly a CFD solver. |
| P3 | Brine/NCG heat-content case study | The paper compares water, brine, water+NCG, and brine+NCG in a binary ORC primary heat exchanger. It demonstrates how composition changes TQ curves and vapour quality. | Compositions, inlet T-P/heat content, reinjection temperature. | Heat-release curves, vapour quality trends, property differences. | 6; Fig. 8; Tables 3-4 | Use to explain why pure-water assumptions can mislead geothermal plant analysis. | Case is illustrative rather than a separator CFD validation. |
| P4 | EWF-DPM annular-flow CFD | A transient Fluent model combines Eulerian Wall Film for wall liquid with DPM for droplets in the gas core. UDFs implement entrainment correlations and two-way coupling captures droplet/gas exchange. | Gas/liquid flow conditions, film injection, droplet size, entrainment correlation, mesh/domain. | Film thickness, film velocity, entrainment/deposition rates, entrainment fraction. | 2.1-2.6; 3 | Use for annular flow modelling with film-droplet coupling. | Air-water and pipe geometry, not geothermal separator. |
| P4 | Entrainment correlation assessment | Three entrainment models are tested, and Bertodano gives the best agreement with experimental entrainment fractions. The section highlights sensitivity to critical film Reynolds number. | Correlation parameters, film Reynolds number, air-water conditions. | Prediction error versus experiments; recommended correlation. | 2.5; 3; 4 | Use to discuss entrainment-correlation uncertainty. | Correlation transfer to geothermal conditions is uncertain. |
| P5 | Geothermal separator literature review | The paper synthesises prior work on separator/dryer design, evaluation, Bangma BOC tests, Webre separators, and Lazalde-Crabtree methodology. It also provides a comparison matrix of reviewed references. | Published separator studies, design methods, performance/evaluation tools. | Summary of methods, separator types, steam quality targets, design/evaluation features. | 2; Table 1 | Use as the primary separator literature map. | Second-hand summaries should be traced to originals when exact values matter. |
| P5 | Lazalde-Crabtree empirical design/evaluation method | The review identifies Lazalde-Crabtree as a widely used method for geothermal separator and dryer design/evaluation. It links the method to high steam quality and economical pressure drop. | Separator flow conditions, geometry, particle/drop behaviour, steam quality target. | Design dimensions, efficiency, pressure drop, steam quality. | 2; 3 | Use for empirical geothermal separator design context. | Original method details are not fully reproduced. |
| P6 | Three-field annular-flow CFD model | The thesis models steam core, wall film, and droplets as separate fields in Fluent. Entrainment is based on Okawa 1D correlations and deposition is calculated through DPM particle trajectories. | Mass flux, quality, geometry, film/droplet initial conditions, correlations. | Mass flow rates for steam/film/droplets, deposition rate, film thickness, comparison with experiments. | 1; 3; 4; 5 | Use for intuition about three-field mass exchange. | BWR pipe model, not geothermal separator. |
| P6 | DPM transverse velocity sensitivity | The thesis applies transverse velocity to droplets at entrainment to improve match with the Okawa deposition trend. This shows droplet initial conditions can strongly affect deposition behaviour. | Droplet injection velocity/direction, gas/film conditions. | Changed deposition rate and better correlation agreement. | 4.2.3; 5; 6 | Use when discussing DPM sensitivity to injection assumptions. | Implementation-specific and needs validation for other geometries. |

---

## Combined figure and table lookup

| Paper ID | Figure/Table | Page(s) | What it shows | Why useful | Related section | Search terms |
| --- | --- | --- | --- | --- | --- | --- |
| P1 | Fig. 1 - Layout of the geothermal power plant | p.4 | Shows proposed plant layout with separator, additional evaporator, ORC loop, cooling-water loop, and dry cooler. | Best visual for understanding the proposed process architecture. | 2.1 | plant layout; additional evaporator; separator |
| P1 | Fig. 2 - ORC temperature-entropy diagram | p.4 | Shows the subcritical ORC with dry/retrograde working fluid behaviour. | Useful for explaining working-fluid thermodynamic path. | 2.1 | T-s diagram; ORC |
| P1 | Fig. 3 - Methodology schematic | p.5 | Maps modelling assumptions, two-phase geofluid model, and aboveground system model. | Useful for quickly explaining the modelling workflow. | 2.2 | methodology; simulation workflow |
| P1 | Fig. 6 - Productivity curve and quality | p.10 | Shows well mass flow and quality as a function of wellhead pressure. | Useful for linking wellhead pressure to separator inlet conditions. | 4 | productivity curve; quality |
| P1 | Tables 8-13 - Results/cost comparison | p.10-p.14 | Provide working-fluid results, heat transfer data, cooling system data, and comparison with reference systems. | Useful for extracting headline numbers and economic comparisons. | 4 | net power; CAPEX; specific power |
| P2 | Fig. 1 - Field testing facilities and tapings | p.3 | Shows field-test layout and pressure tap/instrumentation connections. | Best visual for validation setup and measurement logic. | 2 | field test; pressure taps |
| P2 | Fig. 3 - Flow-meter geometries | p.5 | Shows computational domains for concentric/eccentric/segmental orifice, Nozzle, and Venturi meters. | Useful for comparing geometry shapes in CFD. | 3.1 | geometry; computational domain |
| P2 | Table 2 - CFD modelling parameters | p.6 | Lists solver type, simulation type, gravity, equations, phases, discretisation, Courant number, and initialization. | Most useful Fluent settings table in the uploaded files. | 3.3 | Fluent settings; solver parameters |
| P2 | Fig. 5 / Table 5 - Mesh refinement study | p.7 | Shows mesh refinement and error comparison for pressure drop, enthalpy, and mass flow. | Useful template for mesh convergence analysis. | 3.4 | mesh refinement; Richardson extrapolation |
| P2 | Figs. 9-16 - Pressure/velocity/TKE/thermal contours | p.9-p.14 | Show contour results for pressure, velocity, turbulent kinetic energy, temperature, enthalpy, and entropy. | Useful as a result-presentation template for Fluent CFD. | 4.2 | contours; pressure; velocity; TKE; enthalpy |
| P3 | Fig. 1 - Binary ORC schematic | p.2 | Shows the geothermal geofluid loop, working-fluid loop, and primary heat exchanger arrangement. | Useful for explaining how geofluid properties affect ORC heat input. | 1 | ORC schematic; geofluid |
| P3 | Table 1 - EOS applicability range | p.3 | Lists temperature/composition ranges for binary incompressible fluid EOS. | Useful for showing limits of brine-property models. | 3.2 | EOS; brine; applicability |
| P3 | Fig. 5 - GeoProp architecture | p.6 | Shows how partitioning and property models are coupled through GeoProp. | Best visual for the framework architecture. | 4 | GeoProp; architecture |
| P3 | Figs. 6-7 - Density and enthalpy validation | p.7-p.8 | Compare property predictions against data for brines and synthetic fluids. | Useful for validation discussion. | 5 | density; enthalpy; validation |
| P3 | Fig. 8 - TQ curves and vapour quality | p.8 | Compares heat release and vapour quality for water/brine/NCG cases. | Useful for explaining why fluid composition matters. | 6 | TQ curve; heat content; vapour quality |
| P4 | Fig. 1 / Fig. 2 - Mesh and simulation tube | p.3-p.4 | Shows cross-section mesh and tube boundary sections with injection and annular zones. | Useful for understanding the CFD domain setup. | 2.1 | mesh; simulation domain |
| P4 | Table 1 - Simulation parameters | p.4 | Lists the simulation parameters taken from Sawant et al. for the annular-flow model. | Useful for identifying input cases. | 2 | simulation parameters |
| P4 | Tables 2-3 - Film thickness and wave velocity correlations | p.5 | Lists external correlations used to compare film thickness and film/wave velocity. | Useful as a correlation lookup. | 2.3-2.4 | film thickness; wave velocity |
| P4 | Fig. 5 - Simulation vs experimental entrainment fraction | p.7 | Compares predicted entrainment fraction against experimental data with error bars. | Important validation figure for the EWF-DPM model. | 3 | entrainment fraction; validation |
| P4 | Figs. 8-18 - Film/entrainment/droplet results | p.7-p.11 | Show film thickness, velocity, entrainment/deposition rates, droplet size, and EF trends. | Useful as results examples for annular flow. | 3 | film thickness; deposition; droplet size |
| P5 | Fig. 1 - TOC and BOC schematic | p.2 | Shows top outlet cyclone and bottom outlet cyclone separator concepts. | Best visual for BOC/TOC conceptual comparison. | 2 | BOC; TOC; cyclone separator |
| P5 | Fig. 2 - Steam-water separator and steam dryer | p.2 | Shows geothermal separator and dryer schematic arrangements from Lazalde-Crabtree discussion. | Useful for explaining separator/dryer equipment roles. | 2 | separator; dryer |
| P5 | Table 1 - Matrix comparing references | p.5-p.6 | Compares reviewed works by separator type, design, evaluation, software, plant, and methodology features. | Key lookup table for literature-review planning. | 2 | comparison matrix; references |
| P6 | Fig. 1 - Different flow regimes | PDF p.8 | Shows typical flow regimes including annular flow. | Useful for simple visual explanation of regime transition. | 2.1 | flow regimes; annular |
| P6 | Fig. 2 / Fig. 3 - Model setup and mesh | PDF p.14-p.15 | Shows the simplified model setup and cross-sectional mesh. | Useful for understanding the thesis CFD geometry. | 4.1 | setup; mesh |
| P6 | Fig. 5 - Deposition rate injection comparison | PDF p.17 | Compares deposition rate for different particle injection approaches. | Useful for showing sensitivity to droplet injection method. | 4.2.3 | deposition; particle injection |
| P6 | Figs. 6-15 - Results plots | PDF p.20-p.25 | Show 1D calculations, experimental comparisons, mass flow rates of three fields, film thickness, and deposition-rate comparisons. | Useful for trend extraction and results narrative. | 5 | mass flow; film thickness; deposition |

---

## Combined keyword index

| Paper ID | Keyword / phrase | Category | Location / section | Meaning in this paper | Synonyms / related search terms | Use cases |
| --- | --- | --- | --- | --- | --- | --- |
| P1 | Organic Rankine Cycle (ORC) | Plant cycle | P1 Abstract; 1; 2.1-2.2 | Closed-loop binary cycle used to convert geothermal heat into electricity via a secondary organic working fluid. | binary cycle; recuperative ORC; subcritical ORC | Search when you need plant layout, component equations, or working-fluid discussion. |
| P1 | Additional evaporator | Plant component | P1 2.1; 2.2.2; 4 | Novel component where separated geothermal steam condenses to partially evaporate the ORC working fluid. | steam condenser evaporator; EA; steam-condensing binary | Search when explaining the paper's main novelty. |
| P1 | Specific power output (SPO) | Performance metric | P1 2.2.3; 4; 5 | Power produced per unit geothermal fluid flow/resource input; used to compare plant technologies. | specific output; net power per geofluid flow | Search when comparing proposed system with flash-binary or single-flash. |
| P1 | Turbine inlet temperature (TIT) | Parameter | P1 2.2.5; 4 | ORC design variable that strongly affects thermal efficiency and net power output. | inlet temperature; expander inlet temperature | Search when discussing sensitivity analysis. |
| P1 | Wellhead pressure | Resource/well parameter | P1 2.2.1; 2.2.5; 4 | Operating variable that affects mass flow, flashing, and geothermal fluid quality at the surface. | separator inlet pressure; production pressure | Search when connecting well performance to plant output. |
| P1 | n-pentane / isopentane / n-butane | Working fluids | P1 2.2.6; 4 | Candidate dry organic fluids compared for ORC performance and environmental/safety properties. | ORC fluids; hydrocarbons; dry fluids | Search when justifying fluid selection. |
| P1 | CAPEX | Economics | P1 2.2.4; 4; 5 | Capital expenditure estimated from equipment costs and used to compare system economics. | capital investment; purchased equipment cost; PEC | Search when writing techno-economic analysis. |
| P1 | Flash-binary system | Comparator system | P1 Introduction; 2.3; 4 | Reference hybrid geothermal plant that combines flash and binary units. | single flash-ORC; flash-binary cycle | Search when comparing plant architectures. |
| P2 | Pressure differential flow meter | Instrumentation/CFD | P2 Abstract; 1; 3-4 | Device that estimates flow from pressure difference, including orifice, Nozzle, and Venturi meters. | DP meter; differential pressure device | Search for geothermal two-phase measurement geometry and results. |
| P2 | Mixture model | Multiphase CFD | P2 3.2; 3.3 | ANSYS multiphase approach used to represent water-vapour/steam and liquid water/brine phases as interpenetrating mixture fields. | mixture method; Eulerian mixture | Search when comparing Fluent multiphase model choices. |
| P2 | SST k-omega | Turbulence model | P2 3.2; 3.3; 5 | Turbulence model selected for the two-phase geothermal flow simulations. | k-omega SST; shear stress transport | Search for turbulence-model justification. |
| P2 | Energy equation | Thermal CFD | P2 1; 3.2; 4.2.5 | Equation added so temperature, enthalpy, and entropy changes can be analysed, unlike earlier geothermal orifice CFD. | enthalpy; temperature; thermodynamics | Search when justifying thermal field simulation. |
| P2 | Richardson extrapolation | Mesh convergence | P2 3.4 | Method used to assess mesh refinement error across six mesh densities. | mesh refinement; grid convergence; extrapolated error | Search when writing mesh independence/convergence. |
| P2 | Venturi | Flow-meter geometry | P2 3.1; 4.2 | Flow meter geometry that produced low pressure drop and low TKE compared with orifice geometries. | Venturi tube; pressure recovery | Search when comparing geometries. |
| P2 | Nozzle | Flow-meter geometry | P2 3.1; 4.2.1-4.2.5 | Flow meter geometry used for transient benchmark and shown to have lower pressure drop than orifice meters. | nozzle meter; convergent throat | Search when reviewing transient vs steady validation. |
| P2 | Turbulent kinetic energy (TKE) | CFD result variable | P2 4.2.4 | Result variable used to evaluate fluctuations and separation zones downstream of restrictions. | k; turbulence contour | Search for interpretation of turbulence contours. |
| P3 | GeoProp | Framework | P3 Abstract; 4 | Framework coupling geofluid phase partitioning and property calculations. | geofluid property framework; property engine coupling | Search for the paper's main contribution. |
| P3 | Reaktoro | Software/model engine | P3 Abstract; 3.3; 4 | Chemical equilibrium and phase-partitioning engine used in GeoProp. | reactive transport; equilibrium solver | Search when discussing phase partitioning. |
| P3 | CoolProp | Property engine | P3 Abstract; 3.1-3.2; 4 | Thermophysical property library used for pure and binary/incompressible fluids. | fluid property library; EOS | Search for property model sources. |
| P3 | ThermoFun | Property engine | P3 Abstract; 3.3; 4 | Thermodynamic database/property tool used for chemically reactive systems. | thermodynamic data; aqueous species | Search when discussing reactive geofluid properties. |
| P3 | Non-condensable gases (NCG) | Geofluid chemistry | P3 1; 6 | Gases such as CO2 that affect phase behaviour and heat content in geothermal systems. | CO2; gas impurities; dissolved gas | Search when explaining why pure water is insufficient. |
| P3 | Vapour-liquid equilibrium (VLE) | Phase behaviour | P3 3.3; Appendix B | Equilibrium calculation defining how components distribute between vapour and liquid phases. | phase partition; flash calculation | Search when discussing two-phase geofluid properties. |
| P3 | Brine salinity | Geofluid property | P3 3.2; 5; 6 | Dissolved salts change density, enthalpy, phase behaviour, and heat-release curves. | NaCl; seawater; dissolved salts | Search when justifying brine versus pure-water modelling. |
| P3 | TQ curve / heat content | Thermodynamic result | P3 6 | Temperature-heat release curve used to compare usable heat from different geofluids. | heat released; primary heat exchanger; heat-content curve | Search when linking properties to ORC heat exchange. |
| P4 | Annular flow | Flow regime | P4 Abstract; 1 | Gas-liquid regime with liquid film on the wall, gas in the core, and entrained droplets. | wall film flow; annular mist flow | Search for conceptual flow-regime background. |
| P4 | Discrete Phase Model (DPM) | Multiphase CFD | P4 2.2.1-2.2.2 | Eulerian-Lagrangian Fluent model used to track droplets in the gas core. | particle tracking; Lagrangian droplets | Search for droplet modelling details. |
| P4 | Eulerian Wall Film (EWF) | Wall-film model | P4 2.2.3 | Fluent model for thin liquid film on a wall, including source terms for entrainment/deposition. | thin film; wall film | Search for wall-film equations. |
| P4 | Entrainment fraction (EF) | Annular-flow metric | P4 Abstract; 1; 2; 3 | Fraction of total liquid entrained as droplets in the gas core. | droplet fraction; equilibrium entrainment fraction | Search for model output and validation comparison. |
| P4 | Bertodano correlation | Entrainment correlation | P4 2.5; 3; 4 | Empirical entrainment correlation that performed best in this paper's simulations. | Bertodano et al.; entrainment rate model | Search for the best-performing correlation. |
| P4 | Critical film Reynolds number | Correlation parameter | P4 1; 2.5; 4 | Threshold that controls whether entrainment starts and strongly affects entrainment predictions. | Relfc; onset of entrainment | Search when discussing why correlations differ. |
| P4 | Droplet size correlation | DPM input | P4 2.6; 3 | Empirical input for representative droplet diameter, affecting deposition and entrainment fraction. | particle diameter; SMD; droplet diameter | Search when defining DPM injection size. |
| P4 | Dryout | Safety/heat transfer | P4 1; 4 | Condition where the liquid film disappears and heat transfer deteriorates. | critical heat flux; film depletion | Search for motivation of annular-flow modelling. |
| P5 | Webre-type separator | Separator type | P5 1; 2; 3 | Common geothermal steam-water separator/dryer type reviewed as widely used and effective. | Webre separator; centrifugal separator | Search for geothermal separator design context. |
| P5 | Bottom outlet cyclone (BOC) | Separator type | P5 2 - Bangma discussion | Cyclone separator with vapor discharge at the bottom, noted for simplicity and reduced corrosion/erosion problems. | Bangma separator; bottom outlet separator | Search for BOC design history and dimension ratios. |
| P5 | Lazalde-Crabtree methodology | Design method | P5 Abstract; 2; 3 | Empirical design/evaluation method widely used for geothermal separators and dryers. | separator efficiency method; empirical separator design | Search for design/evaluation method references. |
| P5 | Steam quality | Performance metric | P5 1; 2; 3 | Percent vapour purity after separation; target values around 99.95% are discussed for turbine operation. | vapor quality; separator purity | Search for separator performance targets. |
| P5 | Cerro Prieto Geothermal Field | Case context | P5 Abstract; 1; 2 | Mexican geothermal field used as a motivating case for separator/dryer evaluation tools. | CPGF; Cerro Prieto | Search for field separator evaluation context. |
| P5 | Spiral inlet | Separator geometry | P5 2 - Bangma discussion | Inlet geometry compared against tangential inlet in Bangma's BOC tests. | spiral entry; inlet geometry | Search for inlet geometry effects. |
| P5 | Dryer | Separator auxiliary equipment | P5 1; 2; 3 | Equipment used with separators to further improve steam quality before turbines. | steam dryer; moisture removal | Search when discussing turbine protection. |
| P5 | Design/evaluation software | Tools | P5 Abstract; 2 | Computational tools mentioned for separator/dryer design and performance evaluation. | computer program; separator evaluation tool | Search for software-oriented review material. |
| P6 | Three-field approach | Model architecture | P6 Abstract; 1; 3-4 | Model with steam core, liquid film, and liquid droplets represented separately. | three fields; steam-film-droplet model | Search for overall CFD modelling philosophy. |
| P6 | Okawa correlations | Correlation set | P6 Abstract; 1; 3.2; 5 | 1D correlations used for entrainment and deposition benchmarks. | Okawa et al.; 1D correlations | Search for comparison model equations. |
| P6 | Transverse droplet velocity | Model improvement | P6 Abstract; 4.2.3; 5-6 | Additional droplet velocity component applied at entrainment to improve deposition behaviour and correlation agreement. | radial velocity; particle initial velocity | Search for DPM injection sensitivity. |
| P6 | Liquid film mass flow | Output variable | P6 2.2; 5 | Mass flow carried in the wall film; central variable for dryout and entrainment/deposition balance. | film flow rate; Wlf | Search for results plots and post-processing. |
| P6 | Deposition rate | Mass exchange | P6 3.2.1; 4.2.3; 5 | Rate at which droplets return from gas core to the film. | m_dep; droplet deposition | Search for droplet-wall interaction. |
| P6 | Entrainment rate | Mass exchange | P6 3.2.2; 5 | Rate at which liquid leaves the film and becomes droplets. | m_ent; droplet creation | Search for film-to-droplet source terms. |
| P6 | Lagrangian Particle Tracking (LPT) | Numerical method | P6 Nomenclature; 3.1.2; 4 | Trajectory-based droplet modelling method linked with DPM. | particle tracking; DPM | Search for droplet movement modelling. |
| P6 | Post-processing scripts | Workflow | P6 4.3; Appendices | Scripts/files used to average and process Fluent outputs for comparison plots. | automation; ASCII files; processing | Search for implementation workflow ideas. |

---

## Notes for using this dictionary

- Use the **Paper index** first to decide which paper is relevant to your task.
- Use the **Detailed section dictionary** to jump to a page range or section heading quickly.
- Use the **Keyword lookup table** when you only remember a concept, phrase, model, or variable.
- Use the **Methods / model / data lookup** when writing methodology, CFD setup, thermodynamic modelling, or validation sections.
- Use the **Figure and table lookup** when you need diagrams, results plots, model settings, or comparison tables for your own report.