# Autonomous convergence investigation after E3

**CLOSED — 29 September2026.** Andy instructed stopping E8 and concluding Phase7b. [Closure](../closure.md) supersedes all continuation and experiment-selection provisions below. G1–G7 complete, no qualified case; E8 user-stopped atN128 before first conditioning gate. No further simulation authorized.

## Authority and objective

On 22 September 2026 Andy asked that, after the current run finishes, the agent
audit Shuhei's newly pulled work, check its correctness, learn from its apparent
residual improvement, consult literature and documentation, and keep working
autonomously through the next steps toward good residuals, particularly
continuity. He explicitly requested recurring follow-through without routine
human help. This expands the earlier one-case-only authority **after E3/G3**;
it does not change the running E3 experiment.

The objective is a credible steady full-geometry liquid-removal model with
acceptable continuity and other equation residuals, source-inclusive phase and
mixture mass closure, bounded liquid inventory, and useful phase routing.
Lower displayed residuals alone do not satisfy it. Phase 7b remains the owner
because the geometry and scientific objective are retained.

Phase-loop may select, implement, execute, analyse and revise evidence-backed
numerical and collector-source experiments without another routine approval.
It may test pressure–velocity coupling, steady pseudo-time, relaxation,
discretization, source formulation/coupling and startup/loading strategy, and
other justified diagnostics within this steady full-geometry objective.
Preserve the original model as a comparison control. Each changed assumption
must be explicit; Shuhei's settings are evidence to test, not inherited truth.

Keep the target full-feed operating condition, full geometry, closed brine
boundary, liquid-removal objective and Python/Fluent API route. Start from the
existing Energy-off, Mixture/RNG, DPM/EWF-off basis. A staged inlet history is
a development treatment and must finish and be assessed at full loading.
The earlier rejection of a physical transient/pool-control model remains in
force. Do not turn Shuhei's separate phase or machine into this campaign.

## Accepted bounded finish — 28 September 2026

Andy approved execution of the [26 September review](phase-review-2026-09-26.md) plan with “Sounds good. run it.” This narrows the remaining work to E7 recovery/completion, the source-treatment/linearization audit, and—only if still justified—one isolated Fluent-documented Mixture startup contrast capped at 5000. Record its delta, parent, comparison window, startup/full-feed allocation and stopping conditions before compute. If a concrete implementation defect is found, resolve it explicitly before selecting further treatment; do not add an unbounded series of cases. Passing numerical criteria requires prospectively bounded persistence/restart qualification. Otherwise close the tested route with explicit evidence limits. A separate EWF/drainage phase is not selected by this instruction.

E7 now uses the [N2500 recovery design](coupled-nphase-weaker-sink/recovery-n2500.md), following Andy's “do your recommended” instruction on29 September. Retain original N1–500 and first replay N501–2500, then replay N2501–5000 from the exactly verified N2500 pair:2500 new steps, retained absolute5000, prospective cumulative attempted ceiling6000 including at most500 retired steps in each lost N500–1000/N2500–3000 block. This explicitly supersedes the earlier [N500 recovery](coupled-nphase-weaker-sink/recovery-n500.md) ceiling5500. Retired tails remain immutable and excluded from the new trajectory. Original/recovery pair reopens and N2505 recording passed; phase-state owns current supervision. No further automatic compute-bound expansion is authorized.

The [28 September source audit](source-treatment-audit.md) is complete: no concrete source assignment/sign defect was found, while expression-source implicit derivatives remain unverified.

A focused [startup guidance packet](../../../../PyAnsys/output/phase07b-convergence-investigation/e7/recovery-n500-20260928/resume-n1631/network-recovery-20260928T0408/startup-guidance-packet.md) confirms the documented joint Volume Fraction/Slip Velocity freeze and restore sequence; the conditioning count and quantitative gate remain investigator choices. E6 slip relaxation is already0.1. Combined behavior with N-phase, full split feed and expression removal requires live verification in the E8 implementation below. The documentation lookup itself did not select a run; completed G7 now supports that final selection.

## Final selected discovery contrast — 29 September 2026

G7 is complete and numerically inadequate; all machine and spatial audits pass. Select [E8 documented Mixture startup](mixture-startup/setup.md), classified NEW against the completed unstaged E6/E7 starts. Preserve E6's final treatment and original clean N0 lineage, freeze Volume Fraction and Slip Velocity together, and restore both only after the prospective conditioning gate. Conditioning stops by1000 and total cap is5000. A conditioning-gate failure closes this bounded attempt without pretending the full-equation endpoint was tested; a passing switch leaves at least4000 full-equation/full-feed iterations. No second discovery contrast, automatic extension or new physical phase follows. E7 is complete and must never be relaunched. The ordered work below records the historical investigation sequence.

## Ordered work

1. Finish the existing S40-T020-DIAG controller at its absolute N5000 cap or
   verified numerical-failure disposition. Preserve its endpoint, recover any
   missing evidence and complete G3, including original-T020 comparison and
   the N2700/spike-localisation question. Do not perturb it for this audit.
2. Audit the newly pulled Shuhei evidence. Start with commit `b8c7830`
   (`Record Phase 7.1A runs and control provenance`) and the Phase 7.1A
   [R0 results](../../phase-07-1a-absorber-convergence/roughness-family/r0-smooth-control/results.md),
   [provenance](../../phase-07-1a-absorber-convergence/roughness-family/r0-smooth-control/provenance.md),
   [control window](../../phase-07-1a-absorber-convergence/roughness-family/r0-smooth-control/control-window.md),
   and Phase 7.2A [handoff](../../phase-07-2a-wall-liquid-routing/baseline-control-handoff.md).
   Identify any newer locally available evidence at audit time. Reconcile
   reports against raw histories, scripts, manifests and paired artifacts.
   Resolve foreign absolute paths to verified local copies when possible;
   explicitly separate missing raw evidence from demonstrated correctness.
3. Compare E3/G1/G2 with the audited Shuhei result. Consult maintained CFD_wiki
   evidence, version-matched official Fluent documentation and relevant primary
   literature where they can change the next decision. Use cfd-wiki's focused
   lookup branches as required; use cfd-numerical-analysis for numerical and
   spatial evidence and pyansys-workflow for implementation.
4. Rank competing explanations, choose the smallest useful controlled contrast,
   write its setup and evidence plan before compute, verify it, run it, analyse
   it, and repeat while a feasible test can materially reduce uncertainty.
   Do not stop at a list of suggestions when a justified test is in scope.

## Shuhei correctness and transfer audit

- Establish actual mesh/model/BC/material/source settings, initialization and
  loading history; distinguish intended commands from actual readbacks.
- Reconstruct Coupled / Global-Time-Step changes and their exact parent.
  The provenance reports an unintended low-inlet hold, a corrected ramp and
  two continuations. Treat these as potential confounders until audited.
- Check every equation's raw residual history, scaling/normalization, restarts
  and convergence settings. Reconcile the reported 4580–5580 ledger with
  4586–5586 transcript coordinates without interpolating missing evidence.
- Independently recompute phase and mixture balances with native applied
  source counted exactly once; distinguish source command tracking from mass
  conservation. Inspect liquid carryover, vapor routing, inventory drift,
  reverse flow, limiting and extrema alongside continuity.
- Check source phase targeting, momentum consequences, units/signs,
  liquid availability, iteration lag and any density/volume assumptions.
- Separate evidence for solver improvement from changes in geometry/mesh,
  developed initial field, loading and source law. Identify the closest
  transferable contrast and what the existing records cannot isolate.

## Experiment and claim discipline

Use a single sequential controller on Andy's recorded Fluent endpoint. Use
`PyAnsys/.venv/bin/python` and Fluent API only for PC operations; never
terminate Fluent. Preserve valuable case/data endpoints before replacement,
use unique local-PC checkpoint names, and reconcile uncertain RPC outcomes
before retries. Do not interrupt or duplicate another active controller.
Keep all raw evidence immutable and preserve unrelated work.

Use bounded runs with a predeclared absolute horizon, checkpoints, comparison
window and stopping conditions. The default new discovery horizon is at most
5000 iterations per child. A longer continuation or numerical qualification
is allowed only after recording the evidence-based reason, cumulative horizon,
required persistence/restart test and decision criteria before further solve;
it is not a blind extension because residuals look promising. No parallel
campaign or unlimited solve job is implied. Ordinary balance failure alone
does not retroactively become an early-stop rule.

Carry forward raw scalar/phase/source/flux histories, every equation residual,
inventory, extrema and initial/final native fields. Retain localised diagnostic
capture when it addresses the hypothesis. Core comparisons should expose the
controlled change, raw oscillation/drift and relevant native spatial evidence.
Declare fresh-start versus developed-parent intent and keep parent/normalization
consistent within each contrast. Save/reopen and verify changed settings.

Retain the prior E3 screening criteria for comparison (all seven residuals
below 1e-3 in the declared late window, mean absolute phase/mixture closure
within 1% of feed, and inventory-window change within 1%). For a new solver
path, audit residual definitions/scaling first and predeclare any justified
criterion difference rather than manufacturing improvement by normalization.
Numerical qualification needs suitable late-window/restart persistence;
physical validation requires separate external evidence.

## Durable outputs and continuation

This folder owns the post-G3 audit, hypothesis ranking and experiment map.
Create `shuhei-audit.md` with cited correctness/transfer findings, and
`results.md` with the evolving supported answer and next decision. Give each
selected child a setup/result record and link machine evidence in PyAnsys.
Update phase-state with exactly the active child, disposition and next action.
Keep general literature/method findings in CFD_wiki with primary provenance.

The existing 15-minute task heartbeat continues from E3 supervision into this
investigation; it must not pause simply because G3 is complete. Keep the old
G1 automation paused. Notify Andy only on meaningful findings, a consequential
change of direction, demonstrated completion, failure or an action that truly
requires him. Continue routine research, repairs and in-scope choices without
asking. If an external block persists, record it and complete independent
research/analysis; do not repeatedly launch the same failed action. Pause only
on Andy's instruction, an evidenced terminal conclusion, or a durable external
block with no remaining independent work, and state the actual limitation.
