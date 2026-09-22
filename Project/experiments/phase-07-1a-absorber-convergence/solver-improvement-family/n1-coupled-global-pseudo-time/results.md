# Phase 7.1A — N1 Coupled + Global Time Step result

## Status

**NOT RUN — exact parent endpoint preflight blocked on 2026-09-22.** No
solver result, convergence result, or numerical-improvement claim exists.

## Preflight evidence

- The recorded `student` endpoint could not be inspected through the PyAnsys
  status path; the read-only request returned an MCP connection failure.
- The reachable server-1 endpoint was inspected without mutation. It was
  connected, but the exact v2 prepared case and data paths from the parent
  run-path map were both reported `NOT FOUND` there.
- Because the exact v2 parent was not available on the reachable endpoint, no
  session was loaded, no solver setting was changed, no child artifact was
  saved, and no iteration was run.

This is an execution/access block, not evidence against the Coupled + Global
Time Step hypothesis. The child must remain `NOT_RUN` until the `student`
endpoint is reachable or the same verified parent pair is explicitly staged on
another authorized endpoint.

## Required next action

Reconnect to `student`, verify the two parent hashes and the 60k/715-cell zone
identity, read back the live Coupled and Global Time Step controls, and then
follow the N1 save/reopen and smoke gates in [the setup contract](deffered.md).
Do not substitute server 1’s unrelated session or the historical active-1000
solver-path parent.

## Claim limit

N1 has no scientific result. The only durable conclusion is that the planned
comparison remains well-defined but was not tested because its required parent
and endpoint were unavailable during preflight.
