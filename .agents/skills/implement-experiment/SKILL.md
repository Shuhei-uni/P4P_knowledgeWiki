---
name: implement-experiment
description: "Execute an approved setup faithfully in Fluent: build the specified case, prove the setup by readback and save/reopen, smoke-test it, then hand the fixed target to a Python-supervised Fluent run and verify completion. Use after create-setup has defined the experiment."
---

# Implement Experiment

Get the approved setup done as written.

The scientific decisions have already been made. This skill owns faithful execution, not experiment design.

## Preserve the setup

Treat `setup.md` as the experiment contract. Build the requested delta from the verified parent/reference case and preserve everything that the setup says must remain unchanged.

Have essentially no scientific freedom here. Do not add models, change numerics, alter run length, redefine monitors, or otherwise improve the experiment because another choice seems better.

Implementation details may need to change when Fluent, PyFluent, repository tooling, or pipeline versions differ from what the setup expected. In that case, find an implementation that is scientifically equivalent and preserves the intended case state. If the setup cannot be implemented faithfully, stop the implementation and return that conflict rather than silently changing the experiment.

Use existing `fluent-case-build-and-run` guidance and reusable PyAnsys tooling for the low-level mechanics.

## Prove the case before the long run

Do not spend hours on a case that has only been built in theory.

Before the full run, verify the important setup state by exact readback, save the case, reopen it, and verify that the saved state still matches the intended setup.

Then run a short smoke test, normally about 50 iterations for an iteration-based case. The purpose is simple: prove that the saved case and chosen Python/PyFluent execution path can actually solve and advance before committing to the expensive run.

Initialization is not universally required. Follow the setup. Do not initialize merely because this skill has an initialization step.

If the smoke test exposes an execution error or a setup/pipeline incompatibility, fix only what can be fixed without changing the experiment. Otherwise return the problem for redesign or cancellation.

## Run the intended horizon

Once the verification gate passes, execute the fixed iteration/time target defined by the setup through a Python runner supervised by an agent.

Call `supervise-fluent-run` for the long-lived execution period. The supervisor watches the runner terminal, classifies genuine execution failures, reconciles uncertain state, verifies the final saved data, and returns compact execution facts.

Python-supervised execution is the default for experiments inside `scientific-phase-loop`. Do not switch to TUI-driven iteration or a Fluent journal without explicit human approval for that run.

Do not stop early merely because residuals, balances, or monitors look poor, noisy, oscillatory, or unpromising. Those behaviours are evidence for later analysis. Unless the solver or execution path encounters an actual error that prevents continuation, let the experiment reach its planned horizon.

## Completion means the data reached the target

Do not claim completion because a command was submitted, the Python process exited, or enough wall time has passed.

For an iteration-based experiment, the strongest minimal completion evidence is that the final saved data belongs to the intended run and reports the iteration count requested by `setup.md`.

Preserve the final case/data and any required histories or checkpoints. If execution failed before the target, report the final observed iteration and the failure without pretending the experiment completed.

## Handoff

Return only execution facts: whether the setup matched on readback, whether save/reopen verification passed, whether the smoke test ran, the Python runner used, the requested horizon, the final observed progress, artifact locations, and any implementation deviations or execution failures.

Scientific interpretation belongs downstream.