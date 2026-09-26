# Phase 7b E2 — Lower sink strength at fixed S40 geometry

## Authority and purpose

On 22 September 2026, after the supervisor meeting, Andy accepted the proposed
lower-sink-rate experiment and requested a handover for execution in a new
chat. This is a Phase 7b follow-up, separate from Shuhei's phases. The approved comparison is complete; [results](results.md) and the phase state own
its dispositions and current authority.

Question: does weakening the finite liquid sink at fixed S40 geometry improve
source-inclusive mass conservation and numerical stability while retaining
bounded liquid inventory and useful phase routing?

The hypothesis is source stiffness/coupling, not a demonstrated root cause.
The [G1 results](../results.md) show active removal but unacceptable closure,
nonstationarity and residuals. S40 is a diagnostic reference because it has
the smallest late imbalance among the completed cases, not because it is a
qualified model.

## Selected comparison

| ID | Collector | Tau, s | Role / order |
| --- | --- | ---: | --- |
| S40 baseline | Existing S40 | 0.0024095893 | Reuse completed G1 evidence; no automatic rerun |
| S40-T020 | Same S40 | 0.020 | First new fresh-start case |
| S40-T100 | Same S40 | 0.100 | Second new fresh-start case, after first disposition and analysis |

This packet makes the accepted proposal concrete: two weaker-source points,
up to 5,000 steady iterations per case. A larger tau means weaker removal at
the same liquid inventory (about 8.3 and 41.5 times weaker than the baseline).
These are coefficients in a steady source law, not transient timesteps.
Routine preparation and evidence recovery belong to phase-loop. No further
thickness sweep, numerical tuning, physical qualification or extension beyond
these caps is authorized by this packet.

## Parent, delta and invariants

Use the same clean N0 parent and fresh Hybrid initialization as the verified
[S40 setup](../s040-collector/setup.md). That document supplies the fixed
geometry, physical models, material properties, boundaries and solver
numerics. Its original fixed tau is replaced by the table above for E2 only.
The exact parent identity and live-state precautions are in [HANDOVER](../HANDOVER.md).
Use the original S40 manifest to verify the full reference and Hybrid options.

The S40 mask is `-1.4845837354660034 <= y <= -0.8827502412796020 m`, without
an x/z crop. It selects 41,258 cells and approximately 1.4681621275 m³ of
geometric fluid volume. It does not prescribe liquid inventory.

Change only tau in `S_l = -chi*rho_l*clip(alpha_l,0,1)/tau`. Preserve the
liquid-only mass sink, zero direct vapor sink, mixture momentum removal using
liquid velocity including slip, and shared k/epsilon removal. All accompanying
sources scale through the same changed `S_l`. Retain the original alpha
clipping and update interval. No new source cap, ramp, feedback controller or
Jacobian treatment is part of this comparison.

Remain steady, Python/PyFluent/native expressions only, Energy/DPM/EWF off,
full-feed split velocity inlets, physical brine outlet a wall, no pool patch,
and no requirement to maintain a standing pool. Each new child starts fresh;
neither the converged-looking tail of S40 nor the S100 recovery field is a
scientific parent for E2.

## Preparation and evidence contract

Parameterize the runner explicitly for tau and case identity, preserving the
old baseline default and old manifests. Verify the input, generated definition,
source hooks, setup parity and save/reopen before solving. The runner is now
parameterized and verified for S40-T020; [results](results.md) records that
proof and the recovery of the historical [HANDOVER](../HANDOVER.md) issues.
Repeat the live checks for S40-T100. Keep all paths unique to each new child.

Retain the existing every-iteration instrumentation: vessel/collector/above
liquid volume and mass; native applied and current-field source; all signed
phase and mixture boundary fluxes; source-inclusive closure; exact-face gross
liquid delivery/escape; seven residuals; pressure and maximum mixture speed.
Use the native applied source exactly once in closure. Measure its update lag
again rather than assuming the baseline audit transfers automatically.

Save matching initial/prepared, N50, every-500 and final case/data pairs.
Startup solve iterations count toward the 5,000 cap. Retain local and PC
records, complete native transcripts, recorder error status and checkpoint
readbacks. Preserve endpoints before replacement. API interruptions require
actual-progress reconciliation before retrying; numerical failures require
explicit partial evidence and recovery artifacts, not a fictitious N5000.

Record initial and endpoint horizontal planes at y=0.5, 1.5, 3 and 5 m using
the existing ten-field exporter. Also retain full-height x=0 and z=0 liquid-
fraction views as in the meeting report. Compare matching stages on common
scales. S100's old recovery fields remain labelled N4000.

## Analysis and decision gate G2

Use the same [G1 measurement and analysis conventions](../design.md): complete
N4001–4500 and N4501–5000 windows; full raw histories; mean, extrema, standard
deviation and iteration slope. Partial runs receive explicitly partial
statistics, never substitute late windows.

Report whether each phase and mixture mean absolute closure is within 1% of
measured feed, whole-liquid window means change by at most 1% of the larger
mean (1e-6 m³ floor), and all seven residuals stay at or below 1e-3 throughout
the final window. Retain excursions and spatial evidence; these are discovery
indicators, not physical validation.

Compare both new cases with the existing S40 baseline. Possible findings:

- Better balance/residuals with bounded inventory supports investigating
  source-strength sensitivity further; it does not independently qualify the model.
- Better numerical behaviour but continuing liquid buildup shows a stability/
  removal trade-off; a lower reported source by itself is not a pass.
- Persistent imbalance or divergence across strengths leaves the broader
  source/pressure/turbulence coupling unresolved; tau alone is insufficient
  within this tested range and horizon.

G2 returns the three-point comparison once both new cases have a verified
horizon or an explicit failure disposition and recovered evidence. Scientific
disappointment alone is not an early-stop rule. If one case fails numerically,
preserve it and proceed to the next approved fresh child once session/evidence
integrity is restored. New physics, numerics, coefficient points, horizon
extensions or qualification require a further scientific decision.
