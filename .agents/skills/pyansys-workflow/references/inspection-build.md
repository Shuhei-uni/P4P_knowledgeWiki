# Inspection and build

## Inspect live state

Treat live inspection as a question-answering operation. First state the exact
object, allowed value, model prerequisite, field, zone, or artifact identity
that is uncertain. Inspect the shallowest Settings/API path that can answer it;
capture the relevant state and allowed values before constructing a mutation.
Reacquire affected objects after loading a case/data pair or changing models,
phases, zones, registers, or surfaces, because those operations can replace the
underlying Settings tree.

Reuse a current repository implementation when it demonstrates the same API
pattern, but re-inspect live names, values, paths, and dependencies rather than
copying campaign-specific assumptions. Useful starting points are
`PyAnsys/scripts/inspection/inspect_fluent_session.py` and the connection
helpers under `PyAnsys/scripts/connection/`.

When the configured MCP inspection path is available, capture the narrow exact
paths before and after a change rather than a broad tree dump. Use
`inspect_fluent_session.py --paths <path> --output-json <receipt>` for the
readback and `compare_case_setup.py` with explicit allowed paths after
save/reopen. The execution wrapper
`PyAnsys/scripts/orchestration/execute_fluent_code.py` receives a code snippet
using the supplied `solver` binding; its receipt proves only that code executed,
so pair it with state readback, artifact verification, and smoke evidence.

## Build a verifiable child

1. Prove the exact parent case/data and active Fluent session.
2. Inspect the live Settings/API tree before writing a mutation you are not sure
   about.
3. Apply changes in dependency order and reacquire downstream objects after
   topology/model changes.
4. Read back every critical delta and invariant.
5. Resolve file-backed reports/monitors/checkpoints to explicit destinations.
6. Save the child, reopen it from disk, reacquire, and repeat the critical audit.
7. Run the smallest useful smoke test and prove required instrumentation writes.

Return a compact build receipt: parent, changes, readback, artifact paths,
smoke/instrumentation result, unresolved uncertainty.
