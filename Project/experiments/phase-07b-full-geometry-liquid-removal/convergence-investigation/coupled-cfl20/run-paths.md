# E5 execution map

- Run: `p7b-s40-t020-coupled-cfl20-20260922T202845Z`.
- Setup: [scientific contract](setup.md).
- Local machine evidence: `PyAnsys/output/p7b-s40-t020-coupled-cfl20-20260922T202845Z/`.
- Worker specification/receipt/log: `PyAnsys/output/phase07b-convergence-investigation/e5/`.
- Runner uses the proven E4 path with `--coupled-flow-courant 20`; all changed controls, source/settings parity, save/reopen and exact N0 geometry/field evidence must pass before solve.
- E4 final pair is preserved and restored after G4 graphics. The runner preserves it again before loading the original clean N0 parent.
- Absolute N5000 cap, N50/every500/final pairs, all scalar/flux/residual/source-lag and scheduled/event cell diagnostics. N5000 is the final pair.
- Supervise only the existing controller; no duplicate launch or second client while advancing. Use the file-only running auditor for progress.
- The E5 wrapper uses correct section `index.json` requirements; E4's completion-path reconciliation must not be rerun for E5.
- At terminal disposition compare E4 versus E5, complete G5 numerical/spatial evidence and select the next supported contrast under the autonomous plan.

E5 completed N5000; G5 recording and native QA passed. Its final pair is preserved/restored. See [results](results.md). Do not relaunch this controller. E6 is the selected follow-up.
