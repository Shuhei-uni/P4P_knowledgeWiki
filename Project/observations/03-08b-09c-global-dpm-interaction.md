> **Legacy source:** ResearchProject_wiki/observations/03-08b-09c-global-dpm-interaction.md  
> **Migration note:** Historical wording, evidence status, and uncertainty labels are preserved; this Project copy is not a reinterpretation. Raw and machine-generated artifacts remain at their legacy paths.

# Observation 03 — 08b/09c Global DPM Interaction

## Comparison question

Does enabling DPM feedback to the continuous phase change the split-inlet carrier solution relative to the corresponding one-way-DPM basis?

## Intended controlled difference

The `09c` case definition was built from the `08b`-style split-inlet source case. Its stated intentional change is global DPM interaction:

| Setting | One-way source / `08b` basis | `09c` |
|---|---:|---:|
| DPM interaction with continuous phase | Off | On |
| Update DPM sources every flow iteration | Off | On |
| DPM iteration interval | `10` | `1` |

The readback confirms six inherited surface injections on `steaminlet`, the same `Mixture` carrier model, RNG `k-epsilon` model, split inlets, outlet, and wall fates. No EWF, re-entrainment, stripping, stochastic-dispersion change, or turbulence-model change was deliberately added in this branch. Two-way turbulent coupling and volume displacement also remain off.

## DPM-loading accounting boundary

The `09c` source case retains a six-bin represented DPM payload of `29.22 kg/s` while its Eulerian liquid inlet remains `116.92 kg/s`. The DPM payload is therefore approximately `25%` of the Eulerian liquid inlet and is **additional** to it in this first `09c` build; it was not deducted from the Eulerian liquid boundary.

This means the checkpoint is a screening test of enabling continuous-phase DPM sources for the inherited, unpartitioned payload. It is not yet a mass-consistent test of a known geothermal droplet fraction, and it cannot establish that two-way DPM is required at a physical separator-inlet loading. The later `09cV2` branch explicitly changes this accounting by using a selected DPM fraction and reducing the Eulerian liquid contribution; it is the next branch in the three-way comparison, not a direct replacement for the `08b`/`09c` control.

## Available result contrast

| Quantity | `08b` one-way reference | `09c` two-way checkpoint |
|---|---:|---:|
| Carrier checkpoint | `5000` iterations | `921` iterations |
| Liquid inlet | `116.92 kg/s` | `116.92 kg/s` |
| Vapour inlet | `80.69 kg/s` | `80.69 kg/s` |
| Steam-outlet liquid | `0.08213 kg/s` | approximately `0 kg/s` |
| Steam-outlet vapour | `81.4642 kg/s` | `81.4542 kg/s` |
| Derived phase imbalance | `58.73%` | `58.78%` |
| Continuity state | parent field retained as a screening reference | around `10^-1`; not converged |

The numerical deltas are small relative to the unresolved carrier balance: `09c` has approximately `0.0100 kg/s` less steam-outlet vapour and about `0.0921 kg/s` more unclosed mixture flow than `08b`. These are checkpoint differences, not established DPM-feedback effects.

The apparent two-way result of zero steam-outlet liquid must not be read as improved separation. `09c` is at a much earlier checkpoint, retains an open phase balance, and did not produce a DPM fate analysis. The similar large imbalance ratio shows that neither result closes the carrier-liquid path needed for a separator claim.

## Three-way DPM tracking evidence

The three cases form a useful branch sequence: `08b` supplies the one-way reference, `09c` activates two-way DPM interaction on the inherited unpartitioned payload, and `09cV2` retains two-way interaction while correcting the liquid/DPM accounting at a selected `5%` DPM allocation point. The `09c` particle-fate output was not captured, so its fate cells are intentionally left as a placeholder for later evidence rather than inferred from its carrier flux.

| DPM evidence | `08b` one-way sample | `09c` two-way interaction checkpoint | `09cV2` two-way, `5%` allocation diagnostic |
|---|---:|---:|---:|
| Carrier / DPM liquid accounting | `116.92 kg/s` Eulerian liquid; `29.22 kg/s` DPM probe is one-way | `116.92 kg/s` Eulerian liquid plus `29.22 kg/s` unpartitioned DPM payload | `111.074 kg/s` Eulerian liquid + `5.846 kg/s` DPM = `116.92 kg/s` inlet accounting |
| Interaction and source updates | Off | On; sources updated every flow iteration; interval `1` | On; sources updated every flow iteration; interval `1` |
| DPM material identity | `water-liquid` | `water-liquid` | `water-liquid-at-psep-dpm` |
| Carrier evidence window | Saved `5000`-iteration field | `921`-iteration diagnostic | `909`-iteration diagnostic; exact source checkpoint filename unavailable |
| Parcels tracked | `13,020` | **Not captured — add when available** | `13,020` |
| Escaped / trapped / incomplete | `8 / 0 reported / 13,012` | **Not captured — add when available** | `805 / 4,132 / 8,083` |
| Completed terminal fates | `8` (`0.06%`) | **Not captured — add when available** | `4,937` (`37.9%`) |
| Escaped represented flow | `7.005e-04 kg/s` | **Not captured — add when available** | `0.015676 kg/s` |
| Trapped represented flow | no reported trapped row | **Not captured — add when available** | `2.804297 kg/s` at `bottom` |
| Incomplete represented flow | `29.22 kg/s` | **Not captured — add when available** | `3.02646 kg/s` |

### `09c` DPM tracking placeholder

When the original `09c` result is available, add the following from one matched six-injection Particle Tracks Summary sweep:

| Required `09c` item | Value to add |
|---|---|
| Case/data filename and iteration/time checkpoint | — |
| Six injection names, diameters, and represented mass flows | — |
| Total tracked / escaped / trapped / incomplete parcel counts | — |
| Per-injection escaped / trapped / incomplete counts and terminal zones | — |
| Escaped / trapped / incomplete represented mass flows | — |
| Per-injection and aggregate mass-flow closure residuals | — |
| Tracking controls, including maximum steps and stochastic state | — |

The existing endpoints already show a material fate contrast. In `08b`, only eight `5.63 µm` parcels complete an escape and every larger sampled bin remains incomplete. In `09cV2`, the `5.63` and `28.14 µm` bins report steam-outlet escape, while all six bins report some trapping at `bottom`; the coarse `348.88 µm` bin contributes the largest trapped represented mass. The `09cV2` per-injection mass-transfer rows close to printed precision, unlike the unresolved all-incomplete-dominated `08b` sample.

This three-way view is useful for tracking branch evolution. It does **not** isolate a single cause for the `08b` to `09cV2` fate difference: interaction state, source-update schedule, liquid/DPM allocation, DPM material identity, Fluent version, carrier maturity, and the available tracking/report workflow differ together. The missing `09c` fate summary is the most important bridge for narrowing that uncertainty. In addition, the `09cV2` carrier field is still mass-imbalanced and not converged, so the larger completed escape count is not a steam-purity or separator-performance result.

## Evidence that is present and missing

| Evidence item | `08b` one-way basis | `09c` two-way checkpoint | Comparison use |
|---|---|---|---|
| Carrier phase fluxes | Saved `5000`-iteration flux extract | Saved `921`-iteration flux extract | Diagnostic only; checkpoints are unmatched and the lower liquid path is outside the reported scope. |
| DPM payload and settings | Six-bin, one-way screening payload | Same six-bin `29.22 kg/s` payload; interaction readback on, update every iteration, interval `1` | Confirms the coupling switch was isolated, but the payload is unpartitioned. |
| Integrated DPM mass/momentum sources | Not applicable to one-way tracking | Not reported | Required before quantifying the carrier forcing introduced by coupling. |
| DPM terminal fates | Partial six-bin sample with observed escape plus raw incomplete categories | No fate analysis captured; placeholder retained above | Keep incomplete categories out of blocker logic; await the `09c` sweep for interaction effects. |
| Residual/monitor history | Parent screening reference at `5000` iterations | `921` iterations; continuity around `10^-1` | Insufficient to identify a coupling effect independently of solution maturity. |

The current evidence therefore supports a **setting-isolation result**, not a physics result: the global interaction controls were enabled without intentionally mixing EWF or turbulence changes, but the actual carrier-source history and matched terminal DPM fates are absent.

## Working interpretation

**Reported:** `09c` enabled continuous-phase DPM interaction, source update every flow iteration, and a DPM iteration interval of `1` on the inherited six-bin `29.22 kg/s` payload. The checkpoint reports near-zero Eulerian liquid flux at `steamoutlet`, but a `58.78%` phase-flow imbalance and continuity around `10^-1`.

**Inferred:** two-way source feedback may change the carrier field, but this checkpoint cannot distinguish a real feedback response from different solution maturity or the effect of applying an additional diagnostic DPM load.

**Unresolved:** whether source feedback materially changes carrier flow at a mass-consistent and physically defensible DPM fraction; whether it changes terminal droplet fates; and whether either change survives a closed carrier-flux comparison.

The three-way DPM sequence is a useful hypothesis generator: a mass-partitioned coupled branch may materially alter the resolved fine-droplet escape/trapping picture. Complete the `09c` placeholder before attributing any part of that shift to interaction or allocation.

The valuable result is procedural: global DPM interaction must be treated as a dedicated branch, with source-update controls recorded, rather than being enabled invisibly alongside EWF or turbulence changes.

## Reasoning for the next simulations

Create a mass-accounted, matched one-way/two-way pair from the same carrier checkpoint:

1. converge or define a common transient averaging window for the one-way parent;
2. select and label the DPM mass fraction; either partition the total liquid inlet between Eulerian and DPM liquid in both cases, or explicitly retain an added-load sensitivity rather than calling it physical;
3. duplicate the mass-accounted parent exactly;
4. enable only global DPM interaction, source update every iteration, and the specified DPM interval in the child;
5. run both over the same physical-time window or the same accepted monitor window;
6. record integrated DPM mass and momentum source totals, carrier residual histories, phase fluxes including the lower liquid outlet, and matching DPM terminal fates; and
7. add a separate allocation sensitivity only after the coupled-versus-one-way pair is complete; and
8. populate the `09c` DPM tracking placeholder from the same six-injection summary format before interpreting the three-way fate sequence; and
9. report the coupled-minus-one-way differences alongside the residual, flux-closure, and DPM-completion gates.

That experiment will determine whether global DPM feedback actually changes the flow, rather than merely coinciding with an earlier transient checkpoint.

## Evidence

- [08b result](../experiments/purnanto-08b-parity-split-inlet/results.md)
- [09c result](../experiments/purnanto-09c-two-way-dpm-coupling/results.md)
- [08b phase-flux extract](../experiments/purnanto-08b-parity-split-inlet/phase-flux-result.md)
- [past reported 09c setup definition](../experiments/purnanto-09c-two-way-dpm-coupling/setup.md)
- 09c coupling build/readback (historical machine artifact path: `../../PyAnsys/output/setup09c_two_way_dpm_coupling_summary.json`; not migrated)
- 09c carrier summary (historical machine artifact path: `../../PyAnsys/output/live_postprocess_20260720/09c-summary.json`; not migrated) and residual history (historical machine artifact path: `../../PyAnsys/output/live_postprocess_20260720/09c-residuals_20260720_132009.png`; not migrated)
- [09cV2 result — third comparison state](../experiments/purnanto-09cV2-dpm-partition-control/results.md), injection summary (historical machine artifact path: `../../PyAnsys/output/live_postprocess_20260722/09cV2-server2-dpm/dpm_injection_summary.csv`; not migrated), and zone/fate rows (historical machine artifact path: `../../PyAnsys/output/live_postprocess_20260722/09cV2-server2-dpm/dpm_zone_summary.csv`; not migrated)
