# Phase 07 E5-CZ absorber-control family

This directory contains the human-approved discovery experiments for the
intended no-outlet brine-pool abstraction. The original absorber-control
screen starts from the completed G100 active-2,500 state, uses lower-zone
phase-2 inventory as the primary feedback signal, fixes `G=2.00`, and varies
only the bounded source cap. The separate cold-start balance probe begins from
the E0-style initialized state and is not a continuation of that screen.

| Setup | Gain | Cap | Status |
| --- | ---: | ---: | --- |
| [P7-E5-CZ-ABSORB-G200-CAP14615](p7-e5-cz-absorb-g200-cap14615/setup.md) | `2.00` | `146.15 kg/s` | `COMPLETE_VERIFIED`; 500 iterations, stable baseline but target/global inventory objectives not met |
| [P7-E5-CZ-ABSORB-G200-CAP29230](p7-e5-cz-absorb-g200-cap29230/setup.md) | `2.00` | `292.30 kg/s` | `BLOCKED_VERIFIED`; divergence during block ending active 450 |
| [P7-E5-CZ-ABSORB-G200-CAP58460](p7-e5-cz-absorb-g200-cap58460/setup.md) | `2.00` | `584.60 kg/s` | `BLOCKED_VERIFIED`; corrected rerun diverged during block ending active 450 |
| [P7-E5-CZ-ABSORB-COLD-RAMP11692](p7-e5-cz-absorb-cold-ramp11692/setup.md) | ramp to `116.92 kg/s` | inlet-matched | `NOT_RUN`; setup created, later Phase Loop launch required |

The complete design and evidence contract is in
[design.md](design.md). The lower-zone target is parent-relative and numerical:
`M_L,target = 0.50 × M_L0`, where `M_L0` is read from the active-2,500 parent.
This is not a claim about the physical brine-pool level. The family introduces
no bottom outlet, patch/reset route, UDF, remesh, or qualification path.

The explicit Phase Loop launch decision was entered on 2026-09-10. All three
children have now been classified with parent/source/topology, history, and
plot-led evidence. The low-cap child reached its declared horizon; the two
higher-cap children reached valid controller readbacks through active 400 and
then failed during the block ending at active 450. Their post-divergence
history tails are retained as numerical-failure evidence only.

## Family comparison

The three runs share the same early lower-inventory trajectory: approximately
`59.83 kg` at the parent readback, `39.83 kg` near active 100, `36.33 kg` near
active 150, a rebound to about `45.66 kg` near active 200, and a transient low
near `32.21 kg` near active 300. This means the controller does produce a
real, local phase-2 response. It does not mean that the declared target of
`29.9167 kg` is stably held.

The cap comparison is not a monotonic success story:

- `146.15 kg/s` completed, but the lower inventory oscillated above target and
  the total liquid inventory had a positive late slope of approximately
  `+0.998 kg/native iteration`.
- `292.30 kg/s` reached cap at active 400 and then diverged before the declared
  horizon.
- `584.60 kg/s` had not reached its cap at active 400 (`316.37 kg/s` command)
  and nevertheless encountered the same late divergence signature.

The absorber mechanism therefore remains a useful numerical abstraction and a
valid source-accounting experiment, but this particular G=2 lower-inventory
controller family does not yet provide a successful liquid-removal setting.
No cap member is promoted, and no automatic continuation is opened.

## Results and analysis records

- [CAP14615 results](p7-e5-cz-absorb-g200-cap14615/results.md) — completed
  finite-horizon baseline.
- [CAP29230 results](p7-e5-cz-absorb-g200-cap29230/results.md) — verified
  solver-divergence blocker.
- [CAP58460 results](p7-e5-cz-absorb-g200-cap58460/results.md) — corrected
  rerun verified solver-divergence blocker.

The current planned next step is a human decision on whether to design a
separate numerical-stabilization experiment around the local absorber/source
coupling. A larger cap alone is not supported by this family, and the Phase
Loop does not silently introduce an outlet, patch/reset mechanism, remesh, or
other escape concept.

## Cold-start balance probe

The cold-start child is a distinct test of branch existence, not another cap
continuation. It loads the exact E0-style initialized case/data state before
treatment iterations, preserves the lower split zone and no-outlet boundary,
and applies the fixed schedule
`Q_abs(n) = 116.92 kg/s × min(n/100, 1)`. The command is updated every 10
active iterations, reaches the inlet-matched value at active 100, and then is
held through the declared 1,000-iteration screen.

Its purpose is to distinguish accumulated-parent difficulty from a structural
phase-balance or lower-zone source-realization problem. It is setup-only at
present; no Phase Loop launch has been authorized for order 27.
