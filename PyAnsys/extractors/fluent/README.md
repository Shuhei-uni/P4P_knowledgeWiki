# Fluent-Backed Extractor Skeleton

Use this path later, when you are on the machine that can run or connect to
Fluent.

Purpose:
- connect to a live Fluent session;
- optionally load a case/data file;
- export the active setup tree to JSON;
- capture a small amount of Scheme/TUI state for cross-checking.

This directory is a skeleton, not a finished universal exporter. PyFluent and
Fluent object paths vary by version, so the script is defensive and records what
it can reach.

## Expected workflow later

1. Start Fluent and the gRPC server.
2. Verify `PyAnsys/.env` and connection settings.
3. Run the existing connection checks in `PyAnsys/scripts/`.
4. Run:

```bash
.venv/bin/python extractors/fluent/export_case_settings.py --output-dir output/live_extract_01
```

Optional case load:

```bash
.venv/bin/python extractors/fluent/export_case_settings.py \
  --case "D:\\path\\to\\your\\file.cas.h5" \
  --data "D:\\path\\to\\your\\file.dat.h5" \
  --yes-load \
  --output-dir output/live_extract_01
```

## Expected outputs

- `settings_snapshot.json`: PyFluent settings state that was reachable
- `scheme_snapshot.json`: Scheme probes that help verify runtime/config values
- `notes.txt`: warnings about missing sections or API paths that need adjustment

## Intended use with the offline extractor

Run the offline `h5py` extractor first. Then use the findings here to decide:
- which models or BCs need explicit Fluent-side verification;
- whether the case appears to contain readable config fragments;
- which API sections fail and need troubleshooting on-site.
