# Phase 7.2A Family R results

## Outcome

Family R is complete for `R0`–`R11`, including the human-selected `C_s` sensitivity at the R3 and R5 roughness heights. The human-requested rougher extensions
reduced the modeled phase-2 `steamoutlet` flux magnitude relative to the smooth
control: `R4` by `9.79%`, `R5` by `20.58%`, `R6` by `38.38%`, and `R7` by
`44.09%` over the matched tail-500 window.
This reverses the earlier R0–R3 negative outlet screen, but does **not** establish
improved separation or wall drainage. `R4` and `R9` show oscillatory outlet histories, and R9 has elevated
late residuals; `R5`–`R7` lost about `162`, `183`, and `187 kg` of domain liquid
over their respective child runs. The `C_s` sensitivity reduced outlet magnitude further at matched `k_s`, while R8–R11 lost `6`, `34`, `180`, and `186 kg`, respectively. Their lower outlet flux may reflect liquid
depletion rather than improved routing. The source-inclusive ledger is
non-closing, and the wall-surface
velocity report cannot resolve near-wall motion. Phase 7.2A remains open while
the independent EWF branch is separately owned.

## Execution identity and controls

All twelve children were run on Server 1 from the same verified native-iteration
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

`R6` and `R7` followed the [doubled-roughness setup](extension-r6-r7-setup.md)
at `k_s=4e-3 m` and `8e-3 m`, respectively. Their exact-parent hash and
native-coordinate checks, wall-only readbacks, prepared save/reopen gates,
`3001` rows in each of 16 reports, 12 paired server-local checkpoints each,
and terminal durable pair reopens passed. Their queue and case manifests
report `COMPLETE` at native iteration 8586.

`R8`–`R11` followed the [roughness-constant sensitivity setup](extension-r8-r11-setup.md). At both `k_s=5e-4 m` and `2e-3 m`, `C_s=0.75` and `1.0` were tested as fresh children of the common native-5586 parent. All four passed wall-only readback, unchanged-model audit, prepared save/reopen, one `/solve/iterate 3000` TUI command, 12 paired 250-iteration server-local checkpoints, 16 report histories with 3001 points each, and terminal durable-pair reopen at 8586. The four manifests report `COMPLETE`; no AMG, FPE, nonfinite, or fatal event occurred. Reverse-flow and turbulent-viscosity-limit messages occurred on all 3000 iterations in every case.

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

| Case | `k_s` (m) | `C_s` | Phase-2 outlet (kg/s) | Magnitude change vs R0 | Total liquid mass (kg) | Mass slope (kg/iteration) | Lower-zone liquid mass (kg) | Mean absorber command error (kg/s) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `R0` | `0` | `0.5` | `-24.3715 ± 0.0219` | `0.00%` | `296.022` | `+3.52e-4` | `0.0957` | `-0.603` |
| `R1` | `5e-5` | `0.5` | `-29.5412 ± 0.0338` | `+21.21%` | `320.652` | `-1.78e-4` | `0.0971` | `-2.382` |
| `R2` | `2e-4` | `0.5` | `-28.0762 ± 0.0314` | `+15.20%` | `312.905` | `+3.54e-5` | `0.1132` | `-1.609` |
| `R3` | `5e-4` | `0.5` | `-24.6518 ± 0.0583` | `+1.15%` | `298.154` | `+1.36e-4` | `0.1770` | `-0.244` |
| `R4` | `1e-3` | `0.5` | `-21.9851 ± 1.2723` | `-9.79%` | `262.490` | `-6.17e-4` | `0.2133` | `~0` |
| `R5` | `2e-3` | `0.5` | `-19.3568 ± 0.0114` | `-20.58%` | `134.086` | `+5.34e-4` | `0.2635` | `~0` |
| `R6` | `4e-3` | `0.5` | `-15.0171 ± 0.0161` | `-38.38%` | `111.973` | `+1.32e-3` | `0.3636` | `~0` |
| `R7` | `8e-3` | `0.5` | `-13.6253 ± 0.0331` | `-44.09%` | `108.803` | `-4.36e-5` | `0.2805` | `~0` |
| `R8` | `5e-4` | `0.75` | `-22.6660 ± 0.1292` | `-7.00%` | `290.038` | `-6.82e-5` | `0.2065` | `~0` |
| `R9` | `5e-4` | `1.0` | `-21.8994 ± 1.2839` | `-10.14%` | `261.805` | `-3.64e-4` | `0.2152` | `-0.0623` |
| `R10` | `2e-3` | `0.75` | `-15.7045 ± 0.0066` | `-35.56%` | `115.773` | `-2.86e-4` | `0.3436` | `~0` |
| `R11` | `2e-3` | `1.0` | `-14.0164 ± 0.0160` | `-42.49%` | `109.746` | `-7.85e-4` | `0.3671` | `-0.0813` |

The total-inventory slopes are small over the matched tail, but this does not
erase the much larger whole-run inventory changes. `R4` finishes at `262.135 kg`
and `R5` at `134.192 kg`, versus their common initial `295.854 kg`: losses of
`33.719 kg` and `161.662 kg`. `R4`'s outlet still trends upward over the tail
(`+0.00460 kg/s` per iteration) and its residuals remain elevated. `R5`'s
outlet is comparatively steady (tail slope `-1.11e-5 kg/s` per iteration),
but its reduced inventory makes the outlet result physically ambiguous.

`R6` and `R7` finish at `112.355 kg` and `108.744 kg`, respectively, from the
same `295.854 kg` start: losses of `183.498 kg` and `187.109 kg`. Their
tail-500 outlet fluxes are comparatively tight, and the phase-1 outlet means
remain near `-80.4 kg/s`, but this does not resolve the liquid path. The
lower-zone mass report is small and oscillatory relative to the domain losses.
The reduction from R6 to R7 is only `1.392 kg/s`, while both show almost the
same very low inventory. This pattern is consistent with a depletion-driven
outlet response, though the current reports cannot establish causation.

No case recorded an AMG failure, floating-point exception, nonfinite value, or fatal
solver event. Reversed-flow and turbulent-viscosity-limit messages persist in
all children and are therefore retained as solver-health context, not hidden.


## Roughness-constant sensitivity

At the R3 height (`k_s=5e-4 m`), increasing `C_s` from `0.5` to `0.75`
changed tail-500 phase-2 outlet magnitude by `-8.06%` relative to R3; at
`C_s=1.0` the change was `-11.17%`. R8 was comparatively tight (`SD=0.129
kg/s`); R9 was highly variable (`SD=1.284 kg/s`) and its tail outlet trend
was `+4.93e-3 kg/s per iteration`. Their total domain liquid losses were
`6.01 kg` and `34.33 kg`, respectively.

At the R5 height (`k_s=2e-3 m`), the outlet magnitude fell a further `18.87%`
for `C_s=0.75` and `27.59%` for `C_s=1.0` relative to R5 (`C_s=0.5`). The
corresponding whole-run domain liquid losses grew from `161.66 kg` in R5 to
`180.21 kg` in R10 and `186.33 kg` in R11. This reinforces the existing
interpretation: larger modeled roughness response coincides with severe domain
liquid depletion and does not demonstrate improved separation.

The four matched child windows all end at native iteration 8586. R8, R10,
and R11 have relatively narrow outlet tails; R9 is strongly oscillatory. All
four have large negative phase-2 source-inclusive closure means (about `-22.64`,
`-21.88`, `-15.71`, and `-14.04 kg/s` for R8–R11 by the runner's sign-retained
ledger), so this sensitivity remains a modeled response screen and not an
absolute balance or physical validation.

## Claim limits

- The direct matched response is non-monotonic: `R1`–`R3` did not reduce outlet
  carryover, whereas `R4`–`R11` did. `R11` gives the lowest modeled outlet flux,
  not a qualified separation improvement.
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
- `R4`–`R11` were run under subsequent explicit human extension requests,
  superseding the original conditional `R4` trigger. No further roughness case
  is selected here.

## Evidence

- R0 queue and case manifests:
  `PyAnsys/output/phase72a_family_r/20260922T103758Z/`;
- R1–R3 queue and case manifests:
  `PyAnsys/output/phase72a_family_r/20260922T110217Z/`;
- R4–R5 queue and case manifests:
  `PyAnsys/output/phase72a_family_r/20260923T021955Z/`;
- R6–R7 queue and case manifests:
  `PyAnsys/output/phase72a_family_r/20260923T043840Z/`;
- eight-case matched metrics, table, and figures:
  `PyAnsys/output/phase72a_family_r/analysis-20260923T043840Z/` (R0–R7);
- twelve-case matched metrics, table, and figures: `PyAnsys/output/phase72a_family_r/analysis-20260923T054600Z-cs-sensitivity-v2/`;
- R8–R11 queue and case manifests: `PyAnsys/output/phase72a_family_r/20260923T054600Z/`;
- executable queue owner:
  `PyAnsys/scripts/setup/run_phase72a_family_r_native.py`; and
- analysis owner:
  `PyAnsys/scripts/inspection/analyze_phase72a_family_r.py`.

The twelve-case comparison figure set is:

1. `01-phase2-steamoutlet-carryover.png` — matched carryover response;
2. `02-liquid-inventories.png` — total and lower-zone inventories;
3. `03-wall-velocity-and-absorber-error.png` — zero wall-surface velocity and
   absorber tracking error;
4. `04-vapor-and-absorber.png` — vapor outlet and absorber histories; and
5. `05-residual-histories.png` — complete child residual histories;
6. `06-Cs-sensitivity-at-matched-height.png` — direct `C_s` comparison at the R3 and R5 roughness heights.
