# Historical parallel studies from Andy's checkout

These records recover executed research that was present in Andy's local
`Andy_Dev` checkout when the workspaces were unified on 2026-09-08. They retain
the source notes' diagnostic conclusions and corrections. The original written
records are preserved on the
[recovery branch](https://github.com/Shuhei-uni/P4P_knowledgeWiki/tree/archive/andy-local-20260908).
No calculation, remote-session inspection, or new verification was performed
for this migration; numbers below are **Observed in the preserved notes**.

- [Enthalpy and DPM replication](enthalpy-dpm-replication.md): twelve completed
  baseline/spiral calculations, historically called Andy `08b` and `08c`.
- [Closed-bottom liquid-sink diagnostics](closed-bottom-liquid-sinks.md):
  Andy `07b`–`07f`, including failed qualification and corrected source accounting.
- [Resolved brine-outlet diagnostics](resolved-brine-outlet.md): Andy
  `07g`–`07n`, including the later failed sustained low-feed balance tests.
- [Later mesh-study evidence](../phase-02-parity-reset-and-pre-v2-qualification/purnanto-08b-parity-split-inlet/mesh-convergence-checkpoint-20260803.md#later-evidence-from-andys-07a-study):
  completed seventh mesh and the unresolved 900k continuation.

## Identity and claim boundaries

Andy `08b`/`08c` identify enthalpy/DPM sweeps. The existing Phase-2 `08b`/`08c`
identify the parity split-inlet and fixed-enthalpy inlet-loading experiments.
The reused numbers do **not** establish shared case identity. Use descriptive
record names and the exact parent/mesh evidence when comparing them.

Andy `07n` uses a 620,431-cell resolved-outlet mesh and transient VOF at very
low feed. The current `03A`/Phase-06 lane uses the 231,376-cell full-geometry
F11-derived steady Mixture context. They investigate related outlet/pool
questions with different meshes, parents, formulations, horizons and boundary
conditions. Their endpoints, acceptance windows and operating pressures are
not interchangeable. These historical records do not advance the
[Phase-06 lifecycle](../phase-06-full-geometry-with-brine-pool/phase-state.yaml)
or replace [current project state](../../index.md).

Historical words such as `running`, `accepted`, `next`, and `current` in the
recovery sources refer to their recorded dates. In particular, the 2026-08-21
handoff's proposed `07m` 1% continuation was superseded by later corrections;
it is not a current execution instruction. The retired progress pages and
logs remain source history, not a second active project-status system.
