# Fine-Mist DPM Size and Mass Distribution

## Decision record

| Field | Value |
|---|---|
| Status | `Recommended provisional project baseline` |
| Date | `2026-08-04` |
| Applies to | Future DPM and EWF reruns based on the `09cV2` branch |
| Total-liquid reference | `116.920 kg/s` |
| Baseline DPM diameter range | `5-100 um` |
| Coarse-tail sensitivity | `100-150 um` |
| Evidence basis | [Geothermal fine-mist size-cutoff evidence](../../../CFD_wiki/wiki/synthesis/geothermal-fine-mist-size-cutoff-evidence.md) |
| Validation status | Literature-informed and calculated; not a measured geothermal inlet PSD |

## 1. Project modelling decision

Use the DPM phase to represent only the **entrained fine mist** whose trajectory and capture depend strongly on the steam flow field.

Use the Eulerian liquid phase to represent:

- bulk brine;
- liquid films and slugs;
- coarse liquid structures;
- the portion of the inlet liquid assigned above the project DPM cutoff.

The baseline representation boundary is:

```text
DPM fine mist: 5-100 um
Eulerian/coarse liquid: primarily >100 um
```

This does not claim that a droplet larger than `100 um` can never be carried horizontally by steam. It defines what the project's DPM population is intended to represent.

A separate `100-150 um` coarse-tail sensitivity may be used to test whether excluding larger mist materially changes wall-film loading, carrier coupling, or steam-outlet carryover.

## 2. Why the inherited six-bin distribution is not the new baseline

The historical `09cV2` and downstream `010V2` cases use six inherited diameter classes:

| Diameter [um] | Historical 5% DPM flow [kg/s] | Historical DPM mass share |
|---:|---:|---:|
| `5.63` | `0.038013` | `0.6502%` |
| `28.14` | `0.156053` | `2.6694%` |
| `56.27` | `0.194066` | `3.3196%` |
| `112.54` | `0.390133` | `6.6735%` |
| `168.81` | `0.390133` | `6.6735%` |
| `348.88` | `4.677600` | `80.0137%` |
| **Total** | **`5.846000`** | **`100.0000%`** |

This was retained to isolate the DPM liquid-mass partition from the parent setup. It is historically useful, but it is not a defensible physical inlet PSD because:

1. the `348.88 um` class dominates the total DPM mass;
2. aggregate removal is therefore dominated by a coarse and easily separated class;
3. fine-droplet escape can be hidden by the mass weighting;
4. the six-bin table is a renormalised lower fragment of the broader archived Harwell distribution;
5. it does not clearly distinguish steam-carried mist from bulk/coarse liquid.

Existing results remain valid as **legacy-distribution diagnostics**. They must not be retroactively described as using the new fine-mist baseline.

## 3. Reasoning chain for the `100 um` cutoff

The detailed evidence is maintained in the CFD wiki. The project decision follows this chain:

1. A comparable geothermal separator with a `0.8 m` inlet and `22 m/s` average steam velocity began trapping droplets at approximately `20-30 um`.
2. Geothermal scrubbing evidence identifies droplets above approximately `50 um` as increasingly suitable for settling and inertial removal.
3. Project Stokes-number screening places the `St = 1` transition at approximately:
   - `106 um` for `20 m/s`;
   - `91 um` for `27.1 m/s`;
   - `84 um` for `32.14 m/s`.
4. An upper-bound Weber-number breakup screen gives an approximate stable diameter near `90 um` at the highest project velocity when the full inlet speed is treated as relative velocity.
5. No measured conventional geothermal separator-inlet PSD was found that would justify placing most of the DPM mass above `100 um`.

Therefore:

```text
d_max,DPM = 100 um
```

is selected as a common baseline cutoff for the full inlet-speed sweep. A fixed cutoff is important so that changing inlet velocity does not silently change the modelled droplet population.

## 4. Recommended diameter classes

Use the following intervals:

```text
5-10
10-20
20-30
30-40
40-60
60-80
80-100 um
```

Use the geometric midpoint of each interval as the representative injection diameter:

```text
d_i = sqrt(d_lower d_upper)
```

| Diameter interval [um] | Representative diameter [um] | Role |
|---:|---:|---|
| `5-10` | `7.07` | very fine mist |
| `10-20` | `14.14` | fine mist |
| `20-30` | `24.49` | literature-supported capture-transition region |
| `30-40` | `34.64` | mildly inertial mist |
| `40-60` | `48.99` | intermediate mist |
| `60-80` | `69.28` | coarse-mist transition |
| `80-100` | `89.44` | upper baseline tail |

The binning deliberately adds resolution around `20-60 um`, where the separator response is expected to change most strongly.

## 5. Mass-distribution derivation

### 5.1 Evidence limitation

The literature does not provide a complete measured geothermal separator-inlet mass distribution for the selected classes. The exact mass shares are therefore an **engineering prior**, not reported field measurements.

### 5.2 Selected cumulative distribution

Use a truncated Rosin-Rammler cumulative mass distribution:

```text
F(d) = 1 - exp[-(d / d_c)^n]
```

where:

- `F(d)` is cumulative DPM mass below diameter `d`;
- `d_c` is the characteristic size parameter;
- `n` is the spread parameter.

Two explicit project assumptions define the baseline shape:

```text
F(30 um) = 0.50
F(60 um) = 0.90
```

These assumptions mean:

- approximately half of the fine-mist mass lies below the comparable geothermal separator's `20-30 um` capture-transition range;
- approximately 90% lies below `60 um`, preventing the baseline from being dominated by coarse droplets.

Solving the two constraints gives:

```text
n = 1.7320
d_c = 37.070 um
```

The distribution is truncated to `5-100 um` and renormalised:

```text
w_i = [F(d_i,upper) - F(d_i,lower)] / [F(100) - F(5)]
```

## 6. Recommended baseline size and mass distribution

| Diameter interval [um] | Representative diameter [um] | DPM mass share | Cumulative DPM mass | Approx. number share* |
|---:|---:|---:|---:|---:|
| `5-10` | `7.07` | `6.998%` | `6.998%` | `68.2900%` |
| `10-20` | `14.14` | `19.931%` | `26.929%` | `24.3102%` |
| `20-30` | `24.49` | `21.680%` | `48.609%` | `5.0891%` |
| `30-40` | `34.64` | `18.688%` | `67.297%` | `1.5510%` |
| `40-60` | `48.99` | `22.738%` | `90.035%` | `0.6672%` |
| `60-80` | `69.28` | `8.016%` | `98.051%` | `0.0832%` |
| `80-100` | `89.44` | `1.949%` | `100.000%` | `0.0094%` |
| **Total** | — | **`100.000%`** | **`100.000%`** | **`100.0000%`** |

\*Approximate number shares assume spherical droplets represented at each geometric midpoint and use `number proportional to mass / d^3`.

Key consequences:

- approximately `48.6%` of DPM mass is below `30 um`;
- approximately `90.0%` is below `60 um`;
- only approximately `9.97%` lies above `60 um`;
- only approximately `1.95%` lies in the `80-100 um` upper-tail class;
- approximately `97.7%` of droplets by number are below `30 um`.

## 7. Five-percent DPM allocation

The `5%` DPM screening point retains the same total inlet accounting:

```text
m_liquid,total = 116.920 kg/s
f_DPM = 0.05
m_DPM = 5.846 kg/s
m_Eulerian,liquid = 111.074 kg/s
```

Only the size and mass distribution changes.

| Representative diameter [um] | DPM mass share | Recommended 5% DPM flow [kg/s] |
|---:|---:|---:|
| `7.07` | `6.998%` | `0.409128` |
| `14.14` | `19.931%` | `1.165149` |
| `24.49` | `21.680%` | `1.267410` |
| `34.64` | `18.688%` | `1.092501` |
| `48.99` | `22.738%` | `1.329262` |
| `69.28` | `8.016%` | `0.468606` |
| `89.44` | `1.949%` | `0.113944` |
| **Total** | **`100.000%`** | **`5.846000`** |

Removing the coarse legacy injections must not remove liquid from the inlet mass balance. Their represented liquid remains in the Eulerian liquid allocation.

## 8. Scaling across the DPM-fraction sweep

For any selected DPM fraction:

```text
m_DPM = f_DPM x 116.920 kg/s
m_Eulerian,liquid = (1 - f_DPM) x 116.920 kg/s
m_i = w_i x m_DPM
```

| Representative diameter [um] | 1% DPM | 2% DPM | 3% DPM | 4% DPM | 5% DPM | 10% DPM |
|---:|---:|---:|---:|---:|---:|---:|
| `7.07` | `0.081826` | `0.163651` | `0.245477` | `0.327303` | `0.409128` | `0.818256` |
| `14.14` | `0.233030` | `0.466060` | `0.699089` | `0.932119` | `1.165149` | `2.330298` |
| `24.49` | `0.253482` | `0.506964` | `0.760446` | `1.013928` | `1.267410` | `2.534820` |
| `34.64` | `0.218500` | `0.437000` | `0.655500` | `0.874001` | `1.092501` | `2.185002` |
| `48.99` | `0.265852` | `0.531705` | `0.797557` | `1.063410` | `1.329262` | `2.658525` |
| `69.28` | `0.093721` | `0.187442` | `0.281163` | `0.374884` | `0.468606` | `0.937211` |
| `89.44` | `0.022789` | `0.045578` | `0.068366` | `0.091155` | `0.113944` | `0.227888` |
| **Total DPM flow** | **`1.169200`** | **`2.338400`** | **`3.507600`** | **`4.676800`** | **`5.846000`** | **`11.692000`** |

All mass-flow values are in `kg/s`.

## 9. Fluent implementation rule

### Preferred implementation

Use seven separate surface injections, one for each representative diameter.

Advantages:

- direct per-size escaped, trapped, incomplete, and EWF-absorbed accounting;
- explicit readback of every mass flow;
- exact comparison with the historical six-injection cases;
- easier diagnosis of the separator cut-size response.

### Alternative implementation

Use a tabulated discrete diameter distribution if the active Fluent version exposes a reliable mass-fraction input and complete per-class reporting.

### Continuous Rosin-Rammler option

If Fluent generates the distribution internally, use provisionally:

| Parameter | Value |
|---|---:|
| Minimum diameter | `5 um` |
| Maximum diameter | `100 um` |
| Characteristic size | `37.070 um` |
| Spread parameter | `1.7320` |
| Diameter spacing | logarithmic preferred |
| Number of diameter samples | at least `7`; preferably `10-15` |

The explicit seven-injection implementation remains the project reference because it is easier to audit.

## 10. Controlled comparison with existing setups

The existing `09cV2` and `010V2d-2` results used the legacy six-bin distribution. To isolate the effect of the new PSD:

1. retain the same selected mesh and matured carrier checkpoint;
2. retain `f_DPM = 5%` for the first direct comparison;
3. retain `m_DPM = 5.846 kg/s` and `m_Eulerian,liquid = 111.074 kg/s`;
4. retain DPM interaction, tracking, EWF, wall, material, and numerical settings;
5. replace only the injection diameters and relative mass weights;
6. record the rerun as a new child case rather than overwriting the historical setup.

This comparison answers:

> How much of the historical removal efficiency and film loading was caused by assigning approximately 80% of DPM mass to the `348.88 um` class?

## 11. Required sensitivities

Minimum PSD sensitivity set:

1. **Legacy reference:** historical six-bin distribution.
2. **Fine-mist baseline:** recommended `5-100 um` distribution.
3. **Fine-shifted:** same range with more mass below `30 um`.
4. **Coarse-tail:** add `100-125` and `125-150 um` while keeping total DPM mass fixed.

Report for every class:

- injected mass flow;
- tracked parcel count;
- escaped, trapped, incomplete, and EWF-absorbed fractions;
- residence time where available;
- mass-weighted and number-weighted aggregate efficiency;
- carrier residual and mass-balance state;
- film inventory, film source, and film outflow histories when EWF is active.

## 12. Decision limits

This recommendation must continue to be labelled:

> **Recommended provisional fine-mist PSD — assumed mass shape, literature-informed cutoff.**

It is not a measured geothermal inlet distribution. Revisit the decision if any of the following become available:

- measured separator-inlet droplet histogram;
- measured mist mass fraction or number concentration;
- validated upstream breakup/coalescence simulation;
- field-specific piping, flashing, and wall-film data;
- evidence that the `100-150 um` sensitivity materially changes the target carryover prediction.

## Linked evidence and implementations

- [Detailed CFD evidence for the cutoff](../../../CFD_wiki/wiki/synthesis/geothermal-fine-mist-size-cutoff-evidence.md)
- [Broader geothermal inlet-droplet inventory](../../../CFD_wiki/wiki/synthesis/geothermal-separator-inlet-droplets-and-carryover.md)
- [09cV2 DPM partition setup](../../../Setups/active/09cV2-skoog-partition-injection-control.md)
- [010V2d-2 global-DPM/EWF setup](../../../Setups/active/010V2d-2-ewf-combined-global-dpm.md)
