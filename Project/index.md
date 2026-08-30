# Project

This is the default entry point for the project's current scientific truth.
`Project/` owns the question being pursued, stable model assumptions, selected
experiments, evidence interpretation, and claim limits. Reusable CFD knowledge
belongs in `CFD_wiki/`; executable implementation and machine evidence belong
in `PyAnsys/`.

## What are we trying to answer now?

Can a controlled, sufficiently iterated reference case for the vertical BOC
separator be established before comparing more realistic two-phase inlet
regimes or making report-facing performance claims?

The immediate technical question is whether the extraction-first 08b-parity
full-geometry branch can separate setup-fidelity uncertainty from the intended
inlet change while producing interpretable residual, phase-flux, pressure, and
liquid-carryover evidence.

## Active/latest experiment

The current execution lane is the canonical full-geometry Mixture `03A`
Stage-4 promising-state development campaign. Its Project tracer is the
shortest route through the selected record:

- [03A tracer index](experiments/phase-05-full-geometry-v2/full-geometry-03a-mixture-08b-parity-baseline/index.md)
- [Stage-4 setup contract](experiments/phase-05-full-geometry-v2/full-geometry-03a-mixture-08b-parity-baseline/stage-04/setup.md)
- [Stage-4 execution evidence](experiments/phase-05-full-geometry-v2/full-geometry-03a-mixture-08b-parity-baseline/stage-04/results.md)
- [Stage-3 results](experiments/phase-05-full-geometry-v2/full-geometry-03a-mixture-08b-parity-baseline/stage-03/results.md)

The earlier Project experiment records preserve the migrated setup and result
memory for the Purnanto, full-geometry, DPM, EWF, VOF, and reconstruction
families. Their historical status is part of the evidence; they are not
silently upgraded to current conclusions.

## What did the latest experiment show?

No qualified 03A parent currently exists. Remote named S4-01 and S4-03
case/data pairs, and the Stage-3 F05/F06/F11 parents, are Reported to exist on
the last-known Server-2 tree; they are not missing files. None of those states
has cleared the identity + prescribed-window gate.

A 2026-08-30 PNG review of the committed Stage-4 figures is enough to
**reject** the executed RNG continuations as parent-eligible (Observed). After
the early drop, relative mass imbalance occupies a persistent roughly 5–11%
oscillation on S4-01, S4-02, and S4-03. Continuity remains `O(10^{-1})` on
S4-01/S4-02 and `O(1)` on S4-03. `k`/`epsilon` stay intermittent; PR #7's
bounded-versus-deteriorating distinction is retained, so ugly turbulence
residuals are not by themselves the parent reject. Visual liquid-inventory
plateaus in the 2026-08-20 volume-integral family (~318 kg at F05 3,000,
~345 kg at F11 15,000, late S4-01/S4-03 near ~465 kg) are not
\(dM_l/dN \to 0\). The 2026-08-21 checkpoint kg column (~4,457 kg at F05) is
an unreconciliation family and is not used against these PNGs.

S4-02 remains endpoint-incomplete and not parent-eligible. S4-04 remains
prepared-only from hashed F11 @ 15,000. S4-05/S4-06 remain gated. Contracted
0–5k / 5–10k / 10–20k / 20–30k mean/median/P95/slope are Missing Info because
the portable CSV/JSON package is not in this checkout. Live checksum/readback
is Missing Info: this environment has no Fluent `.env`, no server-profile
YAML, and no reachable `FLUENT_IP2`.

## What remains unresolved?

- live identity of the remote S4-01/S4-03 endpoints and the hashed F11
  15,000 parent;
- prescribed-window CSV statistics for the executed branches;
- whether standard `k-epsilon` from F11 @ 15,000 (existing S4-04) can change
  the residual/mass envelope without claiming a new turbulence authority;
- whether the gated F09 40% loading path (S4-05/S4-06) still matters;
- whether the rebuilt case is truly at parity with the audited Purnanto carrier
  settings apart from its declared project change;
- which external, analytical, or measured targets are appropriate for a
  validation claim (`Project/vnv.md` remains Missing Info for pressure drop,
  carryover, brine flow, and efficiency);
- whether later DPM evidence is complete enough to support more than a bounded
  carryover diagnostic.

## What happens next?

When a Fluent endpoint is reachable, recover the Server-2 CSV/JSON package and
live-hash the named endpoints before any new solve. Do not add another
unchanged RNG `+30,000`. Keep S4-04 as the unexecuted Stage-4-B item, parent
F11 @ 15,000, PyFluent unless a journal is explicitly approved. Keep
S4-05/S4-06 gated. Do not create a parallel experiment that retargets S4-04
onto S4-03 @ 45,000. The Stage-4 packet is `setup.md` + `run-paths.yaml` +
`results.md`.

## Project map

- [experiment phase structure](experiments/README.md)
- [scope](scope.md)
- [stable model assumptions](model.md)
- [V&V and claim limits](vnv.md)
- [selected-experiment contract](experiments/README.md)
- [cross-experiment observations](observations/index.md)
- [technical project records](technical)

## Supporting source input

The original project source inputs and retired written project wiki were
removed from the current checkout at the user's request. Their exact history
is recoverable from Git; they are not active authorities.
