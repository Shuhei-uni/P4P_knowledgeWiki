# Phase 7b — Five-Thickness Discovery Design

## Authority and status

**Human-approved:** CONTEXT.md candidate E1, ideas H1/H2, gate G1; five
collector thicknesses, carrier-only steady Mixture/RNG, Energy off, a closed
brine-outlet wall, identical fresh initialization without a patched standing
pool, and at most 5,000 iterations per case. This is discovery followed by
human review, not a long-run qualification or physical validation claim.

**Preparation in progress:** the geometric mapping and PC/API path discovery
are established, including live counts and volumes for all five masks.
Source coupling, source-mask equivalence, instrumentation, complete reference
readback and the discovery-design transition remain to be proved.
This design is not an executable setup or permission to submit the five runs.

## Question and prior-evidence collision check

Can increasing lower-region collector coverage deliver and remove liquid
while establishing a useful steady carrier solution, with tolerable effects
on separation above it?

| Earlier evidence | What it established | Delta in this screen | Novelty |
| --- | --- | --- | --- |
| Historical 07b–07f closed-bottom sinks | Limited liquid availability in small bands, persistent imbalance and no accepted stability window; phase Net source double-counting was corrected | Full 620,431-cell geometry, five nested lower-region masks, correct accounting and equal-velocity inlet design | PARTIAL REPEAT of mechanism; new geometry/coverage comparison |
| Historical 07g–07n resolved brine outlet | Physical outlet diagnostics did not yield an accepted baseline; later transient low-feed states are not eligible parents | Closed brine outlet; numerical collector; steady full-feed carrier; no pool control | NEW controlled combination; no transient-state inheritance |
| Shuhei full-geometry 02c | Equal-velocity inlet contract and useful setup evidence, with actual feeds affected by different densities | Consistent Purnanto 2013 properties; numerical collector replaces the active brine outlet | PARTIAL REPEAT of carrier/inlet reference, new liquid-removal question |

Sources: [sink evidence](../parallel-andy-studies/closed-bottom-liquid-sinks.md),
[resolved-outlet evidence](../parallel-andy-studies/resolved-brine-outlet.md),
[02c](../phase-02-parity-reset-and-pre-v2-qualification/full-geometry-02c-mixture-pressure-sensitivity/setup.md).
Existing data do not answer the five-height full-geometry comparison. Failed
historical cases remain evidence, not automatic repeat runs or saved parents.

## Cases and comparison control

Use the exact mesh identified in [geometry-proof.md](geometry-proof.md).
The observed numerical lower datum is `y_b = -1.4845837354660034 m`; the
mapped historical cap is `y_c = +0.020 m`. The approved fraction f defines
`y_top = y_b + f (y_c-y_b)`.

| Screen ID | Fraction | Top y [m] | Maximum iterations |
| --- | ---: | ---: | ---: |
| S20 | 20% | -1.1836669883728028 | 5,000 |
| S40 | 40% | -0.8827502412796020 | 5,000 |
| S60 | 60% | -0.5818334941864014 | 5,000 |
| S80 | 80% | -0.2809167470932006 | 5,000 |
| S100 | 100% | +0.0200000000000000 | 5,000 |

Select owned fluid cells whose centroids satisfy `y_b <= y <= y_top`, across
the connected lower vessel and closed brine pipe; no additional x/z crop.
Use identical predicates for the source and its reports. Record actual cell
counts, selected geometric volumes and boundary cell resolution. Cell-based
selection approximates the continuous plane; record its spatial resolution.

All cases start from the same independently prepared reference, not another
thickness's endpoint. Keep mesh, materials, inlet velocities/fractions,
numerics, initialization, source law/strength and instrumentation fixed.
Only the collector top changes. Use the reference conditions in CONTEXT.md,
including Purnanto densities and `27.118 m/s` on both pure-phase inlet faces.
The old saved geometry/reference confirms 10 µm liquid diameter, Manninen
slip and Schiller–Naumann drag. Its Simonin turbulence-interaction entry
differs from the current preparation state's `none`. The version-matched
manual and live active-model check recorded in CONTEXT.md resolve Simonin as
inapplicable to the selected shared Mixture/RNG turbulence formulation; keep
`none` rather than changing formulation to reproduce a saved tuple. No claim
of every historical setting matching is made.

## Finite source and conservation contract

The implementation under review uses `S_l = -chi rho_l alpha_l / tau`,
`S_g = 0`, with positive finite, fixed tau and a bounded liquid fraction.
The sink is zero outside the collector and when no liquid is present. Tau
is a numerical removal coefficient with units seconds; it does not introduce
a physical transient solver or a timestep-dependent inventory controller.
Do not force removal to equal inlet flow regardless of liquid availability.

For the conservative mixture momentum equation, removal at the local liquid
velocity requires `S_M = S_l u_l`. Where slip is active,
`u_l = u_m + u_drift,l`; substituting mixture velocity alone omits the drift
contribution. The phase-velocity accessor must be demonstrated against native
phase-selected fields before accepting this implementation. Do not
dereference unallocated phase storage or silently use a zero/mixture fallback.

Under the shared mixture-turbulence transport assumption, include removal
`S_k = S_l k` and `S_epsilon = S_l epsilon`. Energy remains off. Hook liquid
mass on the liquid phase only and momentum/turbulence on mixture; do not add
a second mixture mass sink or an opposite vapour source. Document source
Jacobians, clipping and lagged quantities in the eventual setup/code.

The 2025 R2 documentation supports the source-hook allocation and explicitly
requires consideration of accompanying momentum/scalar sources:
[source definition](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_udf/flu_udf_ModelSpecificDEFINE.html),
[Mixture hook table](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_udf/x1-79900012.2.html),
[cell-zone source requirements](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/flu_ug_bcs_sec_cell_zones.html).
The conservative momentum/turbulence formulation above is a project
derivation, not a claim that Fluent supplies these terms automatically.

**Historical C-route diagnostic (superseded by the Python direction below):**
installed 2025 R2 headers define phase
`C_U/V/W` as direct velocity-storage access; they do not reconstruct a missing
phase velocity. `C_SLIP_U/V/W` are additional guarded diagnostic candidates.
The header names alone do not establish phase-to-mixture drift versus
secondary-to-primary relative velocity. A nonzero-slip comparison with native
phase fields remains mandatory; zero-slip agreement is insufficient.

**Untested numerical implementation choice:** use common `tau = 0.0024095893 s` for all
five cases. The basis is a first-order remainder of `0.01` over the reference
crossing `h20/Uref`: `tau = (0.3009167471 / 27.118) / ln(100)`.
The 1% remainder is a numerical convention, not a plant requirement. Inlet
speed is a reference scale, not a verified upper bound on collector velocity
or a measured residence time. This therefore does not guarantee 99% actual
capture. Do not retune tau between thicknesses or add a coefficient sweep.

**Human-directed implementation revision:** use Python/PyFluent instead of C.
Investigate native Fluent expressions for the same source law and phase scopes;
no C collector compilation or attachment. The 2025 R2 manual documents
[phase-context field expressions](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/flu_ug_expressions_sources.html)
and [expressions for cell-zone conditions](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/flu_ug_expressions_create_and_use.html).
These establish a route to investigate, not proof that this exact Mixture
source/report contract is supported. Earlier C accessor checks remain
diagnostic evidence, not a requirement to retain that implementation.

**Historical strength comparison:** prior sink studies used tau `0.1 s`,
`0.02 s`, and adaptive values down to `0.002 s` without establishing accepted
stability. The present value is about 41.5 times stronger than `0.1 s` and
8.3 times stronger than `0.02 s` at equal liquid inventory; it is about 17%
weaker than `0.002 s`. This comparison does not transfer results between meshes.
The human has asked about the choice; it must not be presented as an optimized
or separately human-selected coefficient. See the
[historical records](../parallel-andy-studies/closed-bottom-liquid-sinks.md).

**Still required:** verify the exact live Python/native-expression source API,
phase-velocity semantics, expression update frequency and source linearization;
read back and save/reopen the source configuration. No main screen may use an
unverified substitute or silently omit momentum/turbulence removal.
No claim of instantaneous or coefficient-independent perfect collection is
permitted from this single-strength screen.

## Required instrumentation before any screen

All scalar histories below use native steady iteration N, sampled every
iteration and preserved in Fluent-side report files. Retain the raw data;
write local mirrors through the Fluent API as needed. A reconnect must not
erase the evidence. The exact filenames belong in each case's run-paths.yaml.

| Required quantity | Definition / scope | Units and interpretation |
| --- | --- | --- |
| Total liquid volume | `V_l = integral(alpha_l dV)` over all fluid cells | m³; no alpha threshold |
| Total liquid mass | `M_l = integral(rho_l alpha_l dV)` | kg; independently reconcile with volume and constant density |
| Collector liquid volume/mass | Same integrals using chi | m³, kg; distinguishes liquid reaching the collector from liquid remaining above |
| Above-collector liquid volume | Total minus collector, using the same mask | m³; retain both terms |
| Geometric collector volume and cell count | `integral(chi dV)` and owned-cell count | m³, count; fixed per case |
| Integrated liquid source | `Q_l = integral(S_l dV)` | kg/s, negative for removal; do not multiply by alpha twice |
| Positive removal rate | `R_l = -Q_l` | kg/s |
| Boundary-only phase and mixture fluxes | Separate contributions from each inlet and the steam outlet; verify brine-wall zero flux | kg/s, positive inward and negative outward |
| Corrected closure | `B_l+Q_l`, `B_g`, `B_m+Q_l` from boundary-only B | kg/s and percent of measured respective inlet; count sink exactly once |
| Collector delivery/escape | Liquid inward/outward flux across the actual mask boundary | kg/s; distinguish gross circulation from net transport, and prove surface/source-mask consistency |
| Steam recovery and liquid carryover | Steam-outlet phase fluxes divided by corresponding inlet phase fluxes | Ratios; retain signs and raw flows before any reduction |
| Pressure/velocity response | Area-weighted static pressure on each inlet and steam outlet, each inlet-minus-outlet difference, fluid-cell pressure extrema, maximum mixture speed and fixed above-cap sections | Pa, m/s; report both inlet pressure drops separately |
| Scaled residual histories | Every active equation, including continuity, velocities, k, epsilon and liquid fraction | Native equation/iteration labels; preserve any scaling/settings changes |

Fluent phase Net historically included the sink. Therefore record individual
boundary contributions and independently reconstruct B; do not augment an
already source-inclusive Net. Verify this convention before trusting a
derived balance. Record each native report's units, phase, domain and source
inclusion semantics.

`Delta V_l / Delta N` and `Delta M_l / Delta N` are numerical iteration
trends, not physical m³/s or kg/s storage terms. Do not use them as transient
accumulation corrections in the steady mass balance.

Residual monitor buffers alone are insufficient. Preserve a complete native
residual transcript or another demonstrated durable residual history, and
prove recovery after reconnect. Missing required histories make a case
evidence-incomplete even if its iteration count reaches 5,000.

## Analysis, figures and observations

Use full raw histories and fixed final windows `4001–4500` and `4501–5000`
for completed cases. Report mean, min/max, standard deviation, linear slope
and change between windows for inventories, removal and closure. For partial
cases, report the actual available windows explicitly; do not present them
as equivalent 5,000-iteration comparisons. The planned horizon is 5,000
iterations for each case within the human's cap; early scientific
disappointment is not an early-stop rule. G1 always returns the evidence.

**Declared numerical indicators, not physical acceptance criteria:** report
whether the final-window mean absolute liquid, vapour and total closure is
each at most 1% of its measured inlet rate; whether the change in mean total
liquid volume between the two final windows is at most 1% of the larger
window mean (denominator floor `1e-6 m3`); and whether each active scaled
residual is at most `1e-3` throughout the final window. Also retain maxima,
variation and slopes, so these indicators cannot hide excursions. Failure
does not authorize tuning, extra iterations or dropping a case.

Use identical horizontal sections at `y=0.5, 1.5, 3.0, 5.0 m`, restricted to
fluid, for liquid-fraction and mixture/phase velocity components and speed.
They are numerical comparison locations above the common maximum cap, not
physical measurement stations. Verify they are nonempty before execution;
keep section geometry and colour scales common across all five cases.

Use the reference Hybrid Initialization with the same saved settings for
every case: 10 hybrid passes, explicit URFs `[1,1]`, averaged turbulence
parameters, no external-aerodynamics or constant-velocity option, no standing
pool patch. Verify initial liquid inventory and archive the initial fields;
a nonzero initial pool or differing initialization requires reconciliation
before proceeding. Hybrid passes are initialization, separate from the
5,000 steady solution iterations.

| Figure | Question / plot | Axes and comparison | Source / required preparation |
| --- | --- | --- | --- |
| F1 — Water inventory and removal | Does thickness change liquid accumulation and removal? Linked history panels, no dual-axis overlay | N versus total/collector liquid volume [m³] and removal [kg/s]; same five-case axes; raw histories plus labelled final-window summaries | Every-iteration inventory/source reports; plots distinguish transport limitation from insufficient removal |
| F2 — Conservation and outlet routing | Does apparent collection coexist with phase closure and useful steam routing? Separate history panels | N versus liquid/vapour/mixture closure [% of respective measured feed], steam recovery and liquid carryover; same sign convention and windows | Individual boundary fluxes plus independent source integral; no Net double-counting |
| F3 — Spatial effect above the collector | Does the removal region alter separation above its intended zone? Matched contours/profiles | Liquid fraction and velocity on identical sections, with all collector tops shown; compare a common region above the maximum cap | Saved matching case/data and fixed extraction sections/ranges; avoid interpreting larger mask coverage itself as better separation |

All-equation residual plots are mandatory supporting numerical evidence.
Capture initial configuration and final liquid-fraction/velocity fields; save
paired case/data at initialization, every 500 iterations where supported,
and at each terminal state. Keep at least the last two recovery checkpoints
plus the initial and final pair. Record source-library/source-code identity,
parameters, actual solve count and save/reopen provenance with each case.

Create setup.md and results.md together for each selected case after the
required design transition, with run-paths.yaml populated from observed PC
paths. Update each results.md after its terminal state using Observed,
Inferred and Missing Info labels, including failures and missing evidence.
The campaign comparison links those five records; do not create a second
chronological work log or rewrite raw evidence.

## Review and execution boundaries

Initial question-experiment assessment: scientific value 3/4, interpretability
2/4 while source coupling remains unproved, cost-effectiveness
3/4 for the user-selected five-case scope. **Disposition: not run-ready.**
Material issues are the finite-strength confounder, phase-velocity accessor,
correct source accounting, source-mask equivalence, durable residual evidence
and complete save/reopen proof. Geometry mapping is resolved by the linked
proof; prior failures do not make this geometry/coverage screen redundant.

Poor residuals, imbalance or unpromising behaviour alone do not terminate a
fixed-horizon discovery case or justify tuning it. Preserve and report those
observations. Initialization failure, fatal Fluent error, process crash,
unreconciled progress, loss of required evidence or save failure require an
explicit blocked disposition and recovery handling. Never exceed 5,000
iterations or restart an uncertain solve automatically.

At G1, compare all five dispositions and identify a candidate explanation,
supporting observations, strongest alternative explanation, and what a later
qualification would need to establish. Return to the human; no automatic
longer run or claim of validated separator performance follows.
