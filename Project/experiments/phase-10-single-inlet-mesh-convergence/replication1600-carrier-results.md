# R1600 — provisional M04 carrier stage

| Item | Verified result | Limit |
| --- | --- | --- |
| Run | `replication1600-M04-9717fb9b`; M04, 946,967 cells | Provisional recovered carrier setup; full historical spiral settings parity remains unverified |
| Horizon | 1500 new carrier updates: smoke 1, then 1000 and 499 | Matches historical carrier horizon; not convergence proof |
| Native errors | No FPE or AMG-divergence event in the three solve transcripts | Startup viscosity clipping and outlet backflow remain in raw evidence |
| Endpoint | N1500 paired case/data retained on the Fluent computer | DPM has not been tracked |
| Checkpoints | N0, N1, N1001 and N1500; all eight files rehashed; strict reopen/settings checks passed | Fresh starts and checkpoint reads add no solved updates |
| Native state | Owned controller 34176 exited; Fluent idle at N1500; exact recovered OFF carrier settings read back | Other owners' sessions untouched |
| Mesh identity | Saved endpoint has 946,967 cells and 2,385,385 referenced nodes | Delivered mesh has unused vertices; prior mesh-transfer proof owns that normalization |
| Histories | 150 report samples per definition; 1500 residual rows; only identical segment overlaps removed | No interpolated gaps or sample-index axes |
| Solve time | 2520.5 s, about 42.0 min, excluding saves/reopens/retrieval | Not a matched-hardware speedup comparison |
| Qualification | **Unqualified** | Conservation, inventory and active residual criteria do not all pass |
| Replication expectation | Human expects continuity nonconvergence in the historical N1500 method | Continuity alone does not reject or stop the replication; inventory and flux observations remain reported independently |

![Native residual, liquid inventory and phase flux evidence](../../../PyAnsys/output/phase10-single-inlet-mesh-convergence/replication1600-M04/carrier-evidence/carrier-evidence.png)

Shading marks the final-500 interval. Raw residual rows use N1001–N1500; ten-update report samples use N1010–N1500. Inventory endpoint change uses N1000–N1500.

| Final-window observation | Value | Recorded criterion / outcome |
| --- | ---: | --- |
| Liquid inventory, N1000 | 114.193 kg | Window starting value |
| Liquid inventory, N1500 | 217.988 kg | Window ending value |
| Liquid inventory change | +90.895% | <=1%; fails |
| Steam mean absolute flux error / inlet | 0.859% | Maximum 0.946%; <=1%, passes this gate only |
| Liquid mean absolute flux error / inlet | 91.120% | Maximum 95.880%; <=1%, fails |
| Mixture mean absolute flux error / inlet | 53.562% | Maximum 56.360%; <=1%, fails |
| Continuity residual, N1500 | 0.23252 | <=0.0001; fails |

| Evidence owner | Content |
| --- | --- |
| [Native terminal proof](../../../PyAnsys/output/phase10-single-inlet-mesh-convergence/replication1600-M04/carrier-evidence/terminal-proof.json) | Live idle/settings checks, process exit, eight pair hashes, native code identity and 22 text-file copies |
| [Analysis summary](../../../PyAnsys/output/phase10-single-inlet-mesh-convergence/replication1600-M04/carrier-evidence/summary.json) | Exact window definitions, phase errors, inventory, residual criteria and timing |
| [Residual rows](../../../PyAnsys/output/phase10-single-inlet-mesh-convergence/replication1600-M04/carrier-evidence/residual-history.csv) | Native N1–N1500 residual values |
| [Raw evidence](../../../PyAnsys/output/phase10-single-inlet-mesh-convergence/replication1600-M04/carrier-evidence/raw/) | Immutable native manifests, settings, transcripts and report histories |
| [Verification repair](../../../PyAnsys/output/phase10-single-inlet-mesh-convergence/replication1600-M04/carrier-evidence/verification-repair.json) | Original verification errors; Windows CRLF/LF-only source normalization proved; helper escaping repaired; zero extra solver updates |

| Remaining work | Current decision |
| --- | --- |
| DPM source gap | Original `liquid-water` properties and global tracking controls remain unverified; exact nine injection objects alone are insufficient |
| Manual source action | Find `baseline_spiral_inlet.cas.h5` or a Case 4 pair from `spiral_enthalpy_sweep_20260725` on the PC; recover the exact parent settings |
| Follow-up enthalpies | 1440, 1520, 1680 and 1760 remain conditional candidates; none launched while source-setting parity is unresolved |
| Campaign spend | 24369–25059 of 35000 carrier updates; 9941–10631 remain; no budget reset |
| Claim boundary | Technical completion only; no carrier convergence, DPM result, exact replication, mesh independence or improved-mesh claim |
| Interpretation | Consequential scientific interpretation remains with the designated Astra planner; no cross-chat message sent |
| Schedule | Queue awaits source evidence; no pause requested or claimed. `automation_update` unavailable; any required later pause must be done manually in Codex Automations |
