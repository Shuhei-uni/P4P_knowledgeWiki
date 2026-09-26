# E6 execution map

Run `p7b-s40-t020-coupled-cfl20-nphase-20260923T024536Z`. Machine evidence: `PyAnsys/output/p7b-s40-t020-coupled-cfl20-nphase-20260923T024536Z/`. Worker/job: `PyAnsys/output/phase07b-convergence-investigation/e6/`.

[Setup](setup.md) owns the N-phase-only delta and N5000 cap. Runner preserves E5 final, loads original clean N0, uses identical SIMPLE Hybrid fields then applies treatment. Exact settings, source, monitor and save/reopen parity plus N0 physical/geometry equality precede solve. N50 smoke must verify all exposed residuals, scalar and exact-face flux histories, source lag and diagnostics.

One controller only; never connect a second client while advancing. Use local `audit_phase07b_running.py` after N50 and `--terminal` after exit. N50/every500/final pairs (N5000 uses final), scheduled/event whole-cell snapshots, initial/final horizontal/full-height axial fields, all exposed residuals are required. Expected equations come from the live manifest; no assumed primary residual name. Section requirements use index.json. No old E4 reconciliation.

Complete G6 against E5 using the declared late windows and native QA, then select the next evidenced step under the plan. Build/run progress belongs to phase-state and manifests.

G6 tooling: `compare_phase07b_solver.py --experiment E6`; `diagnose_phase07b_e4.py --experiment E6 --child PyAnsys/output/<verified-terminal-run>`; `export_phase07b_g3_native.py <verified-terminal-run-path> --experiment E6 --output <unique-output-path>`. Native exporter requires completed G6 child summary, no active controller, and restores the child endpoint. E6/CFL20 labels have distinct graphics names. All require terminal evidence before invocation.

Current disposition: prepared-data reload caused multi-rank SIGSEGV before solving; worker exited, API unreachable. See [results](results.md). Never relaunch this job ID or claim N50 passed.

## Recovery retry selected after API restoration

Run `p7b-s40-t020-coupled-cfl20-nphase-20260923T223022Z`; job and worker evidence in `PyAnsys/output/phase07b-convergence-investigation/e6/retry1/`. Uses `--nphase-before-hybrid` under [recovery design](recovery.md). Direct physical/geometry NPZ proof must pass before both initial and prepared pair saves/reopens, followed by normal final N0 field/geometry and N50 recording proof. No hidden allocation iterations. The old failed run remains the first attempt; the selected retry and exact controller status belong to phase-state.

Active retry is now `p7b-s40-t020-coupled-cfl20-nphase-20260923T223400Z`, job under `e6/retry2/`. Retry1 stopped at session automatic compilation preference mismatch before any scientific preparation/solve; preference repaired to original False and E5 restored. Never relaunch retry1.

Current recovery retry3 is `p7b-s40-t020-coupled-cfl20-nphase-20260923T225542Z`, job under `e6/retry3/`. Retry2 stopped before solve at the post-Hybrid counter guard. A separate source-free persistence probe passed with native counter0 and exact ordered original fields/geometry after reopen. The narrow pre-save representation repair is declared in recovery.md; all prepared/postreload and N50 requirements remain unchanged. Follow phase-state and the active manifest for actual progress.

Current retry4 is `p7b-s40-t020-coupled-cfl20-nphase-20260923T225918Z`, job `e6/retry4/`. Retry3 timed out during connection before any setup; read-only reconciliation confirmed idle preserved E5N5000. E6-only handshake deadline is now90seconds. Scientific gates/settings unchanged.

Current continuation: `p7b-s40-t020-coupled-cfl20-nphase-resume-20260923T231816Z`, job `e6/resume-n50/job.yaml`. Parent retry4 stopped afterN50 because diagnostic raw fraction integration did not equal native normalized inventory. Recovered completeN50 evidence and unique pair are in parent `recovery-n50/`. Continue same liveN50 without reload/init; extraN55 snapshot/checkpoint thenevery500 to absolute5000. Monitor retains rawbothphase fractions plus normalizedinventorynativeparity and rawsumextrema. See recovery.md for evidence, tolerance and limits. Never relaunch prior retries.
