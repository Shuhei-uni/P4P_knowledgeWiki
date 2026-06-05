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
