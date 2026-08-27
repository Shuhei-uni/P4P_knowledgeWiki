> **Legacy source:** Setups/past/reported/04-mixed-wet-half-actual-area.md  
> **Migration note:** Historical wording, evidence status, and uncertainty labels are preserved; this Project copy is not a reinterpretation. Raw and machine-generated artifacts remain at their legacy paths.

# Mixed Wet-Half Actual-Area Simulation Report

## Setup metadata

| Field | Value |
|---|---|
| Setup ID | `04` |
| Lifecycle | `reported` |
| Role | actual-area calculation and DPM diagnostic |
| Parent setup | [03](../purnanto-03-mixed-wet-half-velocity-inlet/setup.md) |
| Evidence-use label | DPM diagnostic only; flux diagnostic |
| Outcome | needs follow-up |
| Linked report | [04 results](results.md) |

## 1. Purpose

Start a report-facing record for the mixed wet-half velocity-inlet simulation using the actual inlet area measured from the current geometry.

This report currently records the inlet mass-flow calculation. Later sections are placeholders for mass flux, separator efficiency, contour interpretation, velocity-field interpretation, and other useful post-processing values.

Geometry naming note:

- this actual-area branch uses the `purnanto` geometry label;
- inlet boundary style is a separate choice from geometry naming, so this remains `purnanto` even though it is a split-inlet branch.

Correction note:

- Earlier calculation used the reported spiral-inlet velocity `26.81 m/s` directly with the measured actual inlet area, which gives `195.36 kg/s`.
- For the report-facing Purnanto `1600 kJ/kg` setup, use Purnanto's target total inlet mass flow `197.61 kg/s` and calculate the required velocity from the actual inlet area.
- The corrected actual-area velocity is `27.12 m/s`.

## 2. Setup Identity

| Item | Value |
|---|---:|
| Geometry | `purnanto` spiral-inlet BOC separator |
| Inlet representation | mixed wet-half split inlet |
| Boundary type | velocity inlet on both inlet halves |
| Steam-only inlet velocity | `27.12 m/s` |
| Wet-half inlet velocity | `27.12 m/s` |
| Steam-only inlet liquid volume fraction | `0.0` |
| Wet-half inlet liquid volume fraction | `0.018656` |
| Wet-half steam volume fraction | `0.981344` |
| Liquid density | `881.77 kg/m3` |
| Steam density | `5.73 kg/m3` |
| Actual inlet-half area | `2.6209e5 mm2 = 0.26209 m2` |
| Purnanto `1600 kJ/kg` target liquid flow | `116.92 kg/s` |
| Purnanto `1600 kJ/kg` target steam flow | `80.69 kg/s` |
| Purnanto `1600 kJ/kg` target total flow | `197.61 kg/s` |

Evidence labels:

- `Reported`: baseline Purnanto operating values reused through the parent setup report.
- `User-reported`: actual inlet-half area measured from the current geometry.
- `Calculated`: mass-flow values computed from velocity, density, volume fraction, and area.

Parent setup reference:

- `03-mixed-wet-half-velocity-inlet.md`

## 3. Inlet Mass-Flow Calculation

Assumption:

- `2.6209e5 mm2` is the area of each split inlet half, not the combined area of both halves (`User-reported`, interpreted from geometry context).

Area conversion:

```text
A_half = 2.6209e5 mm2 * 1e-6
A_half = 0.26209 m2
```

Mass-flow formula:

```text
m_dot_phase = alpha_phase * rho_phase * V * A
```

Velocity required to preserve Purnanto's `1600 kJ/kg` target mass flow:

```text
Q_liquid = 116.92 / 881.77 = 0.13260 m3/s
Q_steam  = 80.69 / 5.73    = 14.08202 m3/s
Q_total  = 14.21462 m3/s

A_full = 2 * 0.26209 = 0.52418 m2
V = Q_total / A_full
V = 14.21462 / 0.52418
V = 27.12 m/s
```

### Wet Outer Inlet

Inputs:

```text
A_wet = 0.26209 m2
V_wet = 27.12 m/s
alpha_liquid = 0.018656
alpha_steam = 0.981344
rho_liquid = 881.77 kg/m3
rho_steam = 5.73 kg/m3
```

Calculated wet-inlet phase mass flow:

```text
liquid through wet outer inlet = 116.92 kg/s
steam through wet outer inlet  = 39.97 kg/s
total through wet outer inlet  = 156.89 kg/s
```

### Steam Inner Inlet

Inputs:

```text
A_steam = 0.26209 m2
V_steam = 27.12 m/s
alpha_liquid = 0.0
alpha_steam = 1.0
rho_steam = 5.73 kg/m3
```

Calculated steam-inlet phase mass flow:

```text
liquid through steam inner inlet = 0.00 kg/s
steam through steam inner inlet  = 40.72 kg/s
total through steam inner inlet  = 40.72 kg/s
```

### Total Inlet Mass Flow

```text
total liquid inlet = 116.92 kg/s
total steam inlet  = 80.69 kg/s
total inlet flow   = 197.61 kg/s
```

Steam quality by inlet mass:

```text
x = m_dot_steam / (m_dot_liquid + m_dot_steam)
x = 80.69 / 197.61
x = 0.4083
```

This now matches the original Purnanto `1600 kJ/kg` target mass flow while using the measured actual inlet-half area.

## 3A. Pure Liquid / Pure Steam Equal-Velocity Split

Purpose:

- Replace the mixed wet-half inlet with a sharper inlet where one side is pure liquid and the other side is pure steam.
- Preserve Purnanto's `1600 kJ/kg` liquid and steam mass-flow targets.
- Keep one common inlet velocity across both inlet zones.

Inputs:

```text
W = 0.724 m
H = 0.724 m
A_total = 0.724 * 0.724 = 0.524176 m2

m_dot_liquid = 116.92 kg/s
m_dot_steam  = 80.69 kg/s
rho_liquid   = 881.77 kg/m3
rho_steam    = 5.73 kg/m3
```

Volumetric flows:

```text
Q_liquid = 116.92 / 881.77 = 0.1325969 m3/s
Q_steam  = 80.69 / 5.73    = 14.0820244 m3/s
Q_total  = 14.2146214 m3/s
```

Common inlet velocity:

```text
V = Q_total / A_total
V = 14.2146214 / 0.524176
V = 27.1180 m/s
```

Required areas:

```text
A_liquid = Q_liquid / V = 0.0048896 m2
A_steam  = Q_steam  / V = 0.5192864 m2

A_liquid / A_total = 0.009328 = 0.9328 %
A_steam  / A_total = 0.990672 = 99.0672 %
```

Split location along `x` if the inlet height remains `0.724 m`:

```text
x_liquid_width = A_liquid / 0.724 = 0.0067536 m
x_steam_width  = A_steam  / 0.724 = 0.7172464 m
```

Implementation note:

- Put the split line `0.00675 m` from the liquid-side edge, or equivalently `0.71725 m` from the steam-side edge.
- This should be mapped to the actual inlet orientation as outer-wall liquid versus inner/core steam; do not rely only on screen-left/screen-right naming.

Mass-flow check:

```text
liquid = 881.77 * 27.1180 * 0.0048896 = 116.92 kg/s
steam  = 5.73   * 27.1180 * 0.5192864 = 80.69 kg/s
total  = 197.61 kg/s
```

## 4. Mass Flux

To be expanded after post-processing.

Initial calculated inlet mass flux values:

| Quantity | Value |
|---|---:|
| Wet outer inlet total mass flux | `598.59 kg/m2-s` |
| Wet outer inlet liquid mass flux | `446.10 kg/m2-s` |
| Wet outer inlet steam mass flux | `152.49 kg/m2-s` |
| Steam inner inlet mass flux | `155.39 kg/m2-s` |
| Combined inlet average mass flux | `376.99 kg/m2-s` |

Notes to add later:

- compare the combined inlet mass flux against any analytical or literature sanity band available for the separator;
- report whether local high-velocity or high-liquid-loading regions correlate with liquid carryover;
- keep this as an inlet-loading metric, not a separator-efficiency metric by itself.

## 5. Separator Efficiency

Flux report from the current simulation:

### Steam Phase Flux

Reported order: liquid inlet, outlet, steam inlet, net result.

```text
steam through liquid/wet inlet =  39.97615638734752 kg/s
steam through outlet           = -81.45237886488366 kg/s
steam through steam inlet      =  40.73612962156758 kg/s
steam net result               =  -0.7400929 kg/s
```

Steam balance:

```text
steam in  = 39.97615638734752 + 40.73612962156758
steam in  = 80.71228600891510 kg/s
steam out = 81.45237886488366 kg/s
steam net = -0.74009285596856 kg/s
```

### Liquid Phase Flux

Reported order: liquid inlet, outlet, steam inlet, net result.

```text
liquid through liquid/wet inlet = 115.5160537753228 kg/s
liquid through outlet           =  -2.498616005104147 kg/s
liquid through steam inlet      =  -0 kg/s
liquid net result               = 113.0174 kg/s
```

Liquid balance:

```text
liquid in  = 115.5160537753228 kg/s
liquid out = 2.498616005104147 kg/s
liquid net = 113.01743777021865 kg/s
```

### Calculated Efficiency

Using liquid outlet flow as separated liquid:

```text
liquid separation efficiency = liquid outlet / liquid inlet
liquid separation efficiency = 2.498616005104147 / 115.5160537753228
liquid separation efficiency = 0.02163
liquid separation efficiency = 2.16 %
```

Liquid still retained or not removed at this report state:

```text
unremoved liquid fraction = liquid net / liquid inlet
unremoved liquid fraction = 113.0174 / 115.5160537753228
unremoved liquid fraction = 97.84 %
```

Outlet steam dryness, using the reported outlet steam and liquid flux magnitudes:

```text
outlet steam dryness = steam outlet / (steam outlet + liquid outlet)
outlet steam dryness = 81.45237886488366 / (81.45237886488366 + 2.498616005104147)
outlet steam dryness = 0.97024
outlet steam dryness = 97.02 %
```

Suggested reporting structure:

```text
liquid separation efficiency = liquid leaving brine outlet / total liquid inlet
steam purity or steam outlet dryness = steam mass at steam outlet / total mass at steam outlet
liquid carryover = liquid leaving steam outlet / total liquid inlet
```

Use only after the outlet mass-flow reports are stable enough to support quantitative interpretation.

## 6. DPM Particle Injection Notes

### Purnanto-Style Particle Mass-Flow Finding

The nine candidate droplet injection mass-flow values sum to the Purnanto `1600 kJ/kg` liquid mass-flow condition:

```text
5.846 + 13.708474 + 15.722479 + 15.224784 + 7.52414
+ 19.7663 + 17.859486 + 17.182465 + 4.085872
= 116.92 kg/s
```

This matches the reported liquid inlet mass flow for the original `1600 kJ/kg` case, so these values should be treated as droplet-size mass-flow weights rather than arbitrary injection amounts.

Particle injection values used:

| Injection | Droplet diameter `m` | Purnanto mass-flow weight `kg/s` |
|---:|---:|---:|
| `1` | `1.29E-04` | `5.846` |
| `2` | `2.15E-04` | `13.708474` |
| `3` | `3.02E-04` | `15.722479` |
| `4` | `3.88E-04` | `15.224784` |
| `5` | `4.31E-04` | `7.52414` |
| `6` | `5.60E-04` | `19.7663` |
| `7` | `7.32E-04` | `17.859486` |
| `8` | `9.91E-04` | `17.182465` |
| `9` | `1.25E-03` | `4.085872` |
|  | **Total** | **`116.92`** |

Decision for this run:

- Use the original Purnanto mass-flow weights rather than actual-area-scaled values.
- Rationale: the difference between the current actual-area liquid inlet (`115.516 kg/s`) and Purnanto's original liquid inlet (`116.92 kg/s`) is small, so using the source-paper values is acceptable for a Purnanto-matching DPM comparison.

For this actual-area run, the liquid inlet from the flux report is:

```text
liquid inlet = 115.5160537753228 kg/s
```

So strict actual-area scaling would multiply each Purnanto droplet-bin mass flow by:

```text
115.5160537753228 / 116.92 = 0.98799
```

Practical interpretation:

- use the original mass-flow values for strict Purnanto `1600 kJ/kg` comparison;
- use the scaled values for consistency with the current actual-area run;
- do not increase physical injected mass flow just to reduce incomplete tracks.

### DPM Step Sensitivity Check

Test condition:

- Injection tested: injection 1 / particle size 1.
- Initial setup: random initial setup.
- Particle streams: `100`.
- Stochastic tracking: enabled.
- Eddy interaction/effect: enabled.
- Number of tries: `5`.
- Effective total stochastic tracks: `500`.

| Max steps | Step factor | DPM iteration interval | Trapped | Incomplete | Escaped |
|---:|---:|---:|---:|---:|---:|
| `50,000` | `5` | `10` | `158` | `342` | `0` |
| `500,000` | `5` | `10` | `158` | `342` | `0` |
| `50,000` | `2` | `2` | `159` | `341` | `0` |
| `50,000` | `1` | `1` | `157` | `343` | `0` |
| `500,000` | `2` | `2` | `159` | `341` | `0` |

Interpretation:

- Increasing max steps from `50,000` to `500,000` did not reduce incomplete tracks for this tested particle case.
- Reducing step factor and DPM iteration interval produced only negligible changes in trapped/incomplete counts.
- The incomplete-track problem is therefore unlikely to be solved by simply increasing max tracking steps for this setup.
- This is consistent with Purnanto's reported issue that incomplete particles remained difficult even after increasing Euler step limits.

Provisional future DPM setting:

```text
max steps = 50,000
step factor = 2
DPM iteration interval = 2
particle streams = 100
tries = 5
effective stochastic tracks = 500 per injection
```

Evidence-use label:

`DPM diagnostic only`.

This setting is selected as a practical baseline for future testing until a better tracking method is found. It should not yet be treated as final separator-efficiency evidence because incomplete tracks remain dominant.

### DPM Stream-Count Sensitivity Check

Fixed settings:

```text
max steps = 50,000
step factor = 2
DPM iteration interval = 2
tries = 5
stochastic tracking tries = 5
random eddy lifetime = on
```

Stream-count tests:

| Particle streams | Effective total tracks | Trapped | Incomplete | Escaped |
|---:|---:|---:|---:|---:|
| `100` | `500` | `159` | `341` | `0` |
| `200` | `1000` | `316` | `684` | `0` |
| `500` | `2500` | `824` | `1676` | `0` |
| `1000` | `5000` | `1711` | `3289` | `0` |

Percentage summary:

| Total tracks | Trapped | Incomplete |
|---:|---:|---:|
| `500` | `31.8 %` | `68.2 %` |
| `1000` | `31.6 %` | `68.4 %` |
| `2500` | `33.0 %` | `67.0 %` |
| `5000` | `34.2 %` | `65.8 %` |

Interpretation:

- Increasing total stochastic tracks from `500` to `5000` did not remove the incomplete-track problem.
- The trapped fraction stayed in a narrow band of approximately `31.6-34.2 %`.
- The incomplete fraction stayed dominant at approximately `65.8-68.4 %`.
- The higher stream counts improve sampling resolution, but they do not change the underlying trajectory-completion issue.

## 7. Key Visual Findings

Pending contour and vector review.

Add findings under these headings:

### Liquid Volume Fraction Contours

- pending

### Steam Volume Fraction Contours

- pending

### Velocity Magnitude and Vectors

- pending

### Pressure Field

- pending

### Streamlines or Pathlines

- pending

## 8. Useful Values To Add Later

- residual state at selected iteration count;
- global mass imbalance;
- phase mass flow at each outlet;
- pressure drop between inlet and outlets;
- maximum and average velocity near inlet, vessel wall, core, steam outlet, and brine outlet;
- liquid volume fraction near the steam outlet intake;
- water inventory stability if an initialized water pool is used;
- convergence label and evidence-use label.

## 9. Current Evidence-Use Label

`Setup calculation only`.

The inlet mass-flow values are usable as boundary-condition documentation. Separator efficiency and performance claims are not yet filled because outlet fluxes, residual history, and visual post-processing evidence still need to be added.
