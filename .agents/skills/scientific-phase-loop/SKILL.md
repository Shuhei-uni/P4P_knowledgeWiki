---
name: scientific-phase-loop
description: "Navigate a scientific phase from a human-defined phase goal toward a defensible conclusion. Use when the phase direction and boundaries are agreed but the route is not known in advance, and the agent should autonomously learn from evidence, choose between discovery and hypothesis-test experiments, run simulations, interpret results, revise hypotheses and working assumptions, and keep testing until the phase is answered or a genuine human boundary is reached."
---

# Scientific Phase Loop

You are navigating a scientific phase toward a conclusion.

Keep the phase question in view, but do not assume the route to it is known in advance. The purpose of the loop is not to execute a predetermined sequence of simulations. It is to reduce meaningful uncertainty about the phase question until there is sufficient evidence for the decision or scientific statement the phase was created to make.

## Enter with a phase handoff

Start from the agreed phase goal or question and any boundaries supplied by the human or `phase-planner`.

The handoff may include:

- the phase goal or question;
- current evidence that matters;
- important unresolved uncertainty;
- human constraints or compute/resource boundaries;
- what would count as a useful phase-level conclusion;
- conditions that should return control to the human.

Treat this as the destination and boundaries, not the route. Do not turn the phase handoff into a fixed experiment checklist.

Within those boundaries, you own the scientific reasoning needed to move the phase forward.

## Simulation evidence is the anchor

Reasoning, literature, prior experience, and specialist opinions are useful for forming hypotheses, identifying working assumptions, and deciding what to test. Unless genuinely equivalent evidence already exists, they do not tell you what this simulation will do.

Treat untested expectations as hypotheses. Treat assumptions as assumptions: useful working conditions that may bound the interpretation, not hidden facts and not automatic experiment targets.

When the uncertainty concerns the behaviour of the current CFD model, the strongest way to resolve it is normally to run the relevant simulation properly and inspect the resulting data.

The governing posture is:

```text
reasoning proposes
simulation tests
data constrains the conclusion
```

Simulation output is not automatically truth. Its scientific weight depends on whether the case was implemented as intended, run for an adequate duration or convergence window, and shown to be numerically credible for the claim being made. Use the appropriate specialist skills to establish that before making strong conclusions.

## Orient to the phase

Begin by forming a clear picture of where the investigation stands.

Understand the phase goal, the current model, the important working assumptions, the experiments already attempted, the evidence they produced, what appears established, what has failed, and what remains unresolved.

Previous work is evidence, not a prescribed trajectory. Do not simply continue from the last setup because it is the most recent. Reconsider the problem from the phase question itself.

Ask:

- Where are we now?
- What is genuinely supported by simulation evidence?
- What is still only a hypothesis or interpretation?
- Which working assumptions matter to the current conclusion?
- Is any assumption now questioned or materially challenged by evidence?
- What uncertainty matters most to the phase goal?
- What observation would materially change our understanding?

The repository is the durable scientific memory. Use it to understand the investigation, not to constrain the investigation to paths already tried.

## Reconstruct prior experiment history before proposing new work

Before inventing new experiment directions, inspect the retained Project history across all phases. Start from `Project/index.md`, `Project/experiments/README.md`, relevant phase indexes, `Project/observations/`, and the setup/results records of the closest historical experiments.

Search by scientific substance rather than names alone: physical mechanism, formulation, modelling choice, boundary condition, initialization, numerical change, operating regime, intended question, and comparison logic. Failed, rejected, non-converged, partial, and inconclusive runs still count as prior work and may already rule out, constrain, or reshape a proposed idea.

For every serious mainline or speculative candidate, identify the closest previous experiment or experiments and state the exact scientific delta. Classify the candidate as `NEW`, `PARTIAL REPEAT`, `REPLICATION`, or `REDUNDANT`, and explain why existing evidence or additional analysis of existing data does not already answer the proposed question.

A new setup ID, parent, phase, or slightly different parameter value is not enough to make an experiment new. Do not proceed to runnable design with a `REDUNDANT` candidate. A replication must be deliberate and justified as replication. A failed historical run may be repeated only when the new attempt has a specific correction, stronger evidence requirement, or unresolved scientific delta.

## Preflight the live compute fleet before runnable design

Whenever the next step requires new Fluent compute, call `fluent-fleet-orchestration` before committing runnable experiments.

Establish which configured servers are actually reachable now, which are idle or occupied, and which exact parent/final/recovery case+data artifacts are accessible locally or through the shared OneDrive layer. Treat this as live operational evidence, not static project configuration.

Give `design-experiment` the real resource envelope so a scientifically justified campaign can exploit useful parallel capacity and case locality. Use the number of servers actually usable now; never assume a fixed fleet size.

When two or more servers are simultaneously usable for new compute, reserve one server lane for a bold speculative probe. This is mandatory while the autonomous loop is active: ordinary mainline work must not consume every usable server merely because it can. The remaining usable servers carry the strongest runnable mainline work. Do not preempt an already running approved job solely to create the lane; establish or restore the bold lane at the next placement opportunity.

Repeat this preflight every time the loop returns for another round of compute, because server availability and artifact locality may have changed since the previous cycle.

## Navigate uncertainty

Treat the unresolved parts of the phase as a landscape of uncertainty.

There may be several plausible lines of investigation. Some may involve conservative numerical changes. Others may challenge an equation, formulation, physical assumption, initialization strategy, interpretation, or even the way the question has been framed. A useful branch may also be additional analysis of an existing run, literature research, or a deliberately simple diagnostic case.

Do not force the phase into a fixed experiment matrix by default. When the important direction is genuinely unclear and breadth itself would reduce uncertainty, deliberately enter discovery mode and use a bounded matrix instead.

Sketch the branches that are visible now. Leave the rest in the fog. As evidence arrives, new branches may become visible, old branches may collapse, hypotheses may strengthen or weaken, and an assumption may become important enough to challenge.

Do not become fixated on assumptions merely because they exist. Challenge them when evidence gives a concrete reason and when they could materially affect the phase conclusion.

## Choose the experiment-design mode

When new simulation evidence is needed, decide what kind of uncertainty you are trying to reduce before designing the cases.

### Discovery mode: find where to look

Use discovery mode when literature, past results, and current reasoning still leave several plausible directions and it is not yet clear which mechanism, setting, formulation, or branch deserves an expensive test.

Call `design-experiment` in discovery mode and use `explore-experiment-space` to create a quick discovery campaign of at most twelve cases. Twelve is a ceiling, not a target; use fewer whenever they span the useful uncertainty adequately.

A rough budget of 500 to 1,000 iterations per case is a useful project ballpark when that is enough to expose early comparative behaviour. This is a planning default, not a universal convergence criterion.

**Stay attached throughout discovery mode.** Discovery runs are deliberately short, so do not end the agent turn or hand them to the detached sleep/wake path. Wait for each discovery run to finish, inspect the evidence immediately, update the working hypothesis, and choose the next useful discovery experiment while the same scientific thread is active.

Optimise discovery mode for breadth, comparability, and information across the matrix. Use the resulting histories, plots, balances, monitors, and other evidence to identify promising directions, eliminate weak ones, reveal unexpected behaviour, and sharpen the next hypothesis.

Treat these short runs as screening evidence. They can tell you where the evidence is pointing, but they normally cannot support the same strength of statement as a deliberately long hypothesis test.

### Hypothesis-test mode: earn a stronger answer

Use hypothesis-test mode when there is a specific, important hypothesis or question and the result could support a meaningful statement about how the model behaves.

Call `design-experiment` in hypothesis-test mode. Prefer one focused experiment or a very small linked campaign whose evidence is designed around the claim you want to test.

A run around 10,000 iterations may be an appropriate ballpark for the current project when that duration is deliberately chosen to expose the required behaviour. Do not treat 10,000 as a universal criterion; justify the run length from the model, question, and evidence required.

Before spending the compute, be able to say what observations would support or weaken the hypothesis, what working assumptions materially bound the interpretation, and what data must exist to make that judgement.

**Hypothesis-test runs must return to the scientific loop.** On Codex, capture the originating thread/session ID and make the Python execution path resume that exact thread on both `COMPLETE` and `BLOCKED` before a background hypothesis run is launched. On Cursor, keep the agent attached through the approved horizon; do not launch a Codex self-wake job and do not treat missing `CODEX_THREAD_ID` as a blocker.

The two modes are not fixed stages. Discovery can produce a focused hypothesis worth testing deeply. A long hypothesis test can expose an unexpected broad uncertainty that sends the loop back into discovery.

Choose again whenever the evidence changes the nature of the uncertainty.

## Keep one bold-probe lane active when parallel compute exists

When the live fleet has two or more servers usable for new compute, one server is the **bold-probe lane**. Keep that lane running a scientifically justified speculative experiment while the autonomous loop remains active and the fleet continues to support at least two usable servers.

The bold lane is not merely overflow capacity. It exists to test questions that the conservative mainline is unlikely to reach quickly. When a bold probe completes, analyse what it taught, rerun the prior-experiment collision check, and if two or more servers remain usable, select and launch the next justified bold probe rather than quietly folding that server back into ordinary mainline work.

A bold speculative probe may:

- challenge a bold working assumption or accepted interpretation;
- test a substantially different mechanism, formulation, initialization strategy, or operating regime;
- investigate an unexpected behaviour that the current mainline does not explain;
- ask a broader question whose answer could make the current route unnecessary or expose a better future direction;
- screen a question that could become a candidate for a future phase.

Prefer probes with asymmetric information value: quick enough to justify as exploratory compute, independently runnable, and potentially capable of changing how the project is understood even if the expected answer seems unlikely. Both a positive and a negative result should teach something.

The mandatory lane does not authorize junk experiments. Every bold probe must pass the same historical collision check as mainline work and have a clear learning target. Reject probes that are redundant, uninterpretable, unsafe to compare, excessively expensive for the question, or merely small parameter variations dressed up as bold exploration.

If no valid non-redundant bold probe can currently be formulated, do not fill the lane with noise. Use analysis, literature, prior evidence, independent subagents, or adversarial reasoning immediately to generate a better bold question. If a real modelling, artifact, or execution boundary still prevents any justified probe, record that blocker explicitly; that is the exception to keeping the lane occupied.

A speculative probe may sit outside the active phase question as an exploratory side branch when it remains within the agreed compute and modelling boundaries. It does **not** silently create or promote a new formal phase. If its result deserves a sustained new phase, preserve the evidence and return that candidate direction to the human / `phase-planner` for phase-level selection.

Re-evaluate the whole portfolio whenever results return. A speculative branch can be dropped, repeated more carefully, folded into the current phase if it becomes directly relevant, or proposed as a future phase. While two or more servers remain usable, dropping one bold branch should normally lead to a different justified bold probe taking its place.

## Execute approved experiments according to mode

Once `create-setup` has made the experiment precise, call `fluent-fleet-orchestration` again to resolve each server-neutral setup into an explicit execution plan: run ID, selected server, exact parent artifact, any verified OneDrive staging, remote paths, and durability expectations.

Then call `implement-experiment` to build, reload-verify, and smoke-test it.

For **discovery mode**, keep the agent attached to the Python/PyFluent execution through the short planned run. Do not use `run_and_handoff.py` merely to avoid waiting. When the run returns, analyse it immediately and continue the discovery loop while context is live.

For **hypothesis-test mode**, pass the long calculation to `supervise-fluent-run`. On Codex, the Python execution path must include the terminal handoff that resumes the originating Codex thread after verified `COMPLETE` or `BLOCKED`; the current turn may end only after that wake-up contract is in place. On Cursor, keep the agent attached through the approved horizon and analyse when the run returns in the same session.

For multi-server or multi-job Codex hypothesis work, every background job must carry the explicit Codex session/thread ID that owns the scientific loop. Never use `--last`, because jobs may complete in a different order from launch order. Do not use `codex exec resume` from Cursor.

A zero Python return code is not sufficient completion proof. Require locally visible final files and/or a deterministic verifier command that proves the declared remote final state before a hypothesis run records `COMPLETE`.

Do not independently choose TUI-driven iteration, a Fluent journal/batch, or GUI-owned execution. Those mechanisms require explicit human approval for that specific run. If the Python/PyFluent path is blocked, return the execution evidence rather than silently changing run mechanism.

The run supervisor is an execution boundary, not another scientist. It should let poor residuals, poor balances, or unexpected model behaviour continue to the planned horizon when Fluent can still solve. A genuine initialization failure, floating-point/fatal error, process crash, unreconciled run state, or failed final save produces `BLOCKED` and wakes this loop for a rethink rather than improvising numerics inside the worker.

Important final states and selected expensive recovery checkpoints should not remain dependent on one server. When practical, preserve complete paired case+data artifacts and promote them through the OneDrive durability path defined by `fluent-fleet-orchestration`.

## Make simulations earn their cost

Simulation time is expensive. Do not brute-force the phase merely because automation makes it possible.

In hypothesis-test mode, prefer a small number of high-information runs over many weakly motivated cases. In discovery mode, a somewhat broader matrix is justified only because the combined comparison is the information source; keep it bounded and make every case contribute to reducing uncertainty. Bold speculative probes earn their place differently: they must have unusually high potential information value and justify the dedicated exploratory lane through the question they test, not by pretending every available server needs any arbitrary job.

A simulation earns its cost when its possible outcomes would materially change the current understanding, distinguish between plausible explanations, establish a useful bound, reveal behaviour needed to decide the next move, or efficiently screen several plausible directions.

Before committing compute, ask what the run or matrix can teach that the current evidence cannot.

Whenever possible, design a run so that both success and failure are informative. Capture enough behaviour, history, and comparison data that the run can answer more than a narrow endpoint question without contaminating the experiment with unnecessary changes.

Do not confuse a large sweep with a strong investigation. Even discovery mode is a deliberately small scientific matrix, not brute-force coverage.

## Learn, then look again

Each meaningful piece of work should change the picture of the phase.

After new evidence arrives, do not blindly continue the old plan. Reconsider the landscape:

```text
What did the simulation or analysis actually show?
        ↓
What changed in our understanding?
        ↓
What happened to the current hypothesis?
        ↓
Did any important working assumption change state?
        ↓
What remains uncertain?
        ↓
Is the uncertainty broad or focused now?
        ↓
What would be most informative next?
```

Sometimes the answer is another experiment. Sometimes it is more analysis of the same run, a numerical sensitivity, a literature check, a repair to the setup, a challenge to the current model, or no further work at all.

The loop should remain responsive to evidence rather than loyal to its original plan.

When another experiment is justified, form or revise the hypothesis, carry forward the relevant working assumptions, choose discovery or hypothesis-test mode, design the experiment or campaign, run it, analyse the resulting evidence, interpret it, and update the phase understanding before choosing again.

After each meaningful experiment or analysis cycle, call `check-phase-closure` before starting another cycle.

## Use specialists to deepen the investigation

The orchestrator owns the scientific direction, not every specialist discipline beneath it.

Reach for specialist skills and subagents when they can sharpen the picture. They may investigate previous experiments, design candidate tests, assess CFD numerics, analyse data, apply statistics, search literature, implement a Fluent case, supervise an execution, or challenge an interpretation.

Use parallel or independent viewpoints when the problem benefits from diversity of thought. Use adversarial review when a consequential conclusion, experiment design, assumption, or interpretation deserves to be challenged.

Subagents investigate. The orchestrator synthesises and decides.

Do not route work to a specialist merely because that skill exists. Call the capability that fits the uncertainty in front of you.

## Let branches compete with evidence

A phase may have several competing branches at once.

Think of them as hypotheses about how to make progress, not commitments. One branch may explore gentle changes while another challenges the formulation more deeply. One may prove fruitful, several may converge on the same conclusion, or the evidence may reveal that all of them were asking the wrong question.

Branches should earn continued attention through what they teach.

When useful, compare branches by questions such as:

- What uncertainty does this branch reduce?
- What would we learn if it succeeds?
- What would we learn if it fails?
- Can it distinguish between competing explanations?
- Is it repeating something the current evidence has already settled?
- Is there a cheaper or clearer way to learn the same thing?

Do not confuse completing a branch with advancing the phase.

## Human direction and autonomy

The human defines the phase goal and may define boundaries, preferences, compute limits, or decisions they want to retain.

Within those boundaries, use judgement. Do not ask the human to decide questions that can be answered by inspecting evidence, running a reversible diagnostic, or asking a specialist.

Return to the human when the investigation reaches a genuine judgement boundary: a major change in project direction, promotion of a speculative probe into a sustained new phase, a new modelling assumption with broad consequences, an important ambiguity that evidence cannot resolve, a material compute or resource decision outside the agreed scope, an execution mechanism requiring TUI/journal approval, or an explicit human-selection gate.

If the phase has been handed over for autonomous work, keep moving while there are credible, useful ways to reduce uncertainty within the agreed boundaries.

## Use the closure gate

The output of this loop is not a collection of simulations. It is a defensible phase-level conclusion and the evidence that supports it.

After every meaningful cycle, use `check-phase-closure` and act on one of three outcomes:

1. **CONTINUE** — an important unresolved hypothesis or materially challenged assumption remains and a useful, feasible investigation could materially strengthen or change the phase answer;
2. **CONCLUDE PHASE** — there is sufficient evidence for the decision or scientific statement the phase was created to make, and further feasible work is unlikely to change that statement enough to matter;
3. **RETURN TO HUMAN / PHASE-PLANNER** — useful progress now requires a phase-level judgement outside the agreed autonomous boundaries.

Do not use complete understanding as the finish line. CFD investigation can nearly always expose another uncertainty. The relevant question is whether the remaining uncertainty materially threatens the statement this phase needs to make.

### Anti-loop safeguard

If two consecutive experiment or analysis cycles fail to materially change the current understanding, reduce an important uncertainty, strengthen the phase-level statement, or materially update an assumption, treat the current route as stagnant.

Do not generate a third minor variation simply to keep the loop alive.

Instead, substantially rethink the route — including the experiment-design mode, analysis, modelling assumption, or branch — or return control to `phase-planner` when that rethink crosses a genuine phase-level boundary.

Stagnation is evidence about the route, not a reason to lower the evidentiary standard.

When the outcome is `CONCLUDE PHASE` or `RETURN TO HUMAN / PHASE-PLANNER`, do not plan the next phase on your own. Produce a concise phase-state handoff that `phase-planner` and the human can use to decide what comes next.

A good ending should make clear:

- what the phase set out to understand;
- what the simulations and analyses actually established;
- what remains hypothesis rather than evidence;
- which important assumptions remain accepted-for-now, questioned, or materially challenged;
- what numerical or modelling limitations bound the conclusion;
- why the loop stopped or returned control.

Do not manufacture certainty. A well-supported negative or conditional conclusion is a successful phase conclusion.

## Preserve the scientific thread

Long-running research should survive the death of any individual agent context or physical Fluent server.

Use the repository to preserve the scientific thread through setup definitions, results, observations, figures, hypotheses, working assumptions, and the current phase understanding. Use verified OneDrive copies of important full case+data states to preserve the reusable simulation artifacts themselves. A fresh agent should be able to recover where the phase stands and a different available server should be able to recover important parent/restart artifacts without depending on one machine remaining online forever.

Keep durable state concise enough to be useful. The repository is the memory of the investigation, not a transcript of the agent's thought process; OneDrive is the durable artifact layer, not a substitute for scientific provenance.