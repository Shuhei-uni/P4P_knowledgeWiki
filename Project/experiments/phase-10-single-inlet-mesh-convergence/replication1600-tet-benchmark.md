# Matched spiral tet runtime benchmark

| Contract | Selected value |
| --- | --- |
| Authority | Human: run the tet mesh again on the current PC and Fluent |
| Question | Compare the fixed-horizon carrier and DPM compute time with M04 at 1600 kJ/kg |
| Tet mesh | Recovered spiral source, 2964593 cells, SHA-256 `b59ffb1a287699e1fd5839294f74258f706d7729e86166e0f17343bf212185e1` |
| Reference | Completed M04 Case 4: 946967 cells; carrier 2520.498806 s; 100000-step-limit DPM 238.757602 s |
| Controlled delta | Tet mesh instead of M04; rename `outlet` to `steamoutlet` and `wall-fluid` to `wall` to preserve report roles |
| Frozen settings | Exact M04 Case 4 carrier physics/numerics, inlet values, nine injection definitions, particle material, forces, fates and global tracking controls |
| Execution | Same owned Fluent 2025 R2 session and PC; double precision, 16 ranks; one native writer |
| Initialization | Fresh Hybrid N0; no developed fields from historical tet or M04 |
| Carrier | 1500 total updates including smoke; blocks 1, 1000 and 499; paired N0/N1/N1001/N1500 checkpoints |
| DPM | One post-carrier update; maximum 100000 steps; step factor 5; identical report accounting |
| Timing | Elapsed carrier iterate and DPM update calls; setup, save/reopen and retrieval excluded from speed ratio |
| Budget | Prior carrier spend 30369–31059; this case allocates 1500 including retries. Terminal no-retry spend 31869–32559 of35000; DPM counted separately |
| Required evidence | Settings and nine-injection parity, mesh identity, source/pair hashes, same session/ranks, checkpoint reopen, residual/history/final-500 records, DPM fates and timing |
| Failure | Preserve error and last verified pair; no blind solve/tracking retry or silent settings change |
| Claim limit | Fixed-horizon cost and output comparison; no time-to-convergence, mesh independence, validation or improved accuracy claim |
| Status | Complete: N1500 carrier and one DPM update; pairs/settings/histories/reports verified; controller8676 exited and Fluent idle; [results](replication1600-tet-results.md) |

| Artifact / planned comparison | Owner |
| --- | --- |
| Job, launch, preparation, checkpoint and terminal receipts | `PyAnsys/output/phase10-single-inlet-mesh-convergence/replication1600-tet-benchmark/` |
| Compute-cost table | Tet/M04 carrier seconds and seconds/update; DPM seconds shown separately |
| Output table | Escaped/trapped/incomplete mass and assumed-capture efficiency for matched 1600 cases |
| Preserved endpoint | Completed M04 1760 tracked pair remains hash verified before any tet load |

| Preparation recovery / timing limit | Evidence |
| --- | --- |
| First tet preparation | Zero carrier and DPM updates; Hybrid completed, then the strict N0 counter check stopped setup. The preserved M04 pair was restored; native error retained under `attempt-01/raw` |
| Counter repair | Clear inherited residual history in the fresh child. A newly initialized counter of0 or1 is accepted only before any carrier command; the smoke must print exactly nativeN1 and reach measuredN1 before long solving |
| API reference | Fluent252 `solution.monitor.residual.reset()`; [version-matched command guide](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/pdf/Ansys_Fluent_Text_Command_List.pdf) |
| DPM setup timing | M04's original1600 carrier preceded injection installation; tet starts with the verified injections present. Both use one-way interaction, and tet tracking is dispatched only afterN1500. Retain this configuration-stage difference with the cost comparison |
| Retry spend | Preparation repair used0 solved carrier updates; no tracking was repeated |
| Saved N0 counter | Fresh Hybrid reports1; reloading its saved N0 pair reports0. The handoff check was repaired; the saved pair was reused without reinitialization. Both zero-update attempts and errors are preserved |
| Native smoke | Exactly one printedN1 carrier row; measuredN1, paired hashes, all settings and serialized injection frames verified on reopen;4.921702 s |

| Initial geometry diagnostic | Tet | M04 | Limit |
| --- | ---: | ---: | --- |
| Fresh N0 vapor mass (kg) |162.102108 |132.140894 |Both liquid masses are0; identical constant vapor density5.797434 kg/m³ |
| Inferred fluid volume (m³) |27.961010 |22.792997 |Mass/density indicates a22.67% volume difference; direct mesh-volume and geometric source audit pending |

*The benchmark continues as the human-selected comparison of these two models. The volume difference prevents a mesh-only causal cost claim. [Diagnostic evidence](../../../PyAnsys/output/phase10-single-inlet-mesh-convergence/replication1600-tet-benchmark/initial-volume-comparison.json).*

| Native execution / completion | Route |
| --- | --- |
| Executed worker |`C:/Users/qtra338/Documents/FluentRuns/Phase10/20261009/replication1600-tet-b888ff6e`; controller8676 completed and exited |
| Startup proof |[N1 and advancing native output](../../../PyAnsys/output/phase10-single-inlet-mesh-convergence/replication1600-tet-benchmark/startup-verification.json) |
| Passive monitor |`PyAnsys/scripts/setup/probe_phase10_native_receipts.py`; current-launch selectsR1600_TET_BENCHMARK; no OS commands through busy Fluent |
| Terminal retrieval |`PyAnsys/scripts/inspection/fetch_phase10_replication_enthalpies.py --tet-benchmark`; only after native terminal and live idle proof |
| Timing / output analysis |`PyAnsys/scripts/analysis/analyze_phase10_replication_tet_benchmark.py` |
| Scheduling block |automation_update unavailable; saved schedule prompt/state cannot be verified or changed. Any continuing Phase10 monitor must use this current selected contract; no schedule activation or pause claimed |
| Required schedule action |If automated checks are desired, manually update the existing Phase10 monitor to read current-launch and this tet contract, with quiet passive checks and in-scope recovery. The native run continues independently of that schedule |
