# Purnanto Parity Split-Inlet Rebuild

## 1. Purpose

Define setup `08b` as the extraction-first parity rebuild branch for the current project.

This branch exists because setup `07` is no longer trusted as the closest reconstruction of the original Purnanto Fluent setup, while setup `08` proved a useful one-inlet PyFluent scaffold but does not yet answer the current project question:

- preserve the actual observed Purnanto Fluent setup as closely as possible;
- change only the inlet representation needed for the project's two-phase inlet objective;
- rebuild `DPM` from extracted evidence rather than from memory;
- use that rebuilt branch, not setup `07`, as the next verification and validation target.

Primary authority:

- [00a-purnanto-setup-5000-live-audit.md](00a-purnanto-setup-5000-live-audit.md)
- [08-purnanto-one-inlet-massflow-recreation.md](08-purnanto-one-inlet-massflow-recreation.md)
- [../ResearchProject_wiki/wiki/technical/purnanto-live-setup-reference.md](../ResearchProject_wiki/wiki/technical/purnanto-live-setup-reference.md)
- [../ResearchProject_wiki/wiki/project/roadmap.md](../ResearchProject_wiki/wiki/project/roadmap.md)

## 2. Setup Identity

| Item | Value |
|---|---|
| Setup order | `08b` |
| Branch role | active parity-reset and V&V candidate |
| Parent authority | live audited Purnanto setup `00a` with local one-inlet rebuild lessons from `08` |
| Geometry label | `purnanto` |
| Continuous-phase intent | preserve observed Purnanto solver/model/numerics stack unless extraction proves otherwise |
| Inlet representation | two-zone split inlet for project two-phase inlet study |
| DPM intent | preserve observed DPM model settings where present; reconstruct injections only after extraction confirms what is actually missing |
| Evidence-use label | extraction-first parity rebuild |

Evidence labels used in this report:

- `Observed`: taken from the loaded Purnanto case/data audit.
- `Retained`: kept intentionally from the observed Purnanto setup.
- `User-specified`: deliberate project change from the observed Purnanto setup.
- `Assumed`: temporary placeholder until the extraction workflow proves the value.
- `Uncertain`: known unresolved item that must not be treated as settled parity.

## 3. Deliberate Change Budget

This branch is allowed to change only two setup ideas at first:

1. replace the single mixed `Mass-Flow Inlet` with a two-zone inlet representation suited to the project;
2. add project DPM injections through the steam-side inlet only after the original Purnanto DPM settings are extracted and compared.

Everything else should default to:

```text
match the observed Purnanto case first,
then document each intentional deviation explicitly
```

## 4. Continuous-Phase Parity Rule

Treat the observed Purnanto case as the authority for:

- solver family;
- steady/transient mode;
- multiphase model;
- turbulence model;
- gravity and operating pressure;
- material properties;
- discretization schemes;
- under-relaxation factors;
- outlet settings;
- any named cell-zone or wall setting that survives on the current geometry.

Do not inherit those settings from setup `07` if they disagree with the live Purnanto audit.

## 5. Inlet Rule For Setup 08b

### Continuous-flow target

Keep the Purnanto target phase flows:

- vapor `80.69 kg/s`
- liquid `116.92 kg/s`

### Geometric/inlet interpretation

Use a split inlet that maps the project hypothesis:

- outer-wall side = liquid-dominant inlet zone
- inner/core side = steam-side inlet zone

Boundary-type rule:

- `Uncertain`: do not freeze the boundary type as `Velocity Inlet` or split `Mass-Flow Inlet` purely from memory;
- extract what Fluent allows cleanly on the chosen mesh branch and preserve parity with the observed one-inlet case as far as possible;
- if the final branch uses split `Velocity Inlet` zones, record that as a `User-specified` deviation rather than calling it observed Purnanto parity.

## 6. DPM Rule For Setup 08b

Observed starting point from the live audit:

- `Observed`: `DPM` model settings exist in the saved Purnanto case.
- `Observed`: the saved case has no active injections.

This means:

- do not claim the original Purnanto injection implementation is already known;
- do not copy setup `07` injections into this branch and call them parity;
- first extract the full live DPM model tree, then recreate only the settings that are actually present;
- add project injections through the steam-side inlet as a new controlled layer once the carrier setup is accepted.

Initial project rule for the added injections:

- injection origin = steam-side inlet zone
- particle material = water-droplet surrogate matched to the liquid phase unless extraction proves a different legacy material was used
- injection diameters/counts = `Uncertain` until extracted or explicitly chosen as a project sensitivity set

## 7. Required Extraction Workflow

Before using setup `08b` for V&V, complete this order:

1. export the live Purnanto setup tree from Fluent through `PyAnsys`;
2. compare exported settings against the existing human-written setup notes;
3. build a machine-readable parity checklist for:
   - models
   - materials
   - phases
   - boundary conditions
   - numerics
   - DPM model settings
4. rebuild the continuous field on the local/current mesh with only the split-inlet change active;
5. read back the applied settings after each parent-model activation;
6. only then add DPM injections through the steam-side inlet.

## 8. Acceptance Gate

Treat setup `08b` as ready for V&V only when:

1. extracted-versus-rebuilt continuous-phase settings are reconciled or explicitly bounded;
2. inlet phase targets match the intended values closely enough to treat the branch as correctly imposed;
3. residual and monitor behavior is stable enough for comparison;
4. the DPM model state is rebuilt from extracted evidence rather than guessed memory;
5. any remaining unknown injection detail is labeled `Uncertain` and scoped as a sensitivity, not as exact historical parity.

## 9. What Setup 08b Replaces

For project decision-making:

- setup `07` becomes comparison-only context, not the next primary V&V parent;
- setup `08` remains a useful one-inlet automation scaffold and parity-check sandbox;
- setup family `09` stays reserved for later DPM sensitivity work after a trusted parity-reset branch exists.

## 10. Immediate Build Questions

Use setup `08b` to answer these questions in order:

1. What settings in setup `07` actually drifted away from the live Purnanto case?
2. Can Python export and replay the true Purnanto continuous-phase setup reliably enough to remove manual setup error?
3. Once that parity is recovered, does the split-inlet project variant still behave acceptably?
4. After that, what is the minimum justified DPM injection definition through the steam-side inlet?
