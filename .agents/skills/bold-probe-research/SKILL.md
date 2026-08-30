---
name: bold-probe-research
description: "Research and frame evidence-backed bold experiment candidates before a speculative probe is selected. Invoke automatically whenever scientific-phase-loop or design-experiment needs a bold-probe candidate, especially when the point is to challenge a model form, physical assumption, mechanism, numerical architecture, initialization strategy, or accepted interpretation rather than make a nearby parameter variation."
---

# Bold Probe Research

Use this skill before selecting a bold speculative experiment.

A bold probe should come from a researched scientific question, not from novelty for its own sake. Its purpose is to expose a plausible mechanism, formulation, assumption, or alternative representation that the conservative mainline is unlikely to test quickly.

This skill is read-only. It researches and frames candidates; it does not create setup records, mutate Fluent, launch simulations, or decide phase direction on behalf of the orchestrator.

## Mandatory trigger

Invoke this skill whenever:

- `scientific-phase-loop` has two or more usable servers and needs to populate or refresh the mandatory bold-probe lane;
- `design-experiment` is considering a candidate described as bold, speculative, orthogonal, alternative-formulation, or assumption-challenging;
- a completed bold probe needs a genuinely different successor rather than another nearby variation;
- the current mainline is becoming stagnant and an evidence-backed alternative question is needed;
- the best next question may come from literature, Fluent guidance, another modelling family, a known physical mechanism, or a materially different numerical architecture.

Do not use this skill for routine mainline parameter tuning unless that research is needed to understand the science itself.

## Start from the exact scientific tension

Before searching broadly, state the current tension in compact form:

```text
Current model / working interpretation
        ↓
What evidence is failing, unexplained, or unexpectedly insensitive?
        ↓
What assumption or mechanism might explain that?
        ↓
What kind of result would materially change our understanding?
```

Record the strongest mainline evidence, the assumption or mechanism under pressure, the boundaries that must remain respected, and why a conservative continuation is unlikely to answer the same question efficiently.

Do not start from "what other Fluent models exist?" Start from "what scientific explanation is still plausible and consequential?"

## Reconstruct local prior work first

Before external research, perform the same project-history collision check required by `scientific-phase-loop` and `design-experiment`.

Search the retained Project history across phases by scientific substance:

- mechanism;
- formulation;
- turbulence or multiphase model;
- phase treatment;
- boundary condition;
- initialization;
- numerical architecture;
- operating regime;
- intended question;
- comparison logic.

For each candidate direction that later emerges, identify the closest prior experiment and classify the proposed delta as `NEW`, `PARTIAL REPEAT`, `REPLICATION`, or `REDUNDANT`.

A failed or blocked historical implementation still counts. For example, a prior Eulerian setup blocker means a new Eulerian probe must explain what is now different: stronger model definition, a manual-backed capability recipe, a different scientific question, or another concrete correction.

## Research in layers

Use research to widen the mechanism space before narrowing it again.

### 1. Existing reusable CFD knowledge

Search `CFD_wiki/` first for relevant literature extraction, Fluent guidance, model comparisons, known limitations, and previous synthesis.

Use `cfd-wiki` when the repository already contains useful knowledge that needs structured retrieval.

### 2. Official Fluent / Ansys guidance

For candidate Fluent model forms or solver architectures, check the version-relevant official Fluent documentation for:

- intended applicability;
- required model assumptions;
- known limitations;
- recommended model families for the relevant flow regime;
- setup dependencies that materially affect feasibility;
- numerical cautions that could make the candidate impractical or confounded.

This is scientific/model-selection research, not implementation capability research. If the candidate is later selected and a setting cannot be implemented safely, hand that problem to `fluent-live-inspection` / `fluent-manual-researcher`.

Do not treat a Fluent default, screenshot selection, or available menu item as evidence that the model is scientifically appropriate.

### 3. External literature when local coverage is thin

Search current or authoritative external literature when the repo does not adequately cover the uncertainty.

Prefer primary papers, review papers, conference literature with enough methodological detail, official Ansys guidance, and work on comparable cyclone/separator or strongly swirling multiphase problems.

Research should answer questions such as:

- What alternative physical explanation has been reported for similar behaviour?
- Which model form is normally used when the current approximation breaks down?
- What assumptions distinguish the candidate from the current model?
- What diagnostic would reveal whether the candidate mechanism matters?
- What failure mode or confounder is known for this candidate?
- What would make the candidate too expensive or too ambiguous to be useful as a short probe?

### 4. Parallel research when breadth matters

Use `swarm` when the bold question benefits from independent research angles. Split by mechanism or model family rather than having several workers perform the same generic search.

Useful research lanes may include:

- alternative multiphase formulations;
- strong-swirl turbulence treatment;
- outlet / phase-interaction physics;
- initialization and solution architecture;
- comparable separator CFD studies;
- known model limitations or convergence pathologies.

Subagents gather evidence. They do not select the bold experiment.

## Produce a Bold-Probe Research Brief

Synthesize the research before candidate selection. Keep the brief compact enough to guide an experiment decision.

For each serious candidate, record:

| Field | Required content |
|---|---|
| `candidate` | Short direction name |
| `scientific_question` | The actual question the probe would ask |
| `challenged_assumption` | What current assumption, interpretation, equation, or mechanism it puts under pressure |
| `research_basis` | Key literature/manual/project evidence and source pointers |
| `why_now` | Which current project result makes this candidate relevant now |
| `prior_collision` | Closest previous experiment and `NEW` / `PARTIAL REPEAT` / `REPLICATION` / `REDUNDANT` judgement |
| `minimal_probe` | Smallest simulation or diagnostic that could test the idea |
| `positive_learning` | What a positive result would change |
| `negative_learning` | What a negative result would still teach |
| `main_confounders` | What could make the result uninterpretable |
| `tractability` | Rough feasibility / cost / setup risk for a bold-lane screen |
| `implementation_unknowns` | Any Fluent capability questions to resolve only if selected |

Do not create a long literature review. The output exists to improve experiment choice.

## Candidate quality rules

A candidate is strong when:

- it is tied to a plausible researched mechanism or modelling limitation;
- it attacks a consequential uncertainty rather than a cosmetic setting;
- it is meaningfully different from the conservative mainline;
- it can be tested with a bounded experiment or diagnostic;
- both success and failure would teach something;
- the expected information is worth the compute and setup complexity;
- the result can be interpreted without changing so many things that the question becomes meaningless.

Bold does **not** mean maximally complicated.

A simple test of a different governing assumption can be bolder and more informative than enabling five advanced models simultaneously.

Reject or defer candidates that are:

- redundant with project history;
- motivated only by an available Fluent option;
- dependent on an unsupported scientific assumption;
- so expensive that they cannot function as a probe;
- impossible to interpret because several fundamental changes are bundled together;
- outside the human-agreed modelling or compute boundary;
- actually a new phase direction rather than a bounded side probe.

## Distinguish research evidence from simulation evidence

Literature and manuals can justify *why a question deserves to be tested*. They do not prove how the current separator case will behave.

Preserve this distinction explicitly:

```text
Research says this mechanism/model is plausible
        ↓
Bold probe tests whether it matters here
        ↓
Project simulation data decides what happened here
```

Do not write a literature expectation as a project finding.

## Selection handoff

After the research brief is complete:

1. use `arena` when several genuinely different researched candidates deserve independent comparison;
2. hand the strongest candidate or candidate set back to `design-experiment`;
3. let `question-experiment` challenge its scientific value, interpretability, and cost before setup creation;
4. only after selection should implementation-specific uncertainty be resolved through `fluent-live-inspection` or `fluent-manual-researcher`.

If research reveals that the strongest idea would change the phase objective, success definition, or agreed modelling boundary rather than merely probe it, do not silently launch it as a bold side branch. Return that direction to the human / `phase-planner`.

## Output

Return:

- the current scientific tension;
- the research angles covered;
- a compact Bold-Probe Research Brief with the serious candidates;
- rejected/deferred candidates and why;
- the strongest researched candidate(s) to send into `arena` / `design-experiment`;
- any phase-level or implementation boundary that must be resolved before the idea can become runnable.

Do not create or update CFD wiki pages merely because research was performed. Preserve reusable knowledge there only when a separate update is justified by the owning workflow.
