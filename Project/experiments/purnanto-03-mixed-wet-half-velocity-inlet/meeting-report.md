> **Legacy source:** Meeting report/mixed_wet_half_brief_meeting_report.md  
> **Migration note:** Historical wording, evidence status, and uncertainty labels are preserved; this Project copy is not a reinterpretation. Raw and machine-generated artifacts remain at their legacy paths.

# Mixed Wet-Half Simulation — Brief Meeting Report

## Purpose

This note summarises the current mixed wet-half spiral-inlet BOC separator simulation. The aim is to clearly separate:

1. what was calculated,
2. what was set up and tested, and
3. what was found from the current results.

The main clarification is that this case used the reported Purnanto inlet velocity of **26.81 m/s**, applied to the current geometry. The inlet velocity was **not recalculated using the actual inlet-half area** to force the total mass flow to exactly match the Purnanto 1600 kJ/kg case.

---

## 1. What Was Calculated

### 1.1 Reference Purnanto inlet condition

The Purnanto 1600 kJ/kg reference inlet values were used as the comparison target.

| Quantity | Value |
|---|---:|
| Liquid mass flow | 116.92 kg/s |
| Steam mass flow | 80.69 kg/s |
| Total mass flow | 197.61 kg/s |
| Steam quality by mass | 0.4083 |

The steam quality is calculated as:

$$
x = \frac{\dot{m}_{\text{steam}}}
{\dot{m}_{\text{liquid}} + \dot{m}_{\text{steam}}}
$$

$$
x = \frac{80.69}{116.92 + 80.69}
= 0.4083
$$

These values were treated as reference values, not values exactly imposed in the current simulation.

---

### 1.2 Phase mass-flow calculation

The phase mass flow through the inlet is calculated from:

$$
\dot{m}_{\text{phase}}
=
\alpha_{\text{phase}}
\rho_{\text{phase}}
V A
$$

where:

$$
\alpha_{\text{phase}} = \text{phase volume fraction}
$$

$$
\rho_{\text{phase}} = \text{phase density}
$$

$$
V = \text{inlet velocity}
$$

$$
A = \text{inlet area}
$$

For the current simulation:

$$
V = 26.81\ \text{m/s}
$$

The velocity was **not** recalculated as an actual-area-corrected velocity. Therefore, the inlet mass flow is close to the Purnanto target, but it does not match it exactly.

---

### 1.3 Volume-fraction calculation used for the mixed wet-half inlet

Fluent volume fraction is based on phase volumetric flow, not phase mass fraction.

Using the Purnanto 1600 kJ/kg reference phase mass flows and densities:

$$
Q_{\text{liquid}}
=
\frac{\dot{m}_{\text{liquid}}}{\rho_{\text{liquid}}}
=
\frac{116.92}{881.77}
=
0.13260\ \text{m}^3/\text{s}
$$

$$
Q_{\text{steam}}
=
\frac{\dot{m}_{\text{steam}}}{\rho_{\text{steam}}}
=
\frac{80.69}{5.73}
=
14.08202\ \text{m}^3/\text{s}
$$

$$
Q_{\text{total}}
=
0.13260 + 14.08202
=
14.21462\ \text{m}^3/\text{s}
$$

The bulk liquid volume fraction for the full inlet flow is:

$$
\alpha_{\text{liquid,bulk}}
=
\frac{Q_{\text{liquid}}}{Q_{\text{total}}}
=
\frac{0.13260}{14.21462}
=
0.009328
$$

Because the current setup uses an equal two-half inlet and places all liquid only in the wet half, the wet-half liquid volume fraction is doubled:

$$
\alpha_{\text{liquid,wet-half}}
=
2\alpha_{\text{liquid,bulk}}
=
2(0.009328)
=
0.018656
$$

$$
\alpha_{\text{steam,wet-half}}
=
1 - 0.018656
=
0.981344
$$

Therefore, the inlet volume fractions used for this case were:

| Boundary | Liquid volume fraction | Steam volume fraction |
|---|---:|---:|
| Steam-only inlet half | 0.0 | 1.0 |
| Wet inlet half | 0.018656 | 0.981344 |

This volume-fraction calculation comes from the velocity-inlet setup. It should not be described as an actual-area-corrected setup. The actual-area report uses the same volume fractions but recalculates the velocity to 27.12 m/s to force the exact Purnanto mass flow; that was **not** the setup used in this current case.

---

### 1.4 Current simulation inlet flux comparison

From the current Fluent flux report:

| Phase | Current inlet flux |
|---|---:|
| Liquid inlet flow | 115.52 kg/s |
| Steam inlet flow | 80.71 kg/s |
| Total inlet flow | 196.23 kg/s |

The current total inlet mass flow is:

$$
\dot{m}_{\text{current,total}}
=
115.5161 + 80.7123
=
196.2284\ \text{kg/s}
$$

Compared with the Purnanto target:

$$
\dot{m}_{\text{Purnanto,total}}
=
197.61\ \text{kg/s}
$$

The difference is:

$$
\Delta \dot{m}
=
196.2284 - 197.61
=
-1.3816\ \text{kg/s}
$$

The percentage difference is:

$$
\%\ \text{difference}
=
\frac{-1.3816}{197.61}
\times 100
=
-0.70\%
$$

Therefore, the current inlet flow is approximately **0.70% lower** than the Purnanto target.

---

### 1.5 Current outlet-based indicators

From the current outlet flux report:

| Quantity | Value |
|---|---:|
| Steam outlet flow | 81.45 kg/s |
| Liquid outlet flow | 2.50 kg/s |

The liquid separation indicator based only on the outlet flux is:

$$
\eta_{\text{liquid}}
=
\frac{\dot{m}_{\text{liquid,outlet}}}
{\dot{m}_{\text{liquid,inlet}}}
$$

$$
\eta_{\text{liquid}}
=
\frac{2.4986}{115.5161}
=
0.02163
=
2.16\%
$$

The steam outlet dryness is:

$$
x_{\text{outlet}}
=
\frac{\dot{m}_{\text{steam,outlet}}}
{\dot{m}_{\text{steam,outlet}} + \dot{m}_{\text{liquid,outlet}}}
$$

$$
x_{\text{outlet}}
=
\frac{81.4524}{81.4524 + 2.4986}
=
0.9702
=
97.02\%
$$

These outlet-based values are preliminary because they still need to be interpreted together with contours, vectors, pathlines, residuals, and liquid hold-up inside the separator.

---

## 2. What Was Set Up and Tested

### 2.1 CFD setup used for this case

| Item | Current setup |
|---|---|
| Geometry | Spiral-inlet BOC separator |
| Inlet type | Mixed wet-half split inlet |
| Boundary condition | Velocity inlet on both inlet halves |
| Inlet velocity | 26.81 m/s |
| Wet-half liquid volume fraction | 0.018656 |
| Wet-half steam volume fraction | 0.981344 |
| Steam-only inlet liquid volume fraction | 0.0 |
| Liquid density | 881.77 kg/m³ |
| Steam density | 5.73 kg/m³ |

The key point is that the simulation used a **Purnanto velocity-based inlet condition applied to the current geometry**.

It was not an exact **actual-area-corrected mass-flow match**.

---

### 2.2 DPM particle injection setup

DPM particle injections were based on the Purnanto droplet-size mass-flow distribution. The nine injection bins sum to:

$$
\dot{m}_{\text{DPM,total}}
=
116.92\ \text{kg/s}
$$

The bin sum is:

$$
\begin{aligned}
&5.846 + 13.708474 + 15.722479 + 15.224784 + 7.52414 \\
&+ 19.7663 + 17.859486 + 17.182465 + 4.085872 \\
&= 116.92\ \text{kg/s}
\end{aligned}
$$

The injection sizes and mass-flow weights used were:

| Injection | Droplet diameter | Purnanto mass-flow weight |
|---:|---:|---:|
| 1 | 1.29E-04 m | 5.846 kg/s |
| 2 | 2.15E-04 m | 13.708474 kg/s |
| 3 | 3.02E-04 m | 15.722479 kg/s |
| 4 | 3.88E-04 m | 15.224784 kg/s |
| 5 | 4.31E-04 m | 7.52414 kg/s |
| 6 | 5.60E-04 m | 19.7663 kg/s |
| 7 | 7.32E-04 m | 17.859486 kg/s |
| 8 | 9.91E-04 m | 17.182465 kg/s |
| 9 | 1.25E-03 m | 4.085872 kg/s |
|  | **Total** | **116.92 kg/s** |

These original Purnanto mass-flow weights were used rather than actual-area-scaled values. This keeps the DPM comparison aligned with the Purnanto 1600 kJ/kg liquid loading.

However, the DPM total is slightly higher than the current Eulerian liquid inlet flux:

$$
\dot{m}_{\text{liquid,current}}
=
115.5161\ \text{kg/s}
$$

If the DPM bins need to be strictly scaled to the current inlet flux, the scaling factor would be:

$$
\text{scale factor}
=
\frac{\dot{m}_{\text{liquid,current}}}
{\dot{m}_{\text{liquid,Purnanto}}}
$$

$$
\text{scale factor}
=
\frac{115.5161}{116.92}
=
0.98799
$$

Each Purnanto DPM bin could then be scaled as:

$$
\dot{m}_{\text{bin,scaled}}
=
\dot{m}_{\text{bin,Purnanto}}
\times 0.98799
$$

---

### 2.3 DPM step sensitivity check

The step sensitivity check used:

- injection tested: injection 1 / particle size 1,
- initial setup: random initial setup,
- particle streams: 100,
- stochastic tracking: enabled,
- eddy interaction/effect: enabled,
- number of tries: 5,
- effective total stochastic tracks: 500.

| Max steps | Step factor | DPM iteration interval | Trapped | Incomplete | Escaped |
|---:|---:|---:|---:|---:|---:|
| 50,000 | 5 | 10 | 158 | 342 | 0 |
| 500,000 | 5 | 10 | 158 | 342 | 0 |
| 50,000 | 2 | 2 | 159 | 341 | 0 |
| 50,000 | 1 | 1 | 157 | 343 | 0 |
| 500,000 | 2 | 2 | 159 | 341 | 0 |

Increasing max steps from 50,000 to 500,000 did not reduce incomplete tracks for this tested particle case. Reducing step factor and DPM iteration interval produced only negligible changes in trapped and incomplete counts. The incomplete-track issue therefore does not appear to be solved simply by increasing max tracking steps for this setup.

The provisional future DPM setting from this check was:

| DPM setting | Value |
|---|---:|
| Max steps | 50,000 |
| Step factor | 2 |
| DPM iteration interval | 2 |
| Particle streams | 100 |
| Tries | 5 |
| Effective stochastic tracks | 500 per injection |

---

### 2.4 DPM stream-count sensitivity check

The stream-count check used the following fixed settings:

| Fixed setting | Value |
|---|---:|
| Max steps | 50,000 |
| Step factor | 2 |
| DPM iteration interval | 2 |
| Tries | 5 |
| Stochastic tracking tries | 5 |
| Random eddy lifetime | On |

Stream-count results were:

| Particle streams | Effective total tracks | Trapped | Incomplete | Escaped |
|---:|---:|---:|---:|---:|
| 100 | 500 | 159 | 341 | 0 |
| 200 | 1000 | 316 | 684 | 0 |
| 500 | 2500 | 824 | 1676 | 0 |
| 1000 | 5000 | 1711 | 3289 | 0 |

Percentage summary:

| Total tracks | Trapped | Incomplete |
|---:|---:|---:|
| 500 | 31.8% | 68.2% |
| 1000 | 31.6% | 68.4% |
| 2500 | 33.0% | 67.0% |
| 5000 | 34.2% | 65.8% |

Increasing total stochastic tracks from 500 to 5000 improved sampling resolution, but it did not remove the incomplete-track problem. The trapped fraction stayed around **31.6-34.2%**, while incomplete tracks remained dominant at around **65.8-68.4%**.

For this reason, the DPM results are currently treated as **diagnostic only**, not as final separator-efficiency evidence.

---

## 3. What Was Found Out

### 3.1 Main inlet-condition finding

The inlet condition is close to the Purnanto 1600 kJ/kg case, but it is not an exact match.

The reason is that the current simulation used:

$$
V = 26.81\ \text{m/s}
$$

rather than recalculating the inlet velocity from the current actual inlet area.

The current inlet mass flow is:

$$
196.23\ \text{kg/s}
$$

whereas the Purnanto target is:

$$
197.61\ \text{kg/s}
$$

This gives a difference of approximately:

$$
-0.70\%
$$

This is small, but it should still be stated clearly so that the setup is not presented as an exact mass-flow-matched Purnanto replication.

---

### 3.2 Main outlet-flux finding

The current outlet fluxes suggest:

| Indicator | Value |
|---|---:|
| Liquid separation indicator | 2.16% |
| Steam outlet dryness | 97.02% |

The steam outlet appears relatively dry by mass. However, the liquid outlet flow is very low, so the flux-based liquid separation value should not be treated as a final separator efficiency yet.

This needs to be checked against:

- liquid volume fraction contours,
- steam volume fraction contours,
- velocity vectors,
- pressure contours,
- pathlines or streamlines,
- residual convergence,
- liquid accumulation inside the separator,
- and outlet boundary behaviour.

---

### 3.3 Visual evidence to add

#### Liquid volume fraction contours

> Insert figure here.

Comment on:

- where the liquid accumulates,
- whether the liquid moves toward the wall,
- whether liquid remains trapped in the separator,
- and whether liquid approaches the steam outlet.

#### Steam volume fraction contours

> Insert figure here.

Comment on:

- whether a steam-rich core forms,
- whether the steam outlet is mostly vapour,
- and whether this supports the calculated outlet dryness.

#### Velocity contours / vectors

> Insert figure here.

Comment on:

- whether the inlet creates strong swirl,
- whether the flow circulates as expected,
- whether stagnant or recirculating zones appear,
- and whether there is any short-circuiting toward the steam outlet.

#### Pressure contours

> Insert figure here.

Comment on:

- whether the pressure field is physically reasonable,
- whether the inlet-to-outlet pressure drop is sensible,
- and whether the pressure field supports cyclone-like flow behaviour.

#### Pathlines / streamlines

> Insert figure here.

Comment on:

- whether the flow spirals around the separator,
- whether droplets or liquid-rich flow move downward,
- whether some flow escapes upward,
- and whether the pathlines explain the low liquid outlet flux.

---

## 4. Meeting Summary

The main point to explain in the meeting is that this simulation used the **reported Purnanto velocity of 26.81 m/s**, not an actual-area-corrected velocity. Because of this, the current inlet mass flow is close to the Purnanto target but not exactly equal to it.

The current simulation gives a total inlet flow of approximately **196.23 kg/s**, compared with the Purnanto target of **197.61 kg/s**, which is about **0.70% lower**.

The outlet fluxes suggest a relatively dry steam outlet, with approximately **97.02% outlet dryness**, but the liquid outlet flow is very low, giving a flux-based liquid separation indicator of only **2.16%**. This should be treated as a preliminary result until the contours, velocity field, pressure field, pathlines, convergence, and outlet setup are checked.

For now, the DPM results should be treated as diagnostic only because incomplete tracks remain high at around **66–68%**.
