# E2.8 — fast adaptive phase-accretion EWF with fixed-step recovery

## Question

| Question |
| --- |
| Can aggressive adaptive EWF controls reach an E2.7-like developed-film state in fewer iterations and remain numerically usable through 3,000 additional steady iterations, starting from the same native-5586 Phase 7.2A control state? |
| E2.7 reached native 8586 after 3,000 iterations with 3.111 kg film mass and 0.331 mm maximum thickness |
| Its separate 5,000-iteration continuation reached native 13586 with 5.842 kg film mass, 82.41 m/s area-weighted speed, 0.310 mm terminal maximum thickness, and 50.690 m² terminal wetted area |
| E2.8 compares both to its native-8586 endpoint |
| The continuation's copied starting pair had a documented hash mismatch against the earlier E2.7 run manifest; keep that identity limitation attached to the late reference |

## Parent and controlled change

| Item | Parent and controlled change |
| --- | --- |
| — | Start from the exact Phase 7.2A R0 parent at native 5586 described in the [baseline handoff](../../baseline-control-handoff.md): case SHA-256 `4fd493972839929f1f0922ad42679456d1f4aea294da86e4b13d6b7c32f754fc` and data SHA-256 `b2261fac8626b2e338c3a9c80c334c8a910d1bfb536f782ef9234623f00e1a72` |
| This | is an independent child from the same state as E2.7, not a continuation from E2.7's film-bearing endpoint |
| — | Activate the same E2.7 phase-accretion EWF configuration on `wall`, with zero roughness, no DPM interaction, and no film wall on `bottom` |
|  | Change the E2.7 numerical controls as one fast-time package: |

| Control | E2.7 | E2.8 |
| --- | ---: | ---: |
| Time scheme | First-order implicit | First-order implicit |
| Adaptive film stepping | Off | **On** |
| Maximum film Courant | 0.05 | **0.5** |
| Initial film timestep | 1e-4 s, inactive in fixed mode | **1e-4 s** |
| Timestep increase factor | 1.5 | **2.0** |
| Timestep decrease factor | 2.0 | **2.0** |
| Film sub-iterations | 10 | **3** |
| Sub-iteration stop | 1e-5 | **1e-3** |
| EWF Coupled Solution | On | On |
| Film-wall Flow Momentum Coupling | Off | Off |
| Phase Accretion | On | On |
| Maximum film thickness | 0.3 m | 0.3 m |

| Item | Parent and controlled change |
| --- | --- |
| stored fixed-step value | remains 1e-5 s but is inactive while adaptive stepping is on |
| — | Fluent's steady-flow EWF advances film physical time each iteration; its adaptive update uses the maximum Courant and the increase and decrease factors ([2025 R2 solution algorithm](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_th/flu_th_ewf_sec_sol_alg.html)) |
| This | is a combined numerical-control test and cannot attribute a result to one setting in isolation |

## Executed path and evidence

| Item | Executed path and evidence |
| --- | --- |
| — | The fast profile ran from native 5586 through a preserved native-7000 pair (1,414 selected adaptive iterations) |
|  | It briefly approached E2.7's native-8586 film response |
|  | The profile then became numerically unstable; the divergent branch continued 318 additional iterations and was stopped at native 7318 |
| exact native-7000 case/data pair | was reopened and used for recovery with E2.7's stable fixed-step controls: adaptive OFF, fixed film timestep `1e-5 s`, 10 maximum EWF sub-iterations, and stop `1e-5` |
| — | This recovery ran 1,586 iterations to native 8586 |

<details>
<summary>Supporting detail — Executed path and evidence</summary>

| Item | Executed path and evidence |
| --- | --- |
| — | The selected trajectory therefore contains 3,000 additional iterations (1,414 adaptive plus 1,586 fixed-step recovery); total solver work, including the discarded divergent branch, was 3,318 iterations |
| final pair | is a hybrid recovery result, not a stable 3,000-step run of the aggressive profile |
| All 37 native Report Files | were recovered at every selected coordinate from 5586 through 8586 (3,001 points each) |
| set | includes inherited flow, absorber, outlet, and closure monitors, plus EWF film mass, maximum and area-weighted thickness, film Courant, cumulative outflow, phase-accretion mass and collection coefficient, area-weighted and maximum film speed, area-weighted film velocity components, free-surface speed and velocity components, effective pressure, Weber and stripping Weber numbers, and the per-iteration Film Coverage surface integral |
| unavailable report fields | are DPM-to-film source mass, stripped mass, and separated mass; Fluent 2025 R2 does not expose them in the allowed surface-report field list for this case |
| corresponding available phase-accretion and collection reports | were captured |
| Paired checkpoints | were saved every 250 iterations |
| Thickness-distribution areas | were reconstructed from the saved film-height field for 12 checkpoints and the named start/final pairs, across all 3,463 faces on `wall` |
| reconstructed wall area | was `53.436952299276584 m²`, matching Fluent's `53.4369522992766 m²` report within `1.42e-14 m²` |
| analysis | records area at or above `0.01`, `0.05`, `0.10`, `0.25`, and `0.50 mm`, plus six disjoint thickness bands |
| — | Fluent defines Film Coverage from its critical film thickness; these threshold-area series remain separate diagnostics ([partial-wetting definition](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_th/flu_th_ewf_sec_wet.html)) |
| per-iteration native Film Coverage integral and checkpoint reconstruction | are retained separately |
| — | At native 8586 they report `50.20515 m²` and `50.39461 m²`, respectively; the checkpoint method is used for E2.7/E2.8 thickness-area comparisons, and no measurement is substituted for the other |

</details>

### Matched response at the first stable checkpoint

| Item | Matched response at the first stable checkpoint |
| --- | --- |
| — | At native 7000, after 1,414 selected adaptive iterations, the E2.8 response was close to E2.7's native-8586 endpoint |
| table | uses the same EWF Report Files for film mass/thickness/speed and the same saved-pair face-area reconstruction for coverage and threshold areas |

| Measure | E2.7 at 8586 | E2.8 at 7000 | Difference |
| --- | ---: | ---: | ---: |
| Film mass | 3.1112 kg | 3.2007 kg | +2.9% |
| Maximum thickness | 0.3310 mm | 0.3078 mm | -7.0% |
| Area-weighted thickness | 0.06607 mm | 0.06797 mm | +2.9% |
| Area-weighted film speed | 46.34 m/s | 45.36 m/s | -2.1% |
| Maximum film speed | 222.07 m/s | 221.25 m/s | -0.4% |
| Reconstructed Film Coverage area | 50.1453 m² | 50.2027 m² | +0.11% |
| Wall area with thickness ≥ 0.01 mm | 45.3449 m² | 46.3220 m² | +2.15% |
| Wall area with thickness ≥ 0.05 mm | 21.3569 m² | 22.2961 m² | +4.40% |
| Wall area with thickness ≥ 0.10 mm | 13.9070 m² | 13.9150 m² | +0.06% |
| Wall area with thickness ≥ 0.25 mm | 1.5479 m² | 1.6730 m² | +8.08% |
| Wall area with thickness ≥ 0.50 mm | 0 m² | 0 m² | 0 m² |

| Item | Matched response at the first stable checkpoint |
| --- | --- |
| — | The adaptive path had advanced `0.02930 s` of film time by native 7000, compared with `0.03000 s` for E2.7's 3,000 fixed steps |
| Its apparent iteration reduction | was therefore real for this intermediate response, but the adaptive profile did not remain stable |

### Recovered native-8586 endpoint

| Item | Recovered native-8586 endpoint |
| --- | --- |
| — | The selected hybrid trajectory ended at native 8586 with `4.2484 kg` film mass, `0.3026 mm` maximum thickness, `0.09022 mm` area-weighted thickness, `63.14 m/s` area-weighted film speed, `230.19 m/s` maximum film speed, and `50.3946 m²` reconstructed Film Coverage |
|  | Against E2.7 at the same endpoint, the hybrid result has 36.6% more film mass, 36.6% greater area-weighted thickness, and 36.3% greater area-weighted speed; maximum thickness is 8.6% lower and reconstructed coverage is 0.50% higher |
|  | It therefore does not end in the same distribution as E2.7, despite its similar early fast-branch state |
| final film elapsed time | is `0.04516 s`, 1.505 times E2.7's `0.03000 s` for 3,000 fixed steps |
| final maximum film Courant | is `0.1366`; no FPE, AMG divergence, nonfinite, or fatal-event flags were recorded on the selected recovery path |
| — | These flags and endpoint values do not establish convergence |

### Core evidence figures

| Item | Core evidence figures |
| --- | --- |
| [Film response](figures/film-response.svg) | shows the per-iteration film mass, maximum and area-weighted thickness, area-weighted and maximum speed, Film Coverage report, film Courant, and elapsed film time |
| E2.7 matched reference lines | are shown for monitor fields with a native E2.7 monitor |
| [Wall area by thickness](figures/wet-area-by-thickness.svg) | shows five cumulative `area >= thickness` curves and six disjoint thickness bands at each paired 250-iteration checkpoint |
| [Numerical health and transfer](figures/ewf-numerical-health.svg) | shows EWF `h/u/v` residual maxima, maximum film Courant, timestep, and cumulative film outflow |
| Phase-2 absorber, outlet, and closure signals | are included in the [per-iteration report CSV](../../../../../PyAnsys/output/phase72a_ewf_direct_e28_20260926T010700Z/e28-per-iteration-history.csv), but they are not plotted in this EWF-focused figure |

### Decision use and claim limit

| Item | Decision use and claim limit |
| --- | --- |
| — | The aggressive adaptive profile reached an E2.7-like state at native 7000, but the EWF residual stop was not reached in any of its 1,414 updates: all used the three-sub-iteration cap |
|  | The branch then developed nonphysical values: at native 7195, maximum thickness reached `0.11091 m` and area-weighted film speed `73,395 m/s`; maximum CFL reached `4.3616` at 7197 while the timestep collapsed to `9.54e-11 s` |
| branch | was stopped at 7318, and its 318 iterations after the preserved 7000 checkpoint were discarded from the selected trajectory |
| — | During the fixed-step recovery, 230 of 1,586 updates ended with the last captured `h/u/v` residuals all at or below the configured `1e-5` stop, while 1,551 updates reached the 10-sub-iteration cap |
|  | The largest selected-path residuals occurred at native 7395 (`h=2.01e5`, `u=2.23e5`, `v=1.71e3`) |

<details>
<summary>Supporting detail — Decision use and claim limit</summary>

| Item | Decision use and claim limit |
| --- | --- |
| — | The flow residuals and film monitors remained finite, but this does not establish steady film convergence |
|  | The combined controls cannot identify which changed setting drove the transient response |
| E2.8 | is an exploratory numerical speed screen; it cannot establish stationarity, drainage, source-inclusive closure, or physical carryover benefit |
| complete analysis bundle | is linked from the [E2.8 result](../results.md#e28--adaptive-speed-screen-with-fixed-step-recovery--2026-09-26), including the per-iteration CSV, checkpoint area table, run/recovery manifests, transcripts, and response figures |

</details>
