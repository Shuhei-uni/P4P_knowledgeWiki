# Phase 7.1A v2 inlet-loading ramp result

## Answer at a glance

The v2 inlet-development case completed its recorded `2,000` steady Fluent
iterations on `student` from the exact prepared v2 baseline pair. The same
live case was then continued by the user to native iteration `4,002`. The
liquid and steam
inlets were scheduled together from `0.25` of the prior experiment's base
targets toward `116.92 kg/s` liquid and `80.69 kg/s` steam over the requested
horizon, with updates every 10 iterations. Native report histories and the
original residual transcript each contain `2,000` points; the active
continuation Report Files now contain `2,003` points from iterations `2,000`
through `4,002`.

The absorber does begin to realize its inlet-derived command once liquid has
developed in the lower zone. By the late part of the run, the native applied
phase-2 source agrees with the named removal to machine precision and follows
the command. The whole-separator liquid inventory nevertheless grows strongly
through the horizon, while the lower-zone inventory remains only about
`0.10 kg`. The continuation to native iteration `4,002` increases the
lower-zone inventory to `2.497 kg` and the total inventory to `318.661 kg`.
This is useful liquid-development evidence, not a steady or bounded-inventory
result.

One native monitor initialization artifact is retained explicitly: report
iteration `1` contains the inherited parent liquid command (`111.22015 kg/s`)
before the child schedule is reflected in the report cache. From iteration `2`
the inlet history is on the declared ramp, beginning at `29.23 kg/s`; the
control readback confirms that the child schedule was reapplied after the
prepared pair was reopened. The artifact is visible in the raw histories and
is not removed from the evidence.

## Controlled case

| Item | Recorded value |
| --- | --- |
| Runtime | Fluent 2025 R2 on `student` |
| Exact parent | `P71A-BASELINE-V2-VIRTUAL-OUTLET-prepared` pair from the v2 baseline build |
| Start multiplier | `0.25` |
| Active horizon | `2,000` steady iterations |
| Update interval | `10` iterations |
| Liquid base target | `116.92 kg/s` |
| Steam base target | `80.69 kg/s` |
| Absorber law | v2 `P71V2Sink`, driven by the instantaneous phase-2 liquid-inlet throughput |
| Boundary controls | `steamoutlet` is the only pressure outlet; bottom boundaries remain walls; no direct phase-1 source |
| Checkpoints | paired case/data at active `0`, `500`, `1,000`, `1,500`, and `2,000` |

The base targets are the recorded targets from the prior inlet-loading
experiment. They are deliberately different from the v2 prepared parent's
inherited `111.22015 kg/s` liquid and `76.7563625 kg/s` steam settings; the
child schedule reaches the prior experiment's base targets at the end of the
ramp.

## Native observations

The flux signs in the native reports are outward-positive at the outlet below;
the stored Fluent values are negative for an outward outlet flux. The terminal
command shown in the report is one control block behind the final scheduled
boundary target because the schedule is updated after each 10-iteration solve
block. The final boundary schedule itself is `116.92 kg/s` liquid and
`80.69 kg/s` steam. The new native continuation report files reach iteration
`4,002` and record those final inlet values directly.

| Monitor | Iteration 1 | Iteration 2 | Iteration 2,000 | Iteration 4,002 | Interpretation |
| --- | ---: | ---: | ---: | ---: | --- |
| Liquid inlet flux | `111.220 kg/s` parent-cache artifact | `29.230 kg/s` | `116.482 kg/s` | `116.920 kg/s` | Boundary schedule reaches the declared liquid base target |
| Steam inlet flux | `76.756 kg/s` parent-cache artifact | `20.173 kg/s` | `80.387 kg/s` | `80.690 kg/s` | Boundary schedule reaches the declared steam base target |
| Phase-1 steam outlet, outward-positive | `~75.075 kg/s` | `~76.359 kg/s` | `80.311 kg/s` | `80.497 kg/s` | Vapor outlet routing continues to change during the extension |
| Phase-2 steam outlet, outward-positive | `~0 kg/s` | `~0 kg/s` | `9.156 kg/s` | `22.116 kg/s` | Phase-2 outlet flux increases substantially after the 2,000-iteration point |
| Mixture steam outlet, outward-positive | `~75.075 kg/s` | `~76.359 kg/s` | `89.467 kg/s` | `102.624 kg/s` | Mixture outlet is the sum of the phase-resolved outlet reports |
| Absorber command | `111.220 kg/s` parent-cache artifact | `29.230 kg/s` | `116.482 kg/s` | `116.920 kg/s` | Declared command follows the final inlet loading |
| Named absorber removal | `~0 kg/s` | `0 kg/s` | `116.482 kg/s` | `116.920 kg/s` | Lower zone is initially starved, then removal develops |
| Native applied phase-2 source | `~0 kg/s` | `0 kg/s` | `-116.482 kg/s` | `-116.920 kg/s` | Negative sign is the applied sink; its positive removal magnitude matches the named removal |
| Total liquid mass | `0.0145 kg` | `0.0186 kg` | `183.595 kg` | `318.661 kg` | Inventory continues increasing during the extension |
| Total liquid volume | `1.646e-5 m3` | `2.107e-5 m3` | `0.208344 m3` | `0.361617 m3` | Same inventory-growth signal in volume form |
| Lower-zone liquid mass | `~0 kg` | `0 kg` | `0.102785 kg` | `2.497303 kg` | The absorber region now contains appreciable liquid, but inventory is not bounded |
| Lower-zone available liquid volume | `3.02e-23 m3` | `0 m3` | `1.16641e-4 m3` | `2.833945e-3 m3` | Starvation has eased materially by iteration 4,002 |

### Native continuation readback at iteration 4,002

The new column is based on the live `student` session and the active Fluent
Report File objects, not on an extrapolation of the earlier 2,000-point local
history. Fluent's active continuation report files contain `2,003` native
points from iterations `2,000` through `4,002`; their generated names end in
`_2001.out`. The final native report points are preserved in
[live-4002-readback.json](live-4002-readback.json). The live named-expression
readback independently reports `P71V2Iteration = 4002`,
`P71V2Command = 116.92 kg/s`, `P71V2Removal = 116.92 kg/s`, and
`P71V2AvailableVolume = 2.833945e-3 m3`.

For the outlet rows, the table displays outward-positive mass flow. The raw
Fluent native values at iteration `4,002` are `-80.497349 kg/s` for phase 1,
`-22.116498 kg/s` for phase 2, and `-102.623831 kg/s` for the mixture. The
phase-2 liquid-inlet native report is `+116.92 kg/s`; the absorber source is
`-116.92 kg/s`.

After approximately the first few hundred iterations, the native applied
removal and named-expression removal track the command to numerical precision;
from native iteration `501` onward their maximum absolute difference is about
`3e-13 kg/s`. This demonstrates that the v2 source law is being applied when
liquid is available. It does not demonstrate that the commanded removal is a
physically validated absorber capacity.

## Numerical adequacy and limitations

The original 2,000-iteration run completed without a fatal solver diagnostic
and all recorded residual values were finite. The live residual monitor was
then read at native iteration `4,002`; it contains `1,902` points from
iterations `4` through `4,002`. Its endpoint values are:

| Residual | Iteration 2,000 | Iteration 4,002 | Numerical-adequacy reading |
| --- | ---: | ---: | --- |
| Continuity | `9.6158e-3` | `1.7277e-2` | Finite, but increased; not a steady-state qualification |
| x velocity | `3.6501e-5` | `9.1403e-5` | Finite, but increased |
| y velocity | `2.3141e-5` | `8.6271e-5` | Finite, but increased |
| z velocity | `4.0999e-5` | `9.7133e-5` | Finite, but increased |
| k | `4.2133e-4` | `9.0266e-4` | Finite, but increased |
| epsilon | `1.4913e-3` | `2.1760e-3` | Finite, but increased |
| phase-2 volume fraction | `1.7241e-3` | `2.5992e-3` | Finite, but increased |

**Numerical adequacy at iteration 4,002: finite but not qualified.** All seven
residuals remain finite, but all are higher than at iteration `2,000`, with
continuity increasing from `9.62e-3` to `1.73e-2`. The continuation therefore
does not provide evidence of residual improvement or steady convergence.

The transcript reports roughly `245–263` reversed-flow faces at the pressure
outlet through the late portion of the run. The residuals and outlet warnings,
together with the continuously increasing inventory, mean this is a finite-
horizon discovery trajectory. It must not be called converged, steady,
bounded, or physically validated on the evidence above. The live continuation
readback adds native observations and a residual-monitor endpoint comparison
through iteration `4,002`. It still cannot be used to claim that the extended
case became numerically adequate.

The principal scientific reading is therefore: the gentler inlet ramp develops
liquid into the v2 domain and eventually gives the virtual outlet enough local
liquid to realize its feed-forward sink. Continuing to iteration `4,002`
increases lower-zone liquid from `0.102785 kg` to `2.497303 kg`, but total
liquid inventory also increases from `183.595 kg` to `318.661 kg`, while the
phase-2 outlet contribution increases from `9.156 kg/s` to `22.116 kg/s`.
The extension therefore confirms ongoing liquid development and altered phase
routing, not a stable operating point. The next decision should use native
phase-resolved fluxes, source-inclusive balances, late-window inventory slope,
and outlet reverse-flow behaviour rather than residual magnitude alone.

## Evidence and artifacts

- [Setup contract](setup.md)
- [Run-path map](run-paths.yaml)
- [Run manifest](../../../../PyAnsys/output/phase71a_v2_inlet_loading/20260922T031500Z/run-manifest.json)
- [Native report histories](../../../../PyAnsys/output/phase71a_v2_inlet_loading/20260922T031500Z/report-histories.json)
- [Residual history](../../../../PyAnsys/output/phase71a_v2_inlet_loading/20260922T031500Z/residuals.json)
- [Solver transcript](../../../../PyAnsys/output/phase71a_v2_inlet_loading/20260922T031500Z/transcript.txt)
- [Inlet-loading summary figure](../../../../PyAnsys/output/phase71a_v2_inlet_loading/20260922T031500Z/v2-inlet-loading-summary.png)
- [Live iteration-4,002 readback](live-4002-readback.json)

The authoritative local evidence directory is
`PyAnsys/output/phase71a_v2_inlet_loading/20260922T031500Z`. The final paired
case/data artifacts remain on the Fluent host at the OneDrive final root
recorded in `run-manifest.json`:

```text
C:\Users\Shuhei Yokkaichi\OneDrive\OneDrive - The University of Auckland\P4P-Fluent-Artifacts\Phase71A\V2InletLoading\finals\P71A-V2-INLET-LOADING-RAMP\20260922T031500Z\P71A-V2-INLET-LOADING-RAMP-active2000.cas.h5
C:\Users\Shuhei Yokkaichi\OneDrive\OneDrive - The University of Auckland\P4P-Fluent-Artifacts\Phase71A\V2InletLoading\finals\P71A-V2-INLET-LOADING-RAMP\20260922T031500Z\P71A-V2-INLET-LOADING-RAMP-active2000.dat.h5
```

Final SHA-256 identities:

- case: `6c802f8b36c95292f47a925d429bdb92c8bf66cc87cfddb7b36ffc78be5f5d43`
- data: `12f165d67efd6756d9dd0ff69609a577e2bf0a89215450f1fd834d979cf58fca`

The earlier `20260922T024000Z` attempt is superseded and is not used for the
scientific result because its initial post-reopen control block was not
verified cleanly. The `20260922T031500Z` run is the authoritative evidence
package, with the single iteration-1 native monitor-cache artifact documented
above.
