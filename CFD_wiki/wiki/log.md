# CFD Wiki Log

## [2026-05-07] ingest | Cyclone separator SolidWorks Flow Simulation particle study exemplar
- Files created/updated:
  - `wiki/sources/user-cyclone-solidworks-flow-particle-study-report.md`
  - `wiki/setups/cyclone-separator-solidworks-flow-particle-study-exemplar.md`
  - `wiki/entities/solidworks-flow-simulation-particle-study.md`
  - `wiki/entities/geometry-tangential-inlet-cyclone-separator.md`
  - `wiki/entities/multiphase-dpm-particle-tracking.md`
  - `wiki/index.md`
  - `wiki/log.md`
- Reason: store user-provided SolidWorks Flow Simulation cyclone separator notes as a reusable internal-flow, fan-rotation, and particle-diameter comparison exemplar.
- Notable assumptions introduced or removed:
  - Introduced source-limitation label that values are reported from user-provided SolidWorks setup notes rather than a validated paper.
  - Introduced caution that the top rotating fan is a design-specific feature and should not be generalized to passive cyclones.
  - Kept SolidWorks Particle Study separate from Fluent DPM to avoid mixing solver-specific particle boundary meanings.

## [2026-05-07] ingest | Cyclone separator Workbench tetra Fluent RNG-DPM exemplar
- Files created/updated:
  - `wiki/sources/user-cyclone-workbench-rng-dpm-settings-report.md`
  - `wiki/setups/cyclone-separator-workbench-tetra-rng-dpm-exemplar.md`
  - `wiki/setups/cyclone-separator-icem-hexa-rsm-dpm-exemplar.md`
  - `wiki/entities/geometry-tangential-inlet-cyclone-separator.md`
  - `wiki/entities/turbulence-rng-k-epsilon.md`
  - `wiki/entities/multiphase-dpm-particle-tracking.md`
  - `wiki/index.md`
  - `wiki/log.md`
- Reason: store user-provided Workbench/SpaceClaim cyclone separator settings as a reusable tetra mesh, RNG k-epsilon, energy, and DPM source-update exemplar.
- Notable assumptions introduced or removed:
  - Introduced source-limitation label that values are reported from user-provided settings notes rather than a validated paper.
  - Introduced high-risk scale assumption for the 1e-2 mesh size because units and geometry scale are not specified.
  - Flagged DPM inlet `Reflect` and Update DPM Sources as settings that need diagnostic checks before quantitative reuse.

## [2026-05-07] ingest | Cyclone separator ICEM hexa Fluent RSM-DPM exemplar
- Files created/updated:
  - `wiki/sources/youtube-cyclone-separator-icem-fluent-exemplar.md`
  - `wiki/setups/cyclone-separator-icem-hexa-rsm-dpm-exemplar.md`
  - `wiki/entities/geometry-tangential-inlet-cyclone-separator.md`
  - `wiki/entities/turbulence-reynolds-stress-model.md`
  - `wiki/entities/multiphase-dpm-particle-tracking.md`
  - `wiki/entities/geometry-vertical-boc-cyclone-separator.md`
  - `wiki/entities/turbulence-rng-k-epsilon.md`
  - `wiki/concepts/mesh-inflation-boundary-layer.md`
  - `wiki/index.md`
  - `wiki/log.md`
- Reason: store user-provided cyclone separator tutorial notes as a reusable ICEM hexa meshing and Fluent RSM-DPM setup exemplar.
- Notable assumptions introduced or removed:
  - Introduced source-limitation label that values are reported from user-provided video notes rather than a peer-reviewed paper.
  - Introduced medium/high-risk fallbacks for missing CAD dimensions, ICEM spacing units, Fluent solver schemes, and DPM tracking controls.

## [2026-04-21] ingest | Purnanto 2013 geothermal separator baseline
- Files created/updated:
  - `wiki/sources/purnanto-2013-cfd-geothermal-separator.md`
  - `wiki/setups/geothermal-boc-separator-fluent-2013-baseline.md`
  - `wiki/entities/geometry-vertical-boc-cyclone-separator.md`
  - `wiki/entities/turbulence-rng-k-epsilon.md`
  - `wiki/entities/solver-pressure-based-simple-presto.md`
  - `wiki/entities/multiphase-dpm-particle-tracking.md`
  - `wiki/index.md`
  - `wiki/log.md`
- Reason: first source ingest to establish reproducible geothermal separator CFD baseline and numerical-parameter capture workflow.
- Notable assumptions introduced or removed:
  - Introduced inferred two-stage continuous+particle workflow due mixed wording around mixture model vs DPM usage.
  - Introduced medium-risk fallback assumptions for unreported convergence controls.

## [2026-04-21] query | Clarify meaning of "two-phase flow" in separator paper
- Files created/updated:
  - `wiki/concepts/two-phase-flow-regime-vs-cfd-representation.md`
  - `wiki/index.md`
  - `wiki/log.md`
- Reason: distinguish physical geothermal flow regimes from the simplified CFD two-phase representation used in the 2013 separator study.
- Notable assumptions introduced or removed:
  - Introduced one general terminology note listing common regime names as `Assumed` (non-source-specific context).

## [2026-04-30] query | Extract Fluent initialization details from Purnanto 2013
- Files created/updated:
  - `wiki/sources/purnanto-2013-cfd-geothermal-separator.md`
  - `wiki/setups/geothermal-boc-separator-fluent-2013-baseline.md`
  - `wiki/log.md`
- Reason: separate true Fluent initialization reporting from nearby inlet-state and particle assumptions in the separator paper.
- Notable assumptions introduced or removed:
  - Removed any implication that the paper reports initialized field values; it reports only `Hybrid Initialization` and its rationale.

## [2026-04-30] query | Add reusable two-zone split-inlet adaptation
- Files created/updated:
  - `wiki/setups/geothermal-boc-separator-fluent-2013-baseline.md`
  - `wiki/setups/geothermal-boc-separator-two-zone-split-inlet.md`
  - `wiki/index.md`
  - `wiki/log.md`
- Reason: capture a reusable Fluent workflow for replacing a uniform geothermal separator inlet with separate wall-side liquid and inner-side steam boundary zones while reusing the baseline solver stack.
- Notable assumptions introduced or removed:
  - Introduced a project-driven `Assumed` first-pass inlet profile: equal-area face split with pure liquid on the wall side and pure steam on the inner side.
  - Explicitly flagged that the resulting steam-side inlet velocity may become unrealistically high and must be checked as a sensitivity risk.

## [2026-05-05] ingest | Batch process newly added CFD_wiki raw papers
- Files created/updated:
  - `wiki/sources/mubarok-2020-cfd-geothermal-flow-meters.md`
  - `wiki/sources/zarrouk-purnanto-2014-geothermal-separator-design-overview.md`
  - `wiki/sources/rivas-cruz-2015-geothermal-separator-state-of-art-review.md`
  - `wiki/sources/mondal-sharma-2024-air-water-annular-flow-cfd.md`
  - `wiki/sources/skoog-2020-annular-flow-three-field-cfd-thesis.md`
  - `wiki/sources/merbecks-2025-geoprop-geofluid-property-framework.md`
  - `wiki/sources/montesdeoca-martinez-2026-binary-power-plant-two-phase-geofluid.md`
  - `wiki/setups/geothermal-two-phase-flow-meter-fluent-sst-mixture-2020.md`
  - `wiki/setups/geothermal-separator-design-screening-2014-overview.md`
  - `wiki/setups/geothermal-separator-audit-lazalde-crabtree-2015-review-workflow.md`
  - `wiki/setups/vertical-tube-annular-flow-fluent-dpm-ewf-2024.md`
  - `wiki/setups/annular-flow-three-field-fluent-2020-thesis-reproduction.md`
  - `wiki/setups/geoprop-geofluid-properties-2025-workflow.md`
  - `wiki/setups/binary-orc-two-phase-geothermal-2026-system-model.md`
  - `wiki/synthesis/geothermal-separator-design-and-cfd-patterns.md`
  - `wiki/synthesis/annular-flow-three-field-cfd-patterns.md`
  - `wiki/synthesis/two-phase-geofluid-property-to-binary-plant-design.md`
  - `wiki/sources/purnanto-2013-cfd-geothermal-separator.md`
  - `wiki/setups/geothermal-boc-separator-fluent-2013-baseline.md`
  - `wiki/index.md`
  - `wiki/log.md`
- Reason: ingest newly added raw PDFs into reproducible CFD/project-design knowledge pages and connect overlapping papers through synthesis pages.
- Notable assumptions introduced or removed:
  - Introduced explicit `Not Applicable`/`Missing` handling for non-CFD papers (process/property modeling and review papers) to avoid false solver detail claims.
  - Added cross-paper bidirectional links between 2013 separator baseline and 2014/2015 review lineage plus 2020 metering extension.

## [2026-05-05] refactor | Add Fluent guidance-first knowledge layer
- Files created/updated:
  - `wiki/guidance/index.md`
  - `wiki/guidance/fluent-general-click-by-click.md`
  - `wiki/sources/ansys-fluent-users-guide-2025r2.md`
  - `wiki/index.md`
  - `wiki/log.md`
  - `AGENTS.md`
  - `CFD_wiki/AGENTS.md`
- Reason: establish a dedicated guidance directory for click-by-click Fluent navigation so setup answers can consult procedural paths before case-specific pages.
- Notable assumptions introduced or removed:
  - Introduced `Inferred` label usage for UI sequences that are assembled from distributed documentation sections rather than a single explicit path line.

## [2026-05-06] query | Synthesize mesh quality and resolution evidence
- Files created/updated:
  - `wiki/synthesis/mesh-quality-and-resolution-patterns.md`
  - `wiki/index.md`
  - `wiki/log.md`
- Reason: answer whether past CFD papers report mesh quality and node/cell counts, and give reusable interpretation for low Fluent orthogonal quality values.
- Notable assumptions introduced or removed:
  - Introduced an `Inferred` warning-level interpretation for minimum orthogonal quality 6.73e-2; paper evidence supports mesh-count/refinement/independence comparisons but does not provide direct orthogonal-quality thresholds.

## [2026-05-06] query | Revise mesh-density interpretation after 1.8M-node update
- Files created/updated:
  - `wiki/synthesis/mesh-quality-and-resolution-patterns.md`
  - `wiki/log.md`
- Reason: incorporate user correction that the active separator mesh is approximately 1.8M nodes rather than approximately 300k nodes.
- Notable assumptions introduced or removed:
  - Retired the interpretation that current global mesh density is below the separator paper's order-of-millions scale; retained the mesh-quality and local refinement concern.

## [2026-05-06] query | Explain mesh inflation for separator CFD
- Files created/updated:
  - `wiki/concepts/mesh-inflation-boundary-layer.md`
  - `wiki/index.md`
  - `wiki/log.md`
- Reason: capture a reusable explanation of inflation layers and their impact on near-wall resolution and orthogonal quality.
- Notable assumptions introduced or removed:
  - Introduced practical guidance that inflation should be inspected locally at separator inlet/outlet transitions because collapsed layers can worsen quality.
