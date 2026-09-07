# Droplet and steam-quality calculations

These offline tools were recovered from Andy's loose `P4P/Code` directory on
8 September 2026. The four Python files and four compact CSV inputs are
unchanged apart from whitespace/line endings. Deprecated variants and older tables remain in the
[source recovery snapshot](https://github.com/Shuhei-uni/P4P_knowledgeWiki/tree/archive/andy-local-20260908/Workspace/Code).

- `droplet_distribution.py` exposes the fixed nine-bin distribution.
- `harwell_calculation.py` calculates injection diameters/mass flows and
  regenerates the adjacent baseline and spiral result CSVs.
- `distribution_fitting.py` explores fits to the digitized Figure 5 data and
  opens plots. It uses NumPy, SciPy and Matplotlib.
- `steam_quality_calculation.py` uses Python's standard library and the
  adjacent mass-flow lookup to summarize a particle-outcome CSV.

From this directory:

```bash
python3 steam_quality_calculation.py steam_quality_input_template.csv --incomplete separated
python3 steam_quality_calculation.py steam_quality_input_template.csv --incomplete escaped
python3 steam_quality_calculation.py steam_quality_input_template.csv --incomplete ignore
```

The supplied template is example input. Its historical default treats
incomplete particles as separated; that is an explicit assumption, not an
observed particle fate or a validation result. The other options expose the
sensitivity without changing the original implementation. Read the
[current method guidance](../../../../CFD_wiki/wiki/synthesis/fluent-separator-efficiency-methods.md)
and [historical enthalpy experiments](../../../../Project/experiments/parallel-andy-studies/enthalpy-dpm-replication.md)
before interpreting project outputs.

Use the repository's `PyAnsys/.venv/bin/python` for calculations needing
scientific packages. Install SciPy additionally for the optional fitting
script. Review regenerated CSV diffs before committing them.
