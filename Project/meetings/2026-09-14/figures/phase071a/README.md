# Phase 07.1A figure package

The approved figure set is three separate native Fluent vector-only exports
from the matched active-500 finite discovery states:

- RNG reference;
- standard `k–epsilon`;
- realizable `k–epsilon`.

Each should use the same `XY` plane at `Z = 0`, an orthographic camera normal
to the plane, all vectors shown (`skip = 0`), fixed arrow scale, Fluent
velocity-magnitude colour mapping, explicit shared range `0–225 m/s`, and
`2400 × 1800` resolution. Contour overlays are intentionally excluded.

## Exact source pairs

```text
C:\Users\Shuhei Yokkaichi\Documents\FluentRuns\Phase07\Phase71A\TurbulenceFamily\P71A-T0-RNG-REFERENCE\20260911T092613Z\P71A-T0-RNG-REFERENCE-active500.cas.h5
C:\Users\Shuhei Yokkaichi\Documents\FluentRuns\Phase07\Phase71A\TurbulenceFamily\P71A-T1-STANDARD-KEPSILON\20260911T094339Z\P71A-T1-STANDARD-KEPSILON-active500.cas.h5
C:\Users\Shuhei Yokkaichi\Documents\FluentRuns\Phase07\Phase71A\TurbulenceFamily\P71A-T1-REALIZABLE-KEPSILON\20260911T100157Z\P71A-T1-REALIZABLE-KEPSILON-active500.cas.h5
```

Each case has its matching `.dat.h5` pair. The observed velocity-magnitude
maxima on the common centre plane were approximately `199.9`, `219.9`, and
`183.6 m/s`, respectively, so `0–225 m/s` is the rounded union range rather
than a blind global range.

## Current status

No new local vector PNG is promoted here yet. The student Fluent endpoint
dropped while the native PNG transfer was being verified, before the three
new exports could be completed and hash-verified locally. Existing vector
images elsewhere in the meeting folder are deliberately excluded from this
package because the current request said to ignore the earlier figure set.

Once the endpoint is recovered, export the three scenes with identical
camera, vector scale, colour map, and range, then inspect all three for crop
and legend consistency before insertion into the report. No patch/reset was
recorded for this turbulence-family screen, so the post-patch comparison rule
does not add another state requirement here.
