# E8 — documented Mixture startup under fixed E6 treatment

**Historical prospective design — superseded by user closure on29 September2026.** E8 stopped atN128 before its first gate. No continuation authorized. See [results](results.md) and [phase closure](../../closure.md).

Selected prospectively on29 September2026 after completed G7. This is the **last** discovery contrast permitted by Andy's accepted bounded Phase7b finish. Implementation and ordinary recovery are authorized; no physical transient, EWF/drainage, feed ramp, source rewrite, additional parameter sweep or automatic horizon expansion is selected.

## Hypothesis and precedent

Jointly freezing Volume Fraction and Slip Velocity while the flow develops, then restoring both, may reach a more credible full-equation steady endpoint than E6's direct start from the same Hybrid field. This is NEW relative to unstaged E6/E7. Earlier changes to solver coupling, CFL, all-phase fraction equations and sink coefficient did not restore conservation. Shuhei's different mesh/source/loading history cannot isolate this startup effect. The [G7 result](../coupled-nphase-weaker-sink/results.md) and [source audit](../source-treatment-audit.md) support one distinct startup test; neither supports open-ended tuning.

The vendor sequence is configure Mixture, deselect VF/slip together, seek an initially converged flow field, then reselect both [Fluent 2025 R2 UG §27.8.2.2.1–2](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/flu_ug_sec_multiphase_solution.html). The preserved [documentation packet](../../../../../PyAnsys/output/phase07b-convergence-investigation/e7/recovery-n500-20260928/resume-n1631/network-recovery-20260928T0408/startup-guidance-packet.md) records applicability gaps. The numeric budget and gate below are investigator choices, not vendor values.

## Parent, delta and invariants

Use E6's saved **prepared N0** pair, whose exact fresh physical field and ordered geometry were proved against the original common clean Hybrid parent. Its prepared source/numerics are the final E6 treatment. E6's developed N5000 field is a comparison control, never the startup parent. Loading the verified prepared N0 introduces no initialization, field patch, iteration-counter offset or hidden solve. Record exact pair identity and hashes/readbacks in the machine map before compute.

Only equation enablement during conditioning changes. Freeze `mp` (Volume Fraction) and `drift` (Slip Velocity) together; retain `flow` and `ke`. Keep Mixture/slip physics, N-phase, full pure-phase equal-velocity split feed, S40 collector, tau0.02s, all source definitions/assignments/update interval1, Coupled, pseudo-time Off, CFL20, pressure/momentum relaxation0.5/0.5, VF relaxation0.4, drift relaxation0.1, spatial schemes and original residual policy. Energy/DPM/EWF remain off, brine outlet remains a wall. Do not reduce feed, disable source definitions, change materials or repatch the initial fractions.

Before solve, prove live equation paths, both disable/restore transitions without advancing, source/settings/geometry/physical-field parity, and unique child save/reopen persistence. Retain both raw phase fractions and native normalized fields. Verify actual frozen fraction and slip-field behavior during the N50 smoke; missing storage or unexpected behavior is a capability/implementation issue to reconcile, not a scientific failure or permission to change the contrast. Restore baseline after the zero-step capability test before constructing the final frozen child.

## Prospective horizon and switch gate

Total absolute cap5000 with no counter reset; at most1000 conditioning iterations. Solve to N50 for instrumentation/frozen-field smoke, then N200,300,…,1000 for conditioning decisions. The first possible switch isN200. Batch boundaries are evidence/decision checkpoints; they are not convergence claims.

At each candidate switch, require all of the following using native recorded histories:

1. Every active conditioning residual (continuity, x/y/z velocity, k, epsilon) is below1e-3 at **every sample** in the latest100 iterations. Do not synthesize VF residuals while inactive and do not renormalize curves.
2. Mean absolute independent source-inclusive **native mixture** closure in that100-iteration window is≤1% of measured total feed. Record phase budgets as diagnostics; inactive phase equations cannot qualify the final model.
3. For each recorded inlet-to-outlet pressure drop, the absolute change between the latest100 mean and preceding100 mean, divided by max(abs(two means),100Pa), is≤1%.
4. The corresponding change in mean native maximum speed, divided by max(abs(two means),1m/s), is≤1%.

Switch at the first passing checkpoint. Restore VF/slip **together**, prove both phase residual monitors and all original E6 final settings/source/feed policies, save a unique switch pair, and continue without initialization or counter reset to absoluteN5000. This gives4000–4800 full-equation/full-feed iterations. The switch changes startup history only.

If the gate remains unmet atN1000, preserve the conditioning endpoint and close the bounded attempt as **conditioning unsuccessful within the allowed budget**. Do not force a switch and claim that the documented converged-flow prerequisite passed. This outcome leaves a developed full-equation E8 endpoint untested. A solver failure gets a bounded numerical disposition; recording/configuration failures are recovered separately without silently spending or increasing the horizon. No poor full-stage budget or speed event alone is an early-stop rule. No additional replay or compute-bound expansion is automatic.

## Evidence and decision

Keep stage identities, actual native iteration, active residual schema and unmodified stage transcripts. Scalar reports and exact-face phase flux/speed histories are required per completed iteration, with native source/recomputed source and one-iteration lag audit. Preserve full-domain and regional liquid mass/volume, native mixture and independent phase budgets, pressure drops, carryover/vapor routing and limits/extrema. Preserve both raw fractions, raw inventory, raw phase-sum extrema and independently normalized/native inventory parity; normalization is not conservation. Raw SV_MASS_IMBALANCE stays uncalibrated.

Save paired unique local-PC checkpoints atN0/N50, every500, switch and terminal; gates at200/300/400 etc save their decision evidence. Initial/switch/final whole-cell snapshots and initial/final horizontal/full-height axial fields are required. Preserve scheduled2600/2700/2800 and≥500m/s-triggered whole-cell snapshots withN+1/N+5 followups during any full stage. Complete evidence prefixes and reconcile uncertain RPC outcomes before retry; never attach a second controller.

| Artifact | Question and quantities | Comparison/reduction and use |
| --- | --- | --- |
| E8-F1 budgets/inventory | Did staging improve independent phase/native-mixture closure and bound inventory? Signed and absolute closure % measured phase/total feed; native regional/whole liquid volume m³; applied source kg/s | Raw histories with stage boundary, E6/E8 N4501–5000 statistics, inventory means4001–4500 vs4501–5000. If no switch, conditioning gate table and raw history only; no terminal comparison claim. |
| E8-F2 residual/conditioning | Did the declared initial-flow gate pass, and do all restored equations remain small? Actual six/eight residuals, pressure drops Pa, max speed m/s | Real native indices and stage-specific schemas; all gate windows and first passing checkpoint. N4501–5000 all-eight residual maxima if full stage completes. |
| E8-F3 native spatial fields | Are inventory/flow differences localized consistently with integral evidence? Native normalized liquid VF and speed | Matched E6/E8 inlet-height horizontal and full-height axial planes, shared scales/cameras, direct visual QA. If conditioning fails, field description of the frozen endpoint explicitly excludes steady full-model validation. |

The restored-stage necessary criteria retain≤1% mean absolute **each** phase/native-mixture closure,≤1% inventory-window change, all eight residuals<1e-3 throughout N4501–5000, complete histories and spatial evidence. Regional budgets must reconstruct the whole ledger. Report signed versus mean absolute vapor error. Passing these is insufficient for acceptance: prospectively design bounded persistence/restart qualification before further compute. Otherwise close the tested Phase7b route with finite-horizon, startup applicability and model/source linearization limits. No claim that the physical separator cannot work or that no steady solution exists follows from a failed bounded test.
