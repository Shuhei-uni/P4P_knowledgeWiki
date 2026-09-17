# Histories

Prefer native solver/report coordinates and raw values.

## Residuals

Stitch restarted/staged histories on their real iteration/time coordinates.
Show the raw history. Add rolling/statistical summaries only when they clarify a
trend; label the transformation.

Residuals describe numerical behaviour. They do not by themselves prove physical
steady state.

## Fluent report histories

Prefer file-backed report histories when live buffers are incomplete or a run
was detached/restarted. Preserve report identity, units, and sample coordinates.

For comparisons, align scientifically equivalent windows rather than silently
forcing equal row counts.

If a required history does not exist, say whether it can be reconstructed from
saved artifacts. Otherwise return the narrowest rerun/instrumentation repair.
