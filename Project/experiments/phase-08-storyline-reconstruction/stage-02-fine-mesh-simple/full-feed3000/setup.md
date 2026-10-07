# Phase 8 Stage 2 — fresh full-feed F2 SIMPLE trial

| Item | Selected setup |
| --- | --- |
| Authority | Shuhei, current chat: full inlet speed from the start; 3000 iterations |
| Question | How does a fresh full-feed field evolve on the finer split-inlet SIMPLE mesh? |
| Contrast | [Failed low-feed/ramp trial](../results.md); new initialization and feed schedule, same mesh and carrier settings |
| Mesh / server | 997,604 cells; Server 2 only |
| Settings source | Verified N1000 case from failed ramp trial; case only; old data not used |
| Initialization | Fresh Hybrid at full feed; saved/reopened N0 before solving |
| Feed | Liquid 116.93872650 kg/s; vapor 80.70292372 kg/s; pure phase feeds at their own inlet faces |
| Speed label | Nominal combined-area full-feed label 26.81 m/s |
| Numerics | SIMPLE, pseudo time off; PRESTO pressure; second-order momentum/k/epsilon; QUICK liquid fraction; Green-Gauss node gradients |
| Physics | Mixture/RNG; same properties and gravity; closed bottom, smooth walls; sources, DPM feedback and EWF off |
| Solve | N0–N3000 at full feed throughout; three 1000-iteration TUI batches |
| Checkpoints | N0, N1000, N2000, N3000 on Server 2 local disk; failed endpoint preserved separately if possible |
| Reports | Separate native mixture/vapor/liquid boundary flux, inventories, pressure, residual history; report stride 10 |
| Completion | Exactly N3000, final hashes, save/reopen, numerical-control readback and all 17 histories |
| Analysis | N2500–N3000 statistics and inventory trend; native liquid and velocity views; if failed, diagnose preserved endpoint and preceding checkpoint |
| Claim limits | One mesh; no mesh independence, physical validation, stationary liquid inventory or separator-efficiency claim |
| Machine evidence | [Full-feed trial](../../../../../PyAnsys/output/phase8-stage2/20261007/full-feed3000/) |
