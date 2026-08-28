---
name: implement-experiment
description: "Execute an approved setup faithfully in Fluent: stage the exact resolved parent, build the specified case, prove the setup by readback and save/reopen, smoke-test it, then hand the fixed target to a Python-supervised Fluent run and verify completion. Use after create-setup and fluent-fleet-orchestration have defined the experiment and execution placement."
---

# Implement Experiment

Get the approved setup done as written on the server assigned by the execution plan.

The scientific decisions have already been made. This skill owns faithful execution, not experiment design or server selection.

## Receive the execution plan

Before mutating Fluent, require the placement contract produced by `fluent-fleet-orchestration`.

Know at minimum:

- setup ID and run ID;
- selected server;
- exact parent artifact ID;
- verified parent case/data source;
- whether OneDrive staging is required;
- exact remote parent and run/output paths;
- any available expected hashes/provenance for the parent;
- final-artifact durability intent and any selected important checkpoint policy.

Do not choose another server or substitute a similarly named local parent merely because it is convenient. If the assigned parent cannot be staged or verified, return the placement failure for re-planning.

## Preserve the setup

Treat `setup.md` as the experiment contract. Build the requested delta from the verified parent/reference artifact and preserve everything that the setup says must remain unchanged.

Have essentially no scientific freedom here. Do not add models, change numerics, alter run length, redefine monitors, or otherwise improve the experiment because another choice seems better.

Implementation details may need to change when Fluent, PyFluent, repository tooling, or pipeline versions differ from what the setup expected. In that case, find an implementation that is scientifically equivalent and preserves the intended case state. If the setup cannot be implemented faithfully, stop the implementation and return that conflict rather than silently changing the experiment.

Use existing `fluent-case-build-and-run` guidance and reusable PyAnsys tooling for the low-level mechanics.

## Stage and prove the parent

When the exact parent is not already local, stage the complete required case/data pair through the transfer path defined in the execution plan, normally via the verified OneDrive artifact layer.

Before deriving the child, prove that the staged files correspond to the intended parent. Prefer manifest/hash verification when available; otherwise use the strongest available provenance and direct readback evidence. Do not treat matching filenames alone as sufficient proof for an important transferred artifact.

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

## Preserve important artifacts beyond the server

Server-local storage is the working copy, not the only durable scientific copy.

For a scientifically important final state, final parent likely to be branched from again, or deliberately selected expensive recovery checkpoint, preserve a complete paired case+data artifact and promote it to the approved OneDrive location when practical.

Do not upload every autosave. Promote only final states and checkpoints whose loss would materially cost future work.

For an important promoted artifact, preserve the artifact ID, source setup/run, iteration or progress, filenames, origin server, and hashes when feasible. Verify the copied pair before describing it as durable. If the OneDrive step cannot be completed, keep the local pair intact and return a `LOCAL_ONLY` durability status rather than silently treating the run as safely archived.

## Completion means the data reached the target

Do not claim completion because a command was submitted, the Python process exited, or enough wall time has passed.

For an iteration-based experiment, the strongest minimal completion evidence is that the final saved data belongs to the intended run and reports the iteration count requested by `setup.md`.

Preserve the final case/data and any required histories or checkpoints. If execution failed before the target, report the final observed iteration and the failure without pretending the experiment completed.

A successfully solved run and a durably replicated run are related but separate facts. Report both execution completion and durability status.

## Handoff

Return only execution facts: whether the parent was staged and verified, whether the setup matched on readback, whether save/reopen verification passed, whether the smoke test ran, the selected server, Python runner, requested horizon, final observed progress, local artifact locations, verified OneDrive artifact locations when available, durability status, and any implementation deviations or execution failures.

Scientific interpretation belongs downstream.