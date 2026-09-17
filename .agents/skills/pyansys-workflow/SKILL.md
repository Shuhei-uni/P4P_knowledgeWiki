---
name: pyansys-workflow
description: Route Fluent implementation through PyFluent MCP while retaining P4P verification, fleet/artifact handling, specialised extraction and supervised execution.
---

# PyAnsys workflow

Use [MCP integration](../fluent-live-inspection/mcp-integration.md) before Fluent
work. It owns tool selection, generated-code execution, session preservation
and narrow retained-worker exceptions. Generic discovery and mutation use MCP,
not existing scripts first. `PyAnsys/` owns P4P's implementation support and
machine evidence; it is not a second Fluent API-discovery layer.

## Route the task

| Task | Workflow |
| --- | --- |
| Uncertain path, object, current value or allowed option | `fluent-live-inspection` |
| Meaning, prerequisite or version-specific implementation uncertainty | `fluent-manual-researcher` |
| Server ownership, artifact locality, transfer or output paths | `fluent-fleet-orchestration` |
| Implement an approved experiment | `implement-experiment` and `fluent-case-build-and-run` |
| Long hypothesis execution and exact-thread wakeup | `supervise-fluent-run` |
| Residual/report/DPM/EWF evidence | Matching focused extraction skill |
| Spatial Fluent figure | `create-figure` |

Read the selected setup and relevant code only. Reuse a proven domain algorithm,
not its unverified paths, phase names, values or server assumptions. New snippets
use the upstream `solver` binding and the `validate_code` → `run_code` path.
Standalone generated connection scripts and recursive probes are not the route.

## Preserve authority and identity

For active Phase Loop or Auto Loop work, read `CONTEXT.md` and `phase-state.yaml`.
Discovery needs its design permission; long qualification needs
`HYPOTHESIS_RUN_READY == PASS`. MCP availability never grants scientific authority.

Keep artifact, setup, run and `server.ref` distinct. A connection alias does not
identify a case. Fleet orchestration resolves exact parent paths and the canonical
`run-paths.yaml`; verified server profiles provide filesystem knowledge only.

An exclusive phase lease permits approved loaded-state replacement after required
recovery preservation. It does not permit process shutdown/relaunch or overwriting
durable parents. All clients/workers must share one writer for a Fluent session.

## Dependency-ordered implementation

```text
enable approved parent → reacquire → inspect live children/options
→ validate and execute one dependent change → read back → classify
```

Reacquire after model/type/phase/object changes and case/data loads. Missing paths,
readback mismatch or absent required evidence block dependent actions. Classify
order/dependency, path/version, invalid value, wrapper limitation, readback mismatch,
missing verification, or an approved-fallback requirement without guessing.

A fallback recipe is not authorization: TUI/journal use requires the shared
explicit-human-approval and verification conditions. Return a bounded blocker
rather than bypassing MCP or silently changing the experiment.

## Execution and evidence

Build and prove the child before the planned run: exact parent, approved delta,
invariants, paired save/reopen, and smoke/instrumentation at declared paths.
Initialization follows the setup, never a connection or retry convenience.

Discovery stays attached through the approved short horizon and immediate analysis.
Use the setup's screening budget; ordinary family screens remain 500 iterations
with promising extensions to 1,000 unless the recorded setup says otherwise.
Use one clear solve rather than one-iteration keep-alive loops.

Long hypothesis work uses the existing supervisor, not a raw background launch.
Preserve the ordinary 10,000-iteration qualification basis, the explicitly scoped
Auto Loop 2,000-iteration exception, or an approved equivalent non-iteration basis.
Codex requires exact-thread wakeup on `COMPLETE` and `BLOCKED`; other runtimes stay
attached. The supervisor's verifier must prove the actual horizon, final pair and
required histories. An `EXECUTED` MCP receipt or zero exit status is not completion.

Poor residuals/physics are evidence while the approved run can continue. A timeout
or partial mutation requires reconciliation, not replay or a new competing client.

## Placement and durable truth

Keep reusable support in `src/pyansys_fluent/`, MCP clients in connection/inspection
scripts, and supervision in `scripts/orchestration/`. Keep any necessary setup
worker thin and within the retained-worker exception; do not add generic plumbing.

Current experimental evidence belongs in `Project/`, reusable CFD knowledge in
`CFD_wiki/`, durable implementation lessons in `PyAnsys/knowledge/`, and directly
observed filesystem facts in server profiles. Generated `output/` is not scientific
authority. Preserve raw evidence and valuable paired artifacts via the existing
OneDrive policy; create no competing project log or path manifest.
