---
name: scientific-goal-loop
description: "Orchestrate an autonomous scientific research loop from a human goal through evidence review, experiment design, implementation, analysis, interpretation, next-action selection, and stopping. Use when the task is to keep progressing toward a research objective rather than execute one predefined simulation."
---

# Scientific Goal Loop

Own the research loop, not the low-level work.

## Core loop

```text
goal
-> review current project evidence
-> decide what is unresolved
-> design candidate experiments
-> critique/select an experiment
-> create or approve setup.md
-> implement experiment
-> analyse the evidence required by the setup
-> interpret only supported claims
-> choose next action
-> loop, escalate, or stop
```

The repository is the durable memory. Do not depend on one long-lived agent context.

## Start from the goal

Recover:

- the human research goal;
- current project scope and model assumptions;
- relevant prior `setup.md` and `results.md` records;
- unresolved questions, contradictions, and limitations;
- available compute and operational constraints.

State the current question in one sentence. If the goal is too broad to choose a meaningful next experiment, decompose it into the smallest answerable scientific question.

## Delegate discovery

Use subagents for broad read-only review when the evidence spans many experiments or sources. Give each subagent a narrow question and require a concise evidence summary with paths. Keep synthesis and final decisions in the main agent.

Good delegation targets include:

- prior experiments and their conclusions;
- numerical limitations;
- relevant CFD literature/guidance;
- conflicting interpretations;
- missing evidence.

Do not create permanent orchestration files merely to coordinate subagents.

## Design before execution

Invoke `design-experiment` when new evidence is needed. For consequential choices, use `arena` or `interrogate` before accepting the experiment plan.

A candidate experiment must identify:

- one primary question;
- hypothesis or competing explanations where appropriate;
- controlled change(s);
- what remains fixed;
- required evidence and analyses;
- expected decision value;
- approximate cost/risk.

Prefer experiments that distinguish between competing explanations. Do not run a simulation just because it is easy to run.

## Human selection gate

When the human has asked to approve the first setup or select among alternatives, stop at that gate. Present a small set of well-differentiated experiments and wait.

In autonomous/goal mode, continue without approval only when the existing goal and constraints clearly authorize it. Escalate when a choice would materially alter project direction, physics assumptions, validation claims, or compute budget.

## Implement the chosen experiment

Create or confirm `setup.md`, then invoke `implement-experiment`.

Do not let the orchestration skill improvise Fluent commands. The implementation workflow owns case creation, verification, initialization, run launch, checkpoint/recovery, and completion evidence.

If implementation fails, do not automatically redesign the physics experiment. Send the failure through `next-action` first; the correct action may be repair, rerun, capability research, or human review.

## Analyse against the experiment objective

Invoke `plan-analysis` using the experiment question before choosing plots or metrics.

Then use specialist skills as needed:

- `cfd-numerical-analysis` for solver/numerical trustworthiness;
- `numerical-data-analysis` for histories, signals, comparisons, and derived numerical evidence;
- `statistical-analysis` only when statistical reasoning is scientifically appropriate;
- existing deterministic PyAnsys extraction/plotting tools for mechanics.

Do not reverse the workflow into `available script -> plot -> explanation`.

## Interpret with evidence gates

Invoke `interpret-experiment` only after the required evidence is available or the evidence gap itself has been established.

For consequential results, use `interrogate` to challenge:

- unsupported causal claims;
- confounding variables;
- numerical inadequacy;
- alternative explanations;
- whether the plots actually support the written conclusion.

Write/update `results.md` with measured evidence before interpretation.

## Choose the next action

Invoke `next-action`. Valid outcomes include:

- `NEXT_EXPERIMENT`;
- `CONTINUE_RUN`;
- `RERUN_FROM_CHECKPOINT`;
- `REPAIR_SETUP`;
- `COLLECT_MISSING_EVIDENCE`;
- `NUMERICAL_SENSITIVITY`;
- `MODEL_OR_HYPOTHESIS_REVIEW`;
- `HUMAN_REVIEW_REQUIRED`;
- `GOAL_REACHED_STOP`;
- `BRANCH_NOT_WORTH_CONTINUING`.

Do not force every loop iteration to create a new case.

## Stop conditions

Stop and report when:

- the goal is answered to the level justified by the evidence;
- a predeclared stopping criterion is reached;
- further experiments have low expected information value relative to cost;
- progress requires a major new modelling assumption or irreversible direction change;
- the evidence is contradictory enough that human judgement is required;
- infrastructure failure prevents safe unattended continuation.

## Durable handoff

At every loop boundary, ensure another fresh agent can continue by reading the repository rather than the chat history. The minimum durable state is:

- the active goal/question;
- the chosen experiment in `setup.md`;
- the evidence and bounded interpretation in `results.md`;
- explicit unresolved questions/limitations;
- the selected next action or human gate.

Use `show-me-your-work` when a long unattended sequence needs a concise reconstruction of decisions and evidence.