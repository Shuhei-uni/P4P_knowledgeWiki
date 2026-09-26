# New-chat handover — Phase 7b weaker-sink experiment

Current frontier: **G5 complete; API restored and E6 recovery in preparation**, with no qualified case. See [investigation results](convergence-investigation/results.md) and [E6 setup](convergence-investigation/coupled-nphase/setup.md). Machine state owns live progress.

**Latest authority (2026-09-22):** Continue the autonomous investigation after G5. E6 is selected under its N-phase-only setup; read phase-state and run-paths before any operation. Preserve E5; one controller only. The existing heartbeat stays active. Earlier E2–E5 instructions below are historical and must not relaunch completed cases.

## Start here

Andy approved the proposed lower-sink-rate follow-up and will start a new chat.
Use the repository **phase-loop** workflow to prepare and execute the selected
[lower-strength experiment](lower-sink-rate/setup.md): fixed S40 geometry,
tau 0.02 s first, then 0.10 s, each fresh-start and capped at 5,000 steady
iterations. The old S40 tau=0.0024095893 s run is the comparison baseline.
No new solve or solver-code modification was performed while writing this
handover. Prepare the verified runner before launching; another permission
round-trip for the already accepted experiment is unnecessary.

Read in order:

1. `Project/index.md` for separation from Shuhei's work.
2. [CONTEXT](CONTEXT.md) and [phase state](phase-state.yaml) for current authority.
3. [E2 setup](lower-sink-rate/setup.md) for the runnable scientific contract.
4. [G1 results](results.md) and [S40 results](s040-collector/results.md) for the evidence.
5. [S40 setup](s040-collector/setup.md) and the original S40 manifest for invariants.

Use `pyansys-workflow` for Fluent implementation, `cfd-numerical-analysis` for
evidence, and `report-writing` for presentation. Repair routine technical
failures inside scope. Keep Project interpretation, PyAnsys executable/data
records and reusable CFD_wiki knowledge in their respective owners.

## Why we are doing this

The goal is a balanced, numerically stable **steady** full-geometry separator
with ideal lower liquid collection and useful separation above it. Explicit
brine-pool/outlet modelling became too complicated and went transient; Andy
wants to avoid that route. A standing pool is not required. The physical
brine-outlet face is a wall; a liquid-only volumetric sink supplies removal.

Phase 7b is Andy's full-geometry lane, separate from Shuhei's Phase 7/7.1A.
The inlet is split into pure-liquid and pure-vapor faces at the same normal
velocity. The reference full-feed condition is associated with 1600 kJ/kg,
but Energy is off; this is not an enthalpy-controlled new boundary condition.
Do not import the historical 0.05%-flow transient brine study's settings.

G1 varied collector height at one fixed tau. The new question is whether that
sink was too aggressive for the coupled numerical solution. This is a testable
explanation, not an established cause. “Lower sink rate” means **larger tau**,
not a smaller timestep or switching to transient.

## What G1 established

- S20/S40/S60/S80 reached N5000 with complete scalar, exact-face flux and all-
  equation residual histories plus initial/final fields and paired checkpoints.
- Late mean liquid inventory decreased from 0.957893 m³ (S20) to 0.646800 m³
  (S80), but closure and residual quality did not improve monotonically.
- Late liquid mean absolute imbalance was 336.821%, 252.603%, 502.533%,
  343.609% of feed respectively. Inventory window means changed by about
  10–16%. Continuity, k, epsilon and liquid-fraction residuals failed; three
  momentum residuals passed the declared late-window criterion.
- S100 failed at attempted N4183 with epsilon AMG divergence and floating-point
  exceptions. N1–4182 records are complete. Finite terminal runaway values
  are not physical results. The failure has not been replayed to establish
  reproducibility or isolate its cause.
- Liquid reaches the collector and the source is active. Low collector
  inventory does not establish transport starvation. Most liquid inventory
  remains above it; liquid-rich outer regions persist. None is a qualified
  steady model or a validated separator-efficiency prediction.

The [meeting PDF and figures](meeting-report.md) and [speaker notes](meeting-speaker-notes.md)
explain the scientific story. S100 fields are N4000 recovery snapshots;
other field comparisons are N5000. Historical 0.1/0.02/adaptive-tau studies
used a different mesh and collector arrangement and cannot substitute for E2.

## Exact baseline and evidence locations

All local paths below are relative to `/Users/andy/Desktop/P4P/P4P_shared`.

| Case | Local run under `PyAnsys/output/` | Disposition |
| --- | --- | --- |
| S20 | `p7b-s020-20260920T221831Z` | N5000 |
| S40 | `p7b-s040-20260921T013001Z` | N5000; E2 comparison baseline |
| S60 | `p7b-s060-resume-20260921T113238Z` | N5000; stitched verified continuation |
| S80 | `p7b-s080-20260921T130348Z` | N5000 |
| S100 | `p7b-s100-20260921T160825Z` | Numerical failure at attempted4183 |

Each contains `manifest.json`, native `history-*.out`, `collector-flux.jsonl`,
`solve.trn` and `analysis/summary.json`; final/recovery field receipts are linked
from its Project result. S60's original prefix is in
`p7b-s060-20260921T043132Z`; its continuation audit verifies exact prefix
preservation across the user's Wi-Fi pause. Keep that history intact.

Comparison: `PyAnsys/output/phase07b-g1/comparison.json` and G1 PNGs.
Meeting geometry/axial exports: `PyAnsys/output/phase07b-meeting-20260922/`.
Generated output is largely ignored by Git and may exist only on this Mac;
verify availability before assuming a new checkout contains it. Working-tree
changes from this campaign remain uncommitted; preserve them. No commit or
push was requested in this handover turn.

## Last verified PC state — recheck before mutation

All PC operations must use the **Fluent API**. No SSH, remote shell or assumed
local Windows filesystem access. Credentials/configuration are in
`PyAnsys/.env`; load them through the existing connection helper without
printing secrets. The Extreme SSD was not mounted during report preparation;
PC paths were available through Fluent.

Last verified endpoint: configured server-1, `10.104.145.174:60097`, Fluent
2025 R2/settings252, PyFluent0.39.0, 16 ranks. These are last-known facts,
not a guarantee of current connectivity, version or ownership. Resolve current
configuration from the helper and inspect the live session before acting.

PC phase root:
`C:/Users/qtra338/P4P/experiments/phase-07b-full-geometry-liquid-removal`.

**Fresh scientific parent:** under `case-data/`,
`p7b-clean-initial-20260912T080713Z.cas.h5` and matching `.dat.h5`.
Rebuild S40 and apply the same fresh Hybrid options as the original S40
manifest. Do not continue the old S40 endpoint or S100 checkpoint as E2.

**Last live state:** S100 recovery N4000, restored after report extraction:
`case-data/p7b-s100-20260921T160825Z-n04000.cas.h5` plus matching data.
The latest receipt is
`PyAnsys/output/phase07b-meeting-20260922/extraction.json`:
`COMPLETE_NO_SOLVE_OR_CHECKPOINT_OVERWRITE`, restored N4000, zero new iterations.
No controller or iteration callback was left running by this task.

**Preserved failed diagnostic state:**
`case-data/p7b-s100-failed-n04183-20260921T185920Z.cas.h5` plus matching data.
This is diverged diagnostic evidence, not a valid parent. Original completed
endpoints and N4000 recovery pair remain valuable. All server case/data
storage is LOCAL_ONLY; no independent backup destination is configured.

The old `phase-7b-run-check-ins` automation is paused following G1 and targets
this old chat. Keep it paused. If periodic supervision is continued in the new
chat, configure it for the new active task and E2 envelope, with one controller
and no duplicate clients. Scheduling does not imply that a solve is running.

## Implementation lessons that must carry over

- The validated liquid velocity syntax is `Velocity.x(phase="phase-2")`
  (likewise y/z). The alternative component ordering caused a reproduced
  Cortex fault. Shared `TurbulentKineticEnergyk` and
  `TurbulenceDissipationRate` expressions are unqualified.
- Maximum-speed reports require explicit mixture context:
  `VelocityMagnitude(phase="mixture")`. Missing phase context previously
  prevented solving. Read back and compute reports before the scientific run.
- Native applied removal at N matched recomputed removal at N−1. Closure
  uses individually signed boundary flows plus the signed **native applied**
  mass source once. Current-alpha expressions are a different diagnostic.
  Fluent Net reports may already contain sources; never add blindly.
- A steady-iteration inventory slope is not a physical storage rate. Early
  low residuals or reaching the command cap do not establish convergence.
- The source entries have no assigned explicit derivative/Jacobian slot in
  the verified implementation. Do not silently change linearization for a
  tau-only comparison or claim implicit treatment is established.
- Exact collector fluxes use phase-2 `SV_FLUX` on uniquely owned, oriented
  collector interfaces, recorded synchronously at every completed iteration
  to Mac and PC. Preserve/reconcile duplicate-event handling and recorder
  manifests. A recorder failure can leave the solver advancing.
- Reconcile uncertain API outcomes via saved receipts, transcripts and
  `P7bGlobalIteration`. A timeout is not proof that a command did not execute.
  A fatal solve can return control before the requested block finishes.
- Attach with session preservation. Never call `solver.exit()` or introduce
  automatic session shutdown. Preserve valuable state before replacement;
  verify ownership before any recovery that could affect another user's work.
- Transcript paths must be unique: starting a local transcript at an existing
  path can overwrite it. Treat `raw/` and old generated evidence as immutable.

## Concrete preparation work for the new chat

1. Reconcile the configured endpoint, counter, named source definitions, live
   case identity and existence of the saved pair. If another job now owns the
   session, resolve that before replacing it. Do not blindly trust last-state
   notes or start a second controller.
2. Adapt the existing runner rather than launching it unchanged:
   `PyAnsys/scripts/setup/run_phase07b_screen.py` calls
   `prepare_phase07b_collector.definitions(percent)`, whose sink denominator
   is hard-coded to 0.0024095893 s. Add an explicit finite positive tau input,
   a recorded tau field and unique strength-specific run IDs. Preserve the
   baseline default and verify mass/momentum/k/epsilon share the changed sink.
3. Fix the predecessor safety gate deliberately: `--previous-manifest`
   currently assumes a completed N5000 predecessor. The actual last known
   live case is the verified S100 recovery N4000 after a failed run. Accept a
   validated preserved-state receipt and matching live readback; do not
   disable preservation checks or falsely mark the old manifest complete.
4. Build each new case from the clean N0 reference, compare settings and
   Hybrid options to the original S40 manifest, prove the unchanged S40 mask
   and interface mapping, then save/reopen and verify the actual source,
   reports and counters. Record implementation checks before solve.
5. Run the ordered E2 cases and preserve the evidence specified by
   [setup](lower-sink-rate/setup.md). Use actual global iteration to maintain
   the cap. Analyse the first case before advancing. Routine API/instrumentation
   recovery remains in scope; scientific tuning beyond tau does not.
6. Return G2: baseline plus two weaker-source dispositions, full history and
   spatial comparison, numerical indicators, competing explanations and the
   next supported decision. No automatic qualification.

Useful proven modules: `PyAnsys/src/pyansys_fluent/phase07b_flux_monitor.py`,
`PyAnsys/scripts/inspection/export_phase07b_sections.py`,
`PyAnsys/scripts/analysis/analyze_phase07b_screen.py`,
`PyAnsys/scripts/analysis/plot_phase07b_sections.py` and the meeting export/
plot scripts. The G1 comparison script hard-codes old run IDs; parameterize or
create a clearly separate E2 analysis without overwriting G1.

Use `PyAnsys/.venv/bin/python`. The existing connection helper is
`prepare_phase07b_collector.connect(server_id=1, start_transcript=False,
tcp_timeout_seconds=5)`. Respect bounded API deadlines and reacquire Settings
objects after case reloads. These pointers are not a ready launch command:
the runner must first pass the E2 preparation checks above.
