# Repository guide

This repository keeps four active systems separate:

```text
CFD_wiki = reusable external CFD knowledge and Fluent guidance
Project  = current project-specific scientific truth and selected experiments
PyAnsys  = implementation, execution, inspection, and evidence tools
.agents/skills = focused workflows that route work through those owners
```

Codex and Cursor both load this file and the skills under `.agents/skills/`.
Keep that directory as the single skill home. Do not duplicate skills into
`.cursor/skills/` or copy this contract into `.cursor/rules/`.

Nested `AGENTS.md` files in `CFD_wiki/` and `PyAnsys/` apply when work is in
those trees. Cursor treats them as scoped rules; Codex reads them as local
guides.

Human-only skills are invoked as `/skill-name` in Cursor and `$skill-name` in
Codex. Keep `SKILL.md` `disable-model-invocation` aligned with Codex
`agents/openai.yaml` as described in [`.agents/invocation.md`](.agents/invocation.md).

Hypothesis-test self-wake via `codex exec resume` is Codex-only. In Cursor,
keep the agent attached through the approved horizon unless a detached
`COMPLETE`/`BLOCKED` job is explicitly required; see `supervise-fluent-run`.

## Start with the current project

- Begin project work at [`Project/index.md`](Project/index.md).
- Load only the latest relevant experiment `setup.md` or `results.md`, then a
  parent record when the question requires it. Do not preload old chronology
  or whole knowledge trees.
- Create `setup.md` and `results.md` together only for a human-selected
  experiment under `Project/experiments/<campaign>/<experiment>/`.
- Update `Project/index.md` only when the current scientific state changes.
  Git history is the operational history; do not create chat/work logs or a
  second project log.

## Keep ownership clear

- Put reusable literature, CFD methods, generic Fluent guidance, citations,
  evidence labels, units, and uncertainty in `CFD_wiki/`.
- Put case implementation, execution, inspection, extraction, and generated
  evidence in `PyAnsys/`.
- Put current scientific questions, selected experiments, findings, and claim
  boundaries in `Project/`.
- Keep skills narrow and procedural. A skill routes work; it is not a second
  authority for project facts or a dump of run chronology.
- The former project source vault and written wiki were removed. Do not
  recreate them or the retired numbered setup tree; recover exact history from
  Git when needed.

## Skill invocation policy

Read [`.agents/invocation.md`](.agents/invocation.md) when deciding whether a
skill may be entered automatically.

- `phase-planner` is human-only and must never be started implicitly.
- `scientific-phase-loop` and `workflow-surgeon` are hybrid: the human may call
  them directly, and the model may enter them when their documented trigger or
  preconditions are already satisfied.
- Other active specialist skills are model-invoked by default and should be
  selected automatically when applicable.
- Retired/unrouted skills listed in `.agents/invocation.md` must not be selected
  as current workflow authorities.

Invocation policy controls who may start a workflow. The responsibility and
human-gate rules inside each skill still apply.

## Core safeguards

- Never edit any file under a `raw/` directory.
- Do not silently copy case-specific names, values, paths, or branch
  assumptions between experiments.
- Keep `Reported`, `Observed`, `Inferred`, `Assumed`, `Missing Info`, and
  related uncertainty labels required by the owning guide.
- Before changing a subsystem, read its local guide: [`CFD_wiki/AGENTS.md`](CFD_wiki/AGENTS.md)
  or [`PyAnsys/AGENTS.md`](PyAnsys/AGENTS.md). Project records follow the root
  routing and evidence rules.
- Use the smallest applicable repo skill for a repeatable workflow rather than
  creating another general-purpose guide or documentation layer.

For native Fluent runs, also read
[`PyAnsys/knowledge/fluent-settings/native_run_and_autosave.md`](PyAnsys/knowledge/fluent-settings/native_run_and_autosave.md)
and the applicable focused skill.

## Cleanup rule

The former project-written corpus, `Setups/` tree, meeting reports, fixed
`subagents/` prompts, and deprecated wrapper skills are retired. Recover their
exact history from Git when needed; do not add compatibility shells or a new
giant `legacy/` directory.