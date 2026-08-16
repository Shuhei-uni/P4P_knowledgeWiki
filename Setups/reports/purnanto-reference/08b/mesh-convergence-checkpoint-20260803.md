# Setup 08b Mesh-Convergence Checkpoint — 2026-08-03

## Setup and evidence links

- Setup definition: [08b — Purnanto parity split-inlet rebuild](../../past/reported/08b-purnanto-parity-split-inlet-rebuild.md)
- Existing setup result: [08b results](results.md)
- Related mesh-study definition: [Setup 12 — carrier-field mesh-convergence plan](../../future/12-carrier-mesh-convergence-plan.md)
- Quantitative source: [STUDY_HANDOFF_REPORT_20260803.md](/Users/shuheiyokkaichi/Downloads/STUDY_HANDOFF_REPORT_20260803.md)
- Study ID: `split_inlet_mesh_convergence_20260801`
- Snapshot: `2026-08-03`, approximately `13:10 NZST`

**Evidence-use label:** `diagnostic / unresolved` checkpoint. This report records the current mesh-convergence evidence and interpretation; it does not establish mesh independence or select a production mesh.

The checkpoint is based on the handoff report listed above. The referenced machine-readable evidence directory, `PyAnsys/output/split_inlet_mesh_convergence_20260801`, is not present in this checkout, so the tables below should be reconciled against the per-mesh manifests and CSV histories before publication-quality claims are made.

## 1. Study scope

This is a carrier-field mesh-resolution comparison for the split-inlet geothermal-separator case associated with setup `08b`. The completed runs used the same geometry roles, phase model, boundary conditions, materials, numerical methods, initialization procedure, processor count, and monitor definitions. Mesh resolution was the intended controlled change.

The study excludes DPM tracking and Eulerian Wall Film. The mesh-selection quantities are therefore carrier-field outputs: pressure drop, outlet and domain velocity, vorticity, vapor outlet flow, residuals, and monitor stability.

All formal meshes were run to a nominal `3000` iterations, but equal iteration count is not treated as equal convergence. Each mesh must be independently iteration-stable before endpoint differences can be interpreted as spatial discretization effects.

## 2. Mesh ladder and run maturity

The mesh labels are historical names. Actual cell counts and characteristic sizes are the values used for this comparison.

| Mesh | Actual cells | Characteristic size, `h` [m] | Recorded state | Evidence classification |
|---|---:|---:|---|---|
| `mesh-300k` | 1,688,678 | 0.0237620 | 3000 iterations | completed; unresolved |
| `mesh-600k` | 3,609,102 | 0.0184476 | 3000 iterations | completed; unresolved |
| `mesh-900k` | 5,335,623 | 0.0161938 | 3000 iterations | completed; unresolved |
| `mesh-1600k` | 9,720,194 | 0.0132593 | 3000 labelled; residual history to 3087 | completed after recovery; diagnostic/unresolved |
| `mesh-1900k` | 10,756,635 | 0.0128190 | 3000 iterations | completed; unresolved |
| `mesh-2000k` | 11,959,759 | 0.0123739 | 3000 iterations | completed; unresolved |
| `mesh-2300k` | 13,370,267 | 0.0119225 | 1250 recorded; later observed near 1382 | running at snapshot; not classified |

Mesh checks and quality were reported as acceptable across the ladder. The final refinement ratios are close to one (`r ≈ 1.034–1.038`), which provides fine-grid comparisons but makes observed-order and GCI estimates sensitive to numerical noise and incomplete iteration convergence.

## 3. Completed endpoint results

Fluent reports outflow with a negative sign. The vapor-flow interpretation below uses the outlet-flow magnitude.

| Mesh | Pressure drop [kPa] | Vapor at steam outlet [kg/s] | Liquid at steam outlet [kg/s] | Outlet velocity [m/s] | Domain velocity [m/s] | Domain vorticity [1/s] |
|---|---:|---:|---:|---:|---:|---:|
| `300k` | 31.0510 | 81.488642 | 0.84725781 | 51.08266 | 32.85721 | 68.88294 |
| `600k` | 29.0005 | 81.445409 | 0.01250556 | 47.78058 | 32.12963 | 77.79892 |
| `900k` | 27.6593 | 81.447366 | 0.00007952 | 46.23508 | 30.81236 | 82.39088 |
| `1600k` | 25.2610 | 81.461226 | 0.00008392 | 43.04686 | 28.14025 | 85.84952 |
| `1900k` | 24.0141 | 81.466425 | 0.00001114 | 44.14708 | 26.91599 | 86.00685 |
| `2000k` | 24.1355 | 81.462457 | 0.00003356 | 42.55820 | 26.48653 | 86.89046 |

### Observed endpoint trends

- Vapor outlet flow is exceptionally stable at approximately `81.45 kg/s`, with less than approximately `0.06%` variation across the completed meshes. This is useful evidence of vapor-throughput robustness, but it is not sufficient by itself because the value is strongly constrained by the imposed vapor inlet flow.
- Pressure drop decreases from `31.05 kPa` on the coarsest completed mesh to approximately `24.0 kPa` on the fine meshes. This is a substantial apparent mesh effect, although the runs are not iteration-independent.
- Domain-averaged velocity decreases from `32.86 m/s` to `26.49 m/s` with refinement. Outlet velocity is not monotonic: it falls through `1600k`, rises at `1900k`, and falls again at `2000k`.
- Vorticity rises from `68.88 1/s` to `86.89 1/s` and appears to approach a fine-grid level near `86–87 1/s`, but its within-run stability is not uniformly sufficient.
- Liquid outlet flow becomes very small after the `300k` case. Relative percentage comparisons are ill-conditioned near zero and should not be used as a primary mesh metric.

## 4. Iteration-independence evidence

The final-500 drift is calculated from the saved `2500`, `2750`, and `3000` monitor points as `(maximum - minimum) / absolute(mean)`.

| Mesh | Pressure-drop drift [%] | Vapor-flow drift [%] | Outlet-velocity drift [%] | Domain-velocity drift [%] | Vorticity drift [%] |
|---|---:|---:|---:|---:|---:|
| `300k` | 4.377 | 0.0945 | 1.738 | 0.814 | 1.014 |
| `600k` | 5.409 | 0.0497 | 0.658 | 4.373 | 0.526 |
| `900k` | 9.650 | 0.0365 | 4.738 | 6.778 | 1.482 |
| `1600k` | 8.164 | 0.0073 | 1.877 | 8.689 | 0.642 |
| `1900k` | 2.693 | 0.0136 | 3.766 | 9.195 | 0.472 |
| `2000k` | 2.456 | 0.0193 | 0.496 | 9.174 | 1.834 |

The proposed starting criteria were no more than `0.5%` drift for primary monitors and no more than `1%` for velocity/vorticity diagnostics. Vapor flow passes comfortably. Pressure drop fails on every completed mesh. Domain velocity fails on every mesh except that the coarse case is near the secondary threshold, and outlet velocity is generally above the proposed threshold. Vorticity is close to acceptable on some meshes but is not uniformly stable.

The domain-velocity drift is particularly important: it grows from approximately `0.8%` on `300k` to approximately `9.2%` on `1900k` and `2000k`. This supports the interpretation that the finer meshes are less iteration-mature at the common `3000`-iteration endpoint.

The pressure result is also still moving. The final-500 pressure drift remains approximately `2.5–2.7%` on the two finest completed meshes. The apparent `1900k`-to-`2000k` endpoint difference is only `0.51%`, but it is smaller than the within-run pressure drift, so it cannot yet be treated as pressure mesh independence.

## 5. Residual state

| Mesh | Continuity | Maximum momentum | `k` | `epsilon` | Liquid volume fraction |
|---|---:|---:|---:|---:|---:|
| `300k` | 0.05124 | 4.60e-6 | 1.41e-4 | 1.43e-3 | 4.22e-4 |
| `600k` | 0.15054 | 1.45e-5 | 2.76e-4 | 1.14e-3 | 6.62e-4 |
| `900k` | 0.18750 | 1.51e-5 | 2.59e-4 | 7.16e-4 | 7.83e-4 |
| `1600k` | 0.21523 | 1.79e-5 | 2.98e-4 | 7.01e-4 | 7.47e-4 |
| `1900k` | 0.24951 | 2.02e-5 | 3.48e-4 | 9.49e-4 | 7.75e-4 |
| `2000k` | 0.23673 | 1.97e-5 | 3.06e-4 | 8.06e-4 | 6.69e-4 |

Momentum, turbulence, and volume-fraction residuals are relatively low, but continuity remains high and generally plateaued or oscillatory. The fields are numerically bounded rather than explosively divergent; they are not conventionally converged steady solutions.

## 6. Interpretation

The result is promising in one specific sense: the apparent decrease in fine-mesh pressure drop and domain velocity is confounded by incomplete iteration convergence. The finer meshes show larger monitor drift at the common `3000`-iteration endpoint, so the comparison is not yet a clean separation of:

1. iterative convergence error; and
2. spatial discretization error.

It is plausible that additional iterations would move the fine-mesh pressure and velocity values toward a plateau and reduce some of the apparent mesh-to-mesh differences. That hypothesis is supported by the continuing pressure change and the increasing fine-mesh domain-velocity drift, but it is not yet demonstrated. Finer meshes often require more iterations, but this must be established from monitor histories rather than assumed from cell count alone.

The opposite conclusion also remains possible: if pressure and velocity continue drifting without reaching a stable window, the closed-bottom geometry may not possess a physically meaningful steady state under continuous liquid injection. In that case the calculation should be described as a quasi-steady or accumulating-state diagnostic, and the cross-mesh comparison needs a declared common state definition rather than a steady-convergence claim.

The `bottom` zone is intentionally a wall, while `steamoutlet` is the only outlet. The resulting near-total liquid imbalance is therefore a known geometry limitation. Steam-outlet liquid flow and carrier quality may be retained as trend metrics, but they are not validated full-separator efficiency measures in this study.

## 7. Current claim gate

| Quantity or claim | Current status | Interpretation |
|---|---|---|
| Vapor outlet flow | `stable diagnostic` | Mesh-insensitive across completed meshes, but not sufficient as the sole mesh-selection quantity. |
| Pressure drop | `unresolved` | Endpoint changes are substantial and within-run drift exceeds the fine-grid difference. |
| Outlet velocity | `unresolved` | Non-monotonic endpoint sequence and incomplete iteration stability. |
| Domain velocity | `unresolved` | Strong fine-mesh drift at 3000 iterations. |
| Vorticity | `diagnostic / partly stable` | Fine-grid values are close, but stability is not uniform. |
| Continuity residual | `unresolved` | Remains high at completed endpoints. |
| Liquid carryover / quality | `trend only` | Near-zero outlet liquid and closed-bottom geometry make validation and relative comparison inappropriate. |
| Richardson extrapolation / GCI | `not accepted` | Iteration error is not yet smaller than the relevant grid-to-grid changes, and sequences are not consistently monotonic. |
| Overall mesh independence | `not demonstrated` | No production mesh should be selected from this checkpoint alone. |

## 8. Checkpoint conclusion

`Needs follow-up` — retain this as a useful diagnostic mesh-convergence checkpoint for setup `08b`. The completed results indicate that the vapor-throughput quantity is robust, while pressure and velocity-field quantities remain iteration-dependent. The most useful next evidence is a continuation of the fine meshes beyond `3000` iterations, with preserved checkpoints and the same monitor definitions, followed by a common stable-window or otherwise explicitly defined state comparison.

If the fine meshes plateau, re-evaluate mesh sensitivity using the matured outputs. If they do not plateau, document the calculation as a closed-bottom quasi-steady/accumulating-state limitation rather than claiming steady mesh convergence.
