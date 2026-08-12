---
name: setup-report
description: "Manage Setups setup-instance records and reports: inspect lineage, decide whether a concrete Fluent setup belongs in active, future, past reported, or past archived, decide whether a numerical report should be created or updated, and handle case definitions, variants, ordering, naming, and boundary-condition snapshots. Use for setup lifecycle/status requests, proposed new setup branches, setup cleanup, result-report decisions, or Setups/order-dictionary.md. Always recommend the action first and obtain the user's final approval before creating, moving, renaming, archiving, promoting, or otherwise editing setup records or reports."
---

# Setup Report

## Core Rule

Use `Setups/` for concrete setup-instance documents: named case definitions, parent/child setup variants, ordered case history, and report-facing snapshots with boundary conditions, assumptions, and calculations.

Do not use `Setups/` for reusable CFD methods, generic Fluent guidance, literature extraction, day-to-day project status, or PyAnsys implementation code.

Before assessing or editing setup records and reports, read:

1. `AGENTS.md` at the repository root for cross-system routing.
2. `Setups/order-dictionary.md` for ordering, naming, and current lineage.
3. The parent and child setup records directly related to the requested branch and any linked reports relevant to the decision.
4. `ResearchProject_wiki/wiki/project/roadmap.md` when active project direction matters.

## Final-Call Gate

Treat the user's first request as a request to assess and recommend, even when it is phrased as "create," "move," "archive," or "make a report."

Before any setup-management write:

1. Inspect the relevant setup record, lineage, indexes, roadmap, and available numerical evidence.
2. Decide separately:
   - the recommended lifecycle: `active`, `future`, `reported`, `archived`, or no lifecycle change;
   - the recommended report action: create, update, no report, or defer for missing evidence.
3. Present the recommendation, evidence, uncertainty, and exact files or links that would change.
4. Ask the user for the final call: approve the recommendation, choose an alternative, or make no setup-report changes.
5. Make no lifecycle, report, filename, ordering, index, or cross-link edits until the user explicitly confirms the proposed action.

Read-only searches and status explanations do not require confirmation when no mutation is proposed. Once the user confirms the specific recommendation, execute it without asking again unless new evidence materially changes the scope.

Do not treat broad permission, a roadmap idea, or an earlier unrelated approval as the final call for a newly inferred setup or report.

## Search Workflow

Start with `Setups/order-dictionary.md`. Use it to identify:

- the active branch;
- parent and child setup records;
- whether a setup is baseline, diagnostic, superseded, parked, or planned;
- the stable filename to use.

Then open only the relevant setup records and linked reports. Use `rg` for branch-specific searches:

```bash
rg -n "08b|DPM|velocity inlet|mass-flow|brine outlet|parent|child" "Setups"
```

Always verify this against `Setups/order-dictionary.md` before answering because the dictionary is the controlling map.

## Lifecycle And Report Decision

Make lifecycle and report recommendations independently. A setup record defines a case; a report documents numerical results from that case.

Recommend lifecycle using the current evidence:

| Recommendation | Use when |
|---|---|
| `active` | The setup is currently being run or actively changed. It may have a preliminary report and still remain active. |
| `future` | The branch is intentionally planned for later execution, has a useful parent and controlled-change rationale, and is not started. Do not create speculative future records without approval. |
| `reported` | The setup is no longer active and has qualifying numerical flux/efficiency/carryover results or numerical DPM fate/trajectory counts. State whether the evidence is diagnostic, incomplete, non-converged, inherited, or claim-ready. |
| `archived` | The setup is historical, superseded, invalid, parked, or setup-only; it is no longer active and lacks the evidence required for `reported`. |
| No change | The prompt supplies no evidence that the current lifecycle is wrong, or it asks only for reusable guidance, project interpretation, or automation work. |

Recommend a report action using these rules:

- Create or update a report only when actual numerical findings exist and can be tied to one concrete setup.
- Allow preliminary reports for active setups when real values exist; label incomplete convergence, missing balances, inherited evidence, and other limitations.
- Do not create a report from planned values, setup targets, screenshots without extracted numbers, or placeholder tables.
- Defer the report and list the missing evidence when the report contract cannot yet be satisfied.
- Do not duplicate the setup definition in the report. Link back to the authoritative setup record.

Recommend no new setup record when the request is generic CFD guidance, a project-status note, a PyAnsys-only implementation detail, a speculative idea the user has not accepted, or a branch already represented by an existing record.

Before recommending a state change, reconcile contradictions among the file location, its `Lifecycle` field, lifecycle indexes, `Setups/order-dictionary.md`, the roadmap, and numerical reports. Surface unresolved contradictions instead of silently choosing one source.

Use this compact approval brief:

```text
Setup: <ID/name or proposed branch>
Current evidence: <what the repository and prompt establish>
Recommended lifecycle: <active|future|reported|archived|no change>
Recommended report action: <create|update|none|defer>
Why: <short evidence-based rationale>
Files affected: <exact paths, including indexes/order/cross-links>
Uncertainty or missing evidence: <items or none>
Final call: Shall I apply this recommendation, choose another state/report action, or leave the setup records unchanged?
```

## Creation And Naming Workflow

After the user gives the final call, create or update a setup record when the approved action involves:

- a new setup branch or variant;
- concrete Fluent boundary conditions for a named case;
- report-facing setup snapshots for a run or planned run;
- setup cleanup, ordering, naming, or parent/child lineage reconstruction.

When creating or renaming setup records:

1. Preserve assigned numbers.
2. Add a new number or branch suffix such as `08`, `08a`, or `08b` rather than renaming old setup records.
3. Avoid filename status words like `current`, `latest`, or `final`.
4. Use pattern `NN[-branch]-short-description.md`.
5. Update `Setups/order-dictionary.md` if ordering, branch identity, or naming changed.
6. Update cross-links in setup records, linked reports, and relevant wiki indexes.

## Lifecycle Management Workflow

After approval:

1. Keep the stable setup ID and filename.
2. Move the setup record to exactly one lifecycle directory:
   - `Setups/active/`
   - `Setups/future/`
   - `Setups/past/reported/`
   - `Setups/past/archived/`
3. Update the record's `Lifecycle`, evidence-use label, outcome, parent/children, and linked-report fields.
4. Remove the old lifecycle-index entry and add the new one.
5. Update `Setups/order-dictionary.md` with the current path/state while preserving sequence and lineage.
6. Repair affected relative links in setup records, reports, and relevant wiki pages.
7. Keep detailed numerical findings under `Setups/reports/<setup-id>/`; moving a setup record must not move or duplicate its report directory.
8. Verify that the record appears in only one lifecycle view and that every report links back to exactly one setup definition.

For an approved new report, start from `Setups/templates/results-report-template.md`. For an approved new setup record, use the closest relevant template under `Setups/templates/` and inherit only verified values from the parent.

## Content Workflow

Keep setup records concrete. Include:

- setup identity and parent/child lineage;
- case identity from explicit or independently observed case evidence; never
  infer it from a Fluent connection/server ID;
- geometry and mesh context;
- boundary conditions and values with units;
- material, physics, solver, initialization, and convergence assumptions;
- calculation notes;
- report-facing status and known limitations;
- links to `CFD_wiki` for reusable method logic and to `ResearchProject_wiki` for project interpretation.

If automation defines or changes the branch, sync the setup identity from `PyAnsys/` into the setup record and leave executable details in `PyAnsys/`.
