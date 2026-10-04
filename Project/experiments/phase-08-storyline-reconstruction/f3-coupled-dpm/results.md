# Phase 8 F3 — allocated two-way droplets

## Current matched N16000 endpoints

| Item | Current matched N16000 endpoints |
| --- | --- |
| — | The authorized Server 1 batch completed all five selected points at N16000, with 6000 mechanism-active iterations |
| Final pairs | were saved/reopened and their synced hashes verified |
| [uniform N15500-16000 comparison](../results.md#current-family-organization-and-matched-n16000-comparison) | is the current comparison; the pilot figures below retain their earlier horizons |
| phase | is paused |
| F3 changes both the liquid representation and carrier feedback | a stated part of the total liquid feed is moved from Eulerian liquid to coupled DPM |
|  | The matched pilots show transient routing changes and strongly size-dependent unresolved fates |
|  | They extend the storyline even when numerical diagnostics are poor |

## Allocating more liquid to DPM changes the bulk response

| Item | Allocating more liquid to DPM changes the bulk response |
| --- | --- |
| speed comparison | uses four 2.5% pilots, each from its independent same-speed F2 N10,000 parent, at N10,000–11,000 with 100-iteration retracking and held sources |
| 26.81 m/s loading comparison | uses the same 2.5% and 5% protocol. 29.48 m/s and the larger selected loading fractions have not been run in this series |

![F3 matched speed pilots](figures/pilot-speed-response.png)

| Item | Allocating more liquid to DPM changes the bulk response |
| --- | --- |
| — | At 26.81 m/s, the 5% pilot loses more Eulerian inventory over the same 1,000 iterations than the 2.5% pilot and ends with a lower Eulerian outlet fraction |
| Figure F3.2 | shows that this difference develops through an oscillatory adjustment after allocation/coupling begins |

![F3 matched loading pilots](figures/pilot-loading-response.png)

| Speed (m/s) | Allocated DPM (%) | N11,000 Eulerian outlet liquid / total liquid feed (%) | Eulerian inventory (kg) | DPM escaped (% of allocated feed) | DPM trapped (%) | DPM unresolved (%) |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 20.11 | 2.5 | 96.126 | 1749.8 | 1.51 | 31.18 | 67.32 |
| 23.46 | 2.5 | 96.998 | 1715.5 | 1.81 | 20.72 | 77.47 |
| 26.81 | 2.5 | 96.972 | 1715.8 | 1.73 | 18.96 | 79.31 |
| 32.14 | 2.5 | 97.935 | 1864.5 | 1.73 | 12.11 | 86.16 |
| 26.81 | 5 | 94.041 | 1676.3 | 1.88 | 19.13 | 78.98 |

| Item | Allocating more liquid to DPM changes the bulk response |
| --- | --- |
| outlet numerator | is Eulerian liquid only, while the denominator is the unchanged total liquid feed, including allocated DPM |
| — | A lower value than F2 therefore partly reflects the representation change; it is not the total liquid carryover |
|  | At 26.81 m/s the 2.5% and 5% pilots end at 96.97% and 94.04%, respectively, with 79.31% and 78.98% of DPM feed unresolved |

## The broad liquid structure persists through the pilot change

| Reference snapshot | Vertical liquid distribution | Inlet-plane circulation |
| --- | --- | --- |
| F3-26.81-2p5-n11000 | ![F3-26.81-2p5-n11000 liquid](figures/F3-26.81-2p5-n11000-liquid.png) | ![F3-26.81-2p5-n11000 inlet-vectors](figures/F3-26.81-2p5-n11000-inlet-vectors.png) |

| Item | The broad liquid structure persists through the pilot change |
| --- | --- |
| — | Compare the N11,000 pilots first |
|  | The 2.5% averaged-source snapshots at N20,000, N25,000 and N15,000, and the 5% held-source N20,000 snapshot, are separate numerical adaptations at unequal development horizons |
|  | The reference 2.5% and 5% centre cuts retain the same broad lower-liquid and outer-wall pattern seen in F2; the loading change does not visibly replace that structure at this pilot horizon |
|  | The mixture inlet vectors still show circumferential circulation |
| Quantitative routing and inventory histories resolve differences that | are subtle on the shared full-range contours |

## Reference-speed pressure

| 2.5% pilot | 5% pilot |
| --- | --- |
| ![F3-26.81-2p5-n11000 pressure](figures/F3-26.81-2p5-n11000-pressure.png) | ![F3-26.81-5-n11000 pressure](figures/F3-26.81-5-n11000-pressure.png) |

## Intermediate droplets dominate the unresolved tracking problem

| Item | Intermediate droplets dominate the unresolved tracking problem |
| --- | --- |
| 14, 24 and 35 µm bins | remain almost entirely incomplete in the pilot fate plots |
| At the reference 2.5% point, the 89 µm trajectories | are trapped while the smallest bin has both escaped and trapped trajectories |
| — | The response therefore depends strongly on diameter, and the completed smallest/largest bins cannot represent the unresolved middle of the distribution |

![F3 pilot droplet fates](figures/pilot-droplet-fates.png)

| Intermediate droplets dominate the unresolved tracking problem |
| --- |
| F3 26.81 m/s 2.5% N11000 — inlet stream 0: |

| 7.07 µm | 34.64 µm | 89.44 µm |
| --- | --- | --- |
| ![F3-26.81-2p5-n11000 stream 0 07](figures/F3-26.81-2p5-n11000-track-07um-stream0.png) | ![F3-26.81-2p5-n11000 stream 0 35](figures/F3-26.81-2p5-n11000-track-35um-stream0.png) | ![F3-26.81-2p5-n11000 stream 0 89](figures/F3-26.81-2p5-n11000-track-89um-stream0.png) |

| Intermediate droplets dominate the unresolved tracking problem |
| --- |
| F3 26.81 m/s 5% N11000 — inlet stream 0: |

| 7.07 µm | 34.64 µm | 89.44 µm |
| --- | --- | --- |
| ![F3-26.81-5-n11000 stream 0 07](figures/F3-26.81-5-n11000-track-07um-stream0.png) | ![F3-26.81-5-n11000 stream 0 35](figures/F3-26.81-5-n11000-track-35um-stream0.png) | ![F3-26.81-5-n11000 stream 0 89](figures/F3-26.81-5-n11000-track-89um-stream0.png) |

| Item | Intermediate droplets dominate the unresolved tracking problem |
| --- | --- |
| Each row | shows three deterministic illustrative paths, not a statistical sample |
| — | Native zone outlines provide vessel/inlet/outlet context; path colour represents diameter on the shared 5–100 µm range |
| line endpoint alone | is not a fate classification |
| saved tracking controls | were retained; no carrier iterations or source-case saves were issued |
| — | Diameter-resolved fate plots, rather than these selected paths, describe the full tracked ensemble |

## Numerical adaptation and tracking sensitivity

![F3 source averaging at unequal horizons](figures/source-averaging-context.png)

![F3 low-speed and 5% continuations](figures/additional-continuation-context.png)

| Item | Numerical adaptation and tracking sensitivity |
| --- | --- |
| — | The earlier continuation campaign investigated source cadence, relaxation, linearization and averaging |
|  | These results document that investigation; they do not redefine Phase 8 as a convergence campaign |
| final original and averaged-source segments | are shown at their actual coordinates, with intervening segments available in the retained receipts |

![F3 tracking cap sensitivity](figures/tracking-cap-sensitivity.png)

| Numerical adaptation and tracking sensitivity |
| --- |
| Increasing the tracking cap from 50,000 to 200,000 steps reduced unresolved represented DPM feed from 82.01% to 73.55% at 26.81 m/s and from 83.40% to 78.27% at 32.14 m/s |
| Each panel holds its carrier fixed; the two carriers have different horizons |
| The further 500,000-step 24/35 µm reference probe did not change their fate counts |
| These probes show sensitivity to termination limits, not completed droplet separation |

## Numerical context

![F3 pilot accounting and continuity context](figures/numerical-context.png)

| Numerical context |
| --- |
| The continuity and boundary-gap histories give context for the pilot response; they do not decide whether this historical stage belongs in Phase 8 |

## What this stage establishes

| What this stage establishes |
| --- |
| F3 recreates the transition from diagnostic paths to mass-carrying coupled droplets |
| Both liquid allocation and feedback affect the carrier, while unresolved intermediate-size trajectories remain the main particle-evidence limit |
| The next historical step, F4, adds a wall-film representation to examine attachment and wall transport; F3 does not establish the missing fates as captured liquid |

## Supporting spatial atlas

<details>
<summary>All saved case contours and vectors</summary>
| Saved snapshot | Liquid, vertical cut | Liquid, inlet slice | Vertical vectors | Inlet vectors |
| --- | --- | --- | --- | --- |
| F3 20.11 m/s 2.5% N11000 | ![F3-20.11-2p5-n11000 liquid](figures/F3-20.11-2p5-n11000-liquid.png) | ![F3-20.11-2p5-n11000 inlet-liquid](figures/F3-20.11-2p5-n11000-inlet-liquid.png) | ![F3-20.11-2p5-n11000 vertical-vectors](figures/F3-20.11-2p5-n11000-vertical-vectors.png) | ![F3-20.11-2p5-n11000 inlet-vectors](figures/F3-20.11-2p5-n11000-inlet-vectors.png) |
| F3 23.46 m/s 2.5% N11000 | ![F3-23.46-2p5-n11000 liquid](figures/F3-23.46-2p5-n11000-liquid.png) | ![F3-23.46-2p5-n11000 inlet-liquid](figures/F3-23.46-2p5-n11000-inlet-liquid.png) | ![F3-23.46-2p5-n11000 vertical-vectors](figures/F3-23.46-2p5-n11000-vertical-vectors.png) | ![F3-23.46-2p5-n11000 inlet-vectors](figures/F3-23.46-2p5-n11000-inlet-vectors.png) |
| F3 26.81 m/s 2.5% N11000 | ![F3-26.81-2p5-n11000 liquid](figures/F3-26.81-2p5-n11000-liquid.png) | ![F3-26.81-2p5-n11000 inlet-liquid](figures/F3-26.81-2p5-n11000-inlet-liquid.png) | ![F3-26.81-2p5-n11000 vertical-vectors](figures/F3-26.81-2p5-n11000-vertical-vectors.png) | ![F3-26.81-2p5-n11000 inlet-vectors](figures/F3-26.81-2p5-n11000-inlet-vectors.png) |
| F3 32.14 m/s 2.5% N11000 | ![F3-32.14-2p5-n11000 liquid](figures/F3-32.14-2p5-n11000-liquid.png) | ![F3-32.14-2p5-n11000 inlet-liquid](figures/F3-32.14-2p5-n11000-inlet-liquid.png) | ![F3-32.14-2p5-n11000 vertical-vectors](figures/F3-32.14-2p5-n11000-vertical-vectors.png) | ![F3-32.14-2p5-n11000 inlet-vectors](figures/F3-32.14-2p5-n11000-inlet-vectors.png) |
| F3 26.81 m/s 5% N11000 | ![F3-26.81-5-n11000 liquid](figures/F3-26.81-5-n11000-liquid.png) | ![F3-26.81-5-n11000 inlet-liquid](figures/F3-26.81-5-n11000-inlet-liquid.png) | ![F3-26.81-5-n11000 vertical-vectors](figures/F3-26.81-5-n11000-vertical-vectors.png) | ![F3-26.81-5-n11000 inlet-vectors](figures/F3-26.81-5-n11000-inlet-vectors.png) |
| F3 26.81 m/s 2.5% averaged N25000 | ![F3-26p81-averaged liquid](figures/F3-26p81-averaged-liquid.png) | ![F3-26p81-averaged inlet-liquid](figures/F3-26p81-averaged-inlet-liquid.png) | ![F3-26p81-averaged vertical-vectors](figures/F3-26p81-averaged-vertical-vectors.png) | ![F3-26p81-averaged inlet-vectors](figures/F3-26p81-averaged-inlet-vectors.png) |
| F3 32.14 m/s 2.5% averaged N15000 | ![F3-32p14-averaged liquid](figures/F3-32p14-averaged-liquid.png) | ![F3-32p14-averaged inlet-liquid](figures/F3-32p14-averaged-inlet-liquid.png) | ![F3-32p14-averaged vertical-vectors](figures/F3-32p14-averaged-vertical-vectors.png) | ![F3-32p14-averaged inlet-vectors](figures/F3-32p14-averaged-inlet-vectors.png) |
| F3 20.11 m/s 2.5% averaged N20000 | ![F3-20p11-averaged liquid](figures/F3-20p11-averaged-liquid.png) | ![F3-20p11-averaged inlet-liquid](figures/F3-20p11-averaged-inlet-liquid.png) | ![F3-20p11-averaged vertical-vectors](figures/F3-20p11-averaged-vertical-vectors.png) | ![F3-20p11-averaged inlet-vectors](figures/F3-20p11-averaged-inlet-vectors.png) |
| F3 26.81 m/s 5% held sources N20000 | ![F3-26p81-5pct-n20000 liquid](figures/F3-26p81-5pct-n20000-liquid.png) | ![F3-26p81-5pct-n20000 inlet-liquid](figures/F3-26p81-5pct-n20000-inlet-liquid.png) | ![F3-26p81-5pct-n20000 vertical-vectors](figures/F3-26p81-5pct-n20000-vertical-vectors.png) | ![F3-26p81-5pct-n20000 inlet-vectors](figures/F3-26p81-5pct-n20000-inlet-vectors.png) |

| Item | Supporting spatial atlas |
| --- | --- |
| — | Columns show separate native liquid contours and mixture-vector views |
| Shared planes, scales and source identities | are specified below |
| SIMPLE and continuation snapshots have their own horizons and | are not substitutes for matched pilot controls |

</details>

## Figure provenance and claim limits

| Item | Figure provenance and claim limits |
| --- | --- |
| Spatial images | are native Fluent 2025 R2 exports from verified case/data pairs |
| vertical cut | is `z = 0`; the horizontal cut is `y = 2.065999985 m`, the midpoint of the measured steam-inlet elevation bounds |
| Vertical axis | is `y` |
| Liquid volume fraction | uses `0–1`; mixture velocity colours use `0–100 m/s` |
| Bulk slice vectors | are in-plane, fixed-length, use shared scale `0.1`, and show every available vector (`skip = 0`) |

<details>
<summary>Supporting detail — Figure provenance and claim limits</summary>

| Item | Figure provenance and claim limits |
| --- | --- |
| — | They show projected direction; colour represents full mixture speed |
|  | Pressure contours use a shared gauge-pressure range `1110–1220 kPa` |
| Evidence | [hash-verified case catalog](../../../../PyAnsys/output/phase8-storyline-20260930/catalog.json), [native export receipt](../../../../PyAnsys/output/phase8-storyline-20260930/export-receipt.json), [surface/range receipt](../../../../PyAnsys/output/phase8-storyline-20260930/range-receipt.json) and [plot summary](../../../../PyAnsys/output/phase8-storyline-20260930/summary.json) |
| — | Phase 8 reconstructs the simulation storyline |
| Numerical shortcomings | are observations and interpretation limits, not progression gates |
| Steady native iterations | are not physical time; inventory slopes must not be called physical storage rates |
| No new flow solves | were performed for these results |

</details>

## Retained detailed execution evidence

<details>
<summary>Earlier receipts, numerical assessments and setup detail</summary>

| Item | Retained detailed execution evidence |
| --- | --- |
| Earlier pass/fail terminology below | records the previous numerical screening rule |
| It | is superseded as a Phase 8 progression/completion requirement by the [2026-09-30 clarification](../CONTEXT.md) |

# F3 allocated two-way DPM, 26.81 m/s and 5%

| Item | F3 allocated two-way DPM, 26.81 m/s and 5% |
| --- | --- |
| [first verified child](../../../../PyAnsys/output/phase8-dpm/F2-allocated-050permil-26p81-20260928T143857Z/build.json) | retained the qualified F2 Coupled carrier field, moved `5.846936325 kg/s` of inlet liquid into the seven inert DPM bins, and reduced Eulerian liquid feed to `111.091790175 kg/s` |
| DPM interaction | was on with a source update every carrier iteration |
| Its [run manifest](../../../../PyAnsys/output/phase8-carrier/F3-26p81-5pct-coupled-20260928T144022Z/manifest.json) | records the saved pre-run case/data pair and the interrupted attempt: tracking every update projected about 23 hours per 1,000 carrier iterations |
| No endpoint from that attempt | is used as a result |
| [recovery child](../../../../PyAnsys/output/phase8-dpm/F2-allocated-050permil-26p81-upd100-20260928T144555Z/build.json) | retained the same feed, particle bins, carrier, and two-way interaction while changing the DPM source update interval to `100` flow iterations |

<details>
<summary>Supporting detail — F3 allocated two-way DPM, 26.81 m/s and 5%</summary>

| Item | F3 allocated two-way DPM, 26.81 m/s and 5% |
| --- | --- |
| control | was read back after save/reopen |
| This numerical change | is identified separately from the scientific DPM-allocation contrast and must be matched in F4 |
| — | The [N=11,000 pilot manifest](../../../../PyAnsys/output/phase8-carrier/F3-26p81-5pct-coupled-upd100-20260928T144733Z/manifest.json) verifies the 1,000-iteration extension, saved/reopened pair, common reports, and seven-bin tracking |
|  | Its [last-500 assessment](../../../../PyAnsys/output/phase8-analysis/26p81-f3-5pct-upd100-n11000/assessment.json) does not qualify the carrier: mean absolute Eulerian boundary gap was `1.792 kg/s` (`0.934%` of Eulerian feed), but liquid inventory fell `1,693.113 → 1,676.324 kg` (`-0.03316 kg/steady iteration`) and continuity ranged `0.01403–0.04070` |
| terminal steam-outlet phase-2 flow | was `109.971 kg/s` |
| — | The seven-bin fate summaries counted `163 escaped`, `1,571 trapped`, and `2,557 incomplete` of `4,291` trajectories |
|  | Weighted by the represented `5.846936325 kg/s` droplet feed, `0.1100 kg/s` (`1.88%`) escaped, `1.1187 kg/s` (`19.13%`) trapped, and `4.6182 kg/s` (`78.98%`) remains unresolved |
|  | Incomplete fates cannot be assigned to carryover or capture |
|  | Reverse outlet flow and viscosity limiting persisted |
|  | The pilot wrapper exited nonzero only during cleanup because it called a nonexistent transcript-capture `stop()` method after writing the complete manifest and tracking output |
| final pair | was already saved and reopened, the process exited, and the script now calls `close()` |
| subsequent continuation verifies that the saved N=11,000 pair | is loadable |
| — | The pilot's `DPM Mass Source` Volume Integral report has incorrect dimensions |
|  | Fluent's [field definition](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/flu_ug_fvdefs.html) and [spray tutorial](https://ansyshelp.ansys.com/public/Views/Secured/corp/v242/en/flu_tg/x1-28900018.html) identify the field as a per-cell mass-flow rate and use Volume Sum |
| pilot source values | are excluded from kg/s balance |
| [N=15,000 continuation](../../../../PyAnsys/output/phase8-carrier/F3-26p81-5pct-coupled-upd100-extension-to15000-20260928T151004Z/manifest.json) | retained the same 100-iteration source cadence, saved local 1,000-iteration checkpoints, saved/reopened the final pair, and completed seven-bin tracking |
| — | The corrected native DPM Mass Source Volume Sum read `0 kg/s` over the last 500 iterations, consistent with inert particles and no particle mass transfer |
|  | Its [assessment](../../../../PyAnsys/output/phase8-analysis/26p81-f3-5pct-upd100-n15000/assessment.json) still fails the declared operational carrier gate: mean absolute Eulerian boundary gap `1.646 kg/s` (`0.858%` of Eulerian feed) passes, but phase-2 inventory rose `1,705.531 → 1,713.322 kg` (`+0.01610 kg/steady iteration`) and continuity ranged `0.01546–0.06951` |
| There | was no fatal solver event |
| terminal phase-2 steam-outlet flow | was `110.212 kg/s` |
| — | Of 4,291 tracks, 109 escaped, 1,543 trapped, and 2,639 remained incomplete; weighted represented rates are `0.0752`, `1.1499`, and `4.6218 kg/s` respectively. 79.05% of represented DPM feed is unresolved |
|  | This continuation does not qualify F3 carryover or whole-system separation |
| A bounded [N=20,000 continuation](../../../../PyAnsys/output/phase8-carrier/F3-26p81-5pct-coupled-upd100-extension-to20000-20260929T063006Z/manifest.json) from the verified N15,000 pair | retained the same feed, coupling, 100-iteration particle retracking cadence, and corrected native DPM source sum |
| Its final case/data pair | was saved/reopened and all seven bins were tracked |
| — | The [N19,500–20,000 assessment](../../../../PyAnsys/output/phase8-analysis/26p81-f3-5pct-upd100-n20000/assessment.json) passes the Eulerian boundary gap (`1.277 kg/s`, `0.666%` of feed) and inventory-slope (`+0.00737 kg/steady iteration`) gates but fails continuity (`0.01370–0.02893`, against the `<0.02` gate) |
| inert DPM Mass Source Volume Sum | remains `0 kg/s`; phase-2 steam-outlet flow is `110.364 kg/s` at N20,000 |
| — | Of 4,291 trajectories, 139 escaped, 1,706 trapped, and 2,446 remained incomplete |
| weighted unresolved rate | is `4.3968 kg/s`, 75.20% of injected DPM feed |
| — | The run does not qualify F3 carrier or carryover |
| locally saved native transcript (path in its manifest) | shows repeatable continuity spikes immediately after the DPM retracking coordinates: N17,001–17,007, 17,101–17,106, 17,201–17,207, and 17,301–17,307 exceeded `0.02`, with peaks `0.0269`, `0.0268`, `0.0304`, and `0.0299`, respectively |
| — | Each block settled below `0.02` later in its 100-iteration cycle |
|  | The temporal alignment suggests a source-update-linked oscillation, though it does not by itself identify the mechanism |
|  | Fluent's [2025 R2 DPM interaction guide](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/flu_ug_sec_discrete_use_oview.html) distinguishes particle retracking interval from updating DPM sources each flow iteration |
|  | The next separately named numerical child tests per-flow-iteration source updating while retaining 100-iteration retracking and the same scientific feed |
|  | The [source-update recovery child](../../../../PyAnsys/output/phase8-carrier/F3-26p81-5pct-coupled-upd100-source-every-iteration-extension-to21000-20260929T083005Z/manifest.json) ran independently from the verified N20,000 pair for one 1,000-iteration block |
|  | Its interaction switch persisted after save/reopen, with particle retracking still every 100 iterations |
|  | Its [N20,500–21,000 assessment](../../../../PyAnsys/output/phase8-analysis/26p81-f3-5pct-upd100-source-every-iter-n21000/assessment.json) worsened: mean Eulerian boundary gap `2.983 kg/s` (`1.555%` of feed), continuity `0.02181–0.12862`, and inventory slope `+0.00500 kg/steady iteration` |
|  | Of the represented DPM feed, `71.11%` still had incomplete trajectories |
|  | Updating held sources each flow iteration alone does not qualify F3 |
| A first [source-relaxation setup attempt](../../../../PyAnsys/output/phase8-carrier/F3-26p81-5pct-coupled-upd100-source-every-iteration-dpmurf0p05-extension-to21000-20260929T085720Z/manifest.json) stopped before iterations because ordinary `solution.controls.under_relaxation` | is inactive in this Coupled/Global Time Step case |
| — | It saved no new endpoint; the N20,000 parent pair remained intact |
|  | A live Fluent readback found the active `solution.controls.pseudo_time_explicit_relaxation_factor.global_dt_pseudo_relax.dpm` control at `0.5` |
|  | The [corrected child](../../../../PyAnsys/output/phase8-carrier/F3-26p81-5pct-coupled-upd100-source-every-iteration-dpmurf0p05-extension-to21000-20260929T090014Z/manifest.json) restarted independently from N20,000 with per-flow-iteration held-source updates, 100-iteration retracking, and this DPM source factor reduced to `0.05` |
|  | The factor and interaction switch persisted after save/reopen |
|  | Its [N20,500–21,000 assessment](../../../../PyAnsys/output/phase8-analysis/26p81-f3-5pct-upd100-source-every-iter-dpmurf0p05-n21000/assessment.json) also fails: mean Eulerian boundary gap `3.573 kg/s` (`1.863%` of feed), phase-2 inventory slope `+0.03274 kg/steady iteration`, and continuity `0.02291–0.07144` |
| Weighted incomplete DPM fate | remains `71.01%` |
| — | This child cannot support a carrier or carryover claim |
|  | Because the peaks align with particle retracking every 100 iterations, the next numerical probe shortens that interval to 20 while updating held sources each flow iteration and retaining the recorded default DPM source factor `0.5` |
|  | The pilot starts again from the preserved N20,000 pair, so its scientific feed, PSD, and parent field remain matched |
|  | This tests whether smaller, more frequent source changes stabilize the coupled carrier; it does not assume that they will |
|  | The [retrack-20 child](../../../../PyAnsys/output/phase8-carrier/F3-26p81-5pct-coupled-upd20-source-every-iteration-extension-to21000-20260929T092747Z/manifest.json) completed its 1,000-iteration block with verified save/reopen and seven-bin tracking |
|  | Its [N20,500–21,000 assessment](../../../../PyAnsys/output/phase8-analysis/26p81-f3-5pct-upd20-source-every-iter-n21000/assessment.json) fails more strongly: mean Eulerian boundary gap `5.638 kg/s` (`2.939%` of feed), inventory slope `+0.06642 kg/steady iteration`, and continuity `0.07320–0.32858` |
| Weighted incomplete DPM fate | is `77.04%` |
| — | More frequent retracking combined with per-flow source updating did not stabilize this carrier |
| [next independent child](../../../../PyAnsys/output/phase8-carrier/F3-26p81-5pct-coupled-upd20-extension-to21000-20260929T104950Z/manifest.json) again | used the preserved N20,000 parent and changed only particle retracking from every 100 to every 20 iterations; held DPM sources updated at retracking events as in the parent, and the DPM source factor remained `0.5` |
| Its final pair and all seven bin tracks | were saved/reopened |
| — | The [N20,500–21,000 assessment](../../../../PyAnsys/output/phase8-analysis/26p81-f3-5pct-upd20-held-source-n21000/assessment.json) fails: mean Eulerian boundary gap `4.735 kg/s` (`2.469%` of feed), inventory slope `+0.05771 kg/steady iteration`, and continuity `0.03887–0.13495` |
| Weighted incomplete DPM fate | is `72.15%` |
| — | More frequent retracking with held sources also did not qualify the 5% point |
| next discovery point | is the human-selected 2.5% allocation at the same `26.81 m/s` speed |
| — | Its [verified child](../../../../PyAnsys/output/phase8-dpm/F2-allocated-025permil-26p81-upd100-20260929T122258Z/build.json) starts independently from the qualified F2 N10,000 carrier, retains the seven-bin PSD and update-100 held-source numerics, and reads back `2.9234681625 kg/s` DPM plus `114.0152583375 kg/s` Eulerian liquid |
|  | The [N=11,000 pilot](../../../../PyAnsys/output/phase8-carrier/F3-26p81-2p5pct-coupled-upd100-20260929T122436Z/manifest.json) saved/reopened its final pair and completed seven-bin tracking |
|  | Its [last-500 assessment](../../../../PyAnsys/output/phase8-analysis/26p81-f3-2p5pct-upd100-n11000/assessment.json) passes mean absolute Eulerian boundary gap (`0.3043 kg/s`, `0.156%` of feed) but narrowly fails phase-2 inventory drift (`-0.01028 kg/steady iteration` versus the `0.01` limit) and continuity (`0.01363–0.02676` versus the `<0.02` limit) |
| inert DPM Mass Source Volume Sum | is `0 kg/s` |
| — | Of 4,291 tracks, 148 escaped, 1,451 trapped, and 2,692 incomplete; weighted unresolved DPM feed is `2.3186 kg/s` (`79.31%`) |
|  | Thus halving loading did not qualify the N11,000 carrier or carryover |
|  | The [N=15,000 continuation](../../../../PyAnsys/output/phase8-carrier/F3-26p81-2p5pct-coupled-upd100-extension-to15000-20260929T132411Z/manifest.json) saved local N12,000–14,000 checkpoints and a shared final pair, reopened the latter, and completed all seven-bin tracks |
|  | Its [N14,500–15,000 assessment](../../../../PyAnsys/output/phase8-analysis/26p81-f3-2p5pct-upd100-n15000/assessment.json) passes Eulerian boundary gap (`0.830 kg/s`, `0.426%` of feed) and liquid inventory slope (`+0.00320 kg/steady iteration`), but continuity still peaks at `0.02481` above the `<0.02` gate |
| inert DPM Mass Source Volume Sum | remains `0 kg/s` |
| — | Of 4,291 trajectories, 158 escaped, 1,478 trapped, and 2,655 incomplete; weighted unresolved DPM feed is `2.3168 kg/s` (`79.25%`) |
|  | Lower loading has not qualified F3 |
|  | An attempted source-factor-only child stopped before iterations because the runner requires per-flow-iteration DPM source updates when reducing the factor to `0.1`; its [blocked manifest](../../../../PyAnsys/output/phase8-carrier/F3-26p81-2p5pct-coupled-upd100-dpmurf0p1-extension-to16000-20260929T152341Z/manifest.json) has no checkpoint, and the N15,000 parent remains intact |
|  | The separately named [N16,000 child](../../../../PyAnsys/output/phase8-carrier/F3-26p81-2p5pct-coupled-upd100-source-every-iteration-dpmurf0p1-extension-to16000-20260929T152528Z/manifest.json) combines per-flow held-source updates with a DPM pseudo-time source factor of `0.1` while keeping particle retracking every 100 iterations |
| Its final pair | was saved/reopened and all seven bins tracked |
| — | The [N15,500–16,000 assessment](../../../../PyAnsys/output/phase8-analysis/26p81-f3-2p5pct-upd100-source-every-iter-dpmurf0p1-n16000/assessment.json) fails continuity (`0.01601–0.03803`) while passing Eulerian boundary gap (`1.519 kg/s`, `0.780%` of feed) and inventory slope (`+0.00798 kg/steady iteration`) |
| Weighted incomplete DPM fate | is `2.2936 kg/s` (`78.45%`) |
| — | The two-control recovery worsened continuity relative to its N15,000 parent (`0.02481`) and does not qualify F3 |
|  | Fluent 2025 R2's [DPM guide](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/flu_ug_sec_discrete_use_oview.html) describes linearized momentum source terms as a steady-flow stability option; the [N16,000 linearization child](../../../../PyAnsys/output/phase8-carrier/F3-26p81-2p5pct-coupled-upd100-linearized-sources-extension-to16000-20260929T162746Z/manifest.json) ran independently from the preserved N15,000 pair with source-term linearization enabled (`false` to `true`), while the 100-iteration retracking and held-source settings remained unchanged |
|  | The setting persisted after save/reopen of both start and final pairs |
|  | Its [N15,500–16,000 assessment](../../../../PyAnsys/output/phase8-analysis/26p81-f3-2p5pct-upd100-linearized-sources-n16000/assessment.json) passes Eulerian boundary gap (`0.990 kg/s`, `0.509%` of feed) but fails inventory drift (`-0.02548 kg/steady iteration`) and continuity (`0.01433–0.03213`) |
| Weighted incomplete DPM fate | remains `79.05%` |
| — | Linearization did not qualify this steady carrier |
|  | Fluent 2025 R2's [node-based DPM averaging guidance](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/flu_ug_sec_discrete_use_oview.html) says that spreading parcel sources to neighboring cells smooths their effect |
|  | A first [setup attempt](../../../../PyAnsys/output/phase8-carrier/F3-26p81-2p5pct-coupled-upd100-averaged-sources-extension-to16000-20260929T172651Z/manifest.json) stopped before iterations because the runner checked the wrong readback key; Fluent actually exposed `source_avg_enabled: true` when node averaging was on |
|  | A second [setup attempt](../../../../PyAnsys/output/phase8-carrier/F3-26p81-2p5pct-coupled-upd100-averaged-sources-extension-to16000-20260929T172804Z/manifest.json) stopped before iterations because Fluent hid the now-inactive source-linearization leaf after save/reopen; the value was `false` before enabling node averaging |
| runner now normalizes that hidden inactive leaf and | retains the raw readback in its manifest |
| [corrected child](../../../../PyAnsys/output/phase8-carrier/F3-26p81-2p5pct-coupled-upd100-averaged-sources-extension-to16000-20260929T172954Z/manifest.json) has passed start-pair save/reopen readback and | is running from the preserved N15,000 pair with the same feed, 100-iteration retracking, and held-source cadence |
| — | It changes node-based averaging from off to on with `source_avg_enabled: true` |
| final pair | was saved/reopened, and seven-bin tracking completed |
| — | Its [N15,500–16,000 assessment](../../../../PyAnsys/output/phase8-analysis/26p81-f3-2p5pct-upd100-averaged-sources-n16000/assessment.json) passes Eulerian boundary gap (`0.976 kg/s`, `0.501%` of feed) and inventory slope (`+0.00466 kg/steady iteration`), but continuity peaks at `0.02154`, narrowly above the `<0.02` gate |
| Weighted incomplete DPM fate | is `2.3740 kg/s` (`81.20%`) |
| This | is the closest F3 carrier gate so far, though droplet fate remains unresolved |
| — | A first continuation attempt [stopped before iterations](../../../../PyAnsys/output/phase8-carrier/F3-26p81-2p5pct-coupled-upd100-extension-to20000-20260929T182601Z/manifest.json) because the runner expected a linearization field that Fluent hides while node averaging is active |
| corrected [N20,000 continuation](../../../../PyAnsys/output/phase8-carrier/F3-26p81-2p5pct-coupled-upd100-averaged-sources-extension-to20000-20260929T182724Z/manifest.json) | retained averaging after save/reopen, saved local N17,000–19,000 checkpoints and a shared final pair, and completed seven-bin tracking |
| — | Its [N19,500–20,000 assessment](../../../../PyAnsys/output/phase8-analysis/26p81-f3-2p5pct-upd100-averaged-sources-n20000/assessment.json) passes Eulerian boundary gap (`0.833 kg/s`, `0.428%` of feed) and inventory slope (`+0.00402 kg/steady iteration`) but still narrowly misses continuity (`0.01219–0.02032`) |
| Weighted incomplete DPM fate | remains `2.3528 kg/s` (`80.48%`) |
| No F3 carrier or carryover claim | is qualified |
| DPM model's `numerics.source_term_settings.underrelaxation_factor` and Coupled pseudo-time `global_dt_pseudo_relax.dpm` | are two Fluent readback paths for the same saved control in this case |
| — | A [readback probe](../../../../PyAnsys/output/phase8-carrier/F3-26p81-2p5pct-coupled-upd100-source-every-iteration-modelurf0p2-averaged-sources-extension-to21000-20260929T203006Z/manifest.json) set the model path to `0.2` and found the pseudo-time path at `0.2` after start-pair reopen; its old assertion treated the paths as independent and stopped before iterations |
|  | A separate live reopen of the earlier 0.1 child read `0.1` on both paths |
|  | Thus the earlier 0.1 test did change the DPM model source relaxation factor; it was not a separate untested numerical control |
|  | After correcting the alias verification, the [N21,000 child](../../../../PyAnsys/output/phase8-carrier/F3-26p81-2p5pct-coupled-upd100-source-every-iteration-dpmurf0p2-averaged-sources-extension-to21000-20260929T203359Z/manifest.json) read back source averaging, per-flow source updates, and `0.2` on both URF paths after start-pair save/reopen |
|  | Its final pair also saved/reopened and all seven bins tracked |
|  | The [N20,500–21,000 assessment](../../../../PyAnsys/output/phase8-analysis/26p81-f3-2p5pct-upd100-averaged-perflow-urf0p2-n21000/assessment.json) passes mean absolute Eulerian boundary gap (`1.940 kg/s`, `0.996%` of feed) but fails inventory slope (`+0.01807 kg/steady iteration`) and continuity (`0.01571–0.02660`) |
| Weighted unresolved DPM feed | is `2.2752 kg/s` (`77.82%`) |
| — | The combined numerical controls did not qualify F3 |
| independent N20,000 averaged-source parent | remains the best operational carrier candidate; its continuity peak improved from `0.02154` at N16,000 to `0.02032` at N20,000 |
| — | A predeclared unchanged continuation to N25,000 will test whether deeper carrier development crosses the gate |
| Incomplete DPM fates | remain a separate claim limit |
| — | The unchanged averaged-source [N=25,000 continuation](../../../../PyAnsys/output/phase8-carrier/F3-26p81-2p5pct-coupled-upd100-averaged-sources-extension-to25000-20260929T213211Z/manifest.json) from the preserved N20,000 pair completed its declared 5,000-iteration block, retained the same 2.5% allocation and source controls, saved local intermediate checkpoints, saved/reopened the selected shared final case/data pair, and tracked all seven bins |
|  | Its [N24,500–25,000 assessment](../../../../PyAnsys/output/phase8-analysis/26p81-f3-2p5pct-upd100-averaged-sources-n25000/assessment.json) passes the declared Eulerian carrier window: mean absolute boundary gap `0.5645 kg/s` (`0.290%` of feed), phase-2 inventory slope `-0.00143 kg/steady iteration`, continuity `0.01245–0.01964`, and no fatal solver event |
| inert DPM Mass Source Volume Sum | remains `0 kg/s` |
| Terminal phase-2 steam-outlet flow | is `113.629 kg/s`; this closed-bottom setup still routes nearly all Eulerian liquid to the steam outlet |
| — | Of 4,291 tracked trajectories, 174 escaped, 1,298 trapped, and 2,819 remained incomplete |
| represented unresolved DPM feed | is `2.3975 kg/s` (82.01%) |
| — | Thus F3 has its first operationally qualified 2.5% coupled carrier window, but neither droplet carryover nor whole-system separation is qualified |
|  | The next independent diagnostic must determine whether incomplete tracks reflect the step cap or persistent recirculation; no escaped-plus-trapped total may silently absorb this unresolved fraction |
|  | A separate [200,000-step two-bin tracking probe](../../../../PyAnsys/output/phase8-dpm/F3-26.81-n25000-dpm-maxsteps-200000-20260929T234513Z/probe.json) reopened the hash-verified N25,000 pair and changed only the unsaved DPM postprocessing step cap from 50,000 |
|  | The 14 µm bin remained at 612 incomplete plus one steam-outlet escape out of 613; the 49 µm bin improved from 404 incomplete and 209 trapped to 192 incomplete and 421 trapped out of 613 |
|  | The cap therefore materially truncates at least the 49 µm fate, whereas most 14 µm trajectories remain unresolved even after four times as many tracking steps |
|  | A separate all-seven-bin probe at the same cap quantified the represented mass-weighted effect |
|  | The independent [all-seven-bin 200,000-step probe](../../../../PyAnsys/output/phase8-dpm/F3-26.81-n25000-dpm-maxsteps-200000-20260929T234829Z/probe.json) completed on the same hash-verified pair without flow iterations or case replacement |
|  | The [mass-weighted comparison](../../../../PyAnsys/output/phase8-analysis/26p81-f3-2p5pct-dpm-200k-step-sensitivity/summary.json) changes escaped/trapped/incomplete represented feed from `2.01% / 15.98% / 82.01%` at 50,000 steps to `2.40% / 24.06% / 73.55%` at 200,000 steps |
|  | The 49 µm bin accounts for most recovered trapped trajectories; 7 µm incomplete falls from 277 to 226, while 14, 24, and 35 µm counts are unchanged |
|  | Their incomplete residence times grow roughly fourfold with the step cap (for example 24 µm mean `23.19 → 92.85 s`), consistent with prolonged unresolved motion rather than a fixed elapsed-time cutoff |
| This | is evidence of tracking-cap sensitivity, not proof that the remaining trajectories are permanently trapped |
| — | A bounded 500,000-step check on 24 and 35 µm then tested whether further tracking changed these fates |
|  | The [500,000-step two-bin probe](../../../../PyAnsys/output/phase8-dpm/F3-26.81-n25000-dpm-maxsteps-500000-20260929T235645Z/probe.json) completed without changing the preserved carrier |
| 24 µm bin | is still `613/613` incomplete; the 35 µm bin is still `597/613` incomplete and `16/613` trapped |
| — | Their mean incomplete residence times rose from `92.85 → 231.2 s` and `111.0 → 278.4 s`, respectively, between 200,000 and 500,000 steps |
| Increasing the cap further | is unlikely to resolve these two bins in this saved steady field |
| Persistent recirculation or another geometry/trajectory mechanism | remains an inference, not a proven fate |
| best all-bin evidence | is still the 200,000-step result with 73.55% of represented DPM feed unresolved; no F3 carryover efficiency is claimed |
| — | At the highest selected speed, the independently built [32.14 m/s, 2.5% child](../../../../PyAnsys/output/phase8-dpm/F2-allocated-025permil-32p14-upd100-20260930T000620Z/build.json) preserved the qualified F2 N10,000 parent and read back `136.682223 kg/s` Eulerian liquid, `3.504672 kg/s` injected DPM, and `96.747183 kg/s` vapor |
|  | The [N11,000 pilot](../../../../PyAnsys/output/phase8-carrier/F3-32p14-2p5pct-coupled-upd100-20260930T000902Z/manifest.json) saved/reopened its final pair and tracked all seven bins |
|  | Its [N10,500–11,000 assessment](../../../../PyAnsys/output/phase8-analysis/32p14-f3-2p5pct-upd100-n11000/assessment.json) passes the Eulerian boundary-gap check (`1.953 kg/s`, `0.837%` of feed) but fails phase-2 inventory slope (`-0.03838 kg/steady iteration`) and continuity (`0.01294–0.02432`) |
| Weighted incomplete DPM fate | is `3.0195 kg/s` (86.16%) |
| — | This short pilot does not qualify a speed effect or carryover; a separately named node-averaged-source continuation will test numerical recovery without changing feed or PSD |
| [32.14 m/s node-averaged-source continuation to N15,000](../../../../PyAnsys/output/phase8-carrier/F3-32p14-2p5pct-coupled-upd100-averaged-sources-extension-to15000-20260930T003916Z/manifest.json) | retained the pilot's mass allocation, seven bins, and 100-iteration DPM retracking cadence; node averaging persisted after save/reopen |
| Local intermediate checkpoints and the selected shared final pair | were saved, the latter reopened, and all seven bins tracked |
| — | Its [N14,500–15,000 assessment](../../../../PyAnsys/output/phase8-analysis/32p14-f3-2p5pct-averaged-sources-n15000/assessment.json) passes the declared Eulerian carrier window: mean absolute boundary gap `1.206 kg/s` (`0.517%` of feed), phase-2 inventory slope `+0.00556 kg/steady iteration`, continuity `0.01180–0.01668`, and no fatal solver event |
| Terminal phase-2 steam-outlet flow | is `135.683 kg/s`; the closed bottom still gives poor Eulerian liquid routing |
| inert DPM Mass Source Volume Sum | is `0 kg/s` |
| — | Baseline 50,000-step tracking leaves `2.9228 kg/s` (83.40%) of represented DPM feed incomplete |
|  | This supports a second operational F3 carrier point but no carryover comparison |
| Apply the same 200,000-step all-bin postprocessing protocol | used at 26.81 m/s before judging any speed effect on particle fate |
| — | The hash-matched [32.14 m/s all-bin 200,000-step probe](../../../../PyAnsys/output/phase8-dpm/F3-32.14-n15000-dpm-maxsteps-200000-20260930T023545Z/probe.json) completed without changing the carrier |
|  | Its [feed-weighted analysis](../../../../PyAnsys/output/phase8-analysis/32p14-f3-2p5pct-dpm-200k-step-sensitivity/summary.json) changes escaped/trapped/incomplete fractions from `1.94% / 14.66% / 83.40%` at 50,000 steps to `2.77% / 18.95% / 78.27%` at 200,000 steps |
| At the matched cap, the 26.81 m/s endpoint | is `2.40% / 24.06% / 73.55%` respectively |
| 14, 24, and 35 µm high-speed bins | remain `613/613` incomplete even after 200,000 steps |
| — | Both carriers pass the operational window, but a few-percent difference in escaped fraction cannot support a carryover-speed claim while roughly three quarters of represented feed lacks a terminal fate |
|  | The independent [20.11 m/s, 2.5% child](../../../../PyAnsys/output/phase8-dpm/F2-allocated-025permil-20p11-upd100-20260930T024344Z/build.json) starts from the qualified same-speed F2 N10,000 carrier and read back `85.522076 kg/s` Eulerian liquid, `2.192874 kg/s` injected DPM, and `60.534718 kg/s` vapor |
|  | Its [N11,000 pilot](../../../../PyAnsys/output/phase8-carrier/F3-20p11-2p5pct-coupled-upd100-20260930T024531Z/manifest.json) saved/reopened the final pair and completed all seven-bin tracking |
|  | The [N10,500–11,000 assessment](../../../../PyAnsys/output/phase8-analysis/20p11-f3-2p5pct-upd100-n11000/assessment.json) passes the boundary-gap (`0.878 kg/s`, `0.601%` of feed) and phase-2 inventory-slope (`-0.00227 kg/steady iteration`) checks, but continuity reaches `0.03205` above the `<0.02` gate |
| 50,000-step weighted incomplete DPM fate | is `1.4762 kg/s` (67.32%) |
| pilot | is unqualified; a node-averaged-source continuation tests whether the same numerical recovery used at 26.81 and 32.14 m/s produces a qualifying carrier |
| [20.11 m/s averaged-source N15,000 child](../../../../PyAnsys/output/phase8-carrier/F3-20p11-2p5pct-coupled-upd100-averaged-sources-extension-to15000-20260930T033606Z/manifest.json) | retained the same 2.5% feed, seven bins, and 100-iteration source cadence, with node averaging verified after save/reopen |
| — | It saved local checkpoints and reopened the selected final pair; all bins tracked |
|  | Its [N14,500–15,000 assessment](../../../../PyAnsys/output/phase8-analysis/20p11-f3-2p5pct-averaged-sources-n15000/assessment.json) passes mean absolute Eulerian boundary gap (`0.617 kg/s`, `0.423%` of feed) but fails phase-2 inventory slope (`-0.01859 kg/steady iteration`) and continuity (`0.01488–0.02491`) |
| Weighted incomplete DPM fate | is `1.6103 kg/s` (73.43%) at the baseline 50,000-step cap |
| — | The numerically changed child does not qualify this low-speed carrier |
|  | An unchanged deeper N20,000 continuation tests whether its last-500 window settles; no speed or carryover claim is made from this result |
| unchanged [20.11 m/s continuation to N20,000](../../../../PyAnsys/output/phase8-carrier/F3-20p11-2p5pct-coupled-upd100-averaged-sources-extension-to20000-20260930T053945Z/manifest.json) | retained source averaging and the same feed, saved local checkpoints and a selected shared final pair, reopened the latter, and tracked all seven bins |
| — | Its [N19,500–20,000 assessment](../../../../PyAnsys/output/phase8-analysis/20p11-f3-2p5pct-averaged-sources-n20000/assessment.json) passes boundary gap (`0.746 kg/s`, `0.511%` of feed) and inventory slope (`+0.00282 kg/steady iteration`), but continuity peaks at `0.02628`, above both the `<0.02` gate and the N15,000 peak (`0.02491`) |
| Weighted incomplete DPM fate | is `1.5518 kg/s` (70.77%) at 50,000 steps |
| — | This deeper unchanged branch does not qualify the low-speed carrier and offers no improving continuity trend |
| It | remains a preserved diagnostic endpoint; 200,000-step fate comparison is deferred because the carrier gate failed |

</details>

</details>
