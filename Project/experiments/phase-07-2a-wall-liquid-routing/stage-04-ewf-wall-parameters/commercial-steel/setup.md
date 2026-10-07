# Commercial steel roughness continuation

| Item | Selected setting |
| --- | --- |
| Human direction | 6 October 2026: change roughness to 0.045 mm; continue film-development parent |
| Parent | Verified transfer-final-N25815; no initialization |
| Parent film time | 265.184339 ms |
| Parent film mass | 6.688275530 kg |
| Parent case SHA-256 | ed46a6f0ce4ee6076e1f5bd0673f081418b43cbfed7529cfc92ef539c71cf26a |
| Parent data SHA-256 | 48efe32e059f33f2716469f9a0e92f4f4b4c2781d8905136e28a1fefd79ee6d1 |
| Roughness height | 0.0005 → 0.000045 m |
| Wall scope | separator-purnanto:1; separator-purnanto:1:001; wall; wall:004 |
| Roughness constant | Retain 0.5 |
| Bottom | Retain smooth wall |
| Bulk equations | Restore original drift, flow, ke and mp advancement so wall changes can affect the flow |
| Film controls | Fixed 1 µs; 30 allowed subiterations; retain inherited alternative implicit scheme |
| Other physics | Retain mesh, materials, inlets, film walls, sources, contact absorber and DPM |
| Completed first horizon | 1000 additional iterations; N25815 → N26815; native paired endpoint verified |
| Batches | Completed 20-update probe; remaining 980 updates submitted as one native server-owned journal |
| Placement | Server 1; preserve separate idle endpoint before replacement |
| Checkpoints | Local FluentRuns disk; paired saves and reopen |
| Required evidence | All inherited native reports; transcripts; accepted film clocks; residuals; roughness readback; paired checkpoint hashes |
| Primary figure | Film mass and liquid carryover against iteration |
| Review bounds | CFL ≤1; film ledger error ≤1%; film mass ≤12.3 kg |
| Claim limit | Initial response to changed roughness with restored bulk flow; no isolated roughness-benefit or steady-film claim |
| Implementation | [Runner](../../../../../PyAnsys/scripts/setup/run_phase72a_commercial_steel_continuation.py) |
| Machine evidence | [Manifest](../../../../../PyAnsys/output/phase72a-commercial-steel/20261006/run-manifest.json) |

| Native handoff | Setting |
| --- | --- |
| Human direction | Resume with simple TUI; allow laptop closure |
| Native command | /solve/iterate 3000 |
| Endpoint write | /file/write-case-data to local native-final-N29815.cas.h5 |
| Execution | Asynchronous native journal inside Server 1 Fluent; no laptop controller |
| Completion | N29815 native endpoint, paired files, hashes and extracted histories verified |

| Extension — 7 October 2026 | Setting |
| --- | --- |
| Human direction | Run 3000 more iterations |
| Start / target | N26815 → N29815 |
| Settings | Retain verified 0.045 mm roughness, Cs 0.5, full bulk advancement and 1 µs fixed film step |
| Parent preservation | Native N26815 pair present; case/data hashes recorded before extension |
| Execution | One native journal; final paired write on server-local FluentRuns disk |
