---
name: dpm-analysis
description: Extract and assess relevant DPM tracking, fate and mass-transfer evidence; discover live injections through MCP and retain complete transcript parsing.
---

# DPM analysis

Run only when the setup question or requested evidence needs DPM. Follow
[MCP integration](../fluent-live-inspection/mcp-integration.md).

## Discover before tracking

Use MCP named-object tools and scoped `describe_path`/`get_state` to verify
active injections, particle types, source surfaces, represented flow, model
coupling and exact case identity. Existing injection objects alone do not prove
active mass loading or scientific relevance.

Tracking is an operation, not read-only discovery. Require the approved diagnostic
scope and tracking budget; avoid an unrequested all-injection retrack or change
to the carrier solution. Ground any generated tracking/report commands through
MCP, validate and execute under the existing session ownership.

## Preserve complete domain evidence

Retain these helpers for semantics not supplied by a generic MCP report:

- `PyAnsys/src/pyansys_fluent/dpm_reports.py`;
- `PyAnsys/src/pyansys_fluent/dpm_transcript.py`;
- `PyAnsys/scripts/inspection/run_dpm_particle_tracks.py`.

Review the exact worker before use and name the missing capability. Any TUI or
journal path still needs the shared contract's explicit run approval; an old
worker is not permission to bypass MCP.

For every selected injection require actual tracked count, a mass-transfer
summary, parsed fate/zone rows and command/transcript completion evidence.
Preserve raw/partial output promptly. A quiet interval alone does not establish
completion; a missing row is not zero. Keep represented/net mass, units,
particle scope and available timing evidence.

Distinguish event/mechanism counters from terminal particle fates so splash or
film-absorption events are not double-counted with later terminal sinks.
Return linked raw and parsed evidence, completeness and claim limits. A complete
DPM report can still be irrelevant to the scientific question; interpretation
belongs to the caller.
