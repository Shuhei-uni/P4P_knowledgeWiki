# Split-Inlet Adaptive Mass-Balance Sink Control

## Purpose and evidence status

Setup `07e` is the final no-geometry-change diagnostic before a resolved brine
outlet. It tests whether deliberately enforcing the missing liquid discharge
rate is sufficient to stabilize the steady carrier solution.

- Study ID: `split_inlet_mass_balance_sink_control_20260810`
- Run label: `mesh-900k_band0p140165_target116p92_v1`
- Final status: `Completed diagnostic / unresolved at maximum iteration budget`
- DPM/EWF: off.
- Evidence-use rule: numerical mass-closure control only. It cannot validate
  outlet hydraulics, separator efficiency, mesh convergence, a physical free
  surface or physical-time accumulation.

## Controlled formulation

The qualified setup-07c liquid-only source and complete `0.1401652536 m`
bottom-local band are retained. No new UDF is compiled in the persistent
Fluent session. Instead, after each 100-iteration feedback block the controller
uses the measured band liquid inventory to update the existing time scale:

```text
tau_next = clamp(M_liquid,band / 116.92, 0.002, 0.2) s
```

Because the source law is `S=-rho_l alpha_l R/tau`, the instantaneous
integrated source after each update targets `R * 116.92 kg/s`, subject to the
tau bounds and redistribution during the next block.

This is explicitly an empirical global feedback control, not a physical drain
boundary. It is useful because it separates “missing liquid mass closure” from
the remaining pressure/velocity/residual stability question.

## Unchanged controls

- setup-07c verified clean prepared 900k checkpoint followed by fresh Hybrid
  Initialization;
- 5,335,623 cells and the same complete 92,058-cell sink band;
- steady pressure-based Mixture, vapor primary/liquid secondary;
- RNG k-epsilon, gravity `(0,-9.81,0)`, Energy off;
- SIMPLE/PRESTO and inherited discretization/URFs;
- liquid/vapor inlets `116.92/80.69 kg/s`, steam outlet `1.12 MPa`;
- bottom remains a stationary wall;
- carried mixture-momentum sources retained;
- DPM interaction off with no injection update or tracking.

## Execution and decision gates

- guarded 1,000-iteration target ramp;
- up to 2,000 full-strength iterations;
- 100-iteration feedback/monitor blocks;
- separate fresh start, ramp, R1 = 1000, R1 = 2000 and final ramp-zero
  case/data;
- early stop for sink above `175 kg/s`, non-finite fields, DPM activation or
  abrupt pressure change;
- acceptance still requires two consecutive passing 500-iteration windows,
  corrected phase/mixture balance, stable physical monitors, non-growing
  residuals and residual levels within the existing gates.

If the mass balance closes but pressure/inventory/velocity do not stabilize,
the result will show that closure alone is insufficient. If the full field
stabilizes, it may be used as a diagnostic carrier control and visualization
source, but the resolved brine outlet remains required for physical claims.

## Accepted launch readback

The non-overwriting production branch was accepted for execution on
2026-08-10 NZST:

- Fluent `2024 R2`, `16` partitions and `5,335,623` cells;
- minimum orthogonal quality `0.202194`, maximum aspect ratio `20.1267`, no
  negative-volume report;
- verified source-hooked prepared fingerprint
  `c5294907faca60ff1305d37573102078d338f8bf06a942f03179a3b4711b128e`;
- complete `92,058`-cell, `0.44378932 m3` bottom-local band;
- fresh Hybrid Initialization after the initial `tau=0.02 s` assignment;
- separate `start_from_prepared07c_fresh_hybrid_tau0p020_ramp0` case/data;
- pressure-based steady Mixture, RNG k-epsilon, Energy off, gravity
  `(0,-9.81,0)`, unchanged phase/boundary settings and bottom wall;
- DPM interaction read back off; no injection update or tracking;
- exactly one detached controller active.

Through the recorded 500-iteration milestone the freshly initialized liquid
front had not yet reached the bottom-local band, so the measured band inventory
and achieved sink remained zero and the bounded feedback correctly selected
`tau=0.2 s`. This is consistent with both completed clean-start controls:
setup 07c and setup 07d first recorded non-negligible band liquid at cumulative
iteration 1250 (`R=1` iteration 250), at `0.00136457 kg` and `0.00199486 kg`,
respectively. The early zero response is therefore treated as a repeatable
transport delay from vapor-filled Hybrid Initialization rather than evidence
of a sink failure. Setup-07e feedback tracking becomes informative only after
phase-2 liquid occupies the marked band; the complete ramp and full-strength
histories remain required for the decision.

The dry-band repeatability audit is exact at the six common saved cumulative
iterations 100, 200, 350, 500, 750 and 1000. Setup 07e and the accepted setup-07d control
have `0.000000%` difference in pressure drop, domain liquid inventory,
mixture/vapor outlet flow, outlet/domain velocity and domain vorticity. At
iteration 500 both report pressure drop `6.8532 kPa`, domain liquid inventory
`12.848118 kg` and outlet velocity `33.57063 m/s`; setup 07c differs by only
`0.45%` in pressure and less than `0.01%` in inventory at that point. This
supports deterministic clean-start lineage and confirms that adaptive `tau`
changes do not alter the solution while the marked band contains no liquid.

At cumulative iteration 600, after the ramp advanced to `R=0.5`, pressure drop
rose to `9.8355 kPa` while the band was still dry. The `43.5%` change from the
iteration-500 block is recorded as startup evolution, not an acceptance
window. The implemented abrupt-pressure guard intentionally begins only after
`R=1` iteration 750; full-strength changes above `20%` then trigger a guarded
stop.

At cumulative iteration 750, the final saved `R=0.5` state remained dry-band
and exactly matched setup 07d. Pressure drop/domain inventory were
`11.9955 kPa`/`16.6630 kg`; continuity and liquid-VF residual were
`0.381361`/`8.40067e-4`. The controller then advanced into the final
`R=0.75` ramp segment without a duplicate or safety event.

At cumulative iteration 1000, the guarded ramp completed with the active band
still effectively dry (`1.30160e-12 kg`) and achieved sink
`4.88101e-12 kg/s`. Pressure drop/domain inventory were
`15.2466 kPa`/`22.5761 kg`; continuity and liquid-VF residual were
`0.405080`/`6.60996e-4`. This state exactly matches setup 07d across all seven
controlled lineage fields. The controller selected the bounded minimum
`tau=0.002 s`, saved the separate ramp-complete case/data pair and entered the
first `R=1` feedback block. These are transition and lineage results only;
feedback tracking remains uninterpretable until liquid occupies the band.

The first material control response was recorded at cumulative iteration 1300
(`R=1` iteration 300). With `tau` still at its bounded `0.002 s` minimum, the
band held `0.00243195 kg` and the achieved numerical sink reached
`1.21598 kg/s`, only `1.040%` of the `116.92 kg/s` command. Corrected liquid
imbalance therefore remained `98.960%`. Pressure drop/domain liquid inventory
continued upward to `18.0216 kPa`/`30.6899 kg`; continuity decreased to
`0.288247` but remained far above the `1e-3` residual gate. This confirms that
the controller is active once the band wets, but does not yet show numerical
mass closure or field stabilization.

By cumulative iteration 1600 (`R=1` iteration 600), the minimum-tau source had
reached only `7.87548 kg/s` (`6.736%` of command), with corrected liquid
imbalance still `93.264%`. Pressure drop/domain inventory continued increasing
to `22.5860 kPa`/`38.6312 kg`. Continuity was essentially flat/slightly worse
over iterations 1501-1600 (`+0.272%`) at `0.240295`, and the liquid-VF
residual worsened `5.076%` to `5.33466e-4`. This plateau/reversal evidence
shows that early residual improvement did not coincide with numerical mass
closure or stable physical monitors.

At cumulative iteration 2000 (`R=1` iteration 1000), the controller preserved
the separate `r1_iter1000_cumulative2000` case/data checkpoint. The achieved
sink was `20.19472 kg/s` (`17.272%` of command), corrected liquid imbalance
was `82.7277%`, and source-inclusive mixture imbalance was `48.6231%`.
Pressure drop/domain inventory reached `23.3447 kPa`/`47.6467 kg`.
Continuity and liquid-VF residuals ended at `0.187581`/`5.13866e-4`; the
residual histories were non-growing over the first complete 500-iteration
window, but continuity still failed its absolute `1e-3` gate. That window also
failed physical stability: pressure, sink and inventory drift were
`7.339%`, `97.927%` and `27.521%`; outlet/domain velocity and vorticity drift
were `2.157%`, `15.721%` and `13.989%`. Zero acceptance windows had passed,
so the controller continued toward its `R=1` iteration 2000 cap.

At cumulative iteration 2400 (`R=1` iteration 1400), the minimum-tau sink had
increased to `40.28520 kg/s` (`34.455%` of command), while corrected liquid
imbalance remained `65.5446%` and source-inclusive mixture imbalance
`38.5261%`. The active band held only `0.0805704 kg`; the implemented source
law would require `0.23384 kg` inside that same band to remove the full liquid
feed at `tau=0.002 s`. Pressure drop/domain inventory continued upward to
`24.7832 kPa`/`55.2498 kg`. Continuity ended at `0.206355`, and continuity and
liquid-VF residuals worsened `1.653%` and `5.175%` over the latest block. The
independent R1=900-1400 window also failed pressure/sink/inventory drift
(`8.253/72.179/19.097%`) and outlet/domain-velocity/vorticity drift
(`2.216/11.265/4.576%`). Only vapor throughput passed its physical-monitor
drift gate; zero complete acceptance windows have passed.

The reusable feedback calculation is also covered by the local sink unit-test
suite. It verifies `tau=M/target` dimensional behavior, empty-band selection
of the maximum tau, both clamp limits and invalid-input rejection. All eight
constant-water-level sink tests passed on 2026-08-10 NZST.

## Terminal qualification result

Setup 07e completed the guarded 1,000-iteration ramp and the full 2,000
full-strength iteration budget (`3,000` total solver iterations). The stop
reason was `maximum iteration budget reached`; zero acceptance windows passed.
The empirical controller therefore did not establish either numerical liquid
closure or an iteration-independent carrier field.

- At the terminal preserved full-strength state, the sink removed
  `50.954294 kg/s`, or `43.6%` of the `116.92 kg/s` liquid feed. Corrected
  liquid imbalance remained `56.419329%`, and source-inclusive mixture
  imbalance remained `33.1674%`.
- Domain and active-band liquid inventories were `65.007547 kg` and
  `0.101909 kg`. At the minimum `tau=0.002 s`, the implemented law requires
  `0.23384 kg` in the band to remove the full feed. The local source was
  therefore inventory/capacity limited even at its lower tau bound.
- Pressure drop reached `26.7252 kPa`. Over the final complete 500-iteration
  window, pressure, sink and domain-inventory drift were `5.8506%`,
  `26.1894%` and `13.3524%`; outlet and domain velocity drift were `3.3033%`
  and `6.9068%`. Vapor outlet flow and vorticity alone passed their drift
  limits.
- Continuity ended at `0.254617` and increased `3.634%` over iterations
  2901-3000. Phase-2 volume-fraction residual ended at `7.53207e-4` and
  increased `8.463%`. The absolute continuity and non-growing-residual gates
  both failed.
- Steam-outlet vapor/liquid flow was `81.11340/0.000225356 kg/s` out. The low
  carrier-liquid outlet value remains trend-only because the liquid balance is
  not closed and there is no resolved brine discharge.

Separate start, ramp-complete, R1=1000, R1=2000 and final ramp-reset-zero
case/data pairs are present. The final source ramp was reset to zero, DPM
interaction read back false, and no DPM injection update or tracking was run.

The result is classified `diagnostic/unresolved capacity-matched sink result`.
It is useful evidence that local sink tuning cannot replace outlet hydraulics,
but it is not an accepted constant-level model, a mesh-converged solution, or
a separator-performance result. Further local band/tau tuning is not
recommended. The next physically meaningful branch is a resolved brine pipe
qualified first on the 900k medium mesh.
