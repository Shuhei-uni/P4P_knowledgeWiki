# Setup Reports

`Setups/reports/` is the dedicated home for **numerical result reports, execution evidence, post-analysis reports, and interpretation sections based on completed simulations**.

Setup definitions and plans are kept separately under the corresponding setup tree.

## Current full-geometry reports

New `Full-geomV2` reports use the mirrored geometry-first hierarchy:

- [Full-geometry reports](full-geometry/index.md)
  - [Mixture reports](full-geometry/mixture/index.md)
  - [VOF reports](full-geometry/vof/index.md)

The path rule is:

```text
setup:  Setups/full-geometry/<physics>/<campaign>/
report: Setups/reports/full-geometry/<physics>/<campaign>/
```

Within each report campaign, give every reportable setup/stage/experiment its own `<experiment-id>/` folder. Keep that folder's `plots/` and `evidence/` beneath it; do not create a shared campaign-level plot folder.

The campaign path should match exactly between the setup side and report side.

## Historical numbered/reference reports

- [Purnanto/reference report navigation](purnanto-reference/index.md)

Historical numbered/reference reports are grouped under their programme folders, including the `09c` family under `purnanto-reference/`. Do not use a new numbered folder for a new full-geometry campaign.

## Full-geometry compatibility reports still in numbered locations

The steady full-geometry campaign predates the new mirrored report structure. Its existing reports remain in `02c/` and `02e/` to avoid breaking links, but they are canonically navigated through:

- [Full-geometry Mixture steady liquid-outlet reports](full-geometry/mixture/steady-liquid-outlet/index.md)

New reports for that campaign should use the mirrored full-geometry report folder.

## Report-only rule

Keep setup plans out of this tree. A result report should link back to the exact setup/stage plan that defined the run.
