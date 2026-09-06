# D06 repair research — steady Eulerian numerical architecture

Status: research brief only. It does not authorize a replacement case or a
solver mutation.

## Current tension

```text
Mixture/RNG discovery cases → complete attached 50 + 500 iteration evidence
        ↓
Eulerian A/B child → model and phase/material mapping save/reopen correctly,
                   but no smoke report coordinate after >17 minutes
        ↓
Is the bold lane uninformative because Eulerian is irrelevant here, or because
the inherited steady numerical architecture is not suitable for Eulerian?
```

The blocked D06 attempt is not evidence either way: it executed no counted
smoke/discovery coordinate and produced no final pair. The phase remains
strictly steady and surrogate-only; this brief does not introduce a physical
controller, a plant target, or a transient qualification route.

## Research evidence

- The Phase-01 reference recommends Eulerian only as a controlled second-stage
  sensitivity from a trusted Mixture baseline because it needs tighter
  numerical/convergence control ([reference setup](../../phase-01-purnanto-baseline-and-inlet-exploration/purnanto-00-reference-spiral-boc/setup.md)).
- The official Fluent multiphase stability guidance recommends the Multiphase
  Coupled solver for **steady Eulerian** solutions, a good starting field, and
  a reduced Courant number when complex/higher-order behaviour causes
  difficulty; it warns that overly low volume-fraction relaxation can delay
  the solution. [Ansys Fluent stability and convergence guidance](https://ansyshelp.ansys.com/public/Views/Secured/corp/v242/en/flu_th/flu_th_sec_multiphase_stab_conv.html)
- The current Fluent User's Guide distinguishes steady Eulerian controls with
  pseudo time enabled versus disabled, and identifies their different
  relaxation/Courant controls. [Fluent multiphase solution strategies](https://ansyshelp.ansys.com/public/Views/Secured/corp/v251/en/flu_ug/flu_ug_sec_multiphase_solution.html)

Research makes a solver-architecture repair plausible; it does **not** show
that Eulerian is a more physical separator model or that the repair will work
for this geometry.

## D06R outcome

`P6-D06R-EC` replaced the original stalled D06 numerical architecture with
the verified Eulerian `Coupled` scheme. Its smoke call advanced only one
printed coordinate before Fluent declared the solution converged, and the
inherited brine-entry total-pressure report was invalid for Eulerian and did
not write a history. The run correctly blocked before a countable screen. This
is a formulation-specific instrumentation incompatibility, not evidence that
Eulerian is physically irrelevant.

Because the campaign's report package was declared before compute, D06R cannot
be made countable by silently omitting that report afterward. A third Eulerian
attempt with a revised package would change both numerical architecture and
instrumentation and is deferred; it is no longer the smallest interpretable
sixth lane.

## Serious replacement candidate

| Field | Evidence-backed candidate |
|---|---|
| Candidate | `P6-D06C-PR`: steady Mixture/RNG prescribed continuation path, starting at 1.115 MPa gauge and applying the predeclared sequence 1.120, 1.125, 1.13125, and 1.1375 MPa after successive 100-iteration chunks. |
| Scientific question | Is the short-horizon lower-pool response at the upper-pressure bracket materially dependent on the controlled pressure path, or is it adequately characterized by the cold fixed-pressure endpoints? |
| Challenged assumption | That D01/D02 cold-start fixed-pressure endpoint comparison is sufficient to characterize the surrogate response, regardless of continuation/initialization path. |
| Research basis | Fluent's steady-Eulerian guidance identifies a good starting field as material to multiphase numerical behaviour. The failed Eulerian lanes make numerical path dependence consequential; the Phase-06 fixed-pressure and feedback screens leave it unresolved. This candidate keeps the verified Mixture/RNG physics and all current valid reports. |
| Prior collision | `NEW`: D04/D05 update pressure in response to pool-mass error; this case applies a fixed, open-loop, monotonic bracket traversal and directly compares its final upper-pressure state with D02. It is not a gain or target variation. |
| Minimal probe | Five 100-iteration chunks across the specified pressure path, using the exact existing F11 parent, all 30 current valid reports, and the same 50 + 500 attached horizon. |
| Positive learning | A path-dependent proxy/routing response demonstrates that initialization/continuation is a competing numerical explanation that a later hypothesis must control. |
| Negative learning | Agreement with D02 at the matched upper-pressure endpoint supports treating the cold fixed-pressure bracket as adequate at discovery scale. |
| Main confounders | The pressure changes are not a physical controller and the final window is short; the result only assesses steady numerical surrogate path sensitivity. |
| Tractability | High: it uses the already evidence-valid Mixture/RNG parent, known pressure setter, unchanged monitor package, and the feedback runner's chunked execution pattern without an Eulerian model mutation. |
| Implementation unknowns | None beyond a deterministic pressure-sequence argument and per-chunk readbacks; no new Fluent model, report field, or manual setting is introduced. |

## Rejected/deferred alternatives

- **Eulerian D06/D06R**: two failed pre-horizon attempts now establish an
  implementation/instrumentation limitation for the inherited 30-report
  package. Do not weaken it post hoc; defer an Eulerian-specific report
  redesign to a later discovery extension only if still needed.
- **Steady VOF**: prior history makes this a high-risk partial repeat with an
  interface/steady confounder; it is not an appropriate fast repair.
- **Another feedback gain**: a nearby parameter sweep is redundant with D04
  and D05 and cannot answer the model-form/numerical-architecture tension.
- **Transient Eulerian or physical controller design**: outside the human-set
  steady numerical-surrogate boundary.

## Required next gates

1. Resolve the exact Fluent 2025 R2 configuration mechanics in a disposable
   child, with pre-save and fresh-reopen readbacks.
2. Update the six-case design to replace unavailable D06 with D06R only if the
   capability recipe is verified; otherwise select another nonredundant
   researched candidate.
3. Obtain a fresh independent `DISCOVERY_DESIGN` transition review before any
   D06R mutation or solve.
