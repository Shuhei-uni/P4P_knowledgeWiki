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
Loop must use the recorded profile rather than stopping for another reply. If
the active handoff or `CONTEXT.md` already records this profile, consume it
directly: a running autonomous goal never waits for duplicate answers.

`ATTEMPTED_UNVERIFIED` and `NOT_RUN` require autonomous reconciliation or
execution. A `BLOCKED_VERIFIED` item satisfies the route only after its
recovery attempts, evidence, and claim consequence are durably recorded; the
loop then continues the remaining queue and may enter its pre-authorized Auto
Loop route.

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

For a scoped Auto Loop profile, the recorded hypothesis horizon is the
authorized horizon. A **2,000-iteration** hypothesis run is a valid scoped
qualification when the setup says so and its claim is limited to the stated
screening/scoping window; it must not be promoted into a long-stationarity or
fully converged claim. Use the normal 10,000+ horizon when the intended claim
needs that stronger basis.

When the user has already supplied a profile in the active goal or handoff,
record it and proceed without another question. In particular, a profile may
direct one available server to deepen existing families and another to broaden
the solution space; new setting families screen at **500 iterations**, extend
promising cases to **1,000**, and use the recorded scoped hypothesis horizon.
