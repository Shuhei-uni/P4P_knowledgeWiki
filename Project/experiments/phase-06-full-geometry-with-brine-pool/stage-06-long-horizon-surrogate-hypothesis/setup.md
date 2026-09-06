# Phase 06 / Stage 06 — long-horizon surrogate hypothesis

## Status and phase-loop audit

**Selected by the human for completion of the Phase-06 scientific loop; not yet run.**

Phase 6 contains the short discovery evidence required by the loop: the
fixed-pressure/reference and `K=10` outlet-vent screens (`P6-S1-R/O`) and the
five-chunk numerical-surrogate discovery (`P6-S3-C`). Stage 4 is a focused
hypothesis test, but it stopped after 1,000 iterations while the controller had
hit its lower pressure bound and the lower-region proxy still rose. Phase-05's
transient Stage-05 record is setup-only; it is not treated as Phase-06 run
evidence.

**Stage question.** Once the stronger bounded pressure-feedback surrogate has
saturated at its lowest allowed pressure, does a substantially longer run show
the lower-region proxy and phase balance settling, or continuing accumulation?

This tests the Stage-04 short-horizon interpretation. It cannot supply a real
pool-level measurement or validate plant level-control behaviour.

## Hypothesis and discriminating observations

**H6.** The Stage-04 reduction in proxy slope was a long transient toward a
bounded numerical-surrogate state, rather than persistent accumulation after
the pressure actuator saturates.

| Long-run observation | Consequence |
|---|---|
| The proxy is bounded around the assumed 200 kg target, the late liquid net rate/imbalance become small and stable, and residual histories are credible | Supports H6 for this numerical surrogate only; it does not validate a physical separator controller. |
| The proxy remains above target with a sustained positive late slope and/or material positive net liquid rate | Weakens H6: the declared bounded surrogate does not establish even a numerical controlled state in this F11 steady Mixture/RNG bracket. |
| Fluent fails, required histories are absent, or final case/data cannot be verified | No physics conclusion; return to the execution boundary. |

## Collision check and experiment choice

| Candidate | Closest prior work | Exact delta | Novelty | Decision |
|---|---|---|---|---|
| `P6-S6-H` long surrogate test | `P6-S4-C`: same outer control law for 1,000 iterations; `P6-S3-C`: lower-gain 500-iteration discovery | 100 × 100 iterations from F11, 10,000-point PyFluent residual capture, final-pair verification, and 5,000-iteration recovery checkpoint | `PARTIAL REPEAT` | Selected: Stage-04 leaves the post-saturation long-time behaviour unresolved. |
| Generic resistance/fixed-pressure sweep | `P6-S1-R/O`, Phase-05 pressure work | Another arbitrary outlet parameter | `REDUNDANT` | Rejected. |
| Phase-specific mass-flow outlet | Phase-05 `02e` MF pilots; deferred `P6-S1-B` | Different outlet architecture but failed historical family and all-outward flow remains unproven | `PARTIAL REPEAT`, prerequisite failed | Deferred. |
| Transient/VOF or literal controller | Phase-02 VOF and Phase-05 transient work | Different time/model/control architecture | `NEW` in this exact question | Outside current Phase-06 boundary without explicit human scope selection and physical control data. |

### Question-experiment assessment

| Criterion (0–4) | Score | Rationale |
|---|---:|---|
| Scientific value | 3 | Resolves the material short-horizon ambiguity in the Stage-04 surrogate conclusion. |
| Evidence and interpretability | 3 | Exact F11 parent, fixed controller, file-backed phase histories, iteration checks, residual capture, and a late-window comparison limit confounders. |
| Cost-effectiveness | 3 | One focused run is more informative than a new arbitrary parameter matrix. |

## Assumptions and limits

| State | Item |
|---|---|
| **Assumed numerical proxy** | `y≤0.10 m` phase-2 liquid mass is only a controller input, not a measured pool elevation. |
| **Assumed numerical target** | `200 kg` remains a deliberately non-plant target from Stages 03–04. |
| **Assumed surrogate actuator** | Bounded `brineoutlet` pressure updates stand in for unknown valve/line/controller behaviour. |
| **Materially challenged** | A fixed pressure outlet represents a real level-controlled brine discharge. |
| **Questioned** | The steady Mixture/RNG model and retained output path can yield a numerically credible controlled state. |
| **Missing Info** | Plant level datum/setpoint/band, outlet hardware/line curve, downstream condition, and controller behaviour. |

## Server-neutral setup contract

| Field | Value |
|---|---|
| Setup ID | `P6-S6-H` |
| Mode | hypothesis test |
| Parent | Canonical Phase-05 F11 paired full-geometry steady Mixture/RNG case/data artifact |
| Controlled change | Only the Stage-04 outer pressure-feedback surrogate; report-path redirection, residual retention, and checkpoints are execution evidence rather than science deltas. |
| Starting pressure | `1.120 MPa` gauge |
| Controlled proxy / target | phase-2 liquid mass in `codex_y010_pool_below_y_0p10m` / `200 kg` |
| Feedback law | After each 100-iteration chunk: `p_next = clamp(p - clamp(2,000 Pa/kg × (proxy − 200 kg), ±5,000 Pa), 1.115–1.1375 MPa)`. |
| Horizon | 100 chunks × 100 steady iterations = **10,000 incremental iterations** |
| Frozen context | F11 geometry, steady pressure-based Mixture/RNG, gravity, inlets, steam outlet, phase definitions, and inherited report definitions |
| Recovery | Save a paired checkpoint every 5,000 iterations and retain the final case/data pair. |

### Execution amendment before the clean successor attempt

The first report-coordinate-corrected attempt completed its 50-iteration
smoke (the native report coordinate advanced to 15,050) but its immediately
following single 100-iteration PyFluent RPC did not return while the server
subsequently reported quiescent. The scientific setup, the 100-iteration
feedback cadence, target, pressure bounds, and total horizon are unchanged.
The clean successor therefore executes each 100-iteration control interval as
**two verified 50-iteration PyFluent calls**, checks the native report
coordinate after each call, and then applies the same one pressure update.
This is an execution-reliability correction only, not a new discovery
condition or an additional controller degree of freedom.

Implementation must prove the remote session is quiescent, the exact parent
pair exists and reads as steady Mixture/RNG with a pressure `brineoutlet`, and
all unique report-file paths are redirected before the smoke run. The child
must be save/reload verified. A zero Python return code alone is not completion
proof. The native coordinates in the redirected report histories are the
authoritative progress coordinate; the inherited Fluent RP iteration value is
not used as a solve-progress check because it remained fixed at `1556` in the
Stage-01 reference despite observed report progress.

## Core figure plan

| Figure | Question and plot | Data / interpretation use |
|---|---|---|
| F1 — numerical-pool proxy | Raw `y≤0.10 m` phase-2 mass and the 200 kg target versus native iteration; pressure steps in an aligned panel; report final-1,000-iteration slope/range | Inherited report plus controller manifest. Persistent positive slope weakens H6. |
| F2 — phase liquid balance | Phase-2 inlet, brine, steam-outlet, and derived `inlet − brine − steam` rate [kg/s] versus iteration, with Fluent signs stated | File-backed phase reports. A local proxy plateau with material net accumulation cannot count as control. |
| F3 — storage and closure | `y≤0.10 m`, `y≤0.30 m`, total phase-2 mass, full imbalance, and relative imbalance histories | Inherited inventory/imbalance reports. Tests whether apparent local response hides global storage. |
| F4 — numerical adequacy | Per-equation scaled residual histories on logarithmic y-axis over the full horizon | PyFluent monitor capture from the owning connection. It bounds, but does not replace, the physical inference. |

## Fleet and bold-probe lane result

The 2026-08-31 preflight found `server-2@10.104.145.174` and
`server-3@10.104.145.176` reachable, quiescent, Fluent 2025 R2-capable, and
able to see the F11 pair. Server 2's first two attempts supplied no hypothesis
evidence; its third completed the smoke but stalled in the first 100-iteration
call. Server 3 was then found actively owned by another solve at the direct
Fluent state gate, so the clean mainline successor returns to a newly proven
quiescent server 2 with the execution amendment above. Bold-probe research
reviewed the local Purnanto scope, Phase-02 VOF, Phase-05 transient work, and
the failed mass-flow-outlet family. No bold case is runnable within this Phase-6
boundary: transient/VOF/controller work changes scope, while another
mass-flow/pressure/resistance trial is prerequisite-blocked or redundant.

The runtime placement and final paths are in [run-paths.yaml](run-paths.yaml);
results belong in [results.md](results.md).
