# Skill invocation policy

P4P skills use three active invocation classes plus a retired/unrouted state.

The purpose of this policy is to keep human decision boundaries explicit while still allowing the scientific loop to compose narrow specialist skills automatically.

## 1. Human-only

Human-only skills are top-level human entry points or conversational controls. They may be invoked explicitly by the human, but the model must not start them implicitly.

For a human-only skill, keep both controls aligned:

```yaml
# SKILL.md frontmatter
disable-model-invocation: true
```

```yaml
# agents/openai.yaml
policy:
  allow_implicit_invocation: false
```

Current human-only skills:

- `phase-planner` — the human phase-level catch-up and direction-setting boundary.
- `wait-what` — a human-triggered conversational reset that re-pitches an explanation when it did not land.

A human-only skill may call model-invoked or hybrid skills after the human has supplied the necessary decision or boundary. It should not be entered merely because an agent thinks it would be useful.

## 2. Hybrid

Hybrid skills may be invoked explicitly by the human or implicitly by another skill/model when their stated preconditions are satisfied.

Do not set `disable-model-invocation: true` or `allow_implicit_invocation: false` on a hybrid skill.

Current hybrid skills:

- `scientific-phase-loop` — may be started directly by the human when a phase goal/boundaries are already supplied, or handed off from `phase-planner` after agreement.
- `workflow-surgeon` — may be invoked explicitly by the human, or implicitly when a concrete repeated workflow defect or clearly identifiable workflow failure satisfies its trigger conditions.

Hybrid does not remove human gates inside the workflow. A hybrid skill must still return to the human when its own boundaries require it.

## 3. Model-invoked specialists

These are narrow, composable disciplines and execution helpers. The model and calling skills should select them automatically when their applicability conditions are met. A human may still explicitly invoke one for a focused task, but they are not primary human workflow boundaries.

Current model-invoked specialists:

- `arena`
- `cfd-numerical-analysis`
- `cfd-wiki`
- `check-phase-closure`
- `create-setup`
- `design-experiment`
- `dpm-analysis`
- `ewf-analysis`
- `explore-experiment-space`
- `fluent-case-build-and-run`
- `fluent-fleet-orchestration`
- `fluent-live-inspection`
- `fluent-manual-researcher`
- `fluent-report-histories`
- `implement-experiment`
- `interpret-experiment`
- `interrogate`
- `next-action`
- `pool-patch-volume`
- `pyansys-workflow`
- `question-experiment`
- `reflect`
- `residual-history-analysis`
- `show-me-your-work`
- `statistical-analysis`
- `supervise-fluent-run`
- `swarm`

Use the smallest applicable specialist. Supporting skills should hand control back to the calling workflow rather than silently taking over the scientific direction.

For Fluent configuration uncertainty, use `fluent-live-inspection` first when the active live tree can resolve the path, object, state, or allowed value directly. Escalate automatically to `fluent-manual-researcher` when the live tree alone cannot safely determine the setting's meaning, prerequisites, activation order, or verifiable PyFluent/TUI implementation path. Do not guess a Fluent configuration from memory or copy a recipe from another model/version merely to keep implementation moving.

## 4. Retired / unrouted

These skill directories remain in the repository for now but belong to superseded architecture and must not be selected as active workflow authorities:

- `post-simulation-analysis`
- `research-project-wiki`
- `setup-report`

The current root `AGENTS.md` routing to `Project/`, `CFD_wiki/`, and `PyAnsys/` takes precedence. Remove or migrate these retired skills in a dedicated cleanup rather than reviving their old `Setups/` or `ResearchProject_wiki/` structures.

## Selection rule

When a task arrives:

1. Respect explicit human invocation first.
2. Never enter a human-only skill implicitly.
3. A hybrid skill may be entered implicitly only when its documented preconditions are already satisfied.
4. Otherwise select the smallest relevant model-invoked specialist and return its result to the calling workflow.
5. Do not select retired/unrouted skills.

The policy controls **who may start a workflow**, not who owns every decision inside it. Scientific, implementation, execution, analysis, and human-gate responsibilities remain defined by each skill and the repository guides.
