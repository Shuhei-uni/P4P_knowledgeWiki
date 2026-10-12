# Server 1 / 680k — EWF Plan v1 implementation

| Setting group | Controlled change / retained value |
| --- | --- |
| Bulk fields and solver | Retain selected N9080 fields, Mixture / RNG / Coupled, existing collector mass/momentum hooks and full feed: liquid 116.92 kg/s; vapor 80.69 kg/s |
| Film physics | Retain full momentum, gravity, gas shear, wall viscosity, pressure, spreading, advection, phase accretion, DPM collection/splash, stripping and separation |
| Film numerics | Sequential mass/momentum; original first-order implicit; first-order spatial schemes; 100 subiterations; stop 1e-5 |
| Surface tension | Film 0.04041 N/m; retain approved bulk coefficient (native serialization 0.04041000083088875 N/m) |
| Curvature smoothing | ON; level 2; factor 0.5 |
| Lower film storage | Enable EWF on mapped lower collector wall `wall:004`; allocate dry storage and restore saved production data; preserve main-wall film facets |
| Direct drain | Lower-film mass sink with matching XYZ momentum removal; 1.5 ms capture time; 1% source-depletion limiter; existing bulk collector retained |
| Update cadence | One film update per native iteration; profile refresh each update; particle update every 20 µs of film time |
| Film stepping | Fixed 0.1 → 2.5 → 5 µs; human-selected continuation from N18580 at 1 µs for 3,000 updates; adaptive stepping OFF; native EWF `solution-options` callback applies each changed fixed step; drain refresh span follows each step |
| Unchanged thresholds | Small film 1e-8 m; maximum thickness 1 m |
| Checkpoint storage | Server-local paired autosave every 1,000 updates; native transcript and paired endpoint for each stage |
| Gates | Verify accepted film clock and finite reports; prove positive frozen-bulk direct drainage and unchanged bulk fields before faster development. Record net-secondary film-source consistency against 1%; retain gross alternative. Human instruction “just keep running” permits continuation when only this ledger check fails. The 1% direct-source depletion limiter remains active. Current selected Courant ceiling 0.8 (human, 11 October 2026); retain earlier block checks at their recorded limit. All other execution checks remain active. |


| Current continuation | Selected value |
| --- | --- |
| Authority | Human, 11 October 2026: complete EWF Plan v1 and keep running until 200 ms. This supersedes the earlier single-next-block boundary. |
| Starting pair | Verified N27580 / 42.5 ms; paired case/data saved, hashed and reopened. Earlier completed stages remain in the machine manifest and results record. |
| Fixed film step | Retain the proven 1 µs step; adaptive stepping OFF. Drain refresh span 1 µs; DPM every 20 updates to retain 20 µs physical cadence. |
| Final target | N185080 / 200 ms; all bulk equations active for the final 195–200 ms. |

| Remaining section | Bulk equations | Film step | Updates | Endpoint |
| --- | --- | ---: | ---: | --- |
| Verified origin | Frozen | 1 µs | 0 | N27580 / 42.5 ms |
| Main development; 15 native commands | Frozen | 1 µs | 15 × 10,000 | N177580 / 192.5 ms |
| Finish frozen interval | Frozen | 1 µs | 2,500 | N180080 / 195 ms |
| Final bulk reactivation | All active | 1 µs | 5,000 | N185080 / 200 ms |
| **Remaining total** | — | — | **157,500** | **200 ms** |

| Execution control | Requirement |
| --- | --- |
| Automatic delivery | One server-local controller sends all 17 remaining native journals in order. Each journal has one solve command and an endpoint save. The controller checks the saved endpoint before sending the next command. |
| Ownership | Existing solver-writer lock prevents duplicate controllers. Prior single-command queue has completed; it submits no further command. |
| Numerical checks | Peak film Courant ≤0.8; exact native count and film clock; finite reports; no fatal event. Frozen stages retain the bulk-field and direct-drain checks. |
| Ledger policy | Keep discrepancies visible against the 1% reference. A ledger-only failure remains diagnostic under the existing human instruction; other checks remain active. |
| Checkpoints | Server-local paired autosaves every 1,000 updates; paired endpoints and transcripts for each section. |
| Final proof | N185080 / 200 ms, all bulk equations active, paired hashes, save/reopen and field/setup comparison, plus selected shared-pair hashes. |
| Completion | Mark complete only after the final endpoint verifier passes. No Codex wake-up is needed between passing sections. |
| Review | [Exact remaining schedule and execution review](../../../../PyAnsys/output/phase9-ewf-server1-680k/20261009/continue-to-200ms-review.json) |

| Machine implementation | Owner |
| --- | --- |
| Setup | [Apply settings](../../../../PyAnsys/scripts/setup/apply_phase9_server1_680k_ewf.py) |
| Native controller | [Run](../../../../PyAnsys/scripts/setup/run_phase9_server1_680k_ewf.py) |
| Evidence root | `PyAnsys/output/phase9-ewf-server1-680k/20261009/` |
| Server-local root | `C:\Users\syok443\Documents\FluentRuns\Phase9-Server1-680k\20261009` |
