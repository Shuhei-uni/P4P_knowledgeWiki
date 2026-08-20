# Fluent Settings Agent Knowledge Base

Purpose: a compact reference for dependency-aware Fluent automation through PyFluent/gRPC/TUI.

Most failures come from either:

1. **wrong order** — a child is set before its parent/model/object is active;
2. **wrong path** — the live Fluent tree differs by version, solver mode, model combination, phase count, object type, or boundary type.

Always inspect the live tree and read back critical values.

## Use this package in this order

1. `orders/global_setup_order.yaml`
2. the relevant model `trees/*.md` and `orders/*.yaml`
3. `indices/path_dependency_index.json` when a path/order is unclear
4. `docs/documentation_map.md` when local knowledge and the live tree disagree
5. `logs/successful_paths.md` for prior verified discoveries

Canonical mutation pattern:

```text
enable/create parent -> reacquire -> inspect -> set -> read back
```

## Run planning

Simulation execution is a separate decision from setup construction. Choose among:

- one direct TUI run for a single uninterrupted case;
- a robust Fluent journal for multiple independent/fixed cases;
- agent-owned Python orchestration for staged/adaptive runs that require intermediate decisions.

See `native_run_and_autosave.md` for the run-mode and recovery policy.

## Failure categories

Use these labels when useful:

- `order/dependency issue`
- `path/version issue`
- `invalid value/format issue`
- `PyFluent wrapper limitation`
- `requires TUI fallback`
- `requires manual GUI cleanup`

Do not rerun an entire setup blindly because one deep path failed. Isolate the smallest failing branch and record reusable discoveries.
