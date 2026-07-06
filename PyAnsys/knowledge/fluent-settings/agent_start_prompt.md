# Agent Start Prompt: Fluent Dependency-Aware Automation

You are automating Ansys Fluent through PyFluent/gRPC/TUI. Your main risk is not only wrong values; it is wrong activation order and wrong settings paths.

Before setting any Fluent value:

1. Confirm the parent model/object exists.
2. Confirm it is active.
3. Refresh or reacquire the object after every major parent change.
4. Inspect child names, command names, and allowed values.
5. Apply the setting.
6. Read the setting back.
7. If it fails, classify the failure as:
   - order/dependency issue
   - path/version issue
   - invalid value/format issue
   - PyFluent wrapper limitation
   - requires TUI fallback
   - requires manual GUI cleanup

Use this package in this order:

1. `orders/global_setup_order.yaml`
2. `indices/path_dependency_index.json`
3. the model-specific `orders/*.yaml` and `trees/*.md`
4. `../../src/pyansys_fluent/common.py`
5. `../../src/pyansys_fluent/dependency_workflow.py`
6. `templates/dependency_aware_setter_pseudocode.py`
7. `docs/documentation_map.md`
8. `templates/failure_log_template.md`

For this project, be especially careful with:

- DPM injection surface binding to `steaminlet`
- DPM inert-particle material creation/assignment
- default injection creation before modifying DPM settings
- Mixture vs VOF multiphase paths
- Energy-dependent fields
- EWF wall/DPM coupling paths

Canonical execution loop for setup construction:

```text
connect -> verify inputs -> enable parent -> reacquire object -> inspect children/options -> set -> read back -> classify failure -> choose fallback
```

Case-building scripts should end by writing `.cas.h5` only.

For actual initialization, iteration, and data writing, use the focused runner:
- `../../scripts/setup/save_data_after_iterations.py`
- input: remote `.cas.h5` path and iteration count
- output: derived `name_X.dat.h5`
- loader helper: `../../src/pyansys_fluent/setup_io.py::load_case_only`

Do not keep rerunning the full setup just because a non-critical deep child path fails. Isolate the failure in a minimal sandbox when possible, log it, use TUI fallback if available, and save a manual-fix checklist if needed.
