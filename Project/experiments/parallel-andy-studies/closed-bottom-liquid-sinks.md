# Historical closed-bottom liquid-sink diagnostics

## Question and controlled scope

Following the unresolved carrier mesh study, Andy `07b`–`07f` tested whether
a liquid-only volumetric removal source near the closed bottom could make
the steady carrier solution close and stabilize without adding outlet geometry.
The inherited reference was the clean 900k-labelled mesh (5,335,623 cells),
steady Mixture/RNG k-epsilon, liquid/vapour feeds 116.92/80.69 kg/s, a bottom
wall and steam pressure outlet. DPM and EWF were off. The source was a
numerical constant-level abstraction, **not** measured outlet hydraulics or
a physical-time controller.

Each source below preserves the case identity, intended controls, execution
history and paths to machine evidence. These are historical observations;
the migration did not rerun the calculations.

| Historical branch | Recorded change and horizon | Recorded result |
|---|---|---|
| [07b](https://github.com/Shuhei-uni/P4P_knowledgeWiki/blob/archive/andy-local-20260908/Setup%20report/07b-split-inlet-constant-water-level-liquid-sink.md) | One-cell bottom-local sink, tau 0.1 s; 6,000 full-strength iterations | Implementation/hook smoke accepted; zero accepted scientific stability window, corrected liquid imbalance 91.1909% |
| [07c](https://github.com/Shuhei-uni/P4P_knowledgeWiki/blob/archive/andy-local-20260908/Setup%20report/07c-split-inlet-thickened-constant-water-level-liquid-sink.md) | Sink band thickened to 0.1401652536 m, tau unchanged; 2,000 full-strength iterations | Zero acceptance windows; corrected liquid imbalance 80.7661%, source-inclusive mixture imbalance 47.4802% |
| [07d](https://github.com/Shuhei-uni/P4P_knowledgeWiki/blob/archive/andy-local-20260908/Setup%20report/07d-split-inlet-capacity-matched-thick-sink.md) | Same band, tau 0.02 s; 1,000 ramp + 2,000 full-strength iterations | Sink 46.987392 kg/s, corrected liquid imbalance 59.812198%; zero acceptance windows |
| [07e](https://github.com/Shuhei-uni/P4P_knowledgeWiki/blob/archive/andy-local-20260908/Setup%20report/07e-split-inlet-adaptive-mass-balance-sink-control.md) | Band-inventory feedback on tau, bounded below by 0.002 s; 1,000 ramp + 2,000 full-strength iterations | Sink 50.954294 kg/s (43.6% of feed), corrected liquid imbalance 56.419329%; zero acceptance windows |
| [07f](https://github.com/Shuhei-uni/P4P_knowledgeWiki/blob/archive/andy-local-20260908/Setup%20report/07f-split-inlet-sink-thickness-rate-matrix.md) | Thickness/rate matrix; first case doubled band to 0.2803305 m at tau 0.02 s | First case completed 3,000 total / 2,000 full-strength iterations: sink 53.133696 kg/s, corrected liquid imbalance 54.5553%, zero acceptance windows; clean cases 2 and 3 remained pending after report/readback failure |

The final `07f` disposition comes from the corrected
[historical status record](https://github.com/Shuhei-uni/P4P_knowledgeWiki/blob/archive/andy-local-20260908/ResearchProject_wiki/wiki/progress/current-status.md),
which supersedes the setup page's older `Running diagnostic matrix` heading.
Partial/interrupted fields were preserved as unverified evidence and are not
completion evidence for the pending cases.

## Source-accounting correction

The `07c` audit found that the phase-2 Fluent report's `Net` already included
the liquid source. Adding the sink again double-counted it. The raw controller
fields `liquid_source_augmented_*` are therefore invalid for these results:
`07b` 84.2956% was corrected to 91.1909%, and `07c` 61.5322% to 80.7661%.
The mixture boundary report still required source augmentation, so its stated
source-inclusive result was retained. The original raw evidence was not
rewritten; `analysis_correction.json` was the source's correction record.

## Retained interpretation

Compiled-source persistence and completed iteration budgets did not establish
constant-level behaviour. In `07e`, available liquid in the band limited the
removal rate even at the minimum tau. Pressure, inventory and other carrier
monitors continued to drift. These results support further examination of
the liquid-discharge representation; they do not establish a physical valve
law, free surface, mesh independence or separator efficiency.

The subsequent [resolved-outlet lane](resolved-brine-outlet.md) deliberately
removed these source terms and introduced different geometry. It must not
inherit a numerical sink as if it represented the resolved outlet.
