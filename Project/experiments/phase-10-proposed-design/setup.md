# Phase 10 — Proposed design comparison setup

| Comparison input | Vertical slit | Angled slit |
| --- | --- | --- |
| Mesh cells | 154,063 | 213,232 |
| Selected endpoint | N44661 / 150.000 ms | N43492 / 150.000 ms |
| Preserved common-age pair | N34661 / 50.000 ms | N33492 / 50.000 ms |
| 150 ms continuation parent | N34661 / 50.000 ms | N33492 / 50.000 ms |
| Earlier basic-EWF preparation parent | N31000 / 13.392 ms | Paused N30862 / 23.705 ms |
| Bulk model | Mixture / RNG / Coupled | Mixture / RNG / Coupled |
| Liquid / vapour feed | 116.92 / 80.69 kg/s | 116.92 / 80.69 kg/s |
| EWF configuration | Basic Stage 3, matched from selected continuation parent | Basic Stage 3 |
| Roughness height / coefficient | 0.5 mm / 0.5 | 0.5 mm / 0.5 |
| Film pressure / surface tension / stripping / edge separation | Off | Off |
| Drain model | Direct native EWF outflow; lower numerical film removal disabled | Direct native EWF outflow |
| 50–150 ms timestep | Fixed 10 µs | Fixed 10 µs |
| Bulk at retained film endpoint | Frozen | Frozen |
| Detailed authority | [Basic-EWF follow-up](vertical-slit154k/basic-ewf-10us/setup.md) | [Angle setup](angled-slit213k/setup.md) |

| Assessment | Required comparison | Current limit |
| --- | --- | --- |
| Inlet interaction | Top-down liquid fraction, turbulence and velocity at the same section and scale | Earlier enhanced-EWF vertical exports exist; matching basic-EWF views absent |
| Slit transport | Vertical section and in-plane velocity vectors through each feature | Vertical exports exist; matching angle section absent |
| Liquid destination | Steam-outlet liquid, wall-film inventory, film drain and numerical absorber separately | Angle endpoint bulk metrics not yet extracted |
| Pressure loss | Same inlet/outlet pressure definition | Earlier enhanced-EWF vertical area-mean static pressure difference available |
| Feature effect | Reference geometry with matched controls and preparation | Current main EWF controls matched; mesh and initial fields/history differ |
| Historical baseline | [Reference 60k Stage 3 startup](../phase-07-2a-wall-liquid-routing/stage-03-shortened-reconstruction/early-ewf-startup/results.md) and [vertical startup](vertical-slit154k/startup-stage3/results.md) | Early startup comparison; does not establish developed-film performance |
