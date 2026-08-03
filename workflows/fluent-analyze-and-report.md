# Fluent Analyze and Report Workflow

This is a workflow, not a skill. It calls:

1. `$fluent-analyze-results`
2. `$fluent-write-results-report`

## Block 1: analyze

Read `../skills/fluent-analyze-results/SKILL.md` and use
`$fluent-analyze-results`.

The laptop agent chooses and adapts analysis commands over gRPC. Pass verified
values, units, scope, raw artifacts, reusable successful commands, and
limitations to the next block.

## Block 2: report

Read `../skills/fluent-write-results-report/SKILL.md` and use
`$fluent-write-results-report`.

If the report needs missing evidence, return only that gap to Block 1. Obtain
the repository's required final approval before writing the setup report.

## Shared recovery rule

For a healthy-session command error, adjust and retry. For Fluent/gRPC loss,
preserve completed outputs, wait patiently for a newer healthy generation,
reconnect, reload and verify the exact case/data pair, and continue unfinished
analysis. Restart may take several minutes.

Return the results report, its evidence paths, and unresolved questions.
