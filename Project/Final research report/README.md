# Final research reports

| Author | Working report | Complete draft |
| --- | --- | --- |
| Andy | [AndyReport](AndyReport/README.md) | [Combined Markdown draft](AndyReport/draft/draft-v1.md) |
| Shuhei | [Shuhei Report](<Shuhei Report/>) | [Combined Markdown draft](<Shuhei Report/draft/draft-v1.md>) |

Both reports use `draft/`, `figures/` and `review/`. AndyReport replaces `andy-draft/` and the external Final Report drafting location. Shared guidance and the supplied template remain here.

## Shared report guidance

- [Part 4 Projects Handbook — revision 02 March 2026](<P4P Projects Handbook 2026.md>): full user-supplied text, including report requirements, learning outcomes, assessment and submission guidance. Its 30-page limit differs from the 25-page limit in [Rough Guidance](<Rough Guidance.md>); the discrepancy is recorded in the handbook transcription.

## Shuhei's report

The report examines **how liquid moves through the separator and reaches a collection route**. Its main contribution connects mesh and inlet choices to liquid retention, collection and wall-film behaviour, supported by practical absorber and startup development. Mesh and inlet assumptions, absorber-free accumulation, wall roughness, film growth, release and drainage form a connected research argument.

The 14 October 2026 revision makes the central insight explicit: wall capture is one stage of collection, and outlet liquid flow must be assessed with storage, release and external removal. The latest review checks the figure sequence and prose separately. Short captions name each display’s main finding and essential conditions; interpretation and detailed settings stay in the body or appendices. Results transitions complete each comparison before introducing the next question. A report-specific conceptual overview is Figure 1, and the abstract and conclusions follow the same argument. The [revision review](<Shuhei Report/revision-review.md>) records the changes and checks.

## Reading order

| Part | File | Purpose |
| --- | --- | --- |
| Front matter | [Title, abstract, declaration, contents and glossary](<Shuhei Report/draft/00-front-matter.md>) | State the research problem, key results and author information |
| 1 | [Introduction and literature review](<Shuhei Report/draft/01-introduction-and-literature-review.md>) | Establish liquid transport, collection and film release as the physical basis for the questions |
| 2–3 | [Model basis, development methods and results](<Shuhei Report/draft/02-03-model-development-methods-and-results.md>) | Establish the inherited model, then introduce each development method beside its findings and the next question |
| 4 | [Discussion, conclusions and future work](<Shuhei Report/draft/04-discussion-conclusions-and-future-work.md>) | Connect the findings and identify the next useful model and design comparisons |
| Supporting material | [References and appendices](<Shuhei Report/draft/05-references-and-appendices.md>) | Retain implementation, case identities, detailed numerical checks, figure provenance and contribution statement |
| Complete draft | [Combined Markdown report](<Shuhei Report/draft/draft-v1.md>) | The six parts assembled in the same order, with working internal links |

## Evidence selected for this draft

The central startup and wall-treatment sequence uses the 60,964-cell simplified domain. It includes the historical reduced-feed hold and checked ramp, common-parent roughness and accretion screens, contact collection, shortened startup and frozen-bulk film development to 500 ms.

The report also includes a concise account of the later release-mechanism and direct-film-drain tests, as selected by the author on 11 October. These use different film settings and developed bulk fields. They demonstrate active release routes and local lower-wall removal, with continuing upper-film storage. The rejected tail of the long drain continuation remains identified.

The 0.045 mm material-reference continuation supplies context for the later film settings; roughness, bulk advancement and film step changed together. Appendix A.14 maps the vertical film blocker to the 154,063-cell vertical-slit geometry and the angled film ramp to the 213,232-cell angle-slit geometry. Both basic-wall-film calculations have reached 150 ms with frozen bulk fields. Their settings and steps match over 50–150 ms, but meshes and earlier fields/history differ, so a geometry-only benefit is not established. The earlier enhanced-film vertical endpoint remains separate. The external collection route remains a design proposal. Meeting records explain rationale and shared attribution rather than supply quantitative simulation results.

The separate absorber-free comparisons include coarse mixed/split-inlet numerical packages and developing 342k, 680k and 997k mesh checkpoints. They support interpretation of the liquid routes and the missing drain. They do not establish a converged mesh study or prove that mesh topology caused the later failure. The combined-model refinement study remains ongoing; no completed mesh-convergence conclusion is selected here. Andy's separate later full-geometry and VOF campaigns are outside Shuhei's experimental account.

Figure 1 introduces the liquid destinations; Figures 2–17 present the selected context and work. Figures 19–20 show film maps followed by the selected mesh-state inventories and removal rates. Main Tables 1–2 retain material properties and boundary conditions. Appendix A has Tables A1–A33. A.9.4 gives residual and film-step details; A.12 gives later mechanism and drain tests; A.13 explains the full-geometry decisions; A.14 identifies design concepts and their completed film-development calculations; A.15 retains supporting startup and balance results; A.16 gives comparison designs; and A.17 preserves the numerical values behind the main figures. Table B2 summarises the research answers, Table B3 retains the supporting literature comparison, and Appendix C records figure sources.

Section 4.13 now develops the Phase 9 narrative: the purpose of the resolution comparison, the coarse-mesh basis for choosing approximately 200 ms, the selected 195 ms film maps and endpoint rates, and the implications for film propagation, supply and release. Figures 19–20 link spatial distribution to storage and drainage. The earlier one-page allowance and retained 25-page proof need reassessment after this addition. Mesh independence remains unestablished; no quantitative design-performance claim is selected.

## Requirements and remaining author/document tasks

The draft follows the [report guidance](<Rough Guidance.md>), [structuring guidance](<Structuring your report.pdf>) and [2026 assessment rubric](<2026 P4P Final Report Rubric Students-1.pdf>). The scientific prose uses New Zealand English; author–date citations link to primary literature and version-matched documentation. The supplied ESB template defines the declaration and title-page fields.

The current body limit is **30 pages from Introduction to Conclusions**, as updated by the author on 14 October 2026; **12 pt Times New Roman** remains required. The refreshed [body review proof](<Shuhei Report/review/body-page-proof.pdf>) is **25 pages**, including the pending mesh-comparison page at **20**. All 17 completed main figures are included. The [rendering record](<Shuhei Report/review/README.md>) and [manifest](<Shuhei Report/review/page-proof-manifest.json>) give the settings and source hashes. This is a content/layout review, not the final submission PDF. Front matter, references and appendices follow the supplied inclusion rules.

The remaining author-only fields are student identification, submission date, final assembled word count and declaration signature. The declaration is explicitly unsigned. Supervisor and co-worker names follow the supplied poster; the acknowledgements and contribution/AI-use statements are drafted for the author's final review.

The report does not claim validated separation efficiency or pressure loss. The selected-state mesh comparison is included; later film development and source histories remain needed. Other numerical and physical assessment tasks are stated as future research.
