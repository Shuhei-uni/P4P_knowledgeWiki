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
