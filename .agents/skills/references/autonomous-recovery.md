# Autonomous recovery

An active Phase Loop or Auto Loop does not return control to the human for a
scientific, evidence, configuration, or execution blocker. A `BLOCK` is an
autonomous work queue: diagnose it, choose the leanest defensible recovery,
record the decision, and continue.

## Recover in this order

1. **Inspect first** — read the exact setup, `CONTEXT.md`, `phase-state.yaml`,
   run manifest, and closest valid parent/result. Do not infer a case state
   from filenames or a failed command.
2. **Research when uncertain** — use `cfd-wiki` for reusable method/evidence,
   `fluent-live-inspection` for live state, then `fluent-manual-researcher` for
   version-matched official Fluent guidance. Use focused web/official research
   only when those sources cannot resolve the uncertainty.
3. **Choose a lean recovery** — prefer, in order:
   - a direct configuration/path/instrumentation repair;
   - a verified equivalent implementation or parent recovery;
   - a small diagnostic or sensitivity family that preserves the phase
     question; or
   - a conservative, explicitly labelled `Assumed` surrogate bracketed by
     sensitivity cases when a project fact is missing.
4. **Prove and record** — write the rationale, evidence, assumption/deviation,
   controlled delta, and recovery gate into `CONTEXT.md`, `setup.md`,
   `run-paths.yaml`, and `results.md` as applicable. Read back/save-reopen/
   smoke-test before compute, then keep claim limits aligned with what was
   actually tested.

Never silently invent a fact or edit a verified durable parent. When an exact
solution is unavailable, test the smallest bounded surrogate or alternative
that can still reduce the uncertainty and label the resulting claim limit.

## Continue, do not hand off

`BLOCK` never means "ask the human what to do." It means resolve the blocker
autonomously or proceed with an independent useful lane. If a path remains
impossible after evidence-backed recovery attempts, record
`BLOCKED_AUTONOMOUS` with the failed evidence and next recovery candidate, then
continue the remaining setup family, the parallel lane, or the next bounded
question until the loop's stop time.

Do not relabel an attempted run, a partial result, or an unresolved blocker as
`PASS`. Evidence gates still require real completion; autonomy changes who
works the problem, not what counts as proof.
