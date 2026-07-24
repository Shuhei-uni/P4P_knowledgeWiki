# Git-Synchronized Setup Plans

This directory is the small Git inbox/outbox between the planning agent and
the local Fluent-PC runner.

- `setup-plans/*.md` are Markdown plans with strict YAML front matter.
- `setup-results/*.json` are compact evidence records committed after a run.
- Case/data files, server-info files, transcripts, and runtime directories stay
  on the Fluent PC and are never committed.

## First vertical slice

`setup-plans/09c-two-way-dpm-interaction.md` is intentionally pinned to a
parent SHA-256. First run the plan runner with `--capture-parent-identity`,
commit the resulting JSON, and have the agent insert that SHA-256 into the
plan. Only the pinned plan may execute the Fluent mutation.

On the Fluent PC, after pulling the plan commit:

```powershell
$Plan = ".\automation\setup-plans\09c-two-way-dpm-interaction.md"
$Result = ".\automation\setup-results\09c-parent-identity.json"

& ".\.venv\Scripts\python.exe" `
  ".\scripts\orchestration\run_markdown_setup_plan.py" `
  --plan $Plan `
  --result-json $Result `
  --capture-parent-identity
```

Commit only the resulting JSON. After the agent replaces the placeholder hash
and you pull that follow-up plan commit, execute the same command without
`--capture-parent-identity`. The result JSON then records the Fluent readbacks
and the new scratch case path.
