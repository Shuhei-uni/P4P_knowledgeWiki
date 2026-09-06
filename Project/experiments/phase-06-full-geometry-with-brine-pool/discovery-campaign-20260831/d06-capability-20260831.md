# D06 steady-Eulerian capability proof

Status: `VERIFIED_CAPABILITY` for the disposable server-3 child. This is a
configuration capability result, not a D06 discovery result; no D06 iterations
were run in this proof.

## Fingerprint

- Runtime: `server-3@10.104.145.176`
- Fluent: `Ansys Fluent 2025 R2`
- Parent: canonical paired F11 case/data in the campaign `run-paths.yaml`
- Parent model: steady Mixture, implicit volume fraction, two phases
- Phase mapping: `phase-1 -> water-vapor-at-psep`; `phase-2 -> water-liquid-at-psep`
- Parent report package: 30 named report-file monitors visible before mutation

## Manual state checklist

The version-matched [Fluent 2025 R2 User's Guide, Steps for Using a
Multiphase Model](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/flu_ug_sec_multiphase_setup.html)
states that the Multiphase Model can be set to VOF, Mixture, or Eulerian; that
Eulerian setup requires the Eulerian phase count and phase definitions/
interactions; and that implicit volume-fraction formulation supports either
steady or transient operation. The manual also lists multiphase turbulence as
an Eulerian setup step when the flow is turbulent.

The proof therefore checks:

1. The live model selector exposes `eulerian` as an allowed value.
2. The exact F11 pair loads successfully.
3. The two phase/material assignments remain present after the switch.
4. The selected model reads back as `eulerian` before save.
5. The disposable paired child saves successfully.
6. The child reopens successfully and reads back as `eulerian`.
7. The phase/material mapping survives reopen.
8. The inherited report-file object names survive reopen.

## Observed live evidence

The live Settings tree on server 3 exposed:

```text
multiphase.model.allowed_values =
  [none, vof, eulerian, mixture, wetsteam]
```

The parent readback was `mixture` with the expected two phase/material
assignments. The disposable switch used the Settings API leaf
`solver.settings.setup.models.multiphase.model.set_state("eulerian")`.
After reacquiring the parent object, the model read back `eulerian`; active
children included `model`, `vof_parameters`, and `phases`; and both phase
material assignments were unchanged. The report-file package retained 30
named objects.

The paired child was saved and reopened at:

```text
C:\Users\syok443\Documents\FluentRuns\P6\D06-capability-20260831T050500Z\prepared.cas.h5
C:\Users\syok443\Documents\FluentRuns\P6\D06-capability-20260831T050500Z\prepared.dat.h5
```

The independent post-reopen readback returned `eulerian`, the same phase/
material mapping, and the same 30 report-file object names. No solver
iteration was issued during the capability proof.

The explicit auxiliary readback on the reopened Eulerian child returned:

```text
viscous.model                       = k-epsilon
viscous.k_epsilon_model             = rng
viscous.multiphase_turbulence       = mixture
multiphase.phase_interaction        = inactive/unavailable in this child
```

The inactive phase-interaction branch was reported as a readback result, not
silently treated as configured. It is a deliberate limitation of this bold
probe: D06 tests the Eulerian formulation with the inherited/default
interaction state and does not claim to test a newly selected interphase
force law. The D06 runner now records this turbulence and interaction state
before smoke and again after each save/reopen boundary.

## Limitations and next step

This proves that the current Fluent version and parent can carry the selected
Eulerian model state through save/reopen with the inherited report package.
It does not prove that the inherited/default Eulerian phase-interaction or
multiphase-turbulence choices are scientifically adequate. D06 remains a
discovery model-form probe. Before its 500-iteration attached screen, the D06
runner must apply only the verified model switch, persist the explicit
auxiliary readback (including the inactive interaction branch), redirect
reports to the D06 run root, and pass the same smoke/instrumentation/final-
pair checks as D01–D05.
