# FG-MIX-T01 Stages 1–2 — Steady Parent and Transient Start States

## Intent

| Field | Value |
|---|---|
| Campaign | Full Geometry — Mixture Transient Liquid-Outlet |
| Stage IDs | `FG-MIX-T01-S1` and `FG-MIX-T01-S2` |
| Investigation mode | numerical-method preparation / diagnostic |
| Primary question | Can one healthy unpatched steady Mixture field be created for the exact production mesh and then reused to construct controlled transient `t = 0` states? |
| Interpretation owner | user-led |
| Parent/reference | [steady Mixture predecessor](../steady-liquid-outlet/index.md) and historical [`02e`](../../../active/02e-mixture-y010-brine-outlet-boundary-characterization.md) |
| Lifecycle | active planning |

These two small stages are combined because Stage 2 exists only to turn the accepted steady parent into the two controlled startup states required by the initialization comparison.

---

# Stage 1 — Build the common unpatched steady parent

## Why this stage exists

The transient campaign should not depend on Hybrid Initialization if a well-developed full-geometry Mixture flow field can be produced first. The steady parent is an initialization artifact, not one of the six outlet-screen results.

Create **one parent per exact mesh + frozen common physics configuration**. If the mesh changes, repeat this stage; do not reuse the old parent across meshes.

## Stage-1 quick pressure-candidate screen — 2026-08-16

For the first Student-server pass, use the exact production mesh and the
02c Mixture boundary/model contract to create one fresh **unpatched** parent,
then create three independent pressure-only children from that parent. The
only intentional child difference is the tangential brine-outlet gauge
pressure; keep the steam outlet at `1.120 MPa` gauge.

| Candidate | Brine-outlet gauge pressure | Difference above steam outlet | Native steady budget |
|---|---:|---:|---:|
| `FG-MIX-T01-S1-C136` | `1.1360 MPa` (`1,136,000 Pa`) | `+16.0 kPa` | `1,000` iterations |
| `FG-MIX-T01-S1-C1375` | `1.1375 MPa` (`1,137,500 Pa`) | `+17.5 kPa` | `1,000` iterations |
| `FG-MIX-T01-S1-C139` | `1.1390 MPa` (`1,139,000 Pa`) | `+19.0 kPa` | `1,000` iterations |

These are quick diagnostic candidates, not three independent production
parents and not a pressure-performance ranking. Choose the candidate parent
only after comparing common-window numerical stability and physical-monitor
behaviour. The selection remains `user-led`; do not infer a final operating
pressure from this screen alone.

The mesh input is locked to:

```text
Full-geomV2-231kcells.msh.h5
```

Do not remesh, adapt, substitute the Student mesh, or alter the mesh file as
part of this screen. Each candidate must be initialized independently from
its case-only child, run natively for `1,000` steady iterations, and saved as
a paired case/data endpoint before comparison.

## Current production target

Use the current production mesh lineage:

```text
Full-geomV2-231kcells.msh.h5
```

Historical production readback from the Y010 work:

```text
Total cells = 231,376
Fluid zones = 1 combined fluid cell zone
```

The exact mesh filename and live readback must be recorded with the new parent artifact before it is accepted.

## Frozen physical/model context

Preserve the current full-geometry Mixture basis:

| Category | Required state |
|---|---|
| Solver | pressure-based, steady |
| Multiphase | Mixture |
| Turbulence | RNG `k-epsilon` |
| Gravity | `[0, -9.81, 0] m/s²` |
| Operating pressure | `0 Pa` |
| DPM / EWF | off |
| Liquid inlet | Velocity Inlet, `27.118 m/s` |
| Steam inlet | Velocity Inlet, `27.118 m/s` |
| Inlet reference / initial gauge pressure | `1.140 MPa` |
| Steam outlet | Pressure Outlet, `1.120 MPa` gauge |
| Brine outlet for parent build | Pressure Outlet, `1.120 MPa` gauge baseline |
| Brine backflow | liquid-dominant; liquid VF `1.0`, complementary vapour VF `0.0` where exposed |
| Materials | preserve verified water-vapour / water-liquid pair |
| Liquid density reference | `881.77 kg/m³` from the current production setup |

The parent brine pressure is only a neutral build condition. It **does not have to equal** the later transient child pressure or even remain the same outlet family after cloning. Child-specific brine conditions are applied before the first transient timestep.

## Initialization rule

For the steady parent:

```text
build/read back common steady Mixture case
→ Hybrid Initialize
→ NO Y010 patch
→ solve to an accepted developed steady field
→ save paired case/data parent
```

Do not patch Y010 during the steady solve. The purpose is to obtain a developed pressure, velocity, turbulence and phase field before the transient initial liquid inventory is imposed.

## Parent acceptance evidence

This is not a new separator-performance experiment, so do not invent an outlet-performance acceptance threshold. The parent does need to be numerically healthy enough to serve as an initial field.

Capture at minimum:

- residual histories;
- total and phase-separated inlet/outlet flux histories where available;
- continuity / overall mass-balance behavior;
- brine-pipe-entry pressure history if already instrumented;
- confirmation that the solution is no longer undergoing a large monotonic startup drift;
- final model/boundary readback;
- exact `.cas.h5` + `.dat.h5` paths.

The user decides whether the field is sufficiently developed to become the campaign parent. Do not select a partially corrupted or floating-point-failure endpoint just because it ran for many iterations.

## Stage-1 output

A uniquely named immutable artifact, conceptually:

```text
FG-MIX-T01-steady-parent-<mesh-id>.cas.h5
FG-MIX-T01-steady-parent-<mesh-id>.dat.h5
```

Once accepted, all later transient qualification cases for that mesh must trace back to this exact parent unless a documented parent revision is created.

The executed quick candidate screen is documented in the [Stage-1 candidate report](../../../reports/full-geometry/mixture/transient-liquid-outlet/stage-01-candidate-screen-20260816.md). It provisionally selects the `1.1375 MPa` endpoint as the candidate parent for the next setup-construction stage; this selection is diagnostic and conditional on the Stage-2 readback gate because the 1,000-iteration field is not converged.

---

# Stage 2 — Construct the two transient startup branches

## Purpose

Prepare the inputs for the Stage-3 initialization comparison without mixing initialization effects with different boundary conditions.

The comparison case is `T-PO-1`:

```text
brine outlet = Pressure Outlet
P_brine = 1.200 MPa gauge
```

Both branches must have the same transient case definition before timestep 1.

## Branch S — developed steady-field start

```text
load accepted steady parent case+data
→ switch Steady → Transient
→ apply the same provisional transient numerical settings used by Branch H
→ set brine outlet to T-PO-1 = 1.200 MPa gauge
→ create/verify Y010 register
→ patch water-liquid VF = 1.0 in Y010 once
→ set/confirm flow time = 0 s
→ save comparison start state
```

Do **not** run additional steady iterations after applying the Y010 patch.

## Branch H — Fluent Hybrid Initialization start

```text
load/rebuild the same case definition on the same mesh
→ switch to Transient
→ apply the same provisional transient numerical settings used by Branch S
→ set brine outlet to T-PO-1 = 1.200 MPa gauge
→ Hybrid Initialize
→ create/verify the identical Y010 register
→ patch water-liquid VF = 1.0 in Y010 once
→ set/confirm flow time = 0 s
→ save comparison start state
```

## Y010 control

Use the approved production-mesh Y010 definition from `02e`:

```text
x = [-2.067034, 1.066098] m
y = [-1.484584, 0.100000] m
z = [-1.469893, 2.000000] m
inside = True
```

Historical reference inventory on the 231k mesh:

```text
Selected cells = 33,315
Geometric selected-cell volume = 4.829410214 m³
Post-patch liquid inventory = 4.790652590 m³
Initial liquid mass = 4224.253734 kg
```

Read the inventory back again for both new startup branches. Do not assume the historical values prove the new artifacts are identical.

## Stage-2 case-construction record — 2026-08-16

The user-selected `FG-MIX-T01-S1-C1375` paired endpoint was used to create the
two matched `T-PO-1` startup-state pairs below. Both use the unchanged
`Full-geomV2-231kcells.msh.h5` mesh and the same provisional transient method;
neither case has advanced a transient timestep.

| Branch | Starting field | Brine outlet | Y010 patch | Paired case/data artifact |
|---|---|---:|---|---|
| `FG-MIX-T01-S2-INIT-S` | developed C1375 field | `1.200 MPa` gauge | once at `t = 0 s` | `FG-MIX-T01-S2-INIT-S-TPO1-p1200kpa-y010-start-20260816T112833Z.cas.h5/.dat.h5` |
| `FG-MIX-T01-S2-INIT-H` | Fluent Hybrid Initialization | `1.200 MPa` gauge | once at `t = 0 s` | `FG-MIX-T01-S2-INIT-H-TPO1-p1200kpa-y010-start-20260816T112833Z.cas.h5/.dat.h5` |

The exact remote artifact directory is:

```text
C:\Users\Shuhei Yokkaichi\Documents\CFD\Brine outlet\
```

The common transient settings were read back as Fluent 2025 R2
`unsteady-2nd-order-bounded`, PISO with one neighbor-correction iteration,
`2.5e-4 s` fixed timestep, `20` maximum iterations per timestep, and flow time
`0 s`. The Y010 register readback was `33,315` cells with the approved bounds.
The `INIT-H` post-patch liquid volume was `4.790652590 m³` (`4,224.253734 kg`);
`INIT-S` read `4.793078931 m³` (`4,226.393209 kg`). The same patch command was
applied once to both branches, but this small `0.05065%` difference means the
equivalence gate is not yet closed. Do not start Stage 3 until the difference is
resolved or explicitly accepted by the user.

The cases contain the Stage-2 phase-flux, Y010/Y030, and total-liquid-volume
report definitions. Fluent 2025 R2 exposed some optional volume-report fields
as read-only during creation, so the saved report package must be inspected or
repaired before treating every history-file toggle as active.

## Stage-2 equivalence gate

Before Stage 3, prove that Branch S and Branch H differ intentionally only in their pre-patch flow field / initialization history. They must share:

- exact mesh;
- models/materials;
- inlet conditions;
- steam outlet;
- T-PO-1 brine condition;
- Y010 patch definition and post-patch inventory;
- provisional transient numerical settings;
- flow time `0 s`;
- monitor package.

If an unintended setup difference exists, fix the build before running the initialization comparison.

## Handoff

Proceed to [Stage 3 — Initialization Comparison](stage-03-initialization-comparison.md).
