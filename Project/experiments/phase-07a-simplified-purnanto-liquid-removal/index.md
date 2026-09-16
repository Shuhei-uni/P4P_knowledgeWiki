# Phase 07A — Simplified Purnanto Liquid-Removal Mechanisms

## Status

**Human-reframed on 2026-09-11.** This record preserves the Phase 07
mechanism-discovery campaign and its evidence. The reference mesh and exact
08b parent were
verified. An initial 2,000-iteration run was invalidated because two parent
RNG options were not preserved. A repaired, save/reopen-proven run preserved
those options but diverged with an epsilon AMG failure and floating-point
exception at native iteration 1,724. The latest corrected rerun reached all
2,000 iterations, emitted the required histories and checkpoints, and passed
final save/reopen readback. E0 now supplies the valid execution reference
needed for fixed-mesh analysis, but not a physical or qualification result.

The historical planning state is maintained in [`CONTEXT.md`](CONTEXT.md).
The lower cell-zone, phase-2-only absorber is now the preferred working
mechanism, while the new convergence question is maintained in
[Phase 7.1A](../phase-07-1a-absorber-convergence/). This record does not claim
physical qualification or steady convergence.

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
- [execution results and blocker](e0-08b-corrected-reference/results.md)
- [resolved run paths](e0-08b-corrected-reference/run-paths.yaml)

The human subsequently authorized loop entry and available-server takeover.
E0 was executed under that authority. Its latest run passes the declared E0
execution requirements; `DISCOVERY_EXECUTION` remains BLOCK because the three
original fixed-mesh E5-PSINK packets could not satisfy their declared
region-specific source-accounting contract. The separately approved E5-CZ
cell-zone recovery family has since completed its G025, recovered G050, and
fresh G100 discovery screens; those records do not reopen the blocked
fixed-mesh packets or the qualification path.

The complete human-approved fixed-mesh series is now defined, compiled, and
has been attempted under the subsequent explicit human authorization for
dependency-gated execution. E0, E1 P1120, E2, E3, and E4 have complete
plot-led execution/analysis packets. Corrected E1 P1160/P1200 attempts prove
the requested pressure readback but block during smoke with Fluent
divergence/floating-point exceptions. The original fixed-mesh E5-PSINK family
reached its live region/source capability probe for all three gains and was
blocked before solving because Fluent exposed no region-specific source
binding. A separately approved E5-CZ cell-zone family then recovered the
mechanism through native zone separation and completed all three gain screens.
These child artifacts are paired with a valid E0 execution reference, but the
finite-horizon screens do not authorize qualification; the fixed-mesh E5-PSINK
branch remains at its capability boundary and E5-CZ remains discovery-only.

The series records are:

- [campaign design and evidence contract](fixed-mesh-treatment-screen/design.md)
- [15-case setup-series index](fixed-mesh-treatment-screen/index.md)
- [Q146.15 conditional fourth-branch results](fixed-mesh-treatment-screen/e3-mfo-q14615/results.md)
- [G1.50 conditional fourth-branch results](fixed-mesh-treatment-screen/e4-adapt-g150/results.md)

The independent G1 design review passed for the approved server-neutral series.
The two conditionally activated fourth branches are now execution-complete and
analyzed on student: Q146.15 retains positive inventory drift/open mixture
balance, and G1.50 reaches the command cap while inventory continues to rise.
The execution and evidence gates remain BLOCK because E1 P1160/P1200 failed
their corrected smoke horizons, the original fixed-mesh E5-PSINK packets did
not pass their declared source-accounting requirement, and the completed
finite-horizon screens do not establish a bounded falsifiable qualification
hypothesis. The E5-CZ recovery family is execution-complete: G025, recovered
G050, and fresh G100 all passed the split/source/readback contracts and
produced finite analyses. G050 has the smallest provisional late inventory
slope, but its current evidence is a recovered native `748--998` continuation
window. All three gains still show positive global inventory drift and open
boundary-only mixture closure. No qualification path is approved.

The human-approved G100 continuation then reached active `2,500`. It retained
positive total inventory drift, lower-region rebound, source-cap saturation,
and open mixture closure under the unchanged controller. The result did not
reject the no-outlet absorber abstraction; it identified the old total-
inventory feedback and command cap as the next controlled uncertainty. The
new [E5-CZ absorber-control family](cell-zone-absorber-control-family/index.md)
is now planned with lower-zone feedback, fixed `G=2.00`, and three bounded
source caps. It remains NOT_RUN pending a separate launch decision.

On 2026-09-15 the human authorized a separate E6 localized pressure-boundary
diagnostic. The design partitions the existing planar bottom into five
mesh-supported radial bands, keeps the inner four as walls, and starts by
opening only the outermost resolved band as a pressure outlet. See the
[E6 localized radial-band pressure-outlet family](ringed-bottom-pressure-outlet-family/index.md).
The family is design-ready but not placed or executed; its mesh catalogue and
save/reopen capability gate remain mandatory.

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
