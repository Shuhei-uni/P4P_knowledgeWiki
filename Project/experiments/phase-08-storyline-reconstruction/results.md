# Phase 8 results — reconstructing the model-development storyline

Phase 8 reconstructs how successive modelling choices changed the simulated liquid behaviour on the common 60,964-cell simplified geometry. The runs reproduce three parts of that history: mixed versus split inlet feed, allocated coupled droplets, and a provisional wall-film treatment. **The purpose is to explain the simulation history leading to the current model. Closing mass imbalance and reducing continuity are supporting diagnostics, not Phase 8 completion objectives.**

The main finding is that each added representation changes what can be observed. Splitting the inlet changes retained liquid without materially resolving steam-outlet routing. Coupled DPM reveals diameter-dependent transport but leaves most represented droplet feed unresolved. EWF produces measurable film and a large bulk-response change, while its available accounting remains insufficient to explain that change as liquid removal. These findings provide the evidence behind the progression toward later liquid-removal and wall-treatment work.

## Scope and comparison basis

These are new-mesh reconstructions, rather than the original historical simulation files or a quantitative replay of a published separator. F1/F2 revisit [Phases 1–2 inlet development](../phase-01-purnanto-baseline-and-inlet-exploration/interpretation.md); F3 revisits [Phase 3 droplet representation](../phase-03-dpm-carryover-and-coupling/interpretation.md); F4 revisits [Phase 4 film mechanisms](../phase-04-ewf-wall-film-mechanisms/interpretation.md). The five speed points are the Phase 8 design, with 26.81 m/s as the reference.

| Comparison | What changes | Saved evidence used here |
| --- | --- | --- |
| F1 → F2 | Mixed feed on both inlet faces → pure-phase split feed | Five matched speeds; Coupled carriers at N10,000 and F1 SIMPLE comparison |
| F2 → F3 | Full Eulerian feed → allocated liquid DPM with feedback | Four 2.5% speed pilots and one 5% reference pilot at N11,000 |
| F3 → F4 | Coupled DPM → provisional E2.7-based EWF package | Matched 26.81 m/s, 5% pilots at N11,000 |

All four families retain a closed bottom and have no absorber. F1 applies the same mixed-phase condition to both original inlet faces. Its two-face SIMPLE series and Coupled recovery series now have matched N10,000 endpoints and windows; a separate merged single-inlet SIMPLE pilot remains a different setup recreation. F3/F4 comparisons change liquid allocation as well as coupling or film treatment, so the stages cannot be ranked as isolated physical improvements.

## Finding 1 — the split inlet changes retention more than outlet routing

The split inlet was introduced to represent liquid and steam entering different parts of the opening. Figure 1 tests whether that representation changes the carrier response across the common speed sweep.

![Figure 1: matched F1 F2 speed response](<C:/Users/Shuhei Yokkaichi/Documents/CFD/P4P_knowledgeWiki/Project/experiments/phase-08-storyline-reconstruction/figures/f1-f2-speed-comparison.png>)

*Figure 1. F1 mixed-feed and F2 split-feed Coupled carriers at five nominal speeds, each independently initialized and run to N10,000. Routing and area-weighted steam-face-to-outlet pressure difference use the final-500 window; inventory is the final saved value. The narrow outlet-axis range highlights small differences: every point remains above 99%.*

F1's final inventory rises from 1,021.5 to 1,629.6 kg with speed, whereas F2 retains 1,719–1,911 kg and has a shallow minimum at 23.46 m/s. At 26.81 m/s, F2 retains 1,734.5 kg compared with F1's 1,262.6 kg: about 472 kg, or 37%, more. The pressure difference rises with speed in both families and is slightly higher in F2 at every point. Yet the outlet fractions remain 99.65–99.73% in F1 and 99.38–99.43% in F2. The clear representation effect is on the internal state; neither carrier supplies an effective liquid-removal path in this geometry.

| F1-26.81-n10000 | F2-26.81-n10000 |
| --- | --- |
| ![F1-26.81-n10000 liquid](<C:/Users/Shuhei Yokkaichi/Documents/CFD/P4P_knowledgeWiki/Project/experiments/phase-08-storyline-reconstruction/f1-one-inlet/figures/F1-26.81-n10000-liquid.png>) | ![F2-26.81-n10000 liquid](<C:/Users/Shuhei Yokkaichi/Documents/CFD/P4P_knowledgeWiki/Project/experiments/phase-08-storyline-reconstruction/f2-split-inlet/figures/F2-26.81-n10000-liquid.png>) |

*Figure 2. Reference-speed vertical liquid-volume-fraction contours, N10,000, `z = 0`, common range 0–1. F2 has a deeper liquid-enriched lower region; both retain outer-wall enrichment and comparatively low liquid volume fraction in much of the central bulk.*

The contour difference supports the inventory measurement but does not quantify it: a plane samples only part of the volume. The larger retained mass is established by the domain report, rather than inferred from coloured area. Retained liquid also differs from removed liquid; the closed lower boundary limits what this redistribution can mean for separator performance.

| F1-26.81-n10000 | F2-26.81-n10000 |
| --- | --- |
| ![F1-26.81-n10000 inlet-vectors](<C:/Users/Shuhei Yokkaichi/Documents/CFD/P4P_knowledgeWiki/Project/experiments/phase-08-storyline-reconstruction/f1-one-inlet/figures/F1-26.81-n10000-inlet-vectors.png>) | ![F2-26.81-n10000 inlet-vectors](<C:/Users/Shuhei Yokkaichi/Documents/CFD/P4P_knowledgeWiki/Project/experiments/phase-08-storyline-reconstruction/f2-split-inlet/figures/F2-26.81-n10000-inlet-vectors.png>) |

*Figure 3. Native mixture vectors through inlet height at the same two endpoints. In-plane arrows show circumferential circulation; colour is full mixture speed, shared range 0–100 m/s. Common fixed arrow length and scale permit a direction comparison.*

Both cases retain the same broad circulation direction. The inlet split therefore modifies liquid placement within a circulating carrier instead of introducing a visibly different overall flow topology. This establishes the carrier reference for the later droplet stage.

## Finding 1a — the F1 numerical package changes the matched carrier response

![F1 SIMPLE versus Coupled at matched speeds](<C:/Users/Shuhei Yokkaichi/Documents/CFD/P4P_knowledgeWiki/PyAnsys/output/phase8-analysis/f1-simple-vs-coupled-n10000/f1-simple-vs-coupled-n10000.png>)

| Speed (m/s) | Steam-outlet liquid / feed, Coupled → SIMPLE (%) | Final liquid inventory, Coupled → SIMPLE (kg) | Pressure difference, Coupled → SIMPLE (kPa) |
| ---: | ---: | ---: | ---: |
| 20.11 | 99.728 → 214.437 | 1021.5 → 3802.5 | 43.29 → 107.80 |
| 23.46 | 99.651 → 258.911 | 1110.8 → 5274.2 | 56.18 → 198.18 |
| 26.81 | 99.671 → 360.424 | 1262.6 → 6576.7 | 71.09 → 406.52 |
| 29.48 | 99.653 → 455.273 | 1428.9 → 7339.8 | 84.97 → 546.56 |
| 32.14 | 99.664 → 673.023 | 1629.6 → 8160.3 | 100.88 → 843.23 |

SIMPLE numerical diagnostics, measured over N9,500–10,000:

| Speed (m/s) | SIMPLE mixture boundary gap (% feed) | SIMPLE inventory slope (kg/iteration) | SIMPLE max continuity residual | Reverse-flow messages | Viscosity-limit messages |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 20.11 | 67.27 | 0.486 | 0.256 | 9998 | 9740 |
| 23.46 | 93.42 | 0.582 | 0.389 | 9998 | 9768 |
| 26.81 | 153.14 | 0.741 | 0.680 | 9998 | 9760 |
| 29.48 | 208.93 | 1.111 | 1.086 | 9998 | 9770 |
| 32.14 | 336.85 | 0.047 | 1.162 | 9998 | 9783 |

The F1 two-face feed, mesh and bounded horizon are matched. SIMPLE uses segregated pseudo-time off and second-order k; the Coupled recovery package uses Global Time Step and first-order k. Changes therefore belong to a package comparison and cannot be attributed to the pressure-coupling algorithm alone. The diagnostic thresholds describe numerical limitations; they are not Phase 8 progression gates.

Reference-speed native liquid contours and inlet vectors at matched N10,000 endpoints:

| SIMPLE package | Coupled recovery package |
| --- | --- |
| ![F1-26.81-simple-n10000 liquid](<C:/Users/Shuhei Yokkaichi/Documents/CFD/P4P_knowledgeWiki/Project/experiments/phase-08-storyline-reconstruction/f1-one-inlet/figures/F1-26.81-simple-n10000-liquid.png>)

![F1-26.81-simple-n10000 inlet-vectors](<C:/Users/Shuhei Yokkaichi/Documents/CFD/P4P_knowledgeWiki/Project/experiments/phase-08-storyline-reconstruction/f1-one-inlet/figures/F1-26.81-simple-n10000-inlet-vectors.png>) | ![F1-26.81-n10000 liquid](<C:/Users/Shuhei Yokkaichi/Documents/CFD/P4P_knowledgeWiki/Project/experiments/phase-08-storyline-reconstruction/f1-one-inlet/figures/F1-26.81-n10000-liquid.png>)

![F1-26.81-n10000 inlet-vectors](<C:/Users/Shuhei Yokkaichi/Documents/CFD/P4P_knowledgeWiki/Project/experiments/phase-08-storyline-reconstruction/f1-one-inlet/figures/F1-26.81-n10000-inlet-vectors.png>) |

Historical [08b setup](../phase-02-parity-reset-and-pre-v2-qualification/purnanto-08b-parity-split-inlet/setup.md) and [results](../phase-02-parity-reset-and-pre-v2-qualification/purnanto-08b-parity-split-inlet/results.md) document split `liquidinlet`/`steaminlet` mass-flow boundaries on a 7,601,261-cell mesh and a 58.73% whole-mixture imbalance ratio at N5,000. F1 applies mixed feed to both inlet faces on the 60,964-cell Phase 8 mesh. Although F1 SIMPLE shares the audited 00a SIMPLE, second-order and QUICK method family, it is not a topology- or mesh-identical 08b recreation.

### One-way DPM diagnostics on the SIMPLE carriers

![F1 SIMPLE carrier one-way DPM diagnostic fates](<C:/Users/Shuhei Yokkaichi/Documents/CFD/P4P_knowledgeWiki/PyAnsys/output/phase8-analysis/f1-simple-vs-coupled-n10000/f1-simple-diagnostic-dpm-fates.png>)

| Speed (m/s) | Escaped represented weight (%) | Trapped represented weight (%) | Incomplete represented weight (%) |
| ---: | ---: | ---: | ---: |
| 20.11 | 0.08 | 0.01 | 99.91 |
| 23.46 | 5.12 | 1.24 | 93.65 |
| 26.81 | 0.18 | 11.79 | 88.03 |
| 29.48 | 4.72 | 0.23 | 95.05 |
| 32.14 | 6.19 | 1.32 | 92.49 |

These seven-bin cases use 5% inert, one-way DPM weight, a 50,000-step tracking cap, and the same full-feed Eulerian SIMPLE carriers. The large incomplete share is unresolved trajectory weight. The fates are diagnostic outcomes on numerically poor carriers, not separator efficiency or validated separation.



## Finding 2 — allocated DPM changes the carrier, while most droplet feed remains unresolved

F3 moves 2.5% or 5% of the total liquid feed into the common seven-bin fine-mist DPM distribution and enables feedback to the carrier. Total water feed is unchanged. The reference loading comparison begins from the same-speed F2 N10,000 basis and records the next 1,000 iterations.

![Figure 4: matched F3 loading histories](<C:/Users/Shuhei Yokkaichi/Documents/CFD/P4P_knowledgeWiki/Project/experiments/phase-08-storyline-reconstruction/f3-coupled-dpm/figures/pilot-loading-response.png>)

*Figure 4. Reference-speed 2.5% and 5% F3 pilots, N10,000–11,000, with 100-iteration retracking and held sources. The outlet numerator is Eulerian liquid only, divided by total liquid feed including allocated DPM. Inventory is also Eulerian liquid only; these are not total carryover percentages.*

The 5% pilot exhibits a larger decrease in Eulerian inventory and ends at 1,676.3 kg, compared with 1,715.8 kg at 2.5%. Terminal Eulerian outlet fractions are 94.04% and 96.97%, respectively. Their histories contain overshoot and continued adjustment, so these endpoints describe the bounded pilot response. A lower bulk outlet percentage partly reflects moving liquid out of the Eulerian representation and cannot by itself demonstrate better separation. The [F3 report](f3-coupled-dpm/results.md) also shows that the broad lower-liquid and outer-wall structure persists in the native pilot contours.

![Figure 5: F3 diameter-resolved pilot fates](<C:/Users/Shuhei Yokkaichi/Documents/CFD/P4P_knowledgeWiki/Project/experiments/phase-08-storyline-reconstruction/f3-coupled-dpm/figures/pilot-droplet-fates.png>)

*Figure 5. Saved seven-bin trajectory-count fates for the four 2.5% speed pilots and the 5% reference pilot at N11,000. Green is trapped, blue escaped and orange incomplete. Per-bin trajectory fractions are distinct from the injection-weighted represented-feed fractions quoted below.*

The 14, 24 and 35 µm bins are almost entirely incomplete, while the smallest and largest bins have more completed fates. At the reference 2.5% pilot, the 89 µm trajectories are trapped, but the smallest bin includes escape as well as trapping. This is evidence of diameter-dependent transport, with a large missing middle of the distribution. The injection-weighted unresolved fractions are 79.31% at 2.5% and 78.98% at 5%; roughly 79% of represented DPM feed therefore remains unclassified at both reference pilots.

Across the four 2.5% speed pilots, unresolved represented feed increases from 67.32% at 20.11 m/s to 86.16% at 32.14 m/s, while the trapped fraction falls from 31.18% to 12.11%. That trend describes the recorded fate categories under the chosen controls. It does not establish that faster flow physically reduces capture, because unresolved mass dominates and may change the final allocation. Native trajectory examples in the family report illustrate circulation but do not substitute for these ensemble statistics.

The earlier continuation campaign also exposed a tracking-limit effect. On fixed averaged-source carriers, increasing the cap from 50,000 to 200,000 steps reduced unresolved feed from 82.01% to 73.55% at 26.81 m/s and from 83.40% to 78.27% at 32.14 m/s. Their horizons differ, so they are sensitivity probes rather than matched speed pilots. F3 consequently establishes explicit droplet transport and feedback in the storyline, with incomplete tracking retained as a finding rather than hidden inside an efficiency estimate.

## Finding 3 — EWF forms film and changes bulk routing, but does not explain liquid removal

F4 adds the provisional E2.7-based film package on `wall` to the 26.81 m/s, 5% coupled-droplet setup. The bottom remains excluded and the absorber remains off. Figure 6 compares the same N10,000–11,000 pilot interval with F3.

![Figure 6: matched F3 F4 mechanism histories](<C:/Users/Shuhei Yokkaichi/Documents/CFD/P4P_knowledgeWiki/Project/experiments/phase-08-storyline-reconstruction/f4-coupled-dpm-ewf/figures/f3-f4-mechanism-response.png>)

*Figure 6. Reference-speed 5% F3 and provisional F4 pilot histories. F4 shows much lower Eulerian outlet flow and inventory, accompanied by a large open Eulerian boundary gap. This is a film-package response, with incomplete transfer accounting.*

F4 ends with 25.541 kg/s Eulerian liquid through the steam outlet, equivalent to 21.84% of total liquid feed, and 771.42 kg bulk inventory. The final-500 Eulerian boundary gap averages 80.761 kg/s. The magnitude of the outlet change is clear, but its interpretation depends on the destinations and transfers of the liquid. A low bulk outlet flux alone cannot establish capture or drainage.

| F3-26.81-5-n11000 | F4-26.81-5-n11000 |
| --- | --- |
| ![F3-26.81-5-n11000 liquid](<C:/Users/Shuhei Yokkaichi/Documents/CFD/P4P_knowledgeWiki/Project/experiments/phase-08-storyline-reconstruction/f3-coupled-dpm/figures/F3-26.81-5-n11000-liquid.png>) | ![F4-26.81-5-n11000 liquid](<C:/Users/Shuhei Yokkaichi/Documents/CFD/P4P_knowledgeWiki/Project/experiments/phase-08-storyline-reconstruction/f4-coupled-dpm-ewf/figures/F4-26.81-5-n11000-liquid.png>) |

*Figure 7. Matched 5% F3/F4 vertical bulk-liquid contours at N11,000, common range 0–1. F4 retains a liquid-enriched lower region but has a weaker wall-adjacent band above it. This spatial change agrees with the lower reported bulk inventory.*

![Figure 8: F4 film formation histories](<C:/Users/Shuhei Yokkaichi/Documents/CFD/P4P_knowledgeWiki/Project/experiments/phase-08-storyline-reconstruction/f4-coupled-dpm-ewf/figures/film-response.png>)

*Figure 8. Native F4 film inventory, maximum thickness, cumulative stripped mass and cumulative film outflow over N10,000–11,000. Film inventory continues to rise to 1.321 kg; maximum thickness reaches approximately 0.165 mm. Cumulative quantities are masses, not rates.*

The film is measurable, but it has not reached a stationary inventory at the saved endpoint. Cumulative stripping is 0.1876 kg and film outflow is 0.00546 kg. Those inventories and accumulated masses cannot close a missing mass-flow ledger without compatible transfer-rate accounting. The native film DPM mass-source report was unavailable, and F4 lacks a directly comparable complete particle fate ledger.

| Wall-film thickness | Wall-film velocity |
| --- | --- |
| ![F4-26.81-5-n11000 film-thickness](<C:/Users/Shuhei Yokkaichi/Documents/CFD/P4P_knowledgeWiki/Project/experiments/phase-08-storyline-reconstruction/f4-coupled-dpm-ewf/figures/F4-26.81-5-n11000-film-thickness.png>) | ![F4-26.81-5-n11000 film-vectors](<C:/Users/Shuhei Yokkaichi/Documents/CFD/P4P_knowledgeWiki/Project/experiments/phase-08-storyline-reconstruction/f4-coupled-dpm-ewf/figures/F4-26.81-5-n11000-film-vectors.png>) |

*Figure 9. F4 N11,000 native 3D wall-film views. Thickness uses 0–0.2 mm; film-speed colour uses 0–87 m/s, with vectors assembled from all three recorded film-velocity components. Film concentrates near inlet height and substantial circumferential motion remains visible.*

These fields show film formation and wall transport, without establishing downward drainage. The supported result is that the provisional film treatment changes the represented liquid state strongly. Its accounting limits remain part of the reconstruction and prevent translating the bulk-outlet reduction into a separation-efficiency improvement.

## How these findings lead toward the current model

![Figure 10: reference-speed stage comparison](<C:/Users/Shuhei Yokkaichi/Documents/CFD/P4P_knowledgeWiki/Project/experiments/phase-08-storyline-reconstruction/figures/reference-storyline-response.png>)

*Figure 10. Reference-speed stage summary: full-Eulerian F1/F2 at N10,000 and 5%-allocated F3/F4 at N11,000. Outlet and pressure bars use the final-500 mean; inventories use the endpoint. In particular, the F4 mean outlet bar differs from its 21.84% terminal value. This is a modelling-stage comparison with changing representation and horizon.*

The reconstructed sequence makes the reasons for the model changes visible. Inlet representation changes liquid distribution and retention, yet leaves high bulk outlet routing. DPM adds a separate diameter-dependent transport question and carrier feedback, while exposing unresolved particle fates. EWF adds measurable wall film but raises an unresolved liquid-accounting question. None of these stages provides a demonstrated lower liquid-removal path in the common closed-bottom geometry.

The original [full-geometry brine-outlet investigation](../phase-05-full-geometry-v2/interpretation.md) and [pool-control work](../phase-06-full-geometry-with-brine-pool/interpretation.md) then supply historical context for the return to a simplified removal architecture; they cannot be recreated on this truncated geometry. The later [Phase 7.1A virtual outlet](../phase-07-1a-absorber-convergence/interpretation.md) and [Phase 7.2A wall-treatment investigation](../phase-07-2a-wall-liquid-routing/interpretation.md) own the evidence for those developments. Phase 8 explains this progression without claiming that an absorber-equipped comparison has already been run.

## Coverage and limits of the report

Saved evidence covers 16 of the intended 60 core points: five F1, five F2, five F3 and one provisional F4. Additional SIMPLE, numerical-continuation and tracking-probe snapshots preserve parts of the investigation without increasing core-matrix coverage. Most F3/F4 loading combinations remain absent. The report therefore supports the demonstrated stage contrasts, rather than a complete response surface or an optimum setup.

Steady native iterations do not define physical elapsed time; inventory slopes are not physical storage rates. The common closed-bottom geometry, assumed fine-mist distribution, incomplete DPM fates and provisional film basis bound the conclusions. Mass balance and continuity histories remain in the family reports to make those limits inspectable. They do not determine whether an unresolved stage belongs in the history.

## Supporting family reports and provenance

- [F1 mixed-feed results](f1-one-inlet/results.md): speed response, liquid distribution, diagnostic droplets and separate SIMPLE snapshots.
- [F2 split-feed results](f2-split-inlet/results.md): matched speed response, retention and diagnostic droplet evidence.
- [F3 coupled-droplet results](f3-coupled-dpm/results.md): speed/loading pilots, diameter-resolved fates and numerical/tracking sensitivity.
- [F4 wall-film results](f4-coupled-dpm-ewf/results.md): matched bulk response, film formation and open accounting.

Spatial images are native Fluent 2025 R2 exports from verified case/data pairs. The vertical cut is `z = 0`; the horizontal cut is `y = 2.065999985 m`, the midpoint of the measured steam-inlet elevation bounds. Vertical axis is `y`. Liquid volume fraction uses `0–1`; mixture velocity colours use `0–100 m/s`. Bulk slice vectors are in-plane, fixed-length, use shared scale `0.1`, and show every available vector (`skip = 0`). They show projected direction; colour represents full mixture speed. Pressure contours use a shared gauge-pressure range `1110–1220 kPa`.

Machine evidence: [hash-verified case catalog](../../../PyAnsys/output/phase8-storyline-20260930/catalog.json), [native export receipt](../../../PyAnsys/output/phase8-storyline-20260930/export-receipt.json), [surface/range receipt](../../../PyAnsys/output/phase8-storyline-20260930/range-receipt.json) and [plot summary](../../../PyAnsys/output/phase8-storyline-20260930/summary.json).

The family reports retain complete spatial atlases and earlier execution receipts in supporting sections. All figures derive from preserved saved evidence, with verified source hashes and no new carrier iterations or case/data overwrites. The experimental loop remains paused.
