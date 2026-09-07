# Brine-Outlet CFD Modelling Handoff — 21 August 2026

## Technical summary

The resolved-brine-outlet work has not yet produced a validated operating-flow
separator solution. It has, however, isolated the earlier failures and
established a safe continuation lineage:

- Setup `07l` is the accepted parent. It proves that the 620,431-cell resolved-
  outlet mesh and the `y<=0 m` liquid pool are bounded at hydrostatic rest when
  both inlets are zero and the brine face is temporarily closed.
- Setup `07m` safely opens the brine pressure face at zero feed and establishes
  a monotonic low/centre/high pressure response. A `0.1%` inlet hold is
  accepted as a bounded startup diagnostic.
- The progressive ramp completed `0.2%` and `0.5%`. Its `1%` checkpoint remained
  finite and bounded but stopped at a final continuity residual of `0.0177001`,
  above the `0.01` promotion limit.
- No Fluent calculation or local controller is active at this handoff. The
  attempted 1% hold timed out while connecting, before any new physical step
  was credited. Its `running` manifest is stale.
- The independent server-2 steady Mixture comparison is a terminal gross-
  drainage diagnostic. At iteration 150 its brine liquid flow was
  `-1372.91 kg/s` and mixture imbalance was `-1247.64 kg/s`; it must not be
  resumed.

The immediate next calculation is therefore a non-overwriting 20-step hold of
the accepted setup-07m `1%` transient VOF checkpoint at the same flow,
`dt=1e-7 s` and 100 inner iterations per step. It is a settling test, not a
flow increase.

## Scope and evidence labels

This document is an operational handoff for the physical brine-outlet branch.
It does not reopen the setup-07a mesh-convergence study, the enthalpy/DPM sweep,
or the numerical-sink branches.

- `Accepted diagnostic`: internally bounded evidence that passed its defined
  numerical and physical gates.
- `Diagnostic / unresolved`: useful troubleshooting evidence that is not a
  validated operating result.
- `Terminal diagnostic`: a failed field that must not be resumed or used as a
  parent.
- `Missing`: information not available in the repository and required before
  a production claim.

## Repository and instruction authority

Repository root:

```text
/Users/andy/Desktop/P4P/P4P_knowledgeWiki
```

Read these before changing or running anything:

1. `AGENTS.md`
2. `PyAnsys/AGENTS.md`
3. `ResearchProject_wiki/AGENTS.md`
4. `CFD_wiki/AGENTS.md`
5. `Setup report/order-dictionary.md`
6. `Setup report/07l-split-inlet-hydrostatic-rest-isolation.md`
7. `Setup report/07m-split-inlet-zero-feed-pressure-opening-and-inlet-ramp.md`
8. `ResearchProject_wiki/wiki/progress/current-status.md`
9. `ResearchProject_wiki/wiki/progress/experiments.md`
10. `ResearchProject_wiki/wiki/progress/blockers.md`
11. `ResearchProject_wiki/wiki/model/validation.md`

When summaries disagree, use this authority order:

1. completed machine-readable manifest and transcript;
2. setup-07m setup report;
3. this handoff;
4. current-status, experiments and order-dictionary summaries;
5. conversation history.

Do not treat a manifest as live solely because it says `running`. Confirm the
recorded PID, local process list, heartbeat age and Fluent writer state.

## Authoritative geometry and clean lineage

### Mesh

```text
Remote mesh:
C:\Users\qtra338\Documents\Mesh study\Meshes\brine-outlet-620kcells.msh.h5

SHA-256:
0d75a86e53bc020aeefa4b13ef8616413a862b15646355d90d8037d1be888394
```

Recorded mesh evidence:

| Item | Value |
|---|---:|
| Cells | `620,431` |
| Minimum orthogonal quality | `0.250003` |
| Maximum aspect ratio | `66.0258` |
| Brine-outlet area | `0.19936247 m2` |
| Brine-face centroid below inferred pool level | `0.25417245 m` |
| Solver ranks | `16` (`n0` through `n15`) |

The geometry has a dedicated brine pipe and boundary face named
`brineoutlet`; it is not the old closed-bottom mesh. The relevant boundary
roles are `liquidinlet`, `steaminlet`, `steamoutlet`, `brineoutlet` and
`wall-fluid`, with one fluid cell zone.

### Sole accepted parent for setup 07m

All setup-07m pressure-opening work must descend from the accepted setup-07l
step-10 case/data pair:

```text
C:\Users\qtra338\Documents\Mesh study\
split_inlet_resolved_brine_outlet_20260813\
brine620k_07l_hydrostatic_rest_v1_checkpoint_step10.cas.h5

C:\Users\qtra338\Documents\Mesh study\
split_inlet_resolved_brine_outlet_20260813\
brine620k_07l_hydrostatic_rest_v1_checkpoint_step10.dat.h5
```

Its physical clock is step 10 at `1.0e-5 s`. Do not reset or fabricate this
clock. Do not source a new branch from setup `07j`, `07k`, an uncheckpointed
live field, the setup-07l initialized time-zero pair, or the failed server-2
Mixture field.

## Fixed carrier physics and numerics

Unless a separately labelled one-factor sensitivity is being run, preserve:

| Item | Fixed value |
|---|---|
| Fluent | 2024 R2, double precision, 16 ranks |
| Solver | pressure-based transient |
| Multiphase | explicit VOF, vapor primary, liquid secondary |
| Materials | `water-vapor-at-psep`, `water-liquid-at-psep` |
| Turbulence | RNG `k-epsilon` |
| Gravity | `(0,-9.81,0) m/s2` |
| Energy | off |
| Coupling/pressure | PISO / PRESTO |
| Volume fraction | Geo-Reconstruct, Sharp interface |
| Body-force treatment | implicit |
| WFGC | on |
| Time discretization | first-order startup |
| Operating density | user-input vapor density `5.79743385 kg/m3` |
| Reference-pressure location | `(0,1,0) m`, in the gas region |
| Initial pool | phase-2 liquid volume fraction 1 for `y<=0 m` |
| DPM | zero injection objects; interaction off; unsteady tracking off |
| EWF | off |
| Numerical sink/UDF | absent/off |

Reference full-feed rates are liquid `116.92 kg/s` and vapor `80.69 kg/s`.
Both phase feeds must be ramped with the same proportional factor. The steam
outlet remains a pressure outlet at `1,120,000 Pa` with vapor backflow. The
brine pressure outlet uses liquid backflow volume fraction `1.0`.

The setup-07m centre brine pressure is:

```text
1,122,090.400 Pa
```

Label it exactly as a **CFD-derived closed-face modified-pressure rest bracket
(diagnostic)**. It is not a measured plant pressure, a validated downstream
line pressure, or a manually added hydrostatic correction.

## Why the clean lineage was necessary

Setup `07j` and `07k` exposed two inherited startup errors:

1. Six DPM injections remained in the imported case and Fluent tracked 6,456
   one-way parcels even though global DPM interaction was off. This probably
   did not cause the carrier pressure failure, but it violated the intended
   carrier-only contract.
2. Hybrid Initialization reported that boundary pressure information was
   unavailable and created a constant-pressure field. The dense liquid pool
   was patched afterward, so the transient solve did not begin in hydrostatic
   pressure equilibrium.

Setup `07l` explicitly deletes all injection objects, disables DPM tracking,
zeros both inlets, closes the brine face, initializes and relaxes the pool, and
then saves a clean accepted parent.

## Branch history and disposition

| Setup | Purpose | Outcome | Reuse rule |
|---|---|---|---|
| `07g` | steady resolved-outlet dry start | vapor-dominant brine discharge and liquid reversal; later divergence | diagnostic only |
| `07h` | steady resolved outlet with initial pool | early intended routing, then nonphysical drainage and FPE | do not resume |
| `07i` | WFGC-only steady sensitivity | continuity `6.9888e14`, Node-4 SIGSEGV at iteration 21 | terminal |
| `07j` | transient VOF, equal `1.12 MPa` outlets | step-2 brine liquid `-4692.8688 kg/s`; storage closure proves real model drainage | terminal |
| `07k` | transient VOF with prescribed `116.92 kg/s` liquid outlet | step-3 pressure `-4.1102e13 Pa` and outlet velocity `5.2599e6 m/s` | terminal |
| `07l` | zero-feed, closed-brine hydrostatic-rest isolation | bounded for ten `1e-6 s` steps | accepted parent |
| `07m` | zero-feed pressure opening and guarded feed ramp | bracket and 0.1% hold accepted; stopped at 1% continuity gate | active diagnostic lineage |

## Accepted setup-07l evidence

At step 10:

| Quantity | Value |
|---|---:|
| Flow time | `1.0e-5 s` |
| Domain-average velocity | `4.8978e-7 m/s` |
| Domain liquid volume fraction | `0.15826588` |
| Liquid inventory | `3774.370486 kg` |
| Brine-wall minus steam pressure | `2090.4 Pa` |
| Maximum reported Global Courant | `1.0095e-8` |
| Final continuity residual | `3.4698e-6` |

The observed `2090.4 Pa` lower-face pressure head is within `4.86%` of the
simple `rho_l g h = 2197.24 Pa` centroid estimate. This supports hydrostatic-
rest consistency but does not identify a production downstream pressure.

Machine evidence:

```text
PyAnsys/output/split_inlet_resolved_brine_outlet_20260813/
brine620k_07l_hydrostatic_rest_v1/
```

## Setup-07m evidence

### Zero-feed pressure opening

The pressure bracket was tested from identical copies of the accepted 07l
step-10 parent at `dt=1e-6`, `3e-6` and `1e-5 s`. All nine independent one-step
members remained finite, VOF-bounded, DPM-free and far below the explicit-VOF
Courant limit.

Ten-step `1e-5 s` extensions established the response:

| Brine pressure | Liquid brine flow at step 10 | Brine velocity |
|---|---:|---:|
| `1,121,895.244 Pa` | `-0.00724149 kg/s` | `0.00120518 m/s` |
| `1,122,090.400 Pa` | `+0.00451280 kg/s` | `0.00120755 m/s` |
| `1,122,285.556 Pa` | `+0.01626494 kg/s` | `0.00121358 m/s` |

Fluent mass-flow sign is negative outward. The response is monotonic and the
endpoints bracket a sign change. The centre was promoted only as a guarded
startup diagnostic.

### Accepted 0.1% hold

The bounded 0.1% hold used `dt=1e-7 s` and 100 inner iterations. End-of-step
continuity fell monotonically to `0.00186867`.

| Metric | Final value |
|---|---:|
| Liquid inlet | `+0.116920 kg/s` |
| Vapor inlet | `+0.080690 kg/s` |
| Brine liquid | `-0.0830901 kg/s` |
| Steam-outlet vapor | `-0.0809126 kg/s` |
| Domain velocity | `0.00369468 m/s` |
| Final Global Courant | `3.46743e-6` |
| Final continuity | `0.00186867` |

The periodic residual trace is expected for a transient solve with many inner
iterations: every physical step creates a new residual spike followed by inner
iteration decay. Accept or reject the envelope and end-of-step values, not the
mere presence of the sawtooth.

### Progressive ramp and current parent

The accepted 0.1% checkpoint progressed through `0.2%`, `0.5%` and `1%`, ten
physical steps per level at `dt=1e-7 s` and 100 inner iterations.

- `0.2%` and `0.5%` completed without a hard-gate failure.
- `1%` remained finite and bounded: maximum Global Courant `3.48732e-5`,
  brine liquid `-0.877498 kg/s`, and steam-outlet vapor `-0.808819 kg/s`.
- Final continuity at 1% was `0.0177001`, so the controller correctly stopped
  and withheld every queued `2%` through `100%` stage.

The accepted continuation checkpoint is:

```text
C:\Users\qtra338\Documents\Mesh study\
split_inlet_resolved_brine_outlet_20260813\
brine620k_07m_pressure_opening_campaign_v1_progressive_micro_ramp_dt1e-7_inner100_fraction_0p01.cas.h5

C:\Users\qtra338\Documents\Mesh study\
split_inlet_resolved_brine_outlet_20260813\
brine620k_07m_pressure_opening_campaign_v1_progressive_micro_ramp_dt1e-7_inner100_fraction_0p01.dat.h5
```

This checkpoint failed only the residual-promotion criterion. It is suitable
for a guarded hold, not for immediate higher-flow promotion.

## Current controller and server state

At the 21 August handoff process audit:

- no setup-07m or server-2 calculation controller was running locally;
- no Fluent calculation was known to be active;
- the 1% hold manifest said `running` but had zero blocks, zero checkpoints and
  no heartbeat; its controller had timed out after 1,800 seconds while
  connecting, before any Fluent step was credited;
- server 2 had stopped safely at iteration 150 on its gross-drainage gate.

`PyAnsys/.env` is configured for two servers using the unsuffixed server-1 keys
and `FLUENT_IP2`, `FLUENT_PORT2`, `FLUENT_PASSWORD2` for server 2. Credentials
must remain only in `.env`; do not copy them into reports, prompts, logs or
transcripts. The connection helper uses `cleanup_on_exit=False` and supports
`--server-id 1` and `--server-id 2`.

Do not assume an endpoint is currently healthy from this handoff. Recheck raw
TCP reachability, the exact credential pair, Fluent 2024 R2, compute-rank count
and connected clients. Never open a competing PyFluent session while a writer
RPC is active.

Server 1 owns the authoritative remote setup-07l/07m files. Server 2 did not
have the setup-07l step-10 checkpoint at the matching remote path. Do not split
the sequential ramp between servers unless the complete parent case/data pair
is copied, checksummed and fully read back on server 2. Server 2 may run an
independent sensitivity only from a verified identical parent.

## Server-2 failure evidence

The server-2 branch was steady Mixture and was not part of setup-07m lineage.
It used full feed immediately and a fixed diagnostic brine pressure after a
non-hydrostatic constant-pressure initialization plus liquid-pool patch.

| Iteration | Continuity | Mixture net | Brine liquid | Brine velocity | Domain velocity |
|---:|---:|---:|---:|---:|---:|
| 50 | `0.31664` | `-271.38 kg/s` | `-390.10 kg/s` | `2.999 m/s` | `7.787 m/s` |
| 100 | `0.38956` | `-79.56 kg/s` | `-197.03 kg/s` | `6.459 m/s` | `10.096 m/s` |
| 150 | `0.53041` | `-1247.64 kg/s` | `-1372.91 kg/s` | `11.017 m/s` | `14.467 m/s` |

The nominal full-feed bulk liquid velocity through the brine face is only:

```text
116.92 / (881.2109 * 0.19936247) = 0.66553 m/s
```

The simultaneous growth of continuity, drainage, velocity and liquid volume
fraction is a true steady instability, not a harmless transient residual
cycle. Iteration-50 and iteration-100 checkpoints and the separately saved
iteration-150 failure state are diagnostic evidence only.

Evidence root:

```text
PyAnsys/output/split_inlet_resolved_brine_outlet_20260813/
server2_mixture_carrier_extension_20260821_resume1/
```

## Immediate safe continuation

### 1. Reconcile ownership before connecting

1. Audit local PIDs and the stale 1% hold manifest.
2. Confirm no writer process or calculation RPC remains.
3. Use a bounded raw TCP check before opening an authenticated PyFluent owner.
4. Confirm the selected server reports Fluent 2024 R2 and exactly 16 solver
   ranks.
5. Confirm the remote 1% case/data pair exists and is readable.
6. Preserve the stale zero-step hold attempt. Do not overwrite its directory;
   use a new attempt label or add a safe output-name option before relaunch.

### 2. Run the fixed 1% hold

Use the saved `0.01` checkpoint with:

```text
inlet fraction: 0.01
liquid inlet:    1.1692 kg/s
vapor inlet:     0.8069 kg/s
dt:              1e-7 s
inner limit:     100 iterations per physical step
additional hold: 20 physical steps
checkpoints:     additional steps 5, 10 and 20
```

The existing driver is:

```text
PyAnsys/scripts/setup/run_setup07m_one_percent_hold.py
```

It currently hardcodes the existing output directory name. Before rerunning,
make its output non-overwriting, for example with an explicit attempt suffix.
Follow the repository's inspection/readback workflow and do not reuse stale
Fluent object handles after loading case/data or changing a boundary type.

### 3. Promotion gate

Promote 1% only after all of the following are true:

- two consecutive end-of-step continuity values are `<=0.01`;
- the end-of-step residual envelope is stable or decreasing;
- actual Global Courant is present and `<=0.25`;
- liquid volume fraction remains finite and within numerical tolerance of
  `[0,1]`;
- pressure and velocity remain finite and within the existing setup-07m hard
  gates;
- phase routing remains steam/vapor outward and brine/liquid outward without
  gross reverse flow;
- liquid inventory and storage-aware phase closure are bounded;
- zero DPM objects and no parcel-tracking text are confirmed;
- no AMG divergence, FPE, SIGSEGV, RPC timeout or incomplete clock advance
  occurs.

Residuals alone do not establish acceptance.

### 4. If the 1% hold fails

Run one factor at a time from the same saved 1% checkpoint:

1. keep `dt=1e-7 s` and test 200 inner iterations per step;
2. then keep 100 inner iterations and test `dt=5e-8 s`;
3. do not change pressure, feed and numerics simultaneously;
4. compare end-of-step residual envelope, Courant, phase flows, pressure,
   velocity, inventory and storage closure.

### 5. If the 1% hold passes

Replace the coarse `1 -> 2 -> 5 -> 10%` sequence with smaller proportional
holds, for example:

```text
1.5%, 2%, 3%, 5%
```

Keep both inlet phases proportional, preserve a checkpoint after every
accepted level, and stop at the first growing end-of-step envelope or physical
gate failure. A Fluent-resident time profile may later reduce connection risk,
but it must be set and read back in Fluent 2024 R2 before use.

## Key scripts and outputs

| Role | File |
|---|---|
| Connection helper | `PyAnsys/src/pyansys_fluent/connection.py` |
| 07l preparation | `PyAnsys/scripts/setup/prepare_setup07l_hydrostatic_rest.py` |
| 07l qualification | `PyAnsys/scripts/setup/run_setup07l_hydrostatic_rest.py` |
| 07m pressure matrix | `PyAnsys/scripts/setup/run_setup07m_pressure_opening_campaign.py` |
| Opening extension | `PyAnsys/scripts/setup/run_setup07m_opening_extension.py` |
| Micro-ramp | `PyAnsys/scripts/setup/run_setup07m_micro_inlet_ramp.py` |
| 0.1% hold | `PyAnsys/scripts/setup/run_setup07m_micro_hold.py` |
| Progressive ramp | `PyAnsys/scripts/setup/run_setup07m_progressive_micro_ramp.py` |
| 1% hold | `PyAnsys/scripts/setup/run_setup07m_one_percent_hold.py` |
| One-factor inner sensitivity | `PyAnsys/scripts/setup/run_setup07m_inner_iteration_sensitivity.py` |
| Independent stage driver | `PyAnsys/scripts/setup/run_setup07m_progressive_ramp_stage.py` |

Primary evidence root:

```text
PyAnsys/output/split_inlet_resolved_brine_outlet_20260813/
brine620k_07m_pressure_opening_campaign_v1/
```

Important children:

- `campaign_manifest.json` and `matrix_summary.csv`;
- `matrix/<pressure_dt>/`;
- `opening_extension_10steps/`;
- `micro_inlet_hold_0p1pct_inner100/`;
- `progressive_micro_ramp_dt1e-7_inner100/`;
- `progressive_hold_1pct_dt1e-7_inner100_steps20/` — stale zero-step attempt.

Focused tests include:

```text
PyAnsys/tests/test_setup07l_hydrostatic_rest.py
PyAnsys/tests/test_setup07m_pressure_opening.py
```

## Missing physical information

The following remain `Missing` and prevent a plant-valid production boundary:

- downstream brine static pressure;
- downstream liquid-level datum;
- pipe length, diameter, elevation changes and fittings;
- valve/control resistance or pressure-flow curve;
- confirmed operating separator liquid level;
- operating data for brine discharge, separator pressure and level response.

The present pressure bracket can test numerical startup behavior only. Before
calling a full-flow result physical, obtain those data or explicitly model a
justified downstream pipe/loss/resistance and level-control condition.

## Claims that remain prohibited

Do not claim any of the following from setup 07m or the server-2 comparison:

- validated downstream brine pressure;
- stable full-feed operation or level control;
- operating-flow phase or mixture closure;
- separator efficiency or steam quality validation;
- mesh independence or GCI;
- DPM carryover, EWF behavior or deposition performance.

Safe wording is: **the pressure-opening response and low-flow startup are
internally consistent bounded diagnostics on the present mesh**.

## Documentation responsibilities for the next modelling run

After each executed branch, update:

1. `Setup report/07m-split-inlet-zero-feed-pressure-opening-and-inlet-ramp.md`;
2. `ResearchProject_wiki/wiki/progress/experiments.md`;
3. `ResearchProject_wiki/wiki/progress/current-status.md`;
4. `ResearchProject_wiki/wiki/progress/blockers.md` if blocked;
5. `ResearchProject_wiki/wiki/model/validation.md`;
6. `Setup report/order-dictionary.md` if branch identity or state changes;
7. `ResearchProject_wiki/wiki/log.md`.

Preserve every earlier case/data pair, transcript, manifest and unrelated
worktree change. Label every result `accepted diagnostic`, `diagnostic /
unresolved`, or `terminal diagnostic`.

## Further questions

1. Does the fixed 1% flow settle below the continuity gate with more physical
   steps, or is there a persistent residual floor?
2. If it does not settle, is the limiting factor inner-iteration count or time
   step size?
3. At what inlet fraction does the bounded pressure-opening branch first lose
   storage-aware closure or stable liquid inventory?
4. What real downstream boundary or resistance should replace the CFD-derived
   rest pressure for an operating calculation?
5. Once an operating carrier solution exists, does it remain stable over a
   physically meaningful residence-time window and across a time-step
   sensitivity?

## Successor evidence recorded on 23 August 2026

This historical 07m handoff has been superseded for physical continuation by
setup 07n; none of the 07m fields above was resumed. Setup 07n reconstructed an
exact `98,473`-cell whole-cell pool from the setup-07l case-only settings
carrier, relaxed the zero-feed closed pool through step 940 / `0.22271 s`, and
used that checksum-bound explicit/PISO pair for all solver comparisons.

The completed screen includes explicit timestep halving through `dt/8`, a
20-versus-100 inner-iteration comparison, cellwise maximum localization,
accepted zero-step implicit-VOF readback, implicit/PISO first- and second-order
Compressive, second-order Modified-HRIC, and explicit/plain-Coupled. All
completed physical branches passed their hard gates. Explicit timestep
independence and explicit-versus-implicit formulation independence did not
pass; the best implicit maximum velocity remains `6.831%` above explicit.
Plain Coupled reproduced PISO within `0.000063%` while costing `3.234x` as
much summed solve-step wall time, so PISO is retained for bounded diagnostic
work.

The authoritative common diagnostic parent is now:

- case: `brine620k_07n_a_closeddrain_meshselected_dt256em6_hold100_stage8_attempt1_20260823_additional_step100.cas.h5`, SHA-256
  `03383ac0e1674b7a2acd47fc65ca84033c907f960bc3a4ace912e4902ce6c7c9`;
- data: the same stem with `.dat.h5`, SHA-256
  `a5963dfada0754dd24685b699a65ac341d90b9ce0c3dda11879863eb9ff0772a`;
- scope: explicit/PISO closed-pool diagnostic comparisons only.

No implicit or Coupled endpoint is eligible as a parent. The next physical
question is no longer another solver swap: it is a separately gated constant-
level brine-outlet/control strategy with an emergent liquid seal. The main
blocker remains downstream pressure/head, pipe/valve resistance and operating
liquid-level evidence. Mesh convergence, full-flow performance, separator
efficiency, DPM and EWF remain prohibited claims.
