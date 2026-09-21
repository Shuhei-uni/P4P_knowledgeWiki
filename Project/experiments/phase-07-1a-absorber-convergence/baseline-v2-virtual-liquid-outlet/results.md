# Phase 7.1A baseline v2 build result

## Answer at a glance

`P71A-BASELINE-V2-VIRTUAL-OUTLET` is ready on `student`. Fluent is currently
loaded with the canonical freshly hybrid-initialized prepared pair, not the
one-iteration smoke pair.

The named 60k source mesh produced `60,964` fluid cells after load. The existing
Phase-7 `y <= 0.10 m` selection became a `715`-cell zone named
`p71a-v2-virtual-outlet`; the remaining parent contains `60,249` cells. The
bottom is a wall, and the only pressure outlet is `steamoutlet`.

The v1 lower-inventory/uniform absorber is absent. V2 instead contains a
phase-2-only, inlet-throughput feed-forward sink weighted by local phase-2
volume fraction, together with matching phase-2-velocity momentum removal and
shared k/epsilon removal. Save/reopen readback and a one-iteration smoke passed.

## Artifact identity

| Artifact | Identity |
| --- | --- |
| Prepared case | `P71A-BASELINE-V2-VIRTUAL-OUTLET-prepared.cas.h5` |
| Prepared case SHA-256 | `294970443203f9c21c054c86406316a935baf65df0ee4ebe2132ca93022989e4` |
| Prepared data SHA-256 | `b77c63cdcadbf5346029823a493ebac599177bd4f19014d858cc611649355d12` |
| Smoke case SHA-256 | `dc505128d38155889bb592a448cc1581323ec8ecb15583afd668595aafa42111` |
| Smoke data SHA-256 | `116c42da22b0e1fbad9ec5c1af4a3a23160ea65f38fc0bc56e5dfb4d4f452047` |
| V1 recovery case SHA-256 | `23c047de914699b4b702c88985a8089a062080aa16dedcec213f6f70625cee92` |
| V1 recovery data SHA-256 | `28749c65d93d8feb05293892cca57e27b36ca4d6638273a7af055914874b00dc` |

The complete server paths are in [run-paths.yaml](run-paths.yaml), and the
full machine readback is in [build-manifest.json](build-manifest.json).

## Verified setup

- Fluent 2025 R2, pressure-based steady solver, absolute velocity formulation.
- Mixture model with `phase-1` vapor and `phase-2` liquid; RNG k-epsilon.
- Fresh Hybrid Initialization, 10 passes, no patched liquid pool.
- Mass-flow inlets: `liquidinlet` and `steaminlet`; pressure outlet:
  `steamoutlet`; bottom remains a wall.
- Prepared inlet-derived liquid command: `111.22015 kg/s`, exactly matching
  the inherited v1 liquid-inlet setting captured for this build.
- Source update interval: one iteration.
- Parent-zone mixture, vapor, and liquid sources: disabled.
- Virtual-outlet vapor source: disabled.
- Virtual-outlet phase-2 mass source: `P71V2Sink`.
- Virtual-outlet mixture sources: `P71V2SinkX`, `P71V2SinkY`,
  `P71V2SinkZ`, `P71V2SinkK`, and `P71V2SinkEpsilon`.
- Named-expression definitions and complete source state were identical after
  reopening the prepared pair and after reloading it following smoke.

## Smoke observation and claim limit

The freshly initialized lower zone contained zero liquid. After one iteration,
its liquid volume was only `3.02e-23 m3`, so the realized sink was effectively
zero (`3.36e-15 kg/s`) while the command remained `111.22015 kg/s`. This is the
expected starvation behavior of an alpha-weighted outlet starting from an
all-vapor lower zone; it is not evidence that the outlet can yet realize the
command under developed liquid loading.

Accordingly, this result establishes only that the requested v2 baseline
exists, persists, reopens, and can advance one iteration without a setup or
source-evaluation failure. It does not establish throughput tracking,
convergence, bounded inventory, mass closure, separation performance, or a
physical brine-outlet analogue.

## Next action

Use this exact prepared pair for the first v2 liquid-development discovery run.
That run must directly compare command, native applied phase-2 source, and
liquid-inlet throughput while recording lower-zone liquid availability, whole-
separator liquid inventory, phase-resolved boundary fluxes, phase-1 source
audit, source-inclusive closure, and residuals. The lower-zone volume is a
starvation diagnostic, not the success metric.
