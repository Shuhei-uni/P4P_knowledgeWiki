# Phase 7.2A Stage 2 — E2.7 EWF plus R3–R5 roughness

The three requested runs are complete to native 16586. See the
[matched results and claim limits](results.md).

## Question and comparison

From the completed E2.7 continuation, how do three previously tested outer-wall
roughness levels affect phase-2 liquid outflow through `steamoutlet`, EWF film
response, and bulk liquid inventory? This is a combined-mechanism screen, not
a replay of the earlier no-EWF R3–R5 results. Compare the three children with
one another and with the E2.7 continuation's terminal behaviour. Historical
R3–R5 results began from a different parent and cannot serve as matched controls.

## Common parent

Each child loads the same final E2.7 continuation case/data pair at native
iteration `13586`, saved under the local OneDrive sync folder
`P4P-Fluent-Artifacts/Phase72A/FamilyE/E2.7-continuation-5000/20260923T102912Z/`:

- `P72A-E2.7-CONT5000-final-N13586.cas.h5` — SHA-256 `bc9eeac09adfeca77ebe467c03e6425f3f9bb7069aa5b1eaa9a839ee44f92990`
- `P72A-E2.7-CONT5000-final-N13586.dat.h5` — SHA-256 `57e8b1a97f9d9db8665eb0ab1a211c08065e1a0befc4570a90b89ab18fe61af5`

These are the **durable final pair** hashes in the [continuation run manifest](../../../../PyAnsys/output/phase72a_ewf_server1_e27_cont5000_20260923T102912Z/run-manifest.json),
confirmed against files on this machine. They differ from the server-local final
pair hashes recorded in that manifest. Use and verify the durable pair as one
matched parent; do not mix pair sources. Confirm native iteration and E2.7
settings after load. The earlier native-8586 source-identity limitation remains
part of this parent provenance; see the [continuation result](../ewf-family/results.md#e27-continuation--another-5000-iterations-on-server-1--2026-09-23).

## Controlled children

| Stage 2 case | Roughness setting inherited from | `k_s` (m) | `C_s` | Setup |
| --- | --- | ---: | ---: | --- |
| `E2.7+R3` | R3 | `5e-4` | `0.5` | [setup](e27-r3/setup.md) |
| `E2.7+R4` | R4 | `1e-3` | `0.5` | [setup](e27-r4/setup.md) |
| `E2.7+R5` | R5 | `2e-3` | `0.5` | [setup](e27-r5/setup.md) |

Apply roughness only to `separator-purnanto:1`,
`separator-purnanto:1:001`, `wall`, and `wall:004`, as in the
[R4/R5 setup](../roughness-family/extension-r4-r5-setup.md). Preserve the
parent mesh, steady Mixture/RNG physics, inlets, phase-2 absorber, outlet,
bottom walls, solver controls, and E2.7 phase-accretion EWF settings. In
particular preserve maximum film thickness `0.3 m`, ten film subiterations,
fixed film timestep `1e-5 s`, EWF Coupled Solution ON, and film-wall Flow
Momentum Coupling OFF. Do not reinitialize, patch, or replay the inlet ramp.

## Run and evidence contract

For each independently prepared child, verify pair hashes and native iteration,
apply and read back the wall-only roughness delta, save/reopen the prepared
pair, then run one native `/solve/iterate 3000` from `13586` to expected
`16586`. Keep Fluent-native reports at every iteration and preserve server-local
paired checkpoints (including start and final). Keep only the shareable start
and final pairs in OneDrive. Record the full solver transcript, residuals,
warnings, and report files. A failure preserves the last valid state and is
reported at its actual native coordinate.

Plot the following against native iteration, with the three children on matched
axes and the parent terminal value indicated where available:

1. signed phase-2 `steamoutlet` mass flux (`kg/s`; negative means outflow);
2. EWF total film mass (`kg`), maximum film thickness (`mm`), and area-weighted
   average film speed (`m/s`);
3. EWF wetted area (`m²` and fraction of active EWF wall area);
4. total bulk liquid inventory (`kg`).

The continuation already has native reports for outlet flux, film mass,
thickness, speed, and liquid inventory. Check their definitions/readback in
each prepared child. Wetted area had only a terminal reconstruction in the
parent, not a full history. Before solving a child, establish an every-iteration
Fluent-native Film Coverage area report on the active EWF wall and verify its
value/zone scope. If Fluent cannot provide that report, preserve enough
per-face film-thickness and face-area evidence at declared checkpoints to
reconstruct wetted area using the documented `1e-10 m` critical-thickness
threshold; state the resulting sampling cadence explicitly. Do not label an
endpoint value as a time history.

For interpretation, also retain absorber command/applied removal, phase-1 and
mixture outlet fluxes, source-inclusive closure/storage, and solver-health
evidence from the existing native reports. Compare raw traces and a common
late 500-iteration window when complete; report trends and variability as well
as endpoints. A lower outlet-flux magnitude alone is insufficient if bulk
inventory is depleted, film response keeps moving, closure deteriorates, or
the solution fails. This screen does not establish physical drainage,
convergence, or plant separation efficiency.
