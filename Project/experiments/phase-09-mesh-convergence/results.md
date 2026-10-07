# Phase 9 — Current evidence

| Question | Current result |
| --- | --- |
| Phase started | Human envelope recorded; input audit complete |
| Meshes solved under Phase 9 | 60k low-feed smoke check passed at N1600; 34 complete report histories; paired reopen verified; 60k campaign running from preserved N1600; low-feed hold submitted to N2080; native iteration progress verified in live transcript |
| Common template | Provisional Stage 4 settings; low-feed A bulk fields unchanged; dry film; save/reopen passed |
| 342k collector mapping | Native cell split and entry/wall topology verified; legacy replacement input saved |
| Transfer failure | Native Replace Mesh crashed Fluent with SIGSEGV; scientific experiment untested |
| Server 3 connection | User restarted Fluent; new configured endpoint connected to Fluent 2025 R2 |
| Retry status | Original E2.7 parent replacement passed; six DPM injections restored; provisional Stage 4 settings applied; save/reopen and native 342,609-cell verification passed |
| Previous Server 3 state | N5180 case/data preserved locally with hashes |
| Mesh files | All five readable; exact counts and hashes recorded |
| Coordinate scale | 342k file uses metre-sized coordinates; other four use millimetre-sized coordinates |
| Wall identity | Fine meshes split original wall into vessel/inlet components; physical mapping required |
| Native mesh scale/quality | 342k: metre extents and native mesh check passed; other meshes pending |
| Current action | Continue 60k low-feed hold, ramp and full-feed hold; then 342k, 680k, 997k and 2.6M through the same endpoint boundary |
| Approved retained controls | Two smoothing passes, current reference values and current DPM tracking controls; no separate tracking pass |
| Bulk correction proof | Corrected common source and 342k saved/reopened with surface tension ON at exact 08b coefficient, compressibility flag ON and drag-modification flag ON |
| Legacy interaction | Human approved stored `none` as an inactive Mixture legacy exception |
| Session interruption | Temporary no-solve model-switch probe stopped Fluent; paired endpoints preserved; no exit command sent |
| Claim limit | Input audit is not solver verification or mesh convergence |

| Mesh label | Actual fluid cells | File nodes | Low-feed hold updates | Ramp updates | Minimum full-feed hold updates |
| --- | ---: | ---: | ---: | ---: | ---: |
| 60k | 60,964 | 233,698 | 500 | 2000 | 1000 |
| 342k | 342,609 | 1,077,053 | 1000 | 2000 | 2000 |
| 680k | 679,970 | 1,764,797 | 1500 | 2000 | 3000 |
| 997k | 997,604 | 3,177,646 | 1500 | 2000 | 3000 |
| 2_6M | 2,596,657 | 6,195,886 | 2000 | 2000 | 4000 |

| Evidence | Location |
| --- | --- |
| Mesh identities | [input audit](../../../PyAnsys/output/phase9-mesh-convergence/20261007/mesh-input-audit.json) |
| Parent topology | [parent audit](../../../PyAnsys/output/phase9-mesh-convergence/20261007/parent-mesh-audit.json) |
| Preservation | [Server 3 pair](../../../PyAnsys/output/phase9-mesh-convergence/20261007/server3-preservation.json) |

![Mesh input resolution](figures/mesh-input-resolution.png)

*Source: supplied CFF mesh files. Wall counts use the union of the original wall and newly named vessel/inlet wall zones. Input audit only.*

| Execution evidence | Location |
| --- | --- |
| Source template | [Verified low-feed template](../../../PyAnsys/output/phase9-mesh-convergence/20261007/source-template.json) |
| Failure and recovery state | [Campaign manifest](../../../PyAnsys/output/phase9-mesh-convergence/20261007/campaign-manifest.json) |
| Immutable native crash | [Transfer transcript](../../../PyAnsys/output/phase9-mesh-convergence/20261007/raw/native-replace-crash-342k/342k-transfer.txt) |

| Verification | Outcome |
| --- | --- |
| Python source compilation | Passed |
| Full-feed stability logic | Stable near-zero carryover accepted; inventory drift, missing histories and short windows rejected |
| Native common source | Save/reopen and low-feed bulk-field invariants passed |
| Native 342k geometry/topology | Metre scale, mesh check, collector adjacency and equivalent entry conditions passed |
| Native 342k transfer | Revised ordering passed replacement and injection recovery; child pair and full invariant receipt passed |
| Verification receipt | [Validation](../../../PyAnsys/output/phase9-mesh-convergence/20261007/validation.json) |

| Low-feed smoke check | Verified evidence |
| --- | --- |
| Native horizon | N1580 to N1600; 20 updates completed |
| Accepted film time | 2.0 microseconds; all steps 0.1 microsecond; saved/reopened time agrees |
| Peak film Courant | 9.406721e-8 during the short check |
| Reports | All 34 report histories cover N1581 through N1600 |
| Readback correction | Live Cortex archive held pre-solve clock; controller now uses accepted native transcript time between checkpoints and verifies the clock after paired reopen |
| Proof | [Smoke verification](../../../PyAnsys/output/phase9-mesh-convergence/20261007/60k-smoke-verification.json) |
| Limit | Short implementation check; no steady-film or mesh-convergence claim |

| Local controller | Current proof |
| --- | --- |
| Deployment | 367 files; verified extracted job; [deployment receipt](../../../PyAnsys/output/phase9-mesh-convergence/20261007/host-deployment.json) |
| Disk | 662 GiB free before launch |
| Launch | Prior host worker ended while connecting to old endpoint, before full-run solves; no active host worker remains |
| Desktop recovery route | Desktop controller launched through the working connection; checkpoints and native transcripts stay on Server 3 local disk; desktop must remain running |
| Recovery proof | [N1600 paired reopen](../../../PyAnsys/output/phase9-mesh-convergence/20261007/restart-N1600-reopen.json), [desktop controller](../../../PyAnsys/output/phase9-mesh-convergence/20261007/desktop-controller.json) |
| Session control | No Fluent exit or restart commands; one desktop campaign controller |

| Active campaign | Verified state |
| --- | --- |
| Controller | One desktop process; live native solve progress observed beyond N1600 |
| Active stage | 60k low-feed hold, target N2080 |
| Subsequent stages | 2000-update ramp, full-feed hold; then remaining four meshes |
| Controller dependency | Keep the desktop running; idle-sleep guard is active for the controller lifetime |
| Claim limit | Campaign started; five full-feed endpoints are not yet complete |
