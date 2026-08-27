> **Legacy source:** Setups/past/reported/010V2c-ewf-particle-stripping.md  
> **Migration note:** Historical wording, evidence status, and uncertainty labels are preserved; this Project copy is not a reinterpretation. Raw and machine-generated artifacts remain at their legacy paths.

# Setup 010V2c — EWF Particle-Stripping Sensitivity

## Setup metadata

| Field | Value |
|---|---|
| Setup ID | `010V2c` |
| Lifecycle | `reported` |
| Role | particle-stripping-only EWF sensitivity |
| Parent setup | [010V2 clean deposition control](../purnanto-010V2-clean-ewf-deposition/setup.md) |
| Controlled change | particle stripping only |
| Evidence-use label | diagnostic until stripped-mass balance closes |
| Outcome | needs follow-up |
| Linked report | [010V2c diagnostic results](results.md) |

## Objective

Test whether carrier shear strips droplets from an existing EWF film under the separator flow conditions.

Stripping is a post-formation mechanism in this project. It must not be enabled while the film is still zero, while the film inventory is unbounded, or on the failed `10a` checkpoint. Start from a stable `010V2` film field, retain the parent intentional fixed transient controls, and keep global DPM interaction `Off`. Before execution, apply the parent DPM correction: unsteady tracking off, no `0.001 s` particle-time-step override, and maximum particle steps `10000`.

## Click-by-click procedure

1. Open the accepted/read-back-verified `010V2` case/data pair.
2. Save as `010V2c-ewf-particle-stripping.cas.h5` and `010V2c-ewf-particle-stripping.dat.h5`.
3. Go to `Models > Eulerian Wall Film > Edit`.
4. Confirm `Particle Splashing = Off`.
5. Confirm `Edge Separation = Off`.
6. Enable `Particle Stripping`.
7. Leave `Critical Shear Stress`, `Diameter Coefficient`, and `Mass Coefficient` at Fluent defaults for the first diagnostic; record their readback.
8. Keep `DPM Coupling = On`, `Surface Shear Force = On`, and `Flow Momentum Coupling = Off` as inherited from `010V2`.
9. Confirm global `DPM Interaction with Continuous Phase = Off` as inherited from the intentional `010V2` configuration.
10. Go to `Boundary Conditions` and verify that every selected EWF wall has the intended wall-film condition.
11. Confirm a finite, bounded film inventory exists in the parent before enabling stripping; do not judge stripping from a zero-film initialization.
12. Check `Models > Discrete Phase > Injections` for the automatically created stripping injection.
13. Verify the generated injection material matches the film material and record its name, diameter, and source.
14. Reopen the EWF panel and record all stripping parameters.
15. Initialize only if required by the setting change; preserve the parent film field.
16. Run a `5-10` step smoke test with the inherited fixed `010V2` transient controls.
17. If film CFL, source terms, or residuals spike, stop and return to the clean `010V2` parent; do not classify the floating-point failure as stripping physics.
18. If stable, run the same transient budget as `010V2`.
19. Save a separate case/data checkpoint.

## Required outputs

- film inventory and film shear-related variables;
- `Film Stripped Mass`;
- generated stripping injection flow and particle count;
- direct DPM escape, generated-particle escape, film outflow, and film storage;
- residuals, film Courant behavior, global DPM interaction state, and phase-flux balance.

If stripping remains zero, report whether the cause is insufficient film, insufficient shear, or the default threshold—not simply “stripping failed.” If the run diverges, report the film CFL/source history and return to `010V2` before changing stripping thresholds.
