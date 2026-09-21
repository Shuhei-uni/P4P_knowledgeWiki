# Histories

Prefer native solver/report coordinates and raw values.

## Residuals

Stitch restarted/staged histories on their real iteration/time coordinates.
Show the raw history. Add rolling/statistical summaries only when they clarify a
trend; label the transformation.

Residuals describe numerical behaviour. They do not by themselves prove physical
steady state.

Use native Fluent iteration/time coordinates, never sample index. For staged or
restarted work, identify every segment's start/end coordinate, source, and
overlap. Remove only verified duplicate coordinates; retain true gaps, stage
boundaries, and failure tails without interpolation. Label the output complete,
partial, or stitched and state the stitch limitation. Start from
`PyAnsys/scripts/inspection/export_residuals.py` for direct export; inspect its
live/file assumptions before adapting it.

## Fluent report histories

Prefer file-backed report histories when live buffers are incomplete or a run
was detached/restarted. Preserve report identity, units, and sample coordinates.

For comparisons, align scientifically equivalent windows rather than silently
forcing equal row counts.

Inspect report definitions and report files before assuming data is in the live
monitor buffer. A relative `.out` path may resolve in Fluent's remote working
directory, not beside the case/data pair. Preserve definition identity, source
path, units, native coordinate, point count, and parser status. The reusable
starting point is `PyAnsys/scripts/inspection/extract_report_plot_histories.py`.

## Descriptive overlays

Keep the raw trace visible. A moving/windowed average, median, percentile band,
rolling spread, or simple final-window slope may clarify a noisy trend when its
window, fitting range, and purpose are shown. If a reasonable alternative window
changes the apparent tendency, show or report that sensitivity. These overlays
describe solver behaviour; they do not create independent samples, prove
convergence, or manufacture uncertainty bounds.

If a required history does not exist, say whether it can be reconstructed from
saved artifacts. Otherwise return the narrowest rerun/instrumentation repair.
