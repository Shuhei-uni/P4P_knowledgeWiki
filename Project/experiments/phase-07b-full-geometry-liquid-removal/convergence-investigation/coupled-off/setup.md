# E4 — fresh S40-T020 with Coupled and pseudo time Off

Selected under the [autonomous investigation](../plan.md), 22 September 2026
UTC, after completed G3 and the [Shuhei audit](../shuhei-audit.md).
Case ID: **S40-T020-COUPLED-OFF**. Classification: **NEW controlled contrast**.
Earlier Coupled cases on other meshes/sources/loading histories cannot answer
this question. This is a solver-path test, not a replication of Shuhei's case.

## Hypothesis and controlled change

Does solving pressure and momentum together suppress the observed inlet-region
excursions and improve source-inclusive steady closure without introducing
Global Time Step? Change SIMPLE to ordinary Coupled; keep volume fraction
segregated (`solve_n_phase=false`) and coupled pseudo time explicitly Off.
Use the documented Coupled/Off starting controls: Flow Courant 200 and explicit
pressure/momentum relaxation 0.5/0.5. These controls are part of the declared
algorithm treatment, not equivalent to SIMPLE's 0.3/0.7 URFs. Preserve existing
phase, k, epsilon, drift and material relaxation. Record automatically activated
coupled linear-solver controls and require all unrelated settings unchanged.
No HOTR, low-order scheme, source-law or mass-transfer change is included.

Before solving, inspect live settings252 allowed values and active controls,
record the exact delta, save/reopen and verify it. A failed setter or unexplained
settings change stops preparation for repair; it is not a failed hypothesis.

## Parent, invariants and initialization

Use original clean N0 `p7b-clean-initial-20260912T080713Z` case/data, the same
S40 partition, identical Hybrid options and no liquid patch. Perform Hybrid
with the original SIMPLE settings, then apply the Coupled treatment at N0 so
the initial field is controlled. Prove initial native section/cell parity to
E3, not merely zero liquid inventory.

Keep tau 0.02 s, source bindings and lag/update interval 1; mesh, materials,
full-feed split velocity BCs, closed brine face, Energy/DPM/EWF off, steady
Mixture/RNG, spatial schemes, gradient/pressure treatment, limiting and all
other settings fixed. Preserve E3 final N5000 before loading this fresh child.

Residual policy: retain global scaling enabled, local scaling disabled,
Normalize disabled, seven equations printed/monitored, automatic convergence
stop disabled. Never renormalize to make a comparison pass. A changed algorithm
can change residual definitions/denominators despite identical options; compare
independent budgets and raw trends, not residual ratios as physical error ratios.
Record initial, post-treatment and reopened residual settings.

## Horizon and decisive evidence

Absolute cap **5000 iterations including N50 smoke**; paired N50, every 500 and
final checkpoints on local PC, with unique destinations. Analyse N4501–5000;
compare inventory means N4001–4500 and N4501–5000. No extension is implicit.
Poor balance/spikes are not early-stop criteria. An actual numerical failure
requires preserved last-valid evidence and explicit partial disposition.

| ID | Question and evidence | Comparison and decision use |
| --- | --- | --- |
| E4-F1 | Raw every-iteration source-inclusive liquid/vapor/native-mixture kg/s budgets, liquid inventory m³ and carryover | Original T020 and E3, same coordinates/windows/feed denominators; does improved continuity correspond to closure and bounded inventory? |
| E4-F2 | All seven raw residual histories, speed m/s, k/epsilon extrema, applied/current source and lag | Whole run and declared late windows; do excursions vanish or merely move/change scale? Preserve raw oscillations and limiting/reverse-flow transcript indicators. |
| E4-F3 | Native horizontal/axial fields plus common-scale inlet-hotspot contours at y=2.4272831101 m | Same initial/final sections and cameras as G3, terminal states at equal iterations; test spatial redistribution without inferring causality from a residual plot. |

Retain exact-face collector flux every iteration, initial/final native field
arrays and E3 whole-cell scheduled/speed-triggered capture with N+1/N+5
followups, iteration/parity checks and explicit missed-event limits. Native
source enters each appropriate balance exactly once. Raw SV_MASS_IMBALANCE
remains uncalibrated supporting evidence.

Discovery indicators remain all seven residuals <1e−3 throughout the late
window, mean absolute phase/mixture errors ≤1% of the respective feed, and
inventory-window change ≤1%. Passing is a candidate for bounded persistence
and restart qualification, not automatic physical validation. Failure of this
one Coupled/Off setting does not reject every Coupled control choice.

## Prospective interpretation

Improved budgets plus bounded inventory and fewer localized excursions support
the coupling hypothesis. Lower displayed residuals with poor budgets do not.
Persistent spatial events suggest source/phase/startup/local numerics remain
plausible; no unique cause follows from this single contrast. Choose the next
small discriminating case only after this disposition and required evidence.
