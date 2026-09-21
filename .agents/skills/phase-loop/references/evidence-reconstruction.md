# Evidence reconstruction

Use this branch after an interruption, long autonomous sequence, or conflicting
records when the next scientific decision needs a compact evidence trail.

## Reconstruct from durable owners

Read the active `CONTEXT.md` and `phase-state.yaml`, then only the setup/result
records and artifacts on the current frontier. Use Git history to recover a
decision only when the active record does not explain why a route was chosen or
abandoned. Prefer artifact manifests, saved case/data identity, report histories,
and figures over remembered chat chronology.

## Produce a decision trail

For each material turn, state:

| Decision | Evidence that caused it | What changed | Durable location |
| --- | --- | --- | --- |
| <selected/repaired/rejected route> | <specific observation/artifact> | <scope, assumption, or next experiment> | <Project/artifact path> |

Include contradictions and course changes explicitly: what prior expectation was
revised, which evidence forced the revision, and what uncertainty remains. Do
not list every command or commit; the purpose is to make the next experiment
intelligible and auditable.

End with the current question, strongest supported observation, untested
alternative, usable parents/artifacts, and the smallest next in-scope action.
