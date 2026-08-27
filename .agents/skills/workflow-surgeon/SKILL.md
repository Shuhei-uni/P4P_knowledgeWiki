---
name: workflow-surgeon
description: "Diagnose friction, repeated failure, confusion, or user frustration in the P4P agent workflow and make the smallest justified improvement to the existing skill system. Use when the human explicitly asks to improve, repair, refine, or surgically edit the workflow, or when a concrete workflow failure repeatedly frustrates the user. Preserve the existing architecture by default; investigate root cause before changing skills and prefer a small edit to an existing skill over rewriting or adding new structure."
---

# Workflow Surgeon

Preserve the working system.

Diagnose the friction, find the smallest responsible seam, and change only what is necessary.

This skill maintains the agent workflow. It does not redesign it from scratch.

## Trigger carefully

Use this skill when:

- the human explicitly invokes it or asks to improve, repair, refine, or surgically edit the workflow;
- the user reports a concrete workflow failure, repeated bad default, confusing handoff, or missing responsibility;
- repeated agent behaviour clearly conflicts with user intent;
- frustrated tone accompanies an identifiable workflow failure.

Do not invoke it merely because the user sounds annoyed about the science, simulation result, compute time, or another problem that is not itself a workflow defect.

## Start from the failure

Translate the complaint or frustration into a concrete workflow symptom.

Establish:

- what the user expected;
- what actually happened;
- where in the workflow it happened;
- whether it happened once or represents a repeatable weakness;
- which existing skill or boundary was supposed to own that responsibility.

Do not begin by rewriting `scientific-phase-loop` or reorganising the skill tree.

Read only the relevant skill chain, repository rules, and execution evidence needed to understand the failure.

## Diagnose before editing

Treat the workflow like a system with interfaces.

Look for failures such as:

- missing responsibility;
- wrong skill boundary;
- bad default behaviour;
- unclear handoff;
- stale or contradictory guidance;
- missing trigger;
- overlapping skills;
- responsibility assigned to the wrong layer;
- missing human decision boundary;
- missing execution or evidence safeguard.

Distinguish the root cause from the visible symptom.

## Use fresh reviewers

For meaningful workflow problems, spawn a small number of fresh subagents before changing the architecture.

Useful independent questions include:

1. What existing skill or boundary most likely caused the behaviour?
2. What is the smallest change that would prevent the failure?
3. What could the proposed change accidentally break, duplicate, or make harder to understand?

Do not prime reviewers with the preferred solution.

Synthesize their findings rather than implementing every suggestion.

Use `interrogate` when the proposed repair affects a consequential workflow boundary. Use `reflect` after the repair to check whether the system became simpler and clearer rather than merely larger.

## Prefer the smallest intervention

Use this preference order:

```text
existing wording or trigger
    ↓
existing handoff or responsibility boundary
    ↓
small supporting reference or configuration
    ↓
small nested specialist skill
    ↓
new human-invoked skill
    ↓
major architecture change only when clearly unavoidable
```

A new skill must represent a genuinely distinct, reusable responsibility.

Do not create a new skill merely because one incident occurred.

## Protect the architecture

Before editing, identify what must remain true.

Important current invariants include:

- `phase-planner` remains the human phase-level planning boundary;
- `scientific-phase-loop` remains the autonomous scientific thinker inside the agreed phase;
- specialist skills remain narrow and composable;
- simulation evidence remains the scientific anchor;
- implementation skills do not redesign experiments;
- execution supervisors do not interpret physics;
- `check-phase-closure` decides continue, conclude, or return-to-human from accumulated evidence;
- Python/PyFluent supervised by an agent remains the default autonomous-loop execution path unless the human explicitly approves another run mechanism.

Preserve these unless the user is explicitly asking to reconsider one of them and the evidence justifies doing so.

Do not clean up unrelated skills while fixing one problem. Do not rewrite working sections merely for consistency or style unless they contribute to the failure.

## Generalize without overfitting

Ask:

> What reusable workflow lesson does this incident reveal?

Encode that lesson, not the exact conversation that exposed it.

Avoid rules so specific that they only prevent one historical failure. Also avoid broad rules whose consequences extend far beyond the evidence.

If the problem is local to one server, model, experiment, or tool version, prefer a local rule or reference over a global workflow doctrine.

## Verify the surgery

After editing:

- inspect the changed skill boundaries;
- search for directly contradictory guidance;
- check that no nearby skill now owns the same responsibility;
- confirm the triggering description still matches the intended use;
- confirm the change does not silently weaken an existing human boundary;
- use `reflect` to ask whether the workflow became simpler or more complicated.

A good repair should normally leave most of the skill system untouched.

## Output

Report:

1. **Observed friction**
2. **Root cause**
3. **Surgical change**
4. **Files changed**
5. **Why this is the smallest sufficient change**
6. **What was deliberately left unchanged**

If the evidence does not justify a workflow change, say so.
