# Setup 02c — Mixture Brine-Outlet Pressure Sensitivity, Unprimed

## Setup metadata

| Field | Value |
|---|---|
| Setup ID | `02c` |
| Lifecycle | `active` |
| Role | three-case brine-outlet-pressure sensitivity and drainage control |
| Parent setup | [02 — Split two-zone velocity-inlet brine-outlet](../past/archived/02-split-two-zone-velocity-inlet-brine-outlet.md) |
| Controlled variable | brine-outlet gauge pressure only |
| Evidence-use label | `User-specified` definition with early screening evidence for Cases B and A; no pressure-performance ranking |
| Outcome | Case B has a 500-iteration diagnostic; Case A has a 649-iteration unprimed screening checkpoint; Case C remains pending |
| Linked report | [02c Cases A/B early diagnostics](../reports/02c/results.md) |

## 1. Objective

Determine whether the new physical tangential brine-outlet pipe can remove the continuous liquid naturally in the existing steady Mixture-model separator while keeping vapour routed to the steam outlet.

The intended physical sequence is:

```text
continuous liquid -> centrifugal separation -> vessel wall -> lower vessel
-> tangential brine outlet

vapour -> central/core region -> steam outlet
```

This is deliberately an **unprimed** control.  It must not create an initial lower-vessel liquid pool or otherwise supply liquid that has not entered through the defined inlet conditions.

## 2. Scope and lineage rule

`02c` is a new child of the earlier full-geometry split-velocity-inlet/brine-outlet branch.  The historical parent is retained as archived context; it must not be overwritten or treated as proof that this three-pressure matrix has run.

`Observed` live-session context on 2026-08-12:

- the loaded Fluent 2025 R2 session exposed `liquid-inlet`, `steam-inlet`, `brine-outlet`, and `steam-outlet` zones;
- `brine-outlet` and `steam-outlet` were both identified as pressure outlets;
- the model state was steady pressure-based Mixture with RNG k-epsilon, gravity enabled, Energy off, DPM off, and EWF off.

`Uncertain` / execution hold point:

- Fluent did not expose the active case/data filename, so the currently loaded session is **not** a verified parent artifact;
- immediately before this report was made, the working session had split **mass-flow** inlets because of a separate live configuration task. That is not the intended inlet representation for this experiment.

Therefore, before creating any `02c` case, explicitly load or otherwise identify a parent case with the prescribed split **velocity-inlet** topology and record its complete path. Do not derive a `02c` artifact from the unverified working session unless the operator explicitly changes this experiment's inlet rule.

## 3. Parent configuration to preserve

The parent case must be read back before cloning. Preserve all settings except the brine-outlet pressure listed in Section 5.

| Category | Required value / rule | Evidence label |
|---|---|---|
| Solver | pressure-based, steady | `User-specified` parent basis |
| Operating pressure | `0 Pa` | `User-specified` parent basis |
| Gravity | enabled | `User-specified` parent basis |
| Multiphase model | Mixture | `User-specified` parent basis |
| Turbulence model | RNG k-epsilon | `User-specified` parent basis |
| Energy | off | `User-specified` parent basis |
| DPM / EWF | preserve the verified parent state; do not enable, disable, or tune for this study | `User-specified` control rule |
| Geometry and mesh | retain the geometry containing the real tangential lower brine pipe and retain the exact parent mesh | `User-specified` control rule |
| Walls, materials, discretization, controls | retain parent readback exactly | `User-specified` control rule |

### 3.1 Inlet contract

Both split inlets must remain **Velocity Inlet** boundaries. Do not convert them to pressure inlets or mass-flow inlets for this experiment.

| Zone role | Required state |
|---|---|
| liquid-side / outer-wall inlet | velocity inlet; normal-to-boundary velocity `27.118 m/s`; liquid-dominant phase state |
| steam-side / core inlet | velocity inlet; normal-to-boundary velocity `27.118 m/s`; vapour-dominant phase state |
| inlet reference / initial gauge pressure | `1.140 MPa` gauge |

The exact zone names must be captured from the verified parent. The current names `liquid-inlet` and `steam-inlet` are only observed live-session labels, not a substitute for parent-case provenance.

### 3.2 Outlet contract

| Outlet role | Type | Gauge pressure | Backflow phase state |
|---|---|---:|---|
| steam outlet | pressure outlet | `1.120 MPa` | preserve verified parent backflow settings; vapour-dominant where the parent exposes phase fractions |
| tangential brine outlet | pressure outlet | varies only by Section 5 | liquid backflow volume fraction = `1.0`; complementary vapour backflow fraction = `0.0` if Fluent exposes it |

The brine backflow fraction is a **backflow** condition only. It must not be described as forcing liquid-only normal outflow.

## 4. Geometry verification gate

Before building any case, verify and record all of the following from the selected parent case and mesh:

1. the end face of the lower tangential pipe is the intended brine-outlet zone;
2. that zone is a pressure outlet, not a wall/interior/unintended open face;
3. the tangential pipe belongs to the expected fluid region and is connected to the lower vessel;
4. there are no unexpected additional inlet or outlet faces; and
5. the steam outlet and each split inlet are the intended physical faces.

If any item is ambiguous, stop the build and request an operator decision. Do not rename, reconnect, remesh, or otherwise modify geometry automatically.

## 5. Case matrix

Create three case-only artifacts from the same verified parent. Their only intentional setup difference is the brine-outlet gauge pressure.

| Case ID | Suggested artifact suffix | Brine gauge pressure | Interpretation |
|---|---|---:|---|
| `02c-A` | `brine-p1115kpa-unprimed` | `1.115 MPa` (`1,115,000 Pa`) | encourages drainage; may increase vapour short-circuit risk |
| `02c-B` | `brine-p1120kpa-unprimed` | `1.120 MPa` (`1,120,000 Pa`) | matches the steam-outlet pressure |
| `02c-C` | `brine-p1125kpa-unprimed` | `1.125 MPa` (`1,125,000 Pa`) | resists vapour escape; tests whether liquid pressure is sufficient for drainage |

Keep the steam outlet at `1.120 MPa` gauge for all three cases. Do not use pressures outside `1.115–1.125 MPa` unless the operator explicitly changes the matrix.

## 6. Build procedure and readback requirements

Build each child independently from the same parent case; reload the parent before applying the next pressure. Python/PyFluent may produce only `.cas.h5` artifacts. Fluent owns later initialization, iteration, and native autosave.

For each case:

1. load the explicitly named parent case and capture its complete boundary/model readback;
2. pass the geometry verification gate in Section 4;
3. verify both split inlets are velocity inlets and retain `27.118 m/s`, their phase conditions, and `1.140 MPa` reference/initial pressure;
4. verify the steam outlet remains a pressure outlet at `1.120 MPa` gauge;
5. set only the brine-outlet gauge pressure from Section 5;
6. set/read back brine liquid backflow volume fraction `1.0` and vapour `0.0` when exposed;
7. read back all controls in Steps 3–6, compare them with the parent snapshot, and fail the build on an unintended difference;
8. write a uniquely named case-only `.cas.h5` artifact and record its remote path, parent path, Fluent version, and local readback snapshot;
9. reload the unchanged parent before creating the next pressure case.

No case may be initialized, iterated, or saved with data as part of this setup-build stage.

## 7. Initialization and run rule

When an operator authorizes a solve, use the parent initialization method; the preferred method is **Hybrid Initialization**.

Do not:

- patch a liquid pool, brine pipe, or lower-vessel region;
- introduce a liquid sink or UDF;
- enable VOF; or
- tune numerical controls between Cases A–C unless a stability recovery is specifically approved and recorded as a deviation.

The initial condition is therefore intentionally a dry/unprimed control. A run may show early liquid accumulation before drainage develops; record the time/iteration history rather than compensating with a patch.

## 8. Required monitor package

Define and verify the monitor/report definitions before starting a solve. Use a consistent outlet sign convention; Fluent normally reports outward mass flow as negative, so record both raw and outward-positive values.

### 8.1 Phase mass flows

| Phase | Required zones |
|---|---|
| liquid | liquid inlet, brine outlet, steam outlet |
| vapour | steam inlet, brine outlet, steam outlet |

The most important new quantities are the outward-positive liquid flow at the brine outlet, `m_dot_liquid_brine`, and outward-positive vapour flow at the brine outlet, `m_dot_vapour_brine`.

### 8.2 Field and balance monitors

Also monitor:

- total continuous-liquid inventory in the vessel;
- pressure near the brine-pipe entrance/outlet and in the lower vessel, using fixed, documented point/surface definitions;
- whole-domain mixture mass imbalance;
- phase-specific mass balances; and
- residual histories and pressure-outlet backflow warnings.

The point/surface definitions used for lower-vessel and brine-adjacent pressure must be frozen across all three cases before Case A begins.

## 9. Required post-processing and derived metrics

Use outward-positive outlet mass-flow magnitudes in the following calculations. If an outlet reports positive under the selected Fluent sign convention, convert it consistently before calculating a balance.

```text
liquid_closure_error =
abs(liquid_in - liquid_brine_out - liquid_steam_out) / abs(liquid_in)

steam_wrong_outlet_fraction =
abs(vapour_brine_out) / abs(vapour_in)
```

The desired trend is:

```text
liquid_in approximately equals liquid_brine_out + liquid_steam_out
vapour_brine_out approximately equals 0
```

Also retain steam-outlet liquid carryover, steam-outlet vapour recovery, pressure drop, liquid inventory trend, phase imbalance, and monitor-window variation. Do not call a low closure error a converged or validated separator result unless residual and physical-monitor stability support that claim.

Required future visual outputs:

- continuous-liquid volume-fraction contours;
- velocity contours;
- pressure contours; and
- velocity vectors and/or streamlines.

Each view must include, where applicable: the split inlet, outer vessel wall, lower vessel, brine-pipe entrance, brine pipe, steam core, and steam outlet.

## 10. Acceptance and stop conditions

Treat this as a diagnostic pressure sensitivity, not a final performance study, unless every case has a stable monitor window and adequately closed phase balances.

Stop a case and record the failure if it has any of the following without a clearly recoverable numerical explanation:

- persistent divergence or unbounded phase fractions;
- an ambiguous or changing geometry/zone contract;
- a materially different inlet, steam-outlet, physics, mesh, or solver setting from the frozen parent;
- sustained vapour short-circuiting through the brine outlet; or
- liquid inventory that continues to drift without a stable operating trend.

Do not alter another control variable to rescue one pressure point. Any approved stability deviation creates a separately identified branch rather than a silent modification of the A/B/C comparison.

## 11. Live Case B build and launch — 2026-08-12

`Observed` setup build evidence:

| Item | Read-back / observed state |
|---|---|
| Child case | `02c-B` / `brine-p1120kpa-unprimed` |
| Pre-initialization case snapshot | `C:\Users\syok443\P4P simulation\brine outlet\02c-B-brine-p1120kpa-unprimed-preinit-20260812T043007Z.cas.h5` |
| Inlet topology | `liquid-inlet` and `steam-inlet` both read back as velocity inlets |
| Inlet reference pressure | `1,140,000 Pa` gauge on both inlets |
| Inlet velocity readback | phase-1 and phase-2 velocity magnitude `27.118 m/s` on both inlets |
| Inlet liquid volume fraction | `liquid-inlet = 1.0`; `steam-inlet = 0.0` |
| Steam outlet | pressure outlet at `1,120,000 Pa` gauge; liquid backflow volume fraction `0.0` |
| Brine outlet | pressure outlet at `1,120,000 Pa` gauge; liquid backflow volume fraction `1.0` |
| Initialization | Hybrid Initialization completed; no phase patch was applied |
| Screening calculation request | `500` steady iterations issued as one Fluent calculation command |

`Uncertain` run state at the time of this update:

- after the calculation command was issued, the Fluent endpoint continued accepting TCP connections but did not complete a new PyFluent/gRPC handoff during repeated bounded read-only checks;
- the calculation is therefore recorded as **launched / completion unverified**, not as a completed 500-iteration result;
- no post-run case/data checkpoint, flux table, convergence history, or performance conclusion has yet been verified.

Do not submit another calculation command, reload the case, or create Case A/C until the current Fluent calculation returns control and the final state is inspected. After it returns, save and verify the paired end-of-screening case/data checkpoint, capture the required monitor/phase-flux evidence, and then rebuild each remaining pressure point from the frozen pre-initialization parent.

The requested 500-iteration endpoint has since been reached, saved, and analysed; see the [Case B results report](../reports/02c/results.md). The remaining Case A/C work is recorded in the [future-run placeholders](../reports/02c/future-runs.md).

Case A was subsequently rebuilt from the recorded Case B pre-initialization snapshot with only `brine-outlet` gauge pressure changed to `1.115 MPa`, Hybrid Initialized without a liquid patch, and run through the requested 500-iteration milestone. A queued continuation was allowed to finish rather than interrupting Fluent, yielding a final 649-iteration checkpoint. Its evidence and limitations are recorded in the [future-run report](../reports/02c/future-runs.md); it has not yet been post-processed or used for a pressure ranking.

## Cross-references

- Historical parent: [02 — Split two-zone velocity inlet with brine outlet](../past/archived/02-split-two-zone-velocity-inlet-brine-outlet.md)
- Setup ordering: [Setups order dictionary](../order-dictionary.md)
- Boundary-setting order: [PyAnsys boundary-condition order](../../PyAnsys/knowledge/fluent-settings/orders/boundary_conditions_order.yaml)
- Parent inlet context: [08b parity split-inlet rebuild](../past/reported/08b-purnanto-parity-split-inlet-rebuild.md)
