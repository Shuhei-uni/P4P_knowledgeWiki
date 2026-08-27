---
name: setup-report
description: "Create and manage concrete Fluent setup records and separate setup-linked result reports. Route by geometry first, organize current Full-geomV2 setup plans by physics family and scientific campaign, mirror completed-run reports under Setups/reports/full-geometry, preserve the historical numbered/reference corpus, make the Fluent build contract explicit, and keep interpretation user-led by default."
---

# Setup Report

## Purpose

`Setups/` documents concrete simulation experiments with a deliberate separation between **experiment definition** and **result evidence**.

A setup record has two jobs:

1. make the intended Fluent case reproducible enough for an implementation agent to build or verify it; and
2. make the scientific reason for the case obvious enough that later analysis can collect relevant evidence.

A result report records what actually happened after execution. It must not be mixed into the setup-plan folder for new full-geometry work.

Keep reusable CFD methods in `CFD_wiki`, project-level conclusions in `ResearchProject_wiki`, and executable automation in `PyAnsys/`.

Before working on a setup or report, read:

1. repository `AGENTS.md`;
2. `Setups/index.md`;
3. the relevant geometry-programme index;
4. the matching report-programme index when results exist;
5. the parent/comparison setup and linked evidence;
6. the project roadmap when current research direction matters.

Read `Setups/order-dictionary.md` when working on the historical numbered corpus. It is not the naming authority for new full-geometry campaigns.

## Geometry first

Determine geometry from explicit mesh/case provenance before choosing a path.

### Current full geometry

New `Full-geomV2` setup work belongs under:

```text
Setups/full-geometry/<physics-family>/<scientific-campaign>/
```

Completed-run reports belong under the exact mirrored path:

```text
Setups/reports/full-geometry/<physics-family>/<scientific-campaign>/
```

Examples:

```text
Setups/full-geometry/mixture/transient-liquid-outlet/
Setups/reports/full-geometry/mixture/transient-liquid-outlet/
```

The campaign folder is the primary human-facing identity. A stable machine/reference ID such as `FG-MIX-T01` may be used in metadata and Fluent artifact names.

Do not create `02f`, `02g`, or another global number merely because the campaign comes later in time.

### Historical numbered/reference programme

The older `active/`, `future/`, `past/`, and numbered `reports/` paths remain as a compatibility layer because many records cross-link to them. Navigate them through `Setups/purnanto-reference/index.md` and `Setups/reports/purnanto-reference/index.md`.

When editing a legacy numbered record:

- preserve its assigned ID;
- preserve existing link topology unless intentionally migrating it;
- use `Setups/order-dictionary.md` for historical lineage;
- do not silently relabel it as current full geometry.

### Geometry identity gate

Never infer geometry from a setup number, branch suffix, or phrase such as “full geometry.” Require an exact mesh filename, verified case identity, or equivalent geometry-provenance evidence.

A methodological predecessor may inform a new campaign without being a case/geometry parent.

## Strict setup/report separation

For new full-geometry work:

### Setup tree

Keep only experiment-definition material in `Setups/full-geometry/...`:

- campaign `index.md`;
- `setup.md`;
- stage plans;
- controlled case matrices;
- initialization plans;
- numerical-qualification plans;
- build/readback requirements;
- pre-run monitor requirements.

### Report tree

Keep only completed-run evidence in `Setups/reports/full-geometry/...`:

- result reports;
- execution evidence summaries;
- post-analysis evidence packets;
- measured/derived numerical findings;
- interpretation sections added after user direction.

Do not create `results.md` beside `setup.md`. Do not place a stage plan in the report tree.

Each report must link back to the exact setup/stage plan that defined the run.

## Canonical campaign structure

Treat one campaign folder as the smallest canonical unit. Use the matching setup/report paths and only the file roles the campaign needs:

```text
Setups/full-geometry/<physics>/<campaign>/
├── index.md
├── setup.md                         # shared campaign contract, if needed
├── setup-<id>-<slug>.md             # independent setup, if needed
└── stage-<nn>-<slug>.md             # ordered stage plan, if needed

Setups/reports/full-geometry/<physics>/<campaign>/
├── index.md
└── <experiment-id>/                 # one setup/stage/experiment
    ├── index.md
    ├── result reports
    ├── plots/                       # local figures for this experiment
    └── evidence/                    # companion artifacts only
```

Use `Setups/templates/campaign-index-template.md` for new campaign indexes. Every campaign has one index and every reportable setup/stage/experiment has one report folder; indexes link to records instead of repeating them. New paths and filenames use lowercase kebab-case. Do not add a status folder, a second ID-based copy, a campaign-level `plots/` directory, or a new global number sequence.

For new records, include `record_type`, `programme`, `geometry`, `physics_family`, `campaign`, `record_id` (or `none`), and `lifecycle` in front matter. The descriptive campaign path is the human-facing identity; the stable ID is metadata and a link key.

Keep all plots and companion evidence under the experiment folder that produced them, using `plots/` and `evidence/` as needed. Do not create unexplained numeric folders or a shared campaign-level plot folder. Keep executable outputs in `PyAnsys/` or their source-data owner and link to them.

## Compatibility and migration rule

`active/`, `future/`, `past/`, `archived/`, `compatibility-snapshots/`, and old numbered report directories are frozen compatibility surfaces. New full-geometry work never starts there. Do not copy a canonical record into them.

If an old record is relocated, leave a redirect stub where possible. Use a detailed compatibility snapshot only when old relative links or historical provenance require the old directory depth, and link it to the canonical record. Edit the canonical record only; preserve legacy names and IDs unless an intentional migration includes link updates.

## Core principle: intent first, interpretation later

Establish the intent contract from information already supplied by the user/repository. Do not ask again when it is already clear.

Record:

- **Primary question** — what the case is trying to learn, diagnose, reproduce, verify, validate, or decide.
- **Investigation mode** — `exploratory`, `diagnostic`, `sensitivity`, `verification`, `validation`, `production/decision`, or a clearer user-defined label.
- **Controlled changes** — what is intentionally different.
- **Frozen context** — what must remain unchanged for the comparison to remain meaningful.
- **Evidence sought** — measurements/histories that help answer the question.
- **Interpretation owner** — default `user-led`; use `joint` or `agent-led` only when the user explicitly requests it.

If ambiguity would materially change the case or analysis, ask. Otherwise proceed.

Exploratory/diagnostic/sensitivity work should not receive invented pass/fail criteria. Verification/validation may use explicit criteria only when tied to the stated claim.

## Setup record structure

Use `Setups/templates/setup-record-template.md` as a flexible guide, not a mandatory form.

A useful setup normally contains:

1. intent and question;
2. geometry/mesh or verified parent identity;
3. reference and controlled changes;
4. frozen comparison context;
5. Fluent build contract;
6. build/readback gates;
7. evidence to instrument before/during the run;
8. interpretation contract;
9. filing metadata, lineage/provenance, optional stable ID, and the mirrored report-home link.

Prefer a controlled delta over restating every inherited value. Read back critical inherited settings before relying on them.

Case identity must come from explicit file/case evidence or an independently verified mapping. Never infer a case from a Fluent server/connection ID.

## Evidence planning

A setup may request pre-run instrumentation because some evidence cannot be reconstructed later. Examples include report definitions, time histories, phase fluxes, local probes, liquid inventory, VOF interface measures, DPM injection results, or EWF bookkeeping.

For each requested measurement, state why it is relevant to the primary question.

Do not require carrier/DPM/EWF analyses simply because a reusable script exists. Post-analysis should inspect the actual case and choose analyses relevant to the campaign question.

## Results behavior

Use `Setups/templates/results-report-template.md` as a flexible guide.

The default result is an **evidence packet**, not an agent verdict. It should:

- link back to the exact setup/stage plan;
- restate the question;
- identify exactly what ran;
- explain what analyses were performed and why;
- present measured/derived values;
- identify missing evidence and numerical limitations;
- separate observations from interpretations;
- set `Interpretation status: pending user direction` unless interpretation was supplied/delegated.

Do not automatically end with `keep`, `reject`, a preferred pressure/model, or the next simulation. If the user asks for interpretation, add a clearly separated interpretation section and identify whether it is user-provided, joint, or agent-proposed.

## Lifecycle

Lifecycle is metadata, not a required directory for new full-geometry work:

- `active` — currently being built/run/analysed;
- `future` — intentionally planned but not started;
- `reported` — no longer active and has useful numerical evidence;
- `archived` — historical, superseded, invalid, parked, or setup-only.

`reported` does not mean verified or validated.

Do not use `current`, `latest`, `final`, `new`, or an unqualified `results.md` for new records. Use role-based names such as `setup-<id>-<slug>.md`, `stage-<nn>-<slug>.md`, and `stage-<nn>-<slug>-results.md`.

## Completion check

Before finishing setup/report work, confirm:

- geometry programme is supported by explicit provenance;
- setup path follows geometry → physics → campaign for new full-geometry work;
- report path exactly mirrors that campaign under `Setups/reports/full-geometry/`;
- campaign has one index and each record has one canonical path;
- new record names use a role plus a descriptive lowercase slug;
- lifecycle is metadata rather than a new top-level status folder;
- compatibility copies are redirect stubs or explicitly labelled snapshots, not second authorities;
- no result report was placed inside the setup tree;
- no setup/stage plan was placed inside the report tree;
- primary question and investigation mode are visible;
- controlled changes and frozen context are unambiguous;
- Fluent implementation/readback requirements are sufficient;
- pre-run evidence is identified;
- hypotheses are not written as conclusions;
- validation language appears only with a validation contract;
- interpretation ownership is explicit and defaults to the user;
- legacy IDs/links remain traceable when historical records are involved.
