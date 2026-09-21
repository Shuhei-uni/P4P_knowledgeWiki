# P7-E5-CZ-G050 results

## Answer at a glance

`COMPLETE_VERIFIED` as a recovered discovery continuation. The first corrected
G050 attempt reached active iteration 500, but the Fluent connection reset while
the final case/data readback was being requested. The durable active-250 pair
was therefore used as the recovery boundary. The continuation reopened that
pair, verified both fluid zones, continued active iterations 251--500, saved
checkpoint pairs and the final pair, then reopened the final case/data and
verified the terminal topology.

The scientific result is still negative for the declared liquid-inventory
objective over this finite screen: the total liquid inventory rose from
`244.14 kg` at the recovered report start to `327.36 kg` at active 500. Its
late continuation slope was `+0.3256 kg/native iteration`. That is lower than
the corrected G025 late slope (`+0.5046`) and slightly lower than G100
(`+0.3521`), so G050 is the most promising provisional member of this family.
This ranking is bounded because G050's current report package covers the
restart window only (`native 748--998`), not a newly recorded full native
501--1,000 history.

## Evidence status

| Requirement | Status | Evidence |
| --- | --- | --- |
| Approved setup/design | PASS | [G050 setup](setup.md), shared E5-CZ design, gain `G=0.50` |
| Exact parent and recovery boundary | PASS | Paired durable active-250 checkpoint from the first corrected attempt; anchor manifest (local generated artifact): `PyAnsys/output/phase07_cell_zone/P7-E5-CZ-G050-student-20260910T034401Z-manifest.json` |
| Cell-zone topology/source binding | PASS | Recovery readback retained `p7-e5-lower-y010` and `separator-purnanto`; source tree remained lower-zone-only |
| Requested active horizon | PASS | Continuation covered active `251--500`; five controller updates through native `998` |
| Final paired case/data | PASS | Final active-500 pair was saved, reopened, and read back successfully |
| Report histories | PASS WITH WINDOW LIMIT | Fourteen histories, 251 points each, native `748--998`; the earlier attempt's full history is retained only as interrupted-attempt evidence |
| Residual history | PASS WITH WINDOW LIMIT | Seven residual series, 251 points, native `748--998` |
| Source audit | PASS | Every continuation update used Fluent `get_sum` for `phase-2-user-mass-source`; integrated values matched the analytical command to floating-point precision |
| Planned figures | PASS WITH WINDOW LIMIT | F1--F4 generated from the current continuation package |
| Prior endpoint failure | RETAINED | superseded first-attempt manifest (local generated artifact): `PyAnsys/output/phase07_cell_zone/P7-E5-CZ-G050-student-20260910T034401Z-manifest.json` records the lost final readback connection after active 500 |

## Controller and source readback

| Active update | Native iteration | Liquid mass [kg] | Requested source [kg/s] | Integrated source [kg/s] |
| ---: | ---: | ---: | ---: | ---: |
| 300 | 798 | 260.558 | 29.101 | -29.101 |
| 350 | 848 | 276.779 | 33.349 | -33.349 |
| 400 | 898 | 291.430 | 37.185 | -37.185 |
| 450 | 948 | 307.611 | 41.422 | -41.422 |
| 500 | 998 | 327.363 | 46.595 | -46.595 |

The final lower-zone phase-2 source was `-151.132656 kg/m3/s`, with final
requested integrated removal `46.594592 kg/s`; Fluent's `get_sum` returned
`-46.594592 kg/s`. No controller update saturated, and the phase-1 direct
source readback remained zero. The full machine-readable controller/source
record is in the continuation manifest (local generated artifact): `PyAnsys/output/phase07_cell_zone/P7-E5-CZ-G050-student-20260910T044606Z-manifest.json`.

## Numerical observations

The current continuation package reports the following late-window values for
native iterations `749--998`:

| Diagnostic | Result | Interpretation |
| --- | ---: | --- |
| Liquid-inventory slope | `+0.32558 kg/iteration` | Inventory still rises throughout the recovery window |
| Inventory start → end | `244.443 → 327.363 kg` | No observed global liquid-drain response |
| Lower-zone volume slope | `+3.695e-4 m3/iteration` | The selected region is not approaching a fixed liquid state |
| Phase-2 liquid outflow | `0.2567 kg/s` mean | Very small relative to `116.92 kg/s` liquid inflow |
| Boundary mixture-imbalance ratio | `0.5877` mean | Boundary-only closure remains materially open |
| Bottom vapor loss ratio | `0` | No bottom vapor-loss signature in this window |

Late residual means were approximately `6.89e-2` continuity, `1.61e-4`,
`1.64e-4`, and `1.63e-4` for the three velocity residuals, `1.36e-3` for
`k`, `2.34e-3` for epsilon, and `6.95e-3` for phase-2 volume fraction. These
are finite numerical histories, not evidence of a converged steady solution.

The report-facing figures are:

1. [F1 — liquid inventory versus E0](figures/P7-E5-CZ-G050-student-20260910T044606Z/F1-liquid-inventory-vs-E0.png), the direct response figure. Its G050 trace is the recovered native `748--998` window and must not be read as a fresh full-history native `501--1,000` trace.
2. [F2 — phase routing and closure](figures/P7-E5-CZ-G050-student-20260910T044606Z/F2-phase-routing-and-closure.png), showing the small liquid-outflow response and open mixture closure.
3. [F3 — numerical adequacy](figures/P7-E5-CZ-G050-student-20260910T044606Z/F3-numerical-adequacy.png), showing residuals and the boundary diagnostic.
4. [F4 — adaptive controller](figures/P7-E5-CZ-G050-student-20260910T044606Z/F4-adaptive-controller.png), showing the rising command without saturation.

## Interpretation and claim boundary

The cell-zone implementation remains technically viable: the existing mesh
was split into a genuine lower fluid zone while preserving the global mesh
counts and coordinate/connectivity topology contract. The lower-zone-only
source branches also read back correctly after restart.

G050 is the most promising provisional gain because its observed late
inventory drift is the smallest of the three gains currently available, but
the evidence does not show successful liquid removal. The imposed source
command increases while phase-2 liquid boundary outflow remains small, and the
boundary-only mixture balance is open. The result is therefore a finite
discovery-screen observation, not a physical drainage or qualification result.

Patching/resetting the field is excluded from this record and is not a next
step. The recovered run also does not justify an automatic long continuation:
the next decision must use the complete three-gain comparison and the Phase 07
lifecycle gate.

## Durable artifacts

- [G050 setup](setup.md)
- [G050 run paths](run-paths.yaml)
- continuation manifest (local generated artifact): `PyAnsys/output/phase07_cell_zone/P7-E5-CZ-G050-student-20260910T044606Z-manifest.json`
- report histories (local generated artifact): `PyAnsys/output/phase07_cell_zone/P7-E5-CZ-G050-student-20260910T044606Z-reports.json`
- residual history (local generated artifact): `PyAnsys/output/phase07_cell_zone/P7-E5-CZ-G050-student-20260910T044606Z-residuals.json`
- numerical summary (local generated artifact): `PyAnsys/output/phase07_cell_zone/P7-E5-CZ-G050-student-20260910T044606Z-analysis/summary.json`
- [corrected fresh-run builder](../../../../../PyAnsys/scripts/setup/run_p7_e5_cz.py)
- [recovery continuation runner](../../../../../PyAnsys/scripts/setup/resume_p7_e5_cz.py)

The final remote pair is recorded in `run-paths.yaml` and the manifest:

```text
C:\Users\Shuhei Yokkaichi\Documents\FluentRuns\Phase07\CellZoneTreatment\20260910T044606Z\P7-E5-CZ-G050\P7-E5-CZ-G050-active500.cas.h5
C:\Users\Shuhei Yokkaichi\Documents\FluentRuns\Phase07\CellZoneTreatment\20260910T044606Z\P7-E5-CZ-G050\P7-E5-CZ-G050-active500.dat.h5
```

## Next action

Use the completed G025/G050/G100 package to make the family decision. The
current evidence supports “cell-zone source binding works, but the finite
screen does not yet remove the global liquid inventory”; it does not support
promotion, qualification, or an unbounded continuation.
