# Phase 07 E5-CZ cell-zone recovery family

This follow-on discovery family was approved by the human on 2026-09-10 after
the original fixed-mesh E5 packets were blocked by the absence of
region-specific source binding. It uses Fluent's native split-by-mark
operation to place the frozen `0≤y≤0.10 m` cells into a separate lower fluid
zone, then screens three adaptive native zone-source gains.

The technical split was proven on `student` before this family was recorded:
`3,794` marked lower cells were separated from the `342,609`-cell parent, and
the unsplit/split pairs retained identical solver mesh counts, extents,
volume/face statistics, and mesh-check status. That is implementation
evidence, not E5 performance evidence.

| Setup | Gain | Status |
| --- | ---: | --- |
| [P7-E5-CZ-G025](p7-e5-cz-g025/setup.md) | `0.25` | `COMPLETE_VERIFIED`; full 500-active screen, positive inventory drift, corrected `get_sum` audit |
| [P7-E5-CZ-G050](p7-e5-cz-g050/setup.md) | `0.50` | `COMPLETE_VERIFIED`; recovered from active 250, restart-window package, smallest provisional late inventory slope |
| [P7-E5-CZ-G100](p7-e5-cz-g100/setup.md) | `1.00` | `COMPLETE_VERIFIED`; full 500-active screen, positive inventory drift, nonfatal inherited-path warning |

The complete server-neutral design and evidence contract are in
[design.md](design.md). Patching/reset remains excluded unless the human
explicitly requests that last-ditch route.

The current family-level comparison is provisional: G050 has the smallest
observed late inventory slope (`+0.3256 kg/iteration`), followed by G100
(`+0.3521`) and G025 (`+0.5046`), but G050's evidence is a recovered
`native 748--998` continuation window rather than a fresh full-history trace.
All three screens still show positive inventory drift, very small phase-2
liquid boundary outflow relative to liquid inflow, and an open boundary-only
mixture closure. No member is promoted or qualified.

The human selected one bounded continuation, [P7-E5-CZ-G100-CONT2500](p7-e5-cz-g100-cont2500/setup.md):
continue the unchanged G100 state for `2,000` additional active iterations,
reaching total active `2,500`. It is now `COMPLETE_VERIFIED`; the continuation
retains positive inventory drift, lower-zone rebound, source-cap saturation,
open mixture closure, and an explicit stale runtime-counter limitation. It did
not close the absorber question or authorize a conventional outlet.

The next family is the separate [E5-CZ absorber-control family](../cell-zone-absorber-control-family/index.md),
which changes the feedback basis to lower-zone liquid inventory and varies
only the predeclared source cap at fixed `G=2.00`. Its children are setup
records only and remain `NOT_RUN` until a later launch decision.
