# P7-E5-CZ-ABSORB-COLD-RAMP11692 setup

## Status and authority

| Field | Contract |
| --- | --- |
| Status | `EXECUTED_DISCOVERY_ANALYZED` — active 1,000 reached; terminal execution verified; F1/F2 complete and F3 partial because vapor-inventory history was not instrumented |
| Phase | Phase 07 simplified Purnanto liquid-removal mechanisms |
| Lifecycle | `discovery` |
| Candidate | `E5-CZ-ABSORB-COLD` / cold-start inlet-matched absorber balance probe |
| Setup ID | `P7-E5-CZ-ABSORB-COLD-RAMP11692` |
| Origin | Explicit human selection in this chat on 2026-09-11 after reviewing the continuation-family evidence |
| Authority | Human-approved-context-only; setup creation approved, later Phase Loop launch still required |
| Gate | `G3` — cold-start inlet-matched absorber balance probe |
| Context | [`../../CONTEXT.md`](../../CONTEXT.md) |
| Related family | [E5-CZ absorber-control family](../index.md) |

## Question and hypothesis

**Question:** Can the no-outlet lower-cell-zone absorber reach a bounded steady
 numerical branch when it is present from the initialized state and its final
 integrated phase-2 removal rate matches the measured liquid-inlet rate?

**Hypothesis:** Starting from the exact E0-style initialized case/data state
will avoid the large accumulated-liquid and strongly disturbed carrier field
present in the G100 active-2,500 continuation. If the lower-zone phase-2
absorber is ramped gently from zero to `116.92 kg/s` and then held, total liquid
inventory may approach a bounded late trend without requiring a bottom outlet.
This is a bounded numerical discovery hypothesis, not a physical brine-pool or
plant-performance claim.

## Terminal analysis pointer

The executed run reached the declared 1,000 active-iteration horizon and passed
final save/reopen verification. The plot-led result is recorded in
[results.md](results.md). Its current evidence classification is execution
complete but discovery evidence partial: the source audit is complete, the
lower zone remained effectively liquid-free, total liquid inventory drifted
positively, and the planned vapor-inventory history is missing. No hypothesis
qualification transition is authorized from this setup alone.

**Competing explanations:**

- The previous continuation failures may have been dominated by the
  accumulated parent state and the abrupt/stiff source response rather than by
  the absorber concept itself.
- The current closed-bottom model may have a structural phase/mixture balance
  problem. If so, a fresh start will still show positive inventory drift or an
  unstable carrier solution even when the final absorber command equals the
  liquid inlet.
- A globally balanced source may still fail to remove liquid effectively if
  liquid does not reach the lower cell zone or if a uniform lower-zone source
  is too aggressive where the local phase-2 fraction is small.

## Parent and initialization basis

This is deliberately **not** a continuation from `P7-E5-CZ-G025`,
`P7-E5-CZ-G050`, `P7-E5-CZ-G100`, `P7-E5-CZ-G100-CONT2500`, or any member of
the `CAP14615/CAP29230/CAP58460` family.

Use the exact E0-style initialized case/data pair from the completed
`P7-E0-REF` preparation, before any treatment iterations. The server-neutral
reference identity is:

- setup: `P7-E0-REF`;
- initialized pair: `initialized.cas.h5` and `initialized.dat.h5` from the
  E0 initialized artifact;
- mesh: `Separator-purnanto342k.msh.h5`;
- mesh identity: `342,609` cells, `1,647,633` faces, and `1,046,255` solver
  nodes; and
- initialization: the proven E0 parent-derived hybrid initialization, with
  its method and post-initialization field state read back before the absorber
  is enabled.

The initialized pair must be proven to be before treatment iterations. The
active-500 and active-2,000 E0 states are not valid substitutes because they
already contain evolved liquid inventory. If the exact initialized pair cannot
be located, reopened, and identified, block the setup rather than silently
using a solved checkpoint or a continuation parent.

After loading the initialized pair, split the supplied mesh into the existing
lower cell zone `p7-e5-lower-y010` using the validated native split-by-mark
operation. Preserve the initialized solution fields through the split and do
not perform a second initialization after the split. Read back the lower-zone
identity, marked-cell count (`3,794` expected), geometric volume, mesh counts,
phase mapping, and source tree before the first active iteration.

## Controlled delta

Relative to the initialized E0 carrier state, the only scientific treatment is
the lower-zone inlet-matched phase-2 absorber schedule:

```text
alpha(n) = min(n / 100, 1.0)
Q_abs(n) = 116.92 kg/s × alpha(n)
S_mass(n) = -Q_abs(n) / V_lower
S_mom,k(n) = S_mass(n) × U_phase2,k,lower
```

Here `n` is the child active-iteration coordinate and `V_lower` is the
read-back lower-zone geometric volume. The schedule is updated every `10`
active iterations, giving a fixed linear ramp through active iteration `100`:

| Active iteration | Integrated phase-2 absorber command |
| ---: | ---: |
| `0` | `0.000 kg/s` |
| `10` | `11.692 kg/s` |
| `20` | `23.384 kg/s` |
| `50` | `58.460 kg/s` |
| `100` and later | `116.920 kg/s` |

The `116.92 kg/s` final value is the predeclared E0 liquid-inlet mass-flow
target, not a measured guarantee that exactly that much liquid reaches the
absorber. The live inlet, outlet, source, and phase-balance values must all be
read back. A small nonzero phase-2 outlet or transfer term may make the exact
net-balanced value differ from `116.92 kg/s`; that is an interpretation issue
to be measured, not a reason to change the schedule after seeing the result.

The source is phase-selective and lower-zone-only:

- phase-2 mass source: one negative uniform SI volumetric source in
  `p7-e5-lower-y010`;
- direct phase-1 mass source: disabled/`none` everywhere;
- mixture x/y/z momentum source: lower-zone-only and matched to the
  phase-2 removal velocity basis at each ramp update;
- parent-zone mass or momentum sources: none;
- energy and turbulence sources: none; and
- no feedback controller, post-hoc target adjustment, UDF, or cap ladder.

The integrated source must be audited through Fluent `get_sum` at every ramp
update. The source sign, units, active zone, and source tree must be read back
before solving and after the final save/reopen.

## Frozen invariants

- no bottom outlet, bottom-boundary change, porous jump, or explicit drainage
  boundary;
- same split topology: `separator-purnanto` plus `p7-e5-lower-y010`;
- lower register: `0 ≤ y ≤ 0.10 m`;
- same material, phase mapping, Mixture model, turbulence, gravity, energy,
  species, DPM-isolation, outlets, and boundary conditions as the reconciled
  E0 carrier setup;
- same numerical methods and relaxation/pseudo-time settings as E0 unless a
  later implementation gate proves an unavoidable dependency;
- no remesh, re-split, zone enlargement, field patch/reset, or second
  initialization after the initialized child state is prepared;
- no direct phase-1 source or vapor sink; and
- no qualification interpretation or automatic continuation.

## Run intent

- Mode: steady discovery from initialized state.
- Horizon: `1,000` absorber-active iterations.
- Ramp: active `0–100`, updated every `10` active iterations.
- Hold: `116.92 kg/s` from active `100` through active `1,000`.
- Smoke: first `50` active iterations, including ramp/source readback and
  warning checks.
- Primary late analysis window: active `700–1,000`; the ramp and early
  establishment windows remain part of the evidence and are not discarded.
- Checkpoints: paired case/data at child start, active `100`, `250`, `500`,
  `750`, and `1,000`, plus the nearest valid recovery state if blocked.
- Finalization: save final case/data, reopen, and read back initialization
  provenance, topology, source tree, ramp endpoint, and report-history extent.
- Durability: preserve the initialized parent identity, the split child start,
  each checkpoint, source audits, histories, residual transcript, warning
  transcript, terminal manifest, and final paired state.

The 1,000-iteration horizon is a discovery screen for boundedness and branch
existence. It is not a 10,000-iteration qualification run and cannot establish
steady convergence, physical drainage, or long-time plant behaviour.

## Required evidence

### Hard pre-run evidence

- exact E0 initialized case/data identity and pre-treatment iteration state;
- initialized-state method, phase fields, model settings, boundary conditions,
  and DPM isolation readback;
- lower-zone split identity, marked-cell count, geometric volume, mesh counts,
  and phase mapping;
- phase-2 inlet mass-flow readback and provenance of the `116.92 kg/s` schedule
  endpoint;
- ramp cadence, command values, phase-2 source density, matched momentum source,
  direct phase-1 source-off state, signs, units, and active source zone;
- report histories for total liquid mass, total liquid volume, lower-zone
  phase-2 mass/volume, adjacent and broad lower-band inventories, vapor
  inventory, phase-resolved inlet/outlet fluxes, source integrals, and
  phase/mixture balances;
- residual histories for continuity, momentum, turbulence, and phase volume
  fraction;
- warning capture for reversed flow, turbulent-viscosity limiting, source
  clipping, divergence, floating-point exceptions, and other solver failures;
- paired child-start save/reopen and a 50-iteration smoke verification; and
- checkpoints that can be reopened independently if the final horizon fails.

### Run and terminal evidence

At every 10-iteration ramp update record active/native iteration, scheduled
command, integrated `get_sum` source, expected source, absolute audit error,
phase-1 source state, phase-2 lower inventory, lower-zone phase-2 velocity
basis, and matched momentum terms.

Across the run retain total and nested liquid inventories; phase-resolved
inlet, steam-outlet, bottom, and absorber-source balances; vapor inventory and
flux; mixture closure; residuals; warnings; and all paired checkpoints.

The terminal evidence must include a final report-history extent, final source
and topology readback, final paired case/data existence, and an explicit
classification as `COMPLETE_VERIFIED`, `BLOCKED_VERIFIED`, or another justified
terminal state. Missing histories or a failed final reopen cannot be silently
waived because the solution appears visually stable.

## Core figure plan

| Figure | Question | Plot and comparison basis | Interpretation use |
| --- | --- | --- | --- |
| F1 — cold-start inventory response | Does the fresh initialized absorber approach bounded liquid inventory? | Total liquid mass and volume, lower-zone phase-2 mass/volume, adjacent-band and broad-band inventories versus active iteration; show the parent initialization anchor, ramp endpoint, and late analysis window | Directly distinguishes a bounded cold-start branch from continued accumulation or lower-zone depletion/rebound |
| F2 — inlet-matched source realization | Does the imposed absorber actually realize the intended phase-2 balance without direct vapor removal? | Scheduled command, integrated phase-2 source, `get_sum` audit error, phase-2 inlet/outlet/source terms, and direct phase-1 source state on the 10-iteration update coordinate | Distinguishes global balance error, source non-realization, and direct vapor-removal contamination |
| F3 — numerical and vapor credibility | Is any apparent bounded state numerically credible and compatible with the no-outlet abstraction? | Phase/mixture balances, vapor inventory/flux, bottom phase fluxes, residual histories, and warning counts over the full horizon with late-window summary | Separates a genuine bounded numerical branch from a transient, open, vapor-disturbed, or divergent field |

## Decision gate G3

Classify the cold-start child before any continuation or cap variation.

**Evidence supporting the cold-start branch:** the run reaches the declared
horizon without divergence; the source audit is precise; direct phase-1 source
remains zero; total liquid inventory has a bounded late trend with no sustained
positive drift; lower-zone inventory remains finite and does not show secular
growth or depletion; phase/mixture balances are interpretable; and vapor is
not directly removed by the absorber.

**Evidence weakening or rejecting the branch:** positive late total-liquid
drift, unbounded lower-zone accumulation, source clipping or non-realization,
material vapor disturbance, persistent open/source-dominated closure, worsening
residuals, or solver divergence. A failure does not prove that every possible
absorber schedule is impossible; it rejects this initialized-state,
inlet-matched ramp as a successful discovery setting.

No result from this setup may establish physical brine-pool level control,
physical outlet fidelity, mesh independence, or plant drainage performance.
The setup authorizes no automatic continuation, larger source, outlet, patch,
remesh, UDF, or qualification run.

## Assumptions and claim limits

- `116.92 kg/s` is the measured/reconciled E0 liquid-inlet target used to
  define the pre-run schedule. It is not assumed to equal the actual absorber
  capture rate without source and phase-balance evidence.
- The lower zone may contain both phases; the source removes only phase 2, but
  the mixture momentum source can alter the shared carrier field. Vapor response
  must therefore be measured rather than inferred from phase-1 source-off.
- “Steady solution” in this setup means a bounded, numerically credible late
  discovery trend over the declared window. It does not mean residual
  convergence or physical steady operation.
- The initialized state is a deliberate scientific comparison boundary. It is
  not interchangeable with any evolved E0 or G100 checkpoint.
