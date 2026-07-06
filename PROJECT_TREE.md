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
├── Setup report/
│   ├── order-dictionary.md
│   └── *.md setup branch records
├── PyAnsys/
│   ├── cases/
│   ├── docs/
│   ├── extractors/
│   ├── knowledge/
│   ├── scripts/
│   └── src/
├── skills/
│   ├── cfd-wiki/
│   ├── research-project-wiki/
│   ├── setup-report/
│   └── pyansys-workflow/
├── subagents/
└── template/
```

## What Goes Where
- `CFD_wiki/`: reusable CFD knowledge, literature extraction, external method logic.
- `ResearchProject_wiki/`: project decisions, progress, technical notes, V&V reports, and sign-off.
- `Setup report/`: concrete setup definitions and lineage.
- `PyAnsys/`: automation, machine-readable targets, and executable workflows.
- `skills/`: repo-local Codex skills distilled from the folder-level agent instructions.
