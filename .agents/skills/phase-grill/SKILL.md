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

Treat the conversation as a **decision tree**. A round contains the current
**frontier**: human decisions whose prerequisites are already settled. Ask the
whole frontier, then wait. Do not mix in a dependent question merely because
it is likely to matter later.

Open every round with a compact mode and outcome. Make every point a labelled
bullet so the human can see what it means and how to answer it:

```md
🧭 **Phase framing — round <n>**

- **Goal:** <the phase decision this round will sharpen>.
- **Unlocks:** <what can be decided after these answers>.

1️⃣ — **<short decision title>**

- **Question:** <one human-owned decision in plain language>.
- **Why it matters:** <the consequence for scope, evidence, or a later choice>.
- **Options:**
  - **A — <option>:** <consequence>.
  - **B — <option>:** <consequence>.
- **Reply with:** <the smallest useful answer; rough notes are welcome>.

➡️ **Recommended answer:** <a provisional answer and its reason>.

---

2️⃣ — **<independent decision title>**

- **Question:** ...
- **Why it matters:** ...
- **Reply with:** ...

➡️ **Recommended answer:** ...
```

Use `🧭` for phase framing and `🧪` for experiment framing. Use options only
when there is a real choice; otherwise omit that bullet. `➡️ Recommended
answer` is an explicit, revisable proposal—not a decision or approved
candidate. If a recommendation would prematurely supply the human's idea, say
so plainly and leave the recommendation open until they have thought aloud.

Mark every question with the sequential numeric emojis `1️⃣`, `2️⃣`, and
`3️⃣`, in the form `1️⃣ — **Title**`. The visible number is the reply handle:
refer back to “1” or “2”, never `Q1`, `Q2`, a red-circle marker, or a
question-mark marker.

Use at most three independent questions in a round. Ask one question when it
is the only frontier decision. Find facts in the repository, evidence, or
tools rather than asking the human for something the agent can determine.

After the human replies, first reflect the outcome before asking the next
frontier:

```md
✅ **Locked in**

- **Decision:** <what the human confirmed>.
- **Reason:** <their stated reasoning, attributed to them>.

⚠️ **Still open**

- **Decision:** <the next unresolved, prerequisite-aware issue>.

📌 **CONTEXT.md update**

- **Record:** <the exact field or candidate/gate status being updated>.
```

Icons guide the conversation only. Record the final decision, evidence, and
approval state in plain, durable `CONTEXT.md` fields; never mistake a `➡️`
recommendation for a `✅` human lock.

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
> - **Tell me:** what you are currently thinking, even if it is rough.
> - **Include anything useful:** what feels promising, suspicious, blocked, or
>   worth trying.
> - **Also include:** experiment or mechanism ideas already in your head and
>   what you would most like to learn.
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

> 🧭 **Phase framing — round <n>**
>
> - **Goal:** settle [one phase-level uncertainty].
> - **Unlocks:** [the phase-contract element this will make safe to frame].
>
> 1️⃣ — **<short decision title>**
>
> - **Question:** [Question whose answer changes the phase question, scope,
>   claim limit, or human decision.]
> - **Why it matters:** [the specific consequence of the answer.]
> - **Reply with:** [a preference, boundary, or rough reasoning.]
>
> ➡️ **Recommended answer:** [a provisional recommendation and why; omit the
> recommendation until the human has supplied the thinking it depends on.]

Clarify the uncertainty worth reducing now, why it matters over other open
issues, what stays fixed or out of scope, what result would still make the
phase useful, and which decisions the loop must return to the human for.

Do not enter experiment framing until the human confirms the phase question,
boundaries, and claim limit in `CONTEXT.md`.

### Experiment framing

Once phase scope is settled, ask again for present experiment ideas:

> 🧪 **Experiment direction**
>
> 💭 **Your thinking**
>
> - **Ideas:** What experiments or mechanisms are you imagining right now?
> - **First contrast:** What would you change or compare first?
> - **Learning value:** What would each idea teach us?
>
> You can list fragments, alternatives, or doubts. I will distinguish your
> ideas from any variants I later recommend.

Remind the human of relevant earlier ideas from `CONTEXT.md` without presenting
them as new evidence. Then clarify only the candidate change, reference,
invariants, screening observation, unacceptable artifact, and potential
qualification path that matter to an interpretable decision. When ready to
grill an idea, use the same scan pattern:

> 🧪 **Experiment framing — round <n>**
>
> - **Idea under discussion:** [named human idea or traceable variant].
> - **Goal:** settle [the next independent experiment decision].
> - **Unlocks:** [the quick-screen or gate detail that can be specified next].
>
> 1️⃣ — **Controlled change**
>
> - **Question:** What single controlled change should this screen make?
> - **Why it matters:** It keeps the comparison interpretable.
> - **Reply with:** the preferred delta, or the choices you are weighing.
>
> ➡️ **Recommended answer:** [the smallest contrastive quick screen and why;
> this remains a proposal until the human approves it.]
>
> 2️⃣ — **Continue signal**
>
> - **Question:** What observation would make the screen worth continuing?
> - **Why it matters:** It defines the evidence that justifies a longer run.
> - **Reply with:** the result you would find informative.
>
> 🚦 **Decision gate**
>
> - **Evidence needed:** [the evidence required before a named qualification
>   path could be considered.]
> - **No automatic branch:** a gate can select only a human-approved path.
>
> 📌 **CONTEXT.md update**
>
> - **Record:** [human idea, proposed candidate, approval state, or gate].

Use ⚖️ only when the human must choose between genuinely different scope,
comparison, or compute trade-offs. In that case, present each alternative as a
bullet with its concrete consequence. Use ⚠️ to name a confounder or missing
information, then ask the one frontier question that resolves it; do not turn
the screen into a long form.

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
