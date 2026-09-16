# E6 outer-ring pressure outlet — P1160

## Setup identity

- **Setup ID:** `P7-E6-RING-OUTER-PO-P1160`
- **Candidate:** `E6-RING-PO`
- **Role:** discovery child, outermost radial band pressure outlet
- **Status:** `DESIGN_READY_NOT_PLACED`
- **Controlled pressure:** `1.160 MPa` gauge on `p7-bottom-ring-r05-outer`
- **Discovery horizon:** 500 steady iterations after the mandatory 50-iteration smoke
- **Parent:** the same verified E0 initialized parent and ringed mesh as P1120

## Boundary topology

The five-zone mesh catalogue must pass first. Keep R01–R04 as walls and
convert only `p7-bottom-ring-r05-outer` to `pressure-outlet`.

## Boundary-condition sequence

Prove the ring zones and all unselected wall types, set the mixture backflow
state first, set the R05 gauge pressure to `1,160,000 Pa` last, and prove the
requested state before save and after reopen. Run the 50-iteration smoke gate
before the 500-iteration discovery horizon. The corrected full-bottom E1 P1160
case failed smoke, so this child is a failure-boundary probe, not an assumed
stable operating point.

## Evidence and claim limit

Record per-ring total/liquid/vapor flux, reverse flow, pressure and velocity at
the wall/outlet junction, liquid inventories, phase-resolved closure,
residuals, warnings, and turbulent-viscosity limiting. A result is a
localized pressure-routing diagnostic, not a liquid-selective or physical
bottom-pressure result.
