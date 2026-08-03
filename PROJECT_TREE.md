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
│       ├── concepts/
│       ├── entities/
│       ├── guidance/
│       ├── physics-basis/
│       ├── setups/
│       ├── sources/
│       └── synthesis/
├── ResearchProject_wiki/
│   ├── AGENTS.md
│   ├── raw/
│   ├── template/
│   └── wiki/
│       ├── gaps/
│       ├── literature/
│       ├── model/
│       ├── progress/
│       ├── project/
│       ├── synthesis/
│       ├── technical/
│       │   ├── model-rebuild/
│       │   └── sources/
│       └── vnv/
│           ├── targets/
│           ├── validation/
│           └── verification/
├── Setups/
│   ├── active/
│   ├── future/
│   ├── past/
│   ├── reports/
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
│   ├── cfd-wiki/
│   ├── fluent-analyze-results/
│   ├── fluent-build-case/
│   ├── fluent-initialize-run/
│   ├── fluent-write-results-report/
│   ├── post-simulation-analysis/
│   ├── pyansys-workflow/
│   ├── research-project-wiki/
│   └── setup-report/
├── subagents/
├── workflows/
│   ├── fluent-analyze-and-report.md
│   └── fluent-build-and-run.md
└── template/
```

## What Goes Where
- `CFD_wiki/`: reusable CFD knowledge, literature extraction, external method logic.
- `ResearchProject_wiki/`: project decisions, progress, technical notes, V&V reports, and sign-off.
- `Setups/`: lifecycle-organized setup definitions, lineage, and numerical reports.
- `PyAnsys/`: automation, machine-readable targets, and executable workflows.
- `skills/`: repo-local Codex skills distilled from the folder-level agent instructions.
- `workflows/`: non-skill orchestration documents that call focused repo-local skills.
