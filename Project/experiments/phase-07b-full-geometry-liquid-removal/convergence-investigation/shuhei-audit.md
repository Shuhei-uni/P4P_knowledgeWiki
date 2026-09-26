# Shuhei R0 audit and transferable lessons

Audited 22 September 2026 UTC, local HEAD `b8c7830ef3dc56b2454d319d9d154b6b0de6cb26`.
This supersedes the older [transfer review](../shuhei-transfer-review.md) for the
newly pulled R0 records. **The reported residual improvement is substantial,
but it does not establish a balanced steady solution or isolate its cause.**

## Evidence and provenance

The [R0 results](../../phase-07-1a-absorber-convergence/roughness-family/r0-smooth-control/results.md),
[provenance](../../phase-07-1a-absorber-convergence/roughness-family/r0-smooth-control/provenance.md),
[control-window definition](../../phase-07-1a-absorber-convergence/roughness-family/r0-smooth-control/control-window.md)
and [7.2A handoff](../../phase-07-2a-wall-liquid-routing/baseline-control-handoff.md)
are locally available, with scripts and PNG figures. The referenced run3/run4
raw histories, transcripts and final binary pairs are not present in this
checkout; foreign absolute paths are not verified local evidence. Reported
hashes cannot be independently checked here. No access to Shuhei's session was
attempted. His records themselves retain a non-qualified conclusion.

Reported lineage is an unintended approximately 1500-iteration 25%-feed hold
(the first driver calculated but did not apply the intended ramp), a corrected
2000-iteration ramp with actual BC writes/readbacks, then SIMPLE to Coupled
**and** Global Time Step, followed by 1000 warm-up and 1000 control iterations.
The declared control ledger is 4580–5580; native coordinates are 4586–5586.
This developed parent differs fundamentally from Andy's fresh full-feed start.

Verified in the pulled baseline-v2 build manifest: 60,964 truncated-domain cells,
715 collector cells, split mass-flow inlets, and a liquid source normalized by
available liquid volume. Andy uses 620,431 full-domain cells, 41,258 S40 cells,
split velocity inlets and a fixed tau law. Material/numerical inheritance also
differs. Thus this is not an isolated solver comparison.
Specifically, the pulled v1 snapshot inside the baseline-v2 build records
first-order k, disabled warped-face correction and a different PRESTO option;
its liquid/vapor densities are 881.210876/5.797434 kg/m³, versus Andy's
881.77/5.73 kg/m³. These are verified predecessor settings; the unavailable
run4 manifest prevents independently proving every inherited setting at run4.

## What the reported numbers demonstrate

The control endpoint reports continuity 0.0027841 and phase fraction 0.00054762.
The locally inspected residual figure confirms continuity oscillations around
0.002–0.005, epsilon around/above 0.001, and recurring phase-fraction peaks
above 0.001. Small momentum residuals are encouraging but the seven-equation
Phase-7b criterion is not met. Warm-up maxima must not be labelled control
window maxima.

Using the **reported rounded endpoint values**, inflow-positive convention,
liquid feed 116.92 kg/s, vapor feed 80.69 kg/s, liquid removal 116.92 kg/s,
liquid outlet −24.3344 kg/s, vapor outlet −80.2509 kg/s and native mixture
outlet −104.5823 kg/s gives:

| Budget | Signed error, kg/s | Error/feed |
| --- | ---: | ---: |
| Liquid boundary plus source once | −24.3344 | −20.8129% |
| Vapor boundary | +0.4391 | +0.5442% |
| Native mixture boundary plus source once | −23.8923 | −12.0906% |

Assumptions: pure-phase inlets, closed lower wall, no other mass transfer.
The phase-summed outlet differs from the reported native mixture outlet by
0.0030 kg/s; preserve that readback/report precision discrepancy. These are
endpoint calculations, not independently reconstructed window statistics.
Reported total liquid mass settles near 295.85 kg, but stationarity alone does
not repair the nonzero phase budget. The records report reverse flow and
turbulent-viscosity limiting throughout the control window; local extent and
severity require unavailable raw fields.

The build's source is `−command*alpha/max(integral(alpha dV),1e−6 m³)` in the
collector, with command equal to the incoming liquid flow. Above the floor,
integrating this expression removes the entire liquid feed by construction.
Matching command and removal therefore verifies source execution, not closure.
With positive liquid carryover, the same law cannot simultaneously give zero
steady liquid balance unless another liquid contribution changes the budget.
Momentum and k/epsilon removal are present; mass is attached to phase 2 only.
Do not copy this normalized law merely because command error is tiny.

## Instrumentation and analysis checks

Code reviewed: `run_p71a_r0_control_continuation.py`,
`resume_p71a_r0_control_batched.py`, `analyze_p71a_r0_control_batched.py`,
`finalize_p71a_r0_control_evidence.py`, and `stage4_native.configure_residual_history`.

- The coupling setter verifies steady/Coupled/global, but does not enforce a
  complete before/after settings diff. Newly active controls need inspection.
- Residual history configuration changes storage/display length only; it does
  not itself renormalize. The inherited scale factors and restart history
  cannot be verified from the pulled run4 raw files because those are absent.
- **Observed figure mismatch:** control residuals span roughly 4586–5586,
  whereas the labelled control inventory and closure PNGs span roughly
  3586–5586, including warm-up. The analyzer does not explicitly filter the
  declared control window. Whole-file scalar summaries are not clean run4-only
  evidence without reconstruction.
- The analyzer uses the total-inventory iteration array for other report
  arrays without proving their coordinate alignment; residual duplicates use
  last-write wins without conflict detection. These are verification gaps,
  not proof that the underlying values are wrong.
- Its plotted mixture closure is the sum of phase budgets rather than an
  independent native-mixture budget. The kg/iteration inventory derivative is
  correctly distinguished from kg/s and must not cancel physical mass error.
- Finalization accepts supplied hashes and includes a hardcoded warm-up native
  coordinate note. Provenance receipts need case-specific confirmation.

## Interpretation and next test

[G3](../spike-diagnostic/results.md) replicated original T020 at recorded
precision and located sampled speed excursions near the inlet upper elevation,
well above the collector. This weakens a recording-artifact explanation but
does not distinguish pressure/velocity coupling, indirect source feedback,
startup history, phase transport or local mesh sensitivity.

The [version-matched guidance](../../../../CFD_wiki/wiki/guidance/fluent-general-click-by-click.md#steady-mixture-coupling-and-residual-comparisons-2025-r2)
supports ordinary Coupled with volume fraction remaining segregated, and allows
pseudo time Off. Global pseudo time carries a documented multiphase mass
conservation caveat; whether a volumetric sink resolves it is unspecified.
Purnanto 2013 reports SIMPLE and Hybrid (§3.3), excludes brine-pipe flow (§3.1),
and supplies no residual/phase-closure acceptance recipe. Pointon 2009 uses
DPM removal and does not establish an Eulerian Mixture sink convergence recipe.
Neither primary paper verifies Global Time Step as the solution here.
Primary copies checked by focused literature lookup:
[Purnanto 2013, §§3.1 and 3.3](https://www.researchgate.net/publication/269519626_CFD_MODELLING_OF_TWO-PHASE_FLOW_INSIDE_GEOTHERMAL_STEAM-WATER_SEPARATORS)
and [Pointon 2009, pp.945–946](https://publications.mygeoenergynow.org/grc/1028587.pdf).
The local raw-paper directory is absent; maintained source records provide
the [Purnanto](../../../../CFD_wiki/wiki/sources/purnanto-2013-cfd-geothermal-separator.md)
and [Pointon](../../../../CFD_wiki/wiki/sources/pointon-2009-geothermal-separator-sizing-cfd-validation.md)
lookup context. A geothermal-flow-meter Coupled lead remains unverified and
is not promoted to a separator or Global Time Step prescription.

Select [E4 Coupled, pseudo time Off](coupled-off/setup.md) from the same fresh
parent. This isolates the coupling algorithm and its required relaxation/linear
solver controls from adding Global Time Step. A conserved, persistent response
would justify qualification; residual-only improvement would direct attention
back to source/phase coupling. Global pseudo time and developed-parent loading
remain separate possible future contrasts, not an automatic queue.
