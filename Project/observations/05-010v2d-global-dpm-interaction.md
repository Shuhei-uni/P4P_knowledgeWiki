> **Retired source:** ResearchProject_wiki/observations/05-010v2d-global-dpm-interaction.md
> **Migration note:** Historical wording, evidence status, and uncertainty labels are preserved; this Project copy is not a reinterpretation. Machine-generated artifacts remain with their original external owners; the retired written source is recoverable from Git history.

# Observation 05 — 010V2d/010V2d-2 Global DPM Interaction With EWF

## Comparison question

After splash, edge separation, and stripping are combined with EWF, what changes when global DPM interaction with the continuous phase is enabled?

## Intended controlled difference

`010V2d` is the combined-EWF state with global DPM interaction off. `010V2d-2` is intended to inherit that state and change only:

| Setting | `010V2d` | `010V2d-2` |
|---|---:|---:|
| Global DPM interaction with continuous phase | Off | On |
| DPM source update | not active globally | every flow iteration |
| DPM iteration interval | not active globally | `1` |

The most direct comparison is therefore `010V2d` versus `010V2d-2`. The simpler `010V2` deposition control provides context, but it cannot isolate global DPM interaction because its optional EWF mechanisms differ.

## Control integrity and comparison boundary

The pair preserves the same broad combined-EWF configuration, but the available snapshots are not a strict same-checkpoint restart pair. The update uses the latest completed checkpoint for each branch: `010V2d` at 5,000 iterations and `010V2d-2` at 4,189 iterations. No completed 5,000-iteration `010V2d-2` analysis is present.

| Comparison item | `010V2d` — interaction off | `010V2d-2` — interaction on | Interpretation |
|---|---|---|---|
| Fluent evidence window | server `1`, Fluent `2024 R2`, 5,000 iterations | server `3`, Fluent `2024 R2`, monitor iterations `128–4189` | Different servers and final monitor windows; the coupled branch has no 5,000 checkpoint. |
| Confirmed film wall / impingement model | `wall` / `stanton-rutland` | `wall` / `stanton-rutland` | Same confirmed wall-level EWF basis. |
| Wall splash / edge-separation evidence | splash enabled with four splashed particles; boundary separation permitted | splash enabled with four splashed particles; boundary separation permitted | Same reported wall-level optional-mechanism state. |
| Global DPM interaction | Off | On; source update every iteration; interval `1` | Intended primary change. |
| Original six-injection represented total | `5.95951 kg/s` | `5.91841 kg/s` | `-0.04110 kg/s` (`-0.69%`) in the coupled snapshot; normalize fate comparisons by each snapshot total. |
| Exact loaded case/data filename | not exposed | not exposed | Parent/checkpoint identity cannot be independently proven from the read-only artifacts. |

This is therefore a strong configuration-level diagnostic pair, but not yet a decisive physical A/B test. The small payload difference and unmatched final monitor state are retained explicitly rather than folded into the interaction effect.

## Observed local film differences

| Quantity | `010V2d` — global DPM off | `010V2d-2` — global DPM on | Observed change |
|---|---:|---:|---:|
| Film inventory | `0.20221 kg` | `0.16917 kg` | `-16.3%` |
| Maximum thickness | `0.457 mm` | `0.512 mm` | `+11.9%` |
| Area-averaged thickness | `3.425 µm` | `2.865 µm` | `-16.3%` |
| Derived mean film speed | `0.1331 m/s` | `0.1134 m/s` | `-14.8%` |
| Final film CFL | `0.00507` | `0.00569` | `+12.3%`, still low |

Relative to the new 5,000-iteration clean `010V2` deposition control, the coupled `010V2d-2` checkpoint has less final film inventory (`0.16917` versus `0.20449 kg`, about `-17%`) but a larger local maximum thickness (`0.512` versus `0.471 mm`, about `+8%`). This is a checkpoint comparison, not evidence that global interaction removes film mass.

## Film localisation is preserved

The maximum-to-area-average thickness ratio is approximately `130` in both cases. Global interaction therefore increases the reported film inventory and thickness without materially changing the final snapshot's localisation ratio:

| Localisation measure | `010V2d` off | `010V2d-2` on | Reading |
|---|---:|---:|---|
| Maximum / area-average thickness | about `133` | about `179` | Both remain strongly localized; the coupled checkpoint is more peaked in this snapshot. |

This is a useful geometric observation: both cases remain localized, but the latest coupled checkpoint is not the same film-shape response as the earlier comparison suggested. Its lower area-average and higher maximum thickness produce a more concentrated snapshot.

## Observed DPM-fate differences

The total injection rates are slightly different between the snapshots, so the fraction of represented DPM mass is more informative than raw totals. From the printed terminal mass-flow rows:

| Fate | `010V2d` — off | `010V2d-2` — on | Direction |
|---|---:|---:|---|
| Direct steam-outlet escape | about `16.9%` | about `19.5%` | up by about `2.6` percentage points in the unmatched coupled checkpoint |
| Film absorption | about `80.1%` | about `76.6%` | down by about `3.5` percentage points in the unmatched coupled checkpoint |
| Bottom trapping | about `2.99%` | about `3.84%` | up by about `0.85` percentage points |

The intermediate droplet bins show the clearest endpoint discrepancy between the two unmatched checkpoints:

| Diameter | Absorbed flow, interaction off | Absorbed flow, interaction on | Change |
|---:|---:|---:|---:|
| `56.27 µm` | `0.03649 kg/s` | `0.02450 kg/s` | `-33%` |
| `112.54 µm` | `0.1763 kg/s` | `0.1374 kg/s` | `-22%` |
| `168.81 µm` | `0.2463 kg/s` | `0.2147 kg/s` | `-13%` |

For the coarse `348.88 µm` bin, absorption remains dominant in both cases: `4.310 kg/s` off versus `4.158 kg/s` on. The latest coupled transcript reports `84` splash events, `222` separation events, and `5` stripping events, compared with `256`, `179`, and `11` in the 5,000-iteration off checkpoint. These are event/parcel counts, not represented secondary-particle masses.

### Full terminal-fate comparison by diameter

Each cell lists `escape / absorption / bottom trap / incomplete` represented mass flow in `kg/s`. These are original-particle terminal rows; splash, separation, and stripping event counters are deliberately excluded from this mass split.

| Diameter | `010V2d` — interaction off | `010V2d-2` — interaction on | Visible shift |
|---:|---:|---:|---|
| `5.63 µm` | `0.03779 / 7.01e-5 / 0 / 1.58e-4` | `0.03777 / not printed / 0 / 2.45e-4` | Fine class remains escape-dominant; coupled absorbed flow was not printed. |
| `28.14 µm` | `0.15180 / 3.02e-3 / 7.19e-4 / 5.03e-4` | `0.15530 / 7.19e-5 / 5.75e-4 / 7.19e-5` | Latest coupled checkpoint has more escape and less reported absorption. |
| `56.27 µm` | `0.15540 / 0.03649 / 1.789e-3 / 3.58e-4` | `0.16770 / 0.02450 / 1.878e-3 / 0` | Latest coupled checkpoint has more escape and less reported absorption. |
| `112.54 µm` | `0.20930 / 0.17630 / 9.529e-3 / 0` | `0.24360 / 0.13740 / 8.809e-3 / 3.596e-4` | Same directional shift as the 56.27 µm class. |
| `168.81 µm` | `0.13690 / 0.24630 / 0.01205 / 0` | `0.16090 / 0.21470 / 0.01456 / 0` | Absorption remains dominant, but is lower in the coupled checkpoint. |
| `348.88 µm` | `0.31660 / 4.31000 / 0.15410 / ~0` | `0.39040 / 4.15800 / 0.20140 / 0` | Coarse absorption remains dominant; coupled escape/trapping are higher. |

The DPM fate transition stays in the same order—fine droplets escape, intermediate droplets shift toward the film, and the coarse class is absorption-dominant. The updated table shows that the completed branches can differ materially in absorbed flow while retaining that ordering; the event counters still cannot be interpreted as extra mass sinks.

### Secondary-event comparison

| Coarse `348.88 µm` event signal | `010V2d` off | `010V2d-2` on | Interpretation limit |
|---|---:|---:|---|
| Splash events | `256` | `84` | Event/parcel counts only; no represented splashed mass. |
| Edge-separation events | `179` | `222` | Not a separate terminal mass sink; no represented separated mass. |
| Stripping events | `11` | `5` | Reported event signals, not integrated stripped-mass results. |

These signals support a richer coupled EWF/DPM interaction at the coarse end. They must not be summed with original-particle fates or interpreted as a mass-conserved secondary-droplet population.

## Carrier and numerical response

The reported steam-outlet vapour flow barely changes (`81.422408` to `81.422109 kg/s`) and both cases retain zero reported liquid at the scoped steam outlet plus the same approximately `57.54%` selected-surface imbalance. In this reporting scope, global DPM interaction does not show a meaningful change in bulk outlet throughput.

The local DPM/film response comes with a less-settled carrier residual state:

| Residual at captured checkpoint | `010V2d` off | `010V2d-2` on |
|---|---:|---:|
| Continuity | `8.209e-3` | `6.043e-3` |
| Turbulent kinetic energy, `k` | `1.133e-1` | `7.224e-3` |
| Dissipation, `epsilon` | `2.358e-1` | `4.552e-2` |

At their reported endpoints, continuity is about `26%` lower in the coupled state, `k` is about `94%` lower, and epsilon is about `81%` lower. These residual differences cannot be attributed to global interaction because the endpoints are unmatched. In contrast, scoped steam-outlet vapour changes by only `-0.000299 kg/s` (less than `0.001%`).

This distinction is important: the recorded response is local turbulence/DPM/film/fate change with a less-settled carrier state, not a demonstrated bulk-throughput change. It is consistent with DPM source feedback altering the local carrier/film field, but direct DPM-to-carrier source totals were not captured, so it is not proof of the causal mechanism.

## Current causal evidence chain

```text
global DPM interaction enabled
  -> different residual/turbulence endpoint at an unmatched checkpoint
  -> different local wall-film inventory/shape and DPM fate distribution
  -> coarse-bin absorption remains dominant, with coupled escape/trapping higher in the latest snapshot
  -> secondary splash/separation/stripping event counts also differ
```

The arrows describe the observed checkpoint sequence, not a closed mass/momentum proof. The missing bridge is time-integrated DPM-to-carrier and DPM-to-film source data from a common simulation window.

## Working conclusion

At the updated checkpoints, enabling global DPM interaction is associated with a different local film state and DPM fate distribution, but not with the earlier claimed increase in film absorption. The latest coupled snapshot has lower final film inventory and lower reported absorption for the 56.27–348.88 µm classes, while coarse absorption remains dominant. Because the coupled branch stops at 4,189 rather than 5,000 iterations, this reversal is a diagnostic discrepancy, not evidence that interaction reduces deposition.

This remains a working observation for simulation planning. It is not a validated physical conclusion because the cases have different final iteration/time states, slightly different injection totals, no common history window, no direct carrier source totals, and an open carrier balance. The old 1,520/2,068 comparison must no longer be used as the current quantitative summary.

## Reasoning for the next simulations

Run the decisive paired experiment from one saved `010V2d` checkpoint:

1. preserve the combined-EWF case/data and create two copies;
2. keep global DPM interaction off in one and turn it on only in the other;
3. retain identical injection payload, transient timestep, EWF mechanisms, and wall settings;
4. run both across the same physical-time interval; and
5. compare time histories of DPM-to-carrier source, film DPM source, film mass, thickness, localisation ratio, CFL, carrier residuals, original/secondary particle fates, and all liquid outlets.

If the thicker-film and lower-direct-escape pattern persists in that matched pair, global DPM interaction becomes a justified physics sensitivity rather than a preliminary checkpoint association.

## Evidence

- [010V2 control result](../experiments/purnanto-010V2-clean-ewf-deposition/results.md)
- [010V2d combined-EWF result](../experiments/purnanto-010V2d-ewf-combined-mechanisms/results.md)
- [010V2d-2 global-DPM result](../experiments/purnanto-010V2d-2-ewf-global-dpm/results.md)
- 010V2d 5,000-iteration original-particle fate rows (historical machine artifact path: `../../PyAnsys/output/ewf_dpm_diagnostics/010V2d-server1-20260723-5000-dpm/dpm_zone_summary.csv`; not migrated)
- 010V2d-2 4,189-iteration original-particle fate rows (historical machine artifact path: `../../PyAnsys/output/ewf_dpm_diagnostics/010V2d-2-server3-4189it-20260723-dpm/dpm_zone_summary.csv`; not migrated)
- 010V2d-2 4,189-iteration interaction audit (historical machine artifact path: `../../PyAnsys/output/ewf_dpm_diagnostics/010V2d-2-server3-4189it-20260723-audit/model_audit.json`; not migrated)
