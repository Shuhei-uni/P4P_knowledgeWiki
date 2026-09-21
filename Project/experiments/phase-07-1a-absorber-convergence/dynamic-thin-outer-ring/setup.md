# C8 dynamic thin-outer-ring setup contract

## Status

**Human-authorized independent Server-3 C8 route — 2026-09-21.** C8 is now a
standalone discovery family. It must begin from a fresh Server-3 237k all-wall
baseline construction and must not use, inspect, wait on, transfer, or inherit
any C7 case/data artifact. An internal C8 all-wall development run (`C8-D0`)
creates the sole eligible C8 parent and its trigger evidence.

`C8-D0` uses both inlet targets and the phase-2 absorber at multiplier `0.25`
at active 0, linearly ramps all three together to `1.00` through active 2,000,
then holds the unchanged base commands through active 5,000. All five bottom
bands remain walls throughout. It has the same paired checkpoint cadence and
file-backed inventory/flux/residual evidence as a C8 child, but it never opens
the ring.

## Stage-1 packets

| Packet | Ring gauge pressure | Parent | Trigger | Horizon |
| --- | ---: | --- | --- | ---: |
| C8-P0 | 1.120 MPa | exact selected C8-D0 Server-3 pair | C8-D0-established persistence rule | 5,000 active iterations |
| C8-P10 | 1.110 MPa | same exact C8-D0 Server-3 pair | same rule | 5,000 active iterations |
| C8-P30 | 1.090 MPa | same exact C8-D0 Server-3 pair | same rule | 5,000 active iterations |
| C8-P60 | 1.060 MPa | same exact C8-D0 Server-3 pair | same rule | 5,000 active iterations |

The ladder is strictly sequential. Do not start a later point if the preceding
case has sustained vapor-dominated ring outflow, unacceptable phase/mixture
balance, destructive reverse flow, or a solver failure.

## Parent and immutable controls

Before constructing any child on Server 3, the C8 operator must prove:

1. a new Server-3 all-wall 237k baseline pair has been save/reopened and
   audited against the baseline fingerprint;
2. C8-D0 has a selected all-wall paired checkpoint, durable Server-3 identity
   receipt, and file-backed late development evidence;
3. Server 3 can reopen both C8-D0 files and reproduce the all-wall readback;
4. the mesh has the five named bands `bottom`,
   `bottom-thin-inner-separator-purnanto`,
   `bottom-thick-inner-separator-purnanto`,
   `bottom-thick-outer-separator-purnanto`, and
   `bottom-bottom-band1-thin-outer-separator-purnanto`; and
5. the lower `p7-e5-lower-y010` source remains phase-2-only with its integrated
   command at `-116.92 kg/s`, zero direct phase-1 source, and unchanged base
   inlet targets (`116.92 kg/s` liquid and `80.69 kg/s` vapor).

Every C8 child begins from a fresh read of that same selected C8-D0 pair. The
first four bands remain stationary no-slip walls throughout. The named thin
outer ring also remains a wall until the trigger is satisfied. No C8 setup
may reinitialize, patch, remesh, retune the absorber, or change any solver or
turbulence setting.

## Monitor-based activation rule

After C8-D0 completes, derive the reference trigger from its raw active
4,000--5,000 lower-liquid-mass samples before building a C8 child. The
threshold is `0.80 × median(C8-D0 lower-liquid mass over active 4,000--5,000)`
and persistence is 20 consecutive 10-active-iteration samples. Record the
resulting numeric threshold and selection receipt in this file and the C8
manifest. C8 will not replace either with a bare iteration condition.

```text
metric: lower-zone liquid mass, report definition absorb-lower-liquid-mass
threshold_kg: 0.80 × median(C8-D0 active-4000..5000 lower-liquid mass)
persistence_active_iterations: 200
cadence_active_iterations: 10
open condition: metric >= threshold_kg at every sample in the persistence window
```

At the first satisfied sample, save an all-wall pre-switch paired checkpoint
to the Server 3 local run directory, change only
`bottom-bottom-band1-thin-outer-separator-purnanto` to a pressure outlet, set
its requested gauge pressure, read back the type/pressure/backflow settings,
save a post-switch local pair, and continue. A missing trigger is a valid
`NO_SWITCH` result after the full horizon, not permission to open by iteration.

## Evidence and checkpoints

Each child writes file-backed histories for residuals; mixture, phase-1, and
phase-2 fluxes at both inlets, the steam outlet, and the ring; total/lower/
adjacent liquid inventories; and absorber source accounting. It also captures
ring pressure, ring wall/open state, switch iteration, phase fractions,
reverse-flow/fatal diagnostics, and the last valid state.

Before a C8 smoke solve, delete any inherited or generic report-file objects,
recreate the named flux and inventory report definitions, and bind each output
file to exactly one definition. Read back the binding and require every
expected file to exist and contain samples after the active-50 smoke. This is
an explicit recovery against the stale, unbound `report_defs: None` objects
observed in the first C7 attempts; it is instrumentation-only and does not
alter C8 physics.

Save paired case/data checkpoints at active 1,000, 2,000, 3,000, 4,000, and
5,000 **to the Server 3 local run directory only**. The terminal paired case
and data, or the last valid pair when a child fails, are the only case/data
files copied to OneDrive. File-backed monitor evidence, manifests, and failure
transcripts remain durable C8 evidence even when an intermediate checkpoint is
not copied to OneDrive. The terminal analysis compares liquid ring flux
against direct vapor loss and reports phase and mixture balance including
storage/source terms. Stage 2 is enabled only after Stage 1 identifies the
least-aggressive useful pressure.
