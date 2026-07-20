---
name: post-simulation-analysis
description: "Use for post-simulation analysis of existing Ansys Fluent case/data files, especially DPM particle-track Summary reports, injection fate counts, EWF event counts, and CSV/JSON result extraction. Do not use for rebuilding Fluent setups or changing solver models."
---

# Post-Simulation Analysis

## Overview

Use this skill when an existing Fluent `.cas.h5` and `.dat.h5` need to be inspected or analyzed without rebuilding the setup. The current project runner is:

`/Users/shuheiyokkaichi/Developer/P4P_knowledgeWiki/PyAnsys/scripts/inspection/run_dpm_particle_tracks.py`

Keep post-processing separate from setup construction. Never assume that a successful Fluent command means the intended result was produced; inspect names, settings, reports, and readbacks.

## Current DPM runner

Activate the PyAnsys environment:

```bash
source /Users/shuheiyokkaichi/Developer/P4P_knowledgeWiki/PyAnsys/.venv/bin/activate
```

The normal workflow assumes the desired case/data pair is already loaded in Fluent. Discover the active DPM list without tracking:

```bash
python /Users/shuheiyokkaichi/Developer/P4P_knowledgeWiki/PyAnsys/scripts/inspection/run_dpm_particle_tracks.py \
  --server-id 1 \
  --inspect-only
```

Run one injection by its current live-list index:

```bash
python /Users/shuheiyokkaichi/Developer/P4P_knowledgeWiki/PyAnsys/scripts/inspection/run_dpm_particle_tracks.py \
  --server-id 1 \
  --index 0 \
  --order live
```

Omit `--index` and `--injection` to run every live injection. Names can also be selected directly with repeated `--injection` options. If the script should load inputs explicitly, opt in:

```bash
python /Users/shuheiyokkaichi/Developer/P4P_knowledgeWiki/PyAnsys/scripts/inspection/run_dpm_particle_tracks.py \
  --server-id 1 \
  --load-case-data \
  --case-file 'C:\Users\syok443\Documents\case.cas.h5' \
  --data-file 'C:\Users\syok443\Documents\case.dat.h5'
```

The script records both the live index and injection name. The index is a selection convenience for the current session; the name is the audit identity in the output. Results are written under `PyAnsys/output/dpm_particle_tracks/` unless `--output-dir` is supplied:

- `*-particle-track-summary.json`
- `*-particle-track-summary.csv`
- `*-particle-track-transcript.txt`

## Remaining assumptions and pitfalls

The runner is dynamic with respect to DPM injections, but it still assumes:

- Fluent already has the intended case/data pair loaded unless `--load-case-data` is supplied;
- the live Settings API exposes `setup.models.discrete_phase.injections`;
- the active Fluent version supports the legacy 2024 R2-compatible TUI sequence;
- the DPM Particle Tracks report is configured as Summary with display disabled;
- the current 2024 R2 prompts accept `screen`, `mixture`, and `particle-resid-time`;
- selected injections can be identified by their live names.

Changing the DPM set should no longer fail merely because names or diameters changed. New, renamed, or removed injections are discovered from the active session. The script fails only when:

- the active case has no DPM injection branch or the list is empty;
- a requested `--index` is outside the current live list;
- a requested `--injection` name is not present;
- Fluent’s TUI path or prompt order differs from the supported 2024 R2 workflow;
- a Summary count cannot be parsed.

Do not compare indices between different cases or sessions: Fluent can reorder the list. Use the recorded injection name, diameter, material, and surface metadata for comparison. Omitted fate rows are interpreted as zero because Fluent’s Summary report suppresses fates that did not occur.

The runner does not create or repair injections, mutate the case, initialize the solver, or write new case/data files. Its output directory is local to the machine running PyFluent; case/data paths, when explicitly loaded, are paths visible to Fluent.

## Analysis rules

1. Confirm the case and data files belong to the same setup branch and iteration state.
2. Verify Fluent version and the live DPM injection names before tracking.
3. Run one injection as a smoke test before a full sweep.
4. Keep final particle fates separate from EWF event counts; splashing or absorption events are not automatically equal to original injected-particle counts.
5. Preserve the raw transcript with parsed CSV/JSON outputs so a reported count can be audited.
6. Label unavailable, mismatched, or partially parsed results as uncertainty rather than filling values silently.
