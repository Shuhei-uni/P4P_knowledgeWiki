# CFD Wiki Index

## Lookup Dictionaries
- [paper_lookup/index](../paper_lookup/index.md): first-stop index for chunked CFD/geothermal research-paper lookup files.
- [research_paper_dictionary_lookup](../research_paper_dictionary_lookup.md): compatibility router for the broad CFD/geothermal lookup dictionary.
- [geothermal_research_paper_dictionary (1)](../geothermal_research_paper_dictionary%20(1).md): compatibility router for the geothermal separator and steam-purity lookup dictionary.

## Sources
- [user-cyclone-solidworks-flow-particle-study-report](sources/user-cyclone-solidworks-flow-particle-study-report.md): user-provided SolidWorks Flow Simulation cyclone setup with fan rotation and particle-diameter separation comparison.
- [user-cyclone-workbench-rng-dpm-settings-report](sources/user-cyclone-workbench-rng-dpm-settings-report.md): user-provided Workbench/SpaceClaim cyclone setup with tetra mesh, Fluent RNG k-epsilon, energy, and DPM source updates.
- [youtube-cyclone-separator-icem-fluent-exemplar](sources/youtube-cyclone-separator-icem-fluent-exemplar.md): tutorial-style cyclone separator workflow covering ICEM hexa blocking, Fluent RSM, and DPM particle efficiency.
- [pointon-2009-geothermal-separator-sizing-cfd-validation](sources/pointon-2009-geothermal-separator-sizing-cfd-validation.md): geothermal-specific large-separator CFD/FEA validation paper with scrolled-vs-tangential entry comparison and HP separator scale anchors.
- [purnanto-2013-cfd-geothermal-separator](sources/purnanto-2013-cfd-geothermal-separator.md): 2013 baseline CFD study comparing three geothermal BOC separator inlet designs, including Harwell droplet-size extraction notes.
- [zarrouk-purnanto-2014-geothermal-separator-design-overview](sources/zarrouk-purnanto-2014-geothermal-separator-design-overview.md): invited review of geothermal separator design families, sizing logic, and CFD role.
- [rivas-cruz-2015-geothermal-separator-state-of-art-review](sources/rivas-cruz-2015-geothermal-separator-state-of-art-review.md): state-of-art review of separator design/evaluation methods and software.
- [mubarok-2020-cfd-geothermal-flow-meters](sources/mubarok-2020-cfd-geothermal-flow-meters.md): validated CFD comparison of six pressure-differential flow meters for two-phase geothermal flow.
- [skoog-2020-annular-flow-three-field-cfd-thesis](sources/skoog-2020-annular-flow-three-field-cfd-thesis.md): Fluent three-field annular-flow thesis with UDF-level implementation detail.
- [mondal-sharma-2024-air-water-annular-flow-cfd](sources/mondal-sharma-2024-air-water-annular-flow-cfd.md): annular-flow CFD benchmarking of entrainment models with DPM+EWF coupling.
- [chen-2025-straight-through-cyclone-water-separator](sources/chen-2025-straight-through-cyclone-water-separator.md): experiment-backed straight-through cyclone separator benchmark using Fluent RSM-DPM with reported droplet PSD, rough-wall model, and pressure-effect sensitivity.
- [merbecks-2025-geoprop-geofluid-property-framework](sources/merbecks-2025-geoprop-geofluid-property-framework.md): geofluid phase/property modeling framework for geothermal applications.
- [montesdeoca-martinez-2026-binary-power-plant-two-phase-geofluid](sources/montesdeoca-martinez-2026-binary-power-plant-two-phase-geofluid.md): techno-economic binary power-plant model for two-phase geothermal resources.
- [ansys-fluent-users-guide-2025r2](sources/ansys-fluent-users-guide-2025r2.md): Fluent product documentation source for GUI workflow and click-path guidance.

## Setups
- [cyclone-separator-solidworks-flow-particle-study-exemplar](setups/cyclone-separator-solidworks-flow-particle-study-exemplar.md): reusable SolidWorks Flow Simulation cyclone setup with internal analysis, rotating fan region, and particle-size study.
- [cyclone-separator-workbench-tetra-rng-dpm-exemplar](setups/cyclone-separator-workbench-tetra-rng-dpm-exemplar.md): reusable Workbench/SpaceClaim cyclone setup using fluid-volume extraction, tetra mesh, RNG k-epsilon, and DPM particle visualization.
- [cyclone-separator-icem-hexa-rsm-dpm-exemplar](setups/cyclone-separator-icem-hexa-rsm-dpm-exemplar.md): reusable cyclone separator exemplar for ICEM hexa mesh, Fluent RSM, transient fallback, and DPM efficiency.
- [straight-through-cyclone-water-separator-rsm-dpm-2025](setups/straight-through-cyclone-water-separator-rsm-dpm-2025.md): experiment-backed RSM-DPM separator benchmark with reported Rosin-Rammler droplets, rough-wall model, and pressure-effect validation targets.
- [geothermal-boc-separator-fluent-2013-baseline](setups/geothermal-boc-separator-fluent-2013-baseline.md): beginner-focused reconstruction workflow from source-reported numerics, inlet phase package, and droplet-size assumptions.
- [geothermal-boc-separator-two-zone-split-inlet](setups/geothermal-boc-separator-two-zone-split-inlet.md): reusable adaptation for a segregated two-zone inlet with wall-side liquid and core-side steam.
- [geothermal-boc-separator-pure-phase-split-velocity-inlet](setups/geothermal-boc-separator-pure-phase-split-velocity-inlet.md): consolidated Fluent settings for the Purnanto-derived pure-liquid/pure-steam split velocity-inlet branch.
- [geothermal-separator-design-screening-2014-overview](setups/geothermal-separator-design-screening-2014-overview.md): pre-CFD screening workflow from global separator design review evidence.
- [geothermal-separator-audit-lazalde-crabtree-2015-review-workflow](setups/geothermal-separator-audit-lazalde-crabtree-2015-review-workflow.md): audit workflow for legacy separator performance and design-intent drift.
- [geothermal-two-phase-flow-meter-fluent-sst-mixture-2020](setups/geothermal-two-phase-flow-meter-fluent-sst-mixture-2020.md): CFD benchmark setup for geothermal pressure-differential flow meters.
- [annular-flow-three-field-fluent-2020-thesis-reproduction](setups/annular-flow-three-field-fluent-2020-thesis-reproduction.md): UDF-centric Fluent three-field annular workflow reproduction.
- [vertical-tube-annular-flow-fluent-dpm-ewf-2024](setups/vertical-tube-annular-flow-fluent-dpm-ewf-2024.md): annular-flow DPM+EWF setup with entrainment model comparison.
- [geoprop-geofluid-properties-2025-workflow](setups/geoprop-geofluid-properties-2025-workflow.md): geofluid property/phase-behavior predesign workflow.
- [binary-orc-two-phase-geothermal-2026-system-model](setups/binary-orc-two-phase-geothermal-2026-system-model.md): system-level two-phase binary plant model workflow.

## Guidance
- [guidance/index](guidance/index.md): entry point for reusable click-by-click Fluent guidance pages.
- [fluent-general-click-by-click](guidance/fluent-general-click-by-click.md): first-stop GUI navigation playbook for setup questions.
- [workbench-meshdat-semi-automated-improvement](guidance/workbench-meshdat-semi-automated-improvement.md): conservative `.meshdat` mesh-improvement workflow with PyFluent baseline/export validation and Workbench operator trial steps.
- External guide reference: `../guide/Ansys_Fluent_Users_Guide.pdf` is the local Fluent manual PDF used to verify and extend click-by-click guidance.

## Entities
- [solidworks-flow-simulation-particle-study](entities/solidworks-flow-simulation-particle-study.md): SolidWorks-native particle tracing workflow for post-flow particle-size and accumulation studies.
- [geometry-tangential-inlet-cyclone-separator](entities/geometry-tangential-inlet-cyclone-separator.md): generic tangential-inlet cyclone separator geometry with vortex finder and dustbin/collection region.
- [geometry-vertical-boc-cyclone-separator](entities/geometry-vertical-boc-cyclone-separator.md): canonical separator geometry family used in this domain.
- [turbulence-reynolds-stress-model](entities/turbulence-reynolds-stress-model.md): higher-cost RANS turbulence model used for strong cyclone swirl and anisotropic turbulence.
- [turbulence-rng-k-epsilon](entities/turbulence-rng-k-epsilon.md): recurring turbulence baseline for high-swirl separator flows.
- [solver-pressure-based-simple-presto](entities/solver-pressure-based-simple-presto.md): solver-coupling-pressure scheme stack used in baseline reproduction.
- [multiphase-dpm-particle-tracking](entities/multiphase-dpm-particle-tracking.md): particle carryover estimation workflow and associated numerical risks.

## Concepts
- [two-phase-flow-regime-vs-cfd-representation](concepts/two-phase-flow-regime-vs-cfd-representation.md): distinguishes real geothermal flow regimes from simplified CFD two-phase representations used in separator studies.
- [mesh-inflation-boundary-layer](concepts/mesh-inflation-boundary-layer.md): explains inflation layers, when they help near-wall CFD, and when they can damage mesh quality.

## Physics Basis
- [physics-basis/index](physics-basis/index.md): entry point for reusable separator physics, inherited assumptions, and model-rationale pages.
- [separator-flow-physics](physics-basis/separator-flow-physics.md): core separator flow mechanisms and what they imply for CFD interpretation.
- [droplets-carryover-and-re-entrainment](physics-basis/droplets-carryover-and-re-entrainment.md): inlet droplet assumptions, carryover pathways, and wall-film uncertainty.
- [separator-geometry-and-swirl-mechanisms](physics-basis/separator-geometry-and-swirl-mechanisms.md): geometry and swirl tradeoffs behind separator behavior.
- [governing-equations-and-modeling-levels](physics-basis/governing-equations-and-modeling-levels.md): high-level governing equations and model-family ladder for separator CFD.
- [operating-pressure-enthalpy-and-phase-split](physics-basis/operating-pressure-enthalpy-and-phase-split.md): pressure, enthalpy, and inlet phase-split framing for separator reasoning.
- [uncertainties-and-assumption-register](physics-basis/uncertainties-and-assumption-register.md): active uncertainty register for separator modeling assumptions.

## Synthesis
- [geothermal-separator-design-and-cfd-patterns](synthesis/geothermal-separator-design-and-cfd-patterns.md): merged design defaults and failure checks for geothermal separators.
- [geothermal-separator-inlet-droplets-and-carryover](synthesis/geothermal-separator-inlet-droplets-and-carryover.md): external-web and local-wiki inventory of separator-inlet steam/brine/droplet/mineral evidence, reported sizes, calculated loads, and missing measured particle-size data.
- [fluent-separator-efficiency-methods](synthesis/fluent-separator-efficiency-methods.md): Purnanto-style DPM separator-efficiency reconstruction plus improved Fluent phase-flux, mass-weighted DPM, wall-film, and field-validation workflows.
- [annular-flow-three-field-cfd-patterns](synthesis/annular-flow-three-field-cfd-patterns.md): cross-source annular-flow three-field modeling defaults and sensitivities.
- [two-phase-geofluid-property-to-binary-plant-design](synthesis/two-phase-geofluid-property-to-binary-plant-design.md): links geofluid property modeling to downstream binary-plant design choices.
- [mesh-quality-and-resolution-patterns](synthesis/mesh-quality-and-resolution-patterns.md): compares reported mesh counts, refinement/independence evidence, and practical orthogonal-quality interpretation across CFD papers.
