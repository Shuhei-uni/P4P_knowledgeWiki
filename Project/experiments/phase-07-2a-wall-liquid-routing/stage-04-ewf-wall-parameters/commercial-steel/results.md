# Stage 4 — Commercial steel roughness result at N29815

| Question / status | Answer |
| --- | --- |
| Human-selected diagnostics | Bulk liquid inventory; phase-2 steamoutlet flux; EWF liquid inventory; accretion/drainage; continuity |
| Completed run | N25815 → N29815; 4000 additional updates; final pair present and SHA-256 verified |
| Roughness | 0.5 → 0.045 mm on four existing rough walls; Cs 0.5; bottom smooth |
| Numerical changes | Original bulk equations restored; adaptive film stepping replaced by fixed 1 µs |
| Actual film time | 265.184339 → 269.184339 ms; only 4 ms added |
| Observation | Lower endpoint outlet-flux magnitude; bulk and film inventories above parent values |
| Causality limit | Combined response to changed roughness, restored bulk solves and changed film step; no isolated roughness comparison |
| Steady film | No; accretion remains above drainage |

![Five requested diagnostics](figures/requested-diagnostics-N29815.png)

*Raw native histories; dashed lines show saved parent values; shading marks N29316–N29815. The N25815 continuity marker is inherited from the last bulk solve at N5080. Bulk equations were frozen between those states.*

| Quantity | Saved parent N25815 | Final N29815 | Final 500 mean |
| --- | ---: | ---: | ---: |
| Bulk liquid mass, kg | 61.054883 | 61.786167 | 61.706599 |
| Phase-2 steamoutlet signed flux, kg/s | -3.429962 | -2.753579 | -2.747977 |
| EWF liquid mass, kg | 6.688276 | 6.783154 | 6.777141 |
| Film accretion, kg/s | 81.121377 | 92.348432 | 92.329134 |
| Film drainage, kg/s | 68.218606 | 68.227655 | 68.247253 |
| Scaled continuity | 0.001863 — inherited N5080 | 0.0017337 | 0.00184594 |

| Observation | Interpretation / limit |
| --- | --- |
| Bulk mass first falls to 52.442 kg at N26104, then rises to 61.786 kg | Endpoint-only comparison misses the early redistribution; final bulk inventory is 1.20% above parent |
| Outward liquid flux magnitude falls 19.72% at the endpoint | Lower modeled outlet flux; inventories must be considered before claiming improved separation |
| EWF mass rises 1.42% | Retained film inventory increases |
| Final-500 accretion/drainage: 92.33/68.25 kg/s | Rate gap remains about 24.08 kg/s; not steady drainage |
| Final-500 film storage: 24.09 kg/s | Film still fills despite small absolute mass change over 4 ms |
| Continuity peak 0.016721; final-500 range 0.0016105–0.0022062 | Initial bulk response settles near the inherited residual scale; this alone does not establish convergence |

| Numerical evidence | Result |
| --- | --- |
| Report coverage | All 31 native histories extracted; 4001 parent/child points for requested report quantities |
| Carrier coverage | 4000 new residual rows plus inherited parent row; duplicate segment-start rows checked |
| Film clock | All 4000 printed steps equal 1 µs; printed clocks agree with full-precision parent clock and endpoint within print precision |
| Peak film Courant | 0.014377 |
| Whole-window mean accretion / drainage / storage | 92.020403 / 68.309881 / 23.719662 kg/s |
| Film ledger error | 0.009931% of integrated accretion; ΔM + ΔD − Σ(A Δt) |
| Film inner residuals | Inherited alternative implicit scheme; unavailable; no tolerance-pass claim |
| Transcript scope | Complete retained client stream for first 20 updates; native server transcripts for remaining 980 and 3000 |
| Final pair verification | Native target/counter, local files and hashes verified; no extra solve; no additional final reopen in this analysis |
| Whole-system balance | Film-only ledger does not establish bulk/film/source-inclusive conservation |

| Quantity definition | Native source / calculation |
| --- | --- |
| Bulk liquid inventory | Phase-2 volume-mass report over separator-purnanto and p71a-v2-virtual-outlet |
| Steamoutlet liquid flux | Native phase-2 boundary flux; negative is outward; user-source term excluded |
| EWF inventory | Native film-mass sum on inherited surface wall |
| Accretion | Native film-phase2-mass sum on inherited surface wall; kg/s |
| Drainage | Difference of cumulative film-outflow-mass sum on surface wall divided by accepted film step; kg/s |
| Continuity | First column of each native scaled carrier residual row |
| Comparison window | Final 500 iterations N29316–N29815; raw traces retained |

| Deliverable / evidence | Link |
| --- | --- |
| Overview PDF | [Five diagnostic panels](figures/requested-diagnostics-N29815.pdf) |
| Individual figures | [Bulk inventory](figures/bulk-liquid-inventory.png); [outlet flux](figures/phase2-steamoutlet-flux.png); [EWF inventory](figures/ewf-liquid-inventory.png); [film rates](figures/film-mass-rates.png); [continuity](figures/continuity.png) |
| Numeric table | [Diagnostic CSV](../../../../../PyAnsys/output/phase72a-commercial-steel/20261006/requested-diagnostics-N25815-N29815.csv) |
| Summary / provenance | [Analysis summary](../../../../../PyAnsys/output/phase72a-commercial-steel/20261006/analysis-summary.json); [figure manifest](../../../../../PyAnsys/output/phase72a-commercial-steel/20261006/figure-manifest.json) |
| Immutable native extracts | [Extraction receipt](../../../../../PyAnsys/output/phase72a-commercial-steel/20261006/raw/N29815-20261007/extraction.json) |
| Reproduction | [Analysis script](../../../../../PyAnsys/scripts/analysis/analyze_phase72a_commercial_steel.py) |
| Setup | [Controlled settings](setup.md) |

| Next decision | Requirement |
| --- | --- |
| Continue film development | More native film time is required to test inventory persistence and drainage balance |
| Isolate roughness effect | Matched 0.5 mm and 0.045 mm continuations from the same parent, same bulk advancement and same film controls |
| Further simulation | No new solve submitted during this analysis |
