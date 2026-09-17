# Inspection and build

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
