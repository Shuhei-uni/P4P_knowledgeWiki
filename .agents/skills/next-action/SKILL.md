---
name: next-action
description: "Summarize what the current evidence has answered and what remains weak, then return either the most useful unresolved uncertainty to investigate or a recommendation to conclude. Use as a small handoff back to scientific-phase-loop."
---

# Next Action

Keep this small.

Ask two things:

1. What part of the current hypothesis or phase question is now supported by the available evidence?
2. What important part is still weak, unresolved, or unsupported?

If a meaningful uncertainty remains, identify the smallest useful investigation that would strengthen the answer and hand that uncertainty back to `scientific-phase-loop` / `design-experiment`.

If the evidence already supports a sufficiently strong, bounded statement for the current question, recommend ending this line of investigation and carrying the conclusion back to the phase loop.

Do not generate another simulation merely because one just finished. Reuse existing evidence or additional analysis when that can resolve the remaining weakness.

Return only the current evidence-backed answer, the important remaining uncertainty if any, and the recommended direction: investigate further or conclude.