---
name: post-simulation-analysis
description: "Use for read-only post-simulation checks on an existing Ansys Fluent case/data session: carrier flux balance, residual history, and dynamic DPM Particle Tracks Summary analysis. Do not use for rebuilding Fluent setups or changing solver models."
---

# Post-Simulation Analysis

## Scope

Use this skill after a Fluent case has been solved and the result needs a
repeatable, read-only check. The checks are independent and may be run one at
a time or together:

- `flux`: carrier mass-flow extraction and balance metrics;
- `residual`: residual-monitor history capture and log-scaled plot;
- `dpm`: live DPM injection discovery and Particle Tracks Summary fate counts.

The modular entrypoint is:

`/Users/shuheiyokkaichi/Developer/P4P_knowledgeWiki/PyAnsys/scripts/inspection/post_simulation_analysis.py`

It uses one Fluent connection for all selected checks. It assumes the intended
case/data pair is already loaded; loading is explicit and opt-in.

## Quick start

Activate the project environment:

```bash
source /Users/shuheiyokkaichi/Developer/P4P_knowledgeWiki/PyAnsys/.venv/bin/activate
```

Run one check:

```bash
python /Users/shuheiyokkaichi/Developer/P4P_knowledgeWiki/PyAnsys/scripts/inspection/post_simulation_analysis.py \
  --server-id 1 \
  --check flux \
  --run-label my-case
```

Use `--check residual` or `--check dpm` in the same position. Repeat the
option for selected checks, or use `--check all`:

```bash
python /Users/shuheiyokkaichi/Developer/P4P_knowledgeWiki/PyAnsys/scripts/inspection/post_simulation_analysis.py \
  --server-id 1 \
  --check flux \
  --check residual \
  --check dpm \
  --run-label my-case
```

If the script must load files, pass all three options explicitly:

```bash
python /Users/shuheiyokkaichi/Developer/P4P_knowledgeWiki/PyAnsys/scripts/inspection/post_simulation_analysis.py \
  --server-id 1 \
  --load-case-data \
  --case-file 'C:\\path\\case.cas.h5' \
  --data-file 'C:\\path\\case.dat.h5' \
  --check flux
```

Outputs are written to `PyAnsys/output/post_simulation_analysis/` unless
`--output-dir` is supplied.

## Report filing by setup number

Analysis is not complete when artifacts exist only under `PyAnsys/output/`.
Every analysis must also be interpreted and filed under the corresponding
setup-number report directory:

`/Users/shuheiyokkaichi/Developer/P4P_knowledgeWiki/Setups/reports/<setup-id>/`

Use the setup ID tied to the case branch, such as `08c`, `09c`, or `10a`.
Before writing, check `Setups/order-dictionary.md` and
`Setups/reports/index.md`; do not infer a new number or silently file results
under a different setup. The normal report entrypoint is:

`Setups/reports/<setup-id>/results.md`

Each appended analysis section should identify:

- setup ID and setup-report link;
- case/data filenames and iteration state;
- checks run (`flux`, `residual`, `dpm`);
- key numerical results and units;
- links to the machine-readable JSON/CSV/PNG/transcript artifacts;
- limitations, warnings, convergence status, and claim level.

If the analysis is a large technical extraction or validation comparison,
create a clearly named companion file inside the same numbered report folder,
then link it from `results.md`. Keep the generated raw artifacts in
`PyAnsys/output/`, but never leave the human interpretation there as the only
record.

## Individual checks

### Flux

`--check flux` discovers phase domains and inlet/outlet roles from the live
session, extracts mass flow for the detected zones, and writes:

`<run-label>-flux-check.json`

The output contains raw per-domain/per-zone values and derived metrics such as
phase efficiency, outlet dryness, mass imbalance, and the carryover comparison
note. Treat inferred zone roles and fallback phase mappings as warnings that
need review.

### Residual

`--check residual` captures the existing `residual` monitor set without running
iterations and writes:

- `<run-label>-residual-check.json`
- `<run-label>-residual-check.png`

Use `--monitor-set NAME` for a different Fluent monitor set and adjust
`--residual-timeout-seconds` or `--residual-poll-interval-seconds` when the
history is slow to arrive. A residual plot is evidence of solver-history
behavior, not proof that the physical solution is validated.

The standalone compatibility wrapper remains available at:

`/Users/shuheiyokkaichi/Developer/P4P_knowledgeWiki/PyAnsys/scripts/inspection/export_residuals.py`

### DPM

`--check dpm` uses the current dynamic runner:

`/Users/shuheiyokkaichi/Developer/P4P_knowledgeWiki/PyAnsys/scripts/inspection/run_dpm_particle_tracks.py`

It discovers the live DPM injection list, records index/name/diameter/material
metadata, configures Summary reporting, and tracks by injection name. Select a
subset with repeated options:

```bash
python /Users/shuheiyokkaichi/Developer/P4P_knowledgeWiki/PyAnsys/scripts/inspection/post_simulation_analysis.py \
  --server-id 1 \
  --check dpm \
  --dpm-index 0 \
  --dpm-order live
```

Use `--dpm-injection NAME` when the name is known. Use `--dpm-inspect-only` to
discover the inventory without tracking. DPM outputs are JSON, CSV, and a raw
transcript with `-dpm-particle-track-*` filenames.

The legacy `report/dpm-sample` options in the older combined post-processing
script are not the supported DPM check. Do not use them for new analysis; they
can sample selected boundaries rather than report complete particle fates and
are more sensitive to Fluent prompt order. The current check uses the verified
2024 R2 Particle Tracks Summary TUI workflow.

## Assumptions and pitfalls

- Case/data loading is not performed unless `--load-case-data` is supplied.
- The residual check reads an existing monitor history; it does not initialize,
  iterate, or modify the solution.
- Flux role detection currently recognizes common names such as
  `liquidinlet`, `steaminlet`, and `steamoutlet`; inspect warnings when a case
  uses different names.
- Phase-domain inference uses live phase/material state and falls back to
  `phase-1` as vapor and `phase-2` as liquid when mapping is unavailable.
- DPM indices are only valid for the current live injection list. Use injection
  names and recorded metadata as audit identity across cases.
- DPM Summary parsing treats fate rows omitted by Fluent as zero; a missing
  tracked count is a failed/unparsed result, not zero particles.
- The DPM TUI command is version-sensitive. The current known-good prompt is
  Fluent 2024 R2 with `screen`, `mixture`, and `particle-resid-time`.
- These checks do not create or repair injections, change models, initialize,
  run iterations, or write case/data files.
- Raw reports and warnings must be preserved. Do not silently replace an
  unavailable value with a guessed value.

## Interpretation rules

1. Confirm the case/data pair and iteration state before comparing results.
2. Run `flux`, `residual`, and `dpm` independently when diagnosing a failure so
   one unavailable branch does not hide the others.
3. Treat flux imbalance as a conservation diagnostic, not automatically as a
   DPM capture or carryover measurement.
4. Keep final DPM particle fates separate from EWF wall-film event counts;
   absorption or splashing events are not automatically equal to original
   injected-particle counts.
5. Preserve the JSON/CSV/PNG/transcript artifacts and label unsupported or
   partially parsed results as uncertain.

## Validation status

The modular interface, parser behavior, residual capture helper, and DPM
selection logic are covered by offline/static tests. No live Fluent server was
available for this revision, so a live test of the new combined entrypoint is
still required before relying on it for a production run.
