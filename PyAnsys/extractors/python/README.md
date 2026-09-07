# Offline Case Extractor (`h5py`)

Use this path when you have Fluent case/data files but do not have Fluent
available.

What it does:
- opens the HDF5 file with `h5py`;
- opens legacy text `.cas` files directly;
- records the group/dataset tree;
- captures attributes;
- previews scalar and small string-like datasets;
- flags likely human-readable configuration text for later Fluent-side checking.

What it does not do:
- guarantee a complete Fluent setup reconstruction;
- know which values were manually changed from defaults;
- replace a real Fluent session export.

## Usage

From `PyAnsys/`:

```bash
.venv/bin/python extractors/python/h5_case_extractor.py /path/to/file.cas
.venv/bin/python extractors/python/h5_case_extractor.py /path/to/file.cas.h5
```

Optional output directory:

```bash
.venv/bin/python extractors/python/h5_case_extractor.py /path/to/file.cas \
  --output-dir output/case01_extract
```

Outputs:
- `tree.txt`: readable HDF5 structure
- `summary.json`: machine-readable inventory
- `candidate_strings.txt`: possible text/config snippets worth checking later in Fluent

## Suggested workflow

1. Run this on the case file first.
2. Run it on the matching data file second.
3. Compare the candidate strings and tree structure.
4. Use the findings to decide what to verify later with the Fluent-backed extractor.
