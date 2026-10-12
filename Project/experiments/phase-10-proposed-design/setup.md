# Phase 10 — Proposed design comparison setup

| Comparison input | Vertical slit | Angled slit |
| --- | --- | --- |
| Mesh cells | 154,063 | 213,232 |
| Retained endpoint | N84000 / 50.9 ms | N33492 / 50.000 ms |
| Continuation parent | N5080 / 3.5 ms | Paused N30862 / 23.705 ms |
| Bulk model | Mixture / RNG / Coupled | Mixture / RNG / Coupled |
| Liquid / vapour feed | 116.92 / 80.69 kg/s | 116.92 / 80.69 kg/s |
| EWF configuration | Enhanced Stage 4, Phase 9 continuation | Basic Stage 3 |
| Roughness height / coefficient | 0.045 mm / 0.5 | 0.5 mm / 0.5 |
| Film pressure / surface tension / stripping / edge separation | On | Off |
| Drain model | Lower-wall numerical film removal | Direct native EWF outflow |
| Retained timestep | 2.5 µs | 10 µs main block; final 5 µs update |
| Bulk at retained film endpoint | Frozen | Frozen |
| Detailed authority | [Vertical setup](vertical-slit154k/setup.md) | [Angle setup](angled-slit213k/setup.md) |

| Assessment | Required comparison | Current limit |
| --- | --- | --- |
| Inlet interaction | Top-down liquid fraction, turbulence and velocity at the same section and scale | Vertical exports exist; matching angle exports absent |
| Slit transport | Vertical section and in-plane velocity vectors through each feature | Vertical exports exist; matching angle section absent |
| Liquid destination | Steam-outlet liquid, wall-film inventory, film drain and numerical absorber separately | Angle endpoint bulk metrics not yet extracted |
| Pressure loss | Same inlet/outlet pressure definition | Vertical area-mean static pressure difference available |
| Feature effect | Reference geometry with matched controls and preparation | Existing retained designs use different controls and mesh sizes |
| Historical baseline | [Reference 60k Stage 3 startup](../phase-07-2a-wall-liquid-routing/stage-03-shortened-reconstruction/early-ewf-startup/results.md) and [vertical startup](vertical-slit154k/startup-stage3/results.md) | Early startup comparison; does not establish developed-film performance |
