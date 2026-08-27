# P4P Knowledge Wiki

This repository is the compact working knowledge base for the P4P geothermal
separator CFD project. It has four active systems with clear ownership:

- `CFD_wiki/` — reusable CFD literature, source lookup, Fluent guidance, and
  cross-paper method synthesis.
- `Project/` — current project-specific scientific truth, selected experiments,
  evidence interpretation, and claim limits.
- `PyAnsys/` — executable Fluent automation, inspection, Python-supervised
  execution support, and machine-readable evidence checks.
- `.agents/skills/` — focused repository-local workflows for the active CFD, Fluent,
  evidence, and project-loop tasks.

The former project source vault is not part of the current checkout. The old
written project wiki, numbered setup/report tree, meeting-report folder, and
fixed subagent prompts were retired after their useful content was distilled
into `Project/`, `CFD_wiki/`, and `PyAnsys/`; Git history is their recovery path.

Start with:

- [`AGENTS.md`](AGENTS.md) for repository routing and safety rules.
- [`Project/index.md`](Project/index.md) for current project truth and the
  selected-experiment contract.
- [`CFD_wiki/wiki/index.md`](CFD_wiki/wiki/index.md) for reusable CFD
  knowledge and paper navigation.
- [`PyAnsys/README.md`](PyAnsys/README.md) for implementation and supervised
  Fluent execution workflow.
- [`.agents/skills/`](.agents/skills/) for the focused task-scoped repository
  workflows.

## Human-invoked skills to remember

Most skills are internal specialists and should be called by the scientific workflow when needed. The main skills the human should deliberately invoke are:

- `$phase-planner` — use for a scientific catch-up before a phase, after the autonomous loop stops, or whenever you want to reconstruct where the project stands and discuss the next phase-level direction.
- `$scientific-phase-loop` — use once the phase question, boundaries, and desired level of evidence are agreed. It autonomously designs and runs experiments, analyses results, revises hypotheses and assumptions, and continues until it can conclude the phase or reaches a genuine human boundary.
- `$workflow-surgeon` — use when the agent workflow itself is frustrating, repeatedly behaves badly, has a missing responsibility, stale rule, poor handoff, or bad default. It diagnoses the root cause with fresh reviewers and prefers the smallest surgical change over redesigning the skill system. It may also self-invoke when frustrated user feedback clearly points to an identifiable workflow failure.
- `$show-me-your-work` — optional audit/handoff tool when you specifically want a concise reconstruction of what an autonomous sequence did and where the supporting evidence lives.

Typical scientific flow:

```text
$phase-planner
    ↓
agree phase question / boundaries
    ↓
$scientific-phase-loop
    ↓
autonomous discovery or hypothesis-test cycles
    ↓
conclude phase / return to human
    ↓
$phase-planner
```

Workflow maintenance is separate from the scientific loop:

```text
human encounters workflow friction
    ↓
$workflow-surgeon
    ↓
diagnose root cause
    ↓
smallest justified skill / handoff / rule edit
```

The human normally does not need to invoke experiment-design, setup, Fluent execution, numerical-analysis, interpretation, next-action, or closure skills individually; the loop should call them as required. Inside the loop, long Fluent runs default to a Python/PyFluent runner supervised by an agent. TUI-driven or Fluent-journal execution requires explicit human approval for that run.

## Current execution proof

The latest selected experiment is the 03A-Q01 S4-01 qualification. It loaded
the verified 33,000-iteration parent and issued exactly one Fluent-native
`/solve/iterate 50` command. The Project packet records the endpoint,
transcript, residual history, physical histories, hashes, and limitations. This
is historical execution evidence, not the default execution mechanism for new
autonomous-loop runs.

- [`03A-Q01 setup`](Project/experiments/phase-05-full-geometry-v2/full-geometry-03a-mixture-08b-parity-baseline/q01-s4-01-50-iteration-qualification/setup.md)
- [`03A-Q01 results`](Project/experiments/phase-05-full-geometry-v2/full-geometry-03a-mixture-08b-parity-baseline/q01-s4-01-50-iteration-qualification/results.md)
- [`03A tracer index`](Project/experiments/phase-05-full-geometry-v2/full-geometry-03a-mixture-08b-parity-baseline/index.md)
- [`Q01 runner`](PyAnsys/scripts/setup/run_03a_q01_s4_01_50.py)

## Source and generated files

The original project source inputs were removed from this checkout at the
user's request; their exact committed versions remain recoverable from Git
history. Other source material remains local and intentionally outside normal
GitHub storage, including the CFD paper PDFs under `CFD_wiki/raw/`, the Fluent
manual under `CFD_wiki/guide/`, the local `PyAnsys/.venv/`, and generated run
output. The maintained extracted pages identify the source paths and
uncertainty labels needed for later rechecks.

## Rebuild and verification habits

1. Read `AGENTS.md` and then the local guide for any subsystem you will change.
2. Begin project work at `Project/index.md`; follow only the relevant current
   experiment packet and evidence record.
3. Use `CFD_wiki/paper_lookup/index.md` before reading a long source paper.
4. For Fluent automation, read the relevant focused skill and
   `PyAnsys/knowledge/fluent-settings/native_run_and_autosave.md`.
5. For autonomous-loop execution, use a Python/PyFluent runner supervised by
   an agent through `supervise-fluent-run`; do not switch to TUI or a Fluent
   journal without explicit human approval.
6. When improving the agent workflow, prefer `$workflow-surgeon` so changes are
   root-cause-driven and surgical rather than broad rewrites.
7. Run the repository’s targeted tests and stale-path check after cross-system
   edits.

Do not commit raw papers, the large Fluent manual, local environments, Python
cache files, or generated run output unless the storage strategy is deliberately
changed.
