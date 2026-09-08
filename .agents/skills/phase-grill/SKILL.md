---
name: phase-grill
description: "Inside active phase planning, elicit the human's scientific thinking, sharpen an unsettled phase or experiment direction, and maintain its Project CONTEXT.md. Use after the human asks to choose, reframe, or design work for a phase."
---

# Phase Grill

Turn human thinking into a bounded scientific direction before experiment design
or execution begins. `CONTEXT.md` is the phase's current human-approved planning
authority; `setup.md` remains the runnable scientific contract.

The human originates and selects phase and experiment ideas. This skill may
clarify, challenge, compare, and suggest traceable variants, but it never
silently upgrades an agent-originated idea into an executable candidate.

Read [the phase-context schema](references/phase-context.md) before creating or
materially restructuring a context record.

## Make questions easy to scan

In messages to the human, use a small, consistent visual vocabulary. The
icons label the *kind* of prompt so a response can be free-form without losing
the decision being made:

- 💭 **Your thinking** — an open invitation to ramble, add context, or name an
  intuition. No answer format is required.
- 🧭 **Phase direction** — the phase-level decision currently being sharpened.
- 🧪 **Experiment direction** — an experiment-level idea, comparison, or
  quick-screen question.
- 🎯 **Recommended focus** — the agent's provisional recommendation about the
  next question to settle. State why it is useful; it is never a decision or
  an approved candidate.
- ❓ **Question** — a specific, answerable prompt. Number these when there is
  more than one.
- ⚖️ **Trade-off** — a material choice with its consequences.
- 🚦 **Decision gate** — the evidence/condition that would determine a
  permitted next action.
- ✅ **Locked in** — a concise restatement of something the human has
  explicitly confirmed.
- ⚠️ **Still open** — an uncertainty, risk, or human decision that remains.
- 📌 **What I'll record** — the attributed context update that follows a
  meaningful answer.

Use one leading icon per idea, not a decorative emoji on every line. Keep the
response visually sparse: an opening prompt or recommendation, at most three
questions, and a brief statement of what an answer will unlock. Put the
recommended focus before the questions so the human can accept, reject, or
redirect it. Always leave a low-friction escape hatch such as “You can answer
in rough notes; a partial answer is useful.”

Icons guide the conversation only. Record the final decision, evidence, and
approval state in plain, durable `CONTEXT.md` fields; never mistake a 🎯
recommendation for a ✅ human lock.

## Orient

Read `Project/index.md`, the current phase's `index.md`, its `CONTEXT.md` when
present, and only the latest relevant predecessor setup/result record. Separate
`Observed` evidence, `Human thinking`, `Inferred` implications, `Assumed`
working conditions, and `Missing Info`.

Do not propose a mechanism or simulation matrix before the human has described
their current thinking.

## Hear the human first

Invite an open think-aloud before making any recommendation or asking a
questionnaire:

> 💭 **Your thinking**
>
> Before I frame options, talk me through what you are currently thinking —
> even if it is rough. What feels promising, suspicious, blocked, or worth
> trying? What experiment or mechanism ideas are already in your head, and
> what would you most like to learn from them?
>
> You can answer in rough notes or a stream of thought; you do not need to
> make it coherent yet.

Let the human speak without turning the first response into a questionnaire.
Reflect back the ideas, priorities, evidence references, tensions, and open
points in a concise attributed synthesis. Update the `Human thinking` section
of the phase `CONTEXT.md` after a meaningful decision; maintain current intent
rather than an append-only conversation log.

## Choose the active branch

### Phase framing

Stay at phase level while the phase question, model/scope boundary, claim
limit, useful evidence standard, or human-owned decision is unsettled. Ask one
to three high-information questions per turn. Ask only what can change the
phase contract. Present each turn in this order:

> 🧭 **Phase direction**
>
> 🎯 **Recommended focus:** [the one phase-level uncertainty worth settling
> next]. This matters because [what it unlocks or prevents].
>
> ❓ **1.** [Question whose answer changes the phase question, scope, claim
> limit, or human decision.]
> ❓ **2.** [Optional independent high-information question.]
>
> 📌 **What I'll record:** [the concrete phase-contract element that the
> answer will settle]. You can answer in rough notes or redirect the focus.

Clarify the uncertainty worth reducing now, why it matters over other open
issues, what stays fixed or out of scope, what result would still make the
phase useful, and which decisions the loop must return to the human for.

Do not enter experiment framing until the human confirms the phase question,
boundaries, and claim limit in `CONTEXT.md`.

### Experiment framing

Once phase scope is settled, ask again for present experiment ideas:

> 🧪 **Experiment direction**
>
> 💭 **Your thinking:** Within this phase, what experiments or mechanisms are
> you imagining right now? What would you change or compare first, and what
> would each idea teach us?
>
> You can list fragments, alternatives, or doubts. I will distinguish your
> ideas from any variants I later recommend.

Remind the human of relevant earlier ideas from `CONTEXT.md` without presenting
them as new evidence. Then clarify only the candidate change, reference,
invariants, screening observation, unacceptable artifact, and potential
qualification path that matter to an interpretable decision. When ready to
grill an idea, use the same scan pattern:

> 🧪 **Experiment direction:** [named human idea or its traceable variant]
>
> 🎯 **Recommended focus:** [the smallest contrastive quick screen that would
> make this idea informative]. This is a proposal, not approval.
>
> ❓ **1.** [What single controlled change should this screen make?]
> ❓ **2.** [What observation would make the screen worth continuing?]
> ❓ **3.** [What artifact or result would make this route unhelpful?]
>
> 🚦 **Decision gate:** [the kind of evidence needed before a named long-run
> qualification path could be considered].
>
> 📌 **What I'll record:** [human idea, proposed candidate, or approval state].

Use ⚖️ only when the human must choose between genuinely different scope,
comparison, or compute trade-offs. Use ⚠️ to name a confounder or missing
information, then ask the one question that resolves it; do not turn the
screen into a long form.

## Form traceable candidates and gates

Propose a small number of contrasting quick screens only after the human has
provided ideas. Every candidate records one origin:

- `human idea` — directly stated by the human;
- `human-inspired variant` — a bounded variation of a named human idea; or
- `evidence-driven extension` — a suggestion derived from a named Project
  observation or cited reusable knowledge.

An evidence-driven extension remains `proposed` until the human explicitly
approves it. An approved candidate names its controlled delta, invariants,
screening question, required evidence, rejection/artifact signal, and any
conditional long-run path.

For each approved screen, declare an evidence-based decision gate: the required
evidence, decision condition, named allowed next action, claim the screen cannot
support, and human-return condition. No gate authorizes a new experiment idea.

## Handoff

Return the current `CONTEXT.md` to `phase-planner`. It is ready for
`design-experiment` only when it contains a human-approved candidate or
conditional qualification path. `create-setup` may create `setup.md` only for
that approved context item after the lifecycle gate permits it.

If evidence does not satisfy an approved gate, multiple paths remain plausible,
or a new direction appears, record the unresolved decision and return to the
human; do not create a new branch.
