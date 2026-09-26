# G5 — stronger Coupled damping does not establish steady conservation

E5 reached its declared N5000 cap without numerical failure. The recording audit and six common-scale native spatial figures passed QA; G5 is complete. Neither E4 nor E5 meets the predeclared numerical criteria. The only controlled change is Flow Courant 200 to20 from identical fresh physical fields; all source, phase, physical and other numerical settings were verified unchanged.

## Evidence answering the question

[Raw budget/inventory figure](../../../../../PyAnsys/output/phase07b-g5/E5-F1-closure-inventory.png) and [all-equation residual/speed figure](../../../../../PyAnsys/output/phase07b-g5/E5-F2-residual-speed.png) retain all 5000 samples. Lower Courant strongly damps the rapid alternating vapor error, but leaves slower excursions, large negative liquid/native-mixture balances and continuing inventory growth. Both figures were visually inspected: labels, raw signals, late window and threshold references are legible.

The table uses N4501–5000; inventory compares N4001–4500 and N4501–5000 means, normalized by the larger mean. No physical time is assigned to steady iterations.

| Indicator | E4 CFL200 | E5 CFL20 |
| --- | ---: | ---: |
| Liquid mean absolute closure (% feed) | 263.6773 | 148.1147 |
| Vapor mean absolute closure (% feed) | 5.2228 | 2.1319 |
| Mixture mean absolute closure (% feed) | 155.9607 | 86.7954 |
| Inventory window mean change (%) | 11.5263 | 19.3329 |
| continuity late maximum | 2.3959 | 2.5817 |
| x-velocity late maximum | 0.0002763 | 0.00016729 |
| y-velocity late maximum | 0.0002496 | 0.00010257 |
| z-velocity late maximum | 0.00025584 | 0.00017017 |
| k late maximum | 0.037306 | 0.017551 |
| epsilon late maximum | 0.088281 | 0.048942 |
| vf-phase-2 late maximum | 0.014106 | 0.012917 |

Only the three momentum residuals remain below1e-3 throughout the late window. E5 lowers phase-budget errors, yet all exceed1%; inventory drift worsens and continuity maximum slightly increases. It is therefore not a qualified improvement in steady numerical adequacy.

E4's late signed vapor error is +0.1413% versus5.2228% mean absolute; E5 is +2.0603% versus2.1319%. The small signed E4 value came from cancellation. E5 reduces that fast alternating component (lag-one correlation0.5724→0.9922), but leaves a positive mean bias. These iteration correlations characterize numerical histories, not physical frequencies.

Late mean liquid carryover changes31.5806→11.4927% of liquid feed; vapor recovery99.8587→97.9397%. Mean native applied removal388.2916→276.6614kg/s still far exceeds the116.9212kg/s liquid feed. Mean liquid volume0.584739→0.516966m³, but the E5 final volume is still growing overall. Neither lower carryover nor apparent vapor recovery is credible separation performance while budgets fail. Source-inclusive native-mixture error is independently measured, not merely the phase sum.

## Diagnostics and competing explanations

All5000 scalar, exact-face flux, speed and seven-equation residual samples are present. Applied source at N exactly matches recomputed source at N−1 for4999 consecutive pairs. Paired N50/every500 through4500 plus final N5000 are verified through controller Fluent-API save/existence receipts and exact checkpoint readback. Initial/final horizontal and full-height axial section arrays are finite; initial physical/geometry parity passed. Fifteen scheduled whole-cell snapshots match iteration, native fields and hashes. Event schedule replay passed: there were no≥500m/s events, so no speed-event followups were due. Raw SV_MASS_IMBALANCE remains uncalibrated.

E5's whole-run maximum speed is283.0914m/s versus267.6636 forE4; late maxima154.9601 versus149.5695m/s. Both avoid original SIMPLE's extreme bursts. AroundN2700, epsilon p95 changes0.007910→0.007646 forE5, compared with0.023606→0.032394 forE4 (windows2201–2700 and2701–3200). E5 does not reproduce the original onset as a sharp epsilon-spike increase, but later deterioration persists.

Viscosity limiting is more persistent inE5:4824 transcript messages, maximum4734 cells, versus598/max2088 inE4. Both have4998 reverse-flow messages. Counts reflect reporting occurrences, not unique cells or physical residence times. [Diagnostic evidence](../../../../../PyAnsys/output/phase07b-g5/diagnostic-comparison.json) records sampled maximum locations; these are scheduled snapshots, not a complete trajectory of each unsaved peak.

Observation supports sensitivity to flow-update damping. It does not support aggressive flow CFL as a sufficient explanation of the large liquid imbalance. Slower development under stronger damping can confound an equal-iteration comparison; no asymptotic equivalence or impossibility of a later steady state is claimed. Phase/source coupling, primary-phase treatment, startup history and local transport remain alternatives. Exact one-iteration source lag verifies update behavior, not the source Jacobian or convergence of its coupling.

## Native spatial comparison

[Six native Fluent exports](../../../../../PyAnsys/output/phase07b-g5/native-graphics-manifest.json) compare E4/E5 N5000 on horizontal y=2.427283m and full-height x=0 cuts. Liquid fraction uses0–1; inlet-plane speed0–80m/s covers the discovered ranges (E4max55.31, E5max74.29m/s). Cameras and facet-based display match. E5 shows a thinner liquid band on parts of the curved inlet region and higher local speeds, while both axial cuts show narrow wall liquid and mostly low interior fraction. This is endpoint location evidence, not validated separation or a causal source diagnosis.

The first export attempt hit a generated filename collision before overwriting anything. Its partial artifacts were retained; E5 was restored, unique graphics names corrected, and all six exports completed under the same shared range. E5 final was restored again; zero solver iterations were issued during export/recovery.

## Next decision

Select [E6](../coupled-nphase/setup.md), a fresh E5-matched child with only Solve N-Phase Volume Fraction Equations enabled. Official Fluent2025R2 UG§27.8.1.3.2 identifies this as a case-dependent option for poor convergence/mass imbalance; it solves primary and secondary fractions then rescales their sum toone. This is distinct from coupled volume fractions and does not linearize the liquid source. Live/save-reopen capability, all exposed residuals and unchanged initial physical fields must be verified before compute. The setup will predeclare the N5000 horizon and unchanged late windows. Startup/global pseudo time/source treatments remain alternatives; no blind continuation or Courant sweep is selected.
