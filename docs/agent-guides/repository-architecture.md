# Repository architecture

The repository has four active ownership domains:

- `CFD_wiki/` owns reusable CFD literature extraction, source lookup,
  reconstruction patterns, generic Fluent guidance, and cross-paper synthesis.
- `Project/` owns current project-specific scientific truth, selected
  experiments, findings, evidence interpretation, and claim limits.
- `PyAnsys/` owns executable Fluent setup/inspection/run support, extracted
  machine evidence, and reusable implementation knowledge.
- `skills/` owns focused procedural workflows that route work through those
  systems. Skills do not replace the scientific or implementation authority.

The former project source vault is absent from the current checkout. It is not
an active documentation owner; its exact inputs and the former written project
wiki, numbered setup/report tree, meeting-report folder, and fixed subagent
prompts are recoverable from Git history after their useful content was
migrated.

## Routing map

```text
current question / selected result
    -> Project/
generic CFD or literature evidence
    -> CFD_wiki/
Fluent implementation, inspection, native run, or machine evidence
    -> PyAnsys/
repeatable task procedure
    -> skills/
```

## Project records

The default entry point is [Project/index.md](../../Project/index.md).
Selected experiments live together under
`Project/experiments/<campaign>/<experiment>/`, normally with `setup.md` and
`results.md`. Historical records may keep their original status and uncertainty
labels, but the Project copy is the current navigation and interpretation
surface.

Do not turn `Project/` into a raw transcript or a second automation tree.
Link to focused PyAnsys evidence and keep only the decision-relevant summary.

## PyAnsys records

Use `PyAnsys/README.md` and the applicable focused skill to choose the smallest
proven script. Durable cross-case implementation rules belong in
`PyAnsys/knowledge/`; run-specific output belongs in ignored `PyAnsys/output/`
or on the Fluent host. Fluent-native iteration and autosave remain solver-owned.

## Recovery and cleanup

Deleted nonraw historical files remain recoverable through Git. Do not create a
large `legacy/` compatibility tree or restore old navigation merely because an
old path appears in a historical note. Preserve a small, unique artifact only
when it carries evidence that cannot be reconstructed from Project, CFD_wiki,
PyAnsys code, or Git history.
