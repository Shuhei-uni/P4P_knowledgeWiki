# Full-geometry steady drain-resistance investigation — Andy

## Status and authority
Closed unqualified on 1 October2026 after both independent starts met the stopping predicate. No further solve is selected; unused budget is not continuation authority. [Closure](closure.md). Historical authorized envelope follows.

Andy authorized the recommended scope on 30 September 2026: “Run what you recommend.” This is a new investigation, not reopening Phase 9 or Phase 7b. No numerical phase label is assigned. Only Andy server1 is owned. Preserve all previous checkpoints; never use Shuhei sessions. The accepted standing-pool departure remains explicit; steady full geometry is retained.

## Evidence and hypothesis
The corrected single-liquid benchmark passed its four controls and execution guards, within 2000 repeat / 4000 combined diagnostic iterations. It verifies the simple vent implementation, not multiphase drainage. Phase 9 remained unqualified after N2000 with inventory depletion and failed conservation/routing/residuals. These observations do not establish that absent external resistance caused failure.
Question: can one fixed passive drain resistance support a conservative stationary pool with the same full feed and external reservoir assumption? Hypothesis: resistance changes the hydraulic response enough to permit balanced discharge without progressive pool loss. K=9 is an idealized predeclared mechanism test, not a fitted or measured valve law.

## Envelope
Retain existing 620431-cell full geometry, materials, feed, gravity, RNG turbulence, steady implicit VOF, operating-density convention, downstream head +0.10 m, and automatic pseudo-time scale 0.1. Change only brine pressure outlet to outlet vent with K=9 and the same spatial ambient-pressure expression and liquid backflow fraction. No CAD change, transient, feedback controller, sink, coefficient sweep or numerical tuning.
Use independent fresh +0.10 and +0.30 m starts. Existing N0 setup is a reproducible configuration reference; freshly initialize and prove fields, never inherit an unconverged flow endpoint. No one-way or liquid-selective valve is implied.

## Decision conditions
First selected block is +0.10 m, N0–1000, then evidence review. Up to 2000 discovery iterations per start and 1000 save/reopen persistence per candidate: 6000 total or 14 solver wall-hours including retries. All solves count; no blind extension. Both starts and persistence must meet simultaneous setup gates before qualification. Stop sustained inventory depletion plus major closure/routing failures at the first gate; a failed low start may justify testing the predeclared independent high start, but cannot qualify the two-start hypothesis. Consequential continuation decisions belong to the scientific planner; routine implementation repair stays inside scope. Human pause overrides all authority.

A favorable result supports only numerical feasibility of this coarse-grid idealized drainage model. No plant calibration, mesh independence, dynamic stability or fine-droplet validity is claimed. Negative evidence rejects this fixed K/head setup within the budget, not every steady separator. See setup.md and phase-state.yaml.
