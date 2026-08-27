# 03A — 08b-Parity Steady Mixture Reports

Corresponding setup campaign: [03A setup campaign](../../../../../full-geometry/mixture/steady-liquid-outlet/index.md).

## Stage 2 — numerical stabilisation

- [N1 — reduced turbulence under-relaxation](03a-08b-stage2-N1-results.md)
- [N3 — first-order turbulence transport](03a-08b-stage2-N3-results.md)
- [N4 — first-order momentum and turbulence startup](03a-08b-stage2-N4-results.md)
- [N5 — standard-`k-epsilon` bootstrap and RNG return](03a-08b-stage2-N5-results.md)
- [Stage-2 screening report](03a-08b-stage2-screening-report.md)

## Stage 3 — convergence sweep

- [Fixed-3000 results](03a-stage3-fixed3000-results-20260820.md)
- [Stage-3 results — 2026-08-18](03a-stage3-results-20260818.md)
- [Stage-3 results — 2026-08-21](03a-stage3-results-20260821.md)
- [Canonical final results — iteration-led evidence report](03a-stage3-final-results.md)
- [F03/F07/F09 detailed results — native-history branch-first package](03a-stage3-f03-f07-f09-detailed-results.md)
- [F08/F10/F12 Schedule-D detailed results](03a-stage3-schedule-d-final-results.md)
- [Checkpoint table](03a-stage3-results-20260821-checkpoints.csv)
- [Native queue final results — F02/F04/F05/F06/F11](03a-stage3-native-queue-final-results.md)
- [Native queue branch-by-branch results template](03a-stage3-native-queue-results-template.md)

All figures associated with this setup are under [`plots/`](plots/).

## Stage 4 — promising-state development

- [Initial experiment brief and interrupted execution status](03a-stage4-initial-experiment-brief.md)
- [Native-queue execution and transport-recovery evidence](03a-stage4-native-queue-execution-2026-08-23.md)
- [Server 2 extracted evidence index](evidence/03a-stage4-server2/index.json)
- [Server 2 checkpoint relocation manifest](evidence/03a-stage4-server2/checkpoint-relocation-manifest.json)
- [Server 2 plot index](plots/03a-stage4/server2/index.json)
- [Canonical Stage-4 setup plan](../../../../../full-geometry/mixture/steady-liquid-outlet/03a-stage4-promising-state-development.md)

The current Server 2 reconciliation supersedes the earlier 2026-08-23 snapshot:
S4-01 has a complete `+30,000` run and named endpoint, S4-02 has complete
`+30,000` iteration coverage but no named endpoint or native residual export,
S4-03 has a complete recovery `+30,000` run and named endpoint, and S4-04 was
prepared but not submitted.  S4-05/S4-06 remain gated on exact F09-parent
access.  Portable CSV/JSON histories and plots are stored under this report;
the native H5 case/data binaries remain at the authoritative Server 2 paths
listed in the relocation manifest.
