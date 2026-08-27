---
name: next-action
description: "Make a small inside-the-phase decision after new evidence arrives: summarize what the current hypothesis has answered, identify the most important remaining weakness, and return either the smallest useful investigation or a recommendation to conclude that line of inquiry. Use inside scientific-phase-loop, not for choosing the project's next phase."
---

# Next Action

Keep this small and keep it inside the current phase.

Ask two things:

1. What part of the current hypothesis or phase question is now supported by the available evidence?
2. What important part is still weak, unresolved, or unsupported?

If a meaningful uncertainty remains, identify the smallest useful investigation that would strengthen the answer and hand that uncertainty back to `scientific-phase-loop` / `design-experiment`.

If the evidence already supports a sufficiently strong, bounded statement for the current question, recommend ending this line of investigation and carrying the conclusion back to the phase loop.

Do not generate another simulation merely because one just finished. Reuse existing evidence or additional analysis when that can resolve the remaining weakness.

Do not choose or redefine the next project phase. That belongs to the human-invoked `phase-planner` when the loop reaches a phase boundary.

Return only the current evidence-backed answer, the important remaining uncertainty if any, and the recommended inside-phase direction: investigate further or conclude.