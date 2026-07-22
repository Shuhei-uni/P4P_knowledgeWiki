# Setup Reports

Reports are numerical findings tied to one concrete setup. Keep the setup definition and the result interpretation separate so a setup can be reused while different runs or post-processing reports accumulate against it.

## Current reports

- [08 family — Inlet-loading comparison](08/velocity-family-comparison.md)
- [04 — Mixed wet-half actual-area results](04/results.md)
- [07 — Pure-phase split actual-area results](07/results.md)
- [08b — Purnanto parity split-inlet results](08b/results.md)
- [08c — Preliminary inlet-loading sensitivity results](08c/results.md)
- [09a — Deterministic DPM carryover results](09a/results.md)
- [09b — Stochastic DPM sensitivity results](09b/results.md)
- [09c — Preliminary two-way coupling results](09c/results.md)
- [10a — Preliminary EWF/splash-sensitive results](10a/results.md)
- [010V2a — Preliminary EWF splash diagnostic](010V2a/results.md)

## Report naming rule

Use `Setups/reports/<setup-id>/` for all reports tied to a setup. Start with `results.md`. Add separate files only when the report becomes too large or when a technical extraction, mesh study, or validation comparison needs its own evidence record.

Every report must link back to exactly one setup definition.

The explicitly labelled family-comparison companion under `08/` is an exception: it links the parent `08b` setup and its two `08c` child cases without replacing the individual setup reports.
