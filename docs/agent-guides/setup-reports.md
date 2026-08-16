# Setup reports and lineage

`Setups/` is for concrete simulation experiments, not generic CFD guidance or day-to-day project logging.

A setup record should make two things obvious:

1. what Fluent case the implementation agent is supposed to create or verify; and
2. why that case exists scientifically.

It should not decide what a future result means.

## Route by geometry before naming the setup

Before creating a setup, identify the geometry programme from explicit mesh/case provenance.

### Current full geometry

New `Full-geomV2` setup work belongs under:

```text
Setups/full-geometry/<physics-family>/<scientific-campaign>/
```

Result reports for the same campaign belong under the mirrored path:

```text
Setups/reports/full-geometry/<physics-family>/<scientific-campaign>/
```

Use descriptive campaign names such as `mixture/transient-liquid-outlet`. Stable IDs such as `FG-MIX-T01` may be recorded in metadata and artifact filenames, but do not organize new work as one global numbered sequence.

### Strict setup/report separation

The setup tree answers **what should be run**. The report tree answers **what actually happened**.

Keep in `Setups/full-geometry/...`:

- setup/build contracts;
- stage plans;
- case matrices;
- initialization plans;
- monitor requirements;
- planned numerical qualification.

Keep in `Setups/reports/full-geometry/...`:

- completed-run reports;
- execution evidence summaries;
- post-analysis evidence packets;
- numerical findings;
- later interpretation sections based on completed evidence.

Do not create `results.md` beside `setup.md` for new full-geometry work. Do not put setup/stage plans in the report tree.

### Historical numbered/reference work

The old `active/`, `future/`, `past/`, and numbered `reports/` folders are retained as a compatibility layer for the numbered corpus. Navigate them through `Setups/purnanto-reference/index.md` and `Setups/reports/purnanto-reference/index.md`.

When editing a legacy numbered record, preserve its assigned ID and use `Setups/order-dictionary.md`. Do not renumber historical records merely to fit the new structure.

### Geometry identity rule

Never infer geometry from setup number or title alone. Require an exact mesh/case identity or equivalent provenance before filing work in the full-geometry programme.

A methodological predecessor is not automatically a geometry parent.

## Start with the intent contract

Before drafting a new setup, determine from the user and existing project context:

- the primary investigation question;
- whether the setup is exploratory, diagnostic, sensitivity, verification, validation, production/decision, or another explicitly named mode;
- the controlled change(s) and frozen comparison context;
- evidence that should be instrumented before solving;
- interpretation ownership, defaulting to `user-led`.

If these are already clear from the conversation, do not ask again. If ambiguity would materially change the case or analysis, ask the user.

Exploratory/diagnostic work should not receive invented pass/fail criteria. Verification/validation work may have explicit criteria, but those criteria must be tied to the stated claim.

## Write for the Fluent implementation agent

Prefer a concise controlled-delta definition:

- exact geometry/mesh or verified parent case;
- intentional changes;
- required inherited readbacks;
- exact boundary/model/numerical/initialization state that defines the experiment;
- operator-assisted geometry/patching/zone-identification steps;
- pre-run monitors or histories required by the intended evidence.

Do not duplicate generic CFD theory or every inherited setting when a parent link and critical readbacks are enough.

## Result reports are evidence packets

A result report should be readable before anyone agrees on an interpretation. It should state:

- the exact setup/stage link;
- what the setup was trying to investigate;
- what was actually run;
- what analyses were performed and why they were relevant;
- measured and derived results;
- numerical/evidence limitations;
- neutral observations and unresolved items;
- `Interpretation status: pending user direction` unless interpretation was already delegated or criteria were pre-agreed.

Do not automatically end reports with `keep`, `reject`, a preferred pressure/model, or a next experiment. Ask focused interpretation questions and append an interpretation section only after user direction.

## Post-analysis is adaptive

The post-simulation analysis workflow should discover the live/file state first, then propose setup-specific analyses. Existing carrier/DPM/EWF scripts are reusable tools, not mandatory categories. When they do not answer the setup question, use or create a read-only custom extraction for the relevant Fluent quantity and record how it was obtained.

## Naming and lineage

For new full-geometry work:

1. choose the geometry programme;
2. choose the physics family;
3. choose a descriptive scientific campaign;
4. place setup/stage plans in `Setups/full-geometry/...`;
5. place completed-run reports in the exactly mirrored `Setups/reports/full-geometry/...` path;
6. record an optional stable machine/reference ID in metadata.

For legacy numbered work:

1. preserve assigned sequence/branch IDs;
2. avoid `current`, `latest`, or `final` in filenames;
3. update `Setups/order-dictionary.md` and affected links after a rename or lineage change.

Lifecycle (`active`, `future`, `reported`, `archived`) is metadata, not a required top-level folder for new full-geometry work and not a statement of scientific claim strength.
