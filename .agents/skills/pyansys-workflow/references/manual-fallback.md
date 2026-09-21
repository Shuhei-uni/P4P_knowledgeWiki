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

## Build a usable recipe

Fingerprint the exact problem before searching: Fluent release, solver mode,
active models/phases, relevant zones, current Settings path/state, attempted
operation and error, and the precise desired end state. Search the official
manual for the configuration mechanics first—model activation, prerequisite
panels/commands, option meanings, and ordering—then translate only the verified
portion into the live API.

Keep configuration mechanics distinct from scientific choices. The manual can
establish how to activate a model or write a setting; the active `setup.md` and
phase contract establish which value, surface, horizon, or comparison is wanted.

When a GUI-only clue is material, capture the manual section, screenshot or
figure reference, and the exact release. A settings-path guess is not a recipe.
For a TUI/journal fallback, record the command sequence, required prior state,
all values/units, expected readback, and the reason the Settings route was
insufficient.

Test a new recipe on a recoverable child. Read back the state, save it, reopen
it, reacquire the relevant objects, and repeat the audit. Return the smallest
version-pinned recipe that worked plus its evidence; retain an exact capability
gap when neither documented route can be proven.

Return either a verified recipe or the exact unresolved capability gap.
