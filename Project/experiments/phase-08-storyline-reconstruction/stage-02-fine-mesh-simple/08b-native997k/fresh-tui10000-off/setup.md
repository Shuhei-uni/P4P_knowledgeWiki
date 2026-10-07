# Stage 2 — fresh 08b settings / new997k, native 10,000 OFF

| Item | Run contract |
| --- | --- |
| Authority | Shuhei: fresh initialization; native TUI solve; laptop may close; updated to10,000 iterations and save every1,000 |
| Mesh | Supplied 997,604-cell mesh; source08b mesh replaced |
| Settings | Original08b physics, materials, boundary values, SIMPLE controls and schemes; first-order k |
| Feed | Full original rates: liquid116.92 kg/s; vapor80.69 kg/s; no ramp |
| Absorber | OFF throughout; no lower absorber cell partition; all phase/mixture cell sources OFF |
| DPM | Original six injection definitions; feedbackOFF |
| Start | Fresh native TUI Hybrid initialization; transferred data discarded; fresh pair saved/reopened atN0 |
| Horizon | 10,000 carrier iterations from freshN0 |
| Native solve | One `/solve/iterate 10000` in server-local journal |
| Checkpoints | Paired case/data autosave every1,000 updates; all checkpoints retained on local Windows disk |
| Endpoint | Native journal writes final case/data; host driver checksN10000, fixedsettings, fields and report coverage |
| Reports | 17 native reports every10 updates; native residual/transcript written on Server2 |
| Session | Server2 only; attach; no Fluent restart, exit or termination |
| Laptop dependency | None for solve, autosave, final save or host verification; detached controller and journal on Server2 |
| Budget | No flow verification updates; exactly10,000 requested carrier iterations |
| Superseded preparation | Unrun2,000-update fresh preparation; same initialized fields; changed horizon/cadence before solve |
| Failure rule | Preserve native logs/checkpoints; no automatic restart or changed trial |
| Claim limit | Numerical viability of this fresh setup; no physicalvalidation, meshindependence or universal impossibility claim |

| Machine record | Location |
| --- | --- |
| Prepared pair / audit | [Build](../../../../../../PyAnsys/output/phase8-stage2/20261007/08b-native997k/fresh-tui10000-off/build.json) |
| Native journal | [Journal](../../../../../../PyAnsys/output/phase8-stage2/20261007/08b-native997k/fresh-tui10000-off/run10000-off.jou) |
| Windows working folder | `C:\Users\syok443\Documents\FluentRuns\Phase8\Stage2\20261007\08b-native997k\fresh-tui10000-off` |
