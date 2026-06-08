# Separator Physics Basis Index

## Purpose
This directory stores reusable physics and assumption notes for separator CFD.

Use this layer when the question is:
- what physical behavior past researchers believe is dominant;
- what assumptions earlier separator papers made;
- what is still weakly evidenced or missing;
- which CFD model families are reasonable to test because of those assumptions.

Do not use this layer as a step-by-step setup guide. Setup instructions still belong in `wiki/setups/`.

## Files
- [separator-flow-physics](separator-flow-physics.md): core separator flow mechanisms such as swirl generation, centrifugal separation, core pressure depression, wall migration, and carryover.
- [droplets-carryover-and-re-entrainment](droplets-carryover-and-re-entrainment.md): inlet droplet assumptions, carryover pathways, wall-film behavior, and re-entrainment uncertainty.
- [separator-geometry-and-swirl-mechanisms](separator-geometry-and-swirl-mechanisms.md): how inlet shape, swirl strength, and separator geometry affect separation behavior.
- [governing-equations-and-modeling-levels](governing-equations-and-modeling-levels.md): high-level governing equations and what they imply for model-family choice.
- [operating-pressure-enthalpy-and-phase-split](operating-pressure-enthalpy-and-phase-split.md): thermodynamic framing for pressure, enthalpy, steam fraction, and inlet regime assumptions.
- [uncertainties-and-assumption-register](uncertainties-and-assumption-register.md): current uncertainty register and the sensitivity tests those uncertainties justify.

## Usage Rule
Start here before locking a CFD representation when:
- the inlet regime is uncertain;
- droplet behavior may control carryover;
- swirl or geometry tradeoffs are being interpreted;
- a setup assumption needs a physics-based justification;
- a more complex model family is being considered and needs to be justified.
