---
name: scientific-phase-loop
description: "Execute and analyse a human-approved CFD phase through its mandatory verified lifecycle. Use after phase-planner has fixed the phase question and recorded approved candidates, gates, and conditional qualification paths in CONTEXT.md."
---

# Scientific Phase Loop

Navigate the agreed phase through verified execution and evidence analysis until
it reaches a **verified** phase conclusion or a genuine human-owned boundary.

The route may adapt to evidence, but the lifecycle may not be skipped.

## Hard lifecycle invariant

A normal autonomous phase must progress through this order:

```text
PHASE CONTRACT
    ↓
MANDATORY DISCOVERY
    ↓
DISCOVERY EVIDENCE
    ↓
SPECIFIC HYPOTHESIS
    ↓
LONG HYPOTHESIS QUALIFICATION
    ↓
HYPOTHESIS EVIDENCE
    ↓
PHASE CLOSURE
```

Discovery and hypothesis testing are different evidence classes, not interchangeable labels.

- **Discovery** finds which mechanism, formulation, assumption, or branch deserves expensive testing.
- **Hypothesis qualification** tries to earn a strong scientific statement from a deliberately deep run or very small linked campaign.

Do not call a discovery-scale screen a hypothesis qualification merely because the setup file says `hypothesis-test`.

Do not autonomously `CONCLUDE PHASE` before at least one hypothesis qualification has passed the required transition and evidence gates. The only earlier terminal path is `HUMAN_REQUIRED` or an explicit human instruction to stop/reframe the phase.

Every lifecycle transition must call `verify-phase-transition`. A `BLOCK` or `HUMAN_REQUIRED` result is a lock. The scientific agent may not self-overrule it.

## ❗❗❗ Planner launch authorization

When this loop is reached from `phase-planner`, it may start only after the
human explicitly chose the planner's **1️⃣ Continue in this chat** or
**2️⃣ Start in a new task** launch option. A complete `CONTEXT.md` or handoff
alone does not authorize entry.

If that selection is absent or unclear, return to the planner's ❗❗❗ launch
decision
without creating a phase goal, setup, run, or other lifecycle state. A direct
human invocation of `scientific-phase-loop` remains explicit authorization to
enter the loop.

## Enter with a phase handoff

Start from the human-agreed phase handoff or phase setup.

Require:

- the fixed phase question or goal;
- why the question matters now;
- current evidence that matters;
- important assumptions and missing information;
- modelling/scope boundaries;
- what would count as enough evidence for the phase;
- the granted autonomy envelope;
- conditions that must return to the human; and
- the phase-root `CONTEXT.md`, including at least one human-approved candidate
  or conditional qualification path before new compute.

Treat this as the destination, approved route, authority, and boundaries.

### Context-gated experiment authority

The human owns experiment origination and selection. Before planning, setup
creation, execution, or promotion, read the current phase `CONTEXT.md`.

The loop may without repeated human approval:

- execute a setup derived from a named human-approved context candidate;
- verify declared setup/instrumentation requirements and analyse its evidence;
- evaluate a declared decision gate and take only its named allowed next action;
- use research and specialist analysis to challenge or implement an approved
  candidate without changing its scientific purpose;
- allocate and reallocate available Fluent servers;
- stop active Fluent calculations, terminate abandoned workers, restart/reload Fluent, replace loaded cases, and otherwise control active working sessions;
- preserve a quick recovery case+data pair before destroying a scientifically valuable unpreserved state;
- abandon or defer a candidate only when its declared gate permits that action.

This authority does **not** allow the loop to invent, select, modify, or promote
a new experiment; add a bold lane; change a candidate's purpose, controlled
delta, invariants, claim limit, or required evidence; invent plant facts,
measured setpoints, validation targets, physical controller data, or other
human-owned facts; silently change the fixed phase question; cross an explicit
modelling/scope boundary; or delete verified durable Project/OneDrive parent
artifacts merely to make a run convenient.

If a needed fact is explicitly `Missing Info`, a gate does not cover the result,
or an unplanned observation suggests a new direction, return `HUMAN_REQUIRED`.
Do not clear the boundary by inventing a surrogate or new experiment branch.

## Persist current lifecycle state

Maintain one machine-readable file at the phase root:

```text
Project/experiments/<phase>/phase-state.yaml
```

This is current workflow state, not a narrative log. Git history is the history.

Keep at minimum:

```yaml
phase_id: ...
phase_question: ...
state: PHASE_CONTRACT | DISCOVERY_DESIGN | DISCOVERY_RUNNING | DISCOVERY_ANALYSIS | HYPOTHESIS_DEFINITION | HYPOTHESIS_RUN_READY | HYPOTHESIS_RUNNING | HYPOTHESIS_ANALYSIS | PHASE_CLOSURE | HUMAN_REQUIRED

context:
  path: Project/experiments/<phase>/CONTEXT.md
  authority: human-approved-context-only
  approved_candidate_ids: []

autonomy:
  experiment_selection: context_gated
  fluent_fleet_sessions: exclusive | restricted

gates:
  PHASE_CONTRACT: {status: PASS | BLOCK | HUMAN_REQUIRED}
  DISCOVERY_DESIGN: {status: ...}
  DISCOVERY_EXECUTION: {status: ...}
  DISCOVERY_EVIDENCE: {status: ...}
  HYPOTHESIS_DEFINITION: {status: ...}
  HYPOTHESIS_RUN_READY: {status: ...}
  HYPOTHESIS_EXECUTION: {status: ...}
  HYPOTHESIS_EVIDENCE: {status: ...}
  PHASE_CLOSURE: {status: ...}

active_jobs: []
next_required_action: ...
```

Do not infer permission to advance from conversational memory. Read `phase-state.yaml` after context compaction, a self-wake, or any interruption.

## Gate 0 — verify the phase contract

Call `verify-phase-transition` for `PHASE_CONTRACT` before new phase compute.

If the result is `HUMAN_REQUIRED`, write that lock to `phase-state.yaml` and stop autonomous progression. Only explicit human input/authorization or authoritative evidence that directly resolves the missing fact may clear it.

## Orient from evidence

Before proposing new work:

1. read `Project/index.md` and the current phase contract;
2. reconstruct the closest relevant experiments across **all** phases;
3. inspect failed, blocked, partial, non-converged, rejected, and inconclusive work as evidence too;
4. identify what is observed versus inferred, assumed, or missing;
5. identify the most consequential unresolved uncertainty within the approved
   context route.

Search by scientific substance, not setup names alone: mechanism, formulation, multiphase/turbulence model, boundary condition, initialization, numerical architecture, operating regime, comparison logic, and intended question.

For every approved context candidate identify the closest prior experiment and
classify the delta as `NEW`, `PARTIAL REPEAT`, `REPLICATION`, or `REDUNDANT`.
Do not run a `REDUNDANT` candidate; return to the human instead of substituting
a new one.

The governing posture remains:

```text
reasoning proposes
simulation tests
data constrains the conclusion
```

Literature and manuals can justify what deserves testing. They do not establish how the current project case behaves.

## Take control of the live fleet before compute

Whenever new Fluent compute is required, call `fluent-fleet-orchestration`.

Under an exclusive autonomous fleet lease, treat active Fluent sessions as working resources owned by the phase goal, not as untouchable state. Reconcile what is running, preserve a recovery pair when losing an unpreserved scientifically valuable endpoint would matter, then stop/reload/reassign sessions as needed.

Do not destroy verified durable parent artifacts. Do not let an inherited busy session block the goal merely because Fluent is iterating when the phase has explicit takeover authority.

Repeat fleet preflight whenever another compute wave is selected because reachability, jobs, and artifact locality can change.

## Stage 1 — mandatory discovery

Every new autonomous phase must perform discovery before qualification unless the human phase handoff explicitly supplies equivalent already-verified discovery evidence and `verify-phase-transition` accepts it.

Discovery asks:

> What specific hypothesis is worth paying for a deep qualification run?

It may include human-approved:

- short controlled simulation screens;
- a bounded screen listed in `CONTEXT.md`;
- numerical diagnostics;
- analysis of existing runs;
- literature/manual research;
- probes that challenge the conservative mainline.

When simulation discovery is useful, call `design-experiment` in discovery mode
for a named approved context candidate. The human-approved decision gate, not an
arbitrary case count, determines the smallest adequate campaign. Roughly
500–1,000 iterations per case is a useful project ballpark when enough to
expose comparative behaviour, but the declared screening question determines
the horizon. `bold-probe-research` may research an approved speculative
candidate; idle compute never authorizes a new one.

### Discovery design gate

Before implementing discovery compute, call `verify-phase-transition` for `DISCOVERY_DESIGN`.

No `PASS` means no discovery mutation/solve.

## Discovery execution must stay attached

Discovery runs are foreground scientific work.

For discovery mode:

```text
launch synchronous Python/PyFluent run
→ remain attached
→ wait while Fluent calculates
→ verify terminal execution evidence
→ immediately analyse
→ follow the exact next action authorized by CONTEXT.md
```

Do **not** pause the goal, end the turn because Fluent is still running, launch the detached hypothesis handoff path merely to avoid waiting, or require the human to send another message.

A tool/RPC timeout is not permission to pause the goal. Check the operational manifest and live Fluent state. If the approved discovery calculation is still advancing, keep waiting/polling in the active goal until it returns terminal `COMPLETE` or `BLOCKED` evidence.

The same attached behaviour applies throughout the discovery campaign, not only the first run.

After each discovery run counted as evidence, require exact parent/setup proof, readback, save/reopen, smoke success, required instrumentation, requested horizon, final pair, and required histories. Call `verify-phase-transition` for `DISCOVERY_EXECUTION` before treating the run as valid discovery evidence.

## Discovery analysis must earn a hypothesis

Analyse discovery evidence immediately. Use the preplanned core figures and question-specific histories rather than generic overview plots.

Discovery is complete only when it has materially narrowed the uncertainty enough to formulate a specific falsifiable hypothesis that deserves qualification compute.

The discovery result must identify:

- the hypothesis statement/question;
- the observations that motivated it;
- the strongest competing explanation or material alternative;
- why prior evidence does not already settle it;
- what a deeper run could say that discovery cannot.

If discovery has not produced a defensible hypothesis for a declared context
path, return `HUMAN_REQUIRED`. Do not invent more discovery work or advance
merely because a few short simulations finished.

Call `verify-phase-transition` for `DISCOVERY_EVIDENCE`.

Only `PASS` permits hypothesis formation.

## Stage 2 — define the hypothesis contract

Write or confirm the context-approved hypothesis contract before designing the
long run. A long-run path must be named in `CONTEXT.md` and triggered by a
declared gate; discovery evidence does not independently authorize the loop to
promote a new path.

It must state:

```text
Hypothesis
Discovery basis
Competing explanation / material alternative
What would support the hypothesis
What would weaken or reject it
Strong statement the project could make if evidence is sufficient
Important assumptions / claim limits
```

The “strong statement” is the **form of claim the evidence should be capable of supporting**, not a predicted result.

Examples of claim forms include:

- a carrier state remains bounded and mass-closed over the qualification window;
- a model-form change materially changes phase routing relative to the verified reference;
- a proposed mechanism does not explain the observed drift within the tested bounds.

Call `verify-phase-transition` for `HYPOTHESIS_DEFINITION`.

No `PASS` means no qualification design.

## Stage 3 — design the long hypothesis qualification

Call `design-experiment` in hypothesis-test mode only after `DISCOVERY_EVIDENCE` and `HYPOTHESIS_DEFINITION` are `PASS`.

The long run must be designed backward from the strong statement. Define before solving:

- exact comparison/reference basis;
- support/weaken observations;
- required residual/numerical histories;
- phase/full-domain balances;
- question-specific physical histories/fields;
- qualification/final windows and reductions;
- core figures;
- required checkpoints/final artifacts;
- restart/continuation evidence when stationarity or durability is part of the claim.

### Long-run depth rule

For ordinary steady iteration-based full-geometry qualification in this project, plan **at least 10,000 iterations** by default.

For slow inventory, phase-routing, or stationarity questions, 10k–30k or another deliberately justified horizon may be more appropriate.

A shorter hypothesis run requires either:

- explicit human approval of the exception; or
- a scientifically equivalent non-iteration qualification basis appropriate to the model/question.

A 500–1,000 iteration discovery screen does not become a qualification run because the label changed.

For claims of steady/stationary/bounded/reference behaviour, require a continuation or cold save/reopen qualification window when needed to show that the apparent state survives rather than merely passing through a favourable transient.

Before expensive compute, `question-experiment` must independently challenge the hypothesis strategy, then `verify-phase-transition` must return `HYPOTHESIS_RUN_READY == PASS` after implementation/readback/save-reopen/smoke/instrumentation requirements are satisfied.

## Stage 4 — execute the hypothesis qualification

Use `implement-experiment` to build and prove the selected case exactly.

For Codex long hypothesis work, use `supervise-fluent-run` and the self-waking Python path:

```text
verified hypothesis case
→ capture exact CODEX_THREAD_ID
→ detached Python/PyFluent worker
→ run full approved horizon
→ deterministic terminal verification
→ write COMPLETE or BLOCKED manifest
→ resume exact originating scientific thread
→ read phase-state.yaml
→ continue hypothesis evidence analysis
```

Do not background-launch the raw experiment runner directly.

The wakeup path is mandatory on both `COMPLETE` and `BLOCKED`. Do not use `--last` when several jobs can complete out of order.

On Cursor or a runtime without session resume, keep the agent attached through the approved hypothesis horizon instead.

Poor residuals, mass balance, routing, or scientifically disappointing behaviour are evidence, not reasons for the worker to stop early, while Fluent can continue to the approved horizon.

After terminal execution evidence returns, call `verify-phase-transition` for `HYPOTHESIS_EXECUTION`.

## Stage 5 — hypothesis evidence qualification

Do not jump from “runner completed” to interpretation/phase closure.

Produce the analysis and core figures promised in the hypothesis contract. Check the required evidence explicitly.

Missing required evidence is a blocker. For example, if the setup said scaled residual history is required for numerical credibility and that history is unavailable after the run, do not compensate with prose or quietly weaken the gate after seeing the result.

Classify the hypothesis from the data while preserving claim limits and competing explanations.

Call `verify-phase-transition` for `HYPOTHESIS_EVIDENCE`.

If it returns `BLOCK`, repair an approved setup or obtain missing evidence only
when the approved context path permits it. If new evidence reopens uncertainty
or requires another comparison, return `HUMAN_REQUIRED` rather than creating a
new discovery branch.

## Stage 6 — phase closure

Call `check-phase-closure` only after `HYPOTHESIS_EVIDENCE == PASS`.

Normal autonomous closure requires `verify-phase-transition` to return `PHASE_CLOSURE == PASS`.

A bounded or negative conclusion is valid, but it must be earned by the same lifecycle. The autonomous agent may not close a phase from short discovery evidence, an unverified hypothesis run, missing required residual/history evidence, or an unresolved human lock.

After closure review the outcome is:

- `CONCLUDE PHASE` — verified phase-level statement is supported;
- `CONTINUE` — a named approved context path can materially change/strengthen
  the phase answer;
- `RETURN TO HUMAN / PHASE-PLANNER` — the useful next step crosses the human-owned boundary.

If `CONTINUE` would require a new question, candidate, or revised hypothesis,
return to the human. Only a named approved context path may continue.

## Human locks are real locks

When `verify-phase-transition` or `check-phase-closure` returns `HUMAN_REQUIRED` / `RETURN TO HUMAN`, persist the lock in `phase-state.yaml` and stop autonomous progression.

Do not create later setup stages underneath the lock. Do not reinterpret the missing fact as an “assumed numerical target” unless the human explicitly authorizes that surrogate class in the phase contract.

## Make simulations earn their cost

Automation is not a reason to brute-force.

A run earns compute when its plausible outcomes would materially change understanding, distinguish competing explanations, establish a useful bound, reveal behaviour needed for a decision, or efficiently screen several directions.

Discovery optimises breadth and information. Hypothesis qualification optimises depth and claim strength. Keep those purposes distinct.

## Use specialists without surrendering orchestration

Use the smallest relevant specialist:

- `bold-probe-research`, `swarm`, `arena` to research or challenge approved
  candidates, never to create an executable new candidate;
- `design-experiment`, `question-experiment`, `create-setup` for scientific design;
- `fluent-fleet-orchestration` for live placement/session authority;
- `fluent-live-inspection` and `fluent-manual-researcher` for uncertain Fluent configuration;
- `fluent-case-build-and-run`, `implement-experiment`, `supervise-fluent-run` for execution;
- numerical/statistical/domain analysis skills for evidence;
- `verify-phase-transition` for hard lifecycle permission;
- `check-phase-closure` for the final scientific phase decision.

Subagents investigate or independently verify. The scientific phase loop synthesizes and directs work, but it cannot waive hard gates.

## Completion condition for the autonomous goal

The `/goal` is complete only when one of these is true:

1. `PHASE_CLOSURE == PASS` and `check-phase-closure` returns `CONCLUDE PHASE`; or
2. a persisted `HUMAN_REQUIRED` / `RETURN TO HUMAN` lock identifies the exact missing fact, permission, or phase-level decision.

Do not end the goal merely because a discovery simulation is still running, a long hypothesis worker has been launched, or one experiment produced an interesting result. Discovery stays attached; a Codex hypothesis worker self-wakes the exact originating goal thread; the lifecycle continues from `phase-state.yaml`.
