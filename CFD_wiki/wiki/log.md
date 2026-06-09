# CFD Wiki Log

## [2026-06-09] query | Clarify that the Purnanto baseline is a one-inlet mixed feed
- Files created/updated:
  - `wiki/setups/geothermal-boc-separator-fluent-2013-baseline.md`
  - `wiki/log.md`
- Reason: support a project reset back to the direct Purnanto recreation by making the reusable baseline page explicit that the paper-style setup uses one inlet carrying both phases together.
- Notable assumptions introduced or removed:
  - Added a plain-language `Inferred` note that the baseline should not be confused with the later split-inlet or full-face velocity-inlet reinterpretations.

## [2026-06-09] ingest | Cross-check Purnanto paper against live HDF5 setup
- Files created/updated:
  - `sources/purnanto-2013-cfd-geothermal-separator.md`
  - `setups/geothermal-boc-separator-fluent-2013-baseline.md`
  - `wiki/log.md`
- Reason: the repo now contains an extracted Fluent HDF5 case/data pair that confirms the saved Purnanto baseline setup, so the paper extraction pages needed a live cross-check instead of leaving the same solver and inlet values as paper-only assumptions.
- Notable result: the live HDF5 audit confirms the core baseline stack, mesh scale, inlet/outlet values, and convergence criteria; the setup page now points to a more direct project reference for the audited case.
- Notable assumptions introduced or removed:
  - removed the need to infer mesh counts, URFs, residual criteria, and inlet hydraulic diameter for the saved baseline case;
  - retained the paper as the provenance source for what was originally reported.
- Next action: keep future Purnanto-related setup notes anchored to the audited live case reference rather than restating paper-derived guesses.

## [2026-06-04] refactor | Add separator physics-basis layer
- Files created/updated:
  - `template/physics-basis-page.md`
  - `wiki/physics-basis/index.md`
  - `wiki/physics-basis/separator-flow-physics.md`
  - `wiki/physics-basis/droplets-carryover-and-re-entrainment.md`
  - `wiki/physics-basis/separator-geometry-and-swirl-mechanisms.md`
  - `wiki/physics-basis/governing-equations-and-modeling-levels.md`
  - `wiki/physics-basis/operating-pressure-enthalpy-and-phase-split.md`
  - `wiki/physics-basis/uncertainties-and-assumption-register.md`
  - `wiki/index.md`
  - `wiki/synthesis/geothermal-separator-design-and-cfd-patterns.md`
  - `wiki/synthesis/geothermal-separator-inlet-droplets-and-carryover.md`
  - `wiki/synthesis/fluent-separator-efficiency-methods.md`
  - `wiki/concepts/two-phase-flow-regime-vs-cfd-representation.md`
  - `wiki/log.md`
- Reason: create a reusable physics-and-assumptions layer that explains what separator flow behavior past research supports, what remains uncertain, and which CFD model families those assumptions make reasonable to test.
- Notable assumptions introduced or removed:
  - Added an explicit rule that the new physics-basis layer justifies candidate CFD directions and does not declare one active setup as the correct one.
  - Elevated inlet droplet structure, inlet phase arrangement, and wall-film fate as the current highest-risk physical uncertainties driving future sensitivity choices.

## [2026-06-04] ingest | Ingest Chen 2025 and Pointon 2009 separator papers
- Files created/updated:
  - `wiki/sources/chen-2025-straight-through-cyclone-water-separator.md`
  - `wiki/sources/pointon-2009-geothermal-separator-sizing-cfd-validation.md`
  - `wiki/setups/straight-through-cyclone-water-separator-rsm-dpm-2025.md`
  - `wiki/synthesis/fluent-separator-efficiency-methods.md`
  - `paper_lookup/index.md`
  - `paper_lookup/broad/index-and-topic-map.md`
  - `paper_lookup/broad/straight-through-cyclone-water-separator-rsm-dpm.md`
  - `paper_lookup/geothermal/index-and-topic-map.md`
  - `paper_lookup/geothermal/large-separator-cfd-fea-validation.md`
  - `wiki/index.md`
  - `wiki/log.md`
- Reason: process two newly added raw papers into reusable CFD-wiki source, setup, synthesis, and lookup pages, with special attention to Chen 2025 as an experiment-backed separator-method benchmark.
- Notable assumptions introduced or removed:
  - Added a method-transfer rule that Chen 2025 should inform RSM-DPM validation discipline and swirl-tradeoff reasoning, but its air-water operating values should not be copied directly into geothermal work.
  - Added a geothermal trend anchor from Pointon 2009 for scrolled-entry preference, HP separator scale, and pressure-drop/dryness order of magnitude.

## [2026-06-03] query | Add time-limited DPM baseline guidance
- Files created/updated:
  - `wiki/guidance/fluent-general-click-by-click.md`
  - `wiki/synthesis/fluent-separator-efficiency-methods.md`
  - `wiki/log.md`
- Reason: answer a Fluent DPM setup question for a time-limited separator-efficiency baseline after the professional setup `07` run.
- Notable assumptions introduced or removed:
  - Introduced a minimal three-diameter DPM sweep: `5 um`, `10 um`, and `40-41 um`.
  - Clarified baseline DPM boundary behavior: steam outlet `escape`, intended collection surfaces `trap`, ordinary walls only `trap` if wall impact is being treated as permanent collection, and `reflect` when wall deposition is not being counted.
  - Deferred transient Eulerian Wall Film setup until phase-flux balance and basic DPM fate counts are stable.

## [2026-06-02] query | Expand separator-efficiency recommendation into run report
- Files created/updated:
  - `wiki/synthesis/fluent-separator-efficiency-methods.md`
  - `wiki/log.md`
- Reason: convert the recommended hierarchy into a report-style Fluent workflow with droplet-size sweep, wall-film re-entrainment test, equations, acceptance criteria, and results templates.
- Notable assumptions introduced or removed:
  - Introduced a four-tier run matrix: phase-flux baseline, DPM droplet-size sweep, transient wall-film re-entrainment test, and field/chemistry validation.
  - Clarified that wall-hit droplets should not automatically be treated as permanently separated when wall-film re-entrainment is physically plausible.
  - Added decision rules for choosing between phase-flux, DPM, film-aware, and validated efficiency metrics.

## [2026-06-02] query | Synthesize Fluent separator-efficiency methods
- Files created/updated:
  - `wiki/synthesis/fluent-separator-efficiency-methods.md`
  - `wiki/index.md`
  - `wiki/log.md`
- Reason: answer how Purnanto calculated separator efficiency in Fluent and compare it with more defensible current methods using local CFD wiki evidence plus web literature.
- Notable assumptions introduced or removed:
  - Clarified that Purnanto's literal escaped/total droplet ratio is a carryover fraction, so collection efficiency should be reported as `1 - escaped/total` or, preferably, mass-weighted by droplet-size bin.
  - Added efficiency bracketing for incomplete DPM tracks instead of treating them as separated without qualification.
  - Recommended phase-flux mass balance, mass-weighted DPM grade efficiency, DPM+Eulerian Wall Film for re-entrainment, and chloride/sodium/tracer validation as higher-confidence workflows.

## [2026-06-02] query | Deep separator-inlet droplet and particle evidence pass
- Files created/updated:
  - `wiki/synthesis/geothermal-separator-inlet-droplets-and-carryover.md`
  - `wiki/sources/purnanto-2013-cfd-geothermal-separator.md`
  - `wiki/setups/geothermal-boc-separator-fluent-2013-baseline.md`
  - `wiki/index.md`
  - `wiki/log.md`
- Reason: prioritize external academic/web evidence for geothermal separator inlet droplets, brine/water loading, mineral/solid particles, NCG/chemistry context, and CFD DPM implications.
- Notable assumptions introduced or removed:
  - Confirmed that external evidence supports real well moisture loads, separator/demister capture thresholds, and superheated-silica particle evidence, but still does not provide a measured conventional geothermal separator-inlet droplet-size distribution.
  - Clarified Purnanto Harwell extraction: `10 um` remains the reported baseline average, while the `14.2 um` median and `~41 um` upper marker are `Inferred` only if the `10 um` value is treated as Sauter mean diameter.
  - Kept minerals as dissolved/carryover chemistry for conventional saturated separator CFD unless a case explicitly targets superheated silica precipitation or measured solids.

## [2026-06-02] query | Inventory separator-inlet droplets and mineral carryover
- Files created/updated:
  - `wiki/synthesis/geothermal-separator-inlet-droplets-and-carryover.md`
  - `wiki/index.md`
  - `wiki/log.md`
- Reason: answer what enters geothermal separators from well flow, including reported/assumed droplet sizes, phase mass flows, field chemistry loads, and missing particle-size data.
- Notable assumptions introduced or removed:
  - Introduced an `Inferred` Harwell droplet-size envelope from the reported `10 um` average/Sauter assumption while preserving that the actual nine injected Purnanto diameters are not listed in the maintained extraction.
  - Clarified that dissolved minerals are chemistry/carryover tracers, not solid particles unless precipitation or measured solids are explicitly modelled.

## [2026-05-29] query | Consolidate Purnanto pure-phase split velocity-inlet settings
- Files created/updated:
  - `wiki/setups/geothermal-boc-separator-pure-phase-split-velocity-inlet.md`
  - `wiki/setups/geothermal-boc-separator-two-zone-split-inlet.md`
  - `wiki/index.md`
  - `wiki/log.md`
- Reason: merge the 2013 baseline Fluent stack with the recent setup-report branch calculations into one reusable settings sheet for the pure-liquid/pure-steam split-inlet case.
- Notable assumptions introduced or removed:
  - Introduced a clear branch split between the exact-mass `27.118 m/s` package and the reported-velocity `26.81 m/s` alternate.
  - Kept `Dh = 0.724 m` on both split zones as the first controlled-comparison default, while preserving the phase-specific `0.01338 m` / `0.72061 m` hydraulic diameters as a separate sensitivity path.

## [2026-05-28] model-update | Add equal-velocity pure-phase inlet split rule
- Files created/updated:
  - `wiki/setups/geothermal-boc-separator-two-zone-split-inlet.md`
  - `wiki/log.md`
- Reason: capture the reusable area-ratio calculation for a pure-liquid/pure-steam split inlet that preserves Purnanto `1600 kJ/kg` phase mass flows with one common inlet velocity.
- Notable assumptions introduced or removed:
  - Superseded the 50/50 split as the default for equal-velocity pure-phase setup.
  - Added the calculated rectangular inlet split for `0.724 m x 0.724 m`: liquid `0.0048896 m2`, steam `0.5192864 m2`, split line `0.006754 m` from the liquid-side edge.

## [2026-05-28] model-update | Add fixed reported-velocity split variant
- Files created/updated:
  - `wiki/setups/geothermal-boc-separator-two-zone-split-inlet.md`
  - `wiki/log.md`
- Reason: record the `26.81 m/s` reported-velocity interpretation separately from the exact-mass `27.118 m/s` calculation.
- Notable assumptions introduced or removed:
  - Clarified that the same split location at current geometry gives liquid `115.59 kg/s`, steam `79.77 kg/s`, and total `195.37 kg/s`.
  - Marked the exact-mass conflict: `26.81 m/s` would need `0.5301985 m2`, slightly larger than the current `0.524176 m2` inlet area.

## [2026-05-21] query | Add Fluent case-data post-processing load path
- Files created/updated:
  - `wiki/guidance/fluent-general-click-by-click.md`
  - `wiki/log.md`
- Reason: answer how to load existing `.cas.h5` and `.dat.h5` files for flux reports, contours, vectors, and plots.
- Notable assumptions introduced or removed:
  - Introduced an `Inferred` post-processing check sequence using Fluent Results and Reports panels after reading matching case and data files.

## [2026-05-20] refactor | Split paper lookup dictionaries into topic chunks
- Files created/updated:
  - `paper_lookup/index.md`
  - `paper_lookup/broad/index-and-topic-map.md`
  - `paper_lookup/broad/geofluid-properties-and-orc.md`
  - `paper_lookup/broad/fluent-geothermal-flow-meters.md`
  - `paper_lookup/broad/annular-flow-fluent-and-three-field.md`
  - `paper_lookup/broad/geothermal-separator-review.md`
  - `paper_lookup/broad/combined-lookups.md`
  - `paper_lookup/geothermal/index-and-topic-map.md`
  - `paper_lookup/geothermal/steam-purity-and-carryover.md`
  - `paper_lookup/geothermal/separator-design-sizing-and-mrs.md`
  - `paper_lookup/geothermal/cross-paper-lookups.md`
  - `paper_lookup/archive/original-research_paper_dictionary_lookup.md`
  - `paper_lookup/archive/original-geothermal_research_paper_dictionary.md`
  - `research_paper_dictionary_lookup.md`
  - `geothermal_research_paper_dictionary (1).md`
  - `AGENTS.md`
  - `wiki/index.md`
  - `wiki/log.md`
- Reason: reduce context load from very long root dictionary files while preserving section-level paper lookup detail.
- Notable assumptions introduced or removed:
  - Preserved exact original long dictionaries under `paper_lookup/archive/` before replacing root files with router pages.
  - Split working lookup content by complete paper/topic sections rather than summarizing it, so no lookup sections were intentionally removed.

## [2026-05-20] refactor | Clarify CFD_wiki lookup-guide role
- Files created/updated:
  - `AGENTS.md`
  - `wiki/index.md`
  - `wiki/log.md`
- Reason: update the local CFD_wiki operating guide to reflect the new research-paper lookup direction, add the root-level lookup dictionaries to the catalog, and clarify that `guide/` stores external Fluent guide/manual references while reusable procedures belong in `wiki/guidance/`.
- Notable assumptions introduced or removed:
  - Introduced the rule that dictionary files accelerate navigation but do not replace source verification for setup-critical values.
  - Clarified that the local `CFD_wiki/AGENTS.md` is a CFD_wiki guide, while the repository root `AGENTS.md` remains the cross-wiki routing contract.

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

## [2026-05-28] query | Clarify Fluent velocity-inlet hydraulic diameter
- Files created/updated:
  - `wiki/guidance/fluent-general-click-by-click.md`
  - `wiki/log.md`
- Reason: answer a Fluent 24 setup question about `Intensity and Hydraulic Diameter` for a square separator inlet and preserve the reusable click-path guidance.
- Notable assumptions introduced or removed:
  - Introduced guidance that hydraulic diameter should be recalculated from the active inlet face, and that artificial split zones should usually retain the physical upstream duct hydraulic diameter for the first controlled comparison.

## [2026-06-10] query | Build semi-automated `.meshdat` mesh-improvement workflow
- Files created/updated:
  - `wiki/guidance/workbench-meshdat-semi-automated-improvement.md`
  - `wiki/guidance/index.md`
  - `wiki/index.md`
  - `wiki/log.md`
- Reason: preserve a reusable workflow for conservative Workbench mesh-control trials that uses PyFluent to audit the baseline Fluent mesh, validate exported trial meshes, and avoid geometry or Named Selection changes.
- Notable assumptions introduced or removed:
  - Introduced the workflow boundary that Workbench control edits remain operator-driven while PyFluent handles reopen, audit, comparison, and reporting; preserved uncertainty that the `.meshdat` reopen may expose less diagnostic detail than the exported baseline `.msh`.

## [2026-06-10] query | Tighten split-inlet zone contract for semi-automated mesh workflow
- Files created/updated:
  - `wiki/guidance/workbench-meshdat-semi-automated-improvement.md`
  - `wiki/log.md`
- Reason: update the reusable guidance so split inlet zones must remain separate, exact Fluent-exported names and boundary types are enforced, bad-cell fractions are tracked at thresholds `0.15`, `0.10`, and `0.05`, and cell count is treated as diagnostic rather than the primary success rule.
- Notable assumptions introduced or removed:
  - Removed the earlier assumption that cell target should remain a main pass/fail rule for this workflow; introduced the stricter contract that `liquid-inlet` and `steam-inlet` must stay separate and that local region quality near the split edge and spiral blend still needs explicit review.
