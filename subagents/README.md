# Transitional subagent briefs

These files are retained compatibility briefs from the earlier migration
stages. They are not a second routing or orchestration framework and should be
removed during the explicit #19 cleanup only after the fresh-agent test and
replacement review pass.

For current work, route directly to the smallest relevant skill:

- `project-loop` for current scientific review, experiment proposals, selected
  `Project/experiments/` records, and findings;
- `fluent-implementation` for selected setup execution;
- `post-simulation-analysis` or a focused specialist for evidence extraction;
- `cfd-wiki` for reusable/external CFD knowledge.

Use a brief only when a bounded delegation is genuinely useful or when an
explicit historical repair requires its retained scope. The main agent remains
responsible for reconciling outputs, preserving ownership boundaries, and
removing duplication.

## Retained briefs

- `cfd-subagent.md` — historical reusable-CFD delegation scope.
- `research-subagent.md` — transitional current-project/provenance scope.
- `setup-subagent.md` — transitional selected-experiment/legacy-setup scope.
