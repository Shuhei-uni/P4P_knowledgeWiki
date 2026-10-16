# Non-zero wall-film initialisation — research assessment

| Decision | Assessment |
| --- | --- |
| Human request, 15 October 2026 | Full Server 6 authority; research transfer of the last 997k film state into another case before execution |
| Technical answer | Fluent 2025 R2 supports non-zero initial film height and velocity; spatial transfer through profiles is a supported candidate route |
| Recommendation | First prove a spatial film transfer on a copy of the same 997k case; then test a corresponding mesh or geometry |
| Scientific use | A prescribed wet-film initial condition that may reduce film development cost |
| Scientific limit | Transferred film is not proof of steady film, mesh independence, physical validation, or elapsed target-case film development |
| Live Server 6, 16 October | Fluent 2025 R2 responded; idle startup-failure case at native expression N7000 / 0.542 ms identified; connection reset during read-only host check, then configured TCP port timed out |
| Execution | No solver mutation, case replacement, initialisation, solve or process termination performed |
| Machine evidence | [Donor hashes, saved fields, API inspection and connection result](../../../../PyAnsys/output/phase9-ewf-server6-997k/20261015/nonzero-film-research-preflight.json) |

| Selected receiver and transfer preparation | Result |
| --- | --- |
| Human selection | Server 4 / 2_6M selected initial bulk-development pair, N8580; execute transfer on Server 6 when accessible |
| Receiver identity | 2,596,657 cells; inherited film age 0.700 ms; [original paired-file receipt](../../../../PyAnsys/output/phase9-mesh-convergence-server4/20261007/final-initial-bulk.json) |
| Local receiver case | SHA-256 matches the original receipt |
| Local receiver data | File entry has expected 1,168,416,980-byte size but remains a OneDrive dataless placeholder; full read stalled; fresh local data hash is unverified |
| Selected candidate profiles | [2.6M film initial-condition profiles](../../../../PyAnsys/output/phase9-ewf-server6-997k/20261015/receiver-2_6M-N8580-normal-aware/receiver-film-candidate.prof) |
| Mapping method | Match named walls; choose nearest compatible face among 64 candidates, normal dot product ≥0.9; project velocity onto receiver wall tangent |
| Corner check | 2,117 main-wall faces required a different donor from unrestricted nearest-face mapping; minimum selected normal alignment 0.997115 |
| Film-wall faces | Main wall 31,164 →47,218; lower `wall:004` 402 →402 |
| Total film volume | Donor 0.00234976854 m³; mapped 0.00234850559 m³; change −0.05375%; no thickness scaling or clipping |
| Main-wall film volume | Change −0.05509%; maximum source/target centroid distance 31.83 mm |
| Lower-wall film volume | Change +0.33942%; maximum source/target centroid distance 2.34 mm |
| Thickness | Maximum mapped height remains 0.58771157 mm |
| Mapping limit | Offline surface geometry and stored fields only; small volume change does not prove native initialisation, momentum preservation or physical accuracy |
| Candidate supersession | Unrestricted nearest-face profiles are marked superseded because some face normals were incompatible; use the normal-aware folder |
| Mapping proof | [Per-wall mapping receipt](../../../../PyAnsys/output/phase9-ewf-server6-997k/20261015/receiver-2_6M-N8580-normal-aware/mapping-receipt.json) |
| Transfer preflight and review | [Receiver identity, code review and external blocks](../../../../PyAnsys/output/phase9-ewf-server6-997k/20261015/receiver-2_6M-preflight.json) |
| Code review, 16 October | Replaced invalid scratch inspection RP names/activity expression with checked paths; added durable snapshots before host introspection and reconciliation after lost acknowledgement; [review receipt](../../../../PyAnsys/output/phase9-ewf-server6-997k/20261016/connection-code-review.json) |
| Loaded-case caution | The observed startup-failure case is not the verified donor; film Courant is non-finite; do not continue its solve |
| Execution block | Endpoint responded briefly on 16 October, then reset during host-file inspection and failed subsequent TCP checks; no case replacement, initialisation or solve submitted |
| Resume requirement | Responsive Server 6 endpoint and complete receiver data available on its local disk; preserve current endpoint, apply EWF-only profiles, save/reopen and smoke-test |

| Donor check | Verified evidence |
| --- | --- |
| Selected source | [Completed Server 3 lane](../server3-997k/results.md), 997,604 cells, N50900, film age 200 ms |
| Source lineage | Selected N8080 / 0.650 ms parent; frozen development through 195 ms; final 5 ms bulk active |
| Saved pair | `997k-ewf-final-N50900.cas.h5` and matching `.dat.h5`; both local OneDrive copies read and SHA-256 matched to the final shared-copy receipt |
| Film inventory | Saved native report: 2.06358756 kg |
| Maximum film thickness | Saved native report: 0.58771158 mm; HDF5 field maximum 0.58771157 mm |
| Spatial data | 31,566 stored film face entries; 28,990 have positive height; remaining entries have zero height |
| Available fields | Finite `SV_EFILM_HEIGHT`, `U/V/W` and `US/VS/WS`; initialisation requires the appropriate film velocity, not an assumed interface-velocity substitution |
| Source identity limit | These saved artifacts establish the donor; they do not establish what Server 6 currently holds |

| Research finding | Basis and implication |
| --- | --- |
| Non-zero film is allowed | [2025 R2 User Guide §30.5](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/flu_ug_ewf_sec_bound.html): Initial Condition accepts film height, three velocity components, temperature and passive scalar |
| Initial state evolves freely | [2025 R2 Theory Guide §17.2.3](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_th/flu_th_ewf_sec_bcs.html): initial height and velocity apply at the first film time step; specified fluxes instead act as sources |
| Profiles can carry spatial state | [2025 R2 User Guide §3.7](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/flu_ug_ProfileFiles.html): write surface coordinates and selected fields, then read profiles into another case |
| EWF profile inputs exist in the versioned API | Local PyFluent 0.42.0 `settings_252`: wall `film_height` and each `flux_momentum` item expose `profile_name`, `field_name` and `udf`; live allowed options and the velocity meaning in Initial Condition mode need readback |
| Mapping needs its own check | [2025 R2 User Guide §8.9](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/flu_ug_bcs_sec_prof.html): point profiles interpolate to boundary faces; nearest-point interpolation is the default; profile data use SI units |
| Thickness clipping can hide transfer loss | [2025 R2 User Guide §30.4](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/flu_ug_ewf_sec_eqns.html): maximum thickness removes film above its limit |
| Generic bulk interpolation is insufficient evidence | Native Replace Mesh may transfer bulk fields; this research has not established that it preserves the EWF face fields or their inventory |

| Receiver | Preferred route | Main condition |
| --- | --- | --- |
| Same mesh, full-state continuation | Copy the paired case/data and apply the declared setup change | Retains bulk history as well as film history |
| Same mesh, film only | Export spatial film height and velocity; initialise EWF in the receiver while preserving its bulk solution | Prove recovered face fields and initial inventory; a full data read also imports bulk fields |
| Different mesh, same geometry | Map profiles separately on corresponding physical film walls | Check wet area, mass, momentum, coverage, positivity and tangential velocity |
| Changed geometry | Map only physically corresponding surfaces; declare initial conditions for new surfaces | New ramps, blockers and disconnected film edges can change drainage and have no unique donor counterpart |
| Uniform or wall-average height | Use only as a separately labelled sensitivity case | Removes the donor's spatial wet/dry pattern and local thickness gradients |

| Verification step | Required evidence |
| --- | --- |
| Reconcile Server 6 | Live case/data identity, film age, iteration, controllers and solver activity; preserve any valuable endpoint before loading a child |
| Load donor on Server 6 | Hash-check the selected pair locally; reopen and compare film inventory, thickness and velocity to the donor receipt |
| Export film | Coordinates, wall identity, height and film velocity components; include temperature/scalars only when their equations require them; confirm native export variables exist |
| Same-mesh round trip | Compare exported and initialised fields at the same pre-solve or first-step coordinate; save/reopen; account for first-step evolution if values are applied only on the first film step |
| Preserve receiver bulk | Compare bulk inventories and fields before/after EWF-only initialisation; do not perform full flow initialisation |
| Check mapped inventory | Evaluate film mass as the surface integral of density × height; report source-to-target change separately from the save/reopen check |
| Check mapped velocity | Use film velocity components; project onto changed wall tangents when required; record the resulting momentum change |
| Controlled smoke | One bounded test of the new initialisation route; inspect film advance, finite fields, mass change, direct removal and native outflow separately |
| Subsequent fixed solve | Use at least 1,000 iterations when inputs remain fixed, bounded by the next required decision |
| Scientific comparison | Compare wet and dry starts under the same receiver setup; assess whether inventory, drainage, carryover and spatial film state lose dependence on the initial condition |
| Time accounting | Record donor age, receiver age since initialisation and any inherited clock separately; mapping a 200 ms donor does not simulate 200 ms on the receiver |

| Practical judgement | Consequence |
| --- | --- |
| Useful for wet-start investigations | May avoid repeating early film formation; actual cost reduction remains untested |
| Does not resolve source/receiver inconsistency | Changed inlet, mesh, film model, roughness or drain requires relaxation under the receiver's own equations |
| Added initial inventory must be explicit | A film-only transfer adds liquid to an unchanged bulk state; include that film in the receiver's initial mass ledger |
| Source remains a developing numerical state | Completion of the 200 ms schedule does not establish a stationary or physically validated film |
| Current unresolved work | Live Server 6 recovery/inspection; complete receiver data availability; native profile round trip and selected 2.6M transfer test |
