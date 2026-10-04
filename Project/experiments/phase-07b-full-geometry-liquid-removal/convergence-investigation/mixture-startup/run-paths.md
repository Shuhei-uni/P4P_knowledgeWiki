# E8 machine map

| Item | E8 machine map |
| --- | --- |
| No active controller. User-stopped and preserved atN128; Phase7b closed. | Final machine receipt `PyAnsys/output/phase07b-convergence-investigation/e8/user-stop-20260929/preserved/receipt.json` and independent audit `PyAnsys/output/phase07b-convergence-investigation/e8/user-stop-20260929/partial-evidence-audit.json` verify idle endpoint, unique pair, complete partial histories and field/section exports |
|  | Fluent was left open; owned pause4 removed |
|  | No restart or further solve is authorized |
| Final case | `C:/Users/qtra338/P4P/experiments/phase-07b-full-geometry-liquid-removal/case-data/p7b-e8-user-stop-n00128-20260929T034907Z.cas.h5` |
|  | Matching data: `C:/Users/qtra338/P4P/experiments/phase-07b-full-geometry-liquid-removal/case-data/p7b-e8-user-stop-n00128-20260929T034907Z.dat.h5` |

<details>
<summary>Supporting detail — E8 machine map</summary>

| Item | E8 machine map |
| --- | --- |
| Final case | Local endpoint evidence: `PyAnsys/output/phase07b-convergence-investigation/e8/user-stop-20260929/preserved/` |
| Retired final controller | `p7b-s40-t020-coupled-nphase-staged-resume50-20260929T034045Z`, formerPID92330; job `PyAnsys/output/phase07b-convergence-investigation/e8/resume-n50/job.yaml` |
|  | Its original raw manifest reflects retirement during the50→200 block; it is not the final scientific disposition |
|  | The user-stop receipt supersedes execution-status claims |
|  | Earlier N50 recovery was unchanged-state preservation after clamshell sleep, with no replay |
|  | Historical originalN0 and recovery evidence remains immutable |
| Retired original zero-solve build | `p7b-s40-t020-coupled-nphase-staged-20260929T030501Z` |
|  | Job: `PyAnsys/output/phase07b-convergence-investigation/e8/job.yaml` |
|  | Local output: `PyAnsys/output/p7b-s40-t020-coupled-nphase-staged-20260929T030501Z` |
|  | No launch or iteration is established by this planned identity; phase-state and job/controller evidence own live status |
| Implementation | `PyAnsys/scripts/setup/run_phase07b_mixture_startup.py`; stage parser/gate verification: `PyAnsys/scripts/setup/test_phase07b_mixture_startup.py`; offline receipt and read-only storage inventory: `PyAnsys/output/phase07b-convergence-investigation/e8/` |
|  | The job wraps the controller with process-lifetime `caffeinate -i`; this cannot prevent lid closure or network loss |
| Fresh prepared N0 parent | `C:/Users/qtra338/P4P/experiments/phase-07b-full-geometry-liquid-removal/case-data/p7b-s40-t020-coupled-cfl20-nphase-20260923T225918Z-prepared.cas.h5/.dat.h5` |
|  | Original N0 fields and ordered geometry are in that original run's `pre-reopen-prepared/` directory |
|  | E6 reference manifest: `PyAnsys/output/p7b-s40-t020-coupled-cfl20-nphase-resume-20260923T231816Z/manifest.json` |
| Preserved E7 predecessor | `PyAnsys/output/p7b-s40-t100-coupled-cfl20-nphase-live3227-resume-20260929T003603Z/manifest.json`, final pair in its `pairs.final`; native G7 comparison restored it before E8 preparation |
|  | E8 creates another unique preserved predecessor pair before loading N0 |
| — | All child case/data, report and native transcript names use the selected unique run identity on the Fluent PC's local Phase7b root; exact paths are persisted in the child manifest |
|  | Never overwrite raw evidence, relaunch an existing job, or attach another Fluent client while it advances |
|  | Reconcile actual native counter and the exact owned pause before any technical recovery |
| No automatic replay or compute-bound expansion | is authorized |

</details>
