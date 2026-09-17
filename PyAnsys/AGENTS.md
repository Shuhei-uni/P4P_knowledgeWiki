# PyAnsys contract

`PyAnsys/` owns executable Fluent/PyFluent implementation and machine evidence.
Project scientific conclusions live in `../Project/`; reusable CFD method and
literature live in `../CFD_wiki/`.

Start from the selected experiment, then use `pyansys-workflow` and load only
the branch reference needed for the task.

## Fluent interaction

Treat Fluent as a dependency-ordered state machine.

- inspect live Settings/API state before guessing paths;
- reacquire objects after upstream model/topology changes;
- read back critical state after mutation;
- save/reopen and re-audit important child cases;
- keep outputs on explicit paths with provenance.

If the live tree cannot resolve a required setting, use the version-matched
official manual. A verified TUI/journal fallback is allowed when Settings/API is
unavailable or insufficient; it does not require a separate human approval
round-trip. Prove the final state by readback and save/reopen wherever possible.

## Recovery

Implementation failures are recoverable. A bad path/order/script means the
scientific experiment is untested, not disproven. Repair the smallest cause,
recreate/restart recoverable child/session state when phase authority allows,
and continue.

Preserve valuable endpoints before replacement. Never terminate an unrelated or
unpreserved Fluent process.

## Code

Prefer existing proven scripts/helpers over near-duplicate automation. Keep
machine evidence compact and deterministic. Do not move project interpretation
or literature narrative into this tree.
