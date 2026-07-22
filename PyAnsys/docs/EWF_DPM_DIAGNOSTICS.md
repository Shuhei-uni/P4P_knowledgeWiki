# EWF and DPM Diagnostic Automation

This workflow audits and post-processes an already-built Fluent case/data state. It does **not** rebuild the setup and it does **not** enable or disable EWF, splash, edge separation, stripping, wall-film boundaries, or global DPM coupling.

The implementation is split into:

- `src/pyansys_fluent/ewf_diagnostics.py`: EWF model audit, namespaced report definitions, final-state report computation, film mass-flow extraction, and bookkeeping targets.
- `src/pyansys_fluent/dpm_reports.py`: live injection discovery, deterministic injection selection, 2024 R2 Particle Tracks Summary commands, report parsing, and per-injection mass-flow closure.
- `scripts/inspection/run_ewf_dpm_diagnostics.py`: thin CLI orchestration and CSV/JSON output.

## Safety model

The default mode is `audit`. It only reads settings and writes local JSON.

`snapshot` and `all` create or update report definitions beginning with the chosen prefix, default `ewfdiag-`. They do not alter model physics. Use `--object-policy fail` for a first dry run if existing diagnostic objects must not be touched.

The exploratory GUI journal must not be replayed as production automation because it temporarily enabled Particle Stripping and Edge Separation while inspecting their dependent options. This script never performs those toggles.

## First test on the already-open Fluent session

From the `PyAnsys` directory:

```powershell
python .\scripts\inspection\run_ewf_dpm_diagnostics.py `
  --server-id 1 `
  --mode audit `
  --film-wall wall `
  --output-dir .\output\ewf_dpm_diagnostics `
  --run-label 10a-audit
```

Review:

```text
output/ewf_dpm_diagnostics/10a-audit/
├── model_audit.json
├── run_manifest.json
├── raw_results.json
└── bookkeeping.json
```

Confirm that the audit reports:

- `wall` as the active EWF wall;
- `bottom` as not assigned to EWF;
- the expected global Particle Splashing state;
- Edge Separation and Particle Stripping as disabled;
- no DPM UDF override for impingement, film regime, or splash distribution.

If the active film wall is not detected automatically, continue supplying `--film-wall wall`. The raw wall state is retained in `model_audit.json` so the live key can be added to the adapter after inspection.

## Final-state EWF snapshot

```powershell
python .\scripts\inspection\run_ewf_dpm_diagnostics.py `
  --server-id 1 `
  --mode snapshot `
  --film-wall wall `
  --flux-boundary liquidinlet `
  --flux-boundary steaminlet `
  --flux-boundary steamoutlet `
  --object-policy reuse `
  --output-dir .\output\ewf_dpm_diagnostics `
  --run-label 10a-final-snapshot
```

The script attempts to create and compute:

| Key | Fluent reduction | EWF field |
|---|---|---|
| `film_courant_max` | Facet Maximum | Film Courant Number |
| `film_mass_total` | Sum | Film Mass |
| `film_thickness_max` | Facet Maximum | Film Thickness |
| `film_thickness_area_average` | Area-Weighted Average | Film Thickness |
| `film_dpm_mass_source_total` | Sum | Film DPM Mass Source |
| `film_outflow_mass_total` | Sum | Film Outflow Mass |
| `film_velocity_area_average` | Area-Weighted Average | Film Velocity Magnitude |
| `film_velocity_max` | Facet Maximum | Film Velocity Magnitude |
| `film_x/y/z_velocity_area_average` | Area-Weighted Average | Film velocity component |
| `film_stripped_mass_total` | Sum | Film Stripped Mass, only when stripping is active |
| `film_separated_mass_total` | Sum | Film Separated Mass, only when edge separation is active |

Every report records:

- the requested semantic field and reduction;
- the live allowed values seen by PyFluent;
- the resolved Fluent value;
- setter/readback actions;
- compute attempts, raw console output, parsed value, and units.

The film flux query uses the settings command equivalent of:

```text
report/fluxes/film-mass-flow
```

and records the mixture-level result by boundary.

## DPM tracking and closure

```powershell
python .\scripts\inspection\run_ewf_dpm_diagnostics.py `
  --server-id 1 `
  --mode dpm `
  --order diameter-ascending `
  --keep-going `
  --output-dir .\output\ewf_dpm_diagnostics `
  --run-label 10a-dpm
```

Track selected injections by stable names when narrowing the run:

```powershell
--injection water-liquid-at-psep-5um `
--injection water-liquid-at-psep-348um
```

The script configures the legacy 2024 R2 Particle Tracks workflow as:

```text
/file/set-tui-version "24.2"
/preferences/graphics/enable-non-object-based-workflow yes
/display/set/particle-tracks/report-type summary
/display/set/particle-tracks/report-to screen
/display/set/particle-tracks/display? no
/report/dpm-zone-summaries-per-injection? yes
```

For each injection it records:

- original and total tracked parcel counts;
- escaped, trapped, incomplete, aborted, evaporated, inserted, and injected counts where reported;
- Eulerian wall-film absorbed and splashed event/parcel counters;
- fate rows by zone;
- mass-transfer rows by fate and zone;
- DPM terminal mass-flow closure residual.

The DPM flow closure is:

```text
reported Net injection flow
= escaped + trapped + absorbed + incomplete + other terminal fate flows + residual
```

Splash counters are retained as transfer diagnostics. They are not added as a second terminal sink because secondary parcel mass can later appear in an escaped, trapped, absorbed, or unresolved fate.

## Combined first run

After `audit` and `snapshot` succeed independently:

```powershell
python .\scripts\inspection\run_ewf_dpm_diagnostics.py `
  --server-id 1 `
  --mode all `
  --film-wall wall `
  --flux-boundary liquidinlet `
  --flux-boundary steaminlet `
  --flux-boundary steamoutlet `
  --order diameter-ascending `
  --keep-going `
  --output-dir .\output\ewf_dpm_diagnostics `
  --run-label 10a-ewf-dpm-all
```

## Loading an explicit case/data pair

The safer initial test is against an already-open session so the operator can confirm the exact case. Explicit loading is available when needed:

```powershell
python .\scripts\inspection\run_ewf_dpm_diagnostics.py `
  --server-id 1 `
  --load-case-data `
  --load-mode explicit `
  --case-file "C:\path\setup.cas.h5" `
  --data-file "C:\path\result.dat.h5" `
  --mode all `
  --film-wall wall
```

## Output contract

A typical `all` run writes:

```text
<output>/<run-label>/
├── run_manifest.json
├── model_audit.json
├── final_reports.csv
├── film_flux.csv
├── dpm_injection_summary.csv
├── dpm_zone_summary.csv
├── dpm_particle_track_transcript.txt
├── bookkeeping.json
└── raw_results.json
```

`bookkeeping.json` deliberately labels the final-state EWF balance as `bookkeeping-only`. A true EWF closure requires a defined interval with initial and final film inventory plus time-integrated source and outflow terms.

## Histories

`--create-history-files` enables the report definition's `Create Report File` option where the live 2024 R2 settings tree exposes it. Use it **before** continuing or rerunning iterations. It cannot reconstruct history from a final `.dat.h5` snapshot.

The first live test should verify which report-file objects Fluent creates and where they are written. A later adapter can then set explicit filenames and merge their time histories into the same output bundle.

## Expected first-test feedback

Send back:

1. the console trace;
2. `run_manifest.json`;
3. `model_audit.json`;
4. `raw_results.json`;
5. any failed report object's `configuration.actions` and `compute.attempts`.

Those artifacts are sufficient to correct a 2024 R2 path or allowed-value mismatch without guessing from the GUI.
