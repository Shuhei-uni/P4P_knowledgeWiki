---
name: next-action
description: "Evaluate a declared CONTEXT.md decision gate after new evidence arrives and return its allowed next action or HUMAN_REQUIRED. Use inside Phase Loop or Auto Loop, not for choosing the project's next phase."
---

# Next Action

Keep this small and keep it inside the current phase.

Ask two things:

1. What part of the current hypothesis or phase question is now supported by the available evidence?
2. What important part is still weak, unresolved, or unsupported?

If a meaningful uncertainty remains, evaluate the declared context decision
gate. Return only its named allowed next action. For Auto Loop, a newly
generated action is valid only when it is recorded with gate linkage and stays
inside the active envelope/timebox. If the evidence calls for an unlisted
Phase Loop investigation or an Auto Loop boundary change, return
`HUMAN_REQUIRED` to `phase-planner` / `phase-grill`.

If the evidence already supports a sufficiently strong, bounded statement for the current question, recommend ending this line of investigation and carrying the conclusion back to the phase loop.

Do not generate another simulation merely because one just finished. Reuse existing evidence or additional analysis when that can resolve the remaining weakness.

Do not choose or redefine the next project phase. That belongs to the human-invoked `phase-planner` when the loop reaches a phase boundary.

Return only the current evidence-backed answer, the important remaining
uncertainty if any, the exact declared gate evaluated, and its allowed action
or `HUMAN_REQUIRED`.
