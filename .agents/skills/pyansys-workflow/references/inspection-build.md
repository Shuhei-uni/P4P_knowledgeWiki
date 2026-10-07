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

Before a new build, verify one explicit interpreter and its required modules on
the execution host; record its executable, version and extra dependency paths.
Reuse that receipt for the same host/environment and revalidate the selected
interpreter at the next launch. A missing module is a preflight failure, not a
reason to rerun setup or repeat broad interpreter searches. Use the existing
transfer implementation before writing another repair for lost injections.
Check object inventories for missing/duplicate names before state dictionaries.

When the configured MCP inspection path is available, capture the narrow exact
paths before and after a change rather than a broad tree dump. Use
`inspect_fluent_session.py --paths <path> --output-json <receipt>` for the
readback and `compare_case_setup.py` with explicit allowed paths after
save/reopen. The execution wrapper
`PyAnsys/scripts/orchestration/execute_fluent_code.py` receives a code snippet
using the supplied `solver` binding; its receipt proves only that code executed,
so pair it with state readback, artifact verification, and smoke evidence.

## Build a verifiable child

When the requested delta is a new mesh with the same existing setup, follow
[Replace Mesh](replace-mesh.md) before changing topology or loading the target
mesh. It owns native transfer, zone correspondence, and interpolation checks;
the steps below still define the complete child-case verification.

1. Prove the exact parent case/data and active Fluent session.
2. Inspect the live Settings/API tree before writing a mutation you are not sure
   about. For nested settings or unclear activation order, follow
   [manual fallback](manual-fallback.md) before constructing the mutation.
3. Apply changes in dependency order and reacquire downstream objects after
   topology/model changes.
4. Read back every critical delta and invariant.
5. Resolve file-backed reports/monitors/checkpoints to explicit destinations.
6. Save the child, reopen it from disk, reacquire, and repeat the critical audit.
7. Run the smallest useful smoke test, count it in the experiment horizon, and
   prove required instrumentation and the functional path the experiment needs.

For a new EWF drainage setup or a change to the drain/solve mode, identify the
film collector, direct film sink/outflow, and independent removal reports. When
bulk will be frozen, use a bounded frozen-bulk probe to prove accepted film-time
advancement, positive integrated direct removal, preserved bulk fields, and the
film ledger within the declared probe tolerance. A nonzero bulk sink evaluated
from held fields is insufficient. Reuse matching verified probe evidence;
repeat it only when the drain, relevant setup, or solve mode changes. Record an
intentional no-drain sensitivity explicitly rather than claiming drainage.

For comparisons, keep object names, hooks and flags exact. Apply numeric
tolerances only at declared paths, and normalize Windows paths only for declared
file fields using the verified server working directory. Record all accepted
normalizations. `pyansys_fluent.execution_contract` supplies offline checks;
`PyAnsys/tools/workflow_evidence.py drain-proof` checks an extracted probe receipt.
These checks do not establish steady film or whole-separator mass closure.

Return a compact build receipt: parent, changes, readback, artifact paths,
smoke/instrumentation result, unresolved uncertainty.
