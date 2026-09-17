# Run control

Run only a case whose build receipt proves the intended experiment.

For short discovery work, keep the scientific loop close enough to inspect the
terminal evidence and choose the next probe immediately.

For long work, checkpoint and use deterministic completion proof. A process exit
code alone is not proof; verify the requested horizon and required artifacts.

If the solver/session fails, preserve the latest valid checkpoint, recreate or
reconnect the session under the phase authority, and resume when scientifically
equivalent. Do not silently reinitialize a resumed calculation.

Unexpected physics or poor residuals are not execution-stop conditions unless
the experiment declared one. Let the evidence contract decide what can later be
claimed.
