# E2.81 — slightly tightened aggressive adaptive EWF

## Question

Can a small tightening of E2.8's adaptive controls retain its fast film-time
advance while avoiding the nonphysical branch that appeared near native 7195,
and complete 3,000 additional iterations from the common native-5586 parent?
The target is an E2.7-like developed film at a lower iteration count. This is
an exploratory numerical comparison, not a claim of steady convergence.

## Parent and controlled change

E2.81 is an independent child of the verified Phase 7.2A R0 pair at native
5586, with the same parent identity as E2.7 and E2.8. Case SHA-256 is
`4fd493972839929f1f0922ad42679456d1f4aea294da86e4b13d6b7c32f754fc`; data
SHA-256 is `b2261fac8626b2e338c3a9c80c334c8a910d1bfb536f782ef9234623f00e1a72`.

| Control | E2.8 | E2.81 |
| --- | ---: | ---: |
| Time scheme | First-order implicit | First-order implicit |
| Adaptive film stepping | On | On |
| Maximum film Courant | 0.5 | **0.4** |
| Initial film timestep | 1e-4 s | 1e-4 s |
| Timestep increase factor | 2.0 | **1.5** |
| Timestep decrease factor | 2.0 | 2.0 |
| Film sub-iterations | 3 | **4** |
| Sub-iteration stop | 1e-3 | **5e-4** |
| EWF Coupled Solution | On | On |
| Film-wall Flow Momentum Coupling | Off | Off |
| Phase Accretion | On | On |
| Maximum film thickness | 0.3 m | 0.3 m |

The four bold values are small changes to the E2.8 fast-time package. All
other phase-accretion setup choices follow E2.8: film wall `wall`, zero
roughness, no DPM interaction, and no EWF film wall on `bottom`. The stored
fixed timestep remains 1e-5 s and is inactive while adaptive stepping is on.
Because multiple numerical controls change together, this run cannot isolate
the cause of any difference.

## Run and instrumentation

Run 3,000 additional iterations to native 8586. Use Fluent 2025 R2 directly,
with a fresh load of the exact parent. Save paired local checkpoints every
250 iterations and copy only named start/final pairs to OneDrive. The solve is
staged through native 7196 for a live review immediately before the E2.8
divergence window, then continues with bounded batches. The stage is an
observation point, not a planned reduction in the 3,000-iteration horizon.

Retain the E2.8 instrumentation at every native iteration: 37 report
histories covering inherited flow/absorber/outlet/closure signals and EWF
film mass, thickness, Courant, outflow, accretion/collection, velocity,
pressure, Weber/stripping indicators, and Film Coverage. Also record residual
history, solver transcript/events, adaptive film time step, and EWF solution
state at each solve batch. DPM-to-film source mass, stripped mass, and
separated mass remain unavailable as Fluent 2025 R2 surface-report fields in
this case.

Reconstruct wall area by thickness from saved `wall` film-height fields at
named endpoints and paired 250-iteration checkpoints. Retain cumulative area
at or above 0.01, 0.05, 0.10, 0.25, and 0.50 mm, plus disjoint thickness
bands. Keep reconstructed threshold areas separate from Fluent's native Film
Coverage integral. Verify the reconstructed total against the native wall
area of 53.4369522992766 m².

## Interpretation limits

Compare E2.81 with E2.7 and E2.8 at matched additional-iteration coordinates
and by film physical time. Track whether the E2.7-like mass, thickness,
velocity, and wet-area state appears before the 3,000-iteration endpoint.
Any nonfinite or clearly nonphysical state is a branch failure; preserve the
last valid pair and record actual solver work separately from the selected
trajectory. Finite residuals and bounded film fields alone do not establish
steady film convergence, source-inclusive closure, drainage, or physical
carryover benefit.
