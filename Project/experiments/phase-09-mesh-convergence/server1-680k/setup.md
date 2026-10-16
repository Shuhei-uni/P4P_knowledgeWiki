# Server 1 / 680k — EWF Plan v1 implementation

| Setting group | Controlled change / retained value |
| --- | --- |
| Bulk fields and solver | Retain selected N9080 fields, Mixture / RNG / Coupled, existing collector mass/momentum hooks and full feed: liquid 116.92 kg/s; vapor 80.69 kg/s |
| Film physics | Retain full momentum, gravity, gas shear, wall viscosity, pressure, spreading, advection, phase accretion, DPM collection/splash, stripping and separation |
| Film numerics | Sequential mass/momentum; original first-order implicit; first-order spatial schemes; 100 subiterations; stop 1e-5 |
| Surface tension | Film 0.04041 N/m; retain approved bulk coefficient (native serialization 0.04041000083088875 N/m) |
| Curvature smoothing | ON; level 2; factor 0.5 |
| Lower film storage | Enable EWF on mapped lower collector wall `wall:004`; allocate dry storage and restore saved production data; preserve main-wall film facets |
| Direct drain | Lower-film mass sink with matching XYZ momentum removal; 1.5 ms capture time; 1% source-depletion limiter; existing bulk collector retained |
| Update cadence | One film update per native iteration; profile refresh each update; particle update every 20 µs of film time |
| Film stepping | Current section retains 1 µs. Human-selected next section: 10,000 updates at 2.5 µs, then retain 5 µs to 200 ms. Adaptive stepping OFF; native EWF `solution-options` callback applies each changed fixed step; drain refresh span follows the step. |
| Unchanged thresholds | Small film 1e-8 m; maximum thickness 1 m |
| Checkpoint storage | Server-local paired autosave every 1,000 updates; native transcript and paired endpoint for each stage |
| Gates | Numerical acceptance limits are disabled by human instruction, 12 October 2026. Record Courant, film-balance discrepancy and direct-removal diagnostics without stopping. Stop on solver/command errors, nonfinite values, missing checkpoints or inconsistent native time/settings. Retain the physical drain model and solver settings. |


| Current continuation | Selected value |
| --- | --- |
| Authority | Human: next run at 2.5 µs, then step up to 5 µs; numerical acceptance limits disabled. A verified frozen-bulk endpoint at 195 ms is sufficient; the bulk-active extension to 200 ms is a bonus. |
| Preserved current section | N67580 / 82.5 ms → N77580 / 92.5 ms; 10,000 updates at 1 µs. Do not interrupt its native journal. |
| Next section | 10,000 updates at 2.5 µs → N87580 / 117.5 ms. |
| Later step | Retain 5 µs through the frozen interval to 195 ms and the bulk-active interval to 200 ms. |
| Physical update cadence | DPM every 8 updates at 2.5 µs, then every 4 at 5 µs; both retain 20 µs. Drain refresh span follows the selected film step. |
| Sufficient completion | N103080 / 195 ms with bulk equations frozen; preserve the verified paired checkpoint and diagnostics. |
| Bonus endpoint | N104080 / 200 ms; all bulk equations active for 195–200 ms. This is a sensitivity stage, not a requirement for completion at 195 ms. |

| Remaining section | Bulk equations | Film step | Updates | Endpoint |
| --- | --- | ---: | ---: | --- |
| Finish current accepted command | Frozen | 1 µs | Current 10,000-update section | N77580 / 92.5 ms |
| Next section | Frozen | 2.5 µs | 10,000 | N87580 / 117.5 ms |
| Apply 5 µs step | Frozen | 5 µs | 1,000 | N88580 / 122.5 ms |
| Main development | Frozen | 5 µs | 10,000 | N98580 / 172.5 ms |
| Finish frozen interval | Frozen | 5 µs | 4,500 | N103080 / 195 ms |
| Optional bulk-reactivation bonus | All active | 5 µs | 1,000 | N104080 / 200 ms |
| **Required total after current section** | — | — | **25,500** | **195 ms** |
| **Total including bonus** | — | — | **26,500** | **200 ms** |

| Execution control | Requirement |
| --- | --- |
| Automatic handoff | Server-local file monitor waits for the current journal to finish and its paired endpoint to be hashed in the run manifest. It then stops only the exact Python command owner, reconciles the saved endpoint while Fluent is idle, and starts the reviewed ramp controller. |
| Ownership | Keep the active command untouched. The boundary monitor holds a handle to the exact controller process; the replacement holds the existing exclusive solver-writer lock. Supersede the old file-only fallback to prevent conflicting continuation. |
| Numerical diagnostics | Courant and film-balance discrepancies are recorded without acceptance stops. Native solver/command errors, nonfinite values, inconsistent native time/settings, or missing/corrupt files remain errors. |
| Checkpoints | Server-local paired autosaves every 1,000 updates; paired endpoints and transcripts for each section. |
| Boundary proof | Exact N77580 / 92.5 ms, current-pair hashes, native transcript, frozen bulk preservation against the preceding pair, and paired reopen. Do not replay the completed solve. |
| Completion evidence | Exact N103080 / 195 ms, bulk equations frozen, saved paired checkpoint and hashes, native iteration/film-clock evidence and recorded diagnostics. This establishes the selected development endpoint, not steady film or whole-separator closure. |
| Bonus evidence | If completed: exact N104080 / 200 ms, all bulk equations active, paired hashes, save/reopen and selected shared-pair hashes. Preserve the 195 ms endpoint separately; an error in the bonus does not invalidate that healthy endpoint. Leave Fluent open. |
| Queue receipt | `PyAnsys/output/phase9-ewf-server1-680k/20261009/step-ramp-continuation-launch.json` |

| Machine implementation | Owner |
| --- | --- |
| Setup | [Apply settings](../../../../PyAnsys/scripts/setup/apply_phase9_server1_680k_ewf.py) |
| Native controller | [Run](../../../../PyAnsys/scripts/setup/run_phase9_server1_680k_ewf.py) |
| Evidence root | `PyAnsys/output/phase9-ewf-server1-680k/20261009/` |
| Server-local root | `C:\Users\syok443\Documents\FluentRuns\Phase9-Server1-680k\20261009` |
