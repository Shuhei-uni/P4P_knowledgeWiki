# Skill invocation policy

P4P skills use three active invocation classes plus a retired/unrouted state.

The purpose of this policy is to keep human decision boundaries explicit while still allowing the scientific loop to compose narrow specialist skills automatically.

## 1. Human-only

Human-only skills are top-level human entry points or conversational controls. They may be invoked explicitly by the human, but the model must not start them implicitly.

For a human-only skill, keep both controls aligned. Cursor reads only the
`SKILL.md` flag. Codex also reads `agents/openai.yaml`. Do not set one without
the other.

```yaml
# SKILL.md frontmatter (Cursor and Codex)
disable-model-invocation: true
```

```yaml
# agents/openai.yaml (Codex UI / policy; Cursor ignores this file)
policy:
  allow_implicit_invocation: false
```

Human invocation is `/skill-name` in Cursor and `$skill-name` in Codex.

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
- `bold-probe-research`
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
- `verify-phase-transition`

Use the smallest applicable specialist. Supporting skills should hand control back to the calling workflow rather than silently taking over the scientific direction.

### Mandatory scientific phase lifecycle

When `scientific-phase-loop` is active, its lifecycle is mandatory rather than advisory:

```text
PHASE_CONTRACT
→ DISCOVERY_DESIGN
→ DISCOVERY_EXECUTION / DISCOVERY_EVIDENCE
→ HYPOTHESIS_DEFINITION
→ HYPOTHESIS_RUN_READY
→ HYPOTHESIS_EXECUTION / HYPOTHESIS_EVIDENCE
→ PHASE_CLOSURE
```

Every state-changing transition must invoke `verify-phase-transition`. A `BLOCK` or `HUMAN_REQUIRED` result may not be self-overruled by the scientific loop or another specialist.

Normal autonomous `CONCLUDE PHASE` is illegal until the verified discovery-to-hypothesis lifecycle has completed. A human may explicitly terminate/reframe a phase earlier.

Discovery stays attached to the active scientific goal through terminal execution evidence. A long Codex hypothesis qualification uses the exact-thread self-waking supervisor path and resumes the same scientific loop. `phase-state.yaml` is the machine-readable lifecycle authority after interruption or wakeup.

Before `scientific-phase-loop` or `design-experiment` selects any bold/speculative probe, invoke `bold-probe-research`. The research pass must begin from the current scientific tension, check prior project collisions, examine relevant CFD knowledge and authoritative literature/manual guidance, and produce evidence-backed candidate questions before `arena` or experiment selection. A bold lane must not be populated by an unresearched Fluent option, a random model switch, or a nearby parameter variation merely because compute is available.

For Fluent configuration uncertainty, use `fluent-live-inspection` first when the active live tree can resolve the path, object, state, or allowed value directly. Escalate automatically to `fluent-manual-researcher` when the live tree alone cannot safely determine the setting's meaning, prerequisites, activation order, or verifiable PyFluent/TUI implementation path. Do not guess a Fluent configuration from memory or copy a recipe from another model/version merely to keep implementation moving.

## 4. Retired / unrouted

These skill directories remain in the repository for now but belong to superseded architecture and must not be selected as active workflow authorities:

- `post-simulation-analysis`
- `research-project-wiki`
- `setup-report`

Keep `disable-model-invocation: true` on each retired skill so Cursor does not
auto-apply it from the description. Codex should keep
`allow_implicit_invocation: false` when that skill has `agents/openai.yaml`.

The current root `AGENTS.md` routing to `Project/`, `CFD_wiki/`, and `PyAnsys/` takes precedence. Remove or migrate these retired skills in a dedicated cleanup rather than reviving their old `Setups/` or `ResearchProject_wiki/` structures.

## Selection rule

When a task arrives:

1. Respect explicit human invocation first.
2. Never enter a human-only skill implicitly.
3. A hybrid skill may be entered implicitly only when its documented preconditions are already satisfied.
4. Otherwise select the smallest relevant model-invoked specialist and return its result to the calling workflow.
5. Do not select retired/unrouted skills.
6. While `scientific-phase-loop` is active, no specialist may bypass or retroactively waive a required `verify-phase-transition` gate.

The policy controls who may start a workflow and, for the scientific phase lifecycle, which independent gate must authorize state changes. Scientific, implementation, execution, analysis, and human-gate responsibilities remain defined by each skill and the repository guides.
