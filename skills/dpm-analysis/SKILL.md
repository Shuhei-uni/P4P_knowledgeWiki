---
name: dpm-analysis
description: Extract and assess Fluent DPM tracking, fate, and mass-transfer evidence when DPM is relevant to the experiment question.
---

# DPM analysis

Run this skill only when the experiment question or requested evidence needs
DPM.

## Rules

- Verify active injections, identity, source scope, particle type, and tracked
  rows before interpreting output.
- Preserve raw transcripts/output needed to audit parsing.
- Require actual tracked-count/report evidence; never replace missing rows with
  zero.
- Preserve fate/zone, represented or net mass flow, and units.
- Distinguish mechanism/event counters from terminal particle fates so mass is
  not double-counted.
- Relevance comes from `setup.md`; a complete DPM report can still be
  scientifically irrelevant.

Inspect known-working repository code before constructing an equivalent
PyFluent access pattern from memory. Reuse the access pattern, not case-specific
names, values, paths, or branch assumptions. If the current live Fluent tree
differs, inspect and adapt.

## Known working code

- `PyAnsys/src/pyansys_fluent/dpm_reports.py`
- `PyAnsys/src/pyansys_fluent/dpm_transcript.py`
- `PyAnsys/scripts/inspection/run_dpm_particle_tracks.py`

Inspect current injections/settings when the live case differs from the proven
example. Keep transcript and parsed evidence linked so a missing or ambiguous
fate remains visible.
