# Delegation

Use a bounded read-only subagent when it can answer a concrete uncertainty
faster or provide an independent review. The main agent remains responsible
for scope, evidence reconciliation, edits, cross-links, tests, and the final
decision.

## Brief format

Every handoff should state:

- `GOAL`: one review, inspection, or analysis question;
- `SCOPE`: exact files, paths, or external artifacts;
- `CONTEXT`: the current Project decision and relevant uncertainty;
- `CONSTRAINTS`: read-only or explicitly bounded write scope, never `raw/`;
- `EVIDENCE`: what the agent must inspect;
- `RETURN`: material findings with file/path, evidence, implication, and the
  smallest recommended action;
- `DONE WHEN`: the concrete stopping condition.

Use a fresh reviewer after a meaningful cross-system or cleanup change. Do not
maintain fixed prompt files or duplicate architecture instructions in the
repository.
