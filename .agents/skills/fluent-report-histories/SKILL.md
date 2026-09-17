---
name: fluent-report-histories
description: Recover and analyse Fluent Report Plot or Report File histories using MCP for live configuration discovery and retained parsers for complete recorded samples.
---

# Fluent report histories

Follow [MCP integration](../fluent-live-inspection/mcp-integration.md). Recover
recorded samples, not a current-value summary presented as a history.

1. Resolve exact run identity and canonical `run-paths.yaml`. Through MCP,
   discover/read the relevant report definitions, Report Files and destinations.
   Confirm phase/zone scope, units, definitions and native iteration/time basis.
2. Locate the actual recorded files. A relative `.out` path need not be beside
   the case/data pair; do not change Fluent's working directory to make it fit.
3. Use the reviewed `PyAnsys/scripts/inspection/extract_report_plot_histories.py`
   where complete file retrieval/parsing is not provided by MCP. Inspect its
   current arguments and file-read behaviour, pass the verified remote directory,
   and scope it to the required reports. Record this capability gap and helper.
4. Preserve source files/transcripts, native coordinates, point counts, units,
   sign convention, definition names and parser errors with the extracted data.
5. Hand the complete/partial/unavailable history to numerical analysis. If it
   was never recorded, report `requires rerun`; do not rerun or redefine reports
   inside this extraction task.

`solver_status`, `summarize_setup` and `simulation_report` do not replace full
histories. Empty buffers/files are not zero. Keep serialization failures visible;
repair a parser only against actual source evidence. Creation or modification of
instrumentation belongs to approved implementation, via validated MCP execution
and a smoke test before the planned solve.
