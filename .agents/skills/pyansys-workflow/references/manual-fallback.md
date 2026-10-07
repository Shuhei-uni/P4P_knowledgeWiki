# Manual-backed Fluent fallback

Use this branch for nested settings, unclear activation order, or when the live
Settings/API tree cannot resolve the meaning, prerequisites, or writable path
for a required state. For these difficult setup changes, prefer a TUI recipe
derived from the version-matched Fluent guides and their screenshots.

1. Fingerprint the exact Fluent version, solver mode, active models, object
   names, and relevant parent state.
2. Find the relevant version-matched official Fluent guide section. Open and
   visually inspect its screenshots/figures as well as the surrounding text.
3. Extract the panel hierarchy, prerequisite toggles, nested controls, and
   activation order. Use them to form a TUI command sequence; confirm command
   names and prompt order against the official TUI reference or live TUI help.
4. Pin the sequence to the documented version/state and test it on a recoverable
   child. Use a verified Settings/API route if the TUI route is unavailable.
5. Prove the intended state by readback where possible, then save/reopen and
   verify persistence.

A TUI fallback is a technical implementation choice, not a human approval gate.
The required bar is evidence that the route is version-correct, scoped, and
verifiable.

## Build a usable recipe

Fingerprint the exact problem before searching: Fluent release, solver mode,
active models/phases, relevant zones, current Settings path/state, attempted
operation and error, and the precise desired end state. Use local guide/source
pointers when available, then retrieve the official version-matched guide if
needed. Search for configuration mechanics: model activation, prerequisite
panels/commands, option meanings, and ordering.

Inspect the actual guide images with an image viewer or PDF/page screenshot
tool. A text extraction or figure caption alone does not show nested controls.
Record what each relevant screenshot establishes and combine it with the
surrounding instructions to build the activation sequence. Screenshots establish
GUI structure and dependencies; confirm the corresponding TUI syntax and prompt
responses with the official TUI reference or live command help before execution.
If an image is unavailable or unreadable, record that gap and use other verified
documentation to complete the recipe.

Keep configuration mechanics distinct from scientific choices. The manual can
establish how to activate a model or write a setting; the active `setup.md` and
phase contract establish which value, surface, horizon, or comparison is wanted.

Record the guide section, screenshot/figure or page reference, exact release,
TUI syntax source, command sequence and prompt responses, required prior state,
all values/units, and expected readback. This is the reproducible setup recipe.

Test a new recipe on a recoverable child. Read back the state, save it, reopen
it, reacquire the relevant objects, and repeat the audit. Return the smallest
version-pinned recipe that worked plus its evidence; retain an exact capability
gap when neither documented route can be proven.

Return either a verified recipe or the exact unresolved capability gap.
