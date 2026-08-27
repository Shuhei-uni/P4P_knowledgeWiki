# Setup reports and lineage

> **LEGACY FOR NEW WORK**
> New selected experiments belong in [`Project/experiments/`](../../Project/experiments/), where `setup.md` and `results.md` are co-located.
> Do not create new mirrored setup/report records under `Setups/`.
> This guide now covers retained setup/report sources, historical lineage, and explicit repair of those records.

`Setups/` retains concrete simulation experiments and their provenance, not generic CFD guidance or day-to-day project logging.

A setup record should make two things obvious:

1. what Fluent case the implementation agent is supposed to create or verify; and
2. why that case exists scientifically.

It should not decide what a future result means.

For current work, read [`Project/index.md`](../../Project/index.md) and the [`Project experiment contract`](../../Project/experiments/README.md) first. Read `Setups/index.md` and the relevant retained programme index only when existing setup/report provenance or an explicit historical repair is needed.

## Route by geometry before naming the setup

Before reviewing or explicitly repairing a retained setup, identify the geometry programme from explicit mesh/case provenance.

### Retained full geometry

Existing `Full-geomV2` setup records remain under:

```text
Setups/full-geometry/<physics-family>/<scientific-campaign>/
```

Existing result reports for the same campaign remain under the mirrored path:

```text
Setups/reports/full-geometry/<physics-family>/<scientific-campaign>/
```

Use the retained campaign paths to locate existing records. Stable IDs such as `FG-MIX-T01` may be recorded in metadata and artifact filenames; do not organize new work as a Setups campaign or global numbered sequence.

### Retained setup/report separation

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

Do not create new records in this retained mirror. Existing records keep results separate from setup plans; do not put setup/stage plans in the report tree.

### Canonical campaign unit

For retained work, one campaign directory is the smallest historical unit. Keep its shape predictable:

```text
Setups/full-geometry/<physics-family>/<campaign>/
├── index.md                         # campaign map and status
├── setup.md                         # optional shared campaign contract
├── setup-<id>-<slug>.md             # independent setup definition, when needed
└── stage-<nn>-<slug>.md             # ordered stage plan, when needed

Setups/reports/full-geometry/<physics-family>/<campaign>/
├── index.md                         # campaign report map
└── <experiment-id>/                  # one setup/stage/experiment
    ├── index.md
    ├── result reports
    ├── plots/                        # local figures for this experiment
    └── evidence/                     # optional companion artifacts
```

Use only the branches that the campaign needs. A campaign with one setup may use `setup.md`; a staged campaign may use `setup.md` plus stage plans. Every reportable setup/stage/experiment gets one report folder, and any plots or evidence belong inside that folder. If an experiment has multiple run packets, keep those files together under the experiment folder rather than creating a campaign-level plot directory.

Every retained campaign directory has one `index.md`, and every setup or result record has a single canonical path. Indexes should link to records and report their lifecycle; they should not become second copies of the records. Retained paths and filenames use lowercase kebab-case. Stable IDs belong in metadata and links, not in a new global numbering sequence.

Use `Setups/templates/campaign-index-template.md` when explicitly repairing a retained campaign rather than inventing a new navigation format.

For retained records being repaired, preserve or add machine-readable filing metadata for at least `record_type`, `programme`, `geometry`, `physics_family`, `campaign`, `record_id` (or `none`), and `lifecycle`. The historical campaign path remains the primary identity.

### Compatibility is not a second source of truth

`active/`, `future/`, `past/`, `archived/`, `compatibility-snapshots/`, and old numbered report directories are compatibility surfaces only. Do not add new full-geometry work there. Do not copy a canonical setup or report into one of those locations merely to make navigation easier.

When an existing record is moved, prefer a small redirect stub at the old path. Keep a detailed compatibility snapshot only when old relative links or historical provenance require the original directory depth, and label it as a snapshot with a link to the canonical record. One location must be authoritative; later edits belong there.

Keep plots and small evidence attachments inside the matching experiment folder under `plots/` or `evidence/`. Keep executable outputs and source artifacts in their owning `PyAnsys/` or raw-data location and link to them. Do not put result evidence in the setup tree or create a shared campaign-level `plots/` directory.

### Historical numbered/reference work

The old `active/`, `future/`, `past/`, and numbered `reports/` folders are retained as a compatibility layer for the numbered corpus. Navigate them through `Setups/purnanto-reference/index.md` and `Setups/reports/purnanto-reference/index.md`.

When editing a legacy numbered record, preserve its assigned ID and use `Setups/order-dictionary.md`. Do not renumber historical records merely to fit the new structure.

### Geometry identity rule

Never infer geometry from setup number or title alone. Require an exact mesh/case identity or equivalent provenance before filing work in the full-geometry programme.

A methodological predecessor is not automatically a geometry parent.

## Start with the intent contract

Before reviewing or explicitly repairing a retained setup, determine from the user and existing project context:

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

For historical Setups maintenance:

1. choose the geometry programme;
2. choose the physics family;
3. choose a descriptive scientific campaign;
4. preserve setup/stage plans in the existing `Setups/full-geometry/...` source;
5. preserve completed-run reports in the exactly mirrored `Setups/reports/full-geometry/...` source;
6. if a retained repair requires a new record, name it with its role (`setup`, `stage-<nn>`, or `run-<id>`) and a descriptive lowercase slug;
7. record an optional stable machine/reference ID in metadata.

For legacy numbered work:

1. preserve assigned sequence/branch IDs;
2. avoid `current`, `latest`, or `final` in filenames;
3. update `Setups/order-dictionary.md` and affected links after a rename or lineage change.

Lifecycle (`active`, `future`, `reported`, `archived`) is metadata, not a required top-level folder for retained full-geometry work and not a statement of scientific claim strength.

Do not use `current`, `latest`, `final`, `new`, or an unqualified `results.md` as a new record name. Preserve legacy names and IDs when editing historical records; the naming rule is for new additions and intentional migrations only.
