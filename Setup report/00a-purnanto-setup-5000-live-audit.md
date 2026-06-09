# Purnanto Setup 5000 Live Fluent Audit

## 1. Purpose

Record a live PyFluent audit of the Fluent 2024 R2 case/data pair:

```text
C:\Users\syok443\Documents\Fluent Standalone Test 1\purnanto case\purnanto-setup.cas.h5
C:\Users\syok443\Documents\Fluent Standalone Test 1\purnanto case\purnanto-setup-5000.dat.h5
```

This report is a concrete setup-instance snapshot. It links back to the reusable Purnanto reconstruction knowledge rather than duplicating the full paper extraction:

- CFD source page: [purnanto-2013-cfd-geothermal-separator](../CFD_wiki/wiki/sources/purnanto-2013-cfd-geothermal-separator.md)
- CFD setup page: [geothermal-boc-separator-fluent-2013-baseline](../CFD_wiki/wiki/setups/geothermal-boc-separator-fluent-2013-baseline.md)
- Project technical note: [purnanto-etal-2013](../ResearchProject_wiki/wiki/technical/sources/purnanto-etal-2013.md)
- Friendly live reference: [purnanto-live-setup-reference](../ResearchProject_wiki/wiki/technical/purnanto-live-setup-reference.md)

Evidence labels:

- `Observed`: read from the live Fluent 2024 R2 case/data through PyFluent on 2026-06-05.
- `Observed`: cross-checked against the local extracted HDF5 pair in `PyAnsys/data/` on 2026-06-09.
- `Reported`: inherited from Purnanto, Zarrouk, and Cater (2013) through the linked CFD source/setup pages.
- `Inferred`: interpretation of parity, risk, or next action from comparing the live case to the reported baseline.

## 2. Setup Identity

| Item | Value |
|---|---|
| Setup role | Purnanto paper-baseline live case audit |
| Parent/reference setup | `00-baseline-spiral-boc-reference.md` |
| Fluent version | Ansys Fluent 2024 R2 (`Observed`) |
| Solver launch | 3D, double precision, pressure-based (`Observed`) |
| Case file | `purnanto-setup.cas.h5` (`Observed`) |
| Data file | `purnanto-setup-5000.dat.h5` (`Observed`) |
| Local extracted case file | `4800-iterations-300412-1.cas.h5` (`Observed`) |
| Local extracted data file | `4800-iterations-300412-1-05000.dat.h5` (`Observed`) |
| Iteration count in loaded data | `5000` from `number-of-iterations` Scheme variable (`Observed`) |
| Evidence-use label | baseline setup parity audit; not final separator-efficiency evidence |

Load note:

- `read_case_data(file_name=case_file)` first read the case but searched for the default paired data name `purnanto-setup.dat.h5`, which does not exist.
- The actual data file was then loaded successfully with `read_data(file_name=purnanto-setup-5000.dat.h5)`.
- No iterations were run during this audit.

## 3. Mesh Snapshot

| Mesh item | Observed value |
|---|---:|
| Cell count | `2,964,593` |
| Cell type | tetrahedral |
| Node count | `572,556` |
| Face count | `6,063,406` |
| Cell zones | `1` |
| Face zones | `5` |
| Partitions after load | `5` |
| Original partition warning | `15` partition grid loaded onto `5` compute nodes; Fluent combined every `3` partitions |
| Domain volume | `27.96101 m3` |
| Minimum cell volume | `1.428370e-08 m3` |
| Maximum cell volume | `6.244241e-05 m3` |
| Minimum face area | `9.475795e-06 m2` |
| Maximum face area | `3.398210e-03 m2` |
| Minimum orthogonal quality | `0.277635` |
| Worst orthogonal-quality cell location | `(-2.26065, -4.44891, 0.0925273) m` |
| Maximum aspect ratio | `12.8899` |
| Max-aspect-ratio cell location | `(-2.25667, -4.44645, 0.0991416) m` |

Interpretation:

- `Observed`: mesh quality is materially better than earlier low-quality project warnings and is not an immediate rejection trigger.
- `Inferred`: the worst cells are still worth locating visually because they are near the lower-body region by coordinate, and separator conclusions remain sensitive to local inlet, vortex-core, outlet, and water-level-cutoff resolution.
- `Reported`: Purnanto 2013 states the mesh was unstructured tetrahedral, with order-of-millions scale preferred, average `5 cm` elements, and local `1 cm` refinement near selected boundaries through the linked CFD setup page.

## 4. Physics Model Snapshot

| Model item | Observed value |
|---|---|
| Time model | steady |
| Multiphase | `Mixture`, `2` phases |
| Phase material mapping | `phase-1 = water-vapor-at-psep`; `phase-2 = water-liquid-at-psep` |
| Energy | off |
| Viscous model | RNG `k-epsilon` |
| Wall treatment | standard wall functions |
| RNG differential viscosity | enabled |
| RNG swirl-dominated flow option | enabled |
| Species | off |
| Radiation | none |
| DPM / discrete phase | model settings present, no active injections |

Baseline parity:

- `Observed` model choices match the core Purnanto reconstruction: pressure-based, steady, Mixture multiphase, RNG `k-epsilon`, energy off.
- `Observed` DPM settings exist, but `injections = {}` in the loaded case. This means the saved `5000` data is a continuous/multiphase field snapshot, not an active particle-efficiency setup.
- `Reported`: the Purnanto workflow evaluates particle carryover after the converged continuous solution; the exact particle bins/mass allocation remain incomplete in the source extraction.
- `Observed`: the local extracted HDF5 pair preserves the same audit state, so these values can now be cited from the repo-local files without reopening Fluent.

## 5. Operating Conditions and Reference Values

| Item | Observed value |
|---|---:|
| Gravity enabled | yes |
| Gravity vector | `(0, -9.81, 0) m/s2` |
| Operating pressure | `0 Pa` |
| Operating density method | mixture-averaged |
| Operating temperature | `298.15 K` |
| Reference pressure | `1,080,000 Pa` |
| Reference enthalpy | `1,600,000 J/kg` |
| Reference temperature | `500 K` |
| Reference velocity | `32.14 m/s` |
| Reference zone | `fluid` |

Parity note:

- `Observed` operating pressure of `0 Pa` preserves the paper reconstruction convention where gauge pressures are effectively the reported absolute pressure values.
- `Observed` reference pressure is not the same as the outlet gauge pressure and should not be used as a boundary-condition value.

## 6. Material Properties

| Material | Density | Viscosity | Notes |
|---|---:|---:|---|
| `water-vapor-at-psep` | `5.7974339 kg/m3` | `1.52062e-05 kg/(m s)` | `phase-1` |
| `water-liquid-at-psep` | `881.21088 kg/m3` | `0.000145544 kg/(m s)` | `phase-2` |
| `air` | `1.094 kg/m3` | `1.7894e-05 kg/(m s)` | present in material database, not phase material |
| `steel` | `8030 kg/m3` | not applicable | solid material present |
| `aluminum` | `2719 kg/m3` | not applicable | solid material present |

Comparison note:

- The observed liquid density is `881.21088 kg/m3`, while earlier setup notes often use approximately `881.77 kg/m3`. This is a small property mismatch, but it should be recorded because phase mass-flow calculations depend on density.
- The observed vapor density is `5.7974339 kg/m3`, while earlier setup notes often use approximately `5.73 kg/m3`. This is also a small but nonzero reproducibility difference.

## 7. Boundary Conditions

### Inlet

| Field | Observed value |
|---|---:|
| Boundary name | `inlet` |
| Boundary type | mass-flow inlet |
| Mixture initial/supersonic gauge pressure | `1,140,000 Pa` |
| Direction specification | normal to boundary |
| Turbulence method | intensity and hydraulic diameter |
| Turbulent intensity | `2.11 %` |
| Hydraulic diameter | `0.724 m` |
| `phase-1` mass flow | `80.69 kg/s` |
| `phase-2` mass flow | `116.92 kg/s` |

### Outlet

| Field | Observed value |
|---|---:|
| Boundary name | `outlet` |
| Boundary type | pressure outlet |
| Gauge pressure | `1,120,000 Pa` |
| Backflow direction | normal to boundary |
| Backflow pressure specification | total pressure |
| Backflow turbulent intensity | `2.1525 %` |
| Backflow hydraulic diameter | `0.724 m` |
| `phase-2` backflow volume fraction | `0.0` |

### Walls and Interior

| Boundary | Observed type/settings |
|---|---|
| `wall-fluid` | wall, stationary, no slip, roughness height `0`, roughness constant `0.5` |
| `bottom` | wall, stationary, no slip, roughness height `0`, roughness constant `0.5` |
| `interior-fluid` | interior |

Parity note:

- `Observed`: the loaded case uses exactly one mass-flow inlet and one pressure outlet, which matches the reported Purnanto setup style.
- `Observed`: bottom is a wall, consistent with the wiki's practical interpretation that brine discharge below the fixed water-level simplification is not actively modelled.

## 8. Numerics and Controls

| Numerical item | Observed value |
|---|---|
| Pressure-velocity coupling | SIMPLE |
| Gradient | Green-Gauss Node Based |
| Pressure discretization | PRESTO! |
| Momentum discretization | Second Order Upwind |
| Volume fraction discretization | QUICK |
| Turbulent kinetic energy | Second Order Upwind |
| Turbulent dissipation rate | Second Order Upwind |
| Pseudo-time method | off |
| Velocity formulation | absolute |
| Rhie-Chow high-order term relaxation | disabled |

Under-relaxation factors:

| Variable | Observed URF |
|---|---:|
| pressure | `0.3` |
| momentum | `0.7` |
| density | `1.0` |
| body force | `1.0` |
| slip/drift | `0.1` |
| volume fraction | `0.4000000059604645` |
| turbulent kinetic energy | `0.8` |
| turbulent dissipation rate | `0.8` |
| turbulent viscosity | `1.0` |

Residual monitor criteria:

| Equation | Absolute criterion |
|---|---:|
| continuity | `1e-4` |
| x/y/z velocity | `1e-3` |
| volume fraction `vf-phase-2` | `1e-3` |
| `k` | `1e-3` |
| `epsilon` | `1e-3` |

## 9. Data-State and Quality Flags

Observed during data load:

```text
turbulent viscosity limited to viscosity ratio of 1.000000e+05 in 34302 cells
```

Interpretation:

- `Observed`: the loaded `5000`-iteration data hit the maximum turbulent viscosity ratio cap in `34,302` cells.
- `Inferred`: this does not invalidate the setup audit, but it is a solution-quality warning. Before treating the result as final performance evidence, inspect where those limited cells are located and whether they sit near the inlet, vortex core, outlet, or lower wall.
- `Inferred`: the loaded case should be treated as `audited baseline setup plus solution-warning state`, not as validated separator efficiency.

## 10. Paper-Parity Assessment

Strong matches to the Purnanto reconstruction:

- mass-flow inlet with phase mass flows `80.69 kg/s` vapor and `116.92 kg/s` liquid;
- pressure outlet at `1.12e6 Pa`;
- inlet pressure-related field at `1.14e6 Pa`;
- Mixture multiphase with vapor/liquid phase mapping;
- RNG `k-epsilon`, energy off, gravity on, operating pressure `0 Pa`;
- SIMPLE, Green-Gauss Node Based, PRESTO!, second-order momentum/turbulence, QUICK volume fraction;
- hybrid-style source baseline remains compatible with the saved steady case/data state, though the exact initialization transcript was not extracted.

Differences or items requiring caution:

- live material densities differ slightly from the rounded values used in older setup notes;
- DPM injections are not active in the loaded case despite DPM settings being present;
- data load warns about turbulent-viscosity limiting in `34,302` cells;
- residual history values were not extracted, only monitor criteria and saved `number-of-iterations = 5000`;
- exact geometry identity among the Purnanto paper's three inlet designs is not proven solely from the Fluent settings. Filename and folder label imply Purnanto baseline, but geometry visual confirmation is still needed.

## 11. Reproducibility Risk

Confidence rating: `Medium-High` for solver/setup parity; `Medium` for solution-quality readiness; `Low` for DPM efficiency readiness until injections are explicitly defined and tracked.

Missing or unverified items:

- residual values at iteration `5000`;
- physical monitor histories and mass imbalance;
- cell locations for turbulent-viscosity-limited regions;
- DPM particle injection set for carryover/efficiency calculation;
- geometry visual confirmation against the specific Purnanto inlet design.

High-priority next checks:

1. Export residual history or capture residual plot values from the saved `5000` data.
2. Run mass-flow reports for inlet/outlet by phase and compute mass imbalance.
3. Locate turbulent-viscosity-limited cells and compare against inlet/vortex/outlet regions.
4. Add or audit DPM injections separately only after the continuous field is accepted.
5. Visually confirm whether this case is the spiral-inlet, Bangma, or Lazalde-Crabtree geometry variant.
