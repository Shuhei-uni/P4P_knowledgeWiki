# E4 — direct EWF film feed attempt with fast adaptive stepping

## Question

Starting from the verified Phase 7.2A native-5586 baseline, can the full
`116.92 kg/s` liquid feed be placed directly into an EWF wall boundary at the
liquid-port junction, while aggressive adaptive settings advance film time
quickly enough for a useful exploratory screen?

This is a new inlet-treatment branch, not a continuation of E2.7 and not a
matched comparison that isolates one numerical control. E2.7 established a
numerically stable but still-growing film under phase accretion. The E4 run
below did not test the direct EWF boundary condition: implementation fell
back to the User Source Terms on the initial-condition tab. Treat E4 as a
failed setup/solver screen, not evidence for or against direct film injection.

## Parent and geometry

Use the exact verified native-5586 Phase 7.2A baseline pair from
[`baseline-control-handoff.md`](../../baseline-control-handoff.md): case SHA-256
`4fd493972839929f1f0922ad42679456d1f4aea294da86e4b13d6b7c32f754fc`; data
SHA-256 `b2261fac8626b2e338c3a9c80c334c8a910d1bfb536f782ef9234623f00e1a72`.
The baseline remains untouched.

The live mesh has 60,964 cells. The inlet face `liquidinlet` is perpendicular
to +X, while the adjacent outer wall lies along the inlet stream. A hexahedral
cell register around the wall strip selected 1,098 cells; Fluent split 125
faces from `wall` into `e4_direct_film_inlet`. The source patch area is
`0.0033103625755757093 m²`; the remaining `wall` has 3,338 faces. This is a
boundary-zone split only; the cell count and geometry are unchanged. The new
patch roughness is explicitly set to the parent `wall` value (`k_s=0`,
`C_s=0.5`).

## Direct film feed

The parent phase-2 inlet readback gives `116.92 kg/s`, density
`881.210876 kg/m³`, and uniform +X speed `27.133606 m/s`. The localized EWF
patch therefore receives:

| Input | Value |
| --- | ---: |
| Film mass rate | `116.92 kg/s` |
| Film mass flux | `35,319.393973 kg/(m²·s)` |
| X momentum flux | `958,342.519914 N/m²` |
| Y/Z momentum flux | `0` |

The integrated mass and momentum fluxes match the original liquid inlet
(`116.92 kg/s`, approximately `3,172.76 N`). The liquidinlet phase-2 mass-flow
rate is set to zero. The steam inlet remains phase-1 only (`80.69 kg/s`);
phase-2 flow there remains zero.

The intended mechanism is the EWF **Boundary Condition** type with Film Mass
Flux and X/Y/Z film momentum flux applied only on this localized inlet strip
([Fluent EWF boundary, initial, and source-term conditions](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/flu_ug_ewf_sec_bound.html)).
The executed build instead used `film-wall-initial` and the User Source Terms
panel because the generated PyFluent API path used for the build did not
expose the Boundary Condition flux field. The neighbouring `wall` stayed a
Boundary Condition film wall. Flow Momentum Coupling, phase accretion, DPM
film coupling, and film/VOF coupling were OFF. This API/TUI gap must be closed
and the saved case read back before a direct-film hypothesis test is run.

The inherited absorber is defined from phase-2 bulk inlet throughput. This
branch incorrectly rebound `P71V2Command` to the direct-film feed even though
that feed bypasses the bulk phase-2 inlet and absorber control volume. The
monitors show a `116.92 kg/s` command but only `6.94 kg/s` removal and about
`-109.98 kg/s` command error at native 5870. A corrected direct-film design
must set the bulk absorber command/source to zero and measure film delivery
and drainage separately; the inherited absorber must not target film feed.

## EWF controls

The requested fast-time controls were set: first-order implicit; adaptive
stepping ON; maximum Courant `0.5`; initial film step `1e-4 s`; increase and
decrease factors `2.0`; three film sub-iterations; stop residual `1e-3`; EWF
Coupled Solution ON; Flow Momentum Coupling OFF; maximum step `0.01 s`; and
the existing `0.3 m` thickness cap. These controls round-tripped in the saved
start pair. Phase accretion was OFF for this direct-feed branch. Pressure
gradient was also OFF in the executed case, although the referenced direct-
film proposal called for it ON; correct that in a retry. Gravity, momentum,
and gas-shear driving were ON.

The `underrelax-film-height` option was not applied: Fluent documents it under
DPM numerics for the Lagrangian Wall Film model, not the Eulerian Wall Film
time-advancement controls.

## Run and evidence

Start pair: native 5586, case SHA-256
`B52093419A8E39D222E637134D54F5CAAD270407C97D626E1F0E620F918D8863`, data
SHA-256 `E815584C363C24268C4D278C3677192EA624A0DFA6B8B6613D808D80321D6A91`.
The requested 1,000-iteration batch was stopped after 285 iterations because
maximum thickness reached its cap and film velocity/CFL had diverged. Last
monitor row: native 5870; last native coordinate at stop: 5871; 285 iterations
completed from the parent. Adaptive stepping advanced film elapsed time only
to `2e-4 s`, then collapsed to sub-picosecond steps. Maximum CFL reported at
startup exceeded `6.6e3`; maximum thickness reached `0.300000012 m`; maximum
film velocity reached `5.486e10 m/s`. At the last monitor row, film mass was
`13.948 kg`, cumulative outflow `69.009 kg`, total-liquid report `128.110 kg`,
phase-2 steamoutlet outflow `11.657 kg/s`, and absorber command error
`-109.976 kg/s`. These are divergence and bookkeeping-failure signals, not
physical response measurements. The result does not test the proposed native
film boundary flux.

The only paired autosave is at native 5750 (offset 164): case SHA-256
`FBC2B27F64F484839C6BDBD791AAF23DA13532865AD281A0C61C23CD8DF8BF99`, data
SHA-256 `418E3C7B0720637D2895460660C56E09D552F914CE252BA2F7A0A7E334583A7A`.
The closed-session transcript is copied to the output folder and SHA-256 is
`5372BB6232858228CD96B4DEDD252904F9381DDCB1D8512496704940AF992D07`.
No Fluent session remains open.

The local run root is
`C:\Users\Shuhei Yokkaichi\Documents\FluentRuns\Phase72A\FamilyE\E4-direct-film-fast-20260925T104504Z`;
the machine-readable receipt and monitor histories are under
`PyAnsys/output/phase72a_ewf_e4_direct_film_fast_20260925T104504Z/`.

Next implementation attempt: expose/set the EWF wall Boundary Condition flux
fields, set absorber source/command to zero for the bulk phase-2 pathway, turn
pressure-gradient driving ON, then save/reopen and verify the exact fields
before another solve. A useful run should first confirm finite thickness,
film velocity, Courant and mass accounting before spending a 1,000-iteration
screen. Compare with E2.7 only as a different inlet-treatment branch.
