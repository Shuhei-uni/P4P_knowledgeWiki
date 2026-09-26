# E2.83 — fixed EWF timestep 1.50e-5 s

## Question

Does a 50% increase over E2.7's fixed film timestep accelerate film-time
advancement while retaining a bounded EWF response over 3,000 steady
iterations?

## Parent and controlled delta

Independent child from the verified Phase 7.2A R0 native-5586 parent recorded
in `../../baseline-control-handoff.md` (case SHA-256
`4fd493972839929f1f0922ad42679456d1f4aea294da86e4b13d6b7c32f754fc`; data
SHA-256 `b2261fac8626b2e338c3a9c80c334c8a910d1bfb536f782ef9234623f00e1a72`).
The sole active numerical change from E2.7 is fixed EWF timestep
`1.50e-5 s`, up from `1e-5 s`.

Keep adaptive stepping OFF; EWF Coupled Solution ON; film-wall Flow Momentum
Coupling OFF; Phase Accretion ON; first-order implicit film scheme; 10 maximum
film sub-iterations; residual stop `1e-5`; Courant setting `0.05` (inactive in
fixed mode); zero roughness; film wall `wall`; no film wall on `bottom`; and
the exploratory `0.3 m` maximum thickness limit. Keep the verified mesh, flow,
absorber, material, discretization, and boundary settings unchanged.

## Run and evidence

Run 3,000 native steady iterations to native 8586. Checkpoint paired local
case/data every 250 iterations. Record native flow and EWF histories at every
iteration, including film mass, maximum and area-weighted thickness, film
Courant, film speeds, phase accretion, outlet fluxes, absorber tracking,
closure, and solver events. Include a one-iteration report-write smoke as the
first update in the requested horizon. Compare at matched native coordinates
and at native 8586 against E2.7, and compare film-time advancement separately.

## Decision and limits

The candidate supports a faster numerical buildup only if film time advances
faster than E2.7 while thickness, velocity, EWF residuals, flow behaviour, and
mass accounting remain interpretable through the full horizon. Run completion
or bounded endpoint values alone do not establish stationary film transport,
drainage, closure, or physical carryover benefit.
