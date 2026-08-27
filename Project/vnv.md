# Verification And Validation

## Current claim limit

The project is not ready for final validation. A stable converged reference solution, repeatability, sensitivity evidence, and an external or analytical comparison target are still required (`Inferred`, [project validation summary](../ResearchProject_wiki/wiki/model/validation.md)).

Current longer runs remain diagnostic rather than validation evidence when residuals, phase balances, physical stationarity, or target comparisons are incomplete. Numerical stability alone does not establish physical validation.

## Claim classes

| Class | Allowed meaning |
|---|---|
| `Debug only` | setup behaviour or failure diagnosis; no performance claim |
| `Numerically verified` | internally stable enough for technical comparison after setup, solution, mesh/monitor, and repeatability checks |
| `Trend supported` | numerically verified and consistent with a defensible literature, analytical, or design-correlation trend |
| `Externally validated` | numerically verified, compared with a predefined direct target, and approved by human review of target appropriateness |

Internal A/B comparison is useful sensitivity evidence but is not validation by itself (`Inferred`, [claim classes](../ResearchProject_wiki/wiki/vnv/claim-classes.md)).

## Minimum gate before a report-facing claim

The selected experiment must identify:

1. the exact parent/start state and controlled change;
2. residual and monitor behaviour over a meaningful run window;
3. phase inlet/outlet fluxes and pressure/carryover metrics relevant to the question;
4. repeatability or a stated reason it is not yet available;
5. the external, analytical, or measured target and acceptable comparison logic;
6. the final human-reviewed claim class.

Use the strongest available comparison first: same-geometry or test data, then analytical/design correlation, then separator-CFD literature trend, then internal A/B evidence. If no defensible target exists, label the metric `trend-only` rather than upgrading the claim.

## Ownership and evidence flow

- `CFD_wiki/` owns reusable verification/validation methods and literature hierarchy.
- `Setups/` owns concrete setup definitions and branch lineage.
- `PyAnsys/` owns machine-readable targets, extraction, and automated checks; it may recommend a maximum claim class but does not make the final scientific judgment.
- `Project/` owns the project-specific interpretation and claim boundary.

Detailed project V&V records remain in the existing [V&V layer](../ResearchProject_wiki/wiki/vnv/index.md) until a later issue proves that a different location is needed.
