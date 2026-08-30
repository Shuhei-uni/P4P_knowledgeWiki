# Phase 06 / Stage 01 — level observable and outlet response discovery

## Status and stage question

**Capability-gated; runnable discovery screen selected.** On 2026-08-30 the
three Fluent 2025 R2 endpoints again became reachable, the canonical paired
F11 artifact was visible through OneDrive on all three, and the loaded
full-geometry cases exposed the needed phase-aware report topology. No
Phase-06 case has yet been modified or solved.

**Stage question.** Before testing a controlled brine-pool operating point,
can the F11-derived full-geometry model provide a valid, repeatable pool-level
observable and an unambiguous phase-aware outlet-flow basis on which competing
brine-outlet response representations can be screened?

This reduces a prerequisite uncertainty in the fixed Phase-6 question. It does
not itself claim that a controller, valve relation, or target level has already
been represented.

## Why this is the first stage

The human deliberately wants broad testing first and deeper testing only after
the evidence selects a direction. A rough discussion of inlet and brine flow
magnitudes is therefore retained only as context, not as a target for this
stage. The existing Stage-5 history nevertheless shows why this stage must be
phase-aware: liquid-to-brine flow, liquid carryover to the steam outlet, and
total mixture flow at the brine outlet are materially different quantities.
This stage makes those bases explicit before any apparent outlet improvement is
interpreted as level control.

## Discovery strategy, pending capability gates

The campaign is `NEW`, not a repetition of the Stage-5 fixed-pressure sweep:
each runnable child must carry a new pool-level observable and a declared
outlet-response relation. The exact Fluent boundary type is intentionally not
chosen before live inspection proves what can be configured and read back in
this Fluent version/case fingerprint.

| Candidate | Intentional delta from verified F11 | Learning purpose | Status |
|---|---|---|---|
| `P6-S1-R` | exact paired F11 reference under its read-back pressure outlet; retain the existing phase-flow and lower-region **liquid-mass** inventory reports, but redirect every file-backed history to a Stage-01 run root | establishes whether the two existing lower-region inventory measures are repeatable, useful precursors to a pool proxy | selected |
| `P6-S1-O` | same F11 parent but replace only `brineoutlet` with an outlet-vent resistance boundary at the same ambient pressure; use a deliberately non-plant-calibrated screening coefficient | tests an outlet representation with a pressure-loss equation, rather than another fixed-pressure point | selected |
| `P6-S1-B` | same F11 parent but replace only `brineoutlet` with a phase-specific mass-flow outlet whose liquid command is derived from the reference child readback, never from conversational flow orientation | bold numerical-architecture probe: tests whether an explicitly imposed liquid exit changes the pool proxies/solver path materially; it is not claimed to model a valve or level controller | **deferred**: Fluent documents this representation as strictly outward-flow-only, so it cannot be built until the reference smoke history proves that prerequisite |

The reference and outlet-vent lanes will receive a 50-iteration smoke test then
a 500-iteration attached discovery run if the smoke test passes. The bold
mass-flow lane remains a conditional feasibility probe rather than a committed
third run. The outlet-vent coefficient is
a log-scale capability probe, not an inferred valve coefficient. The
phase-specific mass-flow command is a reference-derived feasibility condition,
not a plant target, and its use is constrained by Fluent's outflow-only
limitation. A completed short screen is discovery evidence only; it does not
establish plant-level control fidelity.

## Required capability gates

1. **Level observable.** Define a geometry-specific liquid-volume/fraction
   calculation that maps to an equivalent pool elevation at the relevant
   physical measurement location. It must retain units, phase definition,
   region bounds, and the mapping/assumptions used.
2. **Outlet semantics.** Inspect the active Fluent boundary tree and
   version-matched manual to establish which outlet-response representations
   are available and which quantity each actually controls. Do not assume that
   a mixture mass-flow field represents liquid-only brine flow.
3. **Readback.** Any candidate outlet relation must survive save/reopen and
   expose a readback sufficient to distinguish it from a fixed pressure outlet.
4. **Evidence.** File-backed histories for level proxy, phase liquid inlet and
   outlet flows, mixture flows, full/pool-region imbalance, brine boundary
   state/command, and scaled residuals must exist before a discovery solve.
5. **Bold-boundary safety.** The mass-flow candidate must prove all flow is
   leaving `brineoutlet` during smoke testing and that phase-specific command
   leaves survive save/reopen. If that condition fails, it is recorded as an
   unavailable representation, not forced through a mixed-flow boundary.

## Core discovery figure plan

| Figure | Question | Plot | X-axis | Y-axis / series | Data source and interpretation use |
|---|---|---|---|---|---|
| `F1` — lower-region inventory response | Does the candidate outlet condition change the two lower-region phase-2 liquid-mass inventories consistently, or merely alter a global inventory? | raw history, matched cases | native iteration | explicitly labelled `y≤0.10 m` and `y≤0.30 m` liquid-mass inventories; no level target/band is displayed because neither instrument mapping nor a durable liquid-volume history is available | inherited file-backed mass reports; a necessary but insufficient precursor to a level observable |
| `F2` — liquid control balance | Is apparent level behaviour consistent with phase-resolved liquid flows? | matched histories | native iteration | liquid inlet, liquid-to-brine, liquid-to-steam, and derived net liquid rate; kg/s with signs | report files; distinguishes true phase balance from a mixture-flow comparison |
| `F3` — numerical/output behaviour | Is the apparent response accompanied by bounded solver and outlet histories? | aligned residual and boundary-command histories | native iteration | scaled residuals and declared outlet command/state | residual monitors plus boundary history; bounds interpretation, does not replace `F1` |

## Working assumptions and limits

| State | Item |
|---|---|
| human context | rough inlet/outlet magnitudes are useful orientation only; they are not a fixed Stage-01 target or acceptance criterion |
| materially challenged | a fixed pressure outlet adequately represents the real level-controlled brine discharge |
| questioned | the retained Mixture field can yield a physically meaningful level proxy at the actual instrument location; custom liquid-volume report files were not retained through the available settings path |
| accepted for now | the F11 full geometry is a suitable first platform for boundary/observable discovery; this does not establish its complete plant fidelity |

## Return to Phase 6 when

- the actual control mechanism/setpoint information is unavailable and a
  provisional target would become a fabricated plant claim;
- Fluent cannot represent and prove a phase-aware outlet response in the
  retained model without an unapproved configuration path;
- no defensible level observable can be constructed from the current geometry
  and phase field; or
- the discovery evidence shows that a literal time-dependent controller/model
  is required before the fixed Phase-6 question can be answered.

## Sources

- [Phase-6 fixed question and boundaries](../setup.md)
- [Phase-6 carried evidence](../results.md)
- [03A Stage-5 fixed-pressure results](../../phase-05-full-geometry-v2/full-geometry-03a-mixture-08b-parity-baseline/stage-05/results.md)
