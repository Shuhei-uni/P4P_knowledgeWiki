# Verification and validation

## Current claim limit

The project is not ready for final validation. A stable converged reference
solution, repeatability, sensitivity evidence, and an external or analytical
comparison target are still required (Inferred).

Current longer runs remain diagnostic rather than validation evidence when
residuals, phase balances, physical stationarity, or target comparisons are
incomplete. Numerical stability alone does not establish physical validation.

## Claim classes

| Class | Allowed meaning |
|---|---|
| Debug only | setup behaviour or failure diagnosis; no performance claim |
| Numerically verified | internally stable enough for technical comparison after setup, solution, mesh/monitor, and repeatability checks |
| Trend supported | numerically verified and consistent with a defensible literature, analytical, or design-correlation trend |
| Externally validated | numerically verified, compared with a predefined direct target, and approved by human review of target appropriateness |

Internal A/B comparison is useful sensitivity evidence but is not validation by
itself (Inferred). Reusable evidence hierarchy and methods remain in
CFD_wiki/; this page owns the project interpretation.

## Minimum gate before a report-facing claim

The selected experiment must identify:

1. the exact parent/start state and controlled change;
2. residual and monitor behaviour over a meaningful run window;
3. phase inlet/outlet fluxes and pressure/carryover metrics relevant to the
   question;
4. repeatability or a stated reason it is not yet available;
5. the external, analytical, or measured target and acceptable comparison
   logic;
6. the final human-reviewed claim class.

Use the strongest available comparison first: same-geometry or test data, then
analytical/design correlation, then separator-CFD literature trend, then
internal A/B evidence. If no defensible target exists, label the metric
trend-only rather than upgrading the claim.

## Current target and sign-off state

- No branch is signed off as Numerically verified or Externally validated. The
  historical sign-off state was pending; that decision remains represented
  here as unresolved (Observed).
- Available geothermal literature and design/correlation sources can support
  context or trend checks. They are not direct validation targets for the
  current geometry unless operating conditions, geometry, and metric
  definitions are shown to be transferable (Inferred).
- A non-geothermal experiment-backed RSM-DPM study can inform a later method
  sensitivity, but its operating values are not geothermal targets (Reported).
- Missing project inputs include an active-geometry pressure-drop target,
  expected steam quality/carryover range, brine-flow expectation,
  separator-efficiency target, and any usable partner/field comparison table
  (Missing Info).

## Ownership and evidence flow

- CFD_wiki/ owns reusable verification/validation methods and literature
  hierarchy.
- PyAnsys/ owns machine-readable targets, extraction, and automated checks; it
  may recommend a maximum claim class but does not make the final scientific
  judgment.
- Project/ owns the project-specific interpretation and claim boundary.

No final human sign-off has been granted. The current Stage-4 execution
package remains diagnostic evidence, not a validation record. The 2026-08-30
PNG review does not upgrade that claim class: executed RNG continuations are
not parent-eligible, and no Numerically verified or Externally validated
state exists.
