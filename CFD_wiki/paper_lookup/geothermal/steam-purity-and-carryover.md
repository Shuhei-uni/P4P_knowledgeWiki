# Paper 1 — Chan & Zarrouk 2023

**File:** `22(2).pdf`  
**Title:** *Modelling Particle Tracking of Moisture Droplets in Geothermal Steam Pipeline*  
**Main purpose:** This paper extends steam purity modelling by treating some carried-over water as droplets moving in the steam core, not just liquid film flowing along the pipe bottom. It is most useful when you need entrainment/deposition correlations, water wash effects, steam pipeline droplet behaviour, and limitations of SPDOT/GSP-type models.

## Best Use Cases

| Use this paper when you need... | Why this paper helps |
|---|---|
| A reason why steam quality can look acceptable but turbines still suffer erosion/scaling | The paper explains that micro-scale droplets can still damage turbines even when dryness limits appear satisfied. |
| A discussion of the difference between steam quality and steam purity | It explicitly frames quality as dryness and purity as cleanliness/mineral content. |
| Entrainment fraction and entrainment/deposition correlations | Section 2 gathers several correlations from two-phase flow literature and adapts them to geothermal pipeline modelling. |
| A research gap for CFD or droplet tracking | It states that separator droplet tracking has been studied, but pipeline droplet entrainment/deposition has not been well covered by CFD. |
| Water wash location optimisation | Section 4.7 compares water wash location effects on dryness, silica, and chloride concentration. |

## Section Dictionary

| Section | Page | What this section contains / when to use it |
|---|---:|---|
| **Abstract** | 1 | Use this for the short motivation of the paper: even very small water droplets in high-dryness geothermal steam can damage turbines over time. It also gives the paper’s central contribution: carryover analysis, droplet interactions, entrainment rate, and equipment limitations before the turbine. |
| **1.1 Geothermal power plants** | 1 | This section explains why older plants such as Wairakei benefited from long cross-country pipelines, which naturally scrubbed steam before it reached the turbine. Use it when arguing that compact modern power station layouts reduce pipe length and therefore reduce natural scrubbing time. |
| **1.2 Existing models** | 1 | This section summarises earlier steam purity models such as GSP and SPDOT. Use it when you want to explain what older models already included: separator efficiency, heat loss, pressure drop, mineral dilution, silica distribution, and water wash mass balance. |
| **1.3 Droplets carryover** | 1–2 | This section is key for explaining the difference between liquid film at the pipe bottom and droplets travelling with the steam core. Use it to justify why a two-phase, three-field view matters: steam, bottom liquid film, and entrained droplets must be treated separately. |
| **2. Entrainment correlations** | 2 | This section introduces why entrainment matters for steam purity and turbine damage. Use it when you need to frame entrainment as both a prediction tool for turbine risk and a design tool for improving moisture removal equipment. |
| **2.1 Entrainment fraction** | 2–3 | This is the most equation-heavy section for entrainment fraction models. Use it when you need definitions of entrainment fraction, droplet mass flow, total liquid mass flow, Weber number, liquid Reynolds number, and correlations such as Ishii & Mishima, Sawant, Al-Sarkhi, Pan & Hanratty, and Karami. |
| **2.2 Entrainment and deposition rate** | 3 | This section introduces the idea that entrainment and deposition are balanced at equilibrium. Use it when you want equations for entrainment rate, deposition rate, local film Reynolds number, droplet concentration, and critical liquid film conditions. |
| **3. Methodology** | 3–5 | This section explains how the paper constructs 24 model combinations from the entrainment and deposition correlations. Use it when you need assumptions, such as entrainment occurring in the separator and entrainment/deposition occurring simultaneously along the steam pipeline. |
| **4. Discussion** | 5 | This section sets up the model comparison against Mills & Lovelock field data for basic and water-wash cases. Use it when you need the model evaluation criteria: MAE, MAPE, RMSE, steam dryness target, silica target, and chloride target. |
| **4.1 Performance of the entrainment models** | 5 | This section compares GSP, SPDOT, and entrainment-model predictions. Use it to show that modelling water droplets separately can reduce the predicted separator efficiency and change the estimated carryover reaching downstream equipment. |
| **4.2 Entrainment and deposition rate across the length** | 5–6 | This section explains how entrainment and deposition rates change along the pipeline. Use it when discussing how water wash increases entrainment in the section where it is introduced, followed by changing deposition behaviour downstream. |
| **4.3 Pipe length optimisation** | 6–7 | This section varies pipe length from 50 m to 150 m and compares pressure drop, condensation, entrainment, deposition, and final steam quality. Use it when discussing the trade-off between longer pipes for scrubbing and extra pressure drop/condensate generation. |
| **4.4 Pipe diameter optimisation** | 7 | This section varies pipe diameter from 0.8 m to 1.2 m. Use it when explaining that larger diameters can reduce pressure drop and entrainment rate while increasing condensation and deposition behaviour. |
| **4.5 Insulation thickness optimisation** | 7–8 | This section varies calcium silicate insulation thickness from 0.025 m to 0.125 m. Use it when you need the counterintuitive point that thicker insulation can reduce condensation and therefore reduce mineral dilution/removal benefits. |
| **4.6 Calibrating entrainment model to match field data** | 8 | This section is useful for explaining why equilibrium assumptions may fail in real steamfields because turbulence and fittings disturb the flow. Use it when discussing calibration, drain-pot placement, scrubber overprediction, and why the best calibrated model matched basic field data very closely. |
| **4.7 Water wash optimisation** | 8–9 | This section compares water wash locations and explains how water wash improves purity but slightly reduces dryness. Use it when you need a direct statement that upstream washing can improve purity and that drain-pot efficiency matters for chloride removal. |
| **4.8 Optimisation exercises conclusion** | 9 | This section gives the design lesson from the optimisation exercises. Use it when arguing that simply upgrading equipment is not enough if the steamfield layout is too short for equipment to reach its intended efficiency. |
| **5. Conclusion** | 9–10 | This section summarises the main findings and limitations. Use it for final report points: no close-to-perfect steam purity model exists yet, large-diameter pipeline correlations are limited, pipe diameter/insulation/water wash affect entrainment and purity, and CFD studies are still needed. |

## Keyword / Search Table

| Keyword | What it means here | Best section/page |
|---|---|---|
| Steam quality | Dryness of the steam; relates to liquid content. | 1.1–1.3, p.1–2 |
| Steam purity | Cleanliness/mineral content of steam; relates to silica/chloride/TDS. | 1.1–1.3, p.1–2 |
| Droplet carryover | Water droplets travelling with the steam core rather than only as bottom film. | 1.3, p.1–2 |
| Two-phase, three-field flow | Steam, liquid film, and droplets treated as different fields. | 1.3, p.1–2 |
| Entrainment fraction | Ratio of droplet flow to total liquid flow. | 2.1, p.2–3 |
| Deposition rate | Rate at which droplets deposit from steam core to wall/bottom film. | 2.2, p.3 |
| Water wash | Water injection to capture volatile minerals; can reduce dryness slightly. | 4.7, p.8–9 |
| Pipe length optimisation | Varying section length to assess pressure drop, condensation, and purity. | 4.3, p.6–7 |
| Pipe diameter optimisation | Varying diameter to assess entrainment/deposition and quality. | 4.4, p.7 |
| Insulation thickness | Affects condensation, dilution, and purity. | 4.5, p.7–8 |
| MAPE / calibration | Model accuracy measure and fitting to field data. | 4.6, p.8 |

## Useful Figures / Tables

| Item | Why it is useful |
|---|---|
| Figure 1: Two-phase, three-field flow | Good visual for explaining steam, bottom liquid film, and entrained droplets. |
| Figure 2: Roll-wave entrainment mechanism | Useful for explaining how liquid film becomes droplets. |
| Table 3: Entrainment in separator | Good for comparing GSP, SPDOT, and droplet-entrainment model carryover. |
| Figures 5–8 | Useful for how entrainment/deposition rates evolve along a pipeline with and without water wash. |
| Tables 4–6 | Good quick numerical lookup for pipe length, diameter, and insulation effects. |
| Figures 13–16 | Useful for calibration and water wash location optimisation. |

## Best Report Claims Supported by This Paper

- Steam quality and steam purity are related but not identical; high dryness does not guarantee low mineral carryover.
- Existing models such as GSP and SPDOT are strong system models but can miss the droplet field in the steam core.
- Pipe geometry, insulation, drain-pot location, and water wash location can change the balance between entrainment, deposition, dilution, and final purity.
- CFD and better large-diameter pipeline correlations are needed to improve droplet tracking in geothermal steam pipelines.

---

# Paper 2 — Umanzor, Zarrouk & Rodríguez 2021

**File:** `33(2).pdf`  
**Title:** *Steam Purity Troubleshooting: The Berlin Geothermal Steam Field, El Salvador*  
**Main purpose:** This paper is a real-world troubleshooting case study for steam purity, mineral deposition, condensate drain pots, steam traps, and field-model diagnosis. It is most useful when you need to show how modelling, measurements, and root-cause analysis are combined to diagnose turbine scaling despite apparently acceptable steam purity monitoring.

## Best Use Cases

| Use this paper when you need... | Why this paper helps |
|---|---|
| A real case where turbine deposits occurred despite monitoring | U2 had mineral deposits in rotor seals even though measured demister outlet limits were reportedly not exceeded. |
| Condensate drain pot and steam trap placement discussion | The paper directly links poor CDP/trap location and an underground crossing to possible carryover. |
| Field model structure for steam purity | It lists primary separation, IAPWS thermodynamic properties, mass balance, pressure drop, heat losses, and CDP efficiency. |
| A troubleshooting diagram / root cause analysis style example | Section 5 gives failure analysis and potential causes. |
| Secondary separation efficiency | Section 4.2 focuses on CDP series, CDP efficiency assumptions, and the TR-2/9 branch line. |

## Section Dictionary

| Section | Page | What this section contains / when to use it |
|---|---:|---|
| **Abstract** | 1 | The abstract gives the economic and operational motivation: wet/dirty steam causes lost generation, overhauls, retrofits, and turbine damage. Use it when introducing why steam purity problems are expensive and need integrated modelling rather than only simple rules. |
| **1.1 Berlin Power Station and Steamfield Configuration** | 1 | This section describes the Berlin field, its production wells, reinjection wells, separation stations, turbine units, and distance from plant. Use it when you need a concise field-layout example showing how long lines normally should improve scrubbing. |
| **1.2 Separation Systems** | 2 | This section describes tangential inlet BOC separators, long cross-country steam lines, condensate drain pots, steam traps, and demisters. Use it when discussing primary versus secondary separation in an actual steam gathering system. |
| **1.3 Steamfield Production** | 2 | This section introduces the production data used as model inputs. Use it when you need to justify that model inputs came from measured separator pressures, mass flows, enthalpies, and chloride concentrations. |
| **2.1 Steam Purity Monitoring** | 2–3 | This section summarises chloride monitoring, measured separation efficiency, manufacturer steam impurity limits, and demister outlet monitoring. Use it when explaining the mismatch between apparently acceptable bulk monitoring and localised turbine deposit problems. |
| **2.2 Startup Problems with U2** | 3 | This section describes the March 2021 U2 startup obstruction and mineral deposits in rotor seals. Use it as a clear field example of steam purity problems affecting operation even when blades/nozzles do not show the main scaling issue. |
| **3.1 Model Configuration** | 3–4 | This section lists the thermofluid model components: primary separation efficiency, IAPWS properties, mass balance, pressure drop, heat losses, and CDP efficiency. Use it as a template for describing how a steamfield process model is assembled. |
| **3.2 Model inputs** | 4 | This section lists production data and general assumptions such as ambient temperature, wall surface temperature, wind speed, insulation material, and insulation thickness. Use it when looking for realistic input parameters for a field-scale steam purity model. |
| **4.1 Primary Separation Efficiency** | 4–5 | This section compares calculated separation efficiency against measured chloride-based efficiency. Use it when arguing that primary separator efficiency can appear high yet still not fully explain downstream deposition problems. |
| **4.2 Secondary Separation Efficiency** | 5 | This section is one of the most useful parts for CDPs because it compares the TR-4A line with multiple CDPs against the TR-2/9 line with only one CDP. Use it to argue that the arrangement and number of drain pots strongly affect carryover removal. |
| **4.3 Enhancement of First CDP downstream of TR-2/9** | 5–6 | This section shows how CDP90 efficiency affects chloride transport to U2. Use it when explaining why the first drain pot downstream of a high-chloride branch can dominate downstream steam purity. |
| **4.4 Heat Losses and Steam Condensate** | 6 | This section quantifies condensation load and tests insulation thickness/material changes. Use it when discussing that more insulation does not necessarily solve purity problems and that condensation can help chloride dilution and scrubbing. |
| **5.1 Improvement Opportunity** | 6 | This section translates measured TDS and steam flow into mineral loading entering the turbine. Use it when you need a strong numerical argument that small ppm levels can become large mineral mass flow rates. |
| **5.2 Potential Cause 1 — Poor efficiency of steam traps downstream of TR-2/9 join** | 6 | This section argues that the only steam trap on the TR-2/9 branch was poorly located and may have allowed droplets to bypass the CDP leg. Use it for practical layout rules: avoid placing CDPs immediately after bends/fittings that create turbulence. |
| **5.3 Potential Cause 2 — TR-2/9 underground crossing with no steam trap** | 6–7 | This section identifies a low-point crossing without a condensate removal device as a likely condensate pool. Use it when discussing water hammer risk and how stagnant condensate can be dragged into the steam flow. |
| **5.4 Potential Cause 3 — Poor primary separation efficiency** | 7 | This subsection appears inside the potential-cause discussion and considers whether convoluted two-phase piping upstream of the separator could atomise liquid and reduce separation quality. Use it when linking upstream piping geometry to separator performance. |
| **6. Recommendations** | 7 | This section gives practical next steps: validate the model, measure full steamfield efficiency using chloride/sodium mass balance, improve TR-2/9 condensate trapping, and investigate local turbine deposits. Use it when writing recommendations for a steam purity investigation. |

## Keyword / Search Table

| Keyword | What it means here | Best section/page |
|---|---|---|
| Berlin steamfield | El Salvador field case study. | 1.1, p.1 |
| U2 startup problem | Turbine free-rotation obstruction due to deposits. | 2.2, p.3 |
| CDP / condensate drain pot | Secondary separation device in steam pipeline. | 1.2, 4.2–4.3, p.2, p.5–6 |
| CDP90 | Important drain pot downstream of TR-2/9. | 4.3, p.5–6 |
| Steam trap | Device whose location/efficiency affects liquid removal. | 5.2–5.3, p.6–7 |
| Chloride mass balance | Method for tracing brine carryover/mineral loading. | 2.1, 3.1, 4.1–4.3 |
| Heat loss | Causes condensate formation along steam lines. | 4.4, p.6 |
| Insulation thickness | Tested but found to have limited improvement beyond current setup. | 4.4, p.6 |
| Water hammer | Risk caused by condensate pooling in low points. | 5.3, p.6–7 |
| Root cause analysis | Failure analysis for U2 deposit problem. | 5, p.6–7 |

## Useful Figures / Tables

| Item | Why it is useful |
|---|---|
| Figure 1 | Shows Berlin steamfield layout and separation stations feeding U1/U2. |
| Figure 3 | Good CDP + inverted bucket steam trap arrangement diagram. |
| Table 2 | Separator production inputs: pressure, total flow, steam flow, enthalpy. |
| Table 3 | Manufacturer impurity limits for TDS, chloride, silica, and iron. |
| Figures 6–7 | Direct visual evidence of mineral deposits in rotor seals. |
| Figure 12 | Shows how CDP90 efficiency affects chloride removal. |
| Figure 14 | Failure analysis and troubleshooting diagram. |
| Figure 17 | Proposed modification to TR-2/9 steam branch line. |

## Best Report Claims Supported by This Paper

- High measured separator efficiency alone may not guarantee a clean and dry turbine inlet.
- Drain-pot number, location, and efficiency can dominate downstream chloride transport.
- Low points without proper trapping can create condensate pools, carryover, and water hammer risk.
- A useful steam purity model should integrate thermodynamics, heat loss, pressure drop, mineral mass balance, primary separation, and secondary separation.

---

# Paper 3 — Rizaldy, Zarrouk & Morris 2016

**File:** `053_Rizaldy_Final(2).pdf`  
**Title:** *Liquid Carryover in Geothermal Steam-Water Separators*  
**Main purpose:** This paper focuses on liquid film entrainment inside vertical cyclone separators and explains why actual separator efficiency may be lower than theoretical/calculated efficiency. It is most useful for separator carryover mechanisms, liquid film behaviour, separator efficiency measurement, and links between liquid loading, inlet velocity, entrainment, and turbine damage.

## Best Use Cases

| Use this paper when you need... | Why this paper helps |
|---|---|
| A clear explanation of separator carryover despite high theoretical efficiency | It directly challenges the idea that calculated 99.995% efficiency always prevents damage. |
| Liquid film entrainment mechanism | It argues that liquid film on cyclone walls can re-entrain into the steam outlet. |
| Field evidence from Wairakei | It uses field data and drain-pot chemistry to discuss carryover and separator performance. |
| Separator efficiency equations using sodium/chloride/TDS | Section 2.3 is useful for efficiency estimation and tracer methods. |
| Why CFD could improve separator carryover prediction | It notes that inlet angle, film thickness, and relative velocity are hard to measure and could be better obtained with CFD. |

## Section Dictionary

| Section | Page | What this section contains / when to use it |
|---|---:|---|
| **Abstract** | 1 | The abstract states the paper’s main argument: theoretical separator efficiency can be very high, but actual performance can be lower due to liquid film entrainment. Use it when you need a concise source explaining that water carryover can still cause scaling and moisture damage. |
| **1. Introduction** | 1–2 | This section explains why dryness and purity at the turbine inlet are critical for reliability, lifespan, and efficiency. Use it when you need background examples of turbine mineral deposition, water impingement erosion, and the cost of shutdowns. |
| **2. Steam-Water Separator** | 2 | This section introduces separators as the main equipment for separating water from steam in wet geothermal fields. Use it when you need a broad transition from geothermal reservoir two-phase production to separator types. |
| **2.1 Horizontal Gravity Separator** | 2 | This section explains horizontal separators, gravity separation, mist eliminators, and why horizontal separators are more common in Iceland, Japan, and Russia. Use it when comparing horizontal and vertical separator concepts and their operating advantages. |
| **2.2 Vertical Cyclone Separator** | 2–3 | This section explains vertical cyclone separators and the movement of two-phase flow inside them. Use it when discussing BOC/TOC separator design, centrifugal separation, and why vertical cyclone separators are common in geothermal systems influenced by New Zealand design. |
| **2.3 Steam-Water Separation Efficiency** | 3–4 | This section explains how separator efficiency is calculated and why natural tracers such as sodium/chloride/TDS can be used to infer carryover. Use it when you need equations or practical measurement logic for actual separator performance. |
| **3. Liquid Carryover Analysis** | 4–5 | This is the key mechanism section: it explains wet steam, liquid film carryover, field sodium data, drain pots, and why separator performance may not match design. Use it when arguing that liquid film formed on cyclone walls can lead to carryover downstream. |
| **3.1 Liquid Entrainment Modeling** | 5–8 | This section develops the entrainment model for the separator and pipeline. Use it when you need equations for entrainment fraction, maximum entrainment fraction, entrainment rate, and assumptions such as treating carryover as deposited into a liquid film. |
| **Conclusions** | 8 | This section summarises that liquid carryover can be significant and increases with liquid loading, film thickness, and inlet velocity. Use it when writing final statements about why separator inlet conditions and liquid loading must be considered in design and operation. |

## Keyword / Search Table

| Keyword | What it means here | Best section/page |
|---|---|---|
| Liquid carryover | Brine/water leaving separator with steam. | Abstract, 1, 3 |
| Liquid film | Water layer on separator wall that can re-entrain. | 3, 3.1 |
| Separator efficiency | Fraction of brine removed from steam. | 2.3 |
| Sodium tracer | Chemical method for measuring brine carryover. | 2.3, 3 |
| Chloride / TDS | Alternative indicators of brine carryover. | 2.3, 3 |
| Wairakei field data | Field evidence for carryover and drain-pot chemistry. | 3 |
| Inlet velocity | Higher velocity increases entrainment and carryover. | 3.1, Conclusion |
| Liquid loading fraction | Higher liquid loading creates thicker liquid film and more entrainment. | 3.1, Conclusion |
| CFD modelling | Proposed route to obtain difficult parameters such as film thickness and inlet flow angle. | 3.1 |

## Useful Figures / Tables

| Item | Why it is useful |
|---|---|
| Figure 1 | Visual example of mineral deposition on turbine components. |
| Figures 2–3 | Useful diagrams of horizontal separator arrangements. |
| Figures 6–8 | Field setup and chemistry data for sodium/TDS in drain pots. |
| Figure 9 | Useful conceptual diagram of entrainment mechanism in separator/pipeline. |
| Table 1 | Separator parameters used in entrainment model testing. |
| Figures 10–13 | Show entrainment/carryover model behaviour against loading and velocity effects. |

## Best Report Claims Supported by This Paper

- Calculated separator efficiency can overestimate real separator performance.
- Liquid film on cyclone walls can re-entrain and become carryover in the steam line.
- Higher liquid loading and higher inlet velocity tend to increase entrainment and carryover.
- CFD can support better modelling by estimating film thickness, inlet flow angle, and steam-liquid relative velocity.

---

# Paper 4 — Umanzor & Zarrouk 2022

**File:** `053(2).pdf`  
**Title:** *The Steamfield Process Design and Optimisation Tool (SPDOT)*  
**Main purpose:** This paper describes the SPDOT system model for geothermal steam gathering systems. It is most useful for explaining integrated process modelling from separators to pipelines, drain pots, scrubbers, demisters, pressure drop, heat loss, condensate generation, mineral dilution, and optimisation of steam quality/purity.

## Best Use Cases

| Use this paper when you need... | Why this paper helps |
|---|---|
| A framework for modelling a whole steamfield system | SPDOT links standalone calculation blocks for separators, pipes, CDPs, scrubbers, and demisters. |
| Steamfield optimisation variables | It studies drain-pot spacing, CDP efficiency, and pipeline length. |
| A model logic diagram | Figures 1 and 2 are useful for explaining block-by-block process simulation. |
| Design-stage motivation | The introduction argues that steam purity problems are cheapest to solve during design, not after commissioning. |
| Difference between component design and system design | The model recalculates fluid properties after each block, showing the downstream effects of each component. |

## Section Dictionary

| Section | Page | What this section contains / when to use it |
|---|---:|---|
| **Abstract** | 1 | The abstract introduces SPDOT as a process design and optimisation tool for geothermal steam gathering systems. Use it when you need a concise description of what the tool calculates: pressure drop, heat transfer, condensate generation, mineral dilution, and thermodynamic properties. |
| **1. Introduction** | 1 | This section gives the design motivation: dirty steam can cause expensive turbine maintenance, and post-commissioning fixes are often limited and costly. Use it to support the argument that steamfield layout and moisture removal should be optimised early in project design. |
| **2. The SPDOT Model** | 1–3 | This section explains the core structure of SPDOT as interconnected calculation blocks with more than 100 equations. Use it when describing a system model that passes updated properties from one block to the next. |
| **3. Model Validation Exercise** | 3 | This section describes a simplified calibration/validation exercise based on prior steamfield modelling. Use it when you need to show that SPDOT was tested against existing field/model data before optimisation exercises. |
| **4. Optimisation Exercises** | 3 | This section introduces the optimisation cases studied in the paper. Use it when you need a high-level explanation that SPDOT can vary equipment layout and operating assumptions to improve steam quality and purity. |
| **4.1 Distance between Condensate Drain Pots** | 3 | This section studies how spacing between CDPs affects liquid removal and final steam condition. Use it when discussing why drain-pot placement is not just a mechanical detail but a steam purity design variable. |
| **4.2 Condensate Drain Pots Removal Efficiency** | 3–4 | This section varies CDP removal efficiency and shows how performance affects downstream steam quality/purity. Use it when you need to justify why CDP efficiency assumptions matter in model predictions. |
| **4.3 Steam Pipeline Length** | 4 | This section explores the effect of pipeline length on steam scrubbing and purity. Use it when explaining the design trade-off between longer lines for more scrubbing and system costs/pressure losses. |
| **4.4 Optimisation Findings and Conclusions** | 4 | This section summarises the optimisation exercise findings. Use it when you want the paper’s practical design message: steamfield geometry and secondary separation equipment can be optimised to improve turbine inlet conditions. |
| **Paper Conclusions** | 4–5 | This final section summarises SPDOT’s value for design and troubleshooting. Use it when writing about integrated modelling as a way to validate steamfield design, identify bottlenecks, and evaluate improvement options. |

## Keyword / Search Table

| Keyword | What it means here | Best section/page |
|---|---|---|
| SPDOT | Steamfield Process Design and Optimisation Tool. | Abstract, 2 |
| Process block | Standalone model element such as separator, pipe, CDP, scrubber, demister. | 2 |
| Thermodynamic properties | Fluid properties recalculated after each block. | 2 |
| Pressure drop | One of the main pipe block calculations. | 2 |
| Heat loss | Leads to condensate generation and mineral dilution effects. | 2 |
| Condensate drain pot | Secondary separation block with removal efficiency. | 2, 4.1–4.2 |
| Entrainment number | Steam velocity/scrubbing criterion used in pipe blocks. | 2 |
| Water wash | Spray water injection for steam washing. | 2 |
| Pipeline length | Optimisation variable for scrubbing and purity. | 4.3 |

## Useful Figures / Tables

| Item | Why it is useful |
|---|---|
| Figure 1: Blocks Processing Logic | Best figure for explaining SPDOT as sequential calculation blocks. |
| Figure 2: Simplified mathematical model | Useful for showing a whole steamfield network representation. |
| Optimisation figures/tables | Useful for linking drain-pot spacing, removal efficiency, and pipeline length to final steam condition. |

## Best Report Claims Supported by This Paper

- Steamfield design should be treated as a connected process system rather than isolated equipment sizing.
- Pressure drop, heat loss, condensate generation, mineral dilution, separation efficiency, and steam washing interact across the network.
- SPDOT is useful for both new design validation and troubleshooting existing steamfield purity problems.

---
