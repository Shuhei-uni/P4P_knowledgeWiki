# Loop autonomy check-in

Run this check-in **once per autonomous goal**, before fleet preflight or any
case mutation. Record the answers in the phase-root `phase-state.yaml` so a
self-wake or a Phase Loop → Auto Loop handoff does not ask them again.

> ❗ **Fluent session authority**
>
> Continuing gives me full authority to overwrite the current Fluent session.
> Reply within **one minute** if you want to restrict that authority. If there
> is no reply, I will proceed with full authority for this loop.

Wait up to one minute when the runtime can wait for a human reply. An explicit
restriction wins; otherwise record `fluent_fleet_sessions: full`, including a
timestamp or timeout expiry. This is the only Fluent-session authority question.
Fleet orchestration consumes the recorded authority and must not ask again.

## Phase Loop completion route

In the same Phase Loop check-in, ask:

> When every defined setup has `COMPLETE_VERIFIED`, should I return to you, or
> continue straight into Auto Loop?

If the answer is **Auto Loop**, collect the Auto Loop profile below before any
Phase Loop execution begins. That pre-authorizes the later transition; Auto
Loop must use the recorded profile rather than stopping for another reply.

`BLOCKED_VERIFIED`, `ATTEMPTED_UNVERIFIED`, and `NOT_RUN` do not satisfy this
completion route. They return to the human unless the human explicitly changes
the queue.

## Auto Loop profile

Ask these bluntly, in one compact reply:

- 🧪 **Setup family:** Any setup family to explore further, if there are
  already results?
- 🔁 **Hypothesis runs:** How many iterations per hypothesis-answering run?
- 🧭 **Direction:** Deepen the experiments already run, or broaden the
  solution space through enumeration?
- ⏰ **Stop time:** What time should I stop launching new work?

Record the answer as the Auto Loop envelope: family focus, hypothesis horizon,
direction, and wall-clock stop time with timezone. The stop time normally
prevents **new** work after the deadline; an already-running approved
hypothesis run finishes its declared horizon unless the human explicitly says
to interrupt it.

An answer below the normal 10,000-iteration qualification depth is an explicit
human-approved short-run exception only when recorded as such in the setup.
Otherwise use it as a discovery/probe horizon; do not relabel a short run as a
hypothesis qualification.
