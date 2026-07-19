# Verification And Validation Index

## Purpose
This directory stores project-owned verification and validation (`V&V`) records for the geothermal separator work.

Use this layer for:
- numerical verification reports tied to a specific setup branch or run family;
- validation reports tied to a specific external anchor or target set;
- project claim-policy and sign-off records;
- links to machine-readable target manifests and automated check outputs.

Do not use this layer for:
- reusable CFD method explanations that belong in `CFD_wiki`;
- setup-branch lineage, parent/child naming, or setup snapshots that belong in `Setups/`;
- raw Python automation artifacts that should stay in `PyAnsys`.

## Core Pages
- [policy](policy.md): project rulebook for V&V scope, allowable claim language, and handoff between automation and human review.
- [claim-classes](claim-classes.md): short project-facing interpretation of `Debug only`, `Numerically verified`, `Trend supported`, and `Externally validated`.
- [signoff-log](signoff-log.md): final human-reviewed record of what each setup branch is allowed to claim.

## Targets
- [targets/index](targets/index.md): target manifests, anchor-selection notes, and links to machine-readable target definitions stored outside the wiki.

## Verification Reports
- [verification/index](verification/index.md): numerical verification reports such as mesh checks, monitor gates, repeatability, and DPM tracking audits.

## Validation Reports
- [validation/index](validation/index.md): external comparison reports against trend anchors, analytical targets, and future measured data.

## Cross-System Links
- Reusable method authority:
  - `../../../CFD_wiki/wiki/synthesis/separator-cfd-verification-and-validation-workflow.md`
- Setup lineage authority:
  - `../../../Setups/order-dictionary.md`
- Active project roadmap:
  - `../project/roadmap.md`
- Current model-facing summary:
  - `../model/validation.md`
