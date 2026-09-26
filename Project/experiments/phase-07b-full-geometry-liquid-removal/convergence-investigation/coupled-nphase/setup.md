# E6 — solve all phase-fraction equations under unchanged CFL20

Predeclared under the [autonomous investigation authority](../plan.md), conditional on completed G5 evidence and live capability verification. Case **S40-T020-COUPLED-CFL20-NPHASE**. One fresh child; no parallel run or automatic continuation.

## Question and controlled change

Does explicitly solving both primary vapor and secondary liquid volume fractions improve source-inclusive phase/native-mixture conservation compared with E5's secondary equation plus primary complement? Change only `solution.methods.p_v_coupling.solve_n_phase` from false to true. Retain ordinary Coupled, pseudo time Off, CFL20, explicit pressure/momentum relaxation0.5/0.5, segregated volume-fraction solution, mp relaxation0.4, tau0.02s, fixed source law, source update interval1, mesh/materials/boundaries, full feed, drift model, discretization, AMG and residual presentation.

This is distinct from Coupled with Volume Fractions. [Fluent2025R2 UG§27.8.1.3.2](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/flu_ug_sec_multiphase_solution.html) identifies N-phase equations as a case-dependent option for poor convergence/mass imbalance: all phase fractions are solved and then scaled to sum toone. That fraction constraint does not guarantee physical mass conservation. The liquid equation is already solved in E5; this does not supply a source Jacobian or establish that the original complement is incorrect.

G5 found lower CFL reduced liquid/vapor/native-mixture late absolute closure to148.115/2.132/86.795% while inventory change worsened to19.333% and continuity maximum2.5817. Further damping is not currently selected. All-phase treatment is a smaller, directly documented diagnostic than introducing Global Time Step, a different startup history or a new source law. These remain alternatives if it fails.

## Parent and implementation proof

Preserve E5 final N5000 before replacement. Use original common clean N0 `p7b-clean-initial-20260912T080713Z`, identical original SIMPLE Hybrid options and physical fields, then apply E5 Coupled/Off CFL20 and the single N-phase switch at N0. Geometry620431 cells, S40 collector41258 cells, full-feed split velocity inlets27.118m/s, liquid/vapor densities881.77/5.73kg/m³ and closed brine wall remain unchanged. Steady Mixture/RNG, Energy/DPM/EWF off.

Before solving, inspect live active Boolean and exposed residual equations. Compare setup, sources, methods, controls and residual options to E5; only solve_n_phase may differ scientifically. Record any newly exposed equation monitors and enable their recording with automatic convergence stopping disabled. Do not invent a primary residual name. Preserve existing seven monitor settings and scaled/global, non-normalized presentation; record expected exposed equation names. Save/reopen, verify exact settings and source parity, and prove initial physical-field/geometry equality using the original section and whole-cell arrays. An inactive option, unexpected setting change, residual mismatch or initial-field mismatch is a recoverable preparation problem, not a tested scientific failure.

## Horizon and evidence

Absolute N5000 including N50 smoke; no poor-balance/spike early stop. A genuine numerical failure requires preserved evidence and an explicit partial disposition. No continuation is selected.

Same N50/every500/final local-PC pairs (N5000 uses final pair), scalar/native exact-face phase and mixture flux histories, source lag, initial/final horizontal and full-height axial native fields, every-iteration speed, scheduled whole-cell captures including2600/2700/2800, and sampled≥500m/s events with N+1/N+5 followups. Verify snapshot iteration, native-field parity, hashes, completeness and errors. Raw SV_MASS_IMBALANCE remains uncalibrated.

Record every exposed residual, retaining the original seven. If a primary-phase residual becomes available it is mandatory; if Fluent exposes no separate primary residual, state that limit explicitly. Independently measured phase/native-mixture budgets remain necessary in either case. No fabricated control curve for a new equation.

## G6 comparison and decision

Compare E5 versus E6 at N4501–5000; inventory means use4001–4500 versus4501–5000. Core figures: raw source-inclusive liquid/vapor/native-mixture budgets and inventory; all exposed residuals and speed; matched N5000 native inlet-region liquid/speed and full-height axial liquid fields with shared cameras/ranges. Report signed and mean-absolute vapor closure, carryover, vapor routing, extrema, limiting, source lag and snapshot locations.

Unchanged discovery indicators: each mean absolute phase/native-mixture closure≤1%feed, inventory mean change≤1%, every exposed equation residual<1e-3 throughout late window. These are necessary discovery indicators, not physical validation. A pass requires prospectively bounded persistence/restart qualification. A failure would leave source coupling/startup/transport as alternatives; it would not prove no steady solution exists. Interpret fraction-sum enforcement separately from conservation and distinguish changed convergence rate from a different asymptotic state.

## Pre-solve persistence recovery boundary

The first E6 attempt crashed during prepared-data reload before solving. [Recovery design](recovery.md) permits a prospective initialization-order repair only if exact original N0 physical/geometry parity and full save/reopen verification still pass. It does not authorize hidden preparation iterations, changed initial fields or a blind retry of the failed pair.
