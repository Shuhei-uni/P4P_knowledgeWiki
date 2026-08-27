> **Retired source:** Setups/reports/purnanto-reference/08/velocity-family-comparison.md
> **Migration note:** Historical wording, evidence status, and uncertainty labels are preserved; this Project copy is not a reinterpretation. Machine-generated artifacts remain with their original external owners; the retired written source is recoverable from Git history.

# Setup 08 Family Comparison — Inlet Loading

## Comparison scope

This report compares the three currently available continuous-phase cases in the `08` setup family:

1. `08b` — the split-inlet parity parent;
2. `08c-v20p00` — the lower-loading sensitivity case;
3. `08c-v32p14` — the higher-loading sensitivity case.

The controlled variable is inlet loading, represented by the split-inlet mass flows and nominal inlet velocity. The inlet enthalpy basis, geometry, split-inlet topology, and main continuous-phase models are kept from `08b`.

Evidence class: **preliminary comparison**. This is not yet an apples-to-apples efficiency study because `08c-v20p00` is only available at `3088` iterations, neither `08c` case has a closed phase balance, and the residuals have not reached an accepted level.

## Setup links

- Parent setup: [08b — Purnanto parity split-inlet rebuild](../purnanto-08b-parity-split-inlet/setup.md)
- Sensitivity setup: [08c — Purnanto parity inlet-velocity sensitivity](setup.md)
- Parent result detail: [08b results](../purnanto-08b-parity-split-inlet/results.md)
- Sensitivity result detail: [08c results](results.md)

## 1. Case identity and comparability

| Case | Family role | Nominal inlet condition | Data checkpoint | Case/data evidence |
|---|---|---:|---:|---|
| `08b` | parent reference | `116.92 kg/s` liquid + `80.69 kg/s` vapor; approximately `27.1 m/s` reference basis | `5000` iterations | saved carrier field and partial DPM sample |
| `08c-v20p00` | low-loading child | `20.00 m/s`; `86.18 kg/s` liquid + `60.21 kg/s` vapor | `3088` iterations | saved carrier field; incomplete convergence history |
| `08c-v32p14` | high-loading child | `32.14 m/s`; `138.48 kg/s` liquid + `96.76 kg/s` vapor | `5000` iterations | saved carrier field; incomplete convergence history |

The `08c` build readback confirms the changed mass-flow inputs. The opposite phase on each split inlet remained `0.0 kg/s`. These are the requested low/reference/high loading cases. The `08b` flow target is not an exact density-derived `27.118 m/s` point, so it remains the practical reference case.

## 2. Carrier-phase comparison

| Case | Total inlet flow | Steam-outlet liquid | Steam-outlet vapor | Scoped steam-line liquid-removal efficiency | Steam-outlet dryness | Derived phase imbalance |
|---|---:|---:|---:|---:|---:|---:|
| `08b` | `197.61 kg/s` | `0.082132007 kg/s` | `81.464165 kg/s` | `99.92975367%` | `99.89928175%` | `116.063719 kg/s` (`0.5873372754` ratio) |
| `08c-v20p00` | `146.39 kg/s` | `0.001326962 kg/s` | `60.768470 kg/s` | `99.9985%` | `99.9978%` | `85.6202 kg/s` (`58.49%`) |
| `08c-v32p14` | `235.24 kg/s` | `0.1132807 kg/s` | `97.659468 kg/s` | `99.9182%` | `99.8841%` | `137.4673 kg/s` (`58.44%`) |

The results show the expected trend:

- increasing from `20.00` to `32.14 m/s` increases steam-outlet liquid carryover from `0.00133` to `0.11328 kg/s`;
- the scoped liquid-removal metric decreases from `99.9985%` to `99.9182%`;
- outlet dryness decreases from `99.9978%` to `99.8841%`.

The `08b` reference sits between the two `08c` cases in loading and also has an intermediate carryover and outlet-dryness result. This supports the expected trend, but does not yet prove a general efficiency relationship.

## 3. Residuals and solution quality

| Case | Current residual evidence | Comparison note |
|---|---|---|
| `08b` | saved at `5000` iterations; the whole-domain phase balance is not closed | useful as the parent reference, but not a validated baseline |
| `08c-v20p00` | checkpoint at `3088`; continuity remains around `10^-1`; velocity, `k`, and `epsilon` improve but have not reached acceptance | less developed than the other two cases |
| `08c-v32p14` | `5000` iterations; continuity remains around `10^-1`, with epsilon spikes and a phase-fraction plateau | same iteration count as `08b`, but still not accepted |

The main comparison problem is that `08c-v20p00` stopped earlier, and both `08c` cases still have a large phase imbalance. A later comparison should use the same iteration checkpoint or the same residual/monitor acceptance gate, then recalculate the flux results.

## 4. DPM comparability

Do not compare DPM performance across these cases yet:

- `08b` has a partial six-bin fate sample: `8` escaped, `0` reported trapped, and `13012` incomplete;
- both `08c` cases have DPM inventory only, with six active injections and no stored fate/result summary;
- the `08c` inventory also intentionally omits the three larger recovered bins from the aggregate interpretation.

This family comparison is carrier-phase only. DPM should wait until the carrier fields pass a basic numerical acceptance gate.

## 5. Current interpretation

The current result is:

> On the split-inlet `08b`/`08c` branch, the higher-loading `32.14 m/s` case has more steam-outlet liquid carryover and lower outlet dryness than the `20.00 m/s` case. This is the expected loading effect. The cases still need better convergence and phase balance before the efficiency difference can be treated as final.

This is the behaviour expected when higher inlet speed makes moisture removal more difficult.

## 6. Follow-up gate

Before using this family for a stronger claim:

1. continue `08c-v20p00` to a checkpoint comparable with the other two cases, or compare all three using the same residual/monitor gate;
2. confirm the continuity and phase-fraction residuals;
3. close or reduce the whole-domain phase imbalance;
4. recalculate steam-line liquid carryover and outlet dryness;
5. then repeat the same DPM tracking sample across the selected cases.

### Source artifacts

- 08c-v20p00 post-processing report (historical machine artifact path: `../../../PyAnsys/output/live_postprocess_20260720/08c-v20p00-report.md`; not migrated)
- 08c-v32p14 post-processing report (historical machine artifact path: `../../../PyAnsys/output/live_postprocess_20260720/08c-v32p14-report.md`; not migrated)
- 08c-v20p00 machine-readable summary (historical machine artifact path: `../../../PyAnsys/output/live_postprocess_20260720/08c-v20p00-summary.json`; not migrated)
- 08c-v32p14 machine-readable summary (historical machine artifact path: `../../../PyAnsys/output/live_postprocess_20260720/08c-v32p14-summary.json`; not migrated)
