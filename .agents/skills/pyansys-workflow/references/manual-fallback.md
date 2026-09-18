# Manual-backed Fluent fallback

Use this branch when the live Settings/API tree cannot confidently resolve the
meaning, prerequisites, activation order, or writable path for a required state.

1. Fingerprint the exact Fluent version, solver mode, active models, object
   names, and relevant parent state.
2. Read the version-matched official Fluent documentation for that exact
   setting/command.
3. Prefer a Settings/API route when one exists.
4. If a TUI/journal route is needed, pin it to the documented version/state and
   test it on a recoverable child.
5. Prove the intended state by readback where possible, then save/reopen and
   verify persistence.

A TUI fallback is a technical implementation choice, not a human approval gate.
The required bar is evidence that the route is version-correct, scoped, and
verifiable.

Return either a verified recipe or the exact unresolved capability gap.
