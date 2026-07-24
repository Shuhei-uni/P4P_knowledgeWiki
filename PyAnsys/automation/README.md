# Git-Synchronized Fluent Build Requests

This directory is the small Git inbox/outbox between the planning agent and
the local Fluent-PC runner.

- `setup-plans/*.md` are Markdown plans with strict YAML front matter.
- The agent commits one case-specific Python build script for each plan. The
  plan pins that script's repository path and SHA-256.
- `setup-results/*.json` are compact evidence records committed after a run.
- Case/data files, server-info files, transcripts, and runtime directories stay
  on the Fluent PC and are never committed.

Markdown is not a Fluent recipe interpreter. The build script is where the
agent writes the step-by-step, live-proven TUI/PyFluent sequence to construct a
case. The local runner only validates the pinned inputs and script, executes it
on the Fluent PC, and returns evidence.

## 09c vertical slice

`setup-plans/09c-two-way-dpm-interaction.md` is intentionally pinned to a
parent SHA-256 and a generated build-script SHA-256. First run the plan runner
with `--capture-parent-identity`, commit the resulting JSON, and have the agent
insert the parent hash and the hash of its reviewed build script into the plan.
Only that exact script may execute the case build.

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

Commit only the resulting JSON. After the agent replaces both placeholders and
you pull that follow-up plan commit, execute the same command without
`--capture-parent-identity`.

The runner invokes the pinned script with `--server-id`, `--source-case`,
`--output-case`, and `--summary-json`. The script—not Markdown—connects to
local Fluent and performs its step-by-step TUI/PyFluent build. The result JSON
then records the script's readbacks and new scratch-case path.
