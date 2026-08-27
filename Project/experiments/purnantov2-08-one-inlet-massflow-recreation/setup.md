> **Legacy source:** Setups/past/archived/08-purnanto-one-inlet-massflow-recreation.md  
> **Migration note:** Historical wording, evidence status, and uncertainty labels are preserved; this Project copy is not a reinterpretation. Raw and machine-generated artifacts remain at their legacy paths.

# Purnanto One-Inlet Mass-Flow Recreation

## Setup metadata

| Field | Value |
|---|---|
| Setup ID | `08` |
| Lifecycle | `archived` |
| Role | one-inlet automation/parity scaffold |
| Parent setup | [00a](../purnanto-00a-live-setup-audit/setup.md) |
| Evidence-use label | setup definition/scaffold only |
| Outcome | retained scaffold |
| Linked report | none |

## 1. Purpose

Define the current-project branch that most directly recreates the Purnanto separator setup style:

- one inlet boundary only;
- both steam and water enter through that same inlet;
- inlet boundary type stays `Mass-Flow Inlet`;
- outlet remains a steam-side `Pressure Outlet`;
- no pure-liquid / pure-steam face split at the inlet.

This report is the concrete setup-instance definition for rebuilding the paper-style inlet package on the current project geometry/mesh. It should be used when the goal is direct Purnanto-style setup parity, not the later split-inlet diagnostics.

Geometry naming note:

- this branch uses the `purnantov2` geometry label even though its inlet package is the direct one-inlet Purnanto-style recreation;
- geometry naming and inlet boundary-condition style are separate, so a one-inlet uniform/two-phase recreation can still sit on `purnantov2` geometry;
- use `purnanto` for setups `04` to `07`, and `purnantov2` for setup `08` and later branches unless a later note explicitly overrides that;
- see `../ResearchProject_wiki/wiki/technical/v2-purnanto-spiral-inlet-geometry.md` for the current project naming rule.

Primary reusable evidence:

- [geothermal-boc-separator-fluent-2013-baseline](../../../CFD_wiki/wiki/setups/geothermal-boc-separator-fluent-2013-baseline.md)
- [purnanto-2013-cfd-geothermal-separator](../../../CFD_wiki/wiki/sources/purnanto-2013-cfd-geothermal-separator.md)
- [00a-purnanto-setup-5000-live-audit.md](../purnanto-00a-live-setup-audit/setup.md)

## 2. Setup Identity

| Item | Value |
|---|---|
| Geometry role | current-project one-inlet recreation on `purnantov2` geometry |
| Inlet representation | one mixed steam-water inlet |
| Inlet boundary count | `1` |
| Inlet boundary type | `Mass-Flow Inlet` |
| Outlet boundary type | steam-side `Pressure Outlet` |
| Bottom liquid handling | bottom remains wall/baseline simplification unless a later branch explicitly changes it |
| Multiphase model | `Mixture` |
| Phase mapping | primary vapor, secondary liquid |
| Turbulence model | `RNG k-epsilon` |
| Energy | `Off` |
| Gravity | on, downward in `y` |
| Evidence-use label | direct paper-style recreation branch |

Evidence labels used in this report:

- `Reported`: directly stated in the paper-linked CFD wiki pages.
- `Observed`: taken from the live Purnanto Fluent audit.
- `Assumed`: required because the current-project branch is being rebuilt on local geometry/mesh rather than loaded from the original paper case file.

## 3. Why This Branch Exists

The recent project lineage drifted toward:

- split inlets;
- velocity-inlet reinterpretations;
- no-brine-outlet diagnostics;
- pure-liquid / pure-steam comparison branches.

Those branches are still useful as comparisons, but they are not the closest recreation of the Purnanto setup. For direct parity, the setup needs to return to the simpler paper-style inlet logic:

```text
one inlet
both phases enter together
mass flow is prescribed by phase
pressure outlet handles discharge
```

## 4. Boundary Package to Recreate

### Inlet

Use one inlet boundary named `inlet` or the current-project equivalent.

| Field | Value |
|---|---:|
| Boundary type | `Mass-Flow Inlet` |
| Mixture/initial gauge pressure | `1,140,000 Pa` |
| Direction | normal to boundary |
| Turbulence method | intensity and hydraulic diameter |
| Turbulence intensity | `2.11 %` |
| Hydraulic diameter | `0.724 m` |
| Vapor mass flow | `80.69 kg/s` |
| Liquid mass flow | `116.92 kg/s` |

Interpretation:

- both phases are imposed through the same boundary;
- this is not a uniform liquid-volume-fraction velocity inlet;
- this is not a pure-phase split across two zones;
- this is the closest current-project reproduction of the live audited Purnanto case.

### Steam Outlet

| Field | Value |
|---|---:|
| Boundary type | `Pressure Outlet` |
| Gauge pressure | `1,120,000 Pa` |
| Backflow direction | normal to boundary |
| Backflow pressure specification | total pressure |
| Backflow turbulence intensity | `2.1525 %` |
| Backflow hydraulic diameter | `0.724 m` |
| Liquid backflow volume fraction | `0.0` |

### Walls / Lower Boundary

| Boundary | Intended treatment |
|---|---|
| vessel wall | stationary no-slip wall |
| lower boundary / bottom | wall in the same spirit as the live Purnanto audit |

Practical note:

- do not introduce a separate active brine outlet in this branch unless the aim changes away from direct Purnanto-style recreation.

## 5. Models and Numerics to Keep

Use the paper-style solver stack from the reusable CFD baseline and the live audit:

| Panel | Setting | Value |
|---|---|---|
| General | Solver | `Pressure-Based` |
| General | Time | `Steady` |
| Models > Multiphase | Model | `Mixture` |
| Models > Energy | Energy | `Off` |
| Models > Viscous | Turbulence | `RNG k-epsilon` |
| Operating Conditions | Gravity | `(0, -9.81, 0) m/s2` |
| Operating Conditions | Operating pressure | `0 Pa` |
| Solution Methods | Coupling | `SIMPLE` |
| Solution Methods | Gradient | `Green-Gauss Node Based` |
| Solution Methods | Pressure | `PRESTO!` |
| Solution Methods | Momentum | `Second Order Upwind` |
| Solution Methods | Volume fraction | `QUICK` |
| Solution Methods | `k` | `Second Order Upwind` |
| Solution Methods | `epsilon` | `Second Order Upwind` |
| Initialization | Method | `Hybrid Initialization` |

Observed under-relaxation factors from the live audit that should be kept unless a later troubleshooting branch is created:

| Variable | Value |
|---|---:|
| pressure | `0.3` |
| momentum | `0.7` |
| density | `1.0` |
| body force | `1.0` |
| slip/drift | `0.1` |
| volume fraction | `0.4` |
| `k` | `0.8` |
| `epsilon` | `0.8` |
| turbulent viscosity | `1.0` |

## 6. What Not To Change In This Branch

Do not do these if the goal is direct Purnanto-style recreation:

- do not split the inlet into liquid-side and steam-side faces;
- do not replace the one inlet with a full-area `Velocity Inlet`;
- do not convert it into a pure-liquid / pure-steam branch;
- do not introduce a water-pool initialization as part of the baseline definition;
- do not add DPM injections yet unless the continuous/multiphase field first behaves acceptably.

## 7. First-Run Checks

Before long iterations, verify:

1. Fluent shows exactly one inlet boundary carrying both phase mass flows.
2. The inlet phase mass-flow report reproduces approximately `80.69 kg/s` vapor and `116.92 kg/s` liquid.
3. The outlet remains the only pressure outlet used for the baseline recreation path.
4. Gravity and `Mixture` model are active.
5. The case is initialized with `Hybrid Initialization`.

## 8. Interpretation Rule

Treat this branch as:

```text
direct Purnanto-style recreation branch
```

Use later split-inlet or velocity-inlet reports only as controlled alternatives after this one-inlet mass-flow branch has been rebuilt and checked.
