# Stage 3 — Three inlet speeds at 500 ms film time

| Contract | Selected work |
| --- | --- |
| Human instruction | 6 October 2026: continue on Server 1; reference plus lowest/highest Phase 8 speeds; all three cases to 500 ms; continuously monitor and recover |
| Question | How does inlet speed change film inventory, spatial development and drainage at equal film time? |
| Classification | New inlet-speed contrast; reference continuation reuses the selected Stage 3 field history |
| Placement / authority | Server 1 fully owned; Server 3 remains separate |
| Horizon | 0.500 s actual native film time since dry-film activation; not 500 ms of carrier physical time |
| Current reference parent | Saved/reopened N25815; 0.2651843386356894 s; 6.688275530493504 kg film |
| Reference case hash | `ed46a6f0ce4ee6076e1f5bd0673f081418b43cbfed7529cfc92ef539c71cf26a` |
| Reference data hash | `48efe32e059f33f2716469f9a0e92f4f4b4c2781d8905136e28a1fefd79ee6d1` |
| New-arm parent | Same prepared historical A bulk fields and dry EWF at N1580; independent startup at each speed |
| A case hash | `5907e357654ebe5437c64f4e6abea19cbbc66b1edd2312f6b2eb63fe408c2b72` |
| A data hash | `72a7134f6358ea68615907f336e71d6e518c713418674477703fc638e41816af` |
| Initialization | Load paired parent; no bulk or film reinitialization |

| Case | Nominal Phase 8 speed (m/s) | Feed factor | Liquid (kg/s) | Vapor (kg/s) |
| --- | ---: | ---: | ---: | ---: |
| Reference | 26.81 | 1.000000000 | 116.920000 | 80.690000 |
| Low | 20.11 | 0.750093249 | 87.700903 | 60.525024 |
| High | 32.14 | 1.198806416 | 140.164446 | 96.731690 |

| Definition / invariant | Contract |
| --- | --- |
| Speed source | [Phase 8 speed contract](../../../../phase-08-storyline-reconstruction/stage-01-60k-storyline/report-contract.md); lowest/highest points verified in its runnable carrier implementation |
| Flow conversion | Scale this case's liquid and vapor commands together by nominal speed / 26.81; retain phase split and inlet openings |
| Nominal label limit | Stage 3 baseline commands are 116.92/80.69 kg/s; Phase 8 parity commands differ slightly. These are matched nominal speed ratios, not copied Phase 8 physical cases. |
| Scientific model | Existing 60,964-cell mesh, R3 height 0.5 mm / Cs 0.5, corrected contact absorber tau 10 µs, E2.7 walls/forces/sources/coupling, diagnostic one-way DPM |
| DPM | Retain saved diagnostic injections and coupling; no new DPM-allocation contrast; bulk interaction and EWF DPM collection are off |
| New-arm startup | From A: Coupled/EWF active; 500 updates at quarter of that arm's target feed; 2000-update inlet ramp; 1000-update full-feed hold |
| Startup film controls | Same fixed 1 µs / 10-subiteration original startup; record inner residuals and their limits |
| Frozen forcing | After each arm's own N5080 startup, freeze all bulk equations; do not change inlet commands on a frozen reference flow and call it a new speed case |
| Film development | Alternative implicit route; per-arm matched-film-time qualification before larger steps; adaptive target 0.2, growth 1.15, reduction 2; actual accepted steps verified |
| Reference step | Continue its verified 7.604375 µs step; screened range up to 20 µs; reduce controls if evidence requires recovery |
| Early stopping | No early completion at stationarity or a review point; each selected arm reaches the requested film-time horizon |
| Terminal time | Cut final remainder where possible; otherwise at most one qualified accepted step beyond 500 ms, explicitly recorded |
| Numerical recovery | Preserve rejected pair; restore last passing pair; lower step/target; separate recovery branch and re-verify |
| Batch checks | Finite nonnegative facet fields; Courant ≤1; maximum reported thickness ≤3 mm; film ledger ≤0.1%; accepted steps within arm's qualified range |
| Inventory review bound | 12.3 kg × feed factor; a case-specific review bound, not a physical film limit |
| Checkpoint policy | Paired local saves/reopen each roughly 1000 updates; final pairs shared to OneDrive and hashes checked |
| Supervision | Active controller, streamed client/native transcripts and per-batch verified receipts; resolve connection loss before resubmission |

| Evidence | Definition / comparison |
| --- | --- |
| Core film history | Film inventory, accretion, drainage and storage against actual film time; all three arms; selected parent paths only |
| Endpoint comparison | 500 ms film mass, maximum thickness, area-weighted thickness coverage, normalized drainage/accretion and liquid routing |
| Common rate window | Final 10 ms of film time; integrate using accepted film increments; do not compare equal update counts at different steps |
| Spatial comparison | Same wall facets, camera and shared thickness scale at each 500 ms endpoint |
| Numerical evidence | Actual accepted steps, native film clock, Courant, ledger, matched-time field comparison and paired save/reopen |
| Carrier evidence | Each new arm's complete startup residuals, boundary flows and bulk inventory; frozen bulk thereafter |
| Claim limit | Equal-time film development under separately developed frozen bulk fields; 500 ms does not establish stationary film, full-model conservation, timestep independence or physical validation |
| Prior knowledge | [Verified adaptive procedure](../../../../../../CFD_wiki/wiki/guidance/fluent-general-click-by-click.md#adaptive-ewf-stepping-apply-and-verify-2025-r2); [preceding numerical setup](../film-development/setup.md) |
| Runner | [Campaign controller](../../../../../../PyAnsys/scripts/setup/run_phase72a_stage3_speed_sensitivity.py) |
| Machine evidence | [Campaign manifest](../../../../../../PyAnsys/output/phase72a-stage3-speed-sensitivity-server1/20261006/run-manifest.json) |
