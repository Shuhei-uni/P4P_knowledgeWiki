# Phase 7.1A autoresearch prompt — v0

You are running bounded steady-state CFD experiments for the Phase 7.1A absorber-convergence problem.

## Goal

Find settings that drive liquid into the lower separator/absorber region while preserving a credible path toward steady mass continuity and very low liquid carryover through `steamoutlet`.

The objectives are **lexicographic**, not an equal-weight scalar score:

1. the experiment must run and produce valid evidence;
2. maximize downward liquid routing;
3. improve phase-2 and mixture mass closure;
4. improve continuity behaviour;
5. reduce liquid leaving through `steamoutlet`;
6. keep total liquid inventory bounded.

Use `evaluation.json` as the deterministic experiment result. Compare candidates using `selection_vector_higher_is_better` from left to right. Do not trade away a materially better primary routing result merely for prettier residuals.

## Evidence contract

Before every experiment, run `PyAnsys/scripts/autoresearch/prepare_p71a_evaluation_reports.py` against a clean experiment monitor directory. This resets stale `.out` histories and redirects the existing Phase 7 report definitions to deterministic filenames.

After the solve, run `PyAnsys/scripts/autoresearch/evaluate_p71a_experiment.py`. Provide the run manifest and residual JSON when available. The evaluator writes `evaluation.json`.

The current routing objective is an **inventory proxy** built from total, broad (`y <= 0.50 m`), adjacent, and lower (`y <= 0.10 m`) liquid inventories. Treat it as a search signal, not final physical proof. A future validated horizontal phase-2 flux monitor should replace this proxy.

## Experiment behaviour

Change one coherent idea at a time unless a setting requires a coupled package to be valid. Record the intended scientific change separately from implementation details.

A Fluent/API/setup/coding/report-file failure is a **technical failure**, not evidence that the scientific idea is bad. Repair or retry the same idea when the intended configuration was not actually tested.

Reject or deprioritize an idea only when a valid run shows that it does not improve the objective hierarchy, it produces a clearly worse/unstable physical state, or repeated valid attempts show no useful progress.

Do not call a case successful merely because integrated mass balance closes. Check where the liquid is, whether inventory remains bounded, whether continuity is improving/stable, and whether phase-2 carryover through `steamoutlet` remains small.

## Minimal loop

For each experiment:

1. Reset/repoint monitor `.out` files.
2. Apply the proposed controlled change and read it back.
3. Run the bounded steady solve.
4. Save the required case/data and residual evidence.
5. Produce `evaluation.json`.
6. Record one short experiment line: `idea | actual change | result | next decision`.
7. Keep the candidate if its lexicographic evaluation is better or if it exposes a useful new mechanism; otherwise revert to the best valid parent.

Do not autonomously move to transient/time-accurate modelling, patch/reset the field as a recovery shortcut, change absorber locality, or add direct vapor removal. Those remain outside the Phase 7.1A boundary.
