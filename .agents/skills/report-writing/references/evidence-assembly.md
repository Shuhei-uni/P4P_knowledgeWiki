# Evidence assembly

Use this branch when reconstructing a report from several Project experiments,
when records disagree, or when deciding which evidence earns space in the final
narrative.

## Build a source map

For each intended claim, link the owning `CONTEXT.md`, `setup.md`, `results.md`,
run/artifact identity, and one decisive figure or table. Read current Project
records first; use Git only to recover an important decision absent from those
records. Keep a discrepancy visible until resolved—do not average conflicting
case names, horizons, or interpretations into a smoother story.

## Choose figures by argumentative role

Select figures that respectively answer the central question, make the relevant
comparison legible, establish the narrow numerical adequacy needed to trust it,
or expose a material limitation. Keep their source run, field/window, units,
comparison basis, and caption-level observation adjacent to the figure.

Ask `cfd-numerical-analysis` to make a missing scientific figure from verified
artifacts. If it cannot be made, label the gap and adjust the claim; do not use
an illustrative substitute as simulation evidence.

For every result group, place direct measured values before derived quantities
and retain units, sign convention, surface/zone definition, and iteration/time
window. Add a DPM, EWF, carrier-flow, VOF, verification, or validation module
only when it helps answer the section question. For example, a DPM section must
retain injection identity, tracked counts, fates, and mass-flow bookkeeping;
an EWF section must keep inventory (`kg`) distinct from rate (`kg/s`); and a
validation section needs its independent reference, metric, and validity scope.
Do not make a final snapshot stand in for an unavailable transient history.

## Write from observation outward

For each section use this order: question → controlled change → direct
observation → interpretation → bounded conclusion. Describe failed attempts
only where they explain the eventual method, ruling-out process, or a limitation.
Use raw histories and machine summaries as traceable supporting material rather
than pasting their full chronology into the narrative.

## Final evidence audit

Before delivery, verify every material statement has an owning Project record,
that all figures are readable at normal size and retain provenance, that units
and terminology are consistent across comparisons, and that limitations are as
easy to find as positive conclusions. A solver endpoint, an unsourced graphic,
or an unexplained inferred mechanism cannot carry a report claim alone.
