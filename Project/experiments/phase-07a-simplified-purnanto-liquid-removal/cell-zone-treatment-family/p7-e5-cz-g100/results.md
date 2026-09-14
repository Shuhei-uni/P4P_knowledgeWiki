# P7-E5-CZ-G100 results

## Answer at a glance

`COMPLETE_VERIFIED` as a fresh 500-controller-iteration discovery screen on
`student`. The run loaded the exact E0 native-500 case/data pair, split the
existing parent into the approved lower fluid zone, passed source-off
save/reopen and smoke, enabled the lower-zone-only source contract, completed
all ten controller updates through native iteration 1,000, saved the final
paired case/data, reopened it, and verified the terminal zones.

G100 reduced the late inventory drift relative to corrected G025, but it did
not reverse the global liquid-inventory trend. The late slope was
`+0.3521 kg/native iteration`; the final inventory was `332.52 kg`, compared
with `365.36 kg` for G025. G050 currently has the smallest provisional late
slope (`+0.3256 kg/iteration`), although G050 is a recovered restart-window
package rather than a fresh full-history run.

One inherited Fluent autosave path warning appeared near native iteration 999:
the old E0 path under `C:\Users\syok443\...` did not exist. Fluent continued,
saved the requested final pair, reopened it, and the terminal manifest is
complete. This is retained as a nonfatal warning, not treated as missing
terminal evidence.

## Evidence status

| Requirement | Status | Evidence |
| --- | --- | --- |
| Approved setup/design | PASS | [G100 setup](setup.md), shared E5-CZ design, gain `G=1.00` |
| Exact parent identity | PASS | Shared E0-REF native-500 case/data pair; parent readback recorded in the manifest |
| Cell-zone split | PASS | `3,794` marked lower cells separated from the `342,609`-cell parent; lower zone `p7-e5-lower-y010` read back after reopen |
| Source binding | PASS | Lower-zone phase-2 mass and mixture x/y/z sources active; parent and phase-1 direct sources disabled |
| Mesh invariants | PASS | Split branch retained the approved global cells/faces/nodes, extents, volume/face statistics, and mesh-check evidence |
| Save/reopen and smoke | PASS | Source-off prepared child and final active-500 pair reopened successfully; smoke completed before source activation |
| Requested horizon | PASS | Ten controller updates, active `1--500`, native `501--1,000` |
| Report histories | PASS | Fourteen histories recovered; flux histories include native 500 and mass/volume histories cover native 501--1,000 |
| Residual history | PASS | Seven native residual series with 500 active points |
| Source audit | PASS | Each update used Fluent `get_sum`; final integrated phase-2 source was `-95.8920768 kg/s`, matching the requested command |
| Final paired case/data | PASS | Final active-500 case/data saved and reopened |
| Planned figures | PASS | F1--F4 generated from the full run package |
| Inherited-path warning | NONFATAL | Old E0 autosave path warning near native 999; no effect on final pair, histories, or terminal readback |
| Prior endpoint failure | RETAINED | [superseded endpoint manifest](../../../../../PyAnsys/output/phase07_cell_zone/P7-E5-CZ-G100-student-20260910T030000Z-manifest.json) remains as the earlier blocked attempt |

## Controller and source readback

| Active update | Native iteration | Liquid mass [kg] | Requested source [kg/s] | Integrated source [kg/s] |
| ---: | ---: | ---: | ---: | ---: |
| 50 | 550 | 168.709 | 10.100 | -10.100 |
| 100 | 600 | 184.712 | 18.481 | -18.481 |
| 150 | 650 | 205.115 | 29.166 | -29.166 |
| 200 | 700 | 225.269 | 39.721 | -39.721 |
| 250 | 750 | 242.313 | 48.647 | -48.647 |
| 300 | 800 | 256.598 | 56.128 | -56.128 |
| 350 | 850 | 272.068 | 64.230 | -64.230 |
| 400 | 900 | 288.345 | 72.755 | -72.755 |
| 450 | 950 | 309.299 | 83.729 | -83.729 |
| 500 | 1,000 | 332.524 | 95.892 | -95.892 |

The final lower-zone phase-2 volumetric source was `-311.032323 kg/m3/s`.
The final commanded removal was `95.892077 kg/s`, below the `146.15 kg/s`
clamp; no controller update saturated. Direct phase-1 source readback stayed
zero. The complete source tree and update-by-update `get_sum` records are in
the [G100 manifest](../../../../../PyAnsys/output/phase07_cell_zone/P7-E5-CZ-G100-student-20260910T045745Z-manifest.json).

## Numerical observations

The full report package gives the following finite-screen values:

| Diagnostic | Full screen | Late window `751--1,000` | Interpretation |
| --- | ---: | ---: | --- |
| Liquid-inventory slope | `+0.35127 kg/iteration` | `+0.35206 kg/iteration` | Positive drift persists |
| Liquid inventory | `149.770 → 332.524 kg` | `242.669 → 332.524 kg` | No global liquid-drain response |
| Lower-zone volume slope | — | `+3.995e-4 m3/iteration` | Selected region continues to fill |
| Phase-2 liquid outflow | — | `0.2642 kg/s` mean | Very small relative to `116.92 kg/s` inflow |
| Boundary mixture-imbalance ratio | — | `0.5887` mean | Boundary-only closure remains open |
| Bottom vapor loss ratio | — | `0` | No bottom vapor-loss signature |

Late residual means were approximately `7.10e-2` continuity, `1.76e-4`,
`1.71e-4`, and `1.77e-4` for the three velocity residuals, `1.69e-3` for
`k`, `3.10e-3` for epsilon, and `7.41e-3` for phase-2 volume fraction. The
histories remain finite, but they do not establish a converged steady solution
or a closed physical balance.

The report-facing figures are:

1. [F1 — liquid inventory versus E0](figures/P7-E5-CZ-G100-student-20260910T045745Z/F1-liquid-inventory-vs-E0.png), the direct response figure over native `501--1,000`.
2. [F2 — phase routing and closure](figures/P7-E5-CZ-G100-student-20260910T045745Z/F2-phase-routing-and-closure.png), showing the small phase-2 liquid outflow and open mixture closure.
3. [F3 — numerical adequacy](figures/P7-E5-CZ-G100-student-20260910T045745Z/F3-numerical-adequacy.png), showing the residual histories and balance diagnostic.
4. [F4 — adaptive controller](figures/P7-E5-CZ-G100-student-20260910T045745Z/F4-adaptive-controller.png), showing the command rising to `95.89 kg/s` without saturation.

## Interpretation and claim boundary

G100 confirms that the native cell-zone source architecture remains operable
at the higher gain: the mesh split, zone binding, adaptive source updates,
integrated source audit, and final restart state all survived a full screen.
The higher gain also reduces the finite-horizon inventory relative to G025,
but it does not produce a falling total liquid inventory. The command grows
strongly while the observed phase-2 liquid boundary outflow stays near zero
relative to the liquid inflow, and the boundary-only mixture closure remains
open.

The correct claim is therefore “G100 completed a valid artificial cell-zone
discovery screen with positive inventory drift,” not “G100 drains the vessel” or
“G100 is qualified.” The three-gain family can be compared for provisional
ranking, but no member should be promoted to a physical or long-horizon claim
from this finite evidence.

Patching/resetting the field is excluded from this record. No automatic
qualification run or unbounded continuation is authorized by this result.

## Durable artifacts

- [G100 setup](setup.md)
- [G100 run paths](run-paths.yaml)
- [G100 manifest](../../../../../PyAnsys/output/phase07_cell_zone/P7-E5-CZ-G100-student-20260910T045745Z-manifest.json)
- [report histories](../../../../../PyAnsys/output/phase07_cell_zone/P7-E5-CZ-G100-student-20260910T045745Z-reports.json)
- [residual history](../../../../../PyAnsys/output/phase07_cell_zone/P7-E5-CZ-G100-student-20260910T045745Z-residuals.json)
- [numerical summary](../../../../../PyAnsys/output/phase07_cell_zone/P7-E5-CZ-G100-student-20260910T045745Z-analysis/summary.json)
- [corrected E5-CZ runner](../../../../../PyAnsys/scripts/setup/run_p7_e5_cz.py)

The final remote pair is recorded in `run-paths.yaml` and the manifest:

```text
C:\Users\Shuhei Yokkaichi\Documents\FluentRuns\Phase07\CellZoneTreatment\20260910T045745Z\P7-E5-CZ-G100\P7-E5-CZ-G100-active500.cas.h5
C:\Users\Shuhei Yokkaichi\Documents\FluentRuns\Phase07\CellZoneTreatment\20260910T045745Z\P7-E5-CZ-G100\P7-E5-CZ-G100-active500.dat.h5
```

## Next action

Compare the completed G025/G050/G100 F1--F4 package under the Phase 07
lifecycle gate. The evidence currently points to G050 as the most promising
provisional gain, while all three still show positive inventory drift and open
closure. A new experiment or long continuation should be selected only after
that comparison, not inferred from G100 completion alone.
