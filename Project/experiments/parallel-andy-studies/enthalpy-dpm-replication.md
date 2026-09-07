# Historical enthalpy and DPM replication

## Scope and provenance

This is Andy's completed six-condition baseline/Bangma-target sweep and its
six-condition spiral-inlet sibling, recorded in July 2026. Their historical
IDs are Andy `08b` and `08c`; they are distinct from the existing Phase-2
parity and inlet-loading experiments. The common historical parent is Andy
`08` one-inlet reconstruction, not a newly qualified carrier baseline.

The source setup records are
[baseline sweep](https://github.com/Shuhei-uni/P4P_knowledgeWiki/blob/archive/andy-local-20260908/Setup%20report/08b-purnanto-baseline-enthalpy-dpm-sweep.md)
and
[spiral sweep](https://github.com/Shuhei-uni/P4P_knowledgeWiki/blob/archive/andy-local-20260908/Setup%20report/08c-purnanto-spiral-inlet-enthalpy-dpm-sweep.md).
The preserved project interpretations provide the detailed operating matrix,
Harwell reconstruction, evidence paths and digitized comparison:
[replication report](https://github.com/Shuhei-uni/P4P_knowledgeWiki/blob/archive/andy-local-20260908/ResearchProject_wiki/wiki/technical/purnanto-enthalpy-dpm-replication.md)
and
[spiral interpretation](https://github.com/Shuhei-uni/P4P_knowledgeWiki/blob/archive/andy-local-20260908/ResearchProject_wiki/wiki/technical/purnanto-spiral-inlet-enthalpy-dpm-replication.md).

## Recorded experiment

Both families used Fluent 2024 R2, a mixed mass-flow inlet, six phase-flow
conditions, nine Harwell-derived injection bins per condition and a nominal
1,500-iteration carrier budget. The five enthalpies were 1440, 1520, 1600,
1680 and 1760 kJ/kg; the sixth condition was 1600 kJ/kg at 25% lower total
flow. The baseline target used inlet area 0.4115 m²; the spiral target used
0.524176 m². Exact CAD/mesh parity with the paper remains **Missing Info**.

The families also differ in velocity, derived droplet diameters, injection
speed and outlet/trapping zone identities. This is not an isolated geometry
sensitivity. One-way DPM was intended, but the baseline manifests did not
preserve all inherited interaction readbacks; do not state that coupling
parity was verified. These facts and limits are recorded in the setup sources.

## Observations and limits

The source reports record all twelve calculations reaching 1,500 iterations,
with nine injection fate rows per case and all cases passing the recorded
0.2% per-injection fate-mass tolerance. Baseline Case 1 has block advancement
in its manifest but lacks a locally mirrored standalone residual CSV; the
other baseline cases and all spiral cases have that CSV evidence. A passing
fate reconciliation accounts for reported particle mass; it does not resolve
the physical fate of incomplete trajectories.

| Condition | Baseline provisional quality (%) | Spiral provisional quality (%) |
|---|---:|---:|
| 1600 kJ/kg, 25% lower flow | 99.7746 | 99.9679 |
| 1440 kJ/kg | 99.6718 | 99.9678 |
| 1520 kJ/kg | 99.7304 | 99.9668 |
| 1600 kJ/kg | 99.7753 | 99.9795 |
| 1680 kJ/kg | 99.8144 | 99.9786 |
| 1760 kJ/kg | 99.8507 | 99.9724 |

These **Inferred** qualities use inlet steam flow divided by inlet steam flow
plus confirmed escaped liquid. They do not classify incomplete trajectories
as trapped or escaped and are not verified outlet-steam-quality measurements.
The baseline incomplete mass is much larger than escaped mass in every case.
Baseline Cases 2–6 have final continuity approximately 0.193–0.343; spiral
cases have approximately 0.145–0.229. Neither family demonstrates convergence.

The source's digitized-paper comparison places all baseline qualities below
the comparison series; the reduced-flow case differs most. Spiral Case 4
differs by approximately +0.1498 percentage points and misses the paper's low
point. Digitization and the missing original numerical series remain explicit
uncertainties. Similar values near 100% do not establish validation.

**Retained conclusion:** a traceable replication dataset and discrepancy map
exist. Exact geometry, inherited DPM settings, incomplete-particle locations,
outlet-flow convention, carrier stationarity and comparison-target parity
remain unresolved. No geometry-only causal claim or separator-performance
validation follows from these results. The source evidence mirrors are named
`PyAnsys/output/enthalpy_sweep_verified_20260721_v2/` and
`PyAnsys/output/spiral_enthalpy_sweep_20260725/`; this migration does not assert
that every remote binary or local output mirror is present in the shared checkout.
