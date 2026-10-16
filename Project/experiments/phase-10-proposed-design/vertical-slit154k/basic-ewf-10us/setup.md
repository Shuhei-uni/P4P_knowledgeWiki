# Vertical slit — angled-settings continuation

| Current continuation — 13 October 2026 | Selected value |
| --- | --- |
| Authority | Human: do another 100 ms on this vertical basic-EWF case |
| Parent | Verified saved/reopened N34661 / 50.000 ms |
| Target | N44661 / 150.000 ms total film age |
| Step and count | Restore fixed 10 µs after the prior 8 µs endpoint update; one 10,000-update native command |
| Physics | Same basic angled EWF, film-wall scope, roughness and native outflow; bulk remains frozen |
| Preparation | Preserve 50 ms pair, apply 10 µs step, save/reopen and verify before solve |
| Numerical thresholds | None; diagnostic histories retained |
| Shared endpoint | Unique OneDrive final-150ms pair; earlier pairs preserved |
| Machine evidence | [150 ms continuation](../../../../../PyAnsys/output/phase10-proposed-design/20261013/vertical-basic-ewf-to150ms/) |

## Original 50 ms run

| Contract | Selected value |
| --- | --- |
| Authority | Human, 12 October 2026: vertical slit with the same EWF settings as angled slit; start around the same native iteration; use 10 µs |
| Parent | Existing vertical autosave N31000 / 13.392 ms; closest saved count to angled N30862 / 23.705 ms |
| Target | 50.000 ms total film age, matching the angled endpoint |
| Basic EWF | Exact angled native model-parameter readback; fixed 10 µs main step; 10 film inner iterations, tolerance 1e-5 |
| Film wall scope | Upper `wall` active; lower `wall:004` non-film with native outflow at the film-domain edge |
| Numerical lower-film drain | Disabled; source switch zero; no lower film domain |
| Wall conditions | Same roughness 0.5 mm / coefficient 0.5; physical bottom smooth; same DPM wall conditions by physical role |
| Bulk | Mixture/RNG/Coupled full-feed fields remain frozen |
| Run plan | 10-update changed-mode smoke; 3650 fixed 10 µs updates; one 8 µs endpoint update; expected N34661 / 50.000 ms |
| Numerical thresholds | None; Courant and film diagnostics recorded |
| Evidence | Exact model and wall readback after paired save/reopen; local transcript, monitor histories, paired checkpoint hashes and endpoint reopen |
| Preservation | Existing vertical enhanced-EWF N84000 / 50.9 ms and angled N33492 / 50 ms preserved |
| Shared final destination | OneDrive Phase10/proposed-design/vertical-slit-basic-ewf-10us |
| Claim limit | Continuation settings match; earlier enhanced-film history and initial film age differ. Lower-wall film is removed when its film domain is disabled. Bulk fields were not recomputed for the roughness change |
| Machine evidence | [Run directory](../../../../../PyAnsys/output/phase10-proposed-design/20261012/vertical-basic-ewf-10us/) |
