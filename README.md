# P4P Knowledge Wiki

This repository stores the working knowledge base for the P4P geothermal separator CFD project. It is split into five linked systems:

- `CFD_wiki/`: reusable CFD knowledge, paper extraction, Fluent guidance, setup patterns, and cross-paper synthesis.
- `Project/`: the compact current authority for project-specific scientific truth, selected experiments, evidence interpretation, and claim boundaries.
- `ResearchProject_wiki/`: the retained project corpus—detailed progress, blockers, technical notes, and existing V&V records—until each area is deliberately cut over.
- `Setups/`: concrete simulation experiments. Current production work is routed geometry-first, with **setup definitions under `Setups/full-geometry/` and completed-run reports under the mirrored `Setups/reports/full-geometry/` tree**. Historical numbered/reference work is navigated separately.
- `PyAnsys/`: executable Fluent automation, case inspection, run orchestration, and machine-readable checks.

Start with:

- `AGENTS.md` for routing rules and repository operating instructions.
- `Project/index.md` for current project truth and the selected-experiment contract.
- `CFD_wiki/wiki/index.md` for reusable CFD knowledge.
- `ResearchProject_wiki/wiki/index.md` for retained project-source, progress, technical, and V&V records.
- `Setups/index.md` for simulation-programme navigation and setup/report separation.
- `Setups/full-geometry/index.md` for current `Full-geomV2` setup definitions.
- `Setups/reports/full-geometry/index.md` for current `Full-geomV2` result reports.
- `Setups/order-dictionary.md` only when working with the historical numbered lineage.

## What Is Not In The Remote Repo

Some local files are intentionally left out of GitHub because they are raw copyrighted papers, local machine artifacts, or too large for normal GitHub storage:

- `CFD_wiki/raw/`: local source PDFs used to build the CFD wiki extraction pages and lookup tables.
- `CFD_wiki/guide/Ansys_Fluent_Users_Guide.pdf`: local Fluent manual PDF; it is about 201 MB, above GitHub's normal 100 MB file limit.
- `PyAnsys/.venv/`: local Python virtual environment.
- `.DS_Store` files and Python cache files.

The remote repo does include smaller project raw files currently under `ResearchProject_wiki/raw/`, including `Shuhei Report.docx` and `Zarrouk and Purnanto 2014.pdf`.

## Required Local Sources To Rebuild

To recreate or verify the knowledge base from first principles, restore the omitted local PDFs into the same paths shown below before re-running extraction or audit work.

### Fluent Manual

- `CFD_wiki/guide/Ansys_Fluent_Users_Guide.pdf`
  - Used by `CFD_wiki/wiki/sources/ansys-fluent-users-guide-2025r2.md`.
  - Required for checking Fluent model descriptions, solver settings, and click-path guidance.

### CFD Wiki Raw Papers

Place these files back under `CFD_wiki/raw/`:

- `1-s2.0-S1738573324002365-main.pdf`
- `1032231.pdf`
- `130_Sadiq_Final.pdf`
- `1-s2.0-S0375650519304328-main.pdf`
- `33.pdf`
- `053.pdf`
- `158_Arifien.pdf`
- `informit.366967552564856.pdf`
- `1028587.pdf`
- `22.pdf`
- `Chen et al. (2025), Experimental and Simulation Research on Straight-Through Cyclone Water Separator.pdf`
- `053_Rizaldy_Final.pdf`
- `1-s2.0-S0375650524002323-main.pdf`
- `054_Mubarok_Final.pdf`
- `Zarrouk and Purnanto 2014.pdf`
- `FULLTEXT02.pdf`
- `1-s2.0-S0196890426000191-main.pdf`

These raw files support the source pages and lookup chunks under:

- `CFD_wiki/wiki/sources/`
- `CFD_wiki/wiki/setups/`
- `CFD_wiki/wiki/synthesis/`
- `CFD_wiki/paper_lookup/`

The key extracted source pages currently cover:

- Ansys Fluent Users Guide 2025 R2
- Chen et al. 2025, straight-through cyclone water separator
- Merbecks et al. 2025, GeoProp thermophysical property framework
- Mondal and Sharma 2024, upward air-water annular flow CFD
- Montesdeoca-Martinez et al. 2026, binary power plant design for two-phase geofluids
- Mubarok et al. 2020, pressure differential flow meters for two-phase geothermal flow
- Pointon et al. 2009, geothermal separator sizing CFD validation
- Purnanto, Zarrouk, and Cater 2013, two-phase flow in geothermal steam-water separators
- Rivas-Cruz et al. 2015, geothermal steam separator state-of-art review
- Skoog 2020, annular flow three-field CFD thesis
- Zarrouk and Purnanto 2014, geothermal separator design overview

Additional user-derived setup/source pages are in `CFD_wiki/wiki/sources/` for cyclone separator Fluent/SolidWorks/ICEM exemplars.

### Project Raw Inputs

These are currently present in the remote, but are still core rebuild inputs:

- `ResearchProject_wiki/raw/Shuhei Report.docx`
- `ResearchProject_wiki/raw/Zarrouk and Purnanto 2014.pdf`

They support the project-specific extraction and audit trail under:

- `ResearchProject_wiki/wiki/technical/sources/purnanto-etal-2013.md`
- `ResearchProject_wiki/wiki/model/`
- `ResearchProject_wiki/wiki/progress/`

## Rebuild Checklist

1. Clone the repo.
2. Restore omitted source PDFs into the same paths.
3. Read `AGENTS.md` before editing so content goes to the correct knowledge system.
4. Use `CFD_wiki/paper_lookup/index.md` as the first stop for paper navigation.
5. Use `Project/index.md` for current project state, then consult `ResearchProject_wiki/wiki/index.md` only for retained source/detail pages.
6. Use `Setups/index.md` to select the geometry programme and distinguish setup definitions from reports.
7. Use `Setups/order-dictionary.md` only for historical numbered-lineage work.

Do not commit `CFD_wiki/raw/`, the large Fluent guide PDF, local virtual environments, or generated cache files unless the storage strategy is changed deliberately.
