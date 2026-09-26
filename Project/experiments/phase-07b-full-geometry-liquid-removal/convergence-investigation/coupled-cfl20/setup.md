# E5 — fresh Coupled/Off with Flow Courant 20

Selected under [autonomous investigation authority](../plan.md) after the
completed E4 scientific comparison. Case **S40-T020-COUPLED-CFL20**. This is a
single-control fresh-start contrast against E4, not a continuation or a new
source law. No simultaneous child or open-ended Courant sweep is selected.

## Question and controlled delta

Does stronger implicit damping of the coupled continuity/momentum equations
reduce E4's rapid vapor-balance oscillation and improve source-inclusive
phase/mixture closure and inventory stationarity? Change only **Flow Courant
200 → 20** relative to E4. Retain ordinary Coupled, pseudo time Off, segregated
volume fraction, explicit pressure/momentum relaxation 0.5/0.5, all scalar and
other relaxation, source law and update interval, spatial schemes, AMG controls
and residual presentation. No normalization or residual reset during solve.

The value 20 is an investigator-selected order-of-magnitude contrast, not a
vendor-prescribed optimum. Fluent 2025 R2 [UG §37.3.1.5](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/flu_ug_sec_uns_solve_pvel_1.html)
documents CFL-based Coupled controls and lowering CFL for immediate AMG
divergence; E4 has no such divergence, so transferring this to its oscillation
is a hypothesis. [Theory §§23.4.4.1–2](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_th/flu_th_sec_time_theory_seg.html)
distinguish implicit CFL damping from explicit variable relaxation. The
multiphase low-Courant stabilization wording in UG §27.8.1.1 is Eulerian,
not direct proof for Mixture. Ordinary Mixture Coupled with segregated volume
fraction is supported in [UG §27.8.1.2](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/flu_ug_sec_multiphase_solution.html).

## Why this contrast first

E4 suppresses >500 m/s events but leaves 263.7% late liquid closure error,
5.22% mean absolute vapor closure and 11.5% inventory mean change. Its vapor
signed mean error is just 0.141%, indicating cancellation of substantial
oscillation. A single verified numerical control offers a smaller contrast
than adding global pseudo time, a developed inlet ramp or a new source law.
It may slow progress and need more iterations; the current cap will not be
silently extended to compensate. Similar bad closure under stronger damping
would weaken numerical-step aggressiveness as a sufficient explanation.

Native expression implicit source derivatives remain unverified. The v252
[DEFINE_SOURCE section](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_udf/flu_udf_ModelSpecificDEFINE.html)
documents supplied UDF derivatives, not automatic expression differentiation.
[UG §5.1](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/flu_ug_expressions_intro.html)
documents profile-interval expression evaluation. No documented API-only
implicit-expression switch was established. E5 is numerical damping, not a
claimed source-Jacobian repair. Existing coupled momentum/turbulence sinks
remain unchanged, as required when removing mass under
[UG §8.2.7](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/flu_ug_bcs_sec_cell_zones.html).

## Parent, build proof and frozen settings

Preserve E4 final N5000 first. Reload original clean N0
`p7b-clean-initial-20260912T080713Z`, reconstruct the same S40 mask, initialize
with exactly the original SIMPLE Hybrid options, then apply Coupled/Off CFL20
at N0. Tau remains 0.02 s. Full geometry, 620,431 cells / 41,258 collector
cells, full-feed split velocity inlets, materials, steady Mixture/RNG,
Energy/DPM/EWF off and closed brine wall are unchanged.

Use E4's verified Coupled controls as the baseline; deep comparison must find
only `p_v_controls.flow_courant_number` different. Verify through live readback,
save/reopen and exact initial physical-field and geometry parity with E4/E3.
Record the source attachment and all seven residual policies. A setter or
parity failure is a preparation problem to repair before solving.

## Horizon, evidence and decision

Absolute cap **N5000**, including N50 smoke. Same checkpoints, every-iteration
scalar/exact-face-flux/seven-residual/speed histories and source-lag audit as
E4. Paired N50/every500/final files on the PC local disk; N5000 is represented
by the final pair. Preserve initial/final horizontal and full-height axial
native fields. Retain scheduled and speed-triggered cell snapshots and N+1/N+5
followups; raw SV_MASS_IMBALANCE remains uncalibrated.

Compare E4 versus E5 on identical N4501–5000 windows; inventory means use
N4001–4500 versus N4501–5000. Core figures: raw liquid/vapor/native-mixture
budgets and inventory; all seven residuals and speed; common-scale native
inlet-region and full-height phase fields. Tabulate signed and absolute vapor
closure separately, liquid carryover, vapor recovery, limiting, extrema,
source-lag and recorded snapshot locations. Preserve raw histories alongside
any window statistics. Original SIMPLE/E3 remain supporting references.

Indicators are unchanged: each mean absolute phase/mixture error ≤1% of feed,
inventory-window mean change ≤1%, all seven residuals <0.001 throughout the
late window. A passing discovery would need prospectively bounded persistence
and restart qualification. A failed N5000 result does not prove no longer
steady solution exists. Poor balances alone do not cause early stopping;
a genuine numerical failure requires preserved evidence and explicit partial
disposition. After G5, select the next smallest supported contrast under the
investigation authority; no automatic extension is implied.
