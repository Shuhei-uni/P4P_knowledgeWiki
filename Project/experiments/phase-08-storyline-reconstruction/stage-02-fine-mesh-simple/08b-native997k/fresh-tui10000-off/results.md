# Stage 2 — fresh 08b settings on new 997k mesh, absorber OFF

| Item | Evidence / state |
| --- | --- |
| Preparation | Fresh Hybrid initialization; paired N0 saved and reopened; original 08b settings retained; absorber OFF |
| Requested horizon | 10,000 native carrier iterations from N0 |
| Execution | Native `/solve/iterate 10000` was launched on Server 2. Latest check: Fluent endpoint is unreachable; current run outcome is unconfirmed. |
| Confirmed progress | Native iterations 1–5 captured; no fatal error in this startup capture. Later progress is not yet checked. |
| Saving | Paired local checkpoints every 1,000 iterations; all retained |
| Laptop dependency | None for solve, autosave, final save or host verification; journal and detached controller run on Windows |
| Completion | Unconfirmed. Transcript RPC returned `UNAVAILABLE`; the configured Fluent TCP port timed out. Windows remains reachable on SMB/RDP ports. Terminal solver log and checkpoint list could not be read. |
| Previous attempt | [Transferred-field failure](../run2000-off/results.md); a separate starting field and horizon |

| Record | Location |
| --- | --- |
| Preparation / save-reopen audit | [Build](../../../../../../PyAnsys/output/phase8-stage2/20261007/08b-native997k/fresh-tui10000-off/build.json) |
| Latest connection check | [Receipt](../../../../../../PyAnsys/output/phase8-stage2/20261007/08b-native997k/fresh-tui10000-off/connection-check-20261007T074724Z.json) |
| Host launch | [Receipt](../../../../../../PyAnsys/output/phase8-stage2/20261007/08b-native997k/fresh-tui10000-off/host-launch.json) |
| Native startup proof | [Progress](../../../../../../PyAnsys/output/phase8-stage2/20261007/08b-native997k/fresh-tui10000-off/launch-native-progress.json), [captured transcript](../../../../../../PyAnsys/output/phase8-stage2/20261007/08b-native997k/fresh-tui10000-off/raw/passive-launch-native.txt) |
| Windows working folder | `C:\Users\syok443\Documents\FluentRuns\Phase8\Stage2\20261007\08b-native997k\fresh-tui10000-off` |
| Native transcript | `raw\native-run.trn` within the Windows working folder |
| Checkpoints | `autosaves\checkpoint…cas.h5` and matching `.dat.h5` within the Windows working folder |
| Host status | `run-manifest.json` and `job-manifest.json` within the Windows working folder |

[Run contract](setup.md)
