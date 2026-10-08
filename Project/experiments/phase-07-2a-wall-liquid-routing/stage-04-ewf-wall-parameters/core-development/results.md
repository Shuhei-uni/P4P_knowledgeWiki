# Stage 4 — Reduced-report film continuation

| Decision | Current state |
| --- | --- |
| Status | SUBMITTED_NATIVE: N43483 → N48483; +5,000 updates / +50 ms. Target is pending; no terminal result claimed. |
| Question / setup | [Full-momentum +50 ms development](setup.md) |
| Selected parent | Preserved N43483 / 0.4081843386354826 s |
| Target | N48483 / expected film clock 0.4581843386354826 s; verify accepted clock and count at capture |
| Selected diagnostics | 17 essential per-update reports; physics and 10 µs / 20-film-step DPM controls retained |
| Restart proof | Original parent hashes verified; prepared child saved/reopened; geometry-matched film fields exactly equal; bulk, wall, model and source controls retained; no initialization |
| Preserved sibling | Cadence40 N42503 case/data retained and hash/reopen verified before replacement |
| Native execution | Fluent-owned journal; all recorded Courant and thickness samples checked at each 1,000-update interval; native autosave at 5,000 updates; local paired endpoint on horizon or rejection, plus transcript |
| Live observation | Passive transcript returned no new text; bounded Settings status query timed out after 12 s at 01:43 UTC. Current count is unresolved; do not infer a stopped solve or submit a duplicate. |
| Accuracy boundary | Earlier 20 ms control has 1.59% reported-rate discrepancy and positive storage; independent DPM event mass and achieved inner residuals remain unavailable |
| Inner-solve evidence | Selected alternative implicit route printed film clocks without h/u/v sub-iteration histories in the earlier [Stage 3 test](../../stage-03-shortened-reconstruction/early-ewf-startup/film-development/results.md). Current 30 / 10⁻⁵ controls do not prove achieved convergence or a useful iteration-reduction speed gain. |
| Next action | Observe the native job passively; capture terminal pair and histories; assess clock/count, stability, routing, original ledger and timing before further extension |

| Machine evidence owner | Link / state |
| --- | --- |
| Current native job | [Continuation manifest](../../../../../PyAnsys/output/phase72a-stage4-core-development/20261008/core17/run-manifest.json); owns server paths, paired hashes, preparation proof and active target |
| Active block | [N43483 → N48483 native job](../../../../../PyAnsys/output/phase72a-stage4-core-development/20261008/core17/run-N43483-N48483); submitted 2026-10-08 01:39:44 UTC |
| Performance selection | [Matched report-cost result](../report-cost/results.md): 29.52% lower solve time with identical common histories and geometry-matched film arrays in the +10 ms test |
| Coupling selection | [Cadence result](../dpm-cadence/results.md): retain 20 film updates per DPM tracking step; no ledger correction |
