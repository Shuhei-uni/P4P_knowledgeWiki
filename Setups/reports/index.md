# Setup Reports

Reports are numerical findings tied to one concrete setup. Keep the setup definition and the result interpretation separate so a setup can be reused while different runs or post-processing reports accumulate against it.

## Current reports

- [08 family — Inlet-loading comparison](08/velocity-family-comparison.md)
- [02c — Unprimed brine-outlet pressure sensitivity: Cases A and B early diagnostics](02c/results.md)
- [02c — Future brine-pressure point placeholders](02c/future-runs.md)
- [04 — Mixed wet-half actual-area results](04/results.md)
- [07 — Pure-phase split actual-area results](07/results.md)
- [08b — Purnanto parity split-inlet results](08b/results.md)
- [08b — Mesh-convergence checkpoint, 2026-08-03](08b/mesh-convergence-checkpoint-20260803.md)
- [08c — Preliminary inlet-loading sensitivity results](08c/results.md)
- [09a — Deterministic DPM carryover results](09a/results.md)
- [09b — Stochastic DPM sensitivity results](09b/results.md)
- [09c — Preliminary two-way coupling results](09c/results.md)
- [09cV2 — Skoog partition and injection-control diagnostic results](09cV2/results.md)
- [09cV3 — Fine-mist allocation diagnostic results](09cV3/results.md)
- [09cV3 — DPM-mass allocation quick results](09cV3/dpm-mass-allocation-quick-report.md)
- [10a-splash — Preliminary EWF/splash-sensitive results](10a/results.md)
- [010V2 — EWF deposition and film-inventory diagnostic results](010V2/results.md)
- [010V2a — EWF splash diagnostic results](010V2a/results.md)
- [010V2b — Partial EWF edge-separation diagnostic results](010V2b/results.md)
- [010V2c — EWF particle-stripping diagnostic results](010V2c/results.md)
- [010V2d — Combined EWF-interaction diagnostic results](010V2d/results.md)
- [010V2d-2 — Combined EWF/global-DPM diagnostic results](010V2d-2/results.md)

## Report naming rule

Use `Setups/reports/<setup-id>/` for all reports tied to a setup. Start with `results.md`. Add separate files only when the report becomes too large or when a technical extraction, mesh study, or validation comparison needs its own evidence record.

Every report must link back to exactly one setup definition.

The explicitly labelled family-comparison companion under `08/` is an exception: it links the parent `08b` setup and its two `08c` child cases without replacing the individual setup reports.
