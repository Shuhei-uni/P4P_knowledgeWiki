# Setup 010V2b — EWF Edge-Separation Sensitivity

## Setup metadata

| Field | Value |
|---|---|
| Setup ID | `010V2b` |
| Lifecycle | `active` |
| Role | edge-separation-only EWF sensitivity |
| Parent setup | [010V2 clean deposition control](010V2-ewf-deposition-film-inventory.md) |
| Controlled change | edge separation only |
| Evidence-use label | diagnostic until generated-particle mass is reported |
| Outcome | needs follow-up |
| Linked report | [010V2b partial diagnostic results](../reports/010V2b/results.md) |

## Objective

Test whether the wall film separates at confirmed geometric film-wall edges and generates DPM parcels.

This branch may only start after the clean `010V2` parent has developed a finite, bounded film at the intended edge. Retain the parent intentional fixed transient controls and global DPM interaction `Off`. Before execution, apply the parent DPM correction: unsteady tracking off, no `0.001 s` particle-time-step override, and maximum particle steps `10000`. Do not enable edge separation on the failed `10a` state or during the initial zero-film transient.

## Click-by-click procedure

1. Open the accepted/read-back-verified `010V2` case/data pair.
2. Save as `010V2b-ewf-edge-separation.cas.h5` and `010V2b-ewf-edge-separation.dat.h5`.
3. Go to `Models > Eulerian Wall Film > Edit`.
4. Confirm `Particle Splashing = Off`.
5. Confirm `Particle Stripping = Off`.
6. Enable `Edge Separation`.
7. Leave `Critical Weber Number`, `Critical Angle`, and `Separation Model` at Fluent defaults for the first diagnostic, unless a project-specified value is already documented.
8. Keep `Random Separation = Off` initially so the first result is deterministic.
9. Go to `Models > Discrete Phase > Interaction` and confirm global `DPM Interaction with Continuous Phase = Off`.
10. Go to `Boundary Conditions` and inspect every EWF wall edge.
11. Confirm the intended edge is a real film-wall edge and is not an accidental mesh/domain boundary.
12. Confirm the film reaches that edge in the `010V2` parent result.
13. Reopen the EWF panel and record every separation parameter after Fluent applies defaults.
14. Check `Models > Discrete Phase > Injections` for an automatically created separation injection, typically named with an EWF strip/separation identity.
15. Verify its material, diameter, source surface, and flow-rate readback; do not manually add a duplicate injection.
16. Initialize only if required by the setting change; preserve the finite parent film field.
17. Run a `5-10` step smoke test with the inherited fixed `010V2` transient controls.
18. If film CFL, source terms, or residuals spike, stop and return to the clean `010V2` parent before interpreting separation.
19. If stable, run the same transient budget as `010V2`.
20. Save a separate case/data checkpoint.

## Required outputs

- film mass arriving at the edge;
- separated DPM parcel count and represented mass;
- separation injection identity and material;
- film outflow and remaining inventory;
- direct DPM escape versus generated-particle escape;
- residuals, film CFL history, global DPM interaction state, and phase-flux balance.

If no particles are generated, first check film presence, edge connectivity, and local Weber/impact conditions. Do not tune thresholds until those checks pass.
