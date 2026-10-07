# Phase 8 Stage 2 — F2 SIMPLE, 997k, 26.81 m/s

| Item | Selected setup |
| --- | --- |
| Authority | [Phase contract](../CONTEXT.md) |
| Classification | Partial repeat: finer mesh and bounded low-feed startup |
| Parent settings | Archived Stage 1 F2 N10000 case, SHA-256 e31dbdf82b75966503b4a8b46dcd0d0cab31cb647092e0de5a88d5f83d37c0c0; settings-only parent; apply recorded SIMPLE parity settings; no parent data loaded |
| Target mesh | Supplied Separator-purnanto-997k.msh.h5; 997,604 cells; input hash from [mesh audit](../../../../PyAnsys/output/phase9-mesh-convergence/20261007/mesh-input-audit.json) |
| Initialization | Fresh Hybrid initialization at 25% feed; no inherited developed bulk state |
| Final liquid feed | 116.93872650 kg/s on liquidinlet; zero on steaminlet |
| Final vapor feed | 80.70292372 kg/s on steaminlet; zero on liquidinlet |
| Speed label | 26.81 m/s combined-area nominal feed label; separate phase-face velocities differ |
| Models / boundaries | Retain Stage 1 F2 Mixture/RNG, properties, gravity and pressure; closed bottom, smooth walls, all sources off |
| Numerics | SIMPLE; segregated pseudo time off; PRESTO; second-order momentum/k/epsilon; QUICK volume fraction; Green-Gauss node gradients |
| DPM / EWF | Carrier only; no injections or continuous-phase feedback; EWF off |
| Geometry proof | Native cell count, mesh check, scale, inlet/outlet areas and zone mapping; retain supplied mesh unchanged |
| Local artifacts | Reports, transcript and checkpoints on Fluent local disk; exact paths in machine receipt |

| Solve interval | Feed multiplier | Iterations |
| --- | ---: | ---: |
| N0–N1000 | 0.25 | 1,000 |
| N1000–N2000 | Gradual linear ramp to 1.0; 10 blocks of 100 iterations | 1,000 |
| N2000–N5000 | 1.0 | 3,000 |
| Total | Includes all verification solves | 5,000 |

| Evidence | Definition / window | Purpose |
| --- | --- | --- |
| S2-A histories | Native phase-1, phase-2 and mixture boundary flux; liquid mass; pressure; residuals across N0–N5000 | Distinguish routing, imbalance and drift |
| S2-B spatial views | N5000 liquid fraction and mixture velocity on z=0 and inlet-height plane; fixed ranges | Show liquid and circulation pattern |
| S2-C summary | N4500–N5000 mean/range; compare inventory slope with N2500–N3000 and N3500–N4000 | Describe late behaviour without assuming convergence |
| Checkpoints | Prepared N0; N1000; N2000; N3000; N4000; N5000 | Recovery and exact iteration proof |
| Completion | Exactly N5000; paired final save/reopen, native mesh/settings verification, report coverage and hashes | Prove execution; numerical limitations remain visible |
| Claim limits | One mesh and one speed; closed bottom; steady iterations are not physical time | No mesh-independence, steady separation or validation claim |
