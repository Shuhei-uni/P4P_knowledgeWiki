# Declared control window — terminal 1000 iterations

This is the control window for all subsequent comparisons in the current
Family R0 record.

The full-loading state preceding this window was reached through the lineage
recorded in [provenance.md](provenance.md). In particular, the approximate
lowest-inlet hold and the preceding 2,000-iteration inlet ramp are preparation
history; they are not part of this control window.

## Window identity

- Control name: `R0-SMOOTH-CONTROL-LAST1000`.
- Parent/start artifact: the verified first-continuation endpoint
  `P71A-R0-SMOOTH-CONTROL-COUPLED-GLOBAL-TIME-full-loading-plus1000`.
- Control run: second Coupled / Global Time Step continuation in
  `PyAnsys/output/phase71a_r0_control_run4`.
- Requested window: exactly 1000 additional native steady iterations.
- Checkpoint ledger: expected native coordinates 4580 through 5580.
- Fluent restarted transcript: native rows 4586 through 5586; the six-row
  restart-boundary offset is retained as an evidence note, not corrected by
  interpolation.
- Solver calls: batches of 100; report files refreshed every native iteration.

## Comparison rule

Use only the terminal second-continuation window as the R0 control for future
comparisons. In particular, use:

- [run4 residual history](/Users/shuheiyokkaichi/Developer/P4P_knowledgeWiki/PyAnsys/output/phase71a_r0_control_run4/residuals-batched-resume.json)
- [run4 analysis summary](/Users/shuheiyokkaichi/Developer/P4P_knowledgeWiki/PyAnsys/output/phase71a_r0_control_run4/analysis/summary.json)
- [run4 completion receipt](/Users/shuheiyokkaichi/Developer/P4P_knowledgeWiki/PyAnsys/output/phase71a_r0_control_run4/authoritative-completion-receipt.json)
- [run4 liquid inventory plot](/Users/shuheiyokkaichi/Developer/P4P_knowledgeWiki/Project/experiments/phase-07-1a-absorber-convergence/roughness-family/r0-smooth-control/control-07-liquid-inventory-dedicated.png)

The first continuation (`run3`, expected 3580–4580) remains provenance and
warm-up history only. Do not pool its statistics with the terminal control
window when reporting a new case comparison.

## Control endpoint

- Case: `C:\Users\syok443\OneDrive - The University of Auckland\P4P-Fluent-Artifacts\Phase71A\FamilyR\finals\P71A-R0-SMOOTH-CONTROL-COUPLED-GLOBAL-TIME-PLUS1000\20260922T162500Z\P71A-R0-SMOOTH-CONTROL-COUPLED-GLOBAL-TIME-PLUS1000-full-loading-plus1000.cas.h5`
- Case SHA256: `4fd493972839929f1f0922ad42679456d1f4aea294da86e4b13d6b7c32f754fc`
- Data: `C:\Users\syok443\OneDrive - The University of Auckland\P4P-Fluent-Artifacts\Phase71A\FamilyR\finals\P71A-R0-SMOOTH-CONTROL-COUPLED-GLOBAL-TIME-PLUS1000\20260922T162500Z\P71A-R0-SMOOTH-CONTROL-COUPLED-GLOBAL-TIME-PLUS1000-full-loading-plus1000.dat.h5`
- Data SHA256: `b2261fac8626b2e338c3a9c80c334c8a910d1bfb536f782ef9234623f00e1a72`

The control is a numerical reference, not a claim of converged or physically
validated separator operation. Its terminal command remained
`116.9200000000001 kg/s`, with command error `4.26e-14 kg/s`; persistent
reverse flow and turbulent-viscosity limiting remain part of the control
evidence and must not be omitted from comparisons.
