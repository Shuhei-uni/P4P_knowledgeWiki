# Evidence: Geothermal Fine-Mist Droplet Size and DPM Cutoff

## Scope

This page collects the physical and literature evidence used to decide which liquid-droplet sizes should be represented as steam-carried DPM at the inlet of the project geothermal separator.

It does **not** define the final project mass distribution. The project-specific decision, fitted distribution, and Fluent allocation are maintained separately in:

- [Fine-mist DPM size and mass distribution](../../../Project/experiments/phase-03-dpm-carryover-and-coupling/purnanto-09cV3-fine-mist-psd/fine-mist-interpretation.md)

The practical question is:

> At inlet steam velocities of approximately `20-32.14 m/s`, which liquid sizes should be treated as entrained mist, and which should remain in the Eulerian liquid representation?

## Evidence boundary

- `Reported`: stated directly by a cited source.
- `Calculated`: derived from stated equations and approximate project operating conditions.
- `Inferred`: a physical interpretation supported by the evidence but not directly measured.
- `Missing`: no complete measured conventional geothermal separator-inlet droplet-size distribution was found.

A critical distinction is maintained throughout:

- a droplet can be transported horizontally by fast steam without closely following a curved streamline;
- a droplet measured after a separator may have formed through coalescence or wall-film re-entrainment;
- a broad pipeline droplet distribution is not automatically the same population as the fine mist intended for DPM coupling.

## 1. Purnanto and the inherited Harwell distribution

Purnanto, Zarrouk, and Cater used a Harwell-based estimate for DPM droplet tracking after solving the continuous carrier field. The Harwell method estimates a characteristic droplet size and relates the Sauter mean and median diameters through:

```text
x_med = 1.42 x_sa
```

The cited standard mass distribution places approximately `5%` of mass below `0.3 x_med` and the upper end near `2.9 x_med`.

The project archive contains nine original Fluent injections:

| Diameter [um] | Original flow weight [kg/s] |
|---:|---:|
| `5.63` | `0.19` |
| `28.14` | `0.78` |
| `56.27` | `0.97` |
| `112.54` | `1.95` |
| `168.81` | `1.95` |
| `348.88` | `23.38` |
| `562.70` | `29.23` |
| `844.06` | `29.23` |
| `1631.84` | `29.23` |

This archived implementation is a broad pipeline-scale distribution extending into millimetre-sized liquid structures. It should not be interpreted as evidence that the steam-carried mist entering the project separator is physically dominated by `348-1632 um` droplets.

The approximately `10 um` diameter used in Purnanto's multiphase setup assumptions and the archived nine-bin DPM weighting are distinct modelling inputs. They should not be combined into a single measured inlet PSD.

### Consequence for the inherited six-bin project setup

The later six-bin setup removed the `562.70`, `844.06`, and `1631.84 um` injections and renormalised the remaining lower portion. Because the retained `348.88 um` class originally carried `20%` of the full Harwell mass while the retained lower six classes together carried only approximately `25%`, renormalisation makes the `348.88 um` class approximately `80%` of the new DPM mass.

That result is mathematically traceable, but it is not a newly derived physical inlet distribution.

## 2. Comparable geothermal separator evidence

### Takahashi et al. 2004

Takahashi et al. analysed a geothermal mist separator with:

- inlet pipe diameter `0.8 m`;
- average steam velocity `22 m/s`;
- tangential steam and droplet entry.

For the shorter `3.4 m` separator, the minimum trapped droplet size was approximately `20-30 um`.

This evidence is highly relevant to the present project because the project inlet width is approximately `0.724 m` and the studied inlet velocity range is `20-32.14 m/s`.

**Interpretation:** the `20-30 um` result is a capture threshold for that separator, not an inlet maximum. It demonstrates that droplets in this fine range already possess enough inertia for separation to begin becoming effective. Larger droplets should become progressively easier to separate and progressively less faithful to the steam streamline.

Source:

- Takahashi, K. et al. (2004), *On Flow Dynamics and Separation Efficiency in Mist Separators Composed of Coaxial Cylinders for Geothermal Power Plant*, DOI [`10.1252/kakoronbunshu.30.200`](https://doi.org/10.1252/kakoronbunshu.30.200).

### Arifien, Zarrouk, and Kurniawan 2015

The geothermal scrubbing-line study concluded that gravity and scrubbing-line residence are more useful for droplets larger than approximately `50 um`; much longer pipe distances are required for smaller droplets.

This supports a physical transition around `30-60 um`:

- below this range, droplets behave more like persistent entrained mist;
- above this range, settling, inertial migration, and wall interaction become increasingly important.

Source:

- Arifien, B. N., Zarrouk, S. J., and Kurniawan, W. (2015), *Scrubbing Lines in Geothermal Power Generation Systems*, 37th New Zealand Geothermal Workshop. Public author copy: <https://www.researchgate.net/publication/283949286_SCRUBBING_LINES_IN_GEOTHERMAL_POWER_GENERATION_SYSTEMS>.

### Machemer and Jonas 2004

Machemer and Jonas monitored droplet mass flow and droplet-size distribution in geothermal separator exhaust at Coso. The downstream distribution included substantial droplets in approximately the `50-200 um` range.

This proves that coarse droplets can appear in separated steam systems, but it does not establish the original well-to-separator inlet PSD. Downstream droplets may be affected by:

- coalescence;
- wall-film collection;
- film stripping or re-entrainment;
- local separator and piping geometry.

Source:

- Machemer, L., and Jonas, O. (2004), *Monitoring of Geothermal Steam Moisture Separator Efficiency*, *Geothermics* 33(5), DOI [`10.1016/j.geothermics.2003.10.004`](https://doi.org/10.1016/j.geothermics.2003.10.004).

### Rivera-Diaz and Koorey 2021

The Rotokawa/RGEN separator study records a demister supplier criterion of approximately `99%` removal for droplets larger than `14 um`, while explicitly noting that the droplet distribution was unknown.

This is useful as evidence that fine droplets are important to steam-quality performance, but it is not a measured inlet mass distribution.

Source:

- Rivera-Diaz, A., and Koorey, K. (2021), *Steam Separator Selection for a Geothermal Power Station*, New Zealand Geothermal Workshop: <https://www.worldgeothermal.org/pdf/IGAstandard/NZGW/2021/120.pdf>.

## 3. Flow-following screening with Stokes number

There is no universal diameter above which steam cannot transport a droplet. A useful screening metric is the Stokes number:

```text
St = tau_p U / L

tau_p = rho_l d^2 / (18 mu_g)
```

For screening only, use:

- characteristic inlet length `L = 0.724 m`;
- inlet speeds `20`, `27.1`, and `32.14 m/s`;
- approximate saturated-steam viscosity near project pressure;
- liquid-water density near project pressure.

Typical interpretation:

- `St < 0.1`: follows steam curvature reasonably closely;
- `0.1 < St < 1`: transitional inertial response;
- `St > 1`: strong departure from curved streamlines and increasing wall-impact tendency.

Approximate project screening values are:

| Diameter [um] | `St` at 20 m/s | `St` at 27.1 m/s | `St` at 32.14 m/s | Physical interpretation |
|---:|---:|---:|---:|---|
| `20` | `0.035` | `0.048` | `0.057` | closely steam-following |
| `30` | `0.079` | `0.108` | `0.128` | near fine-mist transition |
| `40` | `0.141` | `0.191` | `0.227` | mild inertia |
| `50` | `0.221` | `0.299` | `0.355` | increasingly inertial |
| `75` | `0.497` | `0.673` | `0.798` | strong transition |
| `100` | `0.883` | `1.196` | `1.418` | strong wall-separation tendency |
| `150` | `1.99` | `2.69` | `3.19` | predominantly inertial |
| `200` | `3.53` | `4.78` | `5.67` | poor streamline following |
| `350` | `10.8` | `14.7` | `17.4` | coarse-liquid behaviour |

The corresponding approximate `St = 1` diameters are:

| Inlet speed | Approximate `St = 1` diameter |
|---:|---:|
| `20 m/s` | `106 um` |
| `27.1 m/s` | `91 um` |
| `32.14 m/s` | `84 um` |

These calculations support using approximately `100 um` as the upper edge of a fine-mist representation across the complete velocity sweep.

## 4. Aerodynamic breakup screening

A newly stripped or slowly moving droplet can initially experience a large steam-droplet slip velocity. The gas Weber number is:

```text
We_g = rho_g U_rel^2 d / sigma
```

Pilch and Erdman provide a widely used acceleration-induced breakup framework. For low-viscosity water droplets, `We approximately 12` is commonly used as an approximate onset of bag-type breakup.

Using approximate saturated-steam and water properties near the project pressure, and treating the full inlet velocity as an upper-bound relative velocity, gives:

| Relative velocity | Approximate diameter at `We = 12` |
|---:|---:|
| `20 m/s` | `230 um` |
| `27.1 m/s` | `125 um` |
| `32.14 m/s` | `90 um` |

This is not a strict cutoff. A droplet already moving near steam velocity experiences much lower slip and may remain intact at a larger diameter. However, the calculation makes a fine-mist baseline extending far beyond `100 um` difficult to justify at the highest project inlet speed.

Source:

- Pilch, M., and Erdman, C. A. (1987), *Use of Breakup Time Data and Velocity History Data to Predict the Maximum Size of Stable Fragments for Acceleration-Induced Breakup of a Liquid Drop*, *International Journal of Multiphase Flow* 13(6), DOI [`10.1016/0301-9322(87)90063-2`](https://doi.org/10.1016/0301-9322(87)90063-2).

Property framework:

- [IAPWS-IF97 thermodynamic properties](https://iapws.org/relguide/IF97-Rev.html)
- [IAPWS viscosity formulation](https://www.iapws.org/relguide/viscosity.html)
- [IAPWS surface-tension formulation](https://www.iapws.org/relguide/Surf-H2O.html)

## 5. Gravity is not the primary inlet cutoff

Even a coarse droplet already travelling horizontally with fast steam may require a long distance to settle through the full inlet height. Therefore, the argument for assigning large liquid structures to the Eulerian phase should not be:

> droplets above `100 um` cannot be transported by steam.

The stronger interpretation is:

> droplets above the selected cutoff are not the fine, steam-following mist population that the project DPM phase is intended to represent. They are increasingly inertial and are more naturally grouped with bulk liquid, films, slugs, or coarse breakup structures unless a dedicated coarse-droplet or re-entrainment experiment is being performed.

## 6. Evidence synthesis

The literature and screening calculations identify the following physical bands:

| Diameter band | Evidence-based interpretation |
|---:|---|
| `<20 um` | persistent fine mist; strongly steam-following |
| `20-30 um` | comparable geothermal separator begins trapping droplets |
| `30-60 um` | key transition from mist-following to increasingly effective inertial capture |
| `60-100 um` | coarse mist; increasingly separated from steam curvature |
| `100-150 um` | uncertain coarse tail; useful as sensitivity only |
| `>150 um` | predominantly coarse-liquid representation for the baseline model |

The evidence supports a project baseline DPM range of:

```text
5-100 um
```

with `100-150 um` retained as a separate coarse-tail sensitivity.

## 7. Limitations and open evidence gaps

- No complete measured conventional geothermal separator-inlet PSD was found.
- Takahashi et al. report a separator capture threshold, not the inlet population.
- Machemer and Jonas report separator exhaust, not the original inlet.
- The Stokes calculation is a characteristic-scale screen; actual trajectories require the CFD velocity field and a Reynolds-dependent drag law.
- The breakup screen depends on relative velocity, not bulk steam velocity alone.
- Coalescence, breakup, flashing, wall-film stripping, and inlet spatial nonuniformity can alter the real distribution.
- The total mist mass fraction remains independent of the size cutoff and must be tested separately.

## Related project evidence

- [Geothermal separator inlet droplets and carryover inventory](geothermal-separator-inlet-droplets-and-carryover.md)
- [Droplets, carryover, and re-entrainment](../physics-basis/droplets-carryover-and-re-entrainment.md)
- [Purnanto source extraction](../sources/purnanto-2013-cfd-geothermal-separator.md)
- [Project fine-mist DPM decision](../../../Project/experiments/phase-03-dpm-carryover-and-coupling/purnanto-09cV3-fine-mist-psd/fine-mist-interpretation.md)
- [Archived Purnanto injection settings](../../../PyAnsys/cases/actual_setup_archives/purnanto-enthalpy1600-particle-extract/README.md)
