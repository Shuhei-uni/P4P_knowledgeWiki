# Observation 01 — 08b/08c Inlet-Loading Family

## Comparison question

Across the same split-inlet separator family, does raising the inlet loading/speed produce more liquid carryover into the steam outlet?

## Compared cases

| Case | Family role | Nominal condition | Checkpoint |
|---|---|---:|---:|
| `08c-v20p00` | low-loading child | `20.00 m/s`; `86.18 kg/s` liquid + `60.21 kg/s` vapour | `3088` iterations |
| `08b` | practical parity reference | approximately `27.1 m/s`; `116.92 kg/s` liquid + `80.69 kg/s` vapour | `5000` iterations |
| `08c-v32p14` | high-loading child | `32.14 m/s`; `138.48 kg/s` liquid + `96.76 kg/s` vapour | `5000` iterations |

The intended controlled change is inlet loading at the same enthalpy basis, split-inlet topology, geometry, and main carrier-flow model. `08b` is the practical middle reference rather than an exact density-derived velocity point.

## What the carrier results show

| Case | Steam-outlet liquid | Scoped steam-line liquid removal | Steam-outlet dryness | Derived phase imbalance |
|---|---:|---:|---:|---:|
| `08c-v20p00` | `0.00133 kg/s` | `99.9985%` | `99.9978%` | `58.49%` |
| `08b` | `0.08213 kg/s` | `99.9298%` | `99.8993%` | `58.73%` |
| `08c-v32p14` | `0.11328 kg/s` | `99.9182%` | `99.8841%` | `58.44%` |

The three points form the expected directional ordering: greater loading produces more steam-line liquid carryover and lower outlet dryness. The high-loading case has about eighty-five times the reported steam-outlet liquid flow of the low-loading case.

## Carrier flux and DPM tracking are complementary, not additive

The carrier flux report and the DPM particle-track report answer different questions:

- **Carrier flux:** phase-specific liquid flow crossing `steamoutlet`. This is the evidence behind the directional loading trend above.
- **DPM tracking:** a separate, one-way six-bin droplet probe on the saved carrier field. The DPM source interaction is off, so its represented mass is not included in the carrier solution or its phase-flux report.

Do not add DPM escaped mass to the Eulerian steam-outlet liquid flux, and do not interpret their ratio as a total carryover fraction. The DPM payload is a diagnostic representation of six particle sizes, not a partition of the Eulerian liquid inlet.

## DPM tracking comparison

All three checkpoints use the recovered six-bin probe from `5.63` to `348.88 µm`. The `08c` case readbacks retain the reference `27.118 m/s` DPM injection velocity and a fixed `29.22 kg/s` represented six-bin payload while the carrier inlet loading changes. This makes the DPM result a fixed-probe sensitivity to different carrier fields, not a matched physical droplet-loading comparison.

| Case | Completed fate counts: escaped / trapped / incomplete | Completed tracks | Escaped represented DPM flow | What it can support |
|---|---:|---:|---:|---|
| `08c-v20p00` | `1 / 7,358 / 5,661` | `7,359 / 13,020` (`56.5%`) | `8.756e-05 kg/s` | The captured probe shows substantial trapping, increasing by diameter in the completed count summaries. It remains an early, `3088`-iteration checkpoint. |
| `08b` | `8 / 0 reported / 13,012` | `8 / 13,020` (`0.06%`) | `7.005e-04 kg/s` | Only the fine `5.63 µm` bin reported completed escape in the sampled pass; almost every other path is unresolved. |
| `08c-v32p14` | `13 / 0 / 13,007` | `13 / 13,020` (`0.10%`) | `1.138e-03 kg/s` | The apparent lack of trapping is not collection evidence: almost all tracks are incomplete. |

The higher-loading case has the largest reported DPM escaped mass in the completed fine-bin tracks, which is directionally consistent with the carrier flux trend. It is **not** a second, independent carryover trend: the `08c-v32p14` DPM completion rate is only `0.10%`, and the result has no usable coarse-bin terminal-fate information.

For `08c-v20p00`, Fluent did not emit the `348.88 µm` mass-transfer rows even though it emitted that injection's count summary. Consequently, the low-loading DPM mass rows do not close over all six bins and must not be aggregated into a family DPM mass balance.

## Evidence status and interpretation

**Reported:** the carrier liquid flux rises from `0.00132696 kg/s` at `20.00 m/s` to `0.1132807 kg/s` at `32.14 m/s`, a difference of `0.1119537 kg/s` and a factor of about `85.4`. `08b` sits between those endpoints at `0.082132007 kg/s`.

**Inferred:** at the present checkpoints, increasing inlet loading makes moisture removal harder in this split-inlet geometry. Higher gas/liquid throughput plausibly leaves less opportunity for liquid to disengage before the steam outlet.

**Unresolved:** the DPM records do not establish a droplet-fate curve versus loading. Their tracking completion changes from `56.5%` for the low-loading checkpoint to approximately `0.1%` for the reference and high-loading checkpoints, while the carrier states also have different iteration checkpoints and open phase balances.

## Working interpretation

This is a **directional observation only**. Both `08c` cases have continuity on the order of `10^-1`, residual/phase-fraction limitations, and an open phase balance. The low-loading case also stopped earlier than the other two cases. The reported scoped removal values must not be treated as validated separator efficiencies.

## Reasoning for the next simulations

Retain this low/reference/high inlet-loading family. It is the simplest way to establish whether later DPM or EWF changes are occurring in a flow regime where carryover is already sensitive to loading.

Before adding further physics:

1. continue or restart all three cases to a common residual/monitor acceptance window;
2. include the lower liquid outlet or otherwise close the carrier flux scope;
3. repeat the same DPM size set, tracking budget, and per-injection zone summary at each accepted carrier state;
4. retain Fluent `Incomplete` as raw bookkeeping and do not treat it as a blocker; compare observed escape through `steamoutlet` only;
5. if the DPM payload is intended to represent physical inlet loading rather than a fixed probe, scale and document it as a fraction of each case's liquid inlet; and
6. compare carryover against inlet loading only after the three states are numerically comparable.

## Evidence

- [08 family comparison](../../Setups/reports/08/velocity-family-comparison.md)
- [08b result](../../Setups/reports/08b/results.md)
- [08c result](../../Setups/reports/08c/results.md)
- [08b phase-flux extract](../../Setups/reports/08b/phase-flux-result.md)
- [08c-v20p00 carrier summary](../../PyAnsys/output/live_postprocess_20260720/08c-v20p00-summary.json) and [DPM particle-track summary](../../PyAnsys/output/dpm_particle_tracks/20260720-dpm-analysis/08c-v20p00-20260720-dpm-particle-track-summary.json)
- [08c-v32p14 carrier summary](../../PyAnsys/output/live_postprocess_20260720/08c-v32p14-summary.json) and [DPM particle-track summary](../../PyAnsys/output/dpm_particle_tracks/20260720-dpm-analysis/08c-v32p14-20260720-dpm-particle-track-summary.json)

The linked 08-family comparison remains useful for the carrier table. Its DPM section predates the later 08c particle-track summaries above, so this observation uses the detailed `08b` and `08c` result reports plus the raw DPM artifacts for DPM interpretation.
