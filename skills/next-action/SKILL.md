---
name: next-action
description: "Choose the scientifically appropriate next action after an experiment or implementation attempt: continue, rerun, repair, gather evidence, run a numerical sensitivity, design a new experiment, escalate to a human, or stop. Use to prevent an autonomous loop from blindly generating more simulations."
---

# Next Action

Choose the next action that maximizes progress toward the project goal, not the number of simulations run.

## Inputs

Use:

- current project goal/question;
- `setup.md` intent;
- implementation status;
- analysis completeness;
- CFD numerical status;
- bounded interpretation;
- unresolved explanations;
- compute/risk constraints.

## Decision classes

Choose one primary action:

### `NEXT_EXPERIMENT`
Use when the previous evidence is adequate, the goal remains unresolved, and a new controlled experiment can discriminate the remaining explanations.

### `CONTINUE_RUN`
Use when the current setup is still scientifically valid but has not reached a sufficient iteration/physical-time/statistical window.

### `RERUN_FROM_CHECKPOINT`
Use when infrastructure/run interruption occurred and the setup remains valid.

### `REPAIR_SETUP`
Use when implementation does not match `setup.md`, required monitors are missing, or a recoverable setup mistake invalidates the run.

### `COLLECT_MISSING_EVIDENCE`
Use when existing artifacts can answer the question with additional read-only extraction/analysis.

### `NUMERICAL_SENSITIVITY`
Use when timestep, mesh, iteration count, initialization, scheme, or solver sensitivity blocks physical interpretation.

### `MODEL_OR_HYPOTHESIS_REVIEW`
Use when evidence contradicts a core assumption or multiple experiments repeatedly fail to distinguish the same explanations.

### `HUMAN_REVIEW_REQUIRED`
Use for major project-direction choices, large compute commitments, ambiguous contradictory evidence, unsafe automation state, or explicitly reserved human gates.

### `GOAL_REACHED_STOP`
Use when the project question is answered to the level justified by the evidence/stopping criteria.

### `BRANCH_NOT_WORTH_CONTINUING`
Use when additional work has low information value relative to cost or the branch has been invalidated.

## Decision order

Ask in this order:

1. Did implementation actually match the intended experiment?
2. Is the required evidence available?
3. Is the simulation numerically adequate for the desired claim?
4. Does the evidence answer the question?
5. If not, what uncertainty remains?
6. What is the smallest action that resolves that uncertainty?
7. Is that action worth its cost/risk?
8. Does it require human approval?

Do not choose `NEXT_EXPERIMENT` before passing the earlier gates.

## Information value

Prefer actions that:

- separate competing explanations;
- reuse a valid existing run before spending on a new one;
- fix a blocking numerical issue before adding physics complexity;
- collect missing evidence rather than rerun unnecessarily;
- stop when further precision would not change the project decision.

## Challenge the decision

For expensive or consequential next actions, use `interrogate` or a fresh subagent to ask:

- Are we solving the real blocker?
- Is there a cheaper discriminating test?
- Are we mistaking numerical inadequacy for a physics question?
- Would the proposed experiment actually change the conclusion?

## Output

Return:

- selected action;
- one-sentence reason;
- evidence/state that triggered it;
- exact next task;
- human gate if required;
- stopping condition for that next task.

The scientific loop uses this output to continue, escalate, or stop.