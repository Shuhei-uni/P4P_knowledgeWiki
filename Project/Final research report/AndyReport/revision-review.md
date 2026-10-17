# Draft revision review — 16 October 2026

**Current review:** [bounded review, 18 October 2026](review/bounded-review-2026-10-18/README.md). It supersedes the status statements below where explicitly resolved: the reference-year identity is reconciled, the Methods opening clarifies scope/efficiency definitions, and spatial and injection inputs have been added. The older review below is retained as history.

The working report is now the six Markdown sections in `draft/`, assembled in `draft/draft-v1.md`. The imported LaTeX project is retained in `review/latex/`; earlier Word/Markdown versions are in `review/previous-draft/`. The move on 16 October 2026 changed file organisation, not the scientific findings.

| Topic | Last year's wing report | Shuhei's current final report | Action in Andy's working draft |
| --- | --- | --- | --- |
| Setup | Clear Setup subsections for each physics domain | Domain, physical assumptions, boundary conditions, mesh, solver and comparison design | Integrated domain, inlet, collector, film, DPM and resolved-drain methods with case-specific inputs |
| Verification | Separate mesh/domain checks | Integrated numerical assessment and dedicated results discussion | Added an explicit Verification and validation assessment chapter; retained failed or incomplete checks |
| Validation | Comparison sections | Explicit physical-validation limits | Added a validation-basis subsection; replication is not labelled independent physical validation |
| Physical explanation | Setup followed by evidence | Liquid entry, wall transport, collection and drainage form a connected argument | Explained the closed-collector and open-drain distinction before the result families |
| Results | Figures support each physics question | Stronger geometry, spatial and history figures than Andy's first draft | Retained VOF/field-sensitivity plots and added credited ramp and direct-film-drain figures |
| Reproducibility | Short setup account | Substantial methods appendix, settings and figure register | Added an appendix for the still-needed exact case settings; no guessed parameters |
| Authorship | Different project and partner | Shuhei's separate simplified-domain/wall-film contribution | The draft integrates project findings; reused figures retain creator/source attribution |

## Literature review transfer

Current authority: `/Users/andy/Desktop/P4P/Lit Review/qtra338_First_Report_ENGSCI700A.pdf`, PDF pages 6–11. The literature paragraphs, subsection headings, captions and callouts now match that submitted version, with report figure numbers 2–4 retained. Existing higher-resolution images were checked against the PDF and retained. `review/literature-final-pdf-check.json` records verification and differences from the earlier DOCX copy; `review/literature-copy.json` remains the historical extraction record. The source typo “contruct” is retained for exact copying; citation completeness and the prospective validation claim still need a later substantive review.

Do not silently rewrite this section: the user requested a direct copy. Remaining review issues include the 2014/2015 Zarrouk–Purnanto publication year, incomplete publication details in several recovered entries, and its original prospective claim about addressing validation. The later validation section states the actual completed scope. The report remains a draft until these issues and the declaration are resolved with the author.

## Remaining work

1. Reconcile the copied literature review's 2014/2015 design-overview year and prospective validation wording when the author authorises changes to that section. Missing bibliography entries have been recovered from the final first-report PDF, but incomplete publication details still need checking.
2. Resolve the tet/M04 fluid-domain discrepancy before any mesh-only performance claim. Exact settings and wall-resolution evidence remain in the linked project records; select final methods detail during the next report revision.
3. Complete acknowledgements and review the unsigned declaration and AI-use description.
4. Preserve the distinction between local numerical passes, stationary operating qualification and physical validation. Final film/mesh/design endpoints must not inherit a pass from an earlier window.
5. When the author requests a LaTeX/PDF update, recompile the revised Markdown, retain 12 pt Times New Roman and the template layout, and check the 30-page body limit. Until then, edit Markdown only.

Shuhei source reviewed: `P4P_shared/Project/Final research report/Shuhei Report/draft/`, including the consolidated report and the methods/discussion files. His draft is more developed in physical description, figure support and methods detail. The integrated draft now places the wall-film and startup results alongside full-geometry removal, numerical verification, particle tracking and the conditional fixed-iteration cost comparison. Neither draft's status should be treated as physical validation.

## Project-wide findings and report plan

See [Project findings, evidence and report claims](review/project-findings-and-report-claims.md), reviewed against main `619d46c` on 16 October 2026. This replaces the narrower Phase 9/10 review. It covers all phase folders, the ramp/sink improvement, local film and carrier balance successes, corrected drainage verification, conditional reconstruction and remaining model limits. It also maps findings to the original objectives and recommends section-level changes and figure credits.

User decisions: present one integrated project story; preserve technical comparison limits and figure attribution; use a 30-page body limit with 12 pt Times New Roman. Tet/M04 geometries were intended to match, but the recorded volume discrepancy is unresolved. Disputed Phase 5 completion claims remain excluded because the user is unsure and supporting terminal evidence is missing.

The main draft implements this plan; the LaTeX body is retained as an earlier export snapshot. Results include the ramp/sink mass account, active-bulk local film passes, direct drainage and corrected analytical benchmark alongside unresolved operating-state limits. The enthalpy table shows incomplete particle mass beside the assumed-capture estimate. Discussion and conclusions assess each original objective. Introduction and literature text, figures and numbering were protected throughout. Source and layout verification are recorded in `review/`.

## Marker-perspective review — 17 October 2026

Three review passes revised the Markdown for a reader with engineering knowledge but no access to the internal experiment history. Independent read-only reviews checked clarity, the argument and the final revision; selected scientific definitions were checked against the owning Project records and diagnostic implementation.

| Pass | Changes made |
| --- | --- |
| Reader orientation | Explained the two liquid-removal approaches and the roles of Mixture, VOF, DPM and EWF. Replaced internal workflow terms with descriptions of the calculation. Defined film time, particle fates and outlet dryness. Added the cell/node distinction with an Ansys source. |
| Story and interpretation | Added a short Results map and transitions between model configurations. Included the later matched-inlet retention finding in the abstract. Clarified that the 37% difference is at matched iteration endpoints, not a converged performance gain. Explained the denominators of film-error percentages. |
| Consistency and concision | Corrected the scope of the spatial-comparison ranges, distinguished July project efficiency estimates from the published Purnanto reference, and condensed repeated Discussion limits. Kept the four original objectives and the positive component achievements. |

Current Markdown body count: **10,880 words**, including headings, captions and tables, using the existing Pandoc-based count method. All **55 local link/image targets** checked exist; figure numbering remains 1–8 and body table numbering 1–7. The assembled reading copy matches the six numbered parts. The introduction/literature file, figure files and the complete LaTeX/PDF directory retain their pre-review hashes.

No LaTeX synchronisation or PDF compilation was performed. The earlier 28-page body count applies only to the saved export; the revised body must be checked against the 30-page limit when the author requests an export. The copied literature's citation/year and prospective-validation issues, author declaration/acknowledgements, unresolved geometry discrepancy and missing experiment evidence remain as documented above. These were not resolved by prose changes.

## Authorised review export — 17 October 2026

At the author's request, the existing LaTeX project was synchronised and compiled after the marker-perspective revisions. The PDF has **28 body pages**, below the 30-page maximum, and **44 pages overall** including excluded material. Body font remains 12 pt Times New Roman; template margins and 1.15 spacing are unchanged. The expanded glossary's symbols are kept together on a separate front-matter page. Markdown/LaTeX synchronisation passed; compilation had no errors, missing glyphs, undefined references or overfull boxes. All pages received visual review, with Table 5, Figure 8 and the glossary inspected at larger size. See `review/layout-check-2026-10-17.json`. Future drafting remains Markdown-only until another export is requested.

## Figure labels and adversarial review — 17 October 2026, after export

Three further passes checked scientific claims and the experimental argument: independent mass/film and mesh/particle audits alongside a process review; source checks of the revised text; then a final marker/process read. This was a review of saved evidence and analysis definitions, not a new Fluent campaign or a complete reconstruction of every raw result.

| Marker concern | Change |
| --- | --- |
| Internal case names obscure the comparison | Figures 6–8 now identify drain state, initial liquid level, mesh cell count and solver iteration directly. All plotted values are unchanged. Figures 1–5 remain unchanged. Figure 6 retains partner credit and is labelled an adaptation. |
| The experiments can read as disconnected attempts | Methods now links baseline instability to removal, discharge control and wall-film transport, then explains why later historical comparisons remained useful despite failed operating qualification. Separate configurations remain distinct. |
| A local success can sound like global convergence | Corrected the duct claim to final-100 numerical acceptance versus all-500 safety guards. Added transient durations, unavailable steel-wall inner residuals and the late film Courant warning. The 70.32% local drain reduction is compared with only 1.70% lower total film. |
| Acceptance and parameter choices need justification | Appendix B states thresholds, windows and denominators. Appendix D explains inherited settings, uncalibrated collector/control choices, roughness, macroscopic VOF scope and requested versus achieved wall layers. Active bulk is distinguished from reciprocal film–bulk momentum coupling. |
| Output agreement and runtime can be overstated | Clarified prescribed enthalpy inputs without an energy solve, escape-boundary ambiguity, changed solver version and missing historical tracking cap. Reported unequal particle workloads and spatial-projection coverage; neither timing nor field differences isolate mesh accuracy. |

The current body has **11,152 words**, 272 more than the last export. All **186 local link/image occurrences** in the numbered draft and writing reference resolve. The assembled draft matches its six parts; figure numbering is 1–8 and main table numbering is 1–7. Source and output hashes for the three replots pass, and their layouts were inspected. All 31 protected introduction/literature and LaTeX/PDF files remain unchanged. See [verification record](review/adversarial-review-2026-10-17.json).

Remaining limits are scientific, not wording defects: final complete bulk–film–particle balance, stationarity, geometry parity, incomplete particle fates and physical validation are unresolved. Figure 6's upstream analysis summary is absent locally; its exact plotted values were recovered from Shuhei's original provenance, whose image hash passed. No fresh raw-history audit is claimed for that plot. The protected literature still prospectively says the project addresses direct field validation, and Figure 4 lacks printed axis titles; these need a later authorised literature revision, alongside its reference details. The author declaration and acknowledgements remain unfinished.

The LaTeX/PDF was not regenerated in this review. Its **28-body-page** count applies to the saved earlier export; the revised Markdown and new figure dimensions require a new page check at the next requested export.

## Authorised export of revised claims and figure labels — 17 October 2026

The latest requested export synchronised the existing LaTeX project with all six Markdown parts and the updated Figures 6–8. The compiled PDF remains **28 body pages**, from Introduction (physical page 11) through Conclusions and future work (physical page 38); references begin on printed page 29. There are **46 pages overall**, including excluded front matter, references and the expanded appendices. The body has **11,152 words**. No shortening, font reduction or margin/spacing changes were needed.

Markdown/LaTeX parity passed with no differences. Compilation had no errors, missing glyphs, undefined references or overfull boxes. All 46 pages received visual review; the updated figures and new appendix tables were inspected at larger size. An independent audit confirmed the new claims and tables and exact RGB-pixel agreement between all three updated figure assets and their PDF images. The six Markdown sources, protected introduction/literature LaTeX, main source and preamble remain unchanged by this export. [Latest layout verification](review/layout-check-2026-10-17-label-export.json) supersedes the earlier page-count snapshot for the current PDF. Subsequent drafting remains Markdown-only until another export is requested.

## Official-title and latest-Markdown export — 18 October 2026

The authorised export restores **Geothermal steam-water separator design CFD modelling and optimising** on the existing title page and adds the latest Methods opening from Markdown. All updated figure labels are retained. The final PDF has **29 body pages**, **47 total pages** and **11,172 body words**. Flexible figure placement removes the intermediate build's two-line final page without altering text, font sizes, margins, figure dimensions or line spacing.

Markdown/LaTeX synchronisation and compiler checks passed. All pages received visual review; an independent audit confirmed the official title, version sentence, body-page count and exact pixel agreement for Figures 6–8. The six Markdown sources, protected introduction/literature LaTeX and preamble were unchanged by export. See [current layout verification](review/layout-check-2026-10-18.json). Later drafting remains Markdown-only until another explicit export request.
