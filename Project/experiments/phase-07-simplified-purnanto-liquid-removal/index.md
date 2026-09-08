# Phase 07 — Simplified Purnanto Liquid-Removal Mechanisms

## Status

**Selected by the human on 2026-09-08; E0 is approved for experiment design.**
The reference mesh and 08b parent candidate are supplied. E0 will keep the
bottom as a wall and establish the corrected reference behaviour over an
initial `2,000`-iteration discovery horizon. No liquid-removal treatment is
approved yet.

The current human-approved planning state is maintained in
[`CONTEXT.md`](CONTEXT.md). It must record an approved candidate and decision
gate before an experiment is designed or executed.

The first approved planning action is a detailed structural and later live
Fluent inspection of the supplied mesh. See the
[current mesh inspection](mesh-inspection.md).

The supplied parent candidate is
`/Users/shuheiyokkaichi/Library/CloudStorage/OneDrive-TheUniversityofAuckland/P4P-Fluent-Artifacts/TwoPhaseInletV2(Purnanto).cas.h5`
with SHA-256
`b75a69dcad7da29fa9576c15d478a187798029b51d45ac773a265ecdf146ae56`.
It must still be proven as 08b by Fluent settings readback.

The human-approved E0 server-neutral packet is now available:

- [experiment design](e0-08b-corrected-reference/design.md)
- [setup contract](e0-08b-corrected-reference/setup.md)
- [results placeholder](e0-08b-corrected-reference/results.md)
- [unassigned run paths](e0-08b-corrected-reference/run-paths.yaml)

G0 authorizes these records only. No Fluent execution is authorized until the
requested treatment series is defined and the later G1/loop-entry gates pass.

The complete human-approved fixed-mesh series is now defined and compiled:

- [campaign design and evidence contract](fixed-mesh-treatment-screen/design.md)
- [15-case setup-series index](fixed-mesh-treatment-screen/index.md)

The independent G1 design review passed for server-neutral setup creation.
Execution, fleet/session takeover, conditional fourth points, continuations,
and qualification remain separately unauthorized.

## Phase question

> What practical numerical mechanism can remove separated liquid from the
> bottom of the truncated Purnanto separator model while preserving a useful
> and interpretable representation of the separation behaviour?

## Geometry boundary

Phase 07 returns to the simplified Purnanto geometry rather than continuing
with the full separator geometry. The computational geometry will be cut at
the elevation corresponding to the brine-pool surface in the real separator.
That cut plane becomes the bottom boundary of the simplified model, and the
detailed real-separator geometry below the pool surface is excluded.

**Human-confirmed.** The supplied `Separator-purnanto342k.msh.h5` already
contains this cutoff, and all geometry in the mesh is intended. Apart from the
new bottom cutoff, its geometry is unchanged from original Purnanto. The
steam-outlet diameter is `0.876 m`, correcting the former Project value of
`0.724 m`; the measured mesh area gives `0.875936 m`.

**Observed artifact identity.** The selected mesh is available at
`/Users/shuheiyokkaichi/Library/CloudStorage/OneDrive-TheUniversityofAuckland/2026 Sem 1/700/P4PCFD/CAD PurnantoV2/Separator-purnanto342k.msh.h5`
with SHA-256
`59b7cf3bcf1cf0266587d4b98f8c6d67bbca007a4381ceb16a05fd8728b37801`.
Its internal topology and boundary-zone identity have been inspected locally;
solver-side Fluent mesh quality and setting reconciliation remain outstanding.

## Exploration direction

The phase will use human think-aloud and `phase-grill` to identify candidate
ways of removing liquid through or near the bottom of the simplified separator.
Only candidates recorded as approved in `CONTEXT.md` may be tested. Pragmatic
and deliberately “hacky” methods are permitted because the immediate purpose
is mechanism discovery. No candidate is assumed to be physically faithful
merely because it runs or drains liquid.

For every candidate, the project should record:

- the boundary condition, model feature, source/sink treatment, or other
  numerical intervention used;
- the intended liquid-removal mechanism and why it might work;
- whether it also removes steam or otherwise distorts phase routing;
- its effect on liquid inventory, phase-resolved mass balance, separator flow,
  and numerical behaviour;
- known artefacts, failure modes, tuning parameters, and claim limits; and
- the evidence-based decision to retain, revise, or reject it.

The initial useful target is either a trend toward credible mass closure or a
material reduction in the liquid-inventory buildup rate relative to a matched
reference. A candidate is not useful if it achieves drainage through
disastrous steam loss.

## Initial claim boundary

Phase 07 is a modelling-method development phase. Its first useful result may
be a robust numerical workaround rather than a plant-faithful outlet model.
Until separately supported, a successful method may be described only as a
mechanism for removing liquid from the simplified computational separator. It
must not be presented as validation of the real brine-pool interface, outlet
hardware, drainage rate, or level-control response.

## Predecessor decision

- [Phase 06 conclusion](../phase-06-full-geometry-with-brine-pool/conclusion.md)
