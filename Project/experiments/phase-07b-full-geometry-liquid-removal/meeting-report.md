# Phase 7b supervisor meeting report

The [meeting PDF](../../../output/pdf/phase-7b-supervisor-meeting-2026-09-22.pdf)
is a minimal-text, figure-led communication of the [G1 results](results.md),
prepared for Andy's supervisors on 22 September 2026. It does not change the
phase's scientific disposition or authorize further solving.

The 13 landscape pages include the original five G1 comparison figures,
native separator geometry, all five geometric removal extents, two full-height
liquid-volume-fraction section comparisons, all seven residual histories for
all cases, a short findings table and source identities. The
[figure bundle](../../../output/pdf/phase-7b-meeting-figures.zip) also contains
individual two-plane liquid-fraction images for S20/S40/S60/S80/S100.

New sections were extracted through the Fluent API from the four saved N5000
pairs and S100's N4000 recovery pair. S100 is explicitly labelled as recovery
evidence. Geometric region shading is not a liquid-fraction field and describes
the elevation predicate; Fluent uses cell-centroid selection. All field panels
retain native facet values with common scales and no interpolation/smoothing.

The [extraction receipt](../../../PyAnsys/output/phase07b-meeting-20260922/extraction.json)
verifies zero iterations issued and restoration of the preserved S100 N4000
case. No solver case/data artifact was overwritten. Figure sources and hashes
are in the [provenance](../../../PyAnsys/output/phase07b-meeting-20260922/report-provenance.json);
all PDF pages were rendered and reviewed in the [QA record](../../../PyAnsys/output/phase07b-meeting-20260922/report-qa.json).

[Speaker notes and interpretation](meeting-speaker-notes.md) provide a page-by-page narrative and likely supervisor questions.
