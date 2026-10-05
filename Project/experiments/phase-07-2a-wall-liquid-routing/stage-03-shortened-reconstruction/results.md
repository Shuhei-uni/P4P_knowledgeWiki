# Stage 3 — Reconstruction result

| Item | Current result |
| --- | --- |
| Status | N1000 bulk checkpoint verified; native idle flag recovered; continuation running |
| Server | Server 3; human-owned for this stage |
| Source files | Case, data and contact-library archive match recorded hashes on Server 3 and local destination |
| Reference | Corrected R3/contact N33586; developed film, not steady-qualified |
| Smoke | N0–N20 completed; all 20 report rows present; zero film inventory |
| Smoke durability | Paired local checkpoint saved, hashed and reopened; state matches |
| Smoke source | Native applied sink `2.0362565 kg/s` matches independent depletion expression at N20 |
| Smoke numerical limit | No fatal/divergence events; reverse flow present; no convergence claim |
| Smoke cost | 81.24 s including evidence collection and checkpoint reopen; not an estimate of long-run solve time |
| Reconstruction solve | First 1000 updates completed on 18 ranks; continuing the same low-loading hold |
| N1000 solve cost | First 980-update main batch: 522.61 s; excludes smoke and checkpoint overhead |
| N1000 recovery | Fluent retained the solve-active UI flag; clearing it restored calculate/iterate without changing native iteration or fields |
| Batch safeguard | Absolute native solve command; verify requested endpoint before clearing any retained active flag |
| Reproduction | Pending full startup, film screens and comparison |
| Recipe and decision rules | [Setup](setup.md) |
| Machine evidence | [Manifest](../../../../PyAnsys/output/phase72a-stage3-server3/20261005/run-manifest.json) |
| Completion and recovery | [Current job manifest](../../../../PyAnsys/output/phase72a-stage3-server3/20261005/service-recovery-job-manifest.json) |
| Chat handoff limit | Earlier CLI return failed: desktop chat already has an active writer; automatic chat return is not verified |
| Reference report reconciliation | Native UDF source is `64.6792 kg/s`; old receipt cached zero. Inventories, boundary-only fluxes and frozen settings match |

| Missing evidence | Effect |
| --- | --- |
| Short-startup histories and endpoints | No reconstruction claim |
| Fixed/adaptive matched-time comparison | No timestep-efficiency claim |
| Source-inclusive and film accounting | No conservation qualification |
| Matched spatial evidence | Scalar agreement alone cannot establish reproduction |
| Measured duration | No startup-cost reduction claim |

| Next action | Scope |
| --- | --- |
| Complete prescribed startup and two film screens; inspect actual native clocks, balances and spatial comparison | Existing mesh and exact reference model |
