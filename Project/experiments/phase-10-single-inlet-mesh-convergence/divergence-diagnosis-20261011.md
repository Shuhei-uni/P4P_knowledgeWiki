# Phase 10 — Divergence diagnosis

| Question | Evidence-backed answer |
| --- | --- |
| Why did M04 stop? | Numerical overflow at N3911 after large velocity and residual spikes; pressure correction, k and liquid-fraction AMG solvers then failed |
| Is this only a mesh-quality problem? | Not established; all four failed levels share liquid accumulation and incomplete phase balance |
| Strongest common setup issue | Continuous liquid feed; sealed bottom; only the steam outlet can remove liquid; no film or source removal |
| Specific numerical suspect | Gravity is active; implicit body-force treatment is off in all four initial settings readbacks |
| Causal status | Failure chain verified; unique trigger and first unstable cell not identified |
| Current run | M05 N1000 pair recorded by the controller; passive transcript copy reaches N1643 without an FPE |
| Execution changes during diagnosis | None; M05–M07 queue and exact common settings retained |

## Common failure evidence

| Level | Cells | FPE iteration | Last full pair | Diagnostic sample | Liquid held, kg | Net liquid out, kg/s | Liquid flux deficit |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| M01 | 357145 | 1756 | 1000 | 1740 | 583.06 | 34.77 | 70.26% |
| M02 | 487746 | 4488 | 4000 | 4470 | 2436.75 | 66.25 | 43.34% |
| M03 | 681844 | 2769 | 2000 | 2760 | 850.50 | 37.92 | 67.57% |
| M04 | 946967 | 3911 | 3000 | 3890 | 1051.56 | 37.40 | 68.01% |
| M05, partial | 1430497 | None in copied transcript | 1000 | 1630 | 186.66 | 16.70 | 85.71% |

Source: native report histories and complete available solve transcripts in the [immutable text copies](../../../PyAnsys/output/phase10-single-inlet-mesh-convergence/divergence-diagnosis-20261011/raw/); [parsed summary](../../../PyAnsys/output/phase10-single-inlet-mesh-convergence/divergence-diagnosis-20261011/summary.json). Liquid inlet = 116.92 kg/s. Outward native flux is negative; table outflow = minus outlet report. Deficit = absolute(inlet + signed outlet) / inlet. The diagnostic row is the last shared report sample before continuity exceeds 10 or sampled maximum speed exceeds 1000 m/s. This descriptive cutoff does not qualify earlier fields.

![Liquid held inside and net liquid discharge](../../../PyAnsys/output/phase10-single-inlet-mesh-convergence/divergence-diagnosis-20261011/liquid-balance.png)

Raw ten-iteration samples through each diagnostic row; M05 is a partial continuation. Inventory rises across the family; brief discharge peaks in M02 do not establish stationary phase balance. Solver iterations have no physical-time coordinate, so inventory slopes cannot be interpreted as kg/s.

| Check | Observation | Meaning |
| --- | --- | --- |
| Scientific settings parity | M01–M04 initial full readbacks are exactly equal | No recorded model, boundary or numerical difference explains the cross-level failures |
| Phase-mass report validation | Vapor mass / vapor density + liquid mass / liquid density agrees with each mesh volume; maximum relative error 1.5e-12 | Inventory traces are consistent with the phase-volume partition |
| Liquid inventory change | Diagnostic final-500 sample windows: M01 +63.24%; M02 +21.61%; M03 +53.48%; M04 +14.55% | All exceed the recorded 1% stationarity limit; windows are before N5000 and are diagnostic only |
| Minimum OQ | M01 0.2401; M02 0.2349; M03 0.2048; M04 0.2240 | Earliest failure occurs on the best minimum-OQ level; this small sample does not isolate mesh effects |
| Cell-size jump | Only M03 has cells with size change >=300; its maximum is 881.63 | This local issue cannot alone explain M01, M02 and M04 |
| Spatial evidence | First unstable cell and nearby liquid/turbulence fields not recovered | Local mesh/gravity/phase-gradient interaction remains unresolved |

## M04 failure sequence

| Solver coordinate | Recorded event |
| --- | --- |
| N1000 | Liquid inventory 115.41 kg; liquid discharge 3.76 kg/s; continuity residual 0.29344 |
| N2000 | Liquid inventory 344.61 kg; liquid discharge 11.75 kg/s |
| N2775 | First printed epsilon residual above 1; the calculation later recovers from this burst |
| N3000 | Liquid inventory 710.87 kg; liquid discharge 29.89 kg/s; continuity residual 0.39912 |
| N3890 | Liquid inventory 1051.56 kg; liquid discharge 37.40 kg/s; maximum speed 410.01 m/s |
| N3898 | Continuity first exceeds 10 in the printed trace |
| N3900 | Maximum speed 87983.45 m/s |
| After N3909 | Turbulent viscosity reaches its 100000-ratio cap in 944886 of 946967 cells |
| N3910 | Continuity residual 2.2849e71; maximum speed 1.8061e85 m/s |
| Attempted N3911 | AMG pressure correction, k and vof-1 divergence; floating-point exception |

![Printed residuals for the four failed levels](../../../PyAnsys/output/phase10-single-inlet-mesh-convergence/divergence-diagnosis-20261011/failure-residuals.png)

Native iteration coordinates, with identical block-boundary rows deduplicated after equality checks. Vertical range is 1e-6 to 1e2; overflow tails extend beyond it. Dotted thresholds are continuity 1e-4 and other active equations 1e-3. Small momentum residuals coexist with poor continuity, turbulence and liquid-fraction residuals.

## Mechanisms and next discriminating check

| Candidate | Supporting evidence | Limit / discriminating check |
| --- | --- | --- |
| Liquid retention and an unsuitable steady separation boundary | Growing liquid mass; liquid discharge usually well below feed; no separate drain or other liquid-removal mechanism | Does not prove that no steady solution can exist: liquid is allowed to leave through steamoutlet. Confirm intended liquid-removal representation before treating this domain as a steady separator |
| Gravity/pressure imbalance | Density ratio 152.0; gravity active; SIMPLE; implicit body-force treatment off; local speed bursts | Test only implicit body-force treatment on a separate preserved M04 N3000 child; observe whether the failure chain is removed |
| Turbulence and phase transport instability | Repeated epsilon bursts; viscosity clipping; k/epsilon relaxation 0.8; QUICK liquid fraction; full higher-order methods from the Hybrid start | Test one numerical change at a time if the body-force contrast is insufficient; keep eventual final methods identical across levels |
| Local mesh transition / wall layers | Quality target 0.3 unmet; high aspect ratios; M03 size-jump pair | Recover spatial velocity, phase fraction, pressure and turbulence fields from the last full pairs in a separate idle inspection session; correlate with extreme-quality cells |
| API/Wi-Fi caused M04 failure | Native FPE and prior overflow are recorded in the local Windows transcript | Contradicted as the direct cause of M04; original M05 connection reset is a separate technical interruption |

Fluent 2025 R2 recommends implicit body-force treatment for Mixture with gravity, and describes a staged Mixture startup for cyclones. These are documented candidates, not proof of this case's cause. [User's Guide §27.2.7](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/flu_ug_sec_multiphase_setup.html), [§27.8.2.2](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/flu_ug_sec_multiphase_solution.html).

| Prepared diagnostic | Contract |
| --- | --- |
| Parent | M04 checkpoint-N3000 case/data pair, hashes in the original manifest; finite but unqualified diagnostic parent |
| Single delta | Enable implicit body-force treatment; retain all geometry, feed, materials, models, other controls and fields |
| Baseline | Existing N3000–N3911 failure segment; no baseline rerun required to establish its recorded failure |
| Horizon | 1000 additional updates to N4000, including a five-update smoke; distinct output root and ledger |
| Evidence | Strict readback/save/reopen; complete residual transcript; phase/mixture fluxes, inventory, maximum speed and viscosity-clipping history |
| Decision | Survival beyond N3911 supports a numerical-stability effect only; phase balance and inventory must also improve before qualification |
| Authority/status | Human-selected on 11 October 2026 NZ; queued after M07 finishes, not launched; [BF01 contract](setup.md#selected-follow-up--bf01-implicit-body-force-test) keeps this contrast separate from the baseline series |
| Scope boundary | A new liquid outlet, film, sink or transient study changes scientific setup; do not apply silently |

## Evidence and claim limits

| Artifact | Purpose |
| --- | --- |
| [Summary JSON](../../../PyAnsys/output/phase10-single-inlet-mesh-convergence/divergence-diagnosis-20261011/summary.json) | Quantitative diagnostic, parity checks, source hashes and limitations |
| [Report CSV](../../../PyAnsys/output/phase10-single-inlet-mesh-convergence/divergence-diagnosis-20261011/reports.csv) | Raw report values on shared native coordinates, including failure-tail samples |
| [Residual CSV](../../../PyAnsys/output/phase10-single-inlet-mesh-convergence/divergence-diagnosis-20261011/residuals.csv) | Complete available printed residual histories, including overflow tails |
| [Warning CSV](../../../PyAnsys/output/phase10-single-inlet-mesh-convergence/divergence-diagnosis-20261011/warnings.csv) | File/line references and previous printed iteration for each warning |
| [Analysis script](../../../PyAnsys/scripts/analysis/analyze_phase10_divergence.py) | Deterministic offline reconstruction and figures |
| Qualification limit | No mesh independence, poly accuracy advantage, tet/poly speedup or unique causal mechanism established |
