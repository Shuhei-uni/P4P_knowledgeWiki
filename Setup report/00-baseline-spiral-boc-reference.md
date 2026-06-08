## A. Geometry, mesh, and modelling scope

| Section | Item | Set this to | Where | Status / notes | Source |
|---|---|---:|---|---|---|
| Geometry | Separator design | **Spiral-inlet BOC design** | Geometry |  | The paper compares three designs and the spiral-inlet design is one of them.  [oai_citation:0‡informit.366967552564856.pdf](sediment://file_0000000006b0720b935da5499729cdc0) |
| Geometry | Main diameter \(D\) | **2.134 m** | Geometry |  |  [oai_citation:1‡informit.366967552564856.pdf](sediment://file_0000000006b0720b935da5499729cdc0) |
| Geometry | Steam outlet diameter \(D_e\) | **0.724 m** | Geometry |  |  [oai_citation:2‡informit.366967552564856.pdf](sediment://file_0000000006b0720b935da5499729cdc0) |
| Geometry | Brine outlet diameter \(D_b\) | **0.508 m** | Geometry |  |  [oai_citation:3‡informit.366967552564856.pdf](sediment://file_0000000006b0720b935da5499729cdc0) |
| Geometry | \(\alpha\) | **0.200 m** | Geometry |  |  [oai_citation:4‡informit.366967552564856.pdf](sediment://file_0000000006b0720b935da5499729cdc0) |
| Geometry | \(\beta\) | **2.320 m** | Geometry |  |  [oai_citation:5‡informit.366967552564856.pdf](sediment://file_0000000006b0720b935da5499729cdc0) |
| Geometry | \(Z\) | **4.195 m** | Geometry |  |  [oai_citation:6‡informit.366967552564856.pdf](sediment://file_0000000006b0720b935da5499729cdc0) |
| Geometry | \(L_T\) | **4.929 m** | Geometry |  |  [oai_citation:7‡informit.366967552564856.pdf](sediment://file_0000000006b0720b935da5499729cdc0) |
| Geometry | \(L_B\) | **3.579 m** | Geometry |  |  [oai_citation:8‡informit.366967552564856.pdf](sediment://file_0000000006b0720b935da5499729cdc0) |
| Geometry | Outlet area \(A_o\) | **0.5242 m²** | Geometry |  |  [oai_citation:9‡informit.366967552564856.pdf](sediment://file_0000000006b0720b935da5499729cdc0) |
| Mesh | Mesh type | **Unstructured tetrahedral** | Meshing |  |  [oai_citation:10‡informit.366967552564856.pdf](sediment://file_0000000006b0720b935da5499729cdc0) |
| Mesh | Average element size | **5 cm** | Meshing |  |  [oai_citation:11‡informit.366967552564856.pdf](sediment://file_0000000006b0720b935da5499729cdc0) |
| Mesh | Local refined faces | **1 cm** on some faces near boundaries | Meshing |  |  [oai_citation:12‡informit.366967552564856.pdf](sediment://file_0000000006b0720b935da5499729cdc0) |
| Scope | Pre-separator pipe flow | **Not modelled** | Modelling decision |  |  [oai_citation:13‡informit.366967552564856.pdf](sediment://file_0000000006b0720b935da5499729cdc0) |
| Scope | Brine discharge below water level | **Not modelled** | Modelling decision |  |  [oai_citation:14‡informit.366967552564856.pdf](sediment://file_0000000006b0720b935da5499729cdc0) |
| Scope | Water level | **Assume constant, just above brine outlet pipe** | Geometry / modelling decision |  |  [oai_citation:15‡informit.366967552564856.pdf](sediment://file_0000000006b0720b935da5499729cdc0) |
| Scope | Recommended treatment of lower region | **Remove/cut lower fluid region from domain** | Geometry | This is the closest practical interpretation of their simplification | This is an inference from “brine flow not modelled” and “water level assumed constant.”  [oai_citation:16‡informit.366967552564856.pdf](sediment://file_0000000006b0720b935da5499729cdc0) |

## B. Fluent launch

| Section | Item | Set this to | Where | Status / notes | Source |
|---|---|---:|---|---|---|
| Launch | Dimension | **3D** | Fluent launcher |  | Implied by 3D separator geometry and CFD model.  [oai_citation:17‡informit.366967552564856.pdf](sediment://file_0000000006b0720b935da5499729cdc0) |
| Launch | Precision | **Double Precision** | Fluent launcher | Recommended, not explicitly stated in paper | Not specified in paper |
| Launch | Solver workflow | **General Fluent solver setup** | Fluent |  | Not a paper-specific value |

## C. General solver settings

| Section | Item | Set this to | Where | Status / notes | Source |
|---|---|---:|---|---|---|
| General | Solver | **Pressure-Based** | General |  |  [oai_citation:18‡informit.366967552564856.pdf](sediment://file_0000000006b0720b935da5499729cdc0) |
| General | Time | **Steady** | General |  |  |

## D. Operating conditions

| Section | Item | Set this to | Where | Status / notes | Source |
|---|---|---:|---|---|---|
| Operating Conditions | Gravity | **On** | Operating Conditions |  |  [oai_citation:19‡informit.366967552564856.pdf](sediment://file_0000000006b0720b935da5499729cdc0) |
| Operating Conditions | Gravity x | **0 m/s²** | Operating Conditions |  |  [oai_citation:20‡informit.366967552564856.pdf](sediment://file_0000000006b0720b935da5499729cdc0) |
| Operating Conditions | Gravity y | **-9.81 m/s²** | Operating Conditions | Assuming your vertical axis is Fluent y |  [oai_citation:21‡informit.366967552564856.pdf](sediment://file_0000000006b0720b935da5499729cdc0) |
| Operating Conditions | Gravity z | **0 m/s²** | Operating Conditions |  |  [oai_citation:22‡informit.366967552564856.pdf](sediment://file_0000000006b0720b935da5499729cdc0) |
| Operating Conditions | Operating pressure | **0 Pa** | Operating Conditions | So gauge pressure = absolute pressure in their model |  [oai_citation:23‡informit.366967552564856.pdf](sediment://file_0000000006b0720b935da5499729cdc0) |

## E. Models

| Section | Item | Set this to | Where | Status / notes | Source |
|---|---|---:|---|---|---|
| Models | Multiphase model | **Mixture** | Models → Multiphase |  |  [oai_citation:24‡informit.366967552564856.pdf](sediment://file_0000000006b0720b935da5499729cdc0) |
| Models | Flow regime assumption at inlet | **Mist flow** | Modelling basis |  |  [oai_citation:25‡informit.366967552564856.pdf](sediment://file_0000000006b0720b935da5499729cdc0) |
| Models | Primary phase | **Gas / steam / vapour** | Models → Multiphase / Phases |  |  [oai_citation:26‡informit.366967552564856.pdf](sediment://file_0000000006b0720b935da5499729cdc0) |
| Models | Secondary phase | **Liquid water** | Models → Multiphase / Phases |  |  [oai_citation:27‡informit.366967552564856.pdf](sediment://file_0000000006b0720b935da5499729cdc0) |
| Models | Turbulence model | **RNG \(k-\varepsilon\)** | Models → Viscous |  |  |
| Models | Energy equation | **Off** | Models → Energy | Isothermal assumption |  [oai_citation:28‡informit.366967552564856.pdf](sediment://file_0000000006b0720b935da5499729cdc0) |
| Models | Flashing | **Not included** | Do not enable extra phase-change model |  |  [oai_citation:29‡informit.366967552564856.pdf](sediment://file_0000000006b0720b935da5499729cdc0) |

## F. Material properties for baseline case

| Section | Item | Set this to | Where | Status / notes | Source |
|---|---|---:|---|---|---|
| Baseline condition | Total two-phase mass flow \(\dot m_f\) | **197.61 kg/s** | Reference for inlet setup |  |  |
| Baseline condition | Enthalpy \(h\) | **1600 kJ/kg** | Reference for inlet setup |  |  |
| Baseline condition | Separation pressure \(P_{sep}\) | **11.2 bara** | Reference for material properties |  |  [oai_citation:30‡informit.366967552564856.pdf](sediment://file_0000000006b0720b935da5499729cdc0) |
| Materials | Liquid density | **881.77 kg/m³** | Materials | Constant density |  [oai_citation:31‡informit.366967552564856.pdf](sediment://file_0000000006b0720b935da5499729cdc0) |
| Materials | Gas density | **5.73 kg/m³** | Materials | Constant density |  [oai_citation:32‡informit.366967552564856.pdf](sediment://file_0000000006b0720b935da5499729cdc0) |
| Materials | Liquid viscosity | **145.96 × 10⁻⁶ kg/m·s** | Materials | Constant viscosity |  [oai_citation:33‡informit.366967552564856.pdf](sediment://file_0000000006b0720b935da5499729cdc0) |
| Materials | Gas viscosity | **15.188 × 10⁻⁶ kg/m·s** | Materials | Constant viscosity |  [oai_citation:34‡informit.366967552564856.pdf](sediment://file_0000000006b0720b935da5499729cdc0) |
| Materials | Surface tension | **0.0411 N/m** | Multiphase / Phases / Interaction |  |  [oai_citation:35‡informit.366967552564856.pdf](sediment://file_0000000006b0720b935da5499729cdc0) |
| Assumption | Compressibility in separator | **Incompressible** | Modelling basis | Use constant properties |  [oai_citation:36‡informit.366967552564856.pdf](sediment://file_0000000006b0720b935da5499729cdc0) |

## G. Cell zone conditions

| Section | Item | Set this to | Where | Status / notes | Source |
|---|---|---:|---|---|---|
| Cell Zone Conditions | Fluid zone type | **Mixture fluid zone** | Cell Zone Conditions |  | Required by mixture model choice; consistent with paper’s Euler-Euler mixture approach.  [oai_citation:37‡informit.366967552564856.pdf](sediment://file_0000000006b0720b935da5499729cdc0) |
| Cell Zone Conditions | Separate fluid bodies for phases | **No** | Geometry/mesh concept | Same fluid domain, multiphase handled by Fluent | Consistent with mixture model formulation.  [oai_citation:38‡informit.366967552564856.pdf](sediment://file_0000000006b0720b935da5499729cdc0) |

## H. Boundary conditions

### H1. Inlet

| Section | Item | Set this to | Where | Status / notes | Source |
|---|---|---:|---|---|---|
| Boundary Conditions | Inlet type | **Mass-Flow Inlet** | Boundary Conditions → inlet |  |  [oai_citation:39‡informit.366967552564856.pdf](sediment://file_0000000006b0720b935da5499729cdc0) |
| Inlet baseline | Liquid mass flow rate | **116.92 kg/s** | inlet | Baseline case \(h=1600\) kJ/kg |  |
| Inlet baseline | Gas mass flow rate | **80.69 kg/s** | inlet | Baseline case \(h=1600\) kJ/kg |  |
| Inlet baseline | Total mass flow | **197.61 kg/s** | inlet | Baseline case |  |
| Inlet baseline | Liquid mass fraction | **116.92 / 197.61 = 0.5917** | inlet | If Fluent asks for phase fraction instead of phase-specific mass flow | Computed from paper data.  |
| Inlet baseline | Gas mass fraction | **80.69 / 197.61 = 0.4083** | inlet | If Fluent asks for phase fraction instead of phase-specific mass flow | Computed from paper data.  |
| Inlet | Pressure mentioned in paper | **11.4 bar = 1.14 × 10⁶ Pa** | inlet, only if Fluent asks for inlet pressure-related field | Paper states inlet pressure was 11.4 bar |  [oai_citation:40‡informit.366967552564856.pdf](sediment://file_0000000006b0720b935da5499729cdc0) |
| Inlet | Turbulence inputs | **Not fully specified** | inlet | Use sensible defaults / Fluent defaults for first run | The paper does not report turbulence intensity, length scale, etc.  [oai_citation:41‡informit.366967552564856.pdf](sediment://file_0000000006b0720b935da5499729cdc0) |

### H2. Steam outlet

| Section | Item | Set this to | Where | Status / notes | Source |
|---|---|---:|---|---|---|
| Boundary Conditions | Steam outlet type | **Pressure Outlet** | Boundary Conditions → steam outlet |  |  [oai_citation:42‡informit.366967552564856.pdf](sediment://file_0000000006b0720b935da5499729cdc0) |
| Steam outlet | Gauge pressure | **11.2 bar = 1.12 × 10⁶ Pa** | steam outlet | Since operating pressure is 0 Pa |  |
| Steam outlet | Backflow phase setting | **Prefer mostly gas** | steam outlet, if asked | Practical approximation; not specified explicitly | Not specified in paper |

### H3. Walls

| Section | Item | Set this to | Where | Status / notes | Source |
|---|---|---:|---|---|---|
| Boundary Conditions | All physical walls | **Wall** | Boundary Conditions |  | Standard and consistent with paper setup |
| Walls | Roughness | **0** | wall boundary | Smooth wall assumption |  [oai_citation:43‡informit.366967552564856.pdf](sediment://file_0000000006b0720b935da5499729cdc0) |

### H4. Bottom cutoff / brine side

| Section | Item | Set this to | Where | Status / notes | Source |
|---|---|---:|---|---|---|
| Boundary Conditions | Bottom as normal pressure outlet | **Do not use** | Geometry / BC decision | Causes steam to escape downward; not aligned with paper simplification | Paper says brine flow was not modelled.  [oai_citation:44‡informit.366967552564856.pdf](sediment://file_0000000006b0720b935da5499729cdc0) |
| Boundary Conditions | Bottom as real physical wall in full geometry | **Not ideal** | Geometry / BC decision | Causes unrealistic liquid accumulation if lower region remains in domain | Inference from your observed behaviour plus paper simplification |
| Boundary Conditions | Best match to paper | **Exclude lower region from fluid domain; cut at constant water level** | Geometry | Practical interpretation of their simplification |  [oai_citation:45‡informit.366967552564856.pdf](sediment://file_0000000006b0720b935da5499729cdc0) |

## I. Numerical methods

| Section | Item | Set this to | Where | Status / notes | Source |
|---|---|---:|---|---|---|
| Solution Methods | Pressure-velocity coupling | **SIMPLE** | Solution Methods |  |  [oai_citation:46‡informit.366967552564856.pdf](sediment://file_0000000006b0720b935da5499729cdc0) |
| Solution Methods | Gradient | **Green-Gauss Node Based** | Solution Methods |  |  [oai_citation:47‡informit.366967552564856.pdf](sediment://file_0000000006b0720b935da5499729cdc0) |
| Solution Methods | Pressure discretization | **PRESTO!** | Solution Methods |  |  [oai_citation:48‡informit.366967552564856.pdf](sediment://file_0000000006b0720b935da5499729cdc0) |
| Solution Methods | Momentum discretization | **Second Order Upwind** | Solution Methods |  |  [oai_citation:49‡informit.366967552564856.pdf](sediment://file_0000000006b0720b935da5499729cdc0) |
| Solution Methods | Turbulent kinetic energy discretization | **Second Order Upwind** | Solution Methods |  |  [oai_citation:50‡informit.366967552564856.pdf](sediment://file_0000000006b0720b935da5499729cdc0) |
| Solution Methods | Turbulent dissipation rate discretization | **Second Order Upwind** | Solution Methods |  |  [oai_citation:51‡informit.366967552564856.pdf](sediment://file_0000000006b0720b935da5499729cdc0) |
| Solution Methods | Volume fraction discretization | **QUICK** | Solution Methods |  |  [oai_citation:52‡informit.366967552564856.pdf](sediment://file_0000000006b0720b935da5499729cdc0) |

## J. Initialization and running

| Section | Item | Set this to | Where | Status / notes | Source |
|---|---|---:|---|---|---|
| Initialization | Initialization method | **Hybrid Initialization** | Solution Initialization |  |  [oai_citation:53‡informit.366967552564856.pdf](sediment://file_0000000006b0720b935da5499729cdc0) |
| Run Calculation | Iteration count | **Not specified in paper** | Run Calculation | Start with a few hundred, then continue as needed | The paper does not state an exact iteration count.  [oai_citation:54‡informit.366967552564856.pdf](sediment://file_0000000006b0720b935da5499729cdc0) |
| Run Calculation | What this first run solves | **Main steady two-phase flow field** | Interpretation | Velocity, pressure, phase behaviour |  |

## K. Things to leave out for the first recreation

| Item | Set this to | Why | Source |
|---|---:|---|---|
| Energy equation | **Off** | Isothermal |  [oai_citation:55‡informit.366967552564856.pdf](sediment://file_0000000006b0720b935da5499729cdc0) |
| Flashing / evaporation model | **Do not include** | “No flashing occurs inside the separator” |  [oai_citation:56‡informit.366967552564856.pdf](sediment://file_0000000006b0720b935da5499729cdc0) |
| Rough wall modelling | **Do not include** | Smooth walls |  [oai_citation:57‡informit.366967552564856.pdf](sediment://file_0000000006b0720b935da5499729cdc0) |
| Upstream pre-separation pipe model | **Do not include** | Out of scope in paper |  [oai_citation:58‡informit.366967552564856.pdf](sediment://file_0000000006b0720b935da5499729cdc0) |
| Brine outflow model below water level | **Do not include** | Out of scope in paper |  [oai_citation:59‡informit.366967552564856.pdf](sediment://file_0000000006b0720b935da5499729cdc0) |
| DPM droplet injection for first run | **Do not include yet** | Done after converged base flow solution |  |

## L. Unknowns the paper does not fully specify

| Item | Status |
|---|---|
| Exact inlet turbulence intensity / hydraulic diameter / length scale | **Not specified**  [oai_citation:60‡informit.366967552564856.pdf](sediment://file_0000000006b0720b935da5499729cdc0) |
| Under-relaxation factors | **Not specified**  [oai_citation:61‡informit.366967552564856.pdf](sediment://file_0000000006b0720b935da5499729cdc0) |
| Exact residual convergence criteria | **Not specified**  [oai_citation:62‡informit.366967552564856.pdf](sediment://file_0000000006b0720b935da5499729cdc0) |
| Exact iteration count | **Not specified**  [oai_citation:63‡informit.366967552564856.pdf](sediment://file_0000000006b0720b935da5499729cdc0) |
| Detailed mixture sub-options/slip settings | **Not specified**  |
| Exact boundary type used at artificial water-level cutoff | **Not explicitly stated**; best practical interpretation is to exclude lower region from domain  [oai_citation:64‡informit.366967552564856.pdf](sediment://file_0000000006b0720b935da5499729cdc0) |

## M. Super short tracker table

| Done | Setting | Value |
|---|---|---|
| ☐ | Solver | Pressure-Based |
| ☐ | Time | Steady |
| ☐ | Gravity | \(0,\,-9.81,\,0\) |
| ☐ | Operating pressure | 0 Pa |
| ☐ | Multiphase | Mixture |
| ☐ | Primary phase | Steam/vapour |
| ☐ | Secondary phase | Liquid water |
| ☐ | Turbulence | RNG \(k-\varepsilon\) |
| ☐ | Energy | Off |
| ☐ | Liquid density | 881.77 kg/m³ |
| ☐ | Gas density | 5.73 kg/m³ |
| ☐ | Liquid viscosity | \(145.96\times10^{-6}\) kg/m·s |
| ☐ | Gas viscosity | \(15.188\times10^{-6}\) kg/m·s |
| ☐ | Surface tension | 0.0411 N/m |
| ☐ | Inlet type | Mass-Flow Inlet |
| ☐ | Liquid inlet flow | 116.92 kg/s |
| ☐ | Gas inlet flow | 80.69 kg/s |
| ☐ | Outlet type | Pressure Outlet |
| ☐ | Outlet pressure | \(1.12\times10^6\) Pa |
| ☐ | Wall roughness | 0 |
| ☐ | P-V coupling | SIMPLE |
| ☐ | Gradient | Green-Gauss Node Based |
| ☐ | Pressure scheme | PRESTO! |
| ☐ | Momentum | Second Order Upwind |
| ☐ | \(k\) | Second Order Upwind |
| ☐ | \(\varepsilon\) | Second Order Upwind |
| ☐ | Volume fraction | QUICK |
| ☐ | Initialization | Hybrid |
| ☐ | Lower brine region | Excluded from fluid domain |

## N. Accuracy upgrade layer for this project

### N1. What the paper actually implies about `Mixture` versus `Eulerian`

| Item | Recommendation | Why |
|---|---|---|
| What the paper says | **Do not interpret the paper as saying "Eulerian should replace Mixture immediately."** | The paper says `Mixture` and `Eulerian` are both suitable when dispersed-phase volume fraction exceeds 10%, says `Mixture` is the better option for simpler problems because it solves fewer equations, and also says `Mixture` is less accurate than `Eulerian`. It then selects `Mixture` as the most appropriate model for this separator because the separator Stokes number is much less than 1. |
| Best baseline choice | **Keep `Mixture` for the first faithful recreation.** | This preserves parity with the published setup before introducing a higher-cost model change. |
| Best accuracy test after baseline | **Run a controlled `Mixture` versus `Eulerian` A/B test on the same geometry, mesh, and BCs.** | This isolates whether the multiphase model itself improves predictions, instead of mixing model differences with mesh or BC differences. |

### N2. Practical ways to increase accuracy

| Priority | Advice | Why this is likely to help more than a blind model swap | How to test it |
|---|---|---|---|
| 1 | **Get one clean converged `Mixture` baseline first** | If the baseline does not converge cleanly, switching straight to `Eulerian` adds more equations and more stiffness, so it may reduce robustness instead of improving physical accuracy. | Freeze one case: same geometry, same mesh, same BCs, same initialization. Require stable residual trend, low mass imbalance, and stable outlet quantities before changing the multiphase model. |
| 2 | **Refine mesh at the inlet transition, vortex core, steam outlet lip, and water-level cutoff** | In a cyclone separator, local gradients and swirl structure are often more sensitive to mesh than to the difference between `Mixture` and `Eulerian`. The paper itself notes tetra meshes with local refinement and later reports numerical issues in particle tracking that may require refinement. | Keep numerics fixed and run at least three meshes: current, refined local zones, and globally finer. Compare pressure drop, outlet phase split, and vortex-core pressure pattern. |
| 3 | **Improve inlet realism before upgrading the multiphase model** | Your project objective is to replace idealized inlet assumptions with more realistic inlet regimes. A better inlet phase/velocity distribution may improve realism more directly than replacing `Mixture` with `Eulerian` while keeping a uniform inlet. | After the paper-baseline run, test one non-uniform inlet representation only. Compare internal swirl pattern, outlet quality proxy, and liquid carryover trend against the uniform-inlet baseline. |
| 4 | **Use `Eulerian` as a second-stage sensitivity case, not the first fix** | `Eulerian` can be more accurate for strong phase interaction, but it is more expensive and needs tighter control of numerics and convergence. It is best used after the baseline setup is trusted. | Start from the converged `Mixture` case. Change only multiphase model to `Eulerian`. Keep turbulence, mesh, BCs, initialization style, and monitors the same. |
| 5 | **Define accuracy with fixed KPIs, not just prettier contours** | A model can look smoother and still be less reliable. Accuracy has to be judged on repeatable outputs. | Compare each run with the same KPI set: pressure drop, outlet gas mass fraction / steam quality proxy, phase distribution near the outlet tube, mass balance, and convergence stability. |

### N3. Recommended order for your next tests

1. Reproduce the paper-style `Mixture` baseline cleanly.
2. Do a local-mesh refinement study without changing the multiphase model.
3. Improve inlet representation while keeping `Mixture`.
4. Only then run a `Mixture` versus `Eulerian` comparison on the stabilized case.

### N4. Working conclusion

- **Reported from paper**: `Mixture` was selected as the most appropriate model for the separator case, even though the paper acknowledges that `Eulerian` is generally more accurate.
- **Project recommendation**: do **not** treat `Eulerian` as the first accuracy upgrade. First remove bigger error sources: incomplete baseline parity, weak local mesh resolution, and oversimplified inlet structure.
