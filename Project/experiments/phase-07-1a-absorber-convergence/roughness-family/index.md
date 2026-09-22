# Phase 7.1A — Family R: wall roughness

## Status and assignment

**Human-selected discovery family — 2026-09-22.** Run this family on
**Server 1**, independently from the EWF stream on Server 3. The [shared v2
mechanism-screen contract](../v2-mechanism-family-screen/index.md) owns the
parent, ramp, frozen scaffold, and common evidence requirements.

No child is executed merely because this planning record exists.

## Family question

> Does increasing wall roughness, with EWF off, increase wall shear enough to
> change the direction and removal of separated liquid near the outer wall?

The physical mechanism under test is bulk near-wall momentum loss. EWF remains
off so a result can be attributed to roughness rather than conversion into an
explicit wall-attached film.

## Case matrix

All rows use the same v2 parent, the common first-2,000-iteration inlet ramp,
`C_s = 0.5` when roughness is active, and `EWF = off`.

| Case | EWF | `k_s` (m) | Purpose | Status |
| --- | --- | ---: | --- | --- |
| `C0` / `R0` | off | `0` | Shared smooth-wall, no-EWF control | selected control |
| `R1` | off | `5e-5` | Realistic clean-steel baseline | selected |
| `R2` | off | `2e-4` | Moderate roughness diagnostic | selected |
| `R3` | off | `5e-4` | Strong roughness diagnostic | selected |
| `R4` | off | `1e-3` | Aggressive diagnostic if R1–R3 are monotonic but weak | optional, not first queue |

The smooth R0 control endpoint was also continued under the separately
audited Coupled / Global-Time-Step numerical treatment. That run is recorded
in [r0-smooth-control/](r0-smooth-control/) as a solver-endurance control,
not as a roughness result. The terminal second 1000-iteration window is the
declared comparison control; R1–R3 remain unrun in this record.

The roughness setting must be applied only to the intended wall surfaces and
must be read back before solving. The mesh itself is not modified. The Fluent
roughness implementation and wall-zone scope are an execution preflight gate;
if the requested `k_s`/`C_s` controls are not available as a clean wall-only
delta, stop the child as a capability block rather than changing another
physics model to emulate roughness.

## Required interpretation

Track the same phase/source and balance evidence as the shared contract, with
additional emphasis on:

- outer-wall mean liquid vertical velocity, with upward/downward sign fixed in
  the setup record;
- lower-vessel liquid inventory and its late-window slope;
- liquid discharge through the v2 absorber;
- any liquid carryover through `steamoutlet`; and
- steam leakage through any bottom region, which should remain closed under
  this family.

The most informative trend is a systematic response of near-wall liquid
velocity and routing as `k_s` increases. A flat R0–R3 response is itself a
useful negative result: it reduces confidence that missing wall shear is the
dominant mechanism. R4 is not required to make that conclusion unless the
first three points show a credible but unresolved trend.

## Rejection and claim limits

Reject a comparison if roughness is not the only changed physical setting, if
the server-local parent does not match the v2 baseline, or if the wall change
creates an untracked outlet/film/sink path. A roughness response does not
establish physical wall-scale validity or plant drainage performance.
