# Stage 3 — Accelerated film development

| Goal / authority | Contract |
| --- | --- |
| Human-selected goal | Develop the wall film as quickly as numerical stability permits; reach steady film |
| Authority | Continue Stage 3 on fully owned Server 1; 5 October 2026 |
| Owning workflow | `phase-loop`; ordinary numerical recovery and continuation remain in scope |
| Parent | Verified early-EWF N5080; 3.5 ms film time; no initialization |
| Parent film / bulk mass | 0.164512157 / 61.054882609 kg |
| Parent case SHA-256 | `e6aaed696398faa0968bb1dd287f22006c99d71762030fd3a4ceea04fbed7af4` |
| Parent data SHA-256 | `a12b23308d71c44ca6899bb8ed6000f0713f25594938a54e86bf80300af7bf00` |
| Separate work | Server 3 Stage 2 continuation; do not read its live session or change it |
| Invariants | Mesh, materials, full feed, R3, corrected contact absorber, carrier numerical controls apart from the declared temporary freeze, film equations and sources, EWF walls/flow feedback and DPM |
| Parent limit | 15 late inner-film failures with ten subiterations; small ledger error does not remove this limit |

| Numerical strategy | Selected operation |
| --- | --- |
| First repair | Retain fixed 1 µs; allow 30 film subiterations; 100-update probe |
| First adaptive candidate | Courant target 0.05; growth 1.3; reduction 2; initial-step setting 1 µs; retain film fields and clock |
| Step evidence | Printed accepted steps plus saved native film clock; do not treat timestep-max as an adaptive ceiling |
| Growth policy | Qualify a short probe, then a 1000-update batch before raising the target |
| Candidate targets | 0.05 → 0.075 → 0.10 → 0.15 → 0.20; only while inner-solve and accounting evidence remain adequate |
| Recovery | Preserve poor endpoints; return to a verified parent; allow 60 or 100 inner iterations or reduce the step/target |
| Baseline fallback | Smaller fixed step if the current 1 µs inner failures persist; numerical failure does not reject the film-development goal |
| Solver repair contrast | If smaller steps retain the residual plateau, test sequential film mass/momentum solution from the same N5080 fields at 1 µs; retain bulk Coupled and all film equations/forces; qualify before step growth |
| Alternative implicit repair | If sequential film also fails, test the alternative implicit scheme exposed by Fluent 252's version-matched TUI under `eulerian_wallfilm.implicit_options.new_implicit_scheme`; beta numerical route; unchanged equations/fields; compare at 1 µs before adaptive growth |
| Frozen-bulk diagnostic | From the original N5080 fields, freeze bulk drift/flow/k–ε/phase-fraction equation advancement; retain all physical settings and the original film solver at 1 µs; test whether changing bulk forcing drives the film residual bursts |
| Frozen-bulk claim boundary | Temporary numerical diagnostic/relaxation; restore every bulk equation and check the full model before calling its film steady |
| Alternative-solver adequacy test | Residuals are unavailable and never counted as passed; compare 0.5 µs ×1000 and 5 µs ×100 from identical N5080 fields and frozen bulk forcing, each adding 0.5 ms; capture native facet mass, thickness and velocity |
| Matched-time screen | Mass-distribution L1 difference ≤1%; film-mass-weighted velocity difference ≤2%; maximum thickness difference ≤2%; both ledgers ≤0.1%; finite positive fields within recovery bounds; limited to this tested film state/time range |
| Second matched-time candidate | If 5 µs passes, test 10 µs ×50 against the same preserved 0.5 µs reference at 4.0 ms; same criteria and frozen fields; the previous 10 µs failure used the original implicit solver |
| Larger matched-time candidates | If differences leave a clear margin, test 20 µs ×25 and 50 µs ×10 at the same film time; retain the last passing pair; Courant ≤1 and all field/ledger criteria apply; no automatic acceptance of a larger step |
| Alternative continuation limit | A passing matched-time screen permits exploratory development with that method; retain the missing inner-solve evidence as a limit; repeat the timestep check on developed film before quantitative qualification |
| Screened adaptive continuation | Start from the best passing matched-time pair; temporarily retain its frozen bulk fields; target 1.3 times its tested peak Courant, bounded to 0.1–0.5; growth 1.3, reduction 2; 100-update probe then 1000-update batches |
| Adaptive step growth outside screen | Preserve endpoint and previous qualified pair; stop for another matched-time contrast if any accepted step exceeds the tested step; native timestep-max is not an adaptive ceiling |
| Courant-spike recovery | Preserve rejected N8190; resume exact passing N7190 after live pause-state verification; fixed 5 µs ×100 first, then adaptive target 0.2, growth 1.15, reduction 2; inspect a 100-update probe and 1000-update development batches |
| Alternative stationary screen | Three consecutive 1000-update windows with drainage deficit and absolute storage/accretion ≤1%, ledger ≤0.1%, finite positive facet fields; provisional while inner residuals are unavailable and bulk remains frozen |
| Full goal qualification | After frozen-film stationarity, repeat a developed-film timestep comparison, restore all bulk equations and verify sustained film stationarity with updating bulk flow; do not close the goal at the frozen screen |
| Compute measure | Film milliseconds per wall minute; subiteration cost counts against any speed gain |
| Native batch size | 100 for a numerical contrast; approximately 1000 for development and sustained checks |
| Film-time review points | 10, 50, 100, 200 and 500 ms since the dry A start |
| Bounded segment | Up to 200000 additional updates or 500 ms before a new evidence-led continuation decision; neither limit means steady film |
| Checkpoints | Paired local FluentRuns saves after each probe/batch; selected expensive endpoints and final pair shared |

| Evidence / criterion | Requirement |
| --- | --- |
| Instrumentation | All 31 native report histories; all seven carrier residuals; native and client transcripts; every film subiteration |
| Child proof | Preserve N5080; change only stated film controls; fields and film clock match after save/reopen |
| Film ledger | ΔM + ΔD − Σ(A Δt), using actual native film steps |
| Step increase eligibility | At least 99% of updates meet all h/u/v ≤1e−5; no final residual above 1; ledger error ≤0.1% |
| Numerical bounds | Nonfinite fields, CFL >1, maximum thickness >3 mm, film mass >12.3 kg or film ledger error >1%; preserve and recover |
| Steady-film screen | Three consecutive 1000-update windows: absolute drainage deficit ≤1%; absolute storage/accretion ≤1%; film ledger ≤0.1%; ≥99% inner tolerance pass; no final residual >1 |
| Persistence check | Inspect raw inventory, transfer rates, film thickness and sustained windows; do not infer stationarity from one endpoint |
| Primary plot | Film mass and accretion/drainage/storage against actual film time |
| Supporting plot | Accepted step, CFL and final/peak inner residuals; carrier inventory, carryover and continuity |
| Scientific limit | Film-side development and numerical adequacy; whole-separator closure, timestep independence and physical validation remain separate |
| Prior method | [Verified adaptive procedure](../../../../../../CFD_wiki/wiki/guidance/fluent-general-click-by-click.md#adaptive-ewf-stepping-apply-and-verify-2025-r2) |
| Implementation | [Continuation runner](../../../../../../PyAnsys/scripts/setup/continue_phase72a_stage3_film_development.py) |
| Machine evidence | [Run manifest](../../../../../../PyAnsys/output/phase72a-stage3-film-development-server1/20261005/run-manifest.json) |
