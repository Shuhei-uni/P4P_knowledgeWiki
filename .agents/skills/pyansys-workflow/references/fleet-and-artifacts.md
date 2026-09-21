# Fleet and artifact control

Use this branch when choosing a live Fluent endpoint, transferring a parent,
placing a child run, or reconciling a run after interruption.

## Keep identities separate

Record these independently:

- **scientific identity** — phase, setup/run ID, controlled delta, and parent;
- **artifact identity** — exact case/data/checkpoint and manifest identity;
- **location** — server alias, session/process, remote path, and durable copy;
- **authority** — which active phase owns or may recreate the session.

A `server_id`, session name, or a file that happens to be loaded is not proof of
scientific provenance. Resolve the case/data pair from the recorded run paths
and verify it on the selected host before using it as a parent.

## Preflight before placement

Build a small availability map: reachable endpoints, their live status, exact
parents/checkpoints available locally, free capacity, required solver/model
compatibility, and durable-transfer status. Preserve valuable active endpoints
before replacement. A busy endpoint is a resource constraint, not evidence that
the scientific candidate has failed.

Place a run near the verified parent whenever possible. If transfer is needed,
move an explicit paired case/data/checkpoint and verify size, pairing, and
readability at the destination before the child build begins. Keep ordinary
autosaves local when appropriate, but preserve selected expensive recovery and
final states at the recorded durable location.

## Resolve paths explicitly

Before a solve, resolve all case/data, report, monitor, transcript, checkpoint,
picture, and manifest destinations to concrete paths. Relative Fluent paths
often resolve against the solver's working directory, not beside the current
case. Inspect that directory or the configured report definition; do not change
the solver working directory merely to make a guessed path succeed.

Write a compact run-path map that connects each required artifact to its
scientific role. After saving, reopen from the recorded destination and verify
the paired artifact identity. The map is an execution receipt, not a duplicate
of the setup's scientific rationale.

## Reconcile interrupted work

Before restarting, determine whether the named run is live, terminal,
recoverable from a latest valid checkpoint, or uncertain. Reconcile an existing
manifest and output directory before launching the same run ID again; this is
the primary duplicate-compute safeguard. Resume only from a checkpoint whose
parent, iteration/time, and setup identity are known. Never silently initialize
over an intended continuation.
