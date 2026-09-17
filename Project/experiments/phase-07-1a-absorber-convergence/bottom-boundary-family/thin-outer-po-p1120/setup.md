# P71A-BB-THIN-OUTER-PO-P1120

## Identity

| Field | Value |
| --- | --- |
| Family | Phase 7.1A bottom-boundary family |
| Role | prepared baseline / first localized bottom-pressure child |
| Source mesh | `purnanto-separator(bottomrings)-237k.msh.h5` |
| Cell count | `237,137` |
| Bottom delta | thin outer band is a pressure outlet; all other bottom bands are walls |
| Outer-ring gauge pressure | `1,120,000 Pa` |
| Absorber | retained: lower `y <= 0.10 m`, phase-2-only ramp from `0` to `-116.92 kg/s` |
| Run state | ramp baseline paired case/data save/reopen verified; never iterated |

## Boundary map

```text
bottom                                      wall
bottom-thin-inner-separator-purnanto        wall
bottom-thick-inner-separator-purnanto       wall
bottom-thick-outer-separator-purnanto       wall
bottom-bottom-band1-thin-outer-separator-purnanto
                                            pressure outlet, 1.120 MPa gauge
```

The outer pressure outlet has phase-2 backflow volume fraction `0`. This is a
backflow specification only; it does not constrain the phase composition of
outward flow and must not be described as a liquid-only outlet.

## Preserved baseline settings

The child retains the Phase 7.1A pressure-based steady Mixture model, vapor
and liquid materials, RNG k-epsilon closure, Phase 7.1A numerical settings,
liquid inlet (`116.92 kg/s` phase 2), steam inlet (`80.69 kg/s` phase 1), and
steam pressure outlet (`1.120 MPa` gauge). The lower cell zone is recreated on
the supplied mesh, so its volumetric source density is recalculated from that
mesh's measured `0.3212056375 m³` lower-zone volume. The readback source is
`-364.0035739 kg/(m³·s)` at full command.

## Cold-start absorber ramp

The family baseline begins with the absorber source set exactly to zero at
active iteration `0`. A subsequent authorized discovery runner must update the
uniform lower-zone phase-2 source every 10 active iterations according to:

```text
command(active) = 116.92 × min(active / 100, 1) kg/s
source density  = -command / measured lower-zone volume
```

Thus the full `-116.92 kg/s` command is reached at active iteration `100` and
held thereafter. Vapor/phase-1 source remains off throughout. This is the same
source-ramp strategy as the cold Phase 7.1A absorber reference, now applied to
the thin-outer bottom-boundary topology.

## Required run gate

Before any iteration, the selected run packet must add durable monitors for
the thin outer ring's mixture, vapor, and liquid mass flux; retain equivalent
steam-outlet and inlet fluxes; and record total/lower liquid inventory,
absorber source integral, residuals, continuity/imbalance, reverse-flow
events, and turbulent-viscosity limiting. The initial result remains a
finite-window boundary-routing diagnostic.
