# Phase 10 — Proposed design setup

| Input / setting | Basis |
| --- | --- |
| Mesh | `Separator-angle-slit-213k.msh.h5`; 213,232 cells |
| Mesh SHA-256 | `9b68ea200ed4e8bf53785834e380b6b26490b36e4d7271b1b375478f7f410df9` |
| Parent | Stage 3 basic-EWF prepared-A-N1580; 25% feed; dry film |
| Case SHA-256 | `5907e357654ebe5437c64f4e6abea19cbbc66b1edd2312f6b2eb63fe408c2b72` |
| Data SHA-256 | `72a7134f6358ea68615907f336e71d6e518c713418674477703fc638e41816af` |
| Controlled change | Supplied angled-slit geometry and discretization |
| Transfer | Native Replace Mesh; retain mapped bulk fields and dry-film clock |
| Scale | Verify native metre extents before scaling; raw file coordinates alone do not establish units |
| Wall mapping | Prove slit and lower-collector roles from geometry and adjacency; record full transferred boundary conditions |
| Basic EWF | Read back inherited Stage 3 film equations, forces, sources, roughness, walls, feedback and DPM |
| Preparation method | Phase 9 hold/ramp procedure; do not substitute later Stage 4 EWF physics |
| Low feed | Liquid 29.23 kg/s; vapor 20.1725 kg/s |
| Full feed | Liquid 116.92 kg/s; vapor 80.69 kg/s |
| Hold allowance | 1,000 low-feed updates; 2,000 full-feed updates minimum |
| Ramp | 25% → 100% in 2,000 updates; inlet changes every 10 updates |
| Preparation screen | Two final-1,000 windows: pressure-drop range ≤5% of mean; bulk-mass range ≤10% of mean; outlet-liquid range ≤5% of full liquid inlet |
| Film horizon | 0.100 s total native film age; include startup and probes |
| Freeze prerequisite | Prove direct film removal, accepted film-time advancement and preserved bulk fields |
| Film numerics | Initial matched-time qualification selected 0.5 µs. Human revision: preserve the completed batch, run 3,000 updates at 1 µs, then 2.5 µs to 100 ms; adjust only the last step if needed to hit the exact endpoint |
| Revised-step evidence | Human-selected faster steps; record Courant without a stop condition, as requested. Retain thickness, film ledger and frozen-bulk checks. The revised steps do not have matched-time qualification |
| Fixed solve | At least 1,000 updates between required decisions; short smoke, ramp and numerical contrasts only |
| Checkpoints | Local Fluent disk; paired saves at decision boundaries; final paired reopen |

| Evidence ID | Quantity / artifact | Purpose |
| --- | --- | --- |
| P10-1 | Native mesh check, zone map, mapped fields and paired reopen | Prove the proposed-design child |
| P10-2 | Matplotlib film mass and accretion/removal/storage versus actual film time | Assess development and film accounting |
| P10-3 | Final wall-film thickness with declared scope and scale | Locate retained film at 100 ms |
| Supporting | Bulk pressure drop, inventory, signed outlet flux; residuals, accepted steps and Courant | Retain startup and numerical limits |

| Accounting / interpretation | Requirement |
| --- | --- |
| Film ledger | Δfilm mass + integrated removal − integrated input; actual accepted film-time increments |
| Extra terms | Include every active deposition, stripping, separation, evaporation and user source |
| Frozen-bulk limit | Held inventory does not prove bulk stationarity or whole-separator conservation |
| Geometry limit | New geometry is not a pure mesh-resolution contrast |
| Endpoint limit | 100 ms is finite development, not evidence of steady film |
