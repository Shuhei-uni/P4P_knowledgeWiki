# Phase 7b E2 — Weaker-sink results and G2 decision

**Neither weaker sink produced a numerically acceptable steady solution within
5,000 iterations.** All three cases reached N5000 with complete histories and
preserved endpoints. Increasing tau changed the trajectories and liquid
inventory, but did not resolve source-inclusive mass imbalance, inventory
drift or residual excursions. No case is qualified or selected for extension.

The [approved setup](setup.md) changed only the sink time coefficient at fixed
S40 geometry. Both new children used the original common clean N0 parent,
identical Hybrid options and the same physics, mesh, source coupling and
numerics. The original baseline was reused. This remains **Phase 7b E2/G2**.

## Three-point result

![Raw inventory, applied removal and collector crossing histories](../../../../PyAnsys/output/phase07b-g2/G2-inventory-removal.png)

A weaker coefficient did not translate into a proportionately lower realized
source: the collector held more liquid. Its final-window mean liquid mass
rose from 0.941 kg in the baseline to 10.255 kg at tau=0.02 and 43.654 kg at
tau=0.10. Applied removal averaged 390.04, 512.53 and 436.19 kg/s, respectively,
against a measured liquid feed of 116.921 kg/s. Most accumulated liquid was
above the collector. A fixed coefficient therefore does not fix the realized
sink rate.

All means and maxima below use N4501–5000, except the explicitly named earlier
window. The inventory indicator compares N4001–4500 with N4501–5000, normalized
by the larger mean. These are the predeclared windows; none is substituted.

| Measure | S40 baseline | S40-T020 | S40-T100 | Declared indicator |
| --- | ---: | ---: | ---: | --- |
| Tau, s | 0.0024095893 | 0.020 | 0.100 | Only scientific delta |
| Verified disposition | N5000 complete | N5000 complete | N5000 complete | Cap 5000 |
| Earlier mean whole-liquid volume, m³ | 0.69980 | 0.72870 | 0.90381 | — |
| Final-window mean whole-liquid volume, m³ | 0.78573 | 0.89268 | 0.95756 | — |
| Inventory mean change | 10.94% | 18.37% | 5.61% | ≤1%; all fail |
| Mean absolute liquid closure / liquid feed | 252.60% | 354.84% | 312.94% | ≤1%; all fail |
| Mean absolute vapour closure / vapour feed | 2.38% | 3.33% | 2.97% | ≤1%; all fail |
| Mean absolute mixture closure / total feed | 148.49% | 208.59% | 183.95% | ≤1%; all fail |
| Mean liquid carryover / liquid feed | 19.01% | 16.49% | 39.88% | Diagnostic only |
| Mean steam recovery / vapour feed | 97.62% | 96.67% | 97.03% | Diagnostic only |
| Maximum continuity residual | 0.9928 | 1.2497 | 1.4284 | ≤0.001; all fail |
| Maximum k residual | 0.024509 | 0.16321 | 0.037439 | ≤0.001; all fail |
| Maximum epsilon residual | 0.59738 | 32.2 | 3.1356 | ≤0.001; all fail |
| Maximum liquid-fraction residual | 0.012886 | 0.014231 | 0.014794 | ≤0.001; all fail |
| Momentum residuals passing throughout final window | 3/3 | 3/3 | 3/3 | All seven equations required |

Tau=0.10 has the smallest change between the two inventory means, but it still
fails the 1% criterion. Its final-window mass slope is **+0.3309 kg per steady
iteration**, compared with +0.0705 and +0.2316 for baseline and T020. The T100
history falls for part of the window and rises sharply near the end; the
smaller difference between window means is not a steady plateau. Steady
iteration slopes are not physical storage rates.

![Source-inclusive closure and residual comparison](../../../../PyAnsys/output/phase07b-g2/G2-closure-residuals.png)

Closure includes the **native applied source exactly once**. For each new
child, applied removal at N equals the current-field expression at N−1 for
all 4,999 consecutive pairs, with zero difference at stored precision. The
original baseline lag evidence is retained in its analysis. Replacing the
applied source with its current-field value would mix update stages; adding
an inventory slope in kg/iteration would not repair a physical mass balance.

Final-window net delivery to the collector is 389.43, 513.25 and 501.37 kg/s;
applied removal is 390.04, 512.53 and 436.19 kg/s. T100 also has much larger
gross escape (265.43 kg/s versus 35.21 and 98.98). Near agreement between
local delivery and removal in the first two cases coexists with grossly open
whole-vessel balances. Neither that agreement nor a favourable carryover
ratio establishes useful separation. The [Shuhei review](../shuhei-transfer-review.md)
supports this same accounting distinction; none of his different source
control, inlet ramp or numerical settings was transferred to E2.

## Residual-spike observation

Andy's [observation of increased spikiness after roughly N2700](residual-onset.md)
is preserved with the original N4500 diagnostic and its immutable raw snapshot.
It identified sharp epsilon bursts coincident with maximum-speed excursions,
with broader oscillations in the other equations. There was no recorded
configuration change at N2700 and no newly introduced source-update lag.

The terminal records strengthen that observation:

| Case | Largest epsilon in the final window | Iteration | Maximum mixture speed at that same iteration, m/s |
| --- | ---: | ---: | ---: |
| S40 baseline | 0.59738 | 4855 | 614.19 |
| S40-T020 | 32.2 | 4767 | 2477.05 |
| S40-T100 | 3.1356 | 4815 | 1021.40 |

These are numerical excursions in unqualified runs, not credible predictions
of separator velocity. T100's reduced epsilon peak relative to T020 does not
establish a monotonic benefit: its peak still exceeds the baseline, while its
continuity maximum and liquid carryover are higher. Exact coincidence supports
a coupled velocity/turbulence disturbance; integrated histories alone cannot
identify which equation or cells initiated it. N5000 spatial snapshots do not
locate the earlier transient-in-iteration peak.

All seven raw residuals remain visible in the individual
[baseline](../../../../PyAnsys/output/p7b-s040-20260921T013001Z/analysis/residuals.png),
[T020](../../../../PyAnsys/output/p7b-s40-t020-resume-20260921T231240Z/analysis/residuals.png) and
[T100](../../../../PyAnsys/output/p7b-s40-t100-20260922T022956Z/analysis/residuals.png)
plots. [Peak evidence](../../../../PyAnsys/output/phase07b-g2/residual-peak-comparison.json)
links the residual and speed records.

## Matched spatial evidence

The [complete native Fluent gallery](spatial-comparison.md) compares four
horizontal cuts and two full-height centre cuts for all three original N5000
pairs. Phase-2 volume fraction uses a fixed 0–1 scale; the supporting horizontal
mixture-speed contours use 0–120 m/s, rounded outward from the joint surface
maximum of 115.59 m/s. Cameras, planes and ranges match across cases. Every
image passed native-file/hash, source and visual QA.

| Plane | S40 baseline | S40-T020 | S40-T100 |
| --- | --- | --- | --- |
| Full-height x = 0 m | ![S40 baseline, N5000, x0, phase-2-vof](../../../../PyAnsys/output/phase07b-g2/native-axial-label-repair/S40-N5000-x0-liquid.png) | ![S40-T020, N5000, x0, phase-2-vof](../../../../PyAnsys/output/phase07b-g2/native-axial-label-repair/T020-N5000-x0-liquid.png) | ![S40-T100, N5000, x0, phase-2-vof](../../../../PyAnsys/output/phase07b-g2/native-axial-label-repair/T100-N5000-x0-liquid.png) |

All three endpoints show liquid concentrated at the outer wall, with low liquid
fraction over most of the interior. The weaker-sink cases retain localized
liquid in the lower region; the integrated collector masses quantify that
change. At y=3 m the area-mean liquid fraction is about 0.05–0.06 in each new
child despite local wall values near 0.98. Thin high-alpha regions can coexist
with a low plane average. T020's y=1.5 m speed maximum is 115.59 m/s, versus
60.07 m/s for T100. These N5000 fields describe finite endpoints and cannot
locate the earlier epsilon/speed spikes or establish a steady liquid level.


## Interpretation and next supported decision

**Observed:** both coefficient reductions retain unacceptable phase/mixture
closure, changing liquid inventory and four residual equations above the
threshold. The weaker sinks retain more liquid in the collector, and their
realized source histories overlap or exceed the baseline. Epsilon/speed
bursts persist. The response is not monotonic with tau.

**Competing explanations:** stronger local source coupling remains plausible,
but tau alone did not remove the problem. Liquid availability and continuing
flow development change the effective operating state; pressure/phase-fraction
coupling, turbulent transport and recirculation can also contribute. Outlet
reverse-flow face counts and viscosity limiting are numerical context, not
phase-resolved reverse mass flux or proof of a unique mechanism. Mesh and
boundary effects were held fixed, so this comparison cannot separate them.

**G2 decision:** the tested weaker-sink coefficients do not rescue this steady
formulation within the approved horizon. Do not promote a case on carryover,
source-command agreement or solver completion. The next supported scientific
decision is an explicitly designed conservation/coupling diagnostic: identify
where the phase mass equation's flux/source residual and velocity/turbulence
excursions originate, and verify any proposed source linearization or solver
change against equation-level evidence. That is a proposal for a new approved
experiment, not authority to run it. Another tau point or a longer horizon
is not justified automatically by these results. No additional solves,
physics/numerical changes or qualification were performed.

## Evidence and execution provenance

[Machine comparison and full late-window statistics](../../../../PyAnsys/output/phase07b-g2/comparison.json)
retain mean, minimum, maximum, standard deviation and iteration slope, input
hashes, numerical indicators and native figure provenance. Both controllers
exited zero; every-iteration scalar, exact-face flux and seven-equation
residual records are finite and continuous through N5000, with no conflicting
duplicates or fatal solver marker. Finite records do not imply physical validity.

N50, every subsequent 500-iteration checkpoint and the final checkpoint have
paired case/data files on the Fluent PC's local disk. The final pair is the
N5000 checkpoint. Each new child has complete initial/final four-horizontal
and two-axial native field arrays, ten fields per plane. Initial horizontal
fields match the baseline; initial liquid fraction is zero. The original
baseline's final axial arrays are retained with the meeting extraction, and
G2 graphics load its original saved final pair directly.

| Evidence | Baseline | T020 | T100 |
| --- | --- | --- | --- |
| Run manifest | [manifest](../../../../PyAnsys/output/p7b-s040-20260921T013001Z/manifest.json) | [manifest](../../../../PyAnsys/output/p7b-s40-t020-resume-20260921T231240Z/manifest.json) | [manifest](../../../../PyAnsys/output/p7b-s40-t100-20260922T022956Z/manifest.json) |
| Full analysis | [summary](../../../../PyAnsys/output/p7b-s040-20260921T013001Z/analysis/summary.json) | [summary](../../../../PyAnsys/output/p7b-s40-t020-resume-20260921T231240Z/analysis/summary.json) | [summary](../../../../PyAnsys/output/p7b-s40-t100-20260922T022956Z/analysis/summary.json) |
| Completion audit | [G1 record](../s040-collector/results.md) | [audit](../../../../PyAnsys/output/p7b-s40-t020-resume-20260921T231240Z/completion-audit.json) | [audit](../../../../PyAnsys/output/p7b-s40-t100-20260922T022956Z/completion-audit.json) |
| Scalar history | [N1–5000](../../../../PyAnsys/output/p7b-s040-20260921T013001Z/history-05000.out) | [N1–5000](../../../../PyAnsys/output/p7b-s40-t020-resume-20260921T231240Z/history-05000.out) | [N1–5000](../../../../PyAnsys/output/p7b-s40-t100-20260922T022956Z/history-05000.out) |
| Exact-face flux | [JSONL](../../../../PyAnsys/output/p7b-s040-20260921T013001Z/collector-flux.jsonl) | [JSONL](../../../../PyAnsys/output/p7b-s40-t020-resume-20260921T231240Z/collector-flux.jsonl) | [JSONL](../../../../PyAnsys/output/p7b-s40-t100-20260922T022956Z/collector-flux.jsonl) |
| Native transcript | [solve](../../../../PyAnsys/output/p7b-s040-20260921T013001Z/solve.trn) | [solve](../../../../PyAnsys/output/p7b-s40-t020-resume-20260921T231240Z/solve.trn) | [solve](../../../../PyAnsys/output/p7b-s40-t100-20260922T022956Z/solve.trn) |

The [offline implementation proof](../../../../PyAnsys/output/phase07b-e2-preparation/offline-verification.json)
and each child's initial-parity/N50 receipts establish the controlled delta.
T020's original preparation stopped at N0 because a native transcript was
already open; its recovery verified the unchanged prepared state and started
recording without reinitialization. T100's first preparation stopped before
parent loading or solving because `stop_transcript` was already inactive;
the [recovery receipt](../../../../PyAnsys/output/p7b-s40-t100-20260922T022827Z/recovery-disposition.json)
records the activity-check repair. Neither implementation failure is a
numerical disposition or a scientific treatment change.

All source pairs remain preserved. Native graphics are postprocessing only:
no iteration, initialization, patch or scientific-setting change is part of
the export. Fluent is left at the saved T100 N5000 endpoint. The previous G1
check-in remains paused; E2 supervision is also paused, confirmed by the [automation receipt](../../../../PyAnsys/output/phase07b-g2/automation-pause-receipt.json). No new simulation is queued or authorized.
