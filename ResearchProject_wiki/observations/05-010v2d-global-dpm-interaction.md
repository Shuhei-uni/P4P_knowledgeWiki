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

The pair preserves the same broad combined-EWF configuration, but the available snapshots are not a strict same-checkpoint restart pair.

| Comparison item | `010V2d` — interaction off | `010V2d-2` — interaction on | Interpretation |
|---|---|---|---|
| Fluent evidence window | server `3`, Fluent `2024 R2`, monitor iterations `4–1520` | server `1`, Fluent `2024 R2`, monitor iterations `8–2068` | Different servers and final monitor windows. |
| Confirmed film wall / impingement model | `wall` / `stanton-rutland` | `wall` / `stanton-rutland` | Same confirmed wall-level EWF basis. |
| Wall splash / edge-separation evidence | splash enabled with four splashed particles; boundary separation permitted | splash enabled with four splashed particles; boundary separation permitted | Same reported wall-level optional-mechanism state. |
| Global DPM interaction | Off | On; source update every iteration; interval `1` | Intended primary change. |
| Original six-injection represented total | `5.86141 kg/s` | `5.88221 kg/s` | `+0.02080 kg/s` (`+0.36%`); normalize fate comparisons by each snapshot total. |
| Exact loaded case/data filename | not exposed | not exposed | Parent/checkpoint identity cannot be independently proven from the read-only artifacts. |

This is therefore a strong configuration-level diagnostic pair, but not yet a decisive physical A/B test. The small payload difference and unmatched final monitor state are retained explicitly rather than folded into the interaction effect.

## Observed local film differences

| Quantity | `010V2d` — global DPM off | `010V2d-2` — global DPM on | Observed change |
|---|---:|---:|---:|
| Film inventory | `0.05668 kg` | `0.07991 kg` | `+41%` |
| Maximum thickness | `0.125 mm` | `0.177 mm` | `+41%` |
| Area-averaged thickness | `0.960 µm` | `1.354 µm` | `+41%` |
| Derived mean film speed | `0.0533 m/s` | `0.0684 m/s` | `+28%` |
| Final film CFL | `0.00321` | `0.00387` | `+21%`, still low |

Relative to the clean `010V2` deposition control, `010V2d-2` also carries more final film inventory (`0.07991` versus `0.07150 kg`, about `+12%`) and has a larger maximum thickness (`0.177` versus `0.152 mm`, about `+16%`).

## Film localisation is preserved

The maximum-to-area-average thickness ratio is approximately `130` in both cases. Global interaction therefore increases the reported film inventory and thickness without materially changing the final snapshot's localisation ratio:

| Localisation measure | `010V2d` off | `010V2d-2` on | Reading |
|---|---:|---:|---|
| Maximum / area-average thickness | about `130` | about `131` | Both remain strongly localized films, not vessel-wide uniform coatings. |

This is a useful geometric observation: the coupled case appears to amplify the same local film pattern rather than redistribute it over the wall at the captured state.

## Observed DPM-fate differences

The total injection rates are slightly different between the snapshots, so the fraction of represented DPM mass is more informative than raw totals. From the printed terminal mass-flow rows:

| Fate | `010V2d` — off | `010V2d-2` — on | Direction |
|---|---:|---:|---|
| Direct steam-outlet escape | about `31.5%` | about `29.3%` | down by about `2.1` percentage points |
| Film absorption | about `66.9%` | about `68.1%` | up by about `1.2` percentage points |
| Bottom trapping | about `1.65%` | about `2.55%` | up by about `0.9` percentage points |

The intermediate droplet bins show the clearest absorption increase with global feedback:

| Diameter | Absorbed flow, interaction off | Absorbed flow, interaction on | Change |
|---:|---:|---:|---:|
| `56.27 µm` | `0.0119 kg/s` | `0.0196 kg/s` | `+65%` |
| `112.54 µm` | `0.112 kg/s` | `0.137 kg/s` | `+23%` |
| `168.81 µm` | `0.196 kg/s` | `0.223 kg/s` | `+14%` |

For the coarse `348.88 µm` bin, absorption remains dominant in both cases. The global-coupled transcript reports more splash events (`44` versus `20`), more separation events (`188` versus `120`), and additionally prints `7` stripping events. These are event/parcel counts, not represented secondary-particle masses.

### Full terminal-fate comparison by diameter

Each cell lists `escape / absorption / bottom trap / incomplete` represented mass flow in `kg/s`. These are original-particle terminal rows; splash, separation, and stripping event counters are deliberately excluded from this mass split.

| Diameter | `010V2d` — interaction off | `010V2d-2` — interaction on | Visible shift |
|---:|---:|---:|---|
| `5.63 µm` | `0.03793 / 0 / 0 / 8.76e-5` | `0.03779 / 3.50e-5 / 0 / 1.93e-4` | Still escape-dominant; a small absorbed component is reported when coupled. |
| `28.14 µm` | `0.15580 / 0 / 1.44e-4 / 1.44e-4` | `0.15540 / 4.32e-4 / 2.16e-4 / 0` | Small redistribution from direct escape toward absorption/trapping. |
| `56.27 µm` | `0.18140 / 0.01189 / 5.37e-4 / 2.68e-4` | `0.17390 / 0.01959 / 5.37e-4 / 8.94e-5` | Clearest intermediate-bin absorption increase. |
| `112.54 µm` | `0.27510 / 0.11200 / 3.06e-3 / 0` | `0.24970 / 0.13740 / 3.06e-3 / 0` | Interaction shifts represented mass from escape to absorption. |
| `168.81 µm` | `0.18970 / 0.19600 / 4.50e-3 / 0` | `0.16170 / 0.22310 / 6.11e-3 / 0` | Absorption dominance strengthens and bottom trapping increases. |
| `348.88 µm` | `1.00400 / 3.60100 / 8.84e-2 / 0` | `0.94740 / 3.62400 / 0.14010 / 1.64e-3` | Coarse-bin absorption remains dominant; trapping rises materially. |

The DPM fate transition stays in the same order—fine droplets escape, intermediate droplets shift toward the film, and the coarse class is absorption-dominant—but global interaction strengthens the reported film-absorption and bottom-trapping shares in the intermediate-to-coarse range.

### Secondary-event comparison

| Coarse `348.88 µm` event signal | `010V2d` off | `010V2d-2` on | Interpretation limit |
|---|---:|---:|---|
| Splash events | `20` | `44` | Event/parcel counts only; no represented splashed mass. |
| Edge-separation events | `120` | `188` | Not a separate terminal mass sink; no represented separated mass. |
| Stripping events | not printed | `7` | A reported coupled-branch signal, not an integrated stripped-mass result. |

These signals support a richer coupled EWF/DPM interaction at the coarse end. They must not be summed with original-particle fates or interpreted as a mass-conserved secondary-droplet population.

## Carrier and numerical response

The reported steam-outlet vapour flow barely changes (`81.4212` to `81.4193 kg/s`) and both cases retain zero reported liquid at the scoped steam outlet plus the same approximately `57.54%` selected-surface imbalance. In this reporting scope, global DPM interaction does not show a meaningful change in bulk outlet throughput.

The local DPM/film response comes with a less-settled carrier residual state:

| Residual at captured checkpoint | `010V2d` off | `010V2d-2` on |
|---|---:|---:|
| Continuity | `1.827e-3` | `2.875e-3` |
| Turbulent kinetic energy, `k` | `4.295e-2` | `2.057e-1` |
| Dissipation, `epsilon` | `1.181e-1` | `3.845e-1` |

At their reported endpoints, continuity is about `57%` higher in the coupled state, `k` is about `4.8×` higher, and epsilon is about `3.3×` higher. In contrast, scoped steam-outlet vapour changes by only `-0.00193 kg/s` (about `-0.002%`).

This distinction is important: the recorded response is local turbulence/DPM/film/fate change with a less-settled carrier state, not a demonstrated bulk-throughput change. It is consistent with DPM source feedback altering the local carrier/film field, but direct DPM-to-carrier source totals were not captured, so it is not proof of the causal mechanism.

## Current causal evidence chain

```text
global DPM interaction enabled
  -> reported increase in residual/turbulence state
  -> thicker, faster local wall film with unchanged localisation ratio
  -> greater intermediate-bin absorption and coarse-bin trapping
  -> more coarse splash/separation events and reported stripping events
```

The arrows describe the observed checkpoint sequence, not a closed mass/momentum proof. The missing bridge is time-integrated DPM-to-carrier and DPM-to-film source data from a common simulation window.

## Working conclusion

At the current checkpoints, enabling global DPM interaction is associated with a thicker, faster-moving film and a modest shift of represented DPM mass away from direct steam escape toward film absorption and bottom trapping. The strongest relative effect is in the intermediate droplets rather than the already absorption-dominated coarsest class.

This is a meaningful working observation for simulation planning. It is not yet a validated physical conclusion because the cases have different final iteration/time states, slightly different injection totals, no common history window, no direct carrier source totals, and an open carrier balance.

## Reasoning for the next simulations

Run the decisive paired experiment from one saved `010V2d` checkpoint:

1. preserve the combined-EWF case/data and create two copies;
2. keep global DPM interaction off in one and turn it on only in the other;
3. retain identical injection payload, transient timestep, EWF mechanisms, and wall settings;
4. run both across the same physical-time interval; and
5. compare time histories of DPM-to-carrier source, film DPM source, film mass, thickness, localisation ratio, CFL, carrier residuals, original/secondary particle fates, and all liquid outlets.

If the thicker-film and lower-direct-escape pattern persists in that matched pair, global DPM interaction becomes a justified physics sensitivity rather than a preliminary checkpoint association.

## Evidence

- [010V2 control result](../../Setups/reports/010V2/results.md)
- [010V2d combined-EWF result](../../Setups/reports/010V2d/results.md)
- [010V2d-2 global-DPM result](../../Setups/reports/010V2d-2/results.md)
- [010V2d original-particle fate rows](../../PyAnsys/output/ewf_dpm_diagnostics/010V2d-server3-20260722-dpm/dpm_zone_summary.csv)
- [010V2d-2 original-particle fate rows](../../PyAnsys/output/ewf_dpm_diagnostics/010V2d-2-20260722-dpm-complete/dpm_zone_summary.csv)
- [010V2d-2 interaction audit](../../PyAnsys/output/ewf_dpm_diagnostics/010V2d-2-20260722-audit/model_audit.json)
