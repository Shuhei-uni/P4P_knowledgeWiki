# Stage 4 — Selected EWF mechanisms from N29815

| Contract | Value |
| --- | --- |
| Human authority | 7 October 2026; current-chat settings table and 50 ms EWF-only horizon |
| Question | How do the combined selected film force, feedback and particle mechanisms change the commercial-steel endpoint? |
| Parent | Server 1 loaded commercial-steel N29815; preserve and verify paired local files before changes |
| Parent film time | 0.2691843386355824 s |
| Initialization | No bulk or film initialization; continue stored fields and clock |
| Fixed basis | Existing mesh, phase feeds, materials, contact absorber, film wall scope and 0.045 mm roughness / Cs 0.5; bottom smooth |
| Active film wall | wall; other walls remain outside the EWF domain |
| Workflow | phase-loop; pyansys-workflow implementation |

| Setting | Target |
| --- | --- |
| Pressure Gradient | ON |
| Spreading Term | ON |
| Surface Tension | ON; retain parent coefficient 0.07194 N/m |
| Flow Momentum Coupling | ON on wall |
| Particle Splashing | ON; wall splash enabled |
| Edge Separation | ON; wall boundary separation enabled |
| Particle Stripping | ON |
| DPM Coupling in EWF | ON; retain diagnostic inlet feed and global DPM interaction state |
| Phase Accretion | ON; retain secondary-phase mode 1 |
| Solve Momentum | ON; momentum equation |
| Gravity Force / Surface Shear Force | ON / ON |
| EWF Coupled Solution | ON |
| Unselected film options | Retain parent; no energy, scalar, phase change or added inlet particle loading |
| DPM material prerequisite | Add water-liquid-at-psep-pcle with parent film density/viscosity and film surface-tension coefficient; assign existing diagnostic injections; no feed change |
| Existing coefficients | Retain native stripping and separation parameters; record exact readback |

| Segment | Horizon / controls |
| --- | --- |
| Preparation | Official v252 guide figures + prior TUI code; readback; paired save/reopen; no initialization |
| Bulk and film | 2000 additional iterations, including instrumentation probe; fixed parent 1 microsecond film step |
| Transition | Save endpoint; freeze all originally active bulk equations; retain film fields and clock |
| Film only | Add 0.050 s after transition; aim for 15 microseconds; use smaller step for numerical recovery if required |
| Final step | Trim the final fixed step to reach the 50 ms target within native-clock tolerance |
| Batches | Approximately 1000 updates; local paired checkpoints and native transcripts |
| Recovery | Initial 1 microsecond / inherited bulk controls failed at N29827. Restart N29815 prepared pair; film 0.1 microsecond, original implicit solver, 100 film subiterations; bulk pseudo scale 0.01, pressure/momentum relaxation 0.1, turbulence pseudo relaxation 0.1; selected physics unchanged |

| Evidence / decision | Requirement |
| --- | --- |
| Core histories | Bulk liquid mass; phase-2 steamoutlet signed boundary flux; film mass; accretion and drainage; carrier continuity |
| Additional transfers | Film DPM source; cumulative stripped/separated mass; report definitions and native units |
| Numerical adequacy | Actual film clock and accepted steps; Courant; finite reports and thickness; inner residual availability |
| Film ledger | Storage + drainage + stripping + separation versus accretion + DPM source; record sampling and source timing limits |
| Frozen bulk proof | Equation readback and unchanged bulk fields; last solved continuity labelled |
| Completion | Native +2000 bulk horizon; +50 ms film-only horizon; final paired files and reopen; evidence extracted |
| Comparison | Combined finite-time settings contrast; no isolated attribution to one option |
| Claim limit | Frozen-flow film response; no full-system stationarity, complete conservation or physical-validation claim |

| Reference | Link |
| --- | --- |
| Parent results | [Commercial steel](../commercial-steel/results.md) |
| Model options / Figure 30.1 | [Fluent 2025 R2](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/flu_ug_ewf_sec_options.html) |
| Wall options / Figure 30.9 | [Fluent 2025 R2](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/flu_ug_ewf_sec_bound.html) |
| Machine evidence | [Run output](../../../../../PyAnsys/output/phase72a-stage4-realism/20261007/) |
