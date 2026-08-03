# Fluent Build and Run Workflow

This is a workflow, not a skill. It calls:

1. `$fluent-build-case`
2. `$fluent-initialize-run`

Read the setup Markdown directly. Do not hash or compile it.

## Block 1: build

Read `../skills/fluent-build-case/SKILL.md` and use
`$fluent-build-case`.

Continue only after the case has been saved, reloaded, and verified. Pass the
verified case, successful setup commands, important readbacks, initialization
requirements, and unresolved assumptions to the next block.

## Block 2: initialize and run

Read `../skills/fluent-initialize-run/SKILL.md` and use
`$fluent-initialize-run`.

Prove the initialization sequence before giving it to the run worker. Verify
the final case/data pair after the run.

If the run block discovers a setup problem, return to Block 1.

## Shared recovery rule

For a healthy-session command error, adjust and retry. For Fluent/gRPC loss,
wait patiently for a newer healthy generation, reconnect, reload the last
verified state, verify it, and continue. Restart may take several minutes; do
not give up or use handles from the old session.

Return the verified case/data pair, successful setup and initialization
commands, run receipt, recovery checkpoint, and unresolved warnings.
