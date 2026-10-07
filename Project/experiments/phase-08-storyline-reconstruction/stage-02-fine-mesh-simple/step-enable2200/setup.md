# Stage 2 — early absorber activation and stepped inlet

| Item | Setting |
| --- | --- |
| Authority | Shuhei, 7 October 2026: 200 at25%, enable absorber, 500 at25%, increase by25 percentage points every250, hold full for1,000 |
| Status | N0 saved/reopened; host controller launched on restarted Server2 |
| Question | Does earlier absorber activation followed by a low-feed hold and stepped ramp permit completion? |
| Precedent | Previous 1,000-iteration OFF hold ended with a Cortex error before absorber activation; N300 recovered |
| Mesh / carrier | F2, 997,604 cells; SIMPLE, steady Mixture/RNG; same controls and spatial schemes |
| Initial field | Fresh Hybrid at25% with absorber OFF; failed field excluded |
| Full-feed basis | Nominal 26.81 m/s; liquid116.93872650 kg/s and vapor80.70292372 kg/s |
| Absorber | Corrected libcontactv2, tau10 microseconds; existing lower collector; liquid mass and carried momentum only |
| Fixed treatment | Smooth walls, closed bottom; EWF and DPM feedback off; vapor source off |
| Budget | Exactly2,200 new solve iterations; full-speed hold starts immediately on reaching100% |
| Session | Server2 only; attach; no Fluent restart or termination |
| Claim limit | Startup-path sensitivity; no convergence or universal numerical-impossibility claim from completion alone |

| Native iteration | Duration | Feed / nominal speed | Absorber |
| --- | --- | --- | --- |
| N0–N200 | 200 | 25% /6.7025 m/s | Off |
| N200 | No solve | Save pre-enable pair; activate and read back hooks; save post-enable pair | Switch on |
| N200–N700 | 500 | 25% /6.7025 m/s | On |
| N700–N950 | 250 | 50% /13.405 m/s | On |
| N950–N1200 | 250 | 75% /20.1075 m/s | On |
| N1200–N2200 | 1,000 | 100% /26.81 m/s | On |

| Evidence | Purpose |
| --- | --- |
| Start pair saved/reopened at N0 | Confirm fresh field and exact settings |
| Paired checkpoints at N200, N700, N950, N1200 and N2200 | Preserve each startup boundary |
| Pre/post-enable pairs at N200 | Verify activation without advancing solve iterations |
| Native local autosaves every100 | Retain fields before failure |
| 17 carrier reports every10 from N10 | Inventory, phase/mixture fluxes and pressure |
| Applied signed liquid source every10 from N210 | Source-inclusive balance after activation; volume-sum of cell-integrated native source |
| Lower liquid mass/tau | Independent removal estimate after activation |
| Native residuals and saved field views | Numerical and spatial diagnosis |
| Passive transcript monitor | Observe progress without repeated Cortex file queries during iteration |

[Phase context](../../CONTEXT.md) and [state](../../phase-state.yaml) own the active trial.
