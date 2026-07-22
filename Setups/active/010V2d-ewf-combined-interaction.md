# Setup 010V2d — Combined EWF Interaction Confirmation

## Setup metadata

| Field | Value |
|---|---|
| Setup ID | `010V2d` |
| Lifecycle | `active` |
| Role | combined wall-film interaction confirmation |
| Parent setup | accepted subset of [010V2a](010V2a-ewf-splash.md), [010V2b](010V2b-ewf-edge-separation.md), and [010V2c](010V2c-ewf-particle-stripping.md) |
| Controlled changes | only individually accepted EWF mechanisms |
| Evidence-use label | future combination diagnostic; not validated by default |
| Outcome | needs follow-up |
| Linked report | [010V2d diagnostic results](../reports/010V2d/results.md) |

## Objective

Determine whether the individually interpretable EWF mechanisms remain stable and mass-reconcilable when combined.

This branch must not be created until the clean `010V2` control and each selected mechanism branch have separate evidence records.

The combined branch inherits the `010V2` intentional fixed transient controls and global DPM interaction `Off`. Before execution, apply the parent DPM correction: unsteady tracking off, no `0.001 s` particle-time-step override, and maximum particle steps `10000`. Global DPM interaction is enabled only in the separate `010V2d-2` branch.

## Selection rule

1. Start from a fresh copy of the clean, stable `010V2` case/data.
2. Select only mechanisms that produced a bounded film inventory and a reportable generated-particle mass.
3. Do not include a mechanism merely because it produced a visually interesting contour.
4. Do not combine a failed or unresolved mechanism with another mechanism.

## Click-by-click procedure

1. Open the accepted clean `010V2` case/data pair.
2. Save as `010V2d-ewf-combined.cas.h5` and `010V2d-ewf-combined.dat.h5`.
3. Go to `Models > Eulerian Wall Film > Edit`.
4. Enable only the accepted mechanism settings, one at a time.
5. After enabling each mechanism, reopen the panel and record the setting readback.
6. Go to `Boundary Conditions` and enable only the corresponding wall-level settings.
7. Confirm all generated injections are unique and not duplicate manually created injections.
8. Keep film material, DPM materials, fixed `010V2` transient controls, solution schemes, and source under-relaxation identical to the accepted child branches.
9. Run a `5-10` step smoke test with the inherited fixed `010V2` transient controls after the first mechanism is enabled.
10. If stable, enable the next accepted mechanism and repeat the smoke test.
11. If film CFL, source terms, or residuals spike, save the evidence as a failed combination and return to the isolated branches; do not increase the timestep to force continuation.
12. If the second mechanism destabilizes the case, save the evidence as a failed combination and return to the isolated branches.
13. Run the full documented averaging window only after the combined smoke test passes.

## Required outputs

- direct injected DPM mass;
- absorbed DPM mass;
- splash mass, separated mass, and stripped mass separately;
- generated injection identities and represented flows;
- film storage, film outflow, and liquid at the steam outlet;
- total liquid closure, film CFL/source history, global DPM interaction state (`Off`), and residual history.

The combined branch remains diagnostic unless all liquid pathways can be separated and reconciled.
