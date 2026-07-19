---
name: setup-report
description: "Use when working with Setups setup-instance records: searching setup lineage, creating or updating concrete Fluent case definitions, parent/child variants, ordered setup history, setup naming, report-facing boundary-condition snapshots, or Setups/order-dictionary.md."
---

# Setup Report

## Core Rule

Use `Setups/` for concrete setup-instance documents: named case definitions, parent/child setup variants, ordered case history, and report-facing snapshots with boundary conditions, assumptions, and calculations.

Do not use `Setups/` for reusable CFD methods, generic Fluent guidance, literature extraction, day-to-day project status, or PyAnsys implementation code.

Before editing setup reports, read:

1. `AGENTS.md` at the repository root for cross-system routing.
2. `Setups/order-dictionary.md` for ordering, naming, and current lineage.
3. The parent and child setup reports directly related to the requested branch.
4. `ResearchProject_wiki/wiki/project/roadmap.md` when active project direction matters.

## Search Workflow

Start with `Setups/order-dictionary.md`. Use it to identify:

- the active branch;
- parent and child reports;
- whether a report is baseline, diagnostic, superseded, parked, or planned;
- the stable filename to use.

Then open only the relevant setup reports. Use `rg` for branch-specific searches:

```bash
rg -n "08b|DPM|velocity inlet|mass-flow|brine outlet|parent|child" "Setups"
```

Current high-level interpretation from the dictionary:

- `08c-purnanto-parity-inlet-velocity-sensitivity.md` and `09c-dpm-ewf-wall-film-reentrainment.md` are the active branches.
- `04`, `07`, `08b`, `09a`, and `09b` are past reported because they contain actual flux-efficiency and/or DPM trajectory/fate numerics.
- `08a` and the remaining older definitions are archived until numerical evidence is recorded.

Reported-status rule:

- classify a setup as `reported` only when actual numerical flux-efficiency/carryover values or numerical DPM fate/trajectory counts exist;
- planned values, setup targets, and placeholder result tables do not qualify;
- keep the evidence-use label explicit because reported does not imply validated.

Always verify this against `Setups/order-dictionary.md` before answering because the dictionary is the controlling map.

## Creation And Naming Workflow

Create or update a setup report when the request involves:

- a new setup branch or variant;
- concrete Fluent boundary conditions for a named case;
- report-facing setup snapshots for a run or planned run;
- setup cleanup, ordering, naming, or parent/child lineage reconstruction.

When creating or renaming:

1. Preserve assigned numbers.
2. Add a new number or branch suffix such as `08`, `08a`, or `08b` rather than renaming old reports.
3. Avoid filename status words like `current`, `latest`, or `final`.
4. Use pattern `NN[-branch]-short-description.md`.
5. Update `Setups/order-dictionary.md` if ordering, branch identity, or naming changed.
6. Update cross-links in setup reports and relevant wiki indexes.

## Content Workflow

Keep setup reports concrete. Include:

- setup identity and parent/child lineage;
- geometry and mesh context;
- boundary conditions and values with units;
- material, physics, solver, initialization, and convergence assumptions;
- calculation notes;
- report-facing status and known limitations;
- links to `CFD_wiki` for reusable method logic and to `ResearchProject_wiki` for project interpretation.

If automation defines or changes the branch, sync the setup identity from `PyAnsys/` into the setup report and leave executable details in `PyAnsys/`.
