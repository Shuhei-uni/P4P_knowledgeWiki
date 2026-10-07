# Stage 2 — original 08b on the 997k mesh

| Item | Transfer contract |
| --- | --- |
| Authority | Shuhei; load original 08b and replace its mesh with the same supplied 997k mesh |
| Session | Server 2 only; attach; no restart, exit, or solve |
| Source folder | `P4P-Fluent-Artifacts/08b` under university OneDrive |
| Source case | `TwoPhaseInletV2(Purnanto).cas.h5` |
| Source data | `TwoPhaseInletV2(Purnanto)-25-10000.dat.h5` |
| Source mesh | 7,601,261 cells; one `fluid` cell zone |
| Source identity | [Local hashes and topology](../../../../../PyAnsys/output/phase8-stage2/20261007/08b-native997k/source-local-identity.json) |
| Inlet rates | Liquid 116.92 kg/s; vapor 80.69 kg/s; other phase at each inlet zero |
| Numerics | SIMPLE; pseudo time OFF; PRESTO; second-order momentum/epsilon; first-order k; QUICK volume fraction |
| Parent settings | Exact loaded 08b models, materials, boundary values, numerical controls, native phase interaction, DPM injections and report definitions |
| Target | Supplied `Separator-purnanto-997k.msh.h5`; 997,604 cells |
| Zone matching | Preserve bottom; merge other target walls into `wall`; match fluid/interior names; match inlet mass-flow types |
| Absorber | No Stage 2 contact absorber or lower cell partition added |
| Archived coordinate | Native N10000; source liquid mass 327.184406 kg; vapor mass 129.209520 kg; liquid volume fraction 0–1 |
| Field start | Native interpolation of archived 08b data; no initialization |
| Budget | Zero new solve iterations |
| Proof | Settings/interaction/injection/report comparison; mesh check; field inventories and extrema; paired save/reopen |
| Checkpoint location | Local Windows `Documents/FluentRuns/Phase8/Stage2/20261007/08b-native997k` |
| Previous endpoint | Failed N518 pair hash-verified before source load; [preservation receipt](../../../../../PyAnsys/output/phase8-stage2/20261007/08b-native997k/prior-run-preserved.json) |
| Limit | Transfer is a starting case; it does not establish convergence, conservation after interpolation, or the cause of previous failure |
