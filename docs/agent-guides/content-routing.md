# Content routing and cross-system workflow

Route content before writing it.

1. Generic CFD methods, literature extraction, paper lookup, and reusable
   Fluent click paths belong in `CFD_wiki/`.
2. Current geothermal-separator questions, selected experiment contracts,
   findings, evidence interpretation, and claim limits belong in `Project/`.
3. Executable automation, PyFluent discovery, native-run orchestration,
   machine-readable checks, and durable implementation rules belong in
   `PyAnsys/`.
4. A repeatable task procedure belongs in the smallest applicable skill under
   `skills/`.
5. The tracked files under `ResearchProject_wiki/raw/` are immutable source
   inputs only; do not add prose beside them as a new active wiki.

## Selected experiments

Create a selected experiment only after the user or project decision gate
chooses it. Keep the setup and result packet together:

```text
Project/experiments/<campaign>/<experiment>/
  setup.md
  results.md
```

The setup records the exact parent, controlled delta, mesh/case identity,
physics, numerics, run contract, and expected evidence. The results record the
observed endpoint, residual/physical histories, completeness, limitations, and
next decision. Do not infer geometry or lineage from a setup number alone.

## Cross-system handoff

1. Read `Project/index.md` and the selected experiment first.
2. Read the applicable `CFD_wiki` source/guidance or paper lookup only when the
   scientific question needs reusable evidence.
3. Read `PyAnsys/AGENTS.md`, the focused skill, and the relevant implementation
   path for automation work.
4. Keep case-specific execution facts in the Project packet and machine
   evidence in PyAnsys output or named external artifacts.
5. Add links from the owner to the minimum supporting evidence; do not mirror
   a full page across systems.

When an old path appears in a historical Project record, either map it to the
local migrated record or mark it explicitly as retired provenance. Active links
must resolve; immutable chronology does not need cosmetic rewriting.
