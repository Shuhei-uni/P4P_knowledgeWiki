---
name: fluent-analyze-results
description: Analyze an existing Fluent case/data pair through laptop-controlled PyFluent, TUI, and reusable inspection helpers. Use when Codex must adapt analysis commands to the live case, reuse previously successful commands, recover from Fluent restarts, and produce verified result evidence without delegating interpretation to the Fluent computer.
---

# Fluent Analyze Results

Keep analysis selection, command choice, and interpretation on the laptop
agent. Use local Python/PyFluent over gRPC; do not delegate dynamic analysis to
a Fluent-PC worker.

## Process

1. Read the setup Markdown and identify the exact case/data pair.
2. Inspect past successful analysis commands, similar cases, and existing
   laptop-side helpers before inventing new commands.
3. Connect to Fluent, load the pair, and verify its identity and solution
   state.
4. Decide which analyses apply from the setup and live state. Typical areas
   include residuals, fluxes, DPM, and EWF, but do not force analyses that do
   not apply.
5. Run one focused command or helper at a time.
6. Inspect the returned output, units, surfaces, phases, injections, and other
   scope needed to interpret the value.
7. Adapt and retry until the required evidence is verified.
8. Preserve successful raw outputs and a concise analysis summary.

Do not change solver physics merely to expose a result. Do not treat missing
evidence as zero.

## Retry and reconnect

If an analysis command fails while Fluent remains healthy, inspect the response
and try another supported path.

If Fluent or gRPC fails:

1. preserve completed analysis outputs;
2. wait for a newer healthy generation—restarting Fluent may take several
   minutes;
3. poll patiently and keep the user updated;
4. reconnect and discard stale handles;
5. reload the exact case/data pair and verify it;
6. continue only the unfinished analysis.

Do not infer results from partial output.

## Evidence and completion

Keep successful commands when they are reusable, plus verified values, units,
scope, raw artifacts, and unresolved limitations. A detailed record of failed
commands is not required.

Hand the verified evidence to `$fluent-write-results-report`.
