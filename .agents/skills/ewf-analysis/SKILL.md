---
name: ewf-analysis
description: Assess Eulerian Wall Film evidence for relevant active walls and mechanisms, using MCP discovery and scoped domain reductions with explicit completeness.
---

# EWF analysis

Run only when EWF is active and relevant to the setup question. Follow
[MCP integration](../fluent-live-inspection/mcp-integration.md).

1. Through MCP named-object discovery, `describe_path` and `get_state`, confirm
   film walls, mechanisms, coupling, phase mapping and exact checkpoint identity.
   Use `list_fields` to discover available quantities, not infer values.
2. Ground the required scoped report/integral/export paths. Validate and execute
   generated queries through MCP. Model activation or a diagnostic solve is a
   separately authorized implementation step, not analysis convenience.
3. Where upstream lacks the exact reduction or complete evidence semantics,
   retain reviewed helpers: `ewf_core.py`, `ewf_audit.py`, `ewf_flux.py`,
   `ewf_reports.py`, `ewf_report_specs.py`, `ewf_diagnostics.py` under
   `PyAnsys/src/pyansys_fluent/`, and
   `PyAnsys/scripts/inspection/run_ewf_dpm_diagnostics.py`. Name the capability
   gap and inspect the worker's scope, side effects and cleanup before use.
4. Preserve raw and reduced evidence, actual wall/surface/domain scope, units,
   sign convention and extraction method. Distinguish inventory/cumulative
   quantities (`kg`) from rates (`kg/s`), and local/max/area-weighted reductions.
5. Report missing/partial fields and histories explicitly. A missing field does
   not establish zero or an inactive mechanism. A final snapshot cannot prove
   time-integrated closure without the required histories.

Return measured evidence and limitations to the numerical/scientific analysis.
A generic MCP summary is not a complete EWF balance. Any TUI/journal use remains
subject to the shared exception contract; preserve the session and source pair.
