# Phase Context — Phase 7b Full-Geometry Steady Liquid Removal

## Status

- **Planning state:** phase framing
- **Owner:** Andy; separate from Shuhei's Phase 7
- **Last human review:** 2026-09-08
- **Experiment-selection authority:** human-approved-context-only
- **Current decision:** retain the full geometry and investigate a function-based
  liquid-removal zone as an ideal collector in a strictly steady-state model.
  A standing brine pool is not required. The mechanism direction is selected;
  the exact screening experiment and decision gate remain to be defined.

## Human thinking

### Current intent

The human considers the explicit brine-pool/outlet work too complicated and
does not want a transient model. The selected alternative retains the full
vessel geometry, including its lower brine region, but uses a function to
remove liquid entering a designated zone. The human explicitly selected an
ideal collector with no requirement to preserve a standing pool.

Phase 7b is Andy's separate full-geometry investigation. Shuhei's
[Phase 7](../phase-07-simplified-purnanto-liquid-removal/CONTEXT.md) continues
to own the simplified, truncated Purnanto direction. Neither phase supersedes
the other. Phase 06 remains concluded with its historical evidence intact.

### Ideas raised by the human

| ID | Human idea | Why it seems worth considering | Status |
| --- | --- | --- | --- |
| H1 | Keep the full geometry and replace reliance on the physical brine outlet with a function that removes liquid entering a defined zone. | Seek steady liquid removal while simplifying the pool/outlet representation. | Selected mechanism direction; screen not yet specified |

### Constraints expressed by the human

- Keep the full geometry, including the lower brine region.
- Use steady state; switching to a physical transient formulation is outside
  the selected scope.
- Treat the removal region as an ideal collector; preserving or regulating a
  standing brine pool is not required.
- Target liquid water for removal. Zone location, extent, and removal law are
  not yet selected.

## Evidence anchors

- **Observed in preserved notes:** the earlier
  [closed-bottom sink studies](../parallel-andy-studies/closed-bottom-liquid-sinks.md)
  already tested steady liquid-only sinks. None established an accepted
  stability window. The completed first 07f matrix case retained 54.5553%
  corrected liquid imbalance; in 07e, available liquid in the band limited
  removal despite the minimum removal time scale. These used a different,
  closed-bottom mesh and do not determine the proposed full-geometry result.
- **Observed in preserved notes:** the separate
  [resolved brine-outlet studies](../parallel-andy-studies/resolved-brine-outlet.md)
  moved from Mixture to transient VOF. Brief drainage at very low feed did not
  persist; later 07n holds failed the sustained balance gate. This is the
  relevant transient predecessor, distinct from the F11 Phase-06 lane.
- **Observed:** [Phase-06 Stage-06](../phase-06-full-geometry-with-brine-pool/stage-06-long-horizon-surrogate-hypothesis/results.md)
  remained steady Mixture/RNG. Its final-window phase-liquid net rate averaged
  +16.10 kg/s after pressure saturation, and it did not establish a controlled
  numerical pool state. Residual-convergence evidence was unavailable.
- **Inferred:** whether liquid reaches the removal zone is a central
  uncertainty. Stronger removal alone did not qualify the historical small
  bottom-band approach. Changing zone coverage may help, but could also change
  separation above it; neither outcome is established.
- **Missing Info:** exact full-geometry mesh/parent identity, zone coordinates
  and extent, treatment of the former brine outlet, phase formulation, source
  accounting and coupling, screening horizon, and acceptance thresholds.

## Phase contract

### Phase question

> Can a function-based ideal liquid collector in a defined lower region of the
> full separator geometry remove separated water and support a balanced,
> numerically stable steady-state solution while preserving useful separation
> behaviour above the collector?

### Scope, invariants, and claim limit

- **In scope:** the human-selected liquid-removal zone and its effect on
  liquid routing, inventory, steam loss, conservation, and separator flow.
- **Must remain fixed:** full-geometry scope, steady-state formulation, and
  no requirement to preserve a standing brine pool.
- **Out of scope:** physical pool-level control, transient pool/interface
  dynamics, and validation of actual outlet hardware or downstream hydraulics.
- **Claim limit:** success would establish a computational liquid collector.
  It would not validate a physical brine pool or separator efficiency by itself.
- **Planning distinction:** retaining lower-vessel geometry does not imply
  retaining a physically representative liquid pool in that geometry.

### Useful evidence standard

A useful result must distinguish liquid reaching the collector from liquid
actually removed, account for the integrated sink exactly once in the liquid
and total mass balances, and retain steam-outlet phase fluxes, liquid inventory,
pressure/velocity behaviour, and residual histories. Removal coefficient and
zone extent must be explicit. Numerical thresholds and a screening horizon
remain to be proposed before a runnable experiment is selected.

## Candidate experiment pool

| ID | Origin | Controlled delta | Screening question | Required evidence | Artifact/rejection signal | Human status |
| --- | --- | --- | --- | --- | --- | --- |
| E1 | H1 — human idea | Function-based liquid-only removal in a defined lower full-geometry region; exact zone, law, parent and outlet treatment pending. | Does liquid reach the collector and leave through the accounted sink sufficiently to establish a useful steady solution? | Transport into the region, integrated removal, phase and total closure, inventories, steam carryover/loss, pressure/velocity and residual histories. | Persistent imbalance/drift, insufficient liquid delivery, wrong-phase removal, or material distortion of separation above the collector. | Mechanism selected; concrete experiment proposed, not yet approved |

## Approved screening campaign

No screening campaign is approved. First define the collector region and exact
reference, then specify an interpretable screen of E1. Historical failed sink
cases are comparison evidence, not an automatically approved repeat campaign.

## Decision gates

No execution or qualification gate is approved. The evidence standard above
does not itself authorize a solver run.

## Conditional qualification paths

No qualification path is approved.

## Human locks and handoff rules

- Do not restore a standing-pool requirement or switch to transient modelling
  without a new human direction.
- Do not assume the F11 full geometry and the separate 620,431-cell resolved
  outlet mesh are interchangeable. Identify the selected parent explicitly.
- Do not invent a physical pool level to place the collector. Any chosen
  numerical placement must be labelled as such.
- `scientific-phase-loop` may execute only approved context items and declared
  gates. The present selection authorizes framing of H1, not an unspecified run.
