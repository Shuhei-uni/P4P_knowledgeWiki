# BF01 — M04 implicit body-force ON diagnostic

| Question | Observed result |
| --- | --- |
| Did the ON N3000 restart reach N4000? | No. Native k-equation AMG divergence and floating-point exception at **N3567** |
| Was the selected setting applied? | Primary switch and native expert alias ON; reversible alias proof and full other-state comparison passed |
| New update spend | **567** including the five-update smoke; 433 of the cap unused; no retry selected |
| Last verified pair | **ON N3005**; native hashes recomputed, strict save/reopen proof preserved |
| Solver state | Controller 24124 exited; owned Fluent idle at N3567; failed fields are unqualified |
| Original OFF comparison | Original M04 continuation failed at N3911; its N3000 pair remains the diagnostic parent |
| Scientific limit | ON is a saved-field restart; OFF is the original continuation. Timing alone does not isolate a unique cause; [zero-update reload audit](bf01-diagnosis.md) confirms a restart confound |
| Interpretation owner | Consequential interpretation awaits the designated Astra planner; Sol collected and verified evidence |

![M04 OFF/ON histories](../../../PyAnsys/output/phase10-single-inlet-mesh-convergence/bodyforce-BF01-evidence/off-on-comparison.png)

Raw native coordinates: OFF N3000–N3910; ON reports N3000–N3560 and residuals through N3566. Dotted lines mark native failure coordinates. The speed and continuity panels use log scales and retain the overflow tails. Inventory growth is a recorded observation, not a steady-state or conservation proof.

| Required evidence | Coverage / limit |
| --- | --- |
| Parent case/data, mesh and settings | Native hashes verified; 946967 cells, 2385385 solver nodes; no initialization |
| Controlled delta | Only primary implicit body force and proven native alias; strict ON N3000 and N3005 reopen checks |
| Checkpoints | ON N3000 and N3005 retained; N4000 absent because of failure |
| Native residual transcripts | Preparation, smoke and failed continuation retrieved with hashes; original OFF failure transcript also retained |
| Report histories | Sixteen ON report files retrieved; native ten-update sampling retained |
| Declared final-500 at N4000 | Unavailable: requested endpoint not reached. No substituted qualification window |
| Balance / inventory | Finite pre-threshold ON sample N3460: liquid inventory 947.706 kg and feed deficit 77.9%; this is a diagnostic sample, not a qualified balance |
| Campaign budget | 22869–23559 solved/lost updates including BF01; 35000 cap retained |
| Performance comparison | No speedup claim; failure-block elapsed duration was not persisted in the native manifest |
| Further solves | None selected; preserve baseline failures and skipped M07 |
| Schedule | Native pause unverified: automation_update unavailable. Manual action: pause phase-10 in Codex Automations |

| Artifact | Purpose |
| --- | --- |
| [Terminal verification](../../../PyAnsys/output/phase10-single-inlet-mesh-convergence/bodyforce-BF01-terminal-verification.json) | Failure, spend, ON flags, writer exit and pair proof |
| [Summary](../../../PyAnsys/output/phase10-single-inlet-mesh-convergence/bodyforce-BF01-evidence/summary.json) | Parsed OFF/ON observations and source hashes |
| [Retrieval](../../../PyAnsys/output/phase10-single-inlet-mesh-convergence/bodyforce-BF01-evidence/retrieval.json) | Native/local text provenance |
| [Original diagnosis](divergence-diagnosis-20261011.md) | Earlier baseline failure evidence and unresolved causal alternatives |
