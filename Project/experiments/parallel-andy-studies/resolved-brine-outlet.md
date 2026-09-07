# Historical resolved brine-outlet diagnostics

## Scope and identity

Andy `07g`–`07n` explored carrier drainage on the resolved
`brine-outlet-620kcells.msh.h5` mesh: 620,431 cells, minimum orthogonal quality
0.250003, maximum aspect ratio 66.0258. The source records identify mesh
SHA-256 `0d75a86e53bc020aeefa4b13ef8616413a862b15646355d90d8037d1be888394`.
The nominal feeds were liquid 116.92 kg/s and vapour 80.69 kg/s; later
isolation/startup experiments used zero or very small fractions of those feeds.
The former numerical sink was absent. Geometry-derived pool elevations and
CFD-derived brine pressures were **Assumed/Inferred diagnostic inputs**, not
measured plant setpoints.

This lane is separate from the 231,376-cell F11-derived steady Mixture
`03A`/Phase-06 programme. Similar questions or shared server names do not
establish mesh, parent, model or operating-condition parity. No historical
endpoint below is promoted by this migration, and no active phase gate changes.

## Executed findings and corrections

| Historical record | Preserved observation and evidence limit |
|---|---|
| [07g dry-start Mixture](https://github.com/Shuhei-uni/P4P_knowledgeWiki/blob/archive/andy-local-20260908/Setup%20report/07g-split-inlet-resolved-brine-outlet-qualification.md) | Stopped at verified iteration 500; equal-pressure resolved outlets did not qualify a carrier baseline |
| [07h initial liquid pool](https://github.com/Shuhei-uni/P4P_knowledgeWiki/blob/archive/andy-local-20260908/Setup%20report/07h-split-inlet-resolved-brine-outlet-initial-liquid-pool.md) | Changed initialization only; numerical divergence, terminal verified block iteration 250 |
| [07i WFGC sensitivity](https://github.com/Shuhei-uni/P4P_knowledgeWiki/blob/archive/andy-local-20260908/Setup%20report/07i-split-inlet-resolved-brine-outlet-wfgc-sensitivity.md) | Valid 16-process test, not a 20-process mismatch: nodes n0–n15 proved the count. Continuity reached 6.9888e14 at raw iteration 20; iteration-21 SIGSEGV shut down Fluent. No complete 25-iteration block credited |
| [07j transient explicit VOF](https://github.com/Shuhei-uni/P4P_knowledgeWiki/blob/archive/andy-local-20260908/Setup%20report/07j-split-inlet-resolved-brine-outlet-transient-vof.md) | Equal-1.12-MPa bracket failed gross drainage at step 2 / 0.0002 s: brine liquid outflow 4692.8688 kg/s against 116.92 kg/s feed. Storage-aware closure error was only 0.4601% of feed; the large drainage was not merely a report sign error |
| [07k prescribed mass-flow outlet](https://github.com/Shuhei-uni/P4P_knowledgeWiki/blob/archive/andy-local-20260908/Setup%20report/07k-split-inlet-transient-vof-massflow-brine-outlet.md) | Terminal numerical failure; at step 3 steam-outlet pressure was −4.1102e13 Pa and outlet velocity 5.2599e6 m/s. The imposed discharge was a diagnostic boundary, not plant data |
| [07l hydrostatic rest](https://github.com/Shuhei-uni/P4P_knowledgeWiki/blob/archive/andy-local-20260908/Setup%20report/07l-split-inlet-hydrostatic-rest-isolation.md) | Zero inlets, closed brine face and relaxed pool stayed bounded for ten steps / 1e-5 s: inventory 3774.370486 kg, final continuity 3.470e-6. Accepted bounded isolation diagnostic only |
| [07m pressure opening/ramp](https://github.com/Shuhei-uni/P4P_knowledgeWiki/blob/archive/andy-local-20260908/Setup%20report/07m-split-inlet-zero-feed-pressure-opening-and-inlet-ramp.md) | Zero-feed opening bracket and 0.1% hold accepted for their windows; progressive ramp stopped at the 1% continuity gate. Later zero-step hold was stale and not resumed; 22 August correction superseded the older handoff recommendation |

The `07l` forensic audit corrected two earlier statements: six inherited DPM
injections had tracked 6,456 parcels in the `07j`/`07k` lineage despite
interaction being off, and Hybrid Initialization had supplied constant
pressure before the dense pool was patched. One-way parcels were not shown
to cause the carrier failure; disabling interaction alone did not prove
carrier-only execution. `07l` and the later `07n` controls required zero
injection objects, DPM off, EWF off and no mass/momentum source.

## 07n: clean low-feed drainage did not persist

The [07n source record](https://github.com/Shuhei-uni/P4P_knowledgeWiki/blob/archive/andy-local-20260908/Setup%20report/07n-resolved-brine-outlet-model-solver-screening.md)
contains the independent closed-pool reconstruction, timestep/solver screens,
matched parents and subsequent drainage tests. The reconstructed pool used
98,473 cells; it must not be conflated with the earlier `07l` patch. The
closed-pool timestep comparisons did not establish timestep independence,
despite bounded fields and improved inner continuity. A field-matching solver
comparison also did not establish a physically validated formulation.

**Observed in the source, 25 August 2026:** independent cold loads of the clean
server-2 step-90 pair used explicit VOF/PISO, dt 1.28e-4 s and 100 inner
iterations. At 0.05% feed (liquid 0.05846 kg/s, vapour 0.040345 kg/s) and
brine pressure 1,122,263.621237 Pa, ten steps closed phase/total balance,
with total imbalance −9.11e-8 kg/s. The brine face remained liquid VF 1.0
with no cross-phase leakage. This was a short-window drainage diagnostic;
neither plant pressure nor a production parent was established.

**Later limiting evidence, 26–28 August:**

- The same fixed pressure failed on a longer hold: at 36 credited steps,
  liquid imbalance was −0.050185643 kg/s despite low continuity and intact
  liquid coverage. The interrupted following step was uncredited.
- Independent pressure-feedback gains 0.25 and 0.05 did not meet the sustained
  balance gate; all endpoints remained `eligible_parent:false`.
- A separate 70-step hold applied one +23.218830875 Pa pressure action after
  step 10, with every other feed/timestep/model/source setting fixed. Final
  continuity was 7.93757e-4, Courant 0.00764008, brine liquid VF 1.0 and
  cross-phase leakage zero. Nevertheless, final-ten maximum absolute liquid
  and total imbalances were 0.01155471 and 0.011478693 kg/s, both exceeding
  the required 0.005 kg/s limit. Reported inventory stayed 3877.468071 kg;
  that unchanged reported value does not override the failing flux gate.

The `longhold_nonacceptance_disposition_20260828.json` correction in the
source controls stale nested `accepted ... zero-feed` wording. The step-70
and intermediate checkpoints are **diagnostic/unresolved**, ineligible as
parents, and not authorized for resumption or an unchanged repeat. Source
proposals for later controller actions are historical proposals, not actions
authorized by this repository unification.

## Scientific conclusion and remaining uncertainty

The source supports bounded hydrostatic rest and clean resolved drainage over
very short, very low-feed windows. Low residuals, an intact liquid seal and
zero wrong-phase outlet flux did not guarantee sustained liquid balance.
Operating-flow capability, meaningful level resolution, timestep independence,
plant submergence, level target and downstream valve/pressure relation remain
unresolved. The 07n pressure intervention was a mass-flow-balance experiment;
it did not demonstrate water-level control or physical separator validation.

Detailed run IDs, failures, later corrections and evidence paths are retained
in the recovery [experiment notes](https://github.com/Shuhei-uni/P4P_knowledgeWiki/blob/archive/andy-local-20260908/ResearchProject_wiki/wiki/progress/experiments.md)
and [validation notes](https://github.com/Shuhei-uni/P4P_knowledgeWiki/blob/archive/andy-local-20260908/ResearchProject_wiki/wiki/model/validation.md).
Those notes report historical machine/session states; this migration did not
contact Fluent or establish present-day session state.
