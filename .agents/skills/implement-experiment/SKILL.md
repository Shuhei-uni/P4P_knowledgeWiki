---
name: implement-experiment
description: "Execute an approved setup faithfully in Fluent: stage the exact resolved parent, establish explicit output paths, build the specified case, prove the setup by readback and save/reopen, smoke-test it, then execute it according to discovery or hypothesis-test mode. Use after create-setup and fluent-fleet-orchestration have defined the experiment and execution placement."
---

# Implement Experiment

Get the approved setup done as written on the server assigned by the execution plan.

The scientific decisions have already been made. This skill owns faithful execution, not experiment design or server selection.

## Receive the execution plan

Before mutating Fluent, require the placement contract produced by `fluent-fleet-orchestration`.

Know at minimum:

- setup ID and run ID;
- the selected runtime `server.ref` plus separate server ID and IP;
- exact parent artifact ID;
- verified parent case/data source;
- whether OneDrive staging is required;
- exact remote parent and run/output paths;
- the canonical sibling `run-paths.yaml` beside `setup.md` and `results.md` in the Project experiment packet;
- the explicit path map, including Fluent working directory, final case/data, autosave/checkpoint paths, file-backed report/monitor outputs such as `.out`, transcript/log paths, and artifact-manifest locations when applicable;
- any available expected hashes/provenance for the parent;
- final-artifact durability intent and any selected important checkpoint policy.

Do not choose another server or substitute a similarly named local parent merely because it is convenient. If the assigned parent cannot be staged or verified, return the placement failure for re-planning.

Do not identify a run by `server-1`, `server-2`, or another short alias alone. Use the exact runtime server reference resolved by fleet preflight, such as `server-2@192.168.1.42`.

Do not begin a solve while an important output destination is still implicit. A bare filename is not an adequate artifact path unless the intended working directory has been deliberately established and the resulting absolute destination is recorded.

## Preserve the setup

Treat `setup.md` as the experiment contract. Build the requested delta from the verified parent/reference artifact and preserve everything that the setup says must remain unchanged.

Have essentially no scientific freedom here. Do not add models, change numerics, alter run length, redefine monitors, or otherwise improve the experiment because another choice seems better.

Implementation details may need to change when Fluent, PyFluent, repository tooling, or pipeline versions differ from what the setup expected. In that case, find an implementation that is scientifically equivalent and preserves the intended case state. If the setup cannot be implemented faithfully, stop the implementation and return that conflict rather than silently changing the experiment.

Use existing `fluent-case-build-and-run` guidance and reusable PyAnsys tooling for the low-level mechanics.

## Stage and prove the parent

When the exact parent is not already local, stage the complete required case/data pair through the transfer path defined in the execution plan, normally via the verified OneDrive artifact layer.

Before deriving the child, prove that the staged files correspond to the intended parent. Prefer manifest/hash verification when available; otherwise use the strongest available provenance and direct readback evidence. Do not treat matching filenames alone as sufficient proof for an important transferred artifact.

## Establish and verify the run filesystem

Before the smoke test or long solve:

1. create the declared remote run, report, log, checkpoint, staging, and manifest directories as required;
2. verify the intended destinations are writable and will not unintentionally overwrite another run;
3. inspect the active Fluent case for file-backed reports, monitors, autosaves, exports, transcripts, or other outputs with relative or inherited filenames;
4. resolve those outputs to the canonical Project experiment `run-paths.yaml`;
5. where possible, rewrite only the file destination to an explicit run-specific path without changing the scientific monitor/report definition;
6. where Fluent requires a relative filename, deliberately set or verify the Fluent working directory and record the resulting absolute destination;
7. read back important configured destinations when possible;
8. write or update the sibling `run-paths.yaml` in the Project experiment packet before solving.

Do not make the remote run directory the durable home of the path manifest. If the runner needs a local machine-readable copy, it may receive a transient/derived copy, but the Project experiment `run-paths.yaml` remains authoritative.

Do not assume that loading a case changes Fluent's working directory or causes relative `.out` files to be written beside the case. Do not rely on the directory from which an existing Fluent session happened to be launched.

If an important file location cannot be resolved, return a path blocker before the expensive run rather than hoping to locate the file afterward.

## Prove the case before the long run

Do not spend hours on a case that has only been built in theory.

Before the full run, verify the important setup state by exact readback, save the case to its declared full path, reopen it, and verify that the saved state still matches the intended setup.

Then run a short smoke test, normally about 50 iterations for an iteration-based case. The purpose is simple: prove that the saved case and chosen Python/PyFluent execution path can actually solve and advance before committing to the expensive run.

Use the smoke test to confirm that required file-backed outputs are appearing at the declared locations. If Fluent silently writes an important `.out`, checkpoint, transcript, or other artifact somewhere else, reconcile the path configuration before the long run and update the same canonical `run-paths.yaml`.

Initialization is not universally required. Follow the setup. Do not initialize merely because this skill has an initialization step.

If the smoke test exposes an execution error or a setup/pipeline incompatibility, fix only what can be fixed without changing the experiment. Otherwise return the problem for redesign or cancellation.

## Run the intended horizon

Once the verification gate passes, execute the fixed iteration/time target defined by the setup through the approved Python/PyFluent path.

For **discovery mode**, keep the scientific agent attached for the full short run. Do not launch the detached handoff worker. Wait for the run to finish, return the execution evidence immediately, and let the active scientific thread inspect it and choose the next discovery experiment without a human restart.

For **hypothesis-test mode**, call `supervise-fluent-run` and launch the background job only through the self-waking Python entrypoint. The raw experiment runner must not be background-launched directly. The originating Codex thread/session ID must be captured before launch, and the terminal Python path must resume that exact thread on both `COMPLETE` and `BLOCKED`.

The hypothesis job must declare at least one deterministic completion proof: locally visible required files and/or a verifier command that returns zero only when the declared remote final state is verified. A zero runner exit code alone is not sufficient.

Never use `--last` for autonomous multi-server handoff because several jobs may complete out of launch order.

Python/PyFluent execution is the default for experiments inside `scientific-phase-loop`. Do not switch to TUI-driven iteration or a Fluent journal without explicit human approval for that run.

Do not stop early merely because residuals, balances, or monitors look poor, noisy, oscillatory, or unpromising. Those behaviours are evidence for later analysis. Unless the solver or execution path encounters an actual error that prevents continuation, let the experiment reach its planned horizon.

## Preserve important artifacts beyond the server

Server-local storage is the working copy, not the only durable scientific copy.

For a scientifically important final state, final parent likely to be branched from again, or deliberately selected expensive recovery checkpoint, preserve a complete paired case+data artifact and promote it to the approved OneDrive location when practical.

Do not upload every autosave. Promote only final states and checkpoints whose loss would materially cost future work.

For an important promoted artifact, preserve the artifact ID, source setup/run, iteration or progress, filenames, origin `server.ref`, and hashes when feasible. Verify the copied pair before describing it as durable. Record verified OneDrive locations and durability status in the same Project experiment `run-paths.yaml`.

If the OneDrive step cannot be completed, keep the local pair intact, record its actual local path, and return a `LOCAL_ONLY` durability status rather than silently treating the run as safely archived.

## Completion means the data reached the target and outputs are locatable

Do not claim completion because a command was submitted, the Python process exited, or enough wall time has passed.

For an iteration-based experiment, the strongest minimal completion evidence is that the final saved data belongs to the intended run and reports the iteration count requested by `setup.md`.

Also reconcile required generated outputs against the sibling `run-paths.yaml`. Required histories, `.out` files, checkpoints, transcripts, logs, manifests, and final case/data should be locatable at their declared paths or explicitly recorded as anomalies with their actual locations.

Preserve the final case/data and any required histories or checkpoints. If execution failed before the target, report the final observed iteration and the failure without pretending the experiment completed.

A successfully solved run, a successfully launched Codex handoff, and a durably replicated run are related but separate facts. Report all three independently when the handoff path applies.

## Handoff

Return only execution facts: whether the parent was staged and verified, whether the run filesystem/path map was established, the canonical Project `run-paths.yaml` location, whether the setup matched on readback, whether save/reopen verification passed, whether the smoke test ran, the runtime server reference, Python runner, requested horizon, execution mode, terminal status, final observed progress, declared and actual local artifact/output locations, verified OneDrive artifact locations when available, durability status, Codex handoff status for hypothesis runs, and any implementation deviations, path anomalies, or execution failures.

Scientific interpretation belongs downstream.
