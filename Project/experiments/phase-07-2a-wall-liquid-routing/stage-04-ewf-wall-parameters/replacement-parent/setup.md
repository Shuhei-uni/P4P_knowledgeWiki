# Stage 4 — Supplied N8000 parent: bulk response and film drain

| Contract | Selected test |
| --- | --- |
| Authority | Human, 8 October 2026: apply retained EWF settings; run 1,000 bulk-active iterations; assess extension versus bulk freeze; check frozen-film absorber compatibility |
| Parent | Phase72A root `auto-8000-1-08000.cas.h5` / `.dat.h5`; synchronized source hashes and local Server 1 copy verified |
| Preserved endpoint | Previous N48483 full-momentum endpoint; paired files and hashes retained |
| Question | Does the bulk settle after the film/drain changes, and can direct film drainage work with bulk frozen? |
| Parent assumption | Saved bulk accepted as the starting flow; the response test does not establish complete steady convergence |
| Fixed inputs | Parent mesh, full inlet feed, materials, contact absorber, carrier method, stored bulk and existing upper-film fields |
| Film physics | Retained full film momentum and force terms; EWF and Phase Accretion ON; DPM collection/splashing, stripping and separation ON |
| Wall change | Flow Momentum Coupling OFF; lower `wall:004` added to film domain; bottom remains outside film domain |
| Direct film drain | Thickness-proportional liquid mass sink with matching XYZ momentum sinks on lower wall; capture time 1.5 ms; independent of bulk collector and inlet command |
| Bulk collector | Retain parent phase-2 contact UDF at 10 µs and matched momentum sinks; no vapor mass sink |
| Numerical controls | Fixed film step 1 µs during bulk-active response; retained alternative implicit/coupled controls, 30 inner iterations / 10⁻⁵; DPM every 20 film updates |
| Drain refresh bound | Profile refresh each bulk iteration; conservative span of 10 × 1 µs; at most 1% local film depletion per declared span |
| Initialization | Allocate added lower film storage, then restore original parent data; no bulk initialization; preserve upper film and native clock |
| Build proof | Settings readback, bulk/source invariants, local paired save/reopen; version-matched guide Figures 30.1, 30.2, 30.6 and 30.9 reviewed |
| Drain proof | Disposable frozen-bulk source fixture plus production-mode frozen-film smoke; restore prepared parent before the requested run |
| Requested solve | One native `/solve/iterate 1000`; local transcript, reports and final pair; passive transcript observation |
| Stop limits | Film thickness ≥0.3 m or Courant ≥1 rejects further film continuation; solver failures require preserved endpoint and in-scope recovery |

| Evidence / decision | Requirement |
| --- | --- |
| Residual plot | Native continuity, velocity, turbulence and phase residuals over the complete 1,000-iteration interval |
| Inventory plot | Bulk total/lower liquid mass and total/upper/lower film mass; actual native iteration and film time |
| Absorber plot | Applied bulk mass removal, expression removal and direct film removal; source-inclusive outlet terms kept separate from boundary flux |
| Film numerical checks | Courant, thickness, speed, accepted clock/count and source/storage ledger; achieved inner residuals if available |
| Freeze decision | No sustained late bulk inventory/outlet trend; bounded residuals and finite film fields; direct film removal proved with frozen bulk |
| Extension decision | Bulk still adjusts with bounded numerical behaviour; another fixed-input hold can reduce the uncertainty |
| Claim limit | Short response and film-drain functionality; no physical validation, whole-system closure, steady-film or mesh-convergence claim |
| Machine owner | [Run manifest](../../../../../PyAnsys/output/phase72a-stage4-replacement/20261008/run-manifest.json) |
