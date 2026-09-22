# Family R0 smooth control — Coupled / Global Time Step results

> **Control designation:** The terminal second-continuation window is the
> declared R0 control for subsequent comparisons. Use only the last requested
> 1000 iterations from `run4` (expected native 4580–5580; transcript
> 4586–5586). The preceding `run3` 1000 iterations are warm-up/provenance
> history and must not be pooled into control statistics. See
> [control-window.md](control-window.md). The preparation lineage leading to
> the full-loading parent is recorded in [provenance.md](provenance.md): an
> approximate accidental low-inlet hold, the controlled 2,000-iteration inlet
> ramp, and then the Coupled/Global-Time-Step numerical continuation.

## Outcome

The requested continuation completed all four checkpoint stages and wrote a
durable final case/data pair. The run survived the full requested horizon
without an AMG failure, floating-point exception, nonfinite residual event,
fatal solver event, or node failure. That is positive evidence for numerical
endurance of this control branch, but it is not a steady-convergence pass.

The control command remained matched to the applied phase-2 absorber source:
the terminal command was `116.9200000000001 kg/s`, the absorber removal was
`116.9200000000001 kg/s`, and the terminal command error was
`-1.42e-14 kg/s`.

## Checkpoint progression

| Requested offset | Expected native coordinate | Total liquid mass (kg) | Lower liquid mass (kg) | Command error (kg/s) | Events |
| ---: | ---: | ---: | ---: | ---: | --- |
| +250 | 3830 | 255.557 | 0.08653 | 5.68e-14 | reverse flow; viscosity limiting |
| +500 | 4080 | 281.222 | 0.11302 | 1.42e-14 | reverse flow; viscosity limiting |
| +750 | 4330 | 290.083 | 0.00409 | 1.28e-13 | reverse flow; viscosity limiting |
| +1000 | 4580 | 293.703 | 0.00748 | -1.42e-14 | reverse flow; viscosity limiting |

Fluent's restarted transcript/report rows extend to native coordinate 4586.
The checkpoint ledger reaches the requested +1000 coordinate at 4580; this
six-iteration restart-boundary discrepancy is retained rather than silently
rounded away. The stale RP iteration variable is not used to close the count.

## Numerical health and boundedness

Across the stitched native transcript window (3580–4586), the maximum
continuity residual was `9.3745e-3`; the terminal value was `2.7644e-3`. The
maximum phase-2 volume-fraction residual was `4.1527e-3`; the terminal value
was `5.3597e-4`. Momentum residuals were approximately `3e-6` to `7e-6` at
the terminal point, while `k` and `epsilon` were `1.56e-4` and `1.22e-3`.

The residual envelope is calmer after the initial part of the continuation,
but it remains oscillatory and has recurring spikes. The run also logged 1001
reverse-flow messages and 975 turbulent-viscosity-limit messages. The reverse
flow was typically about 240–250 outlet faces; viscosity limiting rose to
about 1180 cells near the terminal window. Thus the branch is more
long-enduring than an immediate numerical failure and shows a lower late
residual level than its early continuation window, but it is not numerically
quiet enough to call converged or fully bounded.

## Inventory, source, and closure evidence

Total liquid inventory increased from `182.518 kg` at the first report point
to `293.703 kg` at the terminal report point, while the lower-zone inventory
oscillated between small values and about `0.113 kg`. The terminal lower-zone
volume was `8.4922e-6 m^3`. This is not bounded operating behaviour in the
phase-specific sense required for promotion.

The direct source audit is explicit: the terminal readback reports
`user_defined_functions.source_terms = none`; phase 1 sources are disabled;
the phase-2 source is the named `P71V2Sink` term in the lower zone, with
matching sink momentum terms. No direct phase-1 mass source was introduced.

At the terminal point, signed source-inclusive diagnostics were:

- phase 1 boundary closure (steam inlet + steam outlet): `+0.5168 kg/s`;
- phase 2 boundary closure plus absorber source: `-24.0143 kg/s`;
- mixture boundary closure plus absorber source: `-23.4975 kg/s`;
- finite-difference total-liquid storage diagnostic: `-0.01395 kg/native iteration`.

These are algebraic diagnostics, not a claim of dimensional physical-time
balance. The nonzero mixture closure and moving inventory are evidence that
the solution is still developing/nonstationary despite the stable command
tracking.

## Requested comparison conclusion

Relative to the supplied R0 reference as a continuation test, the
Coupled/Global-Time-Step branch is the more enduring numerical endpoint: it
completed the requested +1000 batched horizon with finite residuals and no
AMG/FPE/nonfinite/fatal event. It is somewhat calmer in late residual level
than at the beginning of this continuation. It is not more bounded in the
scientific sense: total liquid mass keeps increasing, lower-zone liquid does
not settle, reverse flow persists, and viscosity limiting remains widespread.
The result therefore supports “longer-enduring and somewhat calmer residuals”
but does not support “bounded converged operating state.” A matched
same-horizon R0 run with the old solver controls would still be needed for a
strict causal comparison of the control change itself.

## Figures and machine evidence

The compact figure set was generated from the native report histories and
stitched transcript after the +1000 checkpoint; report files themselves were
refreshed every native iteration while solver calls used 100-iteration
batches. All PNG plots are stored directly beside this `setup.md` and
`results.md` in the R0 record directory. The [plot manifest](plot-manifest.md)
describes the `control-*` and `warmup-*` naming.

- [warm-up total liquid inventory](warmup-01-total-liquid-inventory.png)
- [warm-up command and absorber error](warmup-02-command-absorber-error.png)
- [warm-up lower-zone availability](warmup-03-lower-zone-availability.png)
- [warm-up phase-resolved fluxes](warmup-04-phase-fluxes.png)
- [warm-up source-inclusive closure and storage](warmup-05-source-inclusive-closure.png)
- [warm-up residual health](warmup-06-residual-health.png)

Durable final pair:

- Case: `C:\Users\syok443\OneDrive - The University of Auckland\P4P-Fluent-Artifacts\Phase71A\FamilyR\finals\P71A-R0-SMOOTH-CONTROL-COUPLED-GLOBAL-TIME\20260922T160500Z\P71A-R0-SMOOTH-CONTROL-COUPLED-GLOBAL-TIME-full-loading-plus1000.cas.h5`
- Case SHA256: `d3391ad6b48cfa828edea5f32f9fedb9f9ad3e0d4aa52dfb4258a9e3f31f5c93`
- Data: `C:\Users\syok443\OneDrive - The University of Auckland\P4P-Fluent-Artifacts\Phase71A\FamilyR\finals\P71A-R0-SMOOTH-CONTROL-COUPLED-GLOBAL-TIME\20260922T160500Z\P71A-R0-SMOOTH-CONTROL-COUPLED-GLOBAL-TIME-full-loading-plus1000.dat.h5`
- Data SHA256: `85b8a02cfdeb71d3fd7c18919ddcad13d2e82d682b64e145f9728843075da854`

The result is discovery evidence only. It does not qualify the absorber for
Phase 08 or establish plant drainage performance.

## Second +1000 continuation

This second continuation is the authoritative terminal control window for
future case comparisons. The `run3` continuation above establishes the field
from which this window starts; it is not part of the reported control sample.

At the follow-up request, the verified `full-loading-plus1000` endpoint was
continued for another 1000 native steady iterations with the same Coupled /
Global-Time-Step settings and the same 100-iteration solver batches. The run
started from the local Documents copy of the previous paired endpoint because
reopening the OneDrive copy directly stalled before solving; the final pair
was then written to OneDrive and hash-verified.

The second continuation completed through the +1000 checkpoint with expected
native coordinate 5580; the restarted Fluent transcript reached 5586. Its
terminal values were:

- total liquid mass: `295.8536 kg`;
- total liquid volume: `0.3357353 m^3`;
- lower-zone liquid mass: `0.0021686 kg`;
- command and absorber removal: `116.9200000000001 kg/s`;
- command error: `4.26e-14 kg/s`;
- terminal continuity residual: `2.7841e-3`;
- terminal phase-2 volume-fraction residual: `5.4762e-4`.

The second horizon again had no AMG, FPE, nonfinite, or fatal event. It logged
1000 reverse-flow messages and 1000 turbulent-viscosity-limit messages. The
continuation therefore strengthens the endurance observation, but not the
boundedness claim: the lower-zone inventory still oscillated, and the
reverse-flow/viscosity-limit pattern persisted.

Second-continuation evidence:

- [completion receipt](/Users/shuheiyokkaichi/Developer/P4P_knowledgeWiki/PyAnsys/output/phase71a_r0_control_run4/authoritative-completion-receipt.json)
- [analysis summary](/Users/shuheiyokkaichi/Developer/P4P_knowledgeWiki/PyAnsys/output/phase71a_r0_control_run4/analysis/summary.json)
- [stitched report histories](/Users/shuheiyokkaichi/Developer/P4P_knowledgeWiki/PyAnsys/output/phase71a_r0_control_run4/report-histories-batched.json)
- [control-window residual health](control-06-residual-health.png)

Second durable final pair:

- Case: `C:\Users\syok443\OneDrive - The University of Auckland\P4P-Fluent-Artifacts\Phase71A\FamilyR\finals\P71A-R0-SMOOTH-CONTROL-COUPLED-GLOBAL-TIME-PLUS1000\20260922T162500Z\P71A-R0-SMOOTH-CONTROL-COUPLED-GLOBAL-TIME-PLUS1000-full-loading-plus1000.cas.h5`
- Case SHA256: `4fd493972839929f1f0922ad42679456d1f4aea294da86e4b13d6b7c32f754fc`
- Data: `C:\Users\syok443\OneDrive - The University of Auckland\P4P-Fluent-Artifacts\Phase71A\FamilyR\finals\P71A-R0-SMOOTH-CONTROL-COUPLED-GLOBAL-TIME-PLUS1000\20260922T162500Z\P71A-R0-SMOOTH-CONTROL-COUPLED-GLOBAL-TIME-PLUS1000-full-loading-plus1000.dat.h5`
- Data SHA256: `b2261fac8626b2e338c3a9c80c334c8a910d1bfb536f782ef9234623f00e1a72`
