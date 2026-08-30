# 03A Stage 4 — results

## What ran

The recovered execution evidence distinguishes the native queue from its later recovery branch. It does not infer a successful endpoint from a console iteration count or from a file that lacks the required paired evidence.

| Branch | Actual evidence | Status |
|---|---|---|
| S4-01 | native continuation from F05 reached cumulative iteration `33,000`; paired checkpoints, named endpoint, residual export, transcript, and physical histories exist | completed diagnostic; identity/checksum still Missing Info; PNG visual review done; CSV window stats Missing Info |
| S4-02 | native console reached cumulative iteration `36,000`; paired checkpoints exist through `35,000`; no named endpoint or native residual export, but the transcript contains the cumulative residual table | completed-budget but endpoint-incomplete; forensic evidence only, not parent-eligible |
| S4-03 | recovery continuation from F11 reached cumulative iteration `45,000`; paired checkpoints, named endpoint, residual export, transcript, and physical histories exist | completed diagnostic; identity/checksum still Missing Info; PNG visual review done; CSV window stats Missing Info |
| S4-04 | standard-`k-epsilon` case was prepared from the F11 parent at cumulative 15,000; no solve, data, checkpoint, transcript, or report histories | prepared-only; not executed |
| S4-05 / S4-06 | exact F09 40% parent was not proved accessible for this queue | gated; not submitted |

## Evidence / plots / measurements

The [migrated source execution report](source-native-queue-execution-2026-08-23.md)
records the portable Server-2 evidence package, including residual CSV/JSON
histories, 30 physical report histories per executed branch, checkpoint
relocation manifests, plots, and the authoritative remote case/data locations.
The locally retained report-facing PNGs are indexed in the [Stage-4 figure
index](figures/README.md). The portable CSV/JSON files were not committed and
are not in this checkout (Missing Info). Git history contains the PNGs only.

This 2026-08-30 review used those committed PNGs plus the already-copied
endpoint residual table. It did **not** recompute 0–5k / 5–10k / 10–20k /
20–30k mean, median, P95, or slope. Those remain Missing Info until the
Server-2 CSV/JSON package is recovered.

The recovered endpoint residuals illustrate why the continuation is still diagnostic:

| Branch | Cumulative iteration | Continuity | `k` | `epsilon` | Volume-fraction residual |
|---|---:|---:|---:|---:|---:|
| S4-01 | `33,000` | `0.155722` | `1.23642e-03` | `0.133098` | `2.22671e-03` |
| S4-02 | `36,000` | `0.15066` | `1.4070e-03` | `0.10394` | `2.1425e-03` |
| S4-03 | `45,000` | `1.37284` | `1.04189e-03` | `0.0489749` | `2.19014e-03` |

These residual snapshots are not enough to establish stationarity. They are
consistent with the PNG residual envelopes (Observed).

### Inventory-family freeze

Stage-3 currently carries two inventory families that must not be mixed:

| Family | F05 at 3,000 | F11 at 15,000 | Relation to Stage-4 PNGs |
|---|---:|---:|---|
| 2026-08-20 volume-integral extraction ([source](../stage-03/source-fixed3000-results-20260820.md)) | `317.752 kg`, `0.360585 m³` | `345.365 kg`, `0.391921 m³` at 100% / 15,000 | **Observed match** to Stage-4 PNG start values |
| 2026-08-21 checkpoint table in Stage-3 results | `4,457.055 kg` | `4,686.969 kg` | **not used** for Stage-4 PNG comparison until reconciled |

Mass-imbalance families agree: F05 signed imbalance `−14.336%` (Reported) matches the S4-01 PNG start near ~0.14 relative (Observed). Y010 + Y030 exceeding total liquid mass is already present in the 2026-08-20 table and is treated as overlapping zone diagnostics, not a unit bug.

This review uses the 2026-08-20 / Stage-4 PNG family only.

### Core figure completeness

| Figure | Status | Source |
|---|---|---|
| F0 cross-branch | complete PNG | [00-cross-branch-comparison.png](figures/03a-stage4/server2/00-cross-branch-comparison.png) |
| F1–F7 per S4-01 | complete PNG; CSV stats Missing Info | [s4-01](figures/03a-stage4/server2/s4-01/) |
| F1–F7 per S4-02 | complete PNG; diagnostic-only; CSV stats Missing Info | [s4-02](figures/03a-stage4/server2/s4-02/) |
| F1–F7 per S4-03 | complete PNG; CSV stats Missing Info | [s4-03](figures/03a-stage4/server2/s4-03/) |
| Prescribed window mean/median/P95/slope | unavailable | portable CSV/JSON remain remote-only |

Windows below are continuation-from-parent unless a per-branch PNG uses cumulative Fluent iteration. S4-01 parent = 3,000; S4-02 parent = 6,000; S4-03 parent = 15,000. The 20–30k continuation window is therefore cumulative 23–33k / 26–36k / 35–45k.

### Visual window review (Observed from PNG; not computed statistics)

**Residuals (F1/F2).** Momentum residuals drop early then sit near `~3e-5`. Volume-fraction residuals plateau near `~2e-3`. `k` occupies a noisy band roughly `1e-3`–`1e-1`. `epsilon` spikes from `~1e-2` to `>1e2`–`1e3` for the entire `+30,000` on all three executed branches; the late envelope is not visibly smaller than the mid-run envelope. S4-01/S4-02 continuity sit near `O(10^{-1})`. S4-03 continuity is a distinct `O(1)` band from early in the continuation through 45,000; endpoint `1.37284` sits inside that band, not on a terminal spike. S4-02 transcript residuals at 36,000 (Reported): continuity `0.15066`, `k` `1.4070e-3`, epsilon `0.10394`, vf `2.1425e-3`.

Following PR #7 / Stage-2–3 residual-mass interpretation: a bounded-but-ugly `k`/`epsilon` envelope is not by itself a parent failure. These plots look like persistent intermittency, not a runaway residual. Continuity remaining `O(10^{-1})` to `O(1)` is a separate, stronger residual objection.

**Mass imbalance (F3).** After an early drop from ~0.14/0.12, all three branches occupy a persistent relative-imbalance oscillation of roughly **0.05–0.11** (about 5–11% of inlet) for the rest of the budget. The late-window envelope does not visibly shrink. S4-02’s band sits slightly lower, with a few deeper dips, but late oscillation remains ~0.04–0.10. This is Observed visual range, not a window mean.

**Liquid inventory (F4).** Using the 2026-08-20 family: S4-01 and S4-03 rise from ~318–345 kg to a visually tight plateau near ~465 kg / ~0.525 m³ after ~10–15k continuation. S4-02 rises to a higher plateau near ~495 kg, with a mid-run excursion around 10–16k continuation, then a noisier high plateau. Visual flattening is **not** \(dM_l/dN \to 0\). CSV slope on 20–30k remains Missing Info.

**Phase routing and brine (F5–F7).** Liquid→brine is the dominant liquid outlet and remains noisy (~−87 to −100 on the PNG axis). Liquid→steam stays small (~−8 to −12). Vapour splits are flatter. Brine-entry static pressure sits near `1.122e6` and looks bounded. Inlet mixture traces look flat near the Stage-3 prescribed ~198.5 kg/s. Outlet traces keep oscillating. PNG flux axes say “configured Fluent units”; outflow is negative. Do not quote those traces as Stage-3 kg/s until sign convention is read back.

## Numerical state and limitations

- No recovered Stage-4 execution file indicates NaN, infinity, floating-point exception, or explicit fatal numerical divergence. That is an execution fact, not a convergence result.
- S4-02 has a scientific identity gap: its native continuation reached the budget in the console, but its named endpoint and native residual export were not written. The forensic pair cannot repair that gap. S4-02 may be used for residual/mass **trend**, not as a parent candidate.
- Native H5 case/data files remain on the last-known remote host. This cloud checkout has no `.env`, no `FLUENT_IP2`/`FLUENT_PORT2`, no `ansys` module, and no server-profile YAML. Live checksum/readback is Missing Info. File-transfer limitations still prevent treating local PNG extraction as a replacement for exact binary readback.
- No checkpoint is parent-eligible until paired-file completeness, remote checksums, exact case/data readback, and prescribed-window physical-history analysis are complete. PNG review is enough to **reject** parent eligibility for the executed RNG continuations; it is not enough to **accept** a parent.
- S4-04 did not test the turbulence-model hypothesis because it was prepared but never submitted. Its parent is F11 at 15,000, not S4-03 at 45,000. S4-05/S4-06 did not test the loading-path hypothesis because their exact parent remained gated.
- Historical S4-01/02/03 iteration was journal-owned. Any new solve is PyFluent unless Shuhei approves a journal for that specific run.

## Observations

Hypothesis, then observation, then interpretation:

- **Hypothesis A** (more iteration is enough): an unchanged `+30,000` from F05/F06/F11 would produce bounded residuals, low/stable mass imbalance, bounded inventory, and sensible routing together.
- **Observed, residuals:** momentum and vf settle into a non-decaying band; `k`/`epsilon` remain intermittent; S4-01/02 continuity ~0.15; S4-03 continuity ~O(1) for the whole continuation.
- **Observed, mass:** relative imbalance becomes a 5–11% undamped oscillation after the early drop.
- **Observed, inventory:** S4-01/S4-03 look visually plateaued near ~465 kg in the 2026-08-20 family; S4-02 is higher and had a mid-run excursion.
- **Observed, routing/pressure:** mostly liquid-to-brine and bounded brine-entry pressure, with oscillating liquid→brine.
- **Interpretation:** A is **weakened on residuals and mass**, **visually supported but unquantified on inventory**, and **not contradicted on brine pressure**. The three axes must stay split. A persistent mass-imbalance limit cycle plus unconverged continuity is enough to reject “low and stable” and to reject parent eligibility. It is not enough to declare the holdup field stationary, and it does not by itself prove that a bounded `k`/`epsilon` envelope cannot accompany a later parent-class field (PR #7).
- S4-01, S4-02, and S4-03 are not one residual failure mode. S4-03 is the worst continuity state despite the nicest inventory plateau. S4-02 is the only branch whose inventory did not simply rise-and-sit, so startup history is not shown to have washed out.
- The executed RNG branches do not discriminate “model form is important” (Hypothesis B) because S4-04 never ran. They do not discriminate “loading path is important” (Hypothesis C) because S4-05/S4-06 remain gated.

## Findings / interpretation

Stage 4 remains completed diagnostic evidence, not a qualified baseline. It does not establish physical convergence, mesh independence, plant validation, turbulence-model correctness, or separator performance.

**No qualified 03A parent currently exists.** Remote named S4-01 and S4-03 case/data pairs, and Stage-3 F05/F06/F11 parents, are Reported to exist on the last-known Server-2 tree; they are not missing files. None of those states has cleared the identity + prescribed-window gate, and the committed PNG histories plus endpoint residuals are enough to reject the executed RNG continuations as parent-eligible.

Do not infer a winner from the endpoint residual table. Do not promote S4-03 because its inventory looks flattest. Do not promote S4-01/S4-02 because continuity is “only” ~0.15.

## What this implies for the next review

When a Fluent endpoint is reachable:

1. Recover the portable CSV/JSON package and compute the contracted 0–5k / 5–10k / 10–20k / 20–30k window statistics. That analysis can refine magnitudes; it is not expected to reverse the PNG-based parent reject.
2. Live-hash and read back the named S4-01 and S4-03 endpoints and the hashed F11 15,000 parent. Record actual paths in [run-paths.yaml](run-paths.yaml).
3. Keep S4-04 as the **unexecuted Stage-4-B item**, parent F11 @ 15,000, RNG → standard `k-epsilon` only, `+30,000`, PyFluent unless a journal is explicitly approved. Do not create a parallel experiment that silently retargets S4-04 onto S4-03 @ 45,000.
4. Keep S4-05/S4-06 gated on the exact F09 40% parent. They are not falsified.

Open PR #7 (`codex/stage3-residual-mass-interpretation`) already records the Stage-2/3 residual-vs-mass split and the N5 standard-`k-epsilon` lead. This review does not recreate that retired `Setups/` packet and does not merge that PR.

## Prior-experiment collision (for any next solve)

| Candidate | Closest prior work | Exact delta | Class |
|---|---|---|---|
| Further unchanged RNG `+30k` from S4-01/S4-03 endpoints | S4-01/S4-03 themselves | longer RNG continuation after a demonstrated 5–11% mass limit cycle | **REDUNDANT** unless a specific correction (identity repair, different monitor, different numerics) is stated |
| S4-04 standard `k-epsilon` from F11 @ 15,000 | Stage-2 N5 (standard `k-epsilon` +500 then RNG return +300 from Stage-1); S4-03 is the RNG control from the same F11 parent | stay on standard `k-epsilon`, no RNG return, `+30k`, developed F11 100% parent | **PARTIAL REPEAT** of N5’s model switch; **NEW** duration/parent/no-return. N5 mass 5.24% is not a prediction. |
| S4-04 from S4-03 @ 45,000 | S4-04 as already specified | would change the parent from F11 15,000 to a later RNG field | **NEW** and blocked until that 45,000 pair is checksum/readback verified; not the existing prepared branch |
| S4-05/S4-06 F09 40% path | Stage-3 F09 | gated exact parent | **DEFER** |
| Replay S4-01/02/03 by journal | historical Stage-4 queue | same scientific case | **REDUNDANT**; journal also human-gated |

## question-experiment scoring (next cycle, no new compute from this VM)

| Strategy | Scientific value | Interpretability | Cost | Decision |
|---:|---:|---:|---:|---|
| 1. Identity/readback + CSV window stats | 4 | 4 | 4 | **Select first** when fleet returns |
| 2. Execute existing S4-04 from hashed F11 @ 15k via PyFluent | 3 | 3 | 2 | Keep as unexecuted Stage-4-B; do not retarget parent |
| 3. New S4-04 packet from S4-03 @ 45k | 2 | 1 until identity | 1 | **Reject** until checksum/readback |
| 4. Another RNG +30k | 1 | 2 | 1 | **Reject** (REDUNDANT) |
| 5. S4-05/S4-06 | 3 | 0 until F09 parent | n/a | **Defer** |

Mode if S4-04 later runs: **hypothesis-test**. Discovery-length 500–1,000 would only repeat N5’s short-window question. The unanswered question is whether a standard-`k-epsilon` envelope **persists** beside F11’s mass behaviour over the common `+30,000`. Implement still requires the ~50-iteration smoke test. `CODEX_THREAD_ID` / `codex exec resume` will not work on this Cursor VM; the overseer wakes the agent. A zero Python exit code is not COMPLETE.

Bold-probe lane: **not applicable**. Usable Fluent servers from this checkout = 0. Do not populate a bold lane with an unresearched model switch.

## Fleet preflight (2026-08-30, this checkout)

```text
FLEET: unavailable. check_connection.py --server-id 2 → Endpoint UNKNOWN, gRPC FAILED (no ansys, no FLUENT_IP2/PORT2).
ARTIFACTS: last-known Server-2 tree Reported; this checkout has Stage-4 PNGs only.
PLACEMENT: BLOCKED
PATH MAP: Project/.../stage-04/run-paths.yaml
TRANSFERS: none possible from this VM
DURABILITY: LOCAL_ONLY debt on last-known remote H5/CSV package
BLOCKERS: credentials/VPN/.env/server-profile; no PyFluent runtime; journal gate for any replay of the historical queue
```

Fluent status: **no live job**. No gitignored `PyAnsys/output/` manifest is present.

## check-phase-closure

1. **Outcome:** `CONTINUE`
2. **Phase-level statement currently supported:** No qualified 03A reference/parent exists. The executed unchanged RNG continuations are diagnostically not parent-eligible. Remote parent/endpoint files are Reported to exist and must not be described as absent.
3. **Important unresolved hypothesis:** Hypothesis B (standard `k-epsilon` from F11 @ 15,000) is untested. Hypothesis C (F09 loading path) is gated, not falsified. Inventory-family reconciliation (317.752 kg vs 4,457.055 kg) remains open and does not change the PNG-based reject.
4. **Why another cycle is worth doing:** recovering CSV window stats and live identity is the remaining Stage-4 contract and is cheap relative to a new `+30,000` solve. S4-04 remains the designed model-form discriminator once identity of F11 @ 15,000 is live-confirmed. Further RNG continuation is not justified.
5. **Stagnation status:** not triggered. This cycle changed the picture from “pending visual/history review” to “PNG review rejects executed RNG parents; CSV/identity still Missing Info; S4-04 still unexecuted.”
6. **Important limits / human decision boundary:** this VM cannot reach Fluent. Do not start a journaled S4-04 without explicit approval. Do not invent V&V targets. Return to the human / phase-planner if S4-04 would be treated as a new canonical turbulence authority rather than a diagnostic sensitivity, or if compute outside the existing Stage-4 matrix is proposed.

## next-action

Current evidence-backed answer: more RNG iteration from F05/F06/F11 did not produce a parent-eligible 03A field.

Remaining weakness: identity/readback and contracted window statistics are still Missing Info; Hypothesis B is untested.

Recommended inside-phase direction: **investigate further**, but the next step is analysis of existing Server-2 artifacts when the fleet is reachable, not a new RNG run and not a retargeted S4-04 parent.

## Skill-completion table

| Skill | Done / skipped | Evidence path |
|---|---|---|
| scientific-phase-loop | done (this cycle) | this file; [Project/index.md](../../../../index.md) |
| invocation.md / AGENTS.md | done | `.agents/invocation.md`; root and PyAnsys `AGENTS.md` |
| check-phase-closure | done | section above; outcome CONTINUE |
| residual-history-analysis | done, CSV-limited | PNG F1/F2; endpoint table; S4-02 transcript residuals in [source execution report](source-native-queue-execution-2026-08-23.md); no native-iteration CSV stitch |
| statistical-analysis | skipped for computed windows | Missing Info: portable CSVs absent. No invented mean/median/P95/slope |
| cfd-numerical-analysis | done | core figure completeness table; visual window review |
| fluent-report-histories | partial | PNG report face present; `.out`/CSV recovery blocked |
| interpret-experiment | done | Observations / Findings |
| next-action | done | section above |
| fluent-fleet-orchestration | done, BLOCKED | [run-paths.yaml](run-paths.yaml); `check_connection.py --server-id 2` |
| pyansys-workflow | done for preflight | same connection probe; no `.venv`, no `ansys` |
| question-experiment | done | scoring table; no REDUNDANT candidate selected |
| design-experiment | done | selected strategy is analysis-first, then existing S4-04; no new campaign |
| create-setup | done without a parallel experiment | existing Stage-4 `setup.md` + new `run-paths.yaml` + this `results.md` |
| implement-experiment | skipped | placement BLOCKED; no smoke, no solve |
| fluent-case-build-and-run | skipped | no live parent staging |
| supervise-fluent-run | skipped | no hypothesis job |
| bold-probe-research | skipped | zero usable servers; mandatory lane not in force |
| arena | skipped | no competing new strategies after interrogation |
| explore-experiment-space | skipped | not discovery mode |
| interrogate | done | independent reviews of interpretation and numerics; inventory-family freeze and “no qualified parent” wording adopted |
| reflect | done | see below |
| fluent-live-inspection | skipped | no live session |
| fluent-manual-researcher | skipped | no unresolved live-tree setting |
| dpm-analysis | skipped | DPM not in this experiment |
| ewf-analysis | skipped | EWF not in this experiment |
| swarm | skipped | not needed for PNG review |
| cfd-wiki | done, read-only | RNG vs standard `k-epsilon` / RSM contrast; Purnanto baseline remains RNG; S4-04 is diagnostic sensitivity, not authority promotion |
| phase-planner | skipped | human-only |
| post-simulation-analysis / research-project-wiki / setup-report | skipped | retired |

Overseer follow-up `29585c0c-aa7d-43ee-aa1e-485f4e00a774` folded in: PR #7 read and not competed with; `run-paths.yaml` created as BLOCKED; journal path left human-gated; Q01 404 ignored; no live job to monitor.

## reflect

- Goal advanced: Stage-4 PNG/identity review the records already named as the gate.
- Established: executed RNG continuations are not parent-eligible; inventory family for PNG comparison is the 2026-08-20 ~318 kg family.
- Assumed without live evidence: last-known Server-2 paths still exist; CSV package still exists there.
- No new experiment folder; S4-04 was not retargeted onto 45,000.
- Simplest next step: fleet access, then CSV/identity, not another RNG `+30k`.

## Source

[Migrated Stage-4 execution authority](source-native-queue-execution-2026-08-23.md)

The linked execution report is the superseding status source for the retained Stage-4 setup plan; its recovered S4-03 `45,000` endpoint supersedes the earlier `42,547` execution snapshot in that setup-plan file.
