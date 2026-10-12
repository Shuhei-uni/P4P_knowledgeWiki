# Default RSM experiment — 60k mesh

| Item | Selected scope |
| --- | --- |
| Authority | Shuhei, 9 October 2026: full Server 3 ownership; replace the loaded pair; use guide-backed TUI settings and one 2000-iteration TUI solve |
| Question | How does default Linear Pressure-Strain RSM behave when continued from the developed RNG solution? |
| Mesh | Existing 60,964-cell Phase 9 simplified mesh |
| Parent | Selected Phase 9 N8080 case/data; [selection receipt](../../../../PyAnsys/output/phase9-mesh-convergence/20261007/60k-final-selection-N8080.json) |
| Controlled change | RNG k-epsilon to Linear Pressure-Strain RSM; wall reflection enabled; default RSM constants |
| Retained settings | Existing mesh, feed, multiphase model, wall treatment, EWF and compatible solver settings |
| Initialization | Continue existing data; no Hybrid or Standard Initialization |
| Horizon | One `/solve/iterate 2000`; target native N10080 |
| Bulk equations | Active throughout; no EWF-only stages |
| Separation from Phase 9 | Turbulence-model experiment; does not alter the selected mesh-comparison baselines |
| Claim limit | Experimental continuation; no mesh independence or physical validation claim |
| Machine owner | [Run manifest](../../../../PyAnsys/output/rsm-server3-60k/20261009/run-manifest.json) |

