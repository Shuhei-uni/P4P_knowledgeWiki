# Drainage-boundary verification results

**All four terminal analytical checks passed, but the campaign is not an accepted guarded verification.** Startup exceeded the declared 20 m/s stop threshold and the controller checked speed only after each 500-iteration batch. This implementation defect is material; the initial “all passed” statement was corrected after full-history review. This establishes the forward-flow outlet-vent loss relation for a steady, single-liquid, frictionless straight-duct benchmark. It does not establish a conservative separator solution, hydrostatic-profile/VOF implementation, reverse-flow response, a liquid seal, or the real drain resistance.

| Synthetic loss K | Driving total-to-ambient pressure (Pa) | Predicted speed (m/s) | Fluent speed (m/s) | Mass flow (kg/s) |
|---:|---:|---:|---:|---:|
| 0 | 200 | 0.673523 | 0.673523 | 148.473062 |
| 0 | 800 | 1.347046 | 1.347046 | 296.946123 |
| 9 | 200 | 0.212987 | 0.212987 | 46.951305 |
| 9 | 800 | 0.425973 | 0.425973 | 93.902609 |

The reference is U=sqrt(2Δp/[ρ(1+K)]), using inlet total pressure and external static pressure, not two static-pressure boundaries. Symmetry sides remove wall shear; the uniform straight duct contributes no frictional loss. The internal static pressure for K=9 is 180/720 Pa respectively, consistent with KρU²/2. Geometry is 1×0.5×0.5 m with 320 regular hexahedra and independently checked positive total volume 0.25 m³. Liquid density is 881.77 kg/m³ and viscosity 145.96e−6 Pa s; gravity off, laminar, SIMPLE, second-order pressure/momentum, pseudo-time off. This is an intentionally simple analytical verification, not evidence of comparable accuracy in complex flow.

All cases were freshly initialized, saved/reopened with exact critical-setup matching, and ran 500 iterations. Final case/data pairs and all 500 native report/residual rows are preserved. Final100 maximum relative mass imbalance was below 3.1e−14%, all four active residuals below 6.2e−18, and flow/pressure variation below 3.1e−14%. Prediction agreement is at floating-point roundoff; the declared tolerance was 2%. Quadrupling pressure doubled flow, and resistance reduced flow by sqrt(10). The numerical precision of this uniform test is not a physical error estimate.

![Raw benchmark histories](../../../PyAnsys/output/drainage-benchmark/verification.png)

Raw histories are shown without smoothing; horizontal reference lines are analytical speeds. Residual line styles distinguish cases while retaining the requested continuity colour.

**Implementation recovery:** an initial inspection attempted to read inactive standard-initialization defaults while Hybrid was selected. Standard initialization was selected before any solve. Zero iterations were lost or retried. Mesh-loading and configuration receipts are retained; no benchmark inherited separator solution fields.

**Budget:** exactly 2000 solved iterations, the declared cap, across four cases. The campaign and restoration finished within the two-hour limit; no extra qualification or separator iterations were issued. See machine state and timestamped receipts for elapsed time.

**Decision:** retain terminal agreement as diagnostic evidence only; do not promote the campaign to a clean pass or launch the full separator. The per-iteration speed/nonfinite/deadline guard is now repaired and its decision logic checked offline; actual callback interruption still requires a fresh run. Maximum startup speeds were 2827.6, 11310.5, 6294.4 and 25177.7 m/s, respectively. The pressure-driven zero-velocity initialization produced large numerical overshoots before convergence. This is consistent with a startup defect, not a physical flow prediction. A repeat should use a declared modest nonzero initial velocity (for example 0.1 m/s, independent of each exact answer) and the corrected guard, with unchanged physical controls. It needs a separately agreed additional iteration allowance because the original 2000-iteration ceiling is exhausted. The next candidate is a fresh, full-geometry steady VOF contrast with one fixed idealized resistance, retaining all conservation/inventory/routing/residual/spatial/two-start/persistence requirements. The [concrete proposal](../../drainage-boundary-next-phase-proposal.md#concrete-full-geometry-follow-on-for-discussion-not-launched) defines K=9 as an assumption and a separate bounded campaign. No physical cause of Phase 9's failure has been identified by this test, and its endpoints remain unqualified. Actual downstream head/valve characteristics remain unknown.

[Machine audit and source hashes](../../../PyAnsys/output/drainage-benchmark/analysis.json) · [Campaign and saved checkpoint paths](../../../PyAnsys/output/drainage-benchmark/campaign.json) · [Restored separator receipt](../../../PyAnsys/output/drainage-benchmark/restored-separator.json)

The preserved separator N2000 pair was restored and verified idle after the benchmark. Campaign start through restored-state verification elapsed 0.074 hours (including I/O and idle overhead, not CPU-hours).

## Approved corrected repeat: connection block

Andy authorized another 2000-iteration/two-hour repeat. Unique repeat output paths, a 0.1 m/s initial velocity, per-iteration guard evidence, a deliberate first-iteration interrupt proof and partial-endpoint preservation are prepared. Two TCP preflights to the owned server1 endpoint timed out before any Fluent mutation; zero repeat iterations issued. The saved N2000 separator remains the last verified checkpoint, but current live state is unknown. Reconcile the endpoint on reconnection; do not use another owner’s session. Existing repeat authority remains valid; set a fresh two-hour execution guard when starting after this external block.

## Historical user pause

The user requested a pause before disconnecting. The corrected repeat completed both K=0 controls at N500 each, then stopped the K=9, 200 Pa control at native N460. Owned server1 was verified idle at 2026-09-30T02:08:12.619204+00:00. The paused native case/data pair and report/transcript histories are preserved in the [pause receipt](../../../PyAnsys/output/drainage-benchmark-repeat1/user-pause-receipt.json). The controller and completion watcher are no longer running and the server1 lock is free. No separator restoration or automatic restart will occur.

Repeat spend is 1460 iterations; combined with the original 2000, total diagnostic spend is 3460/4000. The third control is incomplete by user instruction, not a failed physical test; the fourth has not started. During stopping, the original controller reported a socket-stream error and recovered the idle N460 checkpoint. Independent readback subsequently confirmed N460 and the saved pair. Terminal campaign analysis and guard qualification remain pending; no full-separator conclusion is established. Explicit human resume is required.

## Authorized resume after returning home

Andy explicitly resumed the solver. The saved third-control N460 pair was reopened and its critical settings matched the original snapshot before solving. Continue only N461–500 and the final fresh 500-iteration control. Paused report/transcript sources are preserved separately; continuation histories are combined for the final100 audit. The two-hour allowance retains the prior 1945.35 seconds of elapsed runtime; the human pause is excluded, leaving at most 5254.65 seconds at resume preparation. The first launcher failed before Fluent connection because its resolved interpreter bypassed the virtual environment; the corrected r2 launcher issued no retry iterations. Native callbacks now prove progression beyond N460. Scheduled monitoring uses GPT-6.1 Sol high. The total 4000-iteration cap and no-separator-solve boundary remain unchanged.

## Corrected repeat terminal review

**Verified observations:** all four controls completed N500, exactly 2000 repeat iterations and 4000 combined diagnostic iterations. Terminal analysis and per-iteration guard audits pass; each final100 report and residual window has exactly 100 records without conflicting indices, including the stitched N460 continuation. Paused source histories remain preserved. All four final case/data pairs exist. Independent monitoring verified server1 idle with the preserved separator at N2000, original separator contract intact, controller/worker absent and lock free. Monitoring is paused. See [analysis](../../../PyAnsys/output/drainage-benchmark-repeat1/analysis.json), [guard audit](../../../PyAnsys/output/drainage-benchmark-repeat1/guard-audit.json), [history recheck](../../../PyAnsys/output/drainage-benchmark-repeat1/terminal-history-recheck.json), and [live reconciliation](../../../PyAnsys/output/drainage-benchmark-repeat1/monitoring-terminal-reconciliation.json).

**Interpretation:** the fixed outlet-vent resistance implements the expected conservative pressure-to-flow relation in this single-liquid slip duct. The corrected startup satisfies its guard contract; the original guard-defective campaign remains separately classified.

**Claim limits and next decision:** this does not verify multiphase head response, actual valve characteristics, separator conservation or steady drainage. The restored Phase 9 endpoint remains unqualified. The next candidate is the already-drafted full-geometry steady VOF resistance contrast; its scope must be agreed before any separator calculations. No extra solve is selected.
