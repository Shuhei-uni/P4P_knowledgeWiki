# Project V&V Policy

## Purpose
Define where project verification and validation records live, what they are allowed to claim, and how they interact with setup reports and automation outputs.

## Ownership Split
- `CFD_wiki`:
  - reusable verification/validation method, external literature hierarchy, and cross-paper claim discipline.
- `ResearchProject_wiki/wiki/vnv/`:
  - project-specific verification reports, validation reports, target selection notes, and final claim sign-off.
- `Setups/`:
  - concrete setup-instance definition, branch lineage, and report-facing setup snapshots.
- `PyAnsys`:
  - machine-readable target files, claim-gate rules, and automated verification outputs.

## Core Rule
- `Inferred`: Python automation may classify a run up to a maximum allowable claim class.
- `Inferred`: final validation judgment remains human-reviewed and must be recorded in this wiki before a report-facing claim is treated as approved.

## Required Inputs For A V&V Record
Each verification or validation record should link:
1. the setup branch in `Setups/`;
2. the relevant run or run family;
3. the target definition or external anchor used;
4. the specific metrics compared;
5. the final allowed claim language.

## Claim Discipline
- No predefined target record:
  - maximum claim is usually `Debug only` or `Numerically verified`.
- Trend or correlation anchor only:
  - maximum claim is usually `Trend supported`.
- Direct measured or benchmark target plus human review:
  - `Externally validated` may be allowed.

## Naming Guidance
- Verification report examples:
  - `07-verification-baseline.md`
  - `07-verification-mesh-family.md`
- Validation report examples:
  - `07-validation-pointon-trend.md`
  - `07-validation-partner-targets.md`

## Sign-Off Rule
No setup branch is considered report-ready until its final claim class is entered in [signoff-log](signoff-log.md).
