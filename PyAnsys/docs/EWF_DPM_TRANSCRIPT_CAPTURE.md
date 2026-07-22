# DPM Transcript Capture and Completion Gate

## Why this patch exists

The initial DPM diagnostic runner submitted the correct Fluent 2024 R2 TUI commands, but it attempted to capture each report with Python `redirect_stdout`. Fluent transcript output is delivered through PyFluent's transcript streaming service, potentially on a worker thread, so redirecting the calling thread's stdout is not a reliable report boundary.

In the first live test, Fluent completed all six injections in ascending diameter order, while the Python client did not retain the corresponding report blocks. This patch changes the orchestration rather than the Fluent commands.

## New execution behavior

For DPM mode the runner now:

1. registers a callback directly on `solver.transcript`;
2. starts a continuously flushed `dpm_live_transcript.txt`;
3. waits for the existing transcript stream to become quiet before marking the next injection boundary;
4. submits one named-injection Particle Tracks command;
5. waits until the marked transcript slice contains:
   - a parsed `number tracked = ...` line;
   - the `Mass Transfer Summary` section;
   - at least one parsed mass-transfer row;
   - no new transcript text for the configured quiet interval;
6. writes that injection's raw report immediately under `dpm_raw/`;
7. refreshes partial CSV and JSON outputs;
8. only then submits the next injection.

A transcript timeout is a hard sequencing stop. Even with `--keep-going`, the runner does not submit another injection when the previous command's completion was not confirmed.

## Pull the patched branch

```powershell
git fetch origin
git switch agent/ewf-dpm-diagnostics-v1
git pull origin agent/ewf-dpm-diagnostics-v1
```

## Rerun DPM mode

From `PyAnsys`:

```powershell
python .\scripts\inspection\run_ewf_dpm_diagnostics.py `
  --server-id 1 `
  --mode dpm `
  --order diameter-ascending `
  --keep-going `
  --dpm-timeout-seconds 600 `
  --transcript-quiet-seconds 1.0 `
  --output-dir .\output\ewf_dpm_diagnostics `
  --run-label 10a-dpm-streamed
```

Add this only when the Python terminal should echo every captured Fluent transcript line:

```powershell
  --echo-dpm-transcript
```

The Fluent session normally already prints its transcript, so leaving this option off avoids duplicated terminal output.

## Outputs written during the run

```text
output/ewf_dpm_diagnostics/10a-dpm-streamed/
├── dpm_live_transcript.txt
├── dpm_progress.json
├── dpm_injection_summary.partial.csv
├── dpm_zone_summary.partial.csv
├── bookkeeping.partial.json
└── dpm_raw/
    ├── 00-water-liquid-at-psep-5um.txt
    ├── 01-water-liquid-at-psep-28um.txt
    └── ...
```

The exact numeric prefix follows Fluent's live injection-list index. The processing order remains the selected diameter order.

After successful completion, the normal final outputs are also written:

```text
├── dpm_injection_summary.csv
├── dpm_zone_summary.csv
├── dpm_particle_track_transcript.txt
├── bookkeeping.json
├── raw_results.json
└── run_manifest.json
```

## Failure interpretation

### `transcript service is unavailable`

Reconnect through the repository's normal `connect()` helper with transcript streaming enabled. The current helper already uses `start_transcript=True`.

### One injection times out but Fluent is still visibly working

Do not launch another script. Let Fluent return to its prompt, then preserve:

- `dpm_live_transcript.txt`;
- the individual file under `dpm_raw/`, if present;
- `dpm_progress.json`;
- the Python exception/console output;
- the Fluent console transcript.

Increase `--dpm-timeout-seconds` only if the report truly took longer than the configured limit. The timeout is deliberately a sequencing gate, not permission to queue the next track command.

### Complete report but failed parsing

The raw report remains saved. Update the parser against that exact report format before changing the Fluent command.

## Bookkeeping note from the first live run

The first run demonstrated splash events for the 56, 112 and 168 micrometre injections. The wall-film `splashed` counter remains a separate interaction diagnostic; it is not added as another terminal mass sink when the same represented secondary mass later appears in escaped, trapped, absorbed or unresolved fates.
