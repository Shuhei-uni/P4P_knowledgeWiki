# Phase 06 discovery campaign — results

Each case is recorded only after terminal execution evidence exists. A case
that lacks required residual/report history or a matching final pair remains
invalid and does not count toward `DISCOVERY_EXECUTION` or
`DISCOVERY_EVIDENCE`.

## Execution-gated campaign status

All six selected cases now pass the independent `DISCOVERY_EXECUTION` gate:
`P6-D01-R`, `P6-D02-R`, `P6-D03-V`, `P6-D04-F`, `P6-D05-F`, and
`P6-D06C-PR`. Each has the canonical F11 parent readback, a prepared-pair
save/reopen, a 50-iteration smoke, 500 discovery iterations, a final-pair
save/reopen, and 30 report histories with 551 samples each.

The originally malformed residual JSON histories were rebuilt directly from
their preserved Fluent transcripts. The repaired histories retain 551 unique
native coordinates (`15000` through `15550`) and seven aligned scaled-residual
curves. Only byte-equivalent repeated chunk-boundary rows were removed:
D01/D02/D03 each remove one, D04/D06C five, and D05 ten. No interpolation,
extrapolation, or solver rerun was used. Independent review re-parsed each
transcript and accepted the reconstruction.

## Predeclared core figures

| Figure | Status | Evidence | Current bounded observation |
|---|---|---|---|
| F1 `pool_proxy_histories` | `UNAVAILABLE` | The required remote report files are not preserved locally; server 2 is reachable but rejects the configured Fluent credential and server 3 is unreachable as of 2026-08-31. | Do not infer pool boundedness from the manifests or D06C chunk-end proxy values. |
| F2 `phase_liquid_balance` | `UNAVAILABLE` | Same missing remote report-history access; the phase-2 flow and balance histories were recorded remotely but not exported locally. | Do not infer conservation/routing behaviour from terminal report counts. |
| F3 `numerical_adequacy` | `COMPLETE` | [F3 scaled residual histories](figures/F3_numerical_adequacy_residuals.png), [machine-readable F3 summary](figures/F3_numerical_adequacy_summary.json), and six transcript-backed residual JSON files. | All six 550-iteration screens retain noisy scaled residual behaviour; D06C's late continuation steps coincide with elevated continuity and phase-fraction activity. This does not establish a physical cause or a converged steady state. |

The discovery campaign therefore remains in `DISCOVERY_ANALYSIS`. The six
execution-gated runs are not sufficient for `DISCOVERY_EVIDENCE` until F1 and
F2 are recovered or a legitimately redesigned discovery strategy produces
their required evidence.

## Valid execution records

### P6-D01-R — fixed brine-outlet pressure, replication

- Status: `COMPLETE`; attached server: `server-2@10.104.145.174`.
- Manifest: `PyAnsys/output/phase06_discovery/20260831/P6-D01-R-20260831T053000Z.manifest.json`.
- Native file-backed proxy report coordinate: 15000 at start, 15050 after
  smoke, 15550 after the 500-iteration discovery screen; smoke-plus-screen
  span is 550.
- Native residual transcript: 552 points, including the smoke and discovery
  coordinates; every required report history contains 551 samples.
- Terminal pair: saved and reopened successfully; terminal verification is
  `PASS`.
- This is execution evidence only. Physical interpretation and any
  discovery-to-hypothesis transition remain gated on the complete campaign,
  planned analysis, and independent verification.
