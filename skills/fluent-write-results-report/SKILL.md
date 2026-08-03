---
name: fluent-write-results-report
description: Turn verified Fluent analysis evidence into a concise setup-linked results report. Use when Codex has completed result analysis and must report values, provenance, limitations, and conclusions without rerunning Fluent or inventing missing evidence.
---

# Fluent Write Results Report

Use only verified analysis evidence. If important evidence is missing, return
the specific gap to `$fluent-analyze-results`.

## Process

1. Read the setup Markdown, exact case/data identity, analysis summary, raw
   artifacts, existing report, and repository reporting rules.
2. Check that important values retain their units and analysis scope.
3. Separate measured, derived, unresolved, unavailable, and not-applicable
   findings.
4. State convergence and other limitations clearly.
5. Recommend whether to create, update, defer, or skip the report.
6. Obtain the final approval required by `skills/setup-report/SKILL.md`.
7. After approval, write or update the setup-linked results report and required
   indexes or short cross-references.

Link raw analysis artifacts instead of copying complete transcripts. Do not
mix evidence from different case/data checkpoints without saying so.

## Completion

Return the report path, the evidence it uses, any updated index or
cross-reference, and unresolved questions requiring more analysis.
