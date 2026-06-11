# Fluent-Backed Extractor Skeleton

Use this path later, when you are on the machine that can run or connect to
Fluent.

Purpose:
- connect to a live Fluent session;
- optionally load a case/data file;
- export the active setup tree to JSON;
- capture a small amount of Scheme/TUI state for cross-checking.

This directory now contains:

- `export_case_settings.py`
  - smaller live-export skeleton for quick JSON snapshots
- `export_hybrid_case_bundle.py`
  - fuller read-mostly exporter that combines:
    - live PyFluent settings-tree capture
    - Scheme-side probes
    - optional offline `.cas/.dat/.h5` inspection through the local extractor

PyFluent and Fluent object paths still vary by version, so both scripts remain
defensive and record what they can reach rather than pretending the tree is
stable.

## Expected workflow later

1. Start Fluent and the gRPC server.
2. Verify `PyAnsys/.env` and connection settings.
3. Run the existing connection checks in `PyAnsys/scripts/`.
4. For the fuller bundle, run:

```bash
.venv/bin/python extractors/fluent/export_hybrid_case_bundle.py \
  --server-id 1 \
  --case "D:\\path\\to\\purnanto-setup.cas.h5" \
  --data "D:\\path\\to\\purnanto-setup-5000.dat.h5" \
  --yes-load \
  --offline-case-file "/local/path/to/purnanto-setup.cas.h5" \
  --offline-data-file "/local/path/to/purnanto-setup-5000.dat.h5" \
  --archive-root cases/actual_setup_archives \
  --archive-name 00a-purnanto-live-baseline-5000
```

For the smaller live-only snapshot, run:

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

- `live/settings_root_tree.json`: broad recursive settings-tree crawl
- `live/targeted_branches.json`: deeper targeted captures for models, BCs, materials, and solution
- `live/scheme_snapshot.json`: Scheme probes that help verify runtime/config values
- `offline_case/` and `offline_data/`: optional local file inventories and candidate strings
- `manifest.json`: top-level capture metadata
- `notes.txt`: warnings about missing sections or API paths that need adjustment

## Intended use with the offline extractor

Run the offline `h5py` extractor first or let the hybrid bundle call it for you.
Then use the findings here to decide:
- which models or BCs need explicit Fluent-side verification;
- whether the case appears to contain readable config fragments;
- which API sections fail and need troubleshooting on-site.
