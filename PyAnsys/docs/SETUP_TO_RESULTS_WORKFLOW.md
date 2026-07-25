# Setup Markdown to Results

This is the complete laptop-controlled workflow. The Markdown setup is an
agent-readable scientific plan, not a host-executed recipe or setup DSL.

## Runtime state

Choose an untracked laptop directory for each job:

```text
PyAnsys/output/laptop-workflows/010v2/
├── workflow.json
├── ledger.json
├── analysis_manifest.json
└── results/
    ├── result_manifest.json
    └── result-summary.md
```

The setup plan remains in its normal repository location. The workflow records
its SHA-256 and fails closed if the plan changes during execution.

## 1. Register the setup plan

```bash
.venv/bin/python scripts/orchestration/laptop_workflow.py \
  --workspace output/laptop-workflows/010v2 \
  init \
  --job-id 010v2-build \
  --setup-plan ../Setups/active/010v2-example.md \
  --generation 14 \
  --analysis-task case_audit \
  --analysis-task residuals \
  --analysis-task carrier_flux \
  --analysis-task dpm_fates
```

This creates state only. It does not parse the Markdown or contact Fluent.

## 2. Build the case through direct agent control

For every operation, the laptop agent:

1. reads the next requirement from the Markdown;
2. inspects the live Fluent state;
3. researches the Settings API or TUI path;
4. records the step start;
5. applies one targeted operation over direct gRPC;
6. reads the setting back;
7. records completion only when the readback proves success; and
8. saves and accepts a `.cas.h5` at meaningful boundaries.

Example ledger transitions:

```bash
WORKFLOW=output/laptop-workflows/010v2

.venv/bin/python scripts/orchestration/laptop_workflow.py \
  --workspace "$WORKFLOW" step-start load_parent_case

# The agent directly loads and verifies the parent case through PyFluent.

.venv/bin/python scripts/orchestration/laptop_workflow.py \
  --workspace "$WORKFLOW" step-complete load_parent_case

.venv/bin/python scripts/orchestration/laptop_workflow.py \
  --workspace "$WORKFLOW" step-start enable_dpm --safe-to-retry

# The agent enables DPM, reacquires handles, and reads the state back.

.venv/bin/python scripts/orchestration/laptop_workflow.py \
  --workspace "$WORKFLOW" step-complete enable_dpm
```

After a complete setup audit:

```bash
.venv/bin/python scripts/orchestration/laptop_workflow.py \
  --workspace "$WORKFLOW" \
  accept-case 'C:\CFD\cases\010v2-verified.cas.h5'

.venv/bin/python scripts/orchestration/laptop_workflow.py \
  --workspace "$WORKFLOW" case-ready
```

`accept-case` means the agent has already verified the saved case. It is not
merely a record that a write command returned.

If Fluent dies during direct case construction, preserve the interrupted step:

```bash
.venv/bin/python scripts/orchestration/laptop_workflow.py \
  --workspace "$WORKFLOW" setup-connection-lost --generation 14
```

After the watchdog publishes generation `15`, the agent reconnects, loads the
last accepted setup case, inspects it against the last completed step, and then
records recovery:

```bash
.venv/bin/python scripts/orchestration/laptop_workflow.py \
  --workspace "$WORKFLOW" setup-recovered --generation 15
```

The ledger keeps the interrupted step and its `safe_to_retry` flag. The agent
retries it only when that flag and the restored-state readback justify doing so.
Use `human-review` instead when the restored setup cannot be proved.

## 3. Submit the deterministic run

Create a strict request:

```json
{
  "schema_version": 2,
  "job_id": "010v2-run-1500",
  "expected_generation": 14,
  "mode": "initialize",
  "source_case": "C:\\CFD\\cases\\010v2-verified.cas.h5",
  "source_data": null,
  "initialization_tui": [
    "/solve/initialize/hyb-initialization"
  ],
  "target_total_iterations": 1500,
  "completed_iterations": 0,
  "checkpoint_interval": 250,
  "report_interval": 25,
  "output_directory": "C:\\CFD\\runs\\010v2-run-1500",
  "overwrite": false
}
```

Submit through the laptop workflow so the source case and generation are
checked against both the ledger and a fresh `latest_connection.json`:

```bash
.venv/bin/python scripts/orchestration/laptop_workflow.py \
  --workspace "$WORKFLOW" \
  submit request-010v2-run-1500.json \
  --bridge-dir /private/path/to/FluentBridge
```

The Fluent-PC run worker loads the explicit case, replays the agent-verified
`initialization_tui` strings exactly once and in order, runs in chunks, writes
verified recovery pairs, and produces a secret-free receipt containing the
command/output log. It does not interpret the initialization sequence or
decide what to run next. If PyFluent raises while replaying a command, the
worker stops before iteration. Fluent can also return a TUI error as ordinary
text, so the verified sequence should include any required readback/report
command and that output must be reviewed in the receipt.

## 4. Ingest and verify a completed run

```bash
.venv/bin/python scripts/orchestration/laptop_workflow.py \
  --workspace "$WORKFLOW" \
  ingest-receipt /private/path/to/FluentBridge/run_receipts/010v2-run-1500.json
```

The final pair is now `pending`; it is not automatically accepted. The agent
loads the case/data pair in Fluent, checks case identity, iteration state,
models, boundaries, and solution availability, then records that proof:

```bash
.venv/bin/python scripts/orchestration/laptop_workflow.py \
  --workspace "$WORKFLOW" \
  verify-checkpoint \
  --case-path 'C:\CFD\runs\010v2-run-1500\010v2-verified_1500.cas.h5' \
  --data-path 'C:\CFD\runs\010v2-run-1500\010v2-verified_1500.dat.h5' \
  --generation 14
```

## 5. Recover after a Fluent crash

An interrupted receipt records the last file-verified pair but does not accept
it. After the watchdog publishes a newer generation, the laptop agent:

1. reconnects using the new `latest_connection.json`;
2. discards all Settings API handles from the old generation;
3. loads the pending case/data pair;
4. inspects the restored state against the last completed setup/run step; and
5. runs `verify-checkpoint` only if the state is proven.

For an interrupted generation `14`, verification must occur on generation
`15` or later. The workflow then permits a new request with:

```json
{
  "schema_version": 2,
  "job_id": "010v2-run-1500-resume-1",
  "expected_generation": 15,
  "mode": "resume",
  "source_case": "C:\\CFD\\runs\\010v2-run-1500\\checkpoint-00001000.cas.h5",
  "source_data": "C:\\CFD\\runs\\010v2-run-1500\\checkpoint-00001000.dat.h5",
  "initialization_tui": null,
  "target_total_iterations": 1500,
  "completed_iterations": 1000,
  "checkpoint_interval": 250,
  "report_interval": 25,
  "output_directory": "C:\\CFD\\runs\\010v2-run-1500-resume-1",
  "overwrite": false
}
```

The coordinator rejects a different pair, iteration, or generation. Resume
loads both files and never initializes.

If the restored state cannot be proved, stop the workflow explicitly:

```bash
.venv/bin/python scripts/orchestration/laptop_workflow.py \
  --workspace "$WORKFLOW" human-review \
  --generation 15 \
  --reason "Restored model state does not match the last verified step."
```

This leaves the checkpoint unaccepted and prevents a resume request.

## 6. Run and record analysis

The agent loads the accepted final pair and runs the appropriate existing
inspection tools, for example:

```bash
.venv/bin/python scripts/inspection/post_simulation_analysis.py \
  --load-case-data \
  --case-file 'C:\CFD\runs\010v2\final.cas.h5' \
  --data-file 'C:\CFD\runs\010v2\final.dat.h5' \
  --check all \
  --run-label 010v2 \
  --output-dir output/laptop-workflows/010v2/analysis
```

Each explicitly planned analysis item is tracked separately:

```bash
.venv/bin/python scripts/orchestration/laptop_workflow.py \
  --workspace "$WORKFLOW" analysis-start carrier_flux

.venv/bin/python scripts/orchestration/laptop_workflow.py \
  --workspace "$WORKFLOW" analysis-complete carrier_flux \
  --artifact output/laptop-workflows/010v2/analysis/010v2-flux-check.json \
  --notes "Read from the agent-verified final case/data pair."
```

Interrupted or failed analysis can be recorded without losing completed work:

```bash
.venv/bin/python scripts/orchestration/laptop_workflow.py \
  --workspace "$WORKFLOW" analysis-mark dpm_fates \
  --status interrupted \
  --notes "Fluent generation changed during injection 03."
```

## 7. Finalize the result package

After every explicit analysis task is complete:

```bash
.venv/bin/python scripts/orchestration/laptop_workflow.py \
  --workspace "$WORKFLOW" finalize
```

The result manifest contains:

- setup-plan path and SHA-256;
- final agent-verified case/data checkpoint;
- run-receipt history;
- completed iteration identity;
- every analysis task and status; and
- local artifact paths, sizes, and SHA-256 hashes.

The manifest records provenance and completion. Scientific interpretation still
belongs in the appropriate project observation, V&V record, or report.
