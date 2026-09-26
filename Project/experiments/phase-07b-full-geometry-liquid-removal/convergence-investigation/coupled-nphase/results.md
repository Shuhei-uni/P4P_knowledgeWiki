# G6 — all-phase equations did not restore conservation

E6 completed N5000 with the declared N-phase-only delta and exact original N0 physical/geometry parity. It reduced several displayed residuals and liquid carryover compared with E5, but it did not establish credible steady convergence. All three mean-absolute closure indicators and inventory stationarity fail. All required recording and native spatial QA are complete; no qualification or unchanged extension is selected.

## Controlled comparison

E5 and E6 start from the same clean parent and SIMPLE Hybrid physical fields. Only Solve N-Phase Volume Fraction Equations changes; CFL20, Coupled, pseudo time Off, segregated VF, relaxation, full feed, tau0.02s, geometry, materials, source law and update interval remain fixed. E6's instrumentation repair and N50 continuation changed no physics, controls or fields.

Late statistics use N4501–5000; inventory compares means N4001–4500 and N4501–5000.

| Indicator | E5 | E6 |
| --- | ---: | ---: |
| Mean absolute liquid closure (% liquid feed) | 148.115 | 144.369 |
| Mean absolute vapor closure (% vapor feed) | 2.132 | 1.520 |
| Signed mean vapor closure (% vapor feed) | 2.060 | 1.418 |
| Mean absolute native-mixture closure (% total feed) | 86.795 | 84.841 |
| Inventory mean change (%) | 19.333 | 18.451 |
| Continuity maximum | 2.5817 | 1.3259 |
| Mean liquid carryover (% liquid feed) | 11.493 | 8.346 |
| Mean vapor outlet/feed (%) | 97.940 | 98.582 |
| Mean native applied removal (kg/s) | 276.661 | 275.962 |
| Mean liquid inventory (m³) | 0.516966 | 0.475630 |
| Late inventory slope (m³/iteration) | 0.000106865 | 0.000194819 |

The liquid inlet is116.921kg/s. E6's sink removes275.962kg/s on average while liquid also exits the steam outlet; the source-inclusive liquid deficit is168.798kg/s. Native mixture deficit is167.655kg/s. Removal is counted once, using the native applied source; signed vapor averages are shown separately from mean absolute values to expose cancellation. Inventory is not stationary, and the higher late E6 slope cautions against calling its smaller window-mean change a resolved drift improvement. Iterations are numerical, not physical time.

![Raw closure and inventory](../../../../../PyAnsys/output/phase07b-g6/E6-F1-closure-inventory.png)

The histories show persistent over-removal and growing inventory in both algorithms; the N-phase switch leaves their broad behavior similar. No time averaging of a nonconservative solution is accepted as a steady separation prediction.

![All residuals and speed](../../../../../PyAnsys/output/phase07b-g6/E6-F2-residual-speed.png)

E6 late maxima: continuity1.3259; x/y/z momentum0.00010281/0.000080592/0.00011706; k0.0095616; epsilon0.023795; primaryVF0.00018085; secondaryVF0.012148. Only momentum and primaryVF remain below1e-3 throughout the late window. The primary curve has no E5 counterpart. Residual settings match, but the changed equation system limits interpretation of relative residual magnitudes.

## Recording, extrema and fraction semantics

The terminal file-only audit verifies5000 scalar/exact-face/speed/all-eight-residual samples,4999 consecutive source-lag pairs with zero error, native checkpoint flux parity, and all16 required/supplemental whole-cell snapshots. All initial/final horizontal and full-height axial arrays are finite and retained. The recovered N50 prefix and N55 normalization check are included. Final case/data are preserved; controller and job exited successfully. No numerical fatal marker or monitor error occurred.

Both E5/E6 remain below500m/s; maximum283.091m/s occurs during early startup. E6 late maximum82.285m/s versus E5 154.960m/s. E6 sampled N5000 maximum76.322m/s is at(-0.11449,6.26576,-0.26772)m in the main zone, near the upper outlet elevation, not the original SIMPLE extreme-event inlet locus. Snapshots localize sampled states, not every unsaved local event. Turbulent-viscosity limiting appears4825 times (maximum2810cells) in E6 versus4824 (4734cells) in E5; both transcripts contain4998 reversed-flow messages. Message counts are solver diagnostics, not unique spatial incidents.

For E6, raw secondarySV_VOF is not interchangeable with native reported liquid fraction. At N5000 raw integrated liquid volume is0.521586867m³; cellwise alpha2/(alpha1+alpha2) reconstructs native0.498911371m³ within2.97e-11m³. Raw phase sums span0.855596–1.239729 in the main zone and0.953802–1.206692 in the collector. Both raw phases, raw inventory and phase-sum defects remain immutable evidence. Native-normalized parity passes at every snapshot using the original monitor tolerance. This repairs inventory measurement; normalization is not conservation. Generic internal-storage timing remains unverified, and rawSV_MASS_IMBALANCE is uncalibrated. See [recovery semantics](recovery.md).

## Native spatial comparison

Six native Fluent exports use shared0–1 liquid fraction and0–80m/s speed ranges, identical cameras, the inlet-height y=2.427283m cut and full-height x=0 cut. E6 shows a stronger liquid band along the inner curved feature at inlet height, and a slower displayed speed field there, than E5. Both axial cuts show liquid concentrated close to walls with a predominantly vapor interior on this scale. These are finite, nonconservative states: they do not establish physical film thickness, steady separation efficiency, or causality.

![E6 inlet-height liquid](../../../../../PyAnsys/output/phase07b-g6/native-20260924T0524/NPHASE-N5000-hot-liquid.png)
![E5 inlet-height liquid](../../../../../PyAnsys/output/phase07b-g6/native-20260924T0524/CFL20-N5000-hot-liquid.png)

[All six images and provenance](../../../../../PyAnsys/output/phase07b-g6/native-graphics-manifest.json) include plane, camera, observed/displayed ranges, remote/local hashes and visual QA. Native phase-2-vof is the reported normalized quantity in E6; the raw phase-vector defects above remain separate. E6 final was restored and verified after exports; no extra iterations or source-pair overwrites occurred. [Completion audit](../../../../../PyAnsys/output/phase07b-g6/completion-audit.json).

## Interpretation and decision boundary

The hypothesis that all-phase equations alone would restore acceptable conservation is unsupported at the declared horizon. The control contrast supports sensitivity of displayed residuals and finite phase routing to phase-equation treatment. Persistent sink/feed mismatch despite exact lag and recording keeps source stiffness/coupling prominent; startup/developed-field history and discretization remain alternatives. Global steady nonexistence, physical instability and a unique cause have not been established. Original SIMPLE/G3 provide supporting algorithm-sensitive spike evidence, not a matched N-phase control.

The existing sink law and its source Jacobian remain distinct questions: the source report is verified, but an implicit-expression derivative has not been established. A native-normalized fraction field and a low primary residual cannot certify either mass closure or the liquid source's coupling.

Next selected action: [E7 tau0.10 under unchanged Coupled/N-phase](../coupled-nphase-weaker-sink/setup.md), from the original fresh parent. The narrower source coefficient contrast precedes broader pseudo-time or startup changes. No E6 continuation or qualification is selected.

Machine evidence: [comparison](../../../../../PyAnsys/output/phase07b-g6/comparison.json), [diagnostics and snapshot fractions](../../../../../PyAnsys/output/phase07b-g6/diagnostic-comparison.json), [terminal audit](../../../../../PyAnsys/output/phase07b-convergence-investigation/e6/resume-n50/terminal-audit.json), and [run paths](run-paths.md).

# E6 preparation and recovery history

The selected N-phase experiment remains scientifically untested. The live Boolean-only method/control change passed, and Fluent exposed both vf-phase-1 and vf-phase-2 alongside the six other equations. The original clean parent and identical SIMPLE Hybrid route were used. Prepared case/data writes and existence checks completed.

During prepared pair reopen, the case loaded but parallel result-data loading emitted multi-rank SIGSEGV and BAD TERMINATION. The connection reset. No scientific iteration was issued; no N50 or initial parity claim is made. This is a preparation/persistence failure, not evidence that the numerical treatment diverges. The prepared pair is excluded as a verified restart parent.

E5 final was preserved and an additional predecessor pair saved before replacement. [Machine disposition](../../../../../PyAnsys/output/p7b-s40-t020-coupled-cfl20-nphase-20260923T024536Z/pre-solve-disposition.json) retains paths and raw transcript. The detached worker exited and the controller lock is free. A bounded API reconciliation found the configured endpoint unreachable. No Fluent termination command was issued.

Recovery requires a reachable Andy server-1 Fluent API session; the permitted API-only PC route cannot restart a dead service. Do not use Shuhei's sessions or blindly retry the prepared data read. Preserve E5 and all failed evidence; inspect the proposed recovery ordering before a unique retry, retaining exact N0 physical/geometry parity and all save/reopen requirements.

## Restored access

On 24 September NZ, the updated Andy endpoint at10.104.145.174:63093 responded as a blank Fluent2025R2 session. Both E5 and clean N0 pairs existed. E5 final was restored successfully and verified atN5000 with water volume0.5772637064115669m³ and exact saved methods/controls; zero solve iterations. [Restoration receipt](../../../../../PyAnsys/output/phase07b-convergence-investigation/e6/recovery/20260923T222739Z/restore-e5.json). The [predeclared recovery](recovery.md) is being implemented before a unique retry. The failed initial attempt remains immutable.

The first restored-session retry stopped at exact setup comparison because session-level auto_compile_compiled_functions was true, whereas the original reference requires false. No Hybrid/treatment/solve occurred. This preference is restored explicitly for recovery; strict full setup comparison remains enabled. Evidence: `PyAnsys/output/phase07b-convergence-investigation/e6/retry1/`.

Retry2 also stopped before solve: the immediate post-Hybrid counter was1, failing the new pre-save guard. Native physical arrays exactly matched the original reference after bijective cell-coordinate mapping; geometry differed only by roundoff. A separate zero-solve initialized SIMPLE+Nphase pair successfully reopened, returning counter0 and **exact ordered original geometry and physical fields**. Unchanged methods/controls and zero water were separately verified. This supports the initialization-order recovery at its source-free persistence stage only; the final Coupled/source pair and N50 remain unproved. The original probe's failed expected-counter1 assertion is preserved alongside the successful readback reconciliation. See [recovery](recovery.md) and machine evidence `PyAnsys/output/phase07b-convergence-investigation/e6/retry2/`.

Retry4 (`p7b-s40-t020-coupled-cfl20-nphase-20260923T225918Z`) passed both checkpoint reopens, source/method/control readback and exact ordered original N0 physical/geometry checks, then began solving. All eight residual monitors are enabled. This establishes recovered implementation through solve start; numerical adequacy and terminal G6 remain pending. Retry3 had stopped at its30second connection deadline before setup; read-only E5 reconciliation preceded retry4 with90second connection allowance. Live progress and N50 proof belong to phase-state.

The N50 diagnostic failure was resolved without changing or reloading the solver state: cellwise-normalized raw phase fractions reproduce native inventory; both raw phase arrays and their sum defects are retained. Full N50 evidence was recovered, then continuation `p7b-s40-t020-coupled-cfl20-nphase-resume-20260923T231816Z` passed the extraN55 snapshot, all8residual/scalar/flux histories, source-lag audit54pairs(error0), and pairedN55 checkpoint. The file-only live audit passed and one controller continues to the unchanged absolute5000 cap. Neither this recovery nor the native reporting normalization is numerical qualification; G6 remains pending. Details and documentation limits are in recovery.md.


## G6 regional liquid-budget diagnostic

The N4501–5000 liquid deficit is predominantly in the above-collector region under the recorded discrete-flux convention. This is an offline decomposition of the same E5/E6 evidence, not a new simulation or a causal attribution. With interface flux positive outward from the collector, the collector budget is `-net_outward - applied_removal`, and the above-collector budget is `external_net_liquid_inflow + net_outward`. The liquid source is assigned only inside the collector; the external brine-wall liquid flux is zero.

| Regional budget (kg/s) | E5 signed mean | E5 mean absolute | E6 signed mean | E6 mean absolute |
| --- | ---: | ---: | ---: | ---: |
| Collector | -1.409 | 35.110 | -6.136 | 21.014 |
| Above collector | -171.768 | 171.768 | -162.662 | 162.662 |
| Whole vessel | -173.178 | 173.178 | -168.798 | 168.798 |

Negative values denote a deficit in the steady algebraic budget. The collector's smaller signed mean conceals substantial cancellation: E6 instantaneous collector budgets span -73.155 to +37.468 kg/s, while the above-collector budget is negative at every late-window iteration. E6 mean interface delivery/escape are316.007/46.182 kg/s; their net269.826 kg/s entering the collector nearly matches the275.962 kg/s sink in the signed mean, but greatly exceeds107.164 kg/s net external liquid inflow.

The regional budgets sum to the independently reported whole-liquid budget within floating-point roundoff at all5000 aligned iterations; delivery minus escape also reproduces the inward interface flux. This verifies bookkeeping and preserves the existing interface orientation/native-flux proofs. It does **not** demonstrate local conservation, physical accumulation or an internal cellwise residual calibration. The E6 raw-versus-normalized phase-fraction limitation remains: native normalization does not repair conservation, and these budgets use recorded discrete face flux and applied source directly, not flux reconstructed from normalized fields.

Consequently, E7 remains a controlled source-coefficient sensitivity test. A localized collector-sink stiffness mechanism alone is not established by G6; source feedback into upstream transport, phase-equation coupling and discretization remain possible explanations. [Derived regional evidence, input hashes, per-iteration late samples and validation](../../../../../PyAnsys/output/phase07b-g6/regional-budget.json).
