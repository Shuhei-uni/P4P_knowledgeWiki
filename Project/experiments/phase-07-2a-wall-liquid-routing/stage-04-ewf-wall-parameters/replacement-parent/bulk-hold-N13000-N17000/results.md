# N13000 → N17000 — conservative bulk hold

| Item | State / evidence |
| --- | --- |
| Execution | **COMPLETE**; one Fluent-owned `/solve/iterate 4000` command; 4,000 complete bulk residual and accepted film-clock rows |
| Startup proof | Passive native residual stream reached N13001 at 2026-10-08T05:55:36.742722+00:00 |
| Last verified endpoint | N17000 / film clock 0.009641999999999292 s; paired hashes verified and final data reopened |
| Target | N17000; expected +4 ms film time |
| Bulk / film | Bulk active; fixed 1 µs, full momentum; required EWF/Phase Accretion and retained film mechanisms ON; Flow Momentum Coupling OFF |
| Checkpoints | Paired case/data every 1,000 iterations, local Server 1 disk; controls read back |
| Output folder | `C:/Users/syok443/Documents/FluentRuns/Phase72A/Stage4/replacement-20261008/bulk-N13000-N17000` |
| Terminal output | Final N17000 pair, transcript, native reports, residual XY and returned marker |
| Laptop dependency | None for continued solve; keep Server 1 and Fluent running |
| Continuation evidence | [Completed N9000 → N13000 hold](../bulk-hold-4000/results.md): final 500 bulk liquid +0.54%, contact removal −11.4%, outlet outward liquid +4.57% |
| Run contract | [Setup](setup.md) |
| Machine evidence | [Block manifest](../../../../../../PyAnsys/output/phase72a-stage4-replacement/20261008/bulk-N13000-N17000/run-manifest.json), [journal](../../../../../../PyAnsys/output/phase72a-stage4-replacement/20261008/bulk-N13000-N17000/native-run.jou), [startup receipt](../../../../../../PyAnsys/output/phase72a-stage4-replacement/20261008/continuation-startup-monitor.json) |
| Completion / subsequent direction | Endpoint preserved. Bulk liquid 48.5188 → 52.3113 kg (+7.82%); film 0.360477 → 0.659845 kg; actual outward outlet liquid 0.772391 → 1.07831 kg/s. Final two 500-window bulk means differ by 0.957%; no stable-bulk claim. Human selected a new staged run from the original N8000 pair. |
| Numerical evidence | Peak Courant 0.001715993; original reported-rate film ledger error 0.391025%; missing achieved inner residuals/event accounting remain claim limits |
| Analysis | [Source/analysis summary](../../../../../../PyAnsys/output/phase72a-stage4-replacement/20261008/bulk-N13000-N17000/analysis-summary.json) |
| Retrieval limit | Native output retrieval uses Fluent connection; no independent host-file route is available if that connection fails |
