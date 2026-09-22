# C8 dynamic thin-outer-ring family — corrected v2 absorber

## Status

**Deferred after a partial paused attempt on 2026-09-22.** This is a new C8
family lineage. All earlier C8-D0/C8-P0 records are retained as **INCORRECT
ABSORBER (v1)** and are not parents for these runs. The bounded partial result
is recorded in `results-v2-corrected-absorber.md`; this file is retained as
the v2 setup provenance, not as an active execution authorization.

The Server-3 baseline is built from the immutable old C8-D0 pair only as a
field/topology source. Its lower zone was renamed to
`p71a-v2-virtual-outlet` and replaced by the Phase 7.1A v2 source:

\[
S_l=-|\dot m_{l,in}|\,\alpha_l/
\max(\int_{V_a}\alpha_l\,dV,10^{-6}\,m^3).
\]

The source acts on phase 2 only, with matching liquid-momentum and shared
`k`/epsilon removal. Phase 1 has no direct mass source. The bottom remains
all-wall during corrected D0 development; each pressure child changes only
`bottom-bottom-band1-thin-outer-separator-purnanto` after the new persistent
lower-liquid trigger.

## Baseline artifacts

- all-wall v2 prepared parent: `C:\Users\syok443\OneDrive - The University of Auckland\P4P-Fluent-Artifacts\Phase07\C8-v2\20260922T120000Z\C8-V2-thin-outer-all-wall-prepared.cas.h5` and matching data;
- corrected thin-ring P0 baseline: `C:\Users\syok443\OneDrive - The University of Auckland\P4P-Fluent-Artifacts\Phase07\C8-v2\20260922T120000Z\C8-V2-thin-ring-pressure-baseline-P1120.cas.h5` and matching data;
- pressure baseline manifest: `c8-v2-baselines-20260922T120000Z/pressure-baseline-manifest.json`;
- preserved old live recovery pair: `C8-old-incorrect-absorber-live-recovery.cas.h5` and matching data under the Server-3 local correction root.

The pressure baseline was reopened and read back with 1,120,000 Pa gauge
pressure, zero phase-2 backflow volume fraction, four inner bottom bands as
walls, and the v2 source hooks intact.

## Attempted execution and closure

The durable supervisor in
`c8-v2-supervised-20260922T120000Z/supervisor-manifest.json` started the
corrected all-wall `C8-D0-V2` parent from its prepared pair. It wrote the
prepared and `active000` pairs, then captured only Fluent iterations 5001–5008
before the Server-3 stream was removed. The human paused the run at that
point. The bounded evidence is in `results-v2-corrected-absorber.md`.

The following pressure ladder was planned but was not executed:

| Child | Thin outer ring gauge pressure |
| --- | ---: |
| C8-P0 | 1.120 MPa |
| C8-P10 | 1.110 MPa |
| C8-P30 | 1.090 MPa |
| C8-P60 | 1.060 MPa |

Each child starts from the corrected D0 terminal pair, retains all inner
bottom bands as walls, opens only the named thin ring after 20 consecutive
10-iteration trigger samples, and preserves active 1,000/2,000/3,000/4,000
checkpoints plus the final pair. The supervisor stops the ladder on any
blocked child.

No pressure-child result, scientific ranking, trigger receipt, or ladder
completion is claimed. The remaining pressure-family setup packets are
deferred in the `deffered.md` records.
