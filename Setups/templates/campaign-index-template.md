---
record_type: "campaign-index"
programme: "full-geometry"
geometry: "<exact geometry / mesh / case programme>"
physics_family: "<mixture / vof / dpm-ewf / other>"
campaign: "<lowercase-kebab-case-campaign>"
lifecycle: "active | future | reported | archived"
setup_home: "Setups/full-geometry/<physics>/<campaign>/"
report_home: "Setups/reports/full-geometry/<physics>/<campaign>/"
---

# <Programme> — <Physics family> — <Campaign>

> This index is navigation and filing metadata, not a second copy of the setup or result records. Keep one canonical record at each linked path.

## Purpose

- Scientific question: `<one or two sentences>`
- Investigation mode: `exploratory` / `diagnostic` / `sensitivity` / `verification` / `validation` / `production-decision`
- Geometry identity: `<exact mesh/case evidence or link>`
- Interpretation owner: `user-led` by default / `joint` / `agent-led if explicitly requested`

## Canonical homes

- Setup definitions: `Setups/full-geometry/<physics>/<campaign>/`
- Completed-run reports: `Setups/reports/full-geometry/<physics>/<campaign>/`

## Records

| Role | ID | Path | Lifecycle | Linked report or evidence |
|---|---|---|---|---|
| `setup` / `stage-plan` / `result-report` | `<campaign-scoped ID or none>` | `<relative link>` | `active` / `future` / `reported` / `archived` | `<relative link or none>` |

## Filing rules

- Keep setup definitions and completed-run evidence in their separate canonical trees.
- Give each reportable setup/stage/experiment its own folder under the report home; keep that experiment's `plots/` and `evidence/` inside the same folder.
- Use `setup.md` for a shared campaign contract, `setup-<id>-<slug>.md` for an independent setup, and `stage-<nn>-<slug>.md` for an ordered stage plan.
- Use `stage-<nn>-<slug>-results.md` or `run-<id>-<slug>-results.md` for new result packets.
- Use lowercase kebab-case for new paths and filenames; preserve legacy IDs and names when editing historical records.
- Do not add `active/`, `future/`, `past/`, `archived/`, or compatibility copies for new work.
- If an old link must remain, use a redirect stub or a clearly labelled compatibility snapshot that points back here.
