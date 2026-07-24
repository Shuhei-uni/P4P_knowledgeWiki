# Observation 06 — `010V2a`–`010V2d` Iteration-Continuation Checkpoints

## Comparison question

When each isolated/combined EWF branch is inspected again at its reported 5,000-iteration state, do the wall-film and DPM results appear stationary relative to the earlier lower-iteration checkpoint?

## Comparison boundary

This observation compares **each branch with itself**, not one optional mechanism against another. The reports are final-state snapshots from already loaded Fluent sessions; they do not supply a shared restart, case/data filename, defined physical-time interval, or integrated EWF histories. `010V2a` also changed from Fluent `2024 R2` to `2025 R2` between checkpoints. Thus the table is a diagnostic continuation trend, not a formal convergence study or a causal mechanism comparison.

`010V2d` also has a 10,000-iteration follow-up. It is not folded into the four-branch 5,000-iteration table, but it is used below as an important guardrail against assuming that simply continuing iterations will settle the EWF state.

## Comparability audit

| Branch | Session / version change | DPM represented-flow change | What this allows | What it rules out |
|---|---|---:|---|---|
| `010V2a` | same server `2`, but `2024 R2` → `2025 R2`; case/data names unavailable | `5.8460` → `5.8929 kg/s` (`+0.80%`) | directional state comparison | a release-independent continuation or splash effect |
| `010V2b` | earlier named console case `010V2-b-1498`; later server `3`; both `2025 R2` | `5.8534` → `5.8704 kg/s` (`+0.29%`) | strongest payload-matched continuation screen | a strict restart-pair claim because the later case/data name is unavailable |
| `010V2c` | server `4` → server `2`; both `2025 R2`; names unavailable | `5.8464` → `5.9424 kg/s` (`+1.64%`) | DPM/film endpoint comparison | a carrier-convergence comparison: the 5,000-iteration carrier export failed |
| `010V2d` | server `3` → server `1`; both `2024 R2`; names unavailable | `5.8614` → `5.9595 kg/s` (`+1.67%`) | combined-branch continuation screen | a restart-pair or mechanism-only attribution |

The payload drift is small enough that the consistent qualitative fate shift is worth retaining, but it is not zero. DPM tracks are also recomputed at each checkpoint. Percentages below therefore normalize each terminal fate by that checkpoint's own represented injection rate rather than treating raw absorbed flow as directly identical payload evidence.

## Film and numerical-state comparison

| Branch | Earlier checkpoint → 5,000 checkpoint | Film inventory | Maximum thickness | Final continuity residual | Coarse (`348.88 µm`) absorbed flow | Narrow reading |
|---|---|---:|---:|---:|---:|---|
| `010V2a` splash | `1963` → `5000` | `0.07431` → `0.20656 kg` (`2.78×`) | `0.164` → `0.399 mm` (`2.43×`) | `2.29e-3` → `7.475e-3` | `3.624` → `4.276 kg/s` | More stored film and coarse absorption, but the Fluent release also changed. |
| `010V2b` edge separation | `1498` → `5000` | `0.05639` → `0.20543 kg` (`3.64×`) | `0.123` → `0.450 mm` (`3.67×`) | `1.917e-3` → `7.405e-3` | `3.610` → `4.264 kg/s` | Film growth and stronger coarse interception coincide with a worse residual state. |
| `010V2c` stripping branch | `1446` → `5000` | `0.05440` → `0.20107 kg` (`3.70×`) | `0.121` → `0.410 mm` (`3.38×`) | not captured → not captured | `3.567` → `4.236 kg/s` | The final film/fate state changed strongly, but no later carrier/residual bundle was produced. |
| `010V2d` combined | `1520` → `5000` | `0.05668` → `0.20221 kg` (`3.57×`) | `0.125` → `0.457 mm` (`3.66×`) | `1.827e-3` → `8.209e-3` | `3.601` → `4.310 kg/s` | Film growth and stronger coarse interception coexist with a worse residual state. |

All reported final film CFL values at 5,000 remain below `0.011`, but this is only a single-state numerical indicator. It does not demonstrate that the film inventory has levelled off. For `010V2a`, `010V2b`, and `010V2d`, continuity residuals are about `3.3×`, `3.9×`, and `4.5×` higher at the later checkpoint; `010V2c` has no comparable late residual artifact.

## Film morphology and transport interpretation

The inventory increase is not simply a growth of one local peak. The area-weighted thickness rises by the same factor as inventory in every branch, while the maximum-to-area-average thickness ratio stays in the same order of magnitude. That indicates a thicker distributed film with retained localisation, not enough evidence to call it either a uniform coating or a single-cell artefact.

| Branch | Maximum / area-average thickness, earlier → 5,000 | Derived area-average film speed, earlier → 5,000 | Reported outlet-film-flow magnitude, earlier → 5,000 | Interpretation limit |
|---|---:|---:|---:|---|
| `010V2a` | `130` → `114` | `0.0665` → `0.1801 m/s` (`2.71×`) | `6.59e-6` → `2.98e-6 kg/s` (`-54.8%`) | Version changed; the flux is an instantaneous signed boundary report. |
| `010V2b` | `129` → `129` | `0.0530` → `0.1587 m/s` (`3.00×`) | `0` → `0 kg/s` | Stable localisation ratio; zero printed boundary flow is not an interval balance. |
| `010V2c` | `131` → `120` | `0.0516` → `0.1340 m/s` (`2.60×`) | `2.22e-6` → `1.78e-6 kg/s` (`-19.6%`) | Later carrier evidence is absent and no stripping mass is available. |
| `010V2d` | `130` → `134` | `0.0533` → `0.1331 m/s` (`2.50×`) | `0` → `0 kg/s` | Splash/separation/stripping events are not represented film-removal masses. |

The shared pattern—more inventory, higher area-averaged thickness, and about `2.5–3.0×` higher derived film speed without a corresponding measured source or draining term—makes **continued net film storage** the most plausible current interpretation. It is still an inference: the missing `film-dpm-mass-src` history prevents quantifying whether the driver is deposition, absent drainage reporting, an initialization transient, or another EWF source term.

## Size-resolved fate shift

Each 5,000-iteration DPM sweep has terminal fate rows that close to the printed precision. Across all four branches, the later state retains the original size ordering: fine droplets are principally steam-outlet escapes, while the coarse class is absorption-dominant. The intermediate-to-coarse bins show more final absorption and less escape at the later checkpoint.

The clearest normalized common result is the `348.88 µm` bin, where absorption changes from about three quarters to about nine tenths of its own represented injection mass in every branch:

| Branch | Coarse absorption share, earlier → 5,000 | Change | Crossover diameter | Reading |
|---|---:|---:|---:|---|
| `010V2a` | `77.48%` → `90.52%` | `+13.04 percentage points` | `168.81 µm` at both checkpoints | Stronger coarse interception; release change remains a confounder. |
| `010V2b` | `77.05%` → `90.68%` | `+13.63 percentage points` | `168.81 µm` at both checkpoints | Strongest matched-payload coarse trend. |
| `010V2c` | `76.25%` → `88.73%` | `+12.48 percentage points` | `168.81 µm` at both checkpoints | Same fate ordering despite missing late carrier evidence. |
| `010V2d` | `76.73%` → `90.15%` | `+13.42 percentage points` | `168.81 µm` at both checkpoints | Combined branch strengthens the same baseline size effect. |

The unchanged `168.81 µm` crossover matters. More iteration changes the **strength** of interception but does not show a new droplet-size regime or a reversal of the family’s fine-escape/coarse-absorption ordering. Splash, stripping, and separation counters remain interaction events or parcels, not additional terminal mass sinks; no represented mass for those secondary populations is available.

## Residual-history behaviour

Endpoint residuals alone can be misleading, so the available persisted histories were screened over their final 100 stored samples. Continuity is comparatively narrow over that stored tail, but it has moved to a higher level. More importantly, the turbulence residuals remain highly variable; this is incompatible with calling the late state numerically flat on the evidence available.

| Branch | Continuity: early last-100 mean → late last-100 mean | Late continuity range / late mean | Late `k` range / mean | Late epsilon range / mean | Interpretation |
|---|---:|---:|---:|---:|---|
| `010V2a` | `2.392e-3` → `7.354e-3` | `5.6%` | `464%` | `437%` | Continuity plateaued at a worse level; turbulence remains strongly bouncy. |
| `010V2b` | `1.856e-3` → `7.280e-3` | `8.2%` | `661%` | `527%` | Late turbulence variability increased materially from the earlier record. |
| `010V2c` | `1.787e-3` → unavailable | unavailable | unavailable | unavailable | The failed late carrier export blocks a numerical-continuation conclusion. |
| `010V2d` | `1.845e-3` → `7.710e-3` | `11.6%` | `381%` | `234%` | The late state is not flat enough to interpret rising film inventory as a settled steady result. |

These are ranges of stored scaled residuals, not an independently supplied convergence criterion. They show why the lower final `k`/epsilon endpoints in `010V2a` should not be read as a clean improvement: their last-100-sample means and ranges remain much higher and broader than a single final value suggests.

## What the later `010V2d` checkpoint changes

The `010V2d` 10,000-iteration follow-up directly tests the idea that more iteration may simply settle the 5,000-iteration film state. It does not support that idea: from 5,000 to 10,000, film inventory rises a further `42.6%` (`0.2022` → `0.2884 kg`), maximum thickness rises `34.2%`, and continuity rises `182%` (`8.209e-3` → `2.315e-2`). The maximum film CFL jumps from `5.07e-3` to `3.03` (about `599×`).

This does not prove the other branches would behave identically, but it is strong evidence against an uninstrumented “run longer and inspect another final snapshot” workflow. The next continuation must collect interval histories and include a CFL guard.

## What the comparison supports

**Reported:** final film inventory and maximum thickness are approximately `2.8–3.7×` their earlier reported values across `010V2a`–`010V2d`; the coarse absorption share rises consistently by about `12.5–13.6 percentage points`, while the absorption/escape crossover stays at `168.81 µm`.

**Inferred:** the common direction is consistent with continued net film storage and increasing DPM-to-film interception rather than a demonstrably stationary film state. The broadly preserved localisation ratio suggests the film is thickening within the same general wall pattern, not changing into a wholly different geometry-wide state.

**Not established:** carrier convergence, EWF mass closure, a physical accumulation rate, separator efficiency, or a difference caused solely by any optional mechanism. Every available selected-surface carrier comparison retains an approximately `57.54%` inlet-flow imbalance, and the necessary film source/outflow histories are absent.

The paper lookup was checked for applicable EWF guidance. It identifies film thickness, film velocity, deposition/entrainment rates, and field mass flows as the outputs required for an EWF-DPM interpretation, while cautioning that its annular-flow source is not a geothermal-separator validation basis ([annular-flow lookup](../../CFD_wiki/paper_lookup/broad/annular-flow-fluent-and-three-field.md)). The present records have only final snapshots, so they do not meet that stronger accounting standard.

## Decision and ranked next evidence

1. **First, instrument one branch before continuing it.** Correct the `film-dpm-mass-src` and `film-velocity-mag` aliases, then record film inventory, film CFL, DPM-to-film source, all film-boundary flows, and stripped/separated mass where active at a defined cadence. Stop or inspect immediately if film CFL exceeds `1`; the `010V2d` 10,000-iteration outcome makes this a concrete guard rather than a generic caution.
2. **Close the carrier scope over the identical interval.** Report every carrier inlet/outlet and the phase/material mapping, including the lower liquid route or an explicit stored-liquid term. Until then, an apparently unchanged steam-outlet vapor flow only shows a stable *scoped* readout, not a stable separator state.
3. **Use one verified restart pair.** Save and expose the starting case/data name, keep Fluent version and six-bin injection payload fixed, and run a short accepted interval for a clean control plus one mechanism branch. Then normalize original-particle fates by the fixed injection mass and keep secondary events in a separate ledger.
4. **Do not use another end-only checkpoint as a decision gate.** It cannot distinguish real film accumulation from numerical/state drift, and it cannot reconcile storage with deposition, drainage, splash, stripping, or separation.

## Evidence

- [010V2a splash report](../../Setups/reports/010V2a/results.md)
- [010V2b edge-separation report](../../Setups/reports/010V2b/results.md)
- [010V2c stripping report](../../Setups/reports/010V2c/results.md)
- [010V2d combined report](../../Setups/reports/010V2d/results.md)
