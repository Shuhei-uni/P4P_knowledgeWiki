# P71A-T2-RNG-SWIRL-OFF setup draft

| Field | Value |
| --- | --- |
| Status | PLANNING_DRAFT_NOT_EXECUTABLE |
| Lifecycle role | Discovery RNG-option sensitivity |
| Phase context | [Phase 7.1A CONTEXT](../../CONTEXT.md) |
| Baseline | [Active Fluent baseline](../../baseline-setup-record.md) |
| Parent identity | P7-E5-CZ-ABSORB-COLD-RAMP11692 active-1000 pair; see [parent reference](../parent-reference.md) |
| Novelty | NEW RNG-option sensitivity |
| Controlled delta | RNG swirl modification on to off |
| Run authorization | None |

## Question

Is the current RNG swirl modification over- or under-correcting turbulent
viscosity in the separator's rotating and recirculating flow?

## Controlled change

Keep RNG k-epsilon, differential viscosity, standard wall functions, all
non-turbulence settings, and the lower absorber unchanged. Disable only the
RNG swirl-dominated-flow option and read back the closure state.

This is a diagnostic sensitivity. It must not be treated as more physically
credible simply because it is numerically calmer. Planned horizon: 500 native
iterations after smoke, using the verified T0 parent and the shared contract in
the [family README](../README.md).

## Decision boundary

Compare turbulent-viscosity behaviour, phase separation, lower-zone delivery,
and outlet routing together.
