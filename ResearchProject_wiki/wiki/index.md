# Research Wiki Index

## Project Layer
- `wiki/project/objective-and-scope.md`
- `wiki/project/roadmap.md`

## Templates
- `../template/spiral-inlet-run-validation-template.md`

## Setup Reports
- `../../Setup report/order-dictionary.md`
- `../../Setup report/00a-purnanto-setup-5000-live-audit.md`
- `../../Setup report/04-mixed-wet-half-actual-area.md`
- `../../Setup report/05-complete-two-phase-actual-area-no-brine-outlet.md`
- `../../Setup report/06-pure-phase-split-fixed-velocity.md`
- `../../Setup report/07-pure-phase-split-actual-area.md`
- `../../Setup report/07a-split-inlet-carrier-mesh-convergence.md`
- `../../Setup report/07b-split-inlet-constant-water-level-liquid-sink.md`
- `../../Setup report/07c-split-inlet-thickened-constant-water-level-liquid-sink.md`
- `../../Setup report/07d-split-inlet-capacity-matched-thick-sink.md`
- `../../Setup report/07e-split-inlet-adaptive-mass-balance-sink-control.md`
- `../../Setup report/07f-split-inlet-sink-thickness-rate-matrix.md`
- `../../Setup report/07g-split-inlet-resolved-brine-outlet-qualification.md`
- `../../Setup report/07h-split-inlet-resolved-brine-outlet-initial-liquid-pool.md`
- `../../Setup report/07i-split-inlet-resolved-brine-outlet-wfgc-sensitivity.md`
- `../../Setup report/07j-split-inlet-resolved-brine-outlet-transient-vof.md`
- `../../Setup report/07k-split-inlet-transient-vof-massflow-brine-outlet.md`
- `../../Setup report/07l-split-inlet-hydrostatic-rest-isolation.md`
- `../../Setup report/07m-split-inlet-zero-feed-pressure-opening-and-inlet-ramp.md`
- `../../Setup report/08a-steam-outlet-extension-student-trial.md`
- `../../Setup report/08-purnanto-one-inlet-massflow-recreation.md`
- `../../Setup report/08b-purnanto-baseline-enthalpy-dpm-sweep.md`
- `../../Setup report/08c-purnanto-spiral-inlet-enthalpy-dpm-sweep.md`

## Progress Layer
- `wiki/progress/current-status.md`
- `wiki/progress/experiments.md`
- `wiki/progress/blockers.md`
- `wiki/progress/brine-outlet-modelling-handoff-2026-08-21.md`
- `wiki/progress/brine-outlet-modelling-new-chat-prompt-2026-08-21.md`

## Technical Layer
- `../../PyAnsys/docs/PURNANTO_ENTHALPY_DPM_AUTOMATION_RUNBOOK.md`
- `../../PyAnsys/output/split_inlet_mesh_convergence_20260801/STUDY_DIAGNOSTIC_CLOSURE_20260805.md` - final diagnostic closure for setup `07a`, including the 900k liquid-inventory audit.
- `../../PyAnsys/output/split_inlet_constant_water_level_sink_20260807/implementation_summary.json` - machine-readable setup `07b` implementation and one-iteration source proof.
- `../../PyAnsys/output/split_inlet_constant_water_level_sink_20260807/mesh-900k_tau0p100_qualification_v1/QUALIFICATION_RESULT.md` - completed clean-900k `tau=0.1 s` qualification, classified diagnostic/unresolved after 6,000 full-strength iterations.
- `../../PyAnsys/output/split_inlet_thickened_water_level_sink_20260808/mesh-900k_band0p140165_tau0p100_v1/QUALIFICATION_RESULT.md` - setup `07c` 16-layer-equivalent sink sensitivity, completed diagnostic/unresolved after 2,000 full-strength iterations.
- `../../PyAnsys/output/split_inlet_thickened_water_level_sink_20260808/mesh-900k_band0p140165_tau0p100_v1/analysis_correction.json` - machine-readable correction for the setup-07b/07c liquid-source double-count in derived controller fields.
- `wiki/technical/sources/purnanto-etal-2013.md`
- `wiki/technical/purnanto-live-setup-reference.md`
- `wiki/technical/purnanto-enthalpy-dpm-replication.md`
- `wiki/technical/purnanto-spiral-inlet-enthalpy-dpm-replication.md`
- `wiki/technical/v2-purnanto-spiral-inlet-geometry.md`
- `wiki/technical/pyfluent-trial3-one-inlet-reconstruction-smoke-test.md`
- `wiki/technical/mesh-trial1-semi-automated-workflow.md`

## Literature Layer
- `wiki/literature/matrix.md` - now includes linked cross-wiki anchors for Pointon et al. 2009 and Chen et al. 2025.

## Core Models
- `wiki/model/baseline-cfd.md`
- `wiki/model/inlet-regimes.md` - now tracks the planned two-zone split-inlet upgrade path.
- `wiki/model/validation.md`
- Cross-wiki mesh synthesis: `../../CFD_wiki/wiki/synthesis/mesh-quality-and-resolution-patterns.md`

## Gaps and Synthesis
- `wiki/gaps/open-questions.md`
- `wiki/synthesis/`
