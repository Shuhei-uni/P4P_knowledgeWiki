# Phase 06 — Conclusion

## Decision date and status

**Human-directed conclusion as of 2026-09-08.** Phase 06 is concluded for
now. This decision supersedes the unfinished autonomous lifecycle actions in
`phase-state.yaml`; that file is retained as a record of the evidence and gate
state reached before the human changed the project direction.

## Final conclusion for now

The full separator geometry is too complex to remain the immediate
model-development platform. The Phase-06 work did not establish a sufficiently
credible and manageable full-geometry route for representing the bottom brine
pool and its liquid-removal behaviour. Continuing to add control surrogates
and other complexity to that model is not the selected next step.

This is a project-direction conclusion about the usefulness of the current CFD
model, not evidence that the physical separator is inherently uncontrollable
or that a full-geometry model can never work.

## Geometry decision

The project will return to the simplified Purnanto geometry. The geometry will
be truncated at the elevation corresponding to the brine-pool surface in the
real separator. The truncation plane will therefore form the bottom of the
simplified computational geometry; the detailed geometry below the real pool
surface will not be modelled in the next phase.

The exact cut elevation and its translation into the Purnanto coordinate
system remain to be documented and verified before a runnable child setup is
created.

## Handoff to Phase 07

Phase 07 will investigate ways to remove separated liquid from the bottom of
the truncated Purnanto separator model. This is intentionally an exploratory
development phase. It may require several pragmatic or deliberately “hacky”
numerical methods before a useful liquid-removal mechanism is found.

Candidate methods have not yet been selected. Each method must declare what it
changes, how liquid is removed, what numerical or physical artefacts it may
introduce, and what evidence would justify retaining or rejecting it. Success
in Phase 07 would establish a useful modelling mechanism; it would not by
itself validate the mechanism as a faithful representation of the real brine
pool, outlet hardware, or controller.

- [Phase 07 — simplified Purnanto liquid-removal mechanisms](../phase-07-simplified-purnanto-liquid-removal/index.md)
