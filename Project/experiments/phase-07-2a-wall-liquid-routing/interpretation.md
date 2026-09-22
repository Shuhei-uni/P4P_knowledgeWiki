# Phase 7.2A — Interpretation

## Why this phase exists

Phase 7.2A starts only after Phase 7.1A produced a developed parent that was good enough to stop treating global solver development as the main research question.

The remaining dominant failure is physical routing: substantial phase-2 liquid still reaches steamoutlet even though the absorber, inventory behaviour, mass accounting, and continuity are much more usable than in earlier phases.

## Current physical hypothesis

The current hypothesis is that the model may be missing or under-representing the wall interaction that should help separated liquid remain near the outer wall, lose momentum, and move downward rather than being carried back toward the steam outlet.

Two interpretations are being tested separately:

1. Wall roughness: increased wall shear/momentum loss may change wall-adjacent liquid transport.
2. Eulerian Wall Film: explicit film attachment and drainage may represent a continuous wall-liquid structure that the bulk Mixture field alone does not capture adequately.

The first screen keeps these mechanisms separate so their effects can be attributed.

## Baseline inherited from Phase 7.1A

The authoritative parent is the run4 smooth-wall state at native report coordinate 5586.

Key baseline values are:

- total liquid mass: 295.8536 kg;
- absorber command/removal: 116.92 / 116.92 kg/s;
- phase-2 liquid through steamoutlet: -24.3344 kg/s in the stored Fluent sign convention;
- phase-1 vapor through steamoutlet: -80.2509 kg/s;
- continuity residual: 2.7841e-3;
- phase-2 volume-fraction residual: 5.4762e-4.

These are comparison coordinates, not validation targets.

## Initial experiment matrix

| Family | Controlled change | Main question | Evidence required |
| --- | --- | --- | --- |
| R | wall roughness only, EWF off | does extra wall shear reduce liquid carryover or move liquid downward? | steam-outlet phase flux, wall-adjacent liquid motion, inventory, closure, residual/event health |
| E | EWF only, roughness zero | does explicit bulk-to-film transfer and film drainage reduce bulk liquid carryover? | film mass/transfer/velocity, steam-outlet phase flux, inventory, closure, residual/event health |

No roughness-plus-EWF interaction is part of the first screen.

## How this phase should be judged

A lower scaled residual is not enough.

A useful 7.2A result must preserve what was valuable in the Phase-7.1A parent while improving liquid routing. The priority order is:

1. total-liquid inventory boundedness / late-window slope;
2. source-inclusive mass closure;
3. continuity behaviour;
4. phase-resolved routing, especially liquid through steamoutlet;
5. residual amplitude/trend and solver-event health;
6. mechanism-specific evidence showing why the routing changed.

A branch that simply removes more total liquid without an interpretable routing mechanism is not a success.

## Current status

This file is intentionally an active interpretation record. The phase has a well-defined parent and experiment question, but the roughness/EWF comparison results are not yet complete enough to write a phase conclusion.

The current scientific transition is: Phase 7.1A answered "can we obtain a usable developed state?" well enough to proceed. Phase 7.2A asks "can wall physics reduce the remaining liquid carryover without destroying that state?"

## TODO as results arrive

- TODO: add the R-family run matrix and matched late-window carryover values.
- TODO: add the EWF film-mass / transfer / film-velocity evidence.
- TODO: add one matched plot comparing baseline vs roughness vs EWF: steamoutlet liquid flux, total liquid inventory, and continuity.
- TODO: if neither mechanism helps, record that as a negative wall-mechanism result rather than automatically escalating model complexity.
