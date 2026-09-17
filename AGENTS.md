# Repository contract

Route each kind of truth to one owner:

| Owner | Stores |
| --- | --- |
| `Project/` | Current project questions, decisions, selected experiments, findings, and claim limits |
| `CFD_wiki/` | Reusable literature evidence, CFD methods, and generic Fluent guidance |
| `PyAnsys/` | Fluent/PyFluent implementation, execution, inspection, extraction, and machine evidence |
| `.agents/skills/` | Focused workflows that operate on those owners |

For project-specific scientific work, start at [`Project/index.md`](Project/index.md).
For changes under `CFD_wiki/` or `PyAnsys/`, read that tree's `AGENTS.md` first.
Use the smallest matching repository skill for a repeatable workflow; the skill
owns its reading order, gates, procedure, and completion criteria.

For live Fluent discovery, generated execution, or a proposed direct-worker
exception, follow the [MCP integration contract](.agents/skills/fluent-live-inspection/mcp-integration.md).
Generic Fluent interaction is MCP-first; P4P retains scientific gates, evidence,
fleet/artifact management and supervision. Existing Python/PyFluent workflow
wording refers to that route, not permission to bypass it with an old script.

Before a consequential scientific or Fluent decision, run a **three-path
check**: reusable CFD evidence through `cfd-wiki`'s evidence-lookup branch,
generic Fluent guidance through its Fluent-guidance branch (escalating exact
version/case-state uncertainty to `fluent-manual-researcher`), and past project
evidence through `show-me-your-work`. Delegate each applicable path to a
focused subagent with the decision, one precise question, and the kind of fact
that could change or constrain it. Synthesize the compact returns; record why
any path is irrelevant rather than silently skipping it.

## Durable truth

- Keep a fact in its owning system and link to it elsewhere. A skill is a
  procedure, not another store for project facts or run history.
- Keep current human-approved phase decisions in the phase-root `CONTEXT.md`,
  runnable scientific intent in `setup.md`, resulting evidence and bounded
  interpretation in `results.md`, and active lifecycle state in
  `phase-state.yaml`.
- Update `Project/index.md` only when the current scientific state changes.
  Git history is the chronology; use `show-me-your-work` when that chronology
  must be reconstructed for review or handoff.
- Preserve the evidence and uncertainty labels required by the owning guide.
  Treat every directory named `raw/` as immutable source or generated evidence.
- Preserve every Fluent session: never close, exit, terminate, kill, restart, or relaunch Fluent, and call a script only after verifying that its success, error, timeout, and cleanup paths leave the Fluent process running.
- Carry case-specific names, values, paths, parent identity, and assumptions
  only from the selected experiment's verified records. Record uncertainty
  instead of borrowing details from another case.

## Skill maintenance

Use `writing-for-agents` when editing agent instructions. Keep repository skills
only in `.agents/skills/`; when adding, retiring, or changing a skill's
invocation class, follow [`.agents/invocation.md`](.agents/invocation.md).
