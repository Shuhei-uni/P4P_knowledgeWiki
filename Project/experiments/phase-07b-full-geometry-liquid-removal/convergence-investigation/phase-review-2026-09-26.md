# Phase decision review — 26 September 2026

**Recommendation:** finish a small, explicitly bounded numerical investigation
inside Phase 7b, then close that route if it still fails. Do not continue broad
collector/Courant/relaxation sweeps, and do not adopt the new EWF endpoint as a
converged parent. The next substantive model question is conservative wall-film
collection and drainage; Shuhei's existing Phase 7.2A already owns that question
on the simplified geometry. A full-geometry film branch would require a new
human-framed phase, including an explicit decision about film time dependence.

This is a requested planning review, **not a new execution contract or a change
to the physical scope**. No Fluent connection, solve, reload, source change or
automation restart was issued. E7 remains the sole selected unfinished case;
its live iteration is unknown under the recorded external connectivity block.
Neither that block nor a passed recording audit is a numerical outcome.

## What was reviewed

Repository HEAD is `5b4e55c` (our investigation and diagnostic tooling). The new
Shuhei work is `587a68a`, compared with `b19b8e5`: E2.7's additional 5,000
iterations, five exported histories, figures, manifest, setup and export/run
scripts. Its roughness update adds figure interpretation, not another roughness
campaign. Those Phase 7.2A files are unchanged between `587a68a` and HEAD.

The review used the current phase contracts, G1–G6 results, E7 partial evidence,
the regional flux audit, the previous Shuhei audit, the new CSV and its generating
scripts, and focused primary-literature/Fluent v252 lookups. The E6 budget and
E2.7 continuation figures were visually inspected. Their visible trends agree
with the numerical checks below.

[Reproducible offline audit](../../../../PyAnsys/scripts/analysis/audit_phase07b_phase_review.py)
and [machine results](../../../../PyAnsys/output/phase07b-review-20260926/audit.json)
recompute four full-geometry terminal histories and the five EWF CSV series,
retain input hashes, and distinguish missing native evidence. The linked
machine output is local/Git-ignored; this review retains the decision-relevant
numbers in the shared Project record.

## What our work has established

G1 tested five collector extents. Four reached N5000 without satisfying the
declared numerical conditions; S100 failed numerically at attempted N4183.
G2 tested two weaker coefficients under SIMPLE and did not restore balance.
G3 exactly reproduced the original T020 history and located sampled extreme
speeds near the inlet's upper elevation, well above the collector. These are
useful exclusions and diagnostics, even though no case qualified.

The subsequent controlled sequence shows diminishing returns:

| Full-geometry treatment, tau 0.02 s | Liquid error % | Vapor error % | Native mixture error % | Inventory change % | Maximum continuity residual |
| --- | ---: | ---: | ---: | ---: | ---: |
| SIMPLE reference | 354.843 | 3.329 | 208.591 | 18.370 | 1.2497 |
| E4: Coupled, pseudo Off, CFL200 | 263.677 | 5.223 | 155.961 | 11.526 | 2.3959 |
| E5: CFL20 | 148.115 | 2.132 | 86.795 | 19.333 | 2.5817 |
| E6: solve all phase fractions | 144.369 | 1.520 | 84.841 | 18.451 | 1.3259 |

Errors are **mean absolute source-inclusive closure**, divided by each measured
phase/native-mixture feed, on N4501–5000. Inventory compares means N4001–4500
and N4501–5000, divided by the larger mean. Discovery limits remain 1% for each
budget and inventory metric, with all active residuals below 1e-3 throughout
the late window. None passes. Residual scaling/equation-system limitations
remain in the individual results; the budget comparison does not rely on
equal residual scales.

Coupled eliminated all recorded speeds at or above 500 m/s. That is real
numerical improvement, but it did not make the solution conservative. E6's
mean removal is 275.962 kg/s against 116.921 kg/s liquid feed, while liquid
inventory continues growing. Its mean liquid carryover is 8.35% of feed and
vapor outlet recovery is 98.58%; these are observations of an unqualified
field, not separator-performance predictions. Only momentum and primary-VF
residuals pass the late threshold. Vapor signed error (1.418%) and mean absolute
error (1.520%) are both retained; cancellation does not rescue the failed
liquid or mixture budgets. See [G6](coupled-nphase/results.md).

The independent regional ledger is especially informative. E6's late mean
liquid error is -168.798 kg/s: -162.662 kg/s above the collector and -6.136 kg/s
inside it. The collector's mean absolute error is still 21.014 kg/s, so its
smaller signed error partly cancels. The two regional ledgers reconstruct the
whole-domain ledger to roundoff. Most deficit is above the collector; this
does **not** localize the cause solely to a stiff sink. Upstream source feedback,
phase transport and equation coupling remain possible. Source lag is verified
exactly for 4,999 pairs. Normalized native VF/inventory agreement is also
verified, while raw phase sums depart from one. Neither check is conservation.

E7 changes only tau 0.02 → 0.10 s under E6's solver treatment. Its N0/N50 proofs
passed; local evidence reaches flux N679 and residual/speed N678, with the last
complete paired/scalar checkpoint at N500. The controller exited after an RPC
transport timeout. Later access checks failed; this review did not retry them.
The actual live iteration must be reconciled before any continuation.

The retrospectively examined N401–500 window is still startup: E6/E7 removal
is only 1.143/0.383 kg/s and inventories at N500 are 0.10158/0.10183 m³. Thus
E7's saved prefix cannot answer the late-window weaker-sink question. Its
completion is not redundant with the earlier SIMPLE tau 0.10 case.

## What Shuhei's new work adds

The existing R0–R11 roughness screen reports reduced carryover at larger
roughness, but also roughly 162–186 kg bulk-liquid depletion in the R5-height
comparisons and non-closing phase budgets. Its no-slip wall velocity report
is zero and does not measure wall-adjacent downward transport. These results
support roughness sensitivity, not a qualified separation improvement; more
roughness values would not resolve the present conservation question.

The earlier E0/E1/E3 comparisons recorded no film when no effective film
collection was configured. They do not demonstrate that EWF cannot collect
liquid. E2's accretion variants encountered numerical failures; E2.7 completed
with film Flow Momentum Coupling disabled, while retaining phase accretion and
the coupled film-equation solution. The new continuation extends that developed
state from native N8586 to N13586.

The committed CSV has exactly 5,001 consecutive, finite samples for all five
evolving series. Its published manifest statistics match independently
recomputed values:

| Quantity | Start → finish | Interpretation |
| --- | --- | --- |
| Bulk liquid mass | 63.023 → 62.989 kg | -0.054%; nearly stationary bulk inventory |
| Liquid steam-outlet flux | mean -1.7339 kg/s | Negative is outflow; much less carryover than R0 |
| Film mass | 3.111 → 5.842 kg | +87.79%; increases at every step |
| Area-weighted film speed | 46.34 → 82.41 m/s | +77.84%; increases at every step |
| Maximum film thickness | 0.331 → 0.310 mm | Range 0.275–0.531 mm; well below the 300 mm cap |

The bulk report excludes wall film. Combined reported bulk-plus-film storage
increases by 2.697 kg. Film mass still grows 3.48% in the final 500 samples;
its regression slope remains positive over the final 500, 1,000 and 2,000
samples. This is not just a misleading first-to-last comparison. The reported
terminal wetted area is 50.690 m², 94.86% of the film wall, but it is one
reconstructed endpoint measurement. The constant area history is geometric
wall area. Speed magnitude is not evidence of downward drainage.

**What is independently available:** the five exported histories, their
summary manifest, scripts and written results. **What is missing locally:**
the referenced original/continuation native run bundles, full source/flux and
film-time histories, residual histories, exact paired input/final files,
wetted-area calculation receipt, and roughness-family metrics bundle.
Consequently the claims of 26 complete native reports, 49,972 EWF residual
rows and no fatal events remain documented claims rather than reverified raw
evidence here. The setup also records a starting-pair hash mismatch versus
the earlier E2.7 terminal manifest; selected settings/native-coordinate checks
do not prove byte-identical ancestry.

The [committed interpretation](../../phase-07-2a-wall-liquid-routing/ewf-family/results.md)
already acknowledges that this is not fully converged or mass-balanced. The
positive finding is sustained film development with low bulk carryover under
that numerical treatment. It deserves a conservation/drainage audit, not
immediate adoption as a qualified full-geometry parent.

### Concrete accounting issues

The inherited virtual outlet commands the whole liquid-inlet throughput. Above
its normalization floor, integrating its expression returns that command by
construction. Exact command tracking does not allow additional carryover or
film discharge to disappear from the overall balance. Applied native source,
bulk escape, film outflow and both inventories must all be accounted for.

The roughness runner's `closure_summary` adds native mixture outlet to phase
ledgers that already include both phase outlets, counting outlet flow twice.
Its mixture statistic is unsuitable for qualification. This is a code finding
in [run_phase72a_family_r_native.py](../../../../PyAnsys/scripts/setup/run_phase72a_family_r_native.py),
not a demonstrated fault in the five EWF CSV series or in Andy's independent
native-mixture ledger. Correct and regenerate that derived statistic from
matched native histories before using it; retain the original evidence.
The roughness prose also calls R11 the lowest outlet-flow case although its
table has R7 lower (13.6253 versus 14.0164 kg/s). R11 is lowest within the
fixed-height Cs group, not across the entire family.

Film collection and outflow monitor fields in the report registry have units
of kg; they cannot simply be inserted as kg/s. Fluent supplies a separate
**Film Mass Flow Rate** flux report. Native-iteration slopes also cannot be
used as physical storage rates without the actual film-time mapping. For a
consistent combined ledger, internal bulk-to-film accretion cancels; count
external drainage and the user sink once. Continued film accumulation does
not prove zero drainage, but it rules out calling this film stationary.

## What documentation and literature support

- **Reported:** v252 supports phase accretion with Mixture plus Slip Velocity.
  Accretion transfers secondary-phase mass and momentum to film equations.
  Flow Momentum Coupling off makes the flow/film dynamical interaction one-way;
  it does not by itself disable accretion mass transfer. Film Coupled Solution
  is a different setting, coupling film continuity/momentum numerically.
  [Model options](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/flu_ug_ewf_sec_options.html),
  [accretion theory](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_th/flu_th_ewf_sec_film_submodels.html),
  [flow coupling](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/flu_ug_ewf_sec_bound.html),
  [film equation coupling](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_th/flu_th_ewf_sec_time_coupl.html).
- **Reported:** EWF remains time dependent with steady bulk flow. Film-wall
  edges can constitute film outlets; a `closedfilm` name or a bulk pressure
  outlet does not prove the film's drain topology. This must be mapped before
  claiming drainage. [Solution algorithm](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_th/flu_th_ewf_sec_sol_alg.html),
  [boundaries](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/flu_ug_ewf_sec_bound.html),
  [film flux reporting](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/flu_ug_ewf_sec_post.html).
- **Reported:** v252 recommends a cyclone Mixture startup route that temporarily
  freezes volume-fraction/slip equations while establishing flow, then restores
  them. This has not been isolated in our completed contrasts. Global pseudo
  time has a conservation caveat when phases lack separate inlet/outlet
  boundaries; no documented sink exception was found. Therefore copying the
  whole Shuhei numerical stack is a weaker next diagnostic than startup alone.
  [UG §27.8](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/flu_ug_sec_multiphase_solution.html).
- **Reported/Missing:** v252 documents user-supplied source derivatives and a
  degassing example. It does not establish the implicit derivative of our
  expression sink. The example is an analogue, not verified Mixture collector
  code. Phase 7b's Python/native-expression and no-new-C constraint remains;
  a compiled replacement cannot be silently introduced as a routine fix.
  [Source API](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_udf/flu_udf_ModelSpecificDEFINE.html).
- **Reported/Inferred:** Purnanto 2013 excludes brine-pipe flow; Pointon 2009
  truncates the domain near the baffle and idealizes droplet wall removal.
  Both provide useful simplified-separation precedents. Neither proves that
  this full-geometry steady Eulerian local sink converges or represents
  physical drainage. [Purnanto paper](https://www.researchgate.net/publication/269519626_CFD_MODELLING_OF_TWO-PHASE_FLOW_INSIDE_GEOTHERMAL_STEAM-WATER_SEPARATORS),
  [Pointon proceedings](https://publications.mygeoenergynow.org/grc/1028587.pdf).

## Recommended bounded finish to Phase 7b

1. **Resolve E7, without repeating it.** Restore access, reconcile the actual
   live state and any continuing solve, preserve it, then recover histories.
   Complete only the remaining distance to its existing absolute N5000 cap
   if the unchanged state and recording continuity are established. If that
   is impossible, preserve a partial external-block disposition. Do not infer
   the live state from the last local callback or replay from N500 blindly.
2. **Audit the source treatment before another large case.** Confirm signed
   phase/mixture source assignment and the associated momentum/turbulence
   terms against the active model. Keep the unverified expression Jacobian
   explicit. Source-report parity proves what was applied, not how the
   equations were linearized. Prefer read-only inspection and documented
   API capabilities; no speculative C-UDF replacement or open-ended search.
3. **At most one further full-geometry discovery case is justified by the
   present evidence:** the documented Mixture startup staging, if E7 still
   fails and the source audit exposes no concrete implementation defect.
   Retain the final E6 model/source/numerics; vary startup only. Proposed
   budget: at most 1,000 conditioning iterations within an absolute total
   of 5,000, followed by at least 4,000 with every intended equation restored.
   Predeclare the conditioning end rule, original late windows, full recording
   and exact restored-control checks in a setup before any solve. Do not
   simultaneously change slip relaxation, source coefficient or pseudo time.
   The frozen-equation stage is initialization, never an accepted solution.
   This proposal is not yet a selected E8 or runnable setup.

If a concrete source implementation error is demonstrated, repairing and
testing that error takes precedence over the startup proposal; it is not a
reason to run both automatically. If E7 already passes necessary conditions,
use a prospectively bounded persistence/restart test instead of another
discovery case. Include every conditioning/continuation iteration in the
cumulative horizon; do not hide it through a counter reset.

**Decision boundary:** if the final supported diagnostic also fails the
unchanged closure/inventory/residual criteria, close Phase 7b's present
numerical route as **not established within the tested model and budget**.
Report any source-derivative uncertainty as a limitation. Do not infer that
no steady solution exists or that the physical separator must be transient.
No further trial is justified merely because one residual or carryover number
looks better. Reopening requires a specific new causal finding and declared
test, not an unused menu setting. No unchanged long extension is supported by
the rising late inventory and persistently large budgets presently available.

## When a new phase is worthwhile

| Work | Appropriate home | Decision |
| --- | --- | --- |
| Finish E7, verify source accounting, isolate startup | Existing Phase 7b | Small remaining numerical value; bounded finish |
| More arbitrary collector sizes, tau/CFL values, roughness or turbulence combinations | No new phase merely to continue tuning | Low information value now |
| Prove bulk-to-film transfer, real film exits and combined conservation on simplified geometry | Existing Phase 7.2A | Highest-value follow-up to the new EWF result; repair evidence first |
| Test a conservative film/drain representation on the full geometry | New Andy phase if selected | Changes liquid representation/removal mechanism and time semantics |
| Predict separation efficiency, re-entrainment or compare designs | Later verification/validation phase | Needs a credible carrier, representation bookkeeping and external targets |

The recommended future full-geometry question is: **can an explicitly defined
liquid route conserve total liquid and reach bounded bulk/film inventories at
full feed, before optimizing carryover?** Begin with a minimal transfer/drain
verification problem and a declared mapping of liquid represented in bulk,
film and any later DPM. Then assess full-geometry routing. Require native
inlet/outlet/source budgets, film elapsed time, named-boundary film discharge,
spatially resolved thickness and flow direction, thickness-clipping accounting,
and a justified test of omitted film-to-flow feedback. Only afterward compare
carryover, pressure drop and independent measurements.

That would be a scientific change, not simply E7 with EWF enabled. Existing
Phase 06 and transient VOF failures do not authorize a return to pool modelling,
and adding DPM must not count liquid already present in another representation.
No new phase number, physical transient calculation, new compiled collector,
or replacement parent is selected by this review.

The work to date is sufficient for a defensible bounded negative result and
a strong next-question proposal. The reason to spend a little more on Phase
7b is to resolve two identifiable uncertainties—not because the current
budgets are close to acceptable.
