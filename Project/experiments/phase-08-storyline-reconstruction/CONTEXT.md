# Phase Context — Phase 8 Reproducible Storyline Runs

## Status

| Item | Current contract |
| --- | --- |
| Status, 3 October 2026 | **Paused.** Selected batch closed; no further runs authorized. |
| Verified outcome | Ten F3/F4 endpoints at N16000; saved-pair hashes and matched settings passed. |
| Comparison | [Uniform final-window results](results.md#current-family-organization-and-matched-n16000-comparison). |
| Family names | F0: mixed-inlet SIMPLE. F1: mixed-inlet Coupled. |
| Completed batch | Server 1 only; five matched F3/F4 pairs. |
| 2.5% points | 20.11, 23.46, 26.81 and 32.14 m/s. |
| 5% point | 26.81 m/s. |
| F3 continuation | Unaveraged N13,000 → N16,000; 3,000 added iterations. |
| Interpretation limit | F4 uses provisional E2.7 EWF; no absorber and no finalization of Phase 7.2A. |

<details>
<summary>Supporting detail — Status</summary>

| Item | Status |
| --- | --- |
| Human direction, 3 October 2026 | F4 must match those exact five speed/loading points, carrier and DPM controls, adding the existing provisional E2.7 EWF package |
|  | The existing F4 N13,000 point gets 3,000 more; the four missing F4 points start from the same allocated N10,000 parents and run 6,000 iterations |
|  | All ten finish with 6,000 mechanism-active iterations and common N15,500–16,000 windows |
|  | Use Server 1 only, preserve its loaded endpoint first, checkpoint locally every 1,000 iterations, and do not launch local/direct Fluent or change numerics |
|  | Stop at this scope; the general autonomous loop stays paused |
|  | Exact parents and paths are in the [batch specification](../../../PyAnsys/output/phase8-server1-matched-20261003/batch-spec.json) |
|  | F4 remains provisional; this does not finalize 7.2A or add its absorber |
| Human clarification, 2026-09-30 | Phase 8 reconstructs the past simulation steps into a reproducible storyline leading to the current model |
|  | Closing mass imbalance, reducing continuity residuals, and optimizing convergence are not Phase 8 objectives |
|  | Numerical diagnostics describe each step and limit its interpretation; they are not pass/fail conditions for completing the storyline or advancing to the next family |
|  | Preserve unsuccessful and unresolved outcomes as part of the history |
|  | This clarification does not resume the paused phase |
| Human-framed direction, 2026-09-25. | Build four linked run families on the existing Phase 7.2A 60k mesh: one-inlet Purnanto-style carrier plus post-development DPM; split two-phase inlet plus post-development DPM; split inlet with two-way DPM and droplet-loading sensitivity; and the same coupled setup with EWF |
|  | Sweep inlet flow/speed within each family |
|  | The deliverable is a documented, repeatable run and comparison pipeline with common reports |
|  | These are new storyline experiments, not exact repetitions of historical runs |
|  | Finer meshes with the same geometry are planned later and are out of scope |

</details>

## Evidence anchors

| Evidence anchors |
| --- |
| [Phases 1–2](../phase-01-purnanto-baseline-and-inlet-exploration/interpretation.md) moved from a homogeneous inlet to a split two-phase carrier and explored loading. [08b](../phase-02-parity-reset-and-pre-v2-qualification/interpretation.md) had high apparent outlet dryness but open whole-domain balance |
| [Phases 3–4](../phase-03-dpm-carryover-and-coupling/interpretation.md) explored DPM sensitivity and [EWF](../phase-04-ewf-wall-film-mechanisms/interpretation.md) |
| Incomplete tracks, limited film histories, and the unqualified carrier limited interpretation |
| [Phases 5–6](../phase-05-full-geometry-v2/interpretation.md) exposed brine-outlet sensitivity and a [pool-control abstraction](../phase-06-full-geometry-with-brine-pool/interpretation.md) that became a coupled problem beyond the immediate separator-flow goal |
| [Phases 7A–7.1A](../phase-07a-simplified-purnanto-liquid-removal/interpretation.md) selected a lower phase-2 absorber and developed it into a usable virtual outlet |
| The [7.1A parent](../phase-07-1a-absorber-convergence/interpretation.md) still carried roughly 24.33 kg/s phase-2 liquid through `steamoutlet` |
| [Phase 7.2A](../phase-07-2a-wall-liquid-routing/interpretation.md) revisits roughness and EWF |
| Its [monitoring contract](../phase-07-2a-wall-liquid-routing/monitoring-contract.md) informs Phase 8's common definitions |

## Phase contract

### Question and goal

| Item | Question and goal |
| --- | --- |
| — | How can the historical sequence of inlet representation, DPM coupling, wall-film treatment, and later liquid-removal changes be reconstructed on the common 60k geometry to explain the simulation history leading to the current model? |
| The central result is a reproducible simulation history | show the setup at each stage, why the next change was introduced, what the simulations showed, and how that sequence leads to the current model |
|  | Success means faithful setup lineage, bounded runs, preserved evidence, and a clear narrative, including numerical shortcomings |
|  | It does not require each case to converge or demonstrate physical separator efficiency |
|  | The [common report contract](report-contract.md) defines its measurements and comparison rules |

### In scope

| Item | In scope |
| --- | --- |
| Family 0 | the existing five-speed mixed-inlet SIMPLE reconstruction and diagnostic DPM, separated from F1 without changing artifacts |
|  | Compare F0/F1 as a declared numerical-package contrast |
| Family 1 | use one inlet carrying both phases in a Purnanto-style homogeneous inlet package on the 60k mesh; sweep inlet flow/speed, develop each carrier first, then inject and track DPM with feedback to the continuous flow off |
| Family 2 | replace only the inlet representation with the split two-phase inlet; repeat the same flow levels, carrier-development rule, and one-way DPM protocol for a direct Family 1/2 contrast |
| Family 3 | retain Family 2's split inlet, enable DPM interaction with the continuous phase, sweep the same flow levels, and vary the fraction of total inlet liquid represented as injected DPM |

<details>
<summary>Supporting detail — In scope</summary>

| Item | In scope |
| --- | --- |
| Family 3 | The fraction escaping with steam is measured, not commanded |
| Family 4 | retain Family 3's matrix and enable EWF |
|  | Compare matched speed and DPM points with Family 3, with film transfer and inventory added to the accounting |
| — | Families 1–4 retain the simplified closed lower boundary without the phase-2 absorber |
|  | Liquid may accumulate during steady iteration |
|  | Measure boundary-flux imbalance and inventory drift separately; pseudo-time iterations do not define a physical storage rate, and a persistently nonzero boundary imbalance does not establish a converged steady state |
| After Phase 7.2A | is finalized, run its selected final setup with the absorber at matching Family 3/4 flow and DPM-fraction points as a later comparison extension |
| Do not assume the current 7.2A branch | is final or copy unfinished settings into Phase 8 |
| — | Document every case's source setup, new-mesh adaptation, parent/initialization, complete model and boundary settings, solver controls, report definitions, run commands/history, checkpoints, and analysis windows |
|  | Each selected `setup.md` carries its runnable contract; raw machine evidence remains in `PyAnsys/` |
|  | Use the same report names, definitions, sign conventions, frequency, and postprocessing rules across eligible cases |
|  | Record every intentional difference and every inapplicable or unavailable report |
|  | Compare phase routing with source-inclusive boundary balance, inventory stationarity, and numerical health |
|  | Use physical storage-aware closure only if a transient branch with physical time is run |
|  | Interpret outlet dryness or carryover only with those global checks |
|  | Build a concise figure-led narrative explaining each historical change and the evidence that led to the next step |
|  | Keep historical observations separate from the new-mesh recreation |
|  | Run each selected stage to a declared bounded horizon and preserve its last valid endpoint |
|  | Do not extend runs, alter solver controls, or add recovery branches solely to pass mass-balance, inventory-drift, or continuity thresholds |
|  | Repair implementation errors and recover fatal solver failures only as needed to obtain usable storyline evidence; record any numerical departure from the historical setup as a separate adaptation |

</details>

### Boundaries and claim limits

| Item | Boundaries and claim limits |
| --- | --- |
| — | Hold the 60k geometry fixed |
|  | Later finer, geometrically identical meshes belong to a separate convergence study |
|  | Full-geometry brine-outlet and pool-control runs cannot be recreated on this truncated geometry |
|  | Their historical evidence explains the return to simplified geometry; they are context, not a fifth Phase 8 family |
| A one-inlet case on this 60k mesh | is Purnanto-style setup comparison, not an exact reproduction of Purnanto's published geometry, mesh, or results |

<details>
<summary>Supporting detail — Boundaries and claim limits</summary>

| Item | Boundaries and claim limits |
| --- | --- |
| — | Family 1/2 can be directly compared only when total phase feed, outlet, closed lower boundary, carrier settings, and DPM injections are matched apart from inlet topology |
|  | The later absorber comparison changes liquid-removal architecture as well as potentially finalized 7.2A wall treatment |
|  | Attribute effects only through matched controls or label the comparison as a combined-package effect |
|  | Do not present historical and recreated runs as mesh-identical repeats or use historical values as targets |
|  | Do not infer physical separator efficiency from outlet dryness, a residual, or one checkpoint |
| DPM escape claims | require track completion and represented loading; EWF drainage requires transfer and flow evidence |

</details>

## Candidate experiment families

| Family | Controlled contrast on the 60k mesh | Decision illuminated |
| --- | --- | --- |
| F0 — mixed inlet, SIMPLE | Five-speed SIMPLE / pseudo-time-off / second-order-k series and diagnostic DPM | Numerical-package contrast with F1. |
| F1 — one inlet, Coupled | Purnanto-style mixed-phase inlet; common flow/speed sweep; post-development one-way DPM | Reference carrier and droplet response under one-inlet topology. |
| F2 — split inlet | Same sweep and DPM protocol, changing inlet topology | Effect of explicit liquid/steam inlet separation. |
| F3 — coupled DPM | F2 plus interaction with continuous phase and declared injected-liquid DPM-fraction variation, holding droplet size distribution fixed | Effect of droplet feedback and inlet mist allocation. |
| F4 — coupled DPM + EWF | F3 matrix plus EWF | Effect of wall-film transfer and drainage on matched cases. |

| Item | Candidate experiment families |
| --- | --- |
| Human-selected axes | use five nominal inlet speeds—`20.11`, `23.46`, `26.81`, `29.48`, and `32.14 m/s`—at every family, and injected-DPM fractions `2.5%`, `5%`, `7.5%`, `10%`, and `20%` of total inlet liquid in F3/F4 |
|  | Keep the same physical inlet opening and pure-phase split location at every speed; change boundary flow values, not inlet area |
|  | On mass-flow inlets, impose phase mass flows corresponding to each target superficial speed on the verified 60k inlet areas and report the realized speed |
|  | Keep the 1600 kJ/kg reference phase proportion and material state fixed across the speed sweep unless a separately named comparison changes them |
|  | At each DPM fraction, reduce Eulerian liquid by the injected amount so total water feed is unchanged, and keep the droplet-size distribution fixed |

<details>
<summary>Supporting detail — Candidate experiment families</summary>

| Item | Candidate experiment families |
| --- | --- |
| — | For F1, apply the same mixed-phase condition to the existing two inlet faces as one combined physical inlet, subject to Fluent readback of both face-zone settings and their summed phase flux |
|  | For F2, keep the outer liquid and inner steam faces as the pure-phase split |
| At zero DPM fraction, their historical area ratio | is intended to give comparable phase velocities at the reference proportion |
| — | At nonzero DPM fractions in F3/F4, liquid moved to steam-side DPM reduces Eulerian flow through the liquid strip, so equal zone velocities are no longer presumed |
|  | Report steam-zone, liquid-strip, and overall nominal superficial speeds separately |
|  | Later finer meshes should preserve the same physical inlet area and split location, then verify their actual meshed face areas |
|  | F1/F2 retain the full Eulerian liquid feed and use one-way diagnostic DPM tracking from the same physical `steaminlet` face, without continuous-phase source feedback |
|  | All five families share Shuhei's [09cV3 seven-bin fine-mist PSD](../phase-03-dpm-carryover-and-coupling/purnanto-09cV3-fine-mist-psd/setup.md), an assumed distribution rather than measured inlet truth |
|  | F3/F4 instead allocate the stated fraction of inlet liquid to mass-carrying, coupled DPM |
|  | Their difference from F2 therefore combines allocation and coupling |
| A 5% one-way allocated bridge at each speed | is optional and does not expand the core five-family matrix |
| F4's intended EWF mechanisms | are phase accretion, DPM deposition, splash, and stripping, with film momentum transport and DPM-to-carrier interaction ON |
| EWF | is scoped to the zone named `wall`; the bottom is excluded |
| wall's Flow Momentum Coupling | is OFF |
| — | The remaining EWF numerical switch manifest stays provisional until Phase 7.2A's final setup exists |
| Source qualification | [Purnanto et al., Table 2 and Figure 20](https://www.researchgate.net/publication/269519626_CFD_MODELLING_OF_TWO-PHASE_FLOW_INSIDE_GEOTHERMAL_STEAM-WATER_SEPARATORS) explicitly identifies `26.81 m/s` for the 1600 kJ/kg spiral case |
|  | The five-point set above is a Phase 8 experimental design inspired by the paper's range, not the paper's exact plotted speed set. `20.11 m/s` approximates a 25%-lower-flow point relative to `26.81 m/s`; `23.46 m/s` is an intermediate design point |
|  | The project has used `32.14 m/s` in an earlier inlet-loading screen; `29.48 m/s` appears in the paper text for a Lazalde-Crabtree case, so neither is asserted to be a reported spiral coordinate |
|  | Phase 8 holds the 1600 kJ/kg phase proportion fixed while changing flow, rather than reproducing the paper's enthalpy sweep |

</details>

## Decision conditions

| Item | Decision conditions |
| --- | --- |
| — | Before execution, verify mesh identity, inlet face areas, and F1's combined-face versus F2's split-face readback; calculate the five speed-point mass-flow targets, and fix the F1/F2 one-way DPM mass basis, DPM injection definition, bounded carrier-development horizon and matched comparison window |
|  | Write each `setup.md` |
|  | Build and verify common report definitions before solving |
| Direct comparison | requires complete report definitions, signs, comparable windows, source and DPM accounting, and run provenance |
| — | Preserve failures and inapplicable measures explicitly |

<details>
<summary>Supporting detail — Decision conditions</summary>

| Item | Decision conditions |
| --- | --- |
| core matrix | is 5 F0 + 5 F1 + 5 F2 + 25 F3 + 25 F4 = 65 intended cases |
| — | Start with the `26.81 m/s` reference-speed pilot in F1/F2 and a `5%` point in F3 |
|  | F4 waits for finalized 7.2A EWF settings before its pilot |
|  | Advance after setup/readback, reports or explicit report limitations, saved artifact identity, and bounded-run evidence are verified |
|  | Measure source-inclusive balance, inventory drift, continuity, and tracking completeness, but do not require them to pass numerical thresholds before advancing or performing diagnostic DPM tracking |
| Unconverged or incomplete outcomes | remain valid storyline evidence with restricted physical claims |
| Pilot evidence may | require implementation repair without changing the scientific axes |
| — | The original 2026-09-26 F1/F2 bases inherited Phase 7.2A E0 Coupled/Global Time Step numerics |
|  | Following the human's Purnanto-alignment direction, the selected 2026-09-29 parity children share SIMPLE, pseudo-time off, second-order `k`, and the recorded Purnanto inlet/outlet turbulence inputs while retaining the 60,964-cell mesh and 26.81 m/s total feed |
| diagnostic DPM parcel-weight scale and final EWF switch manifest | remain setup-critical open details |
| — | Existing evidence under the earlier numerical qualification rule (superseded as a progression gate on 2026-09-30): the Purnanto-style SIMPLE F1/F2 pilots and the F2 N=5,000 continuation did not meet boundary-balance and inventory-stationarity checks |
| They | remain preserved diagnostic branches and may support labelled diagnostic DPM under the revised storyline purpose when the saved state is usable; no converged-carrier claim follows |
| Separately named F1/F2 numerical-recovery children restore the | recorded Phase 7.2A Coupled/Global Time Step/first-order-`k` stack while retaining the corrected inlet/backflow turbulence inputs |
| — | The N=10,000 Coupled [26.81](../../PyAnsys/output/phase8-analysis/26p81-f1-f2-coupled-n10000/summary.json), [20.11](../../PyAnsys/output/phase8-analysis/20p11-f1-f2-coupled-n10000/summary.json), [23.46](../../PyAnsys/output/phase8-analysis/23p46-f1-f2-coupled-n10000/summary.json), [29.48](../../PyAnsys/output/phase8-analysis/29p48-f1-f2-coupled-n10000/summary.json), and [32.14 m/s](../../PyAnsys/output/phase8-analysis/32p14-f1-f2-coupled-n10000/summary.json) matched carriers all pass the declared last-500 operational gate |
|  | At every speed, however, more than 99% of Eulerian liquid feed exits via the steam outlet in both families |
| Coupled recovery | is a declared solver-package difference from Purnanto parity |
| — | Seven-bin one-way diagnostics at the completed speeds retain large unresolved track fractions |
|  | The 5% F3 [N=20,000 update-100 continuation](../../PyAnsys/output/phase8-analysis/26p81-f3-5pct-upd100-n20000/assessment.json) fails continuity despite passing its Eulerian boundary-gap and inventory-drift checks; updating held DPM sources each flow iteration alone [worsens its N=21,000 gate](../../PyAnsys/output/phase8-analysis/26p81-f3-5pct-upd100-source-every-iter-n21000/assessment.json) |
|  | Lowering the DPM source factor to `0.05` also [fails the N=21,000 gate](../../PyAnsys/output/phase8-analysis/26p81-f3-5pct-upd100-source-every-iter-dpmurf0p05-n21000/assessment.json); both retrack-20 children also failed |
|  | The 2.5% F3 N=15,000 continuation passes boundary balance and inventory drift but still misses continuity; a per-flow-source/DPM-factor-0.1 recovery also fails continuity at N=16,000 |
|  | A DPM source-term-linearization child also failed the carrier gate; the 2.5% node-averaged-source N=20,000 continuation passes balance and inventory but narrowly misses continuity; its per-flow-source/URF-0.2 N=21,000 recovery failed inventory and continuity gates |
|  | The unchanged averaged-source N=25,000 reference-speed continuation passed its last-500 Eulerian carrier gate, but 82.01% of represented DPM feed remained incomplete at 50,000 tracking steps and 73.55% at 200,000 steps |
|  | A separate 32.14 m/s, 2.5% node-averaged-source N=15,000 continuation also passed the carrier gate, but 83.40% of represented DPM feed remained incomplete at 50,000 steps |
|  | At the matched 200,000-step cap, the 32.14 m/s endpoint has 78.27% represented DPM feed incomplete |
|  | The 20.11 m/s, 2.5% low-speed N11,000 pilot passed boundary balance and inventory drift but failed continuity; its node-averaged-source N15,000 child passes boundary balance but fails inventory drift and continuity |
|  | Its unchanged N20,000 continuation passed boundary balance and inventory drift but still failed continuity without an improving trend; the low-speed carrier remains unqualified |
|  | The verified 23.46 m/s, 2.5% child completed its N11,000 pilot, saved/reopened its final pair, and completed seven-bin tracking before the phase was paused; its numerical assessment remains outstanding |
| Carryover | remains unqualified |
| — | Fluent readback established that the DPM model source URF and Coupled pseudo-time DPM factor store one control |
| separately named F4 E2.7-based N=11,000 pilot | is saved but unqualified |
| F4's final matrix comparison | remains provisional until Phase 7.2A EWF treatment is finalized or explicitly reinterpreted |
| Report thesis | reconstruct the simulation history from the mixed inlet through split inlets, droplet coupling, wall film, and the later liquid-removal architecture, showing why each step was introduced and what was observed |
|  | Common reports make the stages comparable and expose unresolved limitations; they do not turn Phase 8 into a convergence or mass-closure campaign |
| Completion standard | account for each selected stage and matrix point with a reproducible setup, bounded-run outcome or explicit technical limitation, preserved evidence, and its place in the storyline |
|  | Keep prior numerical pass/fail assessments as historical diagnostics |
|  | Retain the selected axes and finalized-7.2A dependency for the later comparison |
|  | Phase 8 remains paused until the human resumes execution |

</details>
