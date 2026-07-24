# Autonomy Contracts

This directory holds author-facing JSON examples for the offline Phase 2–6
scaffold. The executable validation source of truth is currently:

- `src/pyansys_fluent/autonomy/capability.py`
- `src/pyansys_fluent/autonomy/setup.py`
- `src/pyansys_fluent/autonomy/analysis.py`
- `src/pyansys_fluent/autonomy/decision.py`

All top-level contracts have an explicit `schema_version`. Unknown fields are
rejected. The scaffold can serialize, validate, compile, and gate documents,
but it cannot connect to Fluent or execute a setup.

`examples/08c-carrier-autonomy-scaffold.json` is a non-executable example for
the first carrier-only vertical slice. Its file paths, hash, values, and
capability paths are placeholders. They must be replaced by live evidence
before any later live adapter is allowed to consume it.

The next schema milestone should generate or maintain formal JSON Schema files
from these validated models after the contract shapes survive the first live
capability-probe work. Until then, the Python validators prevent a second,
potentially drifting schema authority.
