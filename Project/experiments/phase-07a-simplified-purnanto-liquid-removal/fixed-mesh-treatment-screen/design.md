# Phase 07 fixed-mesh treatment-screen design

## Design authority

| Field | Contract |
| --- | --- |
| Lifecycle | `discovery` |
| Context | [`../CONTEXT.md`](../CONTEXT.md) |
| Gate | `G1 — Fixed-mesh liquid-removal screen` |
| Reference | [`P7-E0-REF`](../e0-08b-corrected-reference/setup.md) |
| Approved families | `E1-PO`, `E2-OV`, `E3-MFO`, `E4-ADAPT`, `E5-PSINK` |
| Human approval | Mechanism ladder, three initial settings per family, bounded fourth-point rules, 500-iteration screens, and conditional 2,000-iteration continuations approved on 2026-09-08 |
| Claim class | Comparative numerical mechanism discovery; not physical outlet validation or steady-state qualification |

## Discovery question

> Across multiple settings of each human-approved fixed-mesh treatment, which
> mechanisms and parameter regions materially reduce the E0 liquid-inventory
> buildup or mixture imbalance without unacceptable vapor removal or loss of
> numerical interpretability?

The campaign is designed to distinguish a poor mechanism from a poor single
setting. No family is judged from one simulation, and a 500-iteration endpoint
cannot establish long-term boundedness.

## Fixed scientific context

Every child preserves E0's exact:

- `Separator-purnanto342k.msh.h5` mesh and all zone topology;
- continuous Mixture/RNG model, materials, phase mapping, gravity, operating
  conditions, inlets, steam outlet, and corrected `0.875936 m` steam-outlet
  turbulence/backflow hydraulic diameter;
- solver methods, controls, initialization basis, report definitions, sign
  convention, residual capture, and checkpoint rules; and
- one-way/no-carrier-source DPM isolation.

Only the named bottom treatment and its one approved control value change
within a family. Case-specific solver tuning is prohibited.

## Prior-experiment collision check

| Family | Class | Relevant retained evidence | Nonredundant Phase-07 delta |
| --- | --- | --- | --- |
| E1 pressure outlet | `PARTIAL REPEAT` | Phase-05 full geometry: `1.160 MPa` completed 500; `1.200/1.240 MPa` ended in FPE. | Truncated Phase-07 mesh, no initialized full-geometry pool, corrected outlet, complete total-domain inventory, and matched E0 reference. |
| E2 outlet vent | `PARTIAL REPEAT` | Phase-05: `K=0` completed but over-drained; `K=10/100` failed late; `K=3/7` were planned but not executed. | `K=0/3/7` on the accepted truncated mesh with complete inventory and vapor-loss evidence. |
| E3 prescribed withdrawal | `PARTIAL REPEAT` | Phase-05 mass-flow outlets at about `58/117/234 kg/s` all failed on full geometry. | Includes gentler `29.23 kg/s`, different geometry/initial state, and hard proof of commanded versus realized phase withdrawal. |
| E4 adaptive withdrawal | `NEW` for this geometry/actuator law | Phase-06 used bounded pressure feedback, not normalized adaptive mass withdrawal on the truncated bottom. | Shared E0-derived target/normalization and controlled comparison against E3 fixed withdrawal. |
| E5 phase-selective sink | `NEW` | No retained Project case applies the approved liquid-only bottom-region source with full source accounting. | Explicit liquid-only actuator, fixed region, momentum-consistent removal, and matched controller law against E4. |

No family is `REDUNDANT`. Historical failures constrain the design and claim
limits but do not answer the Phase-07 matched-mesh question.

## Question-experiment challenge

| Criterion | Score | Assessment |
| --- | ---: | --- |
| Scientific value | `4/4` | The family/settings structure can distinguish passive, resistive, prescribed, adaptive-boundary, and phase-selective removal limitations. |
| Evidence and interpretability | `4/4` | One mesh/reference, per-iteration inventory/phase balance, vapor loss, commands, residuals, and predeclared figures make both success and failure informative. |
| Cost-effectiveness | `3/4` | Fifteen initial children are substantial, but they implement the human-required three-setting rule across five genuinely different approved families; short screens and bounded continuations control cost. |

Strongest surviving criticisms:

- **Important:** E1–E3 begin from E0 initialization, while adaptive E4/E5
  activate from E0 iteration 500. Cross-family plots must use treatment-active
  iteration and the matched E0 window; raw native coordinates alone are not a
  fair comparison.
- **Important:** steady solver iteration is not physical time. Inventory slopes
  in `[kg/iteration]` describe numerical progression and cannot be reported as
  physical accumulation rates.
- **Important:** Fluent may not support the intended phase-specific E3/E4
  outlet command. Live capability/readback failure blocks those families; it
  does not authorize a silent total-mixture substitute.
- **Important:** E5's source must remove continuous-liquid mass and associated
  momentum consistently and expose the exact realized source. If this cannot
  be implemented and verified, E5 is blocked rather than simplified after the
  fact.
- **Important:** no numerical steam-loss threshold exists. Clear domination is
  rankable; ambiguous liquid-improvement/vapor-loss tradeoffs return to the
  human under G1.
- **Minor:** family continuations selected after 500 iterations are discovery
  depth extensions, not hypothesis qualification.

Disposition: viable for independent `DISCOVERY_DESIGN` gate review. No solve
is authorized by this document.

## Common execution structure

### E0 prerequisite

E0 must pass its setup, save/reopen, smoke, execution, and evidence requirements
through at least iteration 1,000 before any adaptive case can be normalized.
Its full 2,000 iterations and core analysis remain required for the campaign.

### Non-adaptive children

- Parent: exact E0 initialized iteration-0 case/data pair.
- Initial horizon: 500 iterations, including a 50-iteration smoke segment.
- Primary short-screen window: iterations 401–500.
- Checkpoints: start, 50, 250, and 500.
- Conditional continuation: selected valid family member continues from its
  own 500 checkpoint for 1,500 more iterations, reaching 2,000 total.
- Continuation comparison windows: 1,000–1,500 and 1,500–2,000.

### Adaptive children

- Parent: exact E0 iteration-500 case/data pair.
- Controller-active coordinate resets to 0 in derived analysis while native
  Fluent coordinates remain preserved.
- Initial horizon: 500 controller-active iterations, including a 50-iteration
  adaptive smoke segment.
- Matched E0 control: E0 iterations 500–1,000.
- Primary short-screen window: controller-active iterations 401–500.
- Checkpoints: activation, active 50, 250, and 500.
- Conditional continuation: selected valid family member receives 1,500 more
  controller-active iterations, reaching 2,000 active iterations.

Every child is independent. A failed case preserves its last valid state,
transcript, histories, commands, and failure evidence; it is never rescued by
family-specific numerical changes.

## Approved initial matrix

### E1-PO — pressure outlet

Keep the steam outlet at E0 state. Change `bottom` to a pressure outlet with a
liquid-dominant backflow phase state, parent-consistent turbulence/backflow
form, and the declared pressure only.

| Setup ID | Bottom gauge pressure | Purpose |
| --- | ---: | --- |
| `P7-E1-PO-P1120` | `1.120 MPa` | pressure-equal passive anchor |
| `P7-E1-PO-P1160` | `1.160 MPa` | intermediate backpressure |
| `P7-E1-PO-P1200` | `1.200 MPa` | prior full-geometry failure-edge context |

Conditional fourth: `1.140 MPa` for a low interval, `1.180 MPa` for a
`1.160`-valid/`1.200`-invalid transition, or at most `1.240 MPa` for a valid
unresolved upper edge. Only one may activate.

### E2-OV — outlet vent

Change `bottom` to an outlet vent with `1.120 MPa` gauge discharge pressure,
constant loss coefficient, and `function_of = normal-velocity`. Use the same
liquid-dominant backflow and turbulence basis as E1 where the formulation
exposes them.

| Setup ID | Loss coefficient | Purpose |
| --- | ---: | --- |
| `P7-E2-OV-K000` | `K=0` | zero-added-resistance anchor; compare with E1 P1120 |
| `P7-E2-OV-K003` | `K=3` | moderate resistance |
| `P7-E2-OV-K007` | `K=7` | upper initial resistance below the prior `K=10` failure context |

Conditional fourth: `K=1`, `K=5`, or at most `K=10` under the exact G1
branches in `CONTEXT.md`.

### E3-MFO — prescribed withdrawal

Change `bottom` to the intended phase-specific prescribed liquid-withdrawal
form, with nominal vapor target zero. This family cannot run until live Fluent
capability inspection proves that the command, phase intention, and realized
phase split can be read back and monitored.

| Setup ID | Intended liquid withdrawal | Fraction of nominal liquid inlet |
| --- | ---: | ---: |
| `P7-E3-MFO-Q025` | `29.23 kg/s` | `25%` |
| `P7-E3-MFO-Q050` | `58.46 kg/s` | `50%` |
| `P7-E3-MFO-Q100` | `116.92 kg/s` | `100%` |

Conditional fourth: `14.615`, `87.69`, or at most `146.15 kg/s` under the
exact G1 branches in `CONTEXT.md`.

## Shared adaptive law

From the valid E0 history define:

```text
M*    = E0 total continuous-liquid mass at native iteration 500
ΔMref = E0 total continuous-liquid mass at iteration 1,000 minus M*
e     = max(0, (Mcurrent - M*) / ΔMref)
u     = clamp(G × 116.92 kg/s × e, 0, 146.15 kg/s)
```

`ΔMref` must be positive, finite, based on complete valid reports, and large
enough to avoid noise-dominated normalization. Otherwise both adaptive
families return to the human. Update `u` every 50 controller-active iterations
and hold it constant between updates.

Both adaptive families record at every update: native and active iteration,
`Mcurrent`, `M*`, `ΔMref`, normalized error, requested command, clamped command,
saturation flag, realized liquid removal, realized vapor removal, and all
phase/mixture balances.

### E4-ADAPT — adaptive prescribed withdrawal

Use the proven E3 outlet actuator and vary only `G`.

| Setup ID | Gain | Command at `e=1` before cap |
| --- | ---: | ---: |
| `P7-E4-ADAPT-G025` | `0.25` | `29.23 kg/s` |
| `P7-E4-ADAPT-G050` | `0.50` | `58.46 kg/s` |
| `P7-E4-ADAPT-G100` | `1.00` | `116.92 kg/s` |

Conditional fourth: `G=0.125`, `0.75`, or at most `1.50` under the exact G1
branches in `CONTEXT.md`.

### E5-PSINK — adaptive phase-selective sink

Create one frozen cell register containing only `separator-purnanto` fluid
cells whose centroids satisfy `0 ≤ y ≤ 0.10 m`. Record exact cell IDs, cell
count, geometric volume, and liquid mass at activation. Reuse the identical
register in every E5 child.

Distribute command `u` across registered cells in proportion to their local
continuous-liquid mass. Apply zero direct vapor mass source. Remove associated
continuous-liquid momentum consistently with mass removal and report the exact
integrated mass and momentum sources at every controller update. A requested
command is not evidence of realized removal.

| Setup ID | Gain | Command at `e=1` before cap |
| --- | ---: | ---: |
| `P7-E5-PSINK-G025` | `0.25` | `29.23 kg/s` |
| `P7-E5-PSINK-G050` | `0.50` | `58.46 kg/s` |
| `P7-E5-PSINK-G100` | `1.00` | `116.92 kg/s` |

Conditional fourth: `G=0.125`, `0.75`, or at most `1.50` under the exact G1
branches in `CONTEXT.md`.

## Conditional fourth and continuation selection

A family must complete or terminally classify all three initial children
before a fourth point or continuation is selected.

The conditional fourth is used only when:

- the best valid response is at an initial range edge;
- adjacent settings bracket valid/invalid or useful/unacceptable behavior;
  or
- a material non-monotonic response needs the one pre-bounded discriminator.

The fourth selection must match a named `CONTEXT.md` branch exactly. More than
one plausible fourth branch, a need to exceed the approved bound, or an
unlisted setting returns `HUMAN_REQUIRED`.

At most one valid member per family continues to 2,000 iterations. Rank using:

1. setup/execution validity and numerical credibility;
2. persistent reduction in liquid-inventory buildup or liquid/mixture net
   imbalance relative to its matched E0 window;
3. lower realized bottom vapor loss, with near-zero strongly preferred;
4. predominantly liquid removal and interpretable command/response;
5. absence of destabilizing reversal, saturation, oscillation, or source
   inconsistency; and
6. persistence rather than a favorable final endpoint.

If liquid improvement and vapor loss create a material tradeoff with no clear
dominant case, selection returns to the human.

## Required common evidence

Every child inherits the complete E0 hard report package and adds:

- exact bottom boundary/source state and control-value readback;
- bottom liquid, vapor, and mixture flux or integrated source histories;
- command versus realized removal;
- normalized bottom vapor loss relative to `80.69 kg/s`;
- total continuous-liquid mass and valid volume histories;
- liquid, vapor, and mixture net-rate/imbalance histories;
- native scaled residuals and complete transcript;
- warnings, reversed-flow evidence, limiting, FPE, divergence, and last-valid
  coordinate where applicable;
- prepared save/reopen and smoke proof;
- exact checkpoint/final artifact identities; and
- family-relative and E0-relative final-window statistics.

E2 also records outlet pressure drop and normal velocity. E4/E5 record every
controller update. E5 additionally records selected-region identity and
integrated liquid mass/momentum sources.

## Core figure contract

### F1 — Liquid-inventory response by family

- **Question:** Which settings materially change liquid-inventory progression
  relative to the matched E0 window?
- **Plot:** one aligned panel per family, raw total liquid mass versus
  treatment-active iteration, with matched E0 and all three/four settings.
- **Reduction:** final-100 slope for 500-iteration screens; adjacent final-500
  slopes for continued cases; raw histories remain visible.
- **Units:** liquid mass `[kg]`, slope `[kg/iteration]`.
- **Data source:** mandatory file-backed inventory reports.

### F2 — Liquid-improvement versus vapor-loss tradeoff

- **Question:** Is reduced buildup achieved mainly through useful liquid
  removal or unacceptable vapor loss?
- **Plot:** setting-response curves and/or scatter of E0-relative liquid-slope
  reduction against normalized bottom vapor loss, with family and validity
  encoded distinctly.
- **Reduction:** identical declared final windows; failed cases shown only to
  their last valid coordinate and never as equivalent endpoints.
- **Units:** slope change `[kg/iteration]`; vapor loss fraction `[-]` and
  `[kg/s]`.
- **Data source:** inventory, bottom phase flux/source, and command histories.

### F3 — Phase balance and numerical adequacy

- **Question:** Are apparent improvements consistent with phase conservation
  and credible numerical behavior?
- **Plot:** family panels of liquid/mixture net rate and log-scaled residuals;
  terminal failures and last-valid coordinates marked.
- **Reduction:** raw histories and common final-window mean/range.
- **Units:** balance `[kg/s]`, normalized imbalance `[-]`, scaled residual `[-]`.
- **Data source:** pre-run phase reports and durable residual transcript/file.

### F4 — Adaptive command/response

- **Question:** Do E4/E5 respond smoothly and effectively, or mainly saturate,
  cycle, or fail to realize the requested removal?
- **Plot:** aligned histories of normalized inventory error, requested and
  realized removal, saturation, liquid inventory, and vapor removal for all
  gains.
- **X-axis:** controller-active iteration, with native coordinates retained in
  the source table.
- **Data source:** mandatory 50-iteration controller-update log and continuous
  report histories.

## Gate outcomes and limits

- **Invalid:** missing/unproven capability, setup drift, report failure,
  save/reopen failure, smoke failure, source-accounting failure, or unmatched
  comparison. Repair the same approved child only.
- **Rejected family/setting:** no meaningful improvement, worse behavior,
  numerical failure, unaccounted removal, or vapor-dominated improvement.
- **Diagnostic improvement:** persistent improvement without enough depth or
  steam-loss clarity for a bounded-state hypothesis.
- **Qualification candidate:** a named continued setup approaches stable small
  liquid/mixture imbalance with predominantly liquid removal, low vapor loss,
  and credible numerical histories. This permits only a separately verified
  hypothesis-definition/design path.
- **Human return:** ambiguous tradeoff, unlisted fourth point, missing phase-
  specific capability, invalid adaptive normalization, need to change mesh or
  controller form, or no family clearly deserving continuation.

Discovery cannot establish physical drainage fidelity, a real pool level,
plant control, mesh independence, long-term boundedness, or final steady mass
convergence.
