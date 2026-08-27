> **Retired source:** Meeting report/meeting report.docx
> **Migration note:** This short historical Word report and its embedded figures are preserved as an archival record. The values and evidence status are transcribed or extracted for navigation only; no result has been reinterpreted. Machine-generated artifacts remain with their original external owners; the retired written source is recoverable from Git history.

# Legacy meeting report — mixed wet-half inlet and DPM figures

The unchanged source layout is retained in [the archived Word report](legacy-meeting-report.docx). Its short narrative is mostly headings, calculated-result images, and Fluent figures; the embedded PNGs are extracted unchanged into the [legacy meeting-report figure folder](figures/legacy-meeting-report).

This record is filed with setup `04` because the source's visible rough-efficiency values match the retained setup-04 result report. That filing is an organizational link, not a new identity claim. It remains distinct from the later [mixed wet-half meeting brief](../purnanto-03-mixed-wet-half-velocity-inlet/meeting-report.md), the setup definition, and the report-level result record.

## Inlet setup recorded in the source

- velocity inlet: `26.81 m/s`;
- liquid flow: `116.92 kg/s`;
- steam flow: `80.69 kg/s`;
- total flow: `197.61 kg/s`;
- starting steam quality by mass: `0.4083`.

The source's calculated inlet-phase table records liquid volume fraction `0.0`
and steam volume fraction `1.0` for the steam-only inlet half, and liquid
volume fraction `0.018656` and steam volume fraction `0.981344` for the wet
inlet half.

## Rough flux result recorded in the source

The source records steam-outlet flow `81.45 kg/s`, liquid-outlet flow
`2.50 kg/s`, a flux-based liquid separation indicator of `2.16%`, and steam
outlet dryness of `97.02%`. These are the source's rough preliminary values;
they do not replace the evidence limits carried by the setup-04 result report.

## Injection findings recorded in the source

The nine-injection table reports the following Purnanto mass-flow weights:

| Injection | Droplet diameter [m] | Mass-flow weight [kg/s] |
|---:|---:|---:|
| 1 | `1.29E-04` | `5.846` |
| 2 | `2.15E-04` | `13.708474` |
| 3 | `3.02E-04` | `15.722479` |
| 4 | `3.88E-04` | `15.224784` |
| 5 | `4.31E-04` | `7.52414` |
| 6 | `5.60E-04` | `19.7663` |
| 7 | `7.32E-04` | `17.859486` |
| 8 | `9.91E-04` | `17.182465` |
| 9 | `1.25E-03` | `4.085872` |
| **Total** |  | **`116.92`** |

The source's tracking-settings comparison records trapped, incomplete, and
escaped counts for five settings combinations. The stream-count comparison
records `500`, `1000`, `2500`, and `5000` effective tracks. Incomplete tracks
remain the majority in the source table, decreasing from `68.2%` to `65.8%`
as the effective track count increases; escaped tracks are recorded as zero in
that comparison.

## Embedded report-facing figures

The numbered names preserve the source document's embedded-image order and
the section labels around each image.

### Calculations and summary tables

- [01 — steam-quality calculation](figures/legacy-meeting-report/01-steam-quality.png)
- [02 — volume-flow and volume-fraction calculation](figures/legacy-meeting-report/02-volume-and-volume-fraction-calculation.png)
- [03 — inlet phase-volume fractions](figures/legacy-meeting-report/03-inlet-phase-volume-fractions.png)
- [04 — inlet geometry view](figures/legacy-meeting-report/04-inlet-geometry-view.png)
- [05 — rough efficiency calculation](figures/legacy-meeting-report/05-rough-efficiency-calculation.png)
- [06 — nine-injection mass weights](figures/legacy-meeting-report/06-nine-injection-mass-weights.png)
- [07 — DPM tracking-settings comparison](figures/legacy-meeting-report/07-dpm-tracking-settings-comparison.png)
- [08 — particle stream-count results](figures/legacy-meeting-report/08-particle-stream-count-results.png)

### Fluent contours, vectors, and pathlines

- [09 — static-pressure contour](figures/legacy-meeting-report/09-static-pressure-contour.png)
- [10 — liquid-volume-fraction contour](figures/legacy-meeting-report/10-liquid-volume-fraction-contour.png)
- [11 — velocity-magnitude contour](figures/legacy-meeting-report/11-velocity-magnitude-contour.png)
- [12 — inlet velocity vectors](figures/legacy-meeting-report/12-inlet-velocity-vectors.png)
- [13 — outlet velocity vectors](figures/legacy-meeting-report/13-outlet-velocity-vectors.png)
- [14 — time-coloured pathlines](figures/legacy-meeting-report/14-time-coloured-pathlines.png)
- [15 — particle-ID pathlines](figures/legacy-meeting-report/15-particle-id-pathlines.png)
- [16 — steam particle pathlines](figures/legacy-meeting-report/16-steam-particle-pathlines.png)
