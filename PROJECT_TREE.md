# Project Tree

Simple orientation map for the repository.

```text
P4P_knowledgeWiki/
├── AGENTS.md
├── PROJECT_TREE.md
├── CFD_wiki/
├── ResearchProject_wiki/
├── Setups/
│   ├── full-geometry/                 # setup definitions / plans
│   │   ├── mixture/
│   │   │   ├── steady-liquid-outlet/
│   │   │   └── transient-liquid-outlet/
│   │   └── vof/
│   │       └── transient-liquid-outlet/
│   ├── reports/                       # completed-run evidence
│   │   ├── full-geometry/
│   │   │   ├── mixture/
│   │   │   │   ├── steady-liquid-outlet/
│   │   │   │   └── transient-liquid-outlet/
│   │   │   └── vof/
│   │   │       └── transient-liquid-outlet/
│   │   ├── purnanto-reference/
│   │   └── <numbered folders>/        # legacy compatibility
│   ├── purnanto-reference/
│   ├── active/                        # legacy compatibility
│   ├── future/                        # legacy compatibility
│   ├── past/                          # legacy compatibility
│   ├── templates/
│   └── order-dictionary.md
├── PyAnsys/
├── skills/
├── subagents/
└── docs/
```

## What Goes Where

- `CFD_wiki/`: reusable CFD knowledge, literature extraction, external method logic.
- `ResearchProject_wiki/`: project decisions, progress, technical notes, V&V reports, and sign-off.
- `Setups/full-geometry/`: current production-geometry **setup definitions and plans**, organized by physics family and scientific campaign.
- `Setups/reports/full-geometry/`: current production-geometry **result reports and evidence**, mirroring the setup campaign path.
- `Setups/purnanto-reference/`: navigation for the historical numbered/reference setup corpus.
- `Setups/reports/purnanto-reference/`: navigation for the historical numbered/reference report corpus.
- `Setups/active|future|past` and numbered directories directly under `Setups/reports/`: compatibility storage for existing links.
- `PyAnsys/`: automation, machine-readable targets, and executable workflows.
- `skills/`: repo-local Codex skills distilled from repository workflow rules.
