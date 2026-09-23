# Phase 7.2A Family R results

## Outcome

Family R is complete for `R0`–`R5`. The two human-requested rougher extensions
reduced the modeled phase-2 `steamoutlet` flux magnitude relative to the smooth
control: `R4` by `9.79%` and `R5` by `20.58%` over the matched tail-500 window.
This reverses the earlier R0–R3 negative outlet screen, but does **not** establish
improved separation or wall drainage. `R4` remains oscillatory with elevated
late residuals, while `R5` lost about `162 kg` of domain liquid over the child
run. Its lower outlet flux may reflect liquid depletion rather than improved
routing. The source-inclusive ledger is non-closing, and the wall-surface
velocity report cannot resolve near-wall motion. Phase 7.2A remains open while
the independent EWF branch is separately owned.

## Execution identity and controls

All six children were run on Server 1 from the same verified native-iteration
5586 parent:

- case SHA-256: `4fd493972839929f1f0922ad42679456d1f4aea294da86e4b13d6b7c32f754fc`;
- data SHA-256: `b2261fac8626b2e338c3a9c80c334c8a910d1bfb536f782ef9234623f00e1a72`;
- exact parent paths: [baseline-control-handoff.md](../baseline-control-handoff.md);
- child native window: `5586` through `8586`, inclusive;
- solve control: one literal `/solve/iterate 3000` command per case, with no
  Python iteration loop, reinitialization, patch, inlet ramp, or solver change;
- monitor cadence: every native iteration (`3001` matched rows per report);
- checkpointing: paired server-local case/data autosaves every 250 native
  iterations and paired local plus OneDrive terminal artifacts; and
- EWF remained off, all bottom boundaries remained unchanged, and roughness
  was applied only to `separator-purnanto:1`,
  `separator-purnanto:1:001`, `wall`, and `wall:004`.

`R4` and `R5` were added under the [extension setup](extension-r4-r5-setup.md),
with `k_s=1e-3 m` and `2e-3 m` respectively and `C_s=0.5` in both. Their
prepared cases and terminal case/data pairs passed native reopen/readback;
the four intended wall zones had the requested roughness and the bottom walls
remained smooth. Both queue and case manifests report `COMPLETE`.

The R0 Windows directory-list helper returned an invalid-path message after the
solve, so its manifest's parsed directory inventory is empty. Its native solve
transcript independently records all 12 paired checkpoint writes. The parser
was corrected before R1–R3; each later manifest contains 12 paired checkpoints
derived from those native transcript write records.

## Matched tail comparison

Statistics below use only child offsets `2501`–`3000`. Fluent's outlet sign is
retained: the phase-2 `steamoutlet` values are negative, and carryover is
compared by magnitude. `±` is the sample standard deviation over the tail-500
window, not an uncertainty interval.

| Case | `k_s` (m) | Phase-2 outlet (kg/s) | Magnitude change vs R0 | Total liquid mass (kg) | Mass slope (kg/iteration) | Lower-zone liquid mass (kg) | Mean absorber command error (kg/s) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `R0` | `0` | `-24.3715 ± 0.0219` | `0.00%` | `296.022` | `+3.52e-4` | `0.0957` | `-0.603` |
| `R1` | `5e-5` | `-29.5412 ± 0.0338` | `+21.21%` | `320.652` | `-1.78e-4` | `0.0971` | `-2.382` |
| `R2` | `2e-4` | `-28.0762 ± 0.0314` | `+15.20%` | `312.905` | `+3.54e-5` | `0.1132` | `-1.609` |
| `R3` | `5e-4` | `-24.6518 ± 0.0583` | `+1.15%` | `298.154` | `+1.36e-4` | `0.1770` | `-0.244` |
| `R4` | `1e-3` | `-21.9851 ± 1.2723` | `-9.79%` | `262.490` | `-6.17e-4` | `0.2133` | `~0` |
| `R5` | `2e-3` | `-19.3568 ± 0.0114` | `-20.58%` | `134.086` | `+5.34e-4` | `0.2635` | `~0` |

The total-inventory slopes are small over the matched tail, but this does not
erase the much larger whole-run inventory changes. `R4` finishes at `262.135 kg`
and `R5` at `134.192 kg`, versus their common initial `295.854 kg`: losses of
`33.719 kg` and `161.662 kg`. `R4`'s outlet still trends upward over the tail
(`+0.00460 kg/s` per iteration) and its residuals remain elevated. `R5`'s
outlet is comparatively steady (tail slope `-1.11e-5 kg/s` per iteration),
but its reduced inventory makes the outlet result physically ambiguous. No case
recorded an AMG failure, floating-point exception, nonfinite value, or fatal
solver event. Reversed-flow and turbulent-viscosity-limit messages persist in
all children and are therefore retained as solver-health context, not hidden.

## Claim limits

- The direct matched response is non-monotonic: `R1`–`R3` did not reduce outlet
  carryover, whereas `R4`–`R5` did. `R5` is the clearest numerical outlet
  reduction, not a qualified separation improvement.
- The outer-wall surface-area-average liquid vertical velocity is identically
  zero in every child because the report samples the no-slip wall surface. It
  therefore does not resolve wall-adjacent routing and cannot support a
  mechanistic drainage claim.
- The direct inlet/outlet/source algebraic ledger remains non-closing in every
  case despite nearly stationary tail inventories. Consequently the outlet
  comparison is usable as a matched response, but the present evidence does
  not support an absolute phase or mixture closure claim.
- Lower-zone liquid mass remains highly iteration-oscillatory. Its small mean
  differences are contextual only and are not used to claim successful lower
  delivery.
- `R4` and `R5` were run under a subsequent explicit human extension request,
  superseding the original conditional `R4` trigger. No further roughness case
  is selected here.

## Evidence

- R0 queue and case manifests:
  `PyAnsys/output/phase72a_family_r/20260922T103758Z/`;
- R1–R3 queue and case manifests:
  `PyAnsys/output/phase72a_family_r/20260922T110217Z/`;
- R4–R5 queue and case manifests:
  `PyAnsys/output/phase72a_family_r/20260923T021955Z/`;
- six-case matched metrics, table, and figures:
  `PyAnsys/output/phase72a_family_r/analysis-20260923T021955Z/`;
- executable queue owner:
  `PyAnsys/scripts/setup/run_phase72a_family_r_native.py`; and
- analysis owner:
  `PyAnsys/scripts/inspection/analyze_phase72a_family_r.py`.

The minimum figure set is:

1. `01-phase2-steamoutlet-carryover.png` — matched carryover response;
2. `02-liquid-inventories.png` — total and lower-zone inventories;
3. `03-wall-velocity-and-absorber-error.png` — zero wall-surface velocity and
   absorber tracking error;
4. `04-vapor-and-absorber.png` — vapor outlet and absorber histories; and
5. `05-residual-histories.png` — complete child residual histories.
