# Setup reports and lineage

`Setups/` is for concrete simulation instances, not generic CFD guidance or day-to-day project logging.

A setup record should make two things obvious:

1. **what Fluent case the implementation agent is supposed to create or verify**; and
2. **why that case exists scientifically**.

It should not decide what the future result means.

## Start with the intent contract

Before drafting a new setup, determine from the user and existing project context:

- the primary investigation question;
- whether the setup is exploratory, diagnostic, sensitivity, verification, validation, production/decision, or another explicitly named mode;
- the controlled change(s) and frozen comparison context;
- evidence that should be instrumented before solving;
- interpretation ownership, defaulting to `user-led`.

If these are already clear from the conversation, do not ask again. If the ambiguity would materially change the case or analyses, ask the user.

Exploratory/diagnostic work should not receive invented pass/fail criteria. Verification/validation work may have explicit criteria, but those criteria must be tied to the stated claim.

## Write for the Fluent implementation agent

Prefer a concise controlled-delta definition:

- parent/reference case;
- intentional changes;
- required inherited readbacks;
- exact boundary/model/numerical/initialization state that defines the experiment;
- geometry or patching steps where the user wants the agent to stop and ask for help;
- pre-run monitors or histories needed for the intended evidence.

Do not duplicate generic CFD theory or every inherited setting when a parent link and critical readbacks are enough.

## Results are evidence packets by default

A setup-linked `results.md` should be readable before anyone agrees on an interpretation. It should state:

- what the setup was trying to investigate;
- what was actually run;
- what analyses were performed and why they were relevant;
- measured and derived results;
- numerical/evidence limitations;
- neutral observations and unresolved items;
- `Interpretation status: pending user direction` unless interpretation was already delegated or criteria were pre-agreed.

Do not automatically end reports with `keep`, `reject`, a preferred pressure/model, or a next experiment. Ask focused interpretation questions and append an interpretation section only after user direction.

## Post-analysis is adaptive

The post-simulation analysis skill should discover the live/file state first, then propose setup-specific analyses. Existing carrier/DPM/EWF scripts are reusable tools, not mandatory analysis categories. When they do not answer the setup question, use or create a read-only custom extraction for the relevant Fluent quantity and record how it was obtained.

## Ordering and naming

1. Read [`Setups/order-dictionary.md`](../../Setups/order-dictionary.md) before creating, renaming, or reorganizing setup files.
2. Preserve assigned numbered sequence.
3. Add a number or branch suffix such as `08`, `08a`, or `08b` instead of rewriting older setup identity.
4. Do not use `current`, `latest`, or `final` in setup filenames.
5. Update cross-links and wiki references after a rename or new branch.

Lifecycle (`active`, `future`, `reported`, `archived`) is separate from scientific claim strength. A `reported` setup is not automatically verified or validated.
