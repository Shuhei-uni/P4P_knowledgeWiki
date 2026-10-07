# Stage 4 — Research basis for the targeted sensitivity

| Observed signal near previous endpoint | Native evidence / inference |
| --- | --- |
| Dominant cycle | Approximately four film steps; 60 microseconds at 15 microseconds per step |
| Signed secondary-phase transfer | Mean 142.76 kg/s; standard deviation 40.40 kg/s |
| Stripping | Mean 63.81 kg/s; standard deviation 40.41 kg/s |
| Film storage | Mean 81.49 kg/s; standard deviation 57.06 kg/s |
| Edge separation / DPM source | Standard deviations 0.511 / 0.169 kg/s; much smaller rapid variation |
| Storage correlation | +0.706 with signed secondary-phase transfer; -0.706 with stripping |
| One-step source lag | corr(secondary[t], stripping[t−1]) = −0.999998; standard deviation of their sum 0.0782 kg/s; delayed source-feedback hypothesis |
| Numerical distinction | Repeated finite sources under frozen bulk; not a bulk residual trace or renewed FPE |
| Longer stripping-only continuation | First Courant >1 at N38317; peak 141.9885 at N38841; final 1.995716; rejected 15–30 ms interval |
| Second hypothesis | Removing stripping suppresses the four-step source loop but exposes a larger momentum/curvature response; test Surface Tension alone from verified N38149 |
| Surface Tension OFF outcome | Rejected: peak Courant 2,746,519, peak film speed 1.16937e9 m/s, thickness reaches 1 m; first Courant >1 occurs at the same N38317 as the ON reference. Surface-tension removal does not stabilize this route. |
| Next controlled hypothesis | Spreading force moves liquid down the film-height gradient; disable Spreading alone from the same N38149 parent, keeping Surface Tension ON |
| Spreading OFF outcome | Rejected: peak Courant 306,903.3 and film thickness reaches 1 m. Removing either of the tested force terms worsens the later numerical excursion. |
| Numerical-method contrast | EWF Coupled Solution OFF alone from original N37149, with stripping and all physical film terms ON. Test the sequential update against the original four-step-cycle control before selecting a compound physical-model removal. |
| Numerical-method result with stripping ON | Four-step cycle persists; source/storage detrended standard deviation rises about 7.7%; peak Courant 0.03396543. Not selected to repair the source variation. |
| Conditional numerical-method test | EWF Coupled Solution OFF alone relative to verified stripping-OFF N38149. Check whether it repairs the later Courant excursion while preserving all force terms. |
| Conditional numerical-method outcome | Peak Courant decreases from 141.9885 to 1.914106, but still exceeds the guard; peak reported film speed 5798.83 m/s and sampled ledger discrepancy 14.87%. Rejected despite finite film inventory. |
| Curvature control | Curvature Smoothing ON alone from the same stripping-OFF N38149 parent; EWF Coupled Solution ON, every force term retained, smoothing level 2 / factor 0.5 and 15 microseconds. |
| Curvature-control outcome | Rejected: peak Courant 643,624.3, peak reported film speed 6.86358e8 m/s, thickness reaches 1 m. This manual-supported control does not stabilize this case at the tested step. |
| Continuation selection | Restore the original stripping-ON / coupled-ON control. No tested OFF route supports the longer check. Reduced short-window variation does not justify continuing a rejected child. |
| Frequency claim limit | Step-locked pattern at one step size; cannot establish a physical wave frequency |
| Exact source window | Previous diagnostics: film time >0.318 s, native iteration <37148; excludes trimmed final step |

| Candidate | Evidence and ranking | Controlled test |
| --- | --- | --- |
| Particle Stripping | First: large periodic film mass removal; coupled mass transfer/source timing is plausible | OFF alone; keep edge separation and accretion ON |
| Surface Tension / curvature | Second: coupled-film curvature force uses previous-step film variables; curvature smoothing is OFF | Surface Tension OFF alone when the longer stripping-OFF check exceeds the Courant guard; no simultaneous pressure or spreading change |
| Implicit step / lagged source update | Competing numerical explanation: four-step pattern and no printed inner residuals | Half-step control with unchanged physical flags if needed |
| Phase Accretion | Source also varies, but removing it changes the principal film supply | Defer until simpler removal/force contrasts distinguish the coupling |
| DPM source smoothing / interval | Source smoothing OFF; film steps per DPM step 20; observed DPM source varies little at four-step frequency | Lower priority; do not alter with stripping switch |
| Edge Separation | Transfer changes slowly in the inspected window | Lower priority; retain ON in first screen |
| Spreading | Film-height-gradient force is another part of the pressure term; surface-tension removal worsens, rather than repairs, the later excursion | OFF alone after restoring Surface Tension ON; compare with same N38149 parent and time interval |
| EWF Coupled Solution | Mass and momentum solved together using previous-step fields | Retain initially; changing it together with physics would confound attribution |

| Fluent 2025 R2 primary source | Relevant finding and transfer limit |
| --- | --- |
| [Film submodels](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_th/flu_th_ewf_sec_film_submodels.html) | Stripping removes film mass above a critical shear threshold; particle creation uses accumulated sources during DPM updates. Stripping/separation can also return mass and momentum to the Eulerian secondary phase. This supplies a coupling hypothesis, not proof of a defect. |
| [Model options](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/flu_ug_ewf_sec_options.html) | Stripping has critical shear and mass/diameter coefficients. Source Smoothing acts on particle impingement distributions. Pressure Gradient is a prerequisite for Surface Tension and Spreading, so disabling pressure would change several terms. |
| [Coupled solution theory](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_th/flu_th_ewf_sec_time_coupl.html) | Parallel film mass/momentum updates use previous-step height/velocity; curvature smoothing is provided for stability. The live case has curvature smoothing OFF. |
| [Film momentum terms](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_th/flu_th_ewf_sec_eqns.html); [model dialog](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/flu_ug_models_task_page.html) | Spreading arises from gravity normal to the wall and drives film toward lower thickness. Its switch can be removed while pressure, tangential gravity and surface tension remain ON. |
| [Solution controls](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/flu_ug_ewf_sec_eqns.html) | Film/DPM update interval and relaxation are separate controls; hold them fixed for the first physical contrast. |
| [Temporal differencing](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_th/flu_th_ewf_sec_time_diff.html) | Implicit film equations require iterative source/field updates; the live alternative implicit route prints no inner convergence history. |
| Local reusable guidance | CFD_wiki/wiki/guidance/fluent-general-click-by-click.md recommends staged activation; its older case values are not imported. |

| Verified live value | Value |
| --- | --- |
| Fluent release | 2025 R2 |
| Stripping critical shear / mass coefficient | 100 Pa / 0.5; inherited |
| Curvature smoothing / source smoothing | OFF / OFF |
| Surface-tension coefficient | 0.07194 N/m in EWF and the active film-compatible particle material; retained in every contrast |
| Film/DPM step interval / relaxation | 20 / 1.0 |
| EWF Coupled Solution / alternative implicit | ON / ON |
| Implementation | First contrast changes only native wall-film/model-parameters film-stripping?; the second changes only surface-tension? from the verified stripping-OFF parent. Retain all other native entries; save/reopen and compare. |

| Additional property issue — not tested by the switch contrast | Evidence and limit |
| --- | --- |
| Recorded pressure | Native outlet gauge pressure 1,120,000 Pa plus operating pressure 0 Pa: 11.2 bar absolute |
| Pure-water reference | [IAPWS surface-tension release, equation and Table 1](https://iapws.org/technical-guidance/release/Surf-H2O.download): approximately 0.07197 N/m at 25°C, 0.04219 at 180°C, and 0.04107 at 185°C |
| Possible mismatch | The inherited 0.07194 N/m is close to room-temperature pure water. If the film represents hot saturated liquid at the recorded pressure, the coefficient needs review. |
| Limit | Film energy is OFF; 185°C is an illustrative property calculation, not a solved film temperature. Actual temperature and brine composition are not established here. No coefficient or DPM property was changed. |
| Machine calculation | [Formula, live inputs and assumptions](../../../../../PyAnsys/output/phase72a-stage4-sensitivity/20261007/property-check.json) |
