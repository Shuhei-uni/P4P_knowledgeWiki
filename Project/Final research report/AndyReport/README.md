# AndyReport

Andy’s working final report. This folder follows the structure of the neighbouring `Shuhei Report` folder.

| File | Purpose |
| --- | --- |
| [Writing reference: findings and claims](review/project-findings-and-report-claims.md) | Project-wide evidence, interpretations, claim limits and report plan |
| [Complete draft](draft/draft-v1.md) | All six parts assembled for reading |
| [Front matter](draft/00-front-matter.md) | Title, abstract, declaration, contents and glossary |
| [Introduction and literature review](draft/01-introduction-and-literature-review.md) | Original objectives, project motivation and copied literature section |
| [Model and methods](draft/02-model-and-methods.md) | Setup, comparison design, verification and validation assessment |
| [Results](draft/03-results.md) | Recorded findings and comparison limits |
| [Discussion and conclusions](draft/04-discussion-conclusions-and-future-work.md) | Interpretation and future work |
| [References and appendices](draft/05-references-and-appendices.md) | References, evidence routes and supporting details |
| [Context](Andy-Context.md) | Scope and author decisions |
| [Revision review](revision-review.md) | Comparison with Shuhei and remaining drafting work |
| [Review files](review/README.md) | LaTeX snapshot, source checks and previous drafts |

Edit the numbered Markdown sections and refresh `draft/draft-v1.md` as the assembled reading copy. **Current author instruction (17 October 2026): update Markdown only until explicitly asked to update LaTeX and PDF.** Do not run the synchroniser with `--write` during this drafting stage: it also changes LaTeX. When an export is requested, run `python3 review/sync-report.py --write` from this folder, then compile the existing `review/latex/ESB_report_template.tex`. The script skips the approved introduction and literature review. Check those exports separately against the canonical Markdown; substantive changes to their wording require author direction. Figures are under `figures/`, with literature figures under `figures/literature/`. Scientific evidence remains in Project experiment records.

Use the writing reference before revising the report. The confirmed format is a maximum of 30 body pages in 12 pt Times New Roman. The current Markdown has **11,865 body words**, including headings, captions and tables. The [bounded three-cycle review](review/bounded-review-2026-10-18/README.md) records the fixed snapshots, evidence checks, targeted revisions and fresh verification after each revision. The introduction and literature review remain unchanged.

Figure 5 is an original conceptual map of the model regions. Figures 6 and 7 retain Shuhei Yokkaichi's credit; Figure 7 is the previously labelled adaptation with unchanged numerical values. Figures 8 and 9 retain the audited pool and mesh-comparison plots. Existing figure files are unchanged by the bounded review.

The latest authorised [LaTeX/PDF export](review/latex/ESB_report_template.pdf) includes the bounded-review revisions: **11,865 body words, 30 body pages and 53 pages overall**, in 12 pt Times New Roman. Long-table padding was reduced slightly; template margins, body line spacing and figure sizes are unchanged. See [export checks](review/layout-check-2026-10-18-bounded-review.json). The [previous annotated PDF](review/export-2026-10-18-bounded-review/previous-annotated-report.pdf) is preserved. The DPM follow-up remains deferred at the author’s request.

The Methods opening now names Ansys Fluent and identifies 2025 R2 for the later reconstruction and same-computer tetrahedral repeat. The historical sweep retains its recorded 2024 R2 version. This wording and the official project title are included in the authorised 18 October LaTeX/PDF export.
