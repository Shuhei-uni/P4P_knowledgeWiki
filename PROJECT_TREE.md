# Project Tree

Simple orientation map for the repository.

```text
P4P_knowledgeWiki/
├── AGENTS.md
├── PROJECT_TREE.md
├── CFD_wiki/
│   ├── AGENTS.md
│   ├── paper_lookup/
│   ├── raw/
│   ├── template/
│   └── wiki/
├── ResearchProject_wiki/
│   ├── AGENTS.md
│   ├── raw/
│   ├── template/
│   └── wiki/
├── Setups/
│   ├── full-geometry/
│   │   ├── mixture/
│   │   │   ├── steady-liquid-outlet/
│   │   │   └── transient-liquid-outlet/
│   │   └── vof/
│   │       └── transient-liquid-outlet/
│   ├── purnanto-reference/
│   ├── active/          # legacy compatibility
│   ├── future/          # legacy compatibility
│   ├── past/            # legacy compatibility
│   ├── reports/         # legacy compatibility
│   ├── templates/
│   └── order-dictionary.md
├── PyAnsys/
│   ├── cases/
│   ├── docs/
│   ├── extractors/
│   ├── knowledge/
│   ├── scripts/
│   └── src/
├── skills/
├── subagents/
└── docs/
```

## What Goes Where

- `CFD_wiki/`: reusable CFD knowledge, literature extraction, external method logic.
- `ResearchProject_wiki/`: project decisions, progress, technical notes, V&V reports, and sign-off.
- `Setups/full-geometry/`: current production-geometry experiments organized by physics family and scientific campaign.
- `Setups/purnanto-reference/`: navigation for the historical numbered/reference setup corpus.
- `Setups/active|future|past|reports`: compatibility storage for existing numbered records and links; do not use these paths for new Full-geomV2 campaigns.
- `PyAnsys/`: automation, machine-readable targets, and executable workflows.
- `skills/`: repo-local Codex skills distilled from repository workflow rules.
