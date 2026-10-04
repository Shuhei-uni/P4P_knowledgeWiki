# Family R0 smooth control — Coupled / Global Time Step continuation

## Purpose

| Item | Purpose |
| --- | --- |
| This | is a solver-control continuation of the supplied smooth-wall, no-EWF full-loading R0 reference on Server 1 |
| It | is recorded under Family R as the control endpoint; it is not a roughness perturbation and must not be used as evidence for a roughness response |
| declared control for subsequent comparisons | is the terminal 1000-iteration window recorded in [control-window.md](control-window.md) |
| earlier 1000 iterations | are retained as warm-up/provenance history and are not pooled into control-window statistics |
| full-loading parent itself | was reached through the documented low-inlet and 2,000-iteration ramp lineage in [provenance.md](provenance.md) |

<details>
<summary>Supporting detail — Purpose</summary>

| Item | Purpose |
| --- | --- |
| question | was whether the same full-loading field could persist for a longer native steady continuation under the two explicitly authorized numerical changes: |
| pressure–velocity coupling | current verified setting -> `Coupled`; |
| pseudo-time method | current verified setting -> `Global Time Step` |
| — | Every physical model, mesh, material, boundary, inlet, absorber law, discretization, relaxation/control setting, and steady formulation was held fixed and read back after preparation and at the terminal checkpoint |

</details>

## Parent and execution envelope

| Item | Parent and execution envelope |
| --- | --- |
| Server | 1 (`10.104.145.170:62844`), Fluent 2025 R2 |
| Parent case | `C:\Users\syok443\OneDrive - The University of Auckland\P4P-Fluent-Artifacts\Phase71A\FamilyR\finals\P71A-R0-SMOOTH-CONTROL\20260922T025211Z\P71A-R0-SMOOTH-CONTROL-full-loading-final.cas.h5` |
| Parent data | `C:\Users\syok443\OneDrive - The University of Auckland\P4P-Fluent-Artifacts\Phase71A\FamilyR\finals\P71A-R0-SMOOTH-CONTROL\20260922T025211Z\P71A-R0-SMOOTH-CONTROL-full-loading-final.dat.h5` |
| Parent case SHA256 | `331bc57550fa0eff67bdc89a0925aa52c8c6f79a4632188e234abdd8ece28c3c` |
| Parent data SHA256 | `1a8c31aac6a3a347629a94cc9814edb76b84b49ca1fdfcb1566004bef4517083` |

<details>
<summary>Supporting detail — Parent and execution envelope</summary>

| Item | Parent and execution envelope |
| --- | --- |
| Mesh readback | 60,964 cells; `separator-purnanto` plus the 715-cell `p71a-v2-virtual-outlet` zone |
| Native transcript start used for the continuation | 3580 |
| Continuation | 1000 requested additional steady iterations, report files at native every-iteration cadence, solver calls in batches of 100 after the requested pause/resume |
| Checkpoints | +250, +500, +750, +1000 relative to the recorded native start |

</details>

## Authority and recovery notes

| Item | Authority and recovery notes |
| --- | --- |
| run | was paused at the user's request after native transcript coordinate 3744, saved as a paired case/data checkpoint, and resumed from that pair |
| RP `current-iteration` variable | was stale in this Fluent session; native transcript rows, report-file coordinates, and the continuation offset ledger are therefore authoritative |
| first wrapper | was marked blocked only during post-run final OneDrive hash parsing; the final durable pair was verified by a fresh read-only attachment and has its own completion receipt |
| — | Authoritative evidence: |
|  | [completion receipt](/Users/shuheiyokkaichi/Developer/P4P_knowledgeWiki/PyAnsys/output/phase71a_r0_control_run3/authoritative-completion-receipt.json) |

<details>
<summary>Supporting detail — Authority and recovery notes</summary>

| Item | Authority and recovery notes |
| --- | --- |
| — | [analysis summary](/Users/shuheiyokkaichi/Developer/P4P_knowledgeWiki/PyAnsys/output/phase71a_r0_control_run3/analysis/summary.json) |
|  | [batched transcript](/Users/shuheiyokkaichi/Developer/P4P_knowledgeWiki/PyAnsys/output/phase71a_r0_control_run3/transcript-batched-resume.txt) |
|  | [stitched report histories](/Users/shuheiyokkaichi/Developer/P4P_knowledgeWiki/PyAnsys/output/phase71a_r0_control_run3/report-histories-batched.json) |
|  | [declared terminal control window](control-window.md) |

</details>
