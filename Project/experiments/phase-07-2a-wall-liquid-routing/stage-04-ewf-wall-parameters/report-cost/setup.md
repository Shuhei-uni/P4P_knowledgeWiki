# Stage 4 — Native report-cost comparison

| Contract | Selected test |
| --- | --- |
| Authority | Human, 8 October 2026: keep running; full ownership of Server 1 |
| Question | Does reducing active diagnostic reports reduce film development cost without changing the calculated film? |
| Classification | NEW diagnostic-cost contrast; analytical velocity work showed no useful acceleration |
| Parent | Exact full-momentum N41503 paired checkpoint from the [short comparison](../analytical-film/results.md); film clock 0.3883843386354628 s; hashes in the machine manifest |
| Preserved endpoint | Completed N43483 / +20 ms control remains saved and verified before replacement |
| Controlled delta | All 60 report files active versus 17 essential report files active; active files retain frequency 1 |
| Fixed physics | EWF, accretion, collection, stripping, separation, splash, gravity, shear, pressure gradient, spreading, surface tension, coupled film solution; Flow Momentum Coupling OFF |
| Fixed numerics | 10 µs, frozen bulk, source/profile cadence, drain τ=1.5 ms and 1% removal bound; no initialization |
| Common restart state | Prepared-pair save/reopen changes native elapsed `injection_interval` from 40 to 10 µs in both arms. Require equal prepared span; nominal DPM tracking remains 20 film steps. Historical control is supporting evidence; new paired arms own the comparison. |
| Horizon | 1,000 updates per arm from the same saved parent; +10 ms to N42503 |
| Native execution | One fixed solve per arm; native journal owns solve, all-sample guards, paired final save and transcript |
| Safety | Courant <1; maximum thickness <0.3 m; finite fields; no active-run Scheme queries; passive transcript monitoring |
| Essential reports | Total mass/input/removal ledger; upper/lower inventory; lower input/removal ledger; direct drain; maximum velocity; total Courant/thickness |
| Bulk evidence | Read full bulk reports and equation state before/after each arm; no invented per-update histories in the reduced-report arm |
| Speed decision | ≥20% lower whole-command time supports adoption after field/history agreement; smaller changes need repeat or remain inconclusive |
| Equivalence decision | Compare common per-update reports and saved face fields at the same accepted time; target relative differences ≤1e-5 with stated absolute tolerances for near-zero quantities |
| Claim limit | A reporting speed gain does not establish physical accuracy, conservation qualification or steady film |

| Artifact | Quantity / source / decision |
| --- | --- |
| R1 — cost and agreement | Native whole-command and parallel timers; all common film histories and endpoint face fields; determine speed and numerical equivalence |
| R2 — film ledger | Integrate per-update phase/DPM sources and direct drain; stock differences; retain the known DPM event-accounting limitation |

| Later timestep constraint | Treatment |
| --- | --- |
| Drain bound | `min(1/τ, MaxFraction/RefreshSpan)`; fixed 1% cap would weaken the physical drain above 15 µs if RefreshSpan follows the larger step |
| Faster-step requirement | Preserve 666.667 /s physical strength; treat any bound adjustment as a numerical control and verify removal before claiming a speed gain |
