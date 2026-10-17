# File management

After pulling changes, check `git status --short` and newly added file locations.
Use the existing owner folder before creating another directory.

| Files | Location |
| --- | --- |
| Phase-specific records and scientific figures | `Project/experiments/<phase>/` |
| Shared project guidance and cross-phase comparisons | Shared folders in `Project/` |
| Shuhei / Andy report files | `Project/Final research report/Shuhei Report/` / `AndyReport/` |
| Poster sections and assets | `Project/Poster/` |
| Shared meeting material / retained exports and previews | `Project/meetings/` / `Project/meetings/output/` |
| Executable utilities / reusable Python modules | `PyAnsys/scripts/<category>/` / `PyAnsys/src/` |
| Implementation docs / historical notes | `PyAnsys/docs/` / `PyAnsys/docs/historical/` |
| Machine evidence | `PyAnsys/output/` or the recorded machine location |
| Reusable CFD literature and methods | `CFD_wiki/` |
| Agent workflows | `.agents/skills/` |

Use an operating-system temporary directory for disposable scratch files.
Keep useful previews with their report or meeting output. Root README assets
and repository configuration can stay at the root.

When moving files, update links, imports, generator paths and agent references;
remove empty source folders. Preserve `raw/` evidence and active controllers.
Before committing, check the staged diff, both sides of each move and affected
links. Keep unrelated pending edits out of the commit.
