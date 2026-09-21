# Model-specific evidence

Use only the branches relevant to the active experiment.

## Multiphase / routing

Track inlet and outlet phase mass fluxes, total/phase imbalance, continuous
liquid inventory, and any question-specific region inventory. For inventory
problems, distinguish temporary accumulation/drainage from stationary balance.

## DPM

Require actual tracking evidence. Cover all live injections relevant to the
question and retain tracked counts, fates, and mass-transfer/escape/trap evidence
needed by the experiment. Missing injections/rows are missing evidence, not zero.

Verify injection identity, source scope, particle type, and tracked rows before
interpreting output. Keep raw transcript/output linked to parsed results, retain
fate/zone and represented or net mass flow with units, and distinguish mechanism
counters from terminal particle fates so mass is not double-counted. Reuse the
access pattern—not case names or paths—from `PyAnsys/src/pyansys_fluent/dpm_reports.py`,
`dpm_transcript.py`, and `PyAnsys/scripts/inspection/run_dpm_particle_tracks.py`.

## Eulerian Wall Film

Analyse EWF only on confirmed active film walls/mechanisms. Report the film
quantity and spatial/temporal evidence that answer the experiment question.
Do not infer time-integrated closure from a final snapshot.

Verify active film walls, enabled mechanisms, phase coupling, and extraction
scope first. Keep inventory/cumulative quantities (`kg`) distinct from rates or
sources (`kg/s`), and distinguish local, maximum, and area-weighted reductions.
Use the current reusable patterns in `PyAnsys/src/pyansys_fluent/ewf_core.py`,
`ewf_audit.py`, `ewf_flux.py`, `ewf_reports.py`, and
`PyAnsys/scripts/inspection/run_ewf_dpm_diagnostics.py`; live wall/field names
win over a past case's assumptions.

## Numerical adequacy

Use the smallest set of residual, balance, stationarity, restart/continuation, or
mesh/time-step checks needed for the intended claim. Qualification standards
come from the experiment contract, not from a generic dashboard.
