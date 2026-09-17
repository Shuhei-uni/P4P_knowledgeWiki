# Skill invocation policy

Keep the skill surface small. A new skill is justified by a distinct invocation
boundary, not by a new sub-step.

## Human-only

These exist because the human must deliberately enter them:

- `phase-planner` — frame or reframe the scientific phase;
- `wait-what` — request a clearer re-pitch;
- `direct-fluent-use` — direct local Fluent start/close control.

Use `disable-model-invocation: true` and
`policy.allow_implicit_invocation: false` for these.

## Hybrid

These may be invoked explicitly or reached naturally from active work:

- `phase-loop` — owns the complete scientific experiment loop;
- `workflow-surgeon` — repairs the agent workflow when a real defect appears.

## Model-invoked workflows

- `pyansys-workflow`
- `cfd-numerical-analysis`
- `cfd-wiki`
- `report-writing`
- `writing-for-agents`

These descriptions should name the trigger clearly and stay short.

## Structure rule

Do not create separate skills for inspection, setup compilation, run
supervision, residual analysis, DPM/EWF analysis, experiment review, phase gates,
or similar branches. Put that material under the owning workflow's
`references/` directory and disclose it only when that branch is reached.

Historical records may still mention retired names such as `auto-loop`,
`phase-grill`, `verify-phase-transition`, or
`fluent-manual-researcher`. Treat those as provenance, not active invocation
targets.

## Human gates

Human input is not a routine execution gate. Active workflows recover ordinary
technical and scientific blockers autonomously inside the recorded phase scope.
Return to the human only for a scope/goal change, an unauthorized irreversible
external action, or an actually human-owned judgement.
