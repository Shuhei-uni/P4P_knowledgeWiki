# Phase 8 F0 — mixed inlet, SIMPLE and one-way diagnostic DPM

| Phase 8 F0 — mixed inlet, SIMPLE and one-way diagnostic DPM |
| --- |
| The human separated the existing SIMPLE series from F1 on 3 October 2026 |
| F0 owns that series; F1 owns the mixed-inlet Coupled series |
| This reclassification adds no compute |
| Original run IDs, pairs, hashes and figures containing F1 stay unchanged as provenance |

## Controlled comparison

| Item | Controlled comparison |
| --- | --- |
| — | Use the same 60,964-cell partition, mixed feed on both original inlet faces, full Eulerian liquid feed, closed bottom, smooth walls, no absorber and no EWF as F1 |
|  | Both series independently Hybrid-initialize every speed (20.11, 23.46, 26.81, 29.48, 32.14 m/s), run 10,000 carrier iterations and use N9,500–10,000 |
| F0 | uses SIMPLE, segregated pseudo-time off, second-order momentum/k/epsilon, PRESTO pressure, QUICK phase transport and node-based gradients |
| F1 | uses Coupled/Global Time Step and first-order k |
| This | is a numerical-package contrast |
| One-way diagnostic DPM | retains full Eulerian feed, uses the same seven-bin fine-mist PSD and steaminlet release face, speed-scaled release velocity, 5% diagnostic weight and 50,000-step cap |
| — | Diagnostic weight adds no physical feed |
|  | Incomplete weight must accompany escape/trap fractions |

## Evidence and limits

| Item | Evidence and limits |
| --- | --- |
| — | [Carrier summary](../../../../../PyAnsys/output/phase8-analysis/f1-simple-vs-coupled-n10000/summary.json) and [DPM summary](../../../../../PyAnsys/output/phase8-analysis/f1-simple-vs-coupled-n10000/f1-simple-diagnostic-dpm-fates.json) link the five immutable source manifests. [Results](results.md) owns interpretation |
| bounded horizon | is complete, but all five carriers have poor numerical health; physical separation and Purnanto mesh/topology parity are not established |
| Earlier SIMPLE pilots and the merged single-face recreation | are supporting F0 history with separate horizons/topology and are excluded from this five-speed comparison |
