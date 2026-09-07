# P4P Steam Quality Replication Context

## Goal

This workspace is being used to replicate parts of the study:

- Purnanto, M.H., Zarrouk, S.J., and Cater, J.E. (2013)
- *CFD Modelling of Two-Phase Flow inside Geothermal Steam-Water Separators*

The immediate task is to calculate **overall outlet steam quality** from Fluent DPM / particle-tracking results.

## Current Approach

The implemented logic is:

1. Use Harwell-style injection mass flows to determine how much liquid each injection represents.
2. Read a CSV containing particle outcomes for each injection:
   - `trapped`
   - `escaped`
   - `incomplete`
3. Convert outcome counts into fractions for each injection.
4. Treat `escaped` particles as liquid carryover to the steam outlet.
5. By default, treat `incomplete` particles as **separated** liquid.
6. Sum liquid carryover across all injections.
7. Compute outlet steam quality as:

```text
steam quality = steam mass flow / (steam mass flow + liquid carryover to top outlet)
```

This matches the paper’s described method in substance:

- outlet steam quality is based on the mass ratio at the steam outlet
- escaped droplets are carryover to the steam outlet
- incomplete particles are, by default, treated as separated for the preferred estimate

## Important Interpretation

- `quality %` is the main performance metric if the goal is to match the paper.
- `collect %` is only a supporting diagnostic.

Definitions:

```text
quality % = m_gas / (m_gas + liquid carryover to top outlet)
collect % = liquid separated / total injected liquid
```

## Relevant Files

- [Code/steam_quality_calculation.py](/Users/andy/Desktop/P4P/Code/steam_quality_calculation.py:1)
  - Main script for steam-quality calculation from DPM results.
- [Code/steam_quality_input_template.csv](/Users/andy/Desktop/P4P/Code/steam_quality_input_template.csv:1)
  - Example input format.
- [Code/harwell_calculation.py](/Users/andy/Desktop/P4P/Code/harwell_calculation.py:1)
  - Computes droplet diameters and injection mass flows.
- [Code/harwell_results.csv](/Users/andy/Desktop/P4P/Code/harwell_results.csv:1)
  - Precomputed injection mass flows used by the steam-quality script.
- [Literature/IPENZTransactions40_CFDModelling-TwoPhaseFlow.pdf](/Users/andy/Desktop/P4P/Literature/IPENZTransactions40_CFDModelling-TwoPhaseFlow.pdf:1)
  - Main reference paper.

## How `steam_quality_calculation.py` Works

### Input expectations

Minimum CSV columns:

```csv
inj,trapped,escaped,incomplete
```

Supported multi-case format:

```csv
case,inj,trapped,escaped,incomplete
```

Optional explicit columns:

- `m_gas`
- `liquid_mass_flow_kgs`

### Matching logic

If `liquid_mass_flow_kgs` is **not** supplied in the input CSV:

- the script reads `Code/harwell_results.csv`
- filters by `case`
- matches the row by `inj`
- uses the matched `mass_flow_kgs`

So the effective lookup key is:

```text
(case, inj)
```

If there is no `case` column, the script requires either:

- `--case "Case X"`
- or explicit `m_gas` and `liquid_mass_flow_kgs` columns

### Incomplete-particle handling

CLI option:

```text
--incomplete separated
--incomplete escaped
--incomplete ignore
```

Default:

```text
--incomplete separated
```

This default was chosen because it aligns with the paper’s preferred assumption.

## Current Built-in Cases

The current `steam_quality_calculation.py` and `harwell_calculation.py` use these built-in cases:

1. `Case 1` = `h = 1600 kJ/kg -25%`
2. `Case 2` = `h = 1440 kJ/kg`
3. `Case 3` = `h = 1520 kJ/kg`
4. `Case 4` = `h = 1600 kJ/kg`
5. `Case 5` = `h = 1680 kJ/kg`
6. `Case 6` = `h = 1760 kJ/kg`
7. `Case 7` = `h = 1976 kJ/kg`
8. `Case 8` = `h = 2214 kJ/kg`

Mass flows are currently taken from `Code/harwell_results.csv`, which already contains the injection-level `mass_flow_kgs` values.

## Commands

Run with the template input:

```bash
python3 Code/steam_quality_calculation.py Code/steam_quality_input_template.csv
```

Run with a multi-case CSV:

```bash
python3 Code/steam_quality_calculation.py your_results.csv
```

Run with a single-case CSV that has no `case` column:

```bash
python3 Code/steam_quality_calculation.py your_results.csv --case "Case 4"
```

Write a summary CSV:

```bash
python3 Code/steam_quality_calculation.py your_results.csv --output-csv Code/steam_quality_summary.csv
```

## Verified Behavior

The script has already been run successfully on the template CSV and produced a per-case summary including:

- `m_gas`
- `m_liq`
- `liq->top`
- `quality`
- `quality %`
- `collect %`

## Known Caveats

- `steam_quality_calculation.py` currently contains a stray top-level string line:

```python
"python3 Code/steam_quality_calculation.py Code/steam_quality_input_template.csv"
```

This does not break execution, but it is noise and can be removed.

- `harwell_calculation.py` depends on the droplet-distribution pipeline for regenerating injection results, but `steam_quality_calculation.py` does **not** require NumPy/SciPy as long as `harwell_results.csv` already exists.

- The steam-quality script assumes the input particle counts are representative in proportion to the liquid mass assigned to each injection.

## Recommended Next Steps

- Use the real Fluent DPM results CSV and compute `quality %` for each case.
- Compare the resulting quality values directly against the paper’s reported outlet steam-quality values.
- If results differ significantly, inspect:
  - how `incomplete` particles are being treated
  - whether the `case` naming matches `harwell_results.csv`
  - whether the injection numbering in the Fluent export matches the Harwell injection numbering
