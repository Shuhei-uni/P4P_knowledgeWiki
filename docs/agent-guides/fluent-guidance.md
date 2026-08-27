# Fluent guidance

For a Fluent setup or how-to question:

1. Read the relevant reusable procedure in `CFD_wiki/wiki/guidance/`.
2. Read the selected Project setup when the question is case-specific.
3. Read the applicable focused skill and proven PyAnsys implementation when
   the task involves automation or a live session.
4. Inspect the live Fluent tree and read back critical values before relying on
   a version-sensitive Settings path.

Keep generic click paths and model explanations in `CFD_wiki/`. Keep current
project-specific numerical choices, parent identity, controlled changes, and
claim boundaries in `Project/`. Keep executable logic and machine evidence in
`PyAnsys/`.

For a long run, follow
[PyAnsys native run and autosave policy](../../PyAnsys/knowledge/fluent-settings/native_run_and_autosave.md):
Fluent owns initialization, iteration, and native autosave; Python may prepare,
reconnect, inspect, and analyse. Any narrow exception must be explicitly
documented by the selected experiment.

Do not infer geometry from a setup number, treat a filename as proof of
completion, or promote a diagnostic run to a validation claim without the
Project V&V gate.
