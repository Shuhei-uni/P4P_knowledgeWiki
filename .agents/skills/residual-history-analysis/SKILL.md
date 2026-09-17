---
name: residual-history-analysis
description: Extract, stitch, and plot complete Fluent residual histories with native coordinates; use MCP for live state and retained history parsers where needed.
---

# Residual history analysis

Use [MCP integration](../fluent-live-inspection/mcp-integration.md) for live
operations. Current residuals or a convergence flag are not a recorded history.

1. Read the run/evidence contract and canonical output paths. Use MCP
   `solver_status` for current diagnostic context and scoped discovery/readback
   for residual/monitor configuration; neither establishes historical completeness.
2. Prefer existing file-backed histories/transcripts. Where MCP lacks complete
   export, review `PyAnsys/scripts/inspection/export_residuals.py` and record the
   exact capability gap, source and helper before using it. Preserve the native
   residual definition/scaling and equation identities.
3. Stitch by Fluent iteration or physical time, not sample number. Remove only
   verified duplicate samples. Preserve restarts, stage boundaries, real gaps,
   failed tails and the actual horizon; never blindly concatenate or interpolate.
4. Plot/reduce locally with the approved analysis plan. Record source segments,
   transformations and completeness: complete, partial, unavailable or requires
   rerun. Missing history cannot be made complete by a final data snapshot.

The retired Stage-3 stitched builder is historical implementation evidence, not
a current entry point. Reuse a parser only when a demonstrated need warrants it;
do not recreate generic live probing. Missing required capture is an evidence
block to the calling workflow, not authority to silently change or rerun a case.
