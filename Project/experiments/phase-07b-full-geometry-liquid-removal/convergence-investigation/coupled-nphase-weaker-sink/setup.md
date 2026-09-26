# E7 — weaker sink under unchanged Coupled/N-phase treatment

Predeclared 2026-09-24 after completed G6. Case S40-T100-COUPLED-CFL20-NPHASE. Authorized by [investigation plan](../plan.md). One fresh child; absolute5000 iterations including N50. No continuation selected.

## Question and controlled delta

Does reducing the liquid-removal coefficient fivefold improve independent conservation under the E6 numerical treatment? Change only tau0.02→0.10s in P7bSink. Its linked mass, momentum, k and epsilon sinks consequently reduce fivefold at identical fields. Their definitions, phase targeting, source update interval1 and application remain unchanged. This tests sensitivity to source strength/stiffness, not an undocumented implicit Jacobian. The removal timescale is a model parameter: improvement would not validate original tau or prove a purely numerical cure.

E6 late liquid/native-mixture errors144.369/84.841% and inventory change18.451% remain far outside acceptance despite reduced residuals. Native removal275.962kg/s exceeds liquidfeed116.921kg/s while inventory grows. Exact4999-pair source-lag and flux audits rule out missing recording or an extra source count in the audit. They do not prove satisfactory equation/source coupling.

The previous tau0.10 experiment E2 used SIMPLE, whereas E6 retains ordinary Coupled/Off/CFL20 and all-phase equations. This comparison isolates the source coefficient under that different solver treatment; it is not a duplicate E2 case.

## Invariants, parent and proof

Preserve E6 final N5000 and use original common clean N0 p7b-clean-initial-20260912T080713Z with identical original SIMPLE Hybrid options/physical fields. Use the verified N-phase-before-Hybrid allocation order, initial source-free pair reopen and exact prepared/source-enabled pair reopen. Retain the E6 pre-save counter0/1 and bijective-cell roundoff guard only at initial source-free capture; all postreload/prepared N0 gates requirecounter0 and exact original ordered arrays. No hidden solves, offsets, residual resets or developed-field startup.

Hold mesh620431cells, S40collector41258cells, full split velocity inlet27.118m/s, phase densities881.77/5.73kg/m³, closedbrinewall, pressureoutlet, steadyMixture/RNG, Energy/DPM/EWFoff, drift/slip, all discretization, AMG, residual presentation and source assignment fixed. Coupled, pseudoOff, CFL20, pressure/momentum explicitrelaxation0.5/0.5, segregatedVF, Nphaseon and mpURF0.4 match E6. Verify methods/controls exactly against E6 and expression definitions differ only P7bSink, including coefficient ratio0.2. Preserve all8 residuals with automatic stoppingdisabled.

## Evidence and horizon

Absolute N5000; no poor-balance/spike early stop. Verify exact source/control delta, both pair reopens, exact N0 physical/geometry parity and N50smoke before routine execution. Keep pairedN50/every500/final local-PC checkpoints (N5000 usesfinal), scalar and exact-face flux, all8 residual histories, every-iteration speed, initial/final horizontal and full-height axial native fields, scheduled whole-cell captures including2600/2700/2800, speed>=500 triggers plusN+1/N+5. Retain both raw phase fractions, rawinventory, rawphase-sum extrema and independent normalized-inventory/native parity using originalrtol1e-9/atol1e-12. RawSV_MASS_IMBALANCE remainsuncalibrated. Recover implementation/evidence errors without changing physics; preserve explicit partial numerical-failure dispositions.

## Analysis and decision

Compare E6/E7 N4501–5000; inventory means4001–4500 versus4501–5000. Corefigures: raw source-inclusive liquid/vapor/native-mixture closure and inventory; all8 residuals/speed; matched N5000 native inlet-height liquid/speed and full-height axial liquid with shared cameras/ranges. Report signed versus meanabsolute vaporerror, applied/current source lag, carryover/vapor routing, limiting, extrema, rawfraction semantics and sampledhotspot locations. Original E2tau0.10 and E5 are supporting references only.

Unchanged necessary discovery indicators: all three meanabsolute closureerrors<=1%feed, inventorymeanchange<=1%, everyexposedresidual<1e-3 throughoutlatewindow. Passing requires a prospectively bounded persistence/restart qualification; not physicalvalidation. If deficits stay comparable despite fivefold coefficient reduction, source strength alone is weakened as explanation and solver/source treatment or startup becomes the next discriminant. Increased inventory or carryover can offset a smaller source deficit; judge the complete budget rather than residuals alone.

## Decision-changing documentation and alternatives

Fluent2025R2 [UG27.8.1.3–1.4](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/flu_ug_sec_multiphase_solution.html) excludes Coupled with Volume Fractions for Mixture Slip Velocity; retained drift means that path cannot be a one-control contrast. N-phase normalization does not guarantee conservation. [UG37.14](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/flu_ug_sec_solve_pseudo.html) supports Global Time Step as steady implicit relaxation; [TG23.6.2](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_th/flu_th_sec_pseudo_auto.html) describes automatic convective/gravity/etc timescales without establishing awareness of this user-expression sink timescale. Global pseudo time remains a broader alternative, requiring explicit dependent-control design. No documentation establishes expression-source implicit derivatives. Tau0.10 is investigator-selected, not a manual recommendation.
