# P7-E5-CZ-G025 — native lower-cell-zone source, G=0.25

## Contract

| Field | Value |
| --- | --- |
| Lifecycle | `discovery` adaptive short screen |
| Context | [`../CONTEXT.md`](../CONTEXT.md) |
| Candidate/origin | `E5-CZ`; human-approved H4 follow-on direction, 2026-09-10 |
| Gate/design | `G2`; [`shared design`](../design.md) |
| Parent | Exact valid E0 iteration-500 case/data pair after the split-by-mark operation |
| Mesh delta | Split `separator-purnanto` by the frozen `0≤y≤0.10 m` register using `move_faces=true`; lower zone renamed `p7-e5-lower-y010` |
| Controlled delta | Native lower-zone phase-2 mass source plus audited mixture momentum source, gain `G=0.25` |
| Frozen context | E0 physics/materials/phases/inlets/steam outlet, corrected `0.875936 m` outlet scale, numerics, monitors, and evidence contract |
| Active horizon | `500` controller-active iterations; `50`-iteration smoke; updates every `50` active iterations |

## Source law

Use the shared law from `design.md`:

```text
e       = max(0, (Mcurrent - M*) / ΔMref)
u       = clamp(0.25 × 116.92 kg/s × e, 0, 146.15 kg/s)
S_mass  = -u / V_lower
S_mom,k = S_mass × U_phase2,k,lower
```

Apply one negative constant phase-2 mass source in the lower zone only. Keep
phase-1 mass, energy, turbulence, and parent-zone sources disabled/`none`.
Apply the corresponding x/y/z mixture momentum sources using the explicitly
reported lower-zone phase-2 velocity basis. Read back signs, values, units,
active zone, and integrated user sources at every controller update.

## Required evidence

Before solve, prove the exact E0-500 parent, register, split invariants,
lower-zone cell count/volume, source-tree binding, zero direct phase-1 mass
source, mixture momentum-source basis, save/reopen, and smoke. During the
screen, retain native residuals, full transcript, controller commands,
realized phase-2 removal, integrated source terms, total/lower-zone liquid
inventory, phase-resolved balances, bottom vapor loss, warnings, and
checkpoint/final case-data identities.

Core figures are F1 inventory response, F2 command-versus-realized phase-2
source/removal, and F3 phase/mixture/user-source balances with residual and
vapor-loss support, as defined in [`design.md`](../design.md).

This setup is an artificial zone-scoped source discovery test. It does not
support a physical outlet, local-cell mass-weighted UDF, or steady-convergence
claim.
