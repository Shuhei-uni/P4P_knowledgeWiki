# Stage 4 — Startup method and settings envelope

| Item | Human-selected intent |
| --- | --- |
| Direction | Use the Stage 3 startup sequence while exploring EWF settings and wall parameters |
| Current readiness | Startup method framed; exact next-case configuration not yet selected; no new run submitted |
| Startup reference | [Stage 3 early-EWF startup](../stage-03-shortened-reconstruction/early-ewf-startup/setup.md) |
| Development reference | [Stage 3 film-development method](../stage-03-shortened-reconstruction/early-ewf-startup/film-development/setup.md) |
| Completed Stage 4 evidence | [Commercial-steel continuation setup](commercial-steel/setup.md) and [result](commercial-steel/results.md) |
| New-startup parent | Select and verify a low-feed pre-activation case/data pair; Stage 3 historical A is the method reference |
| N29815 role | Preserved completed continuation endpoint; not selected as the new low-feed startup parent |
| EWF and wall settings | May differ substantially from Stage 3; record actual values before each case |
| Other model scope | Retain the existing Stage 3 geometry/mesh and model basis unless the human changes that scope |

| Step | Method to retain | Details to select / verify |
| --- | --- | --- |
| 1. Prepare low inlet loading | Develop or reuse verified low-feed bulk fields before activation | Exact paired parent, inlet commands, solver state and applied model settings |
| 2. Activate Coupled and EWF | Enable the intended carrier/film configuration at low loading | Selected EWF equations, sources, wall models, coupling and one-time film initialization; preserve verified bulk fields |
| 3. Hold low loading | Allow the activated model to respond before the ramp | Hold length and evidence coverage |
| 4. Ramp both inlets | Increase liquid and vapor feed to full target loading | Ramp duration, command update interval and readback |
| 5. Hold full loading | Check the full-feed response before longer film development | Hold length; bulk inventory, outlet routing, film transfers and continuity |
| 6. Save the full-feed state | Preserve the bulk and film fields after the short full-loading hold | Paired checkpoint; active equation readback; actual film clock |
| 7. Advance EWF only | Freeze bulk equation advancement; retain the established flow fields and advance film in its own time | Keep EWF active; retain film fields/clock; qualify timestep and monitor film inventory, accretion, drainage and numerical behaviour |

| Stage 3 example — method reference only | Recorded value |
| --- | --- |
| Low-feed fraction | 25% of full liquid and vapor feed |
| Activation coordinate | Historical A, N1580 |
| Low-feed hold | 500 updates |
| Ramp | 2000 updates |
| Full-feed hold | 1000 updates |
| Full liquid / vapor feed | 116.92 / 80.69 kg/s |
| Stage 4 scheduling | Preserve the sequence; the above values are not yet a fixed Stage 4 run specification |

| Configurable family | Stage 4 handling |
| --- | --- |
| EWF physical settings | Select, read back and record per case; no blanket inheritance of Stage 3 values |
| Wall parameters | Select and record per case; 0.045 mm is a tested reference, not a frozen value for every future contrast |
| Film numerics | Qualify accepted steps and solver behaviour for each selected configuration |
| Bulk advancement | Active through startup, ramp and short full-feed hold; frozen for the subsequent EWF-only development |
| Full-model qualification | A separate full-bulk check is required before claiming a stationary coupled separator; not part of the selected EWF-only development step |
| Parent preservation | Save the previous valuable endpoint before replacement; keep bulk/film initialization explicit |
| Run placement | Select from the current fleet when execution is requested; other active stages retain their own session authority |
| Checkpoints | Local Fluent machine; verified start/final pairs may be shared through OneDrive |

| Required diagnostic | Definition / use |
| --- | --- |
| Bulk liquid inventory | Native phase-2 mass through full-feed hold; held bulk-field value during EWF-only development |
| Phase-2 steamoutlet flux | Signed boundary flux through full-feed hold; held bulk-field value during EWF-only development; user-source terms separate |
| EWF liquid inventory | Native film mass with explicit wall/report scope |
| Film accretion and drainage | Native accretion rate; drainage from cumulative outflow and actual film step |
| Continuity | Native scaled residual through the full-feed hold; no new continuity solves during the EWF-only segment |
| Numerical/accounting evidence | Film clock, accepted steps, Courant, inner residual availability, source terms and paired restart proof |
| Primary comparison | The five requested histories; mark low hold, activation, ramp, full hold and development |
| Claim limit | Low residuals or lower outlet flux alone do not establish steady film, whole-system closure or improved physical separation |

| EWF-only transition — human direction, 7 October 2026 | Requirement |
| --- | --- |
| Timing | After holding briefly at full inlet loading |
| Bulk fields | Freeze equation advancement without reinitializing stored bulk fields |
| Film fields and clock | Continue the developed film without resetting it |
| Meaning of transient film | Advance native EWF time under fixed bulk forcing; do not infer a globally transient bulk solver requirement from the chat title |
| Stage 3 implementation reference | drift, flow, ke and mp were disabled; inspect the new case's active equation tree before applying its freeze |
| Controls to record | Bulk equation state, active film equations, physical coupling, source treatment and accepted film step |
| Primary evolving diagnostics | EWF inventory, accretion, drainage, storage and film numerical evidence |
| Frozen diagnostics | Bulk inventory and boundary flux may remain fixed; continuity is the last solved value, not a new residual history |
| Scientific conclusion | Film development or film stationarity under the saved bulk flow; not full-system stationarity or reciprocal flow response |
| User-nominated reference | [Solve EWF Transiently](chatgpt-conversation://6ac5733b-48a4-83ec-9e11-23e6902b1d24) |
| Reference access | Conversation content not retrieved: no read_thread tool available in this session; no unverified settings imported |
