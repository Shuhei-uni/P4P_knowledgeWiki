# Final research report — Markdown draft

The report examines **how liquid moves through the separator and reaches a collection route**. Its main contribution connects mesh and inlet choices to liquid retention, collection and wall-film behaviour, supported by practical absorber and startup development. Mesh and inlet assumptions, absorber-free accumulation, wall roughness, film growth, release and drainage form a connected research argument.

The 12 October 2026 revision uses [Shuhei's interpretation](Shuhei-Context.md), the meeting records and selected experiments to explain the model choices. It has been reviewed sentence by sentence, paragraph by paragraph and figure by figure. Experiment records remain the source of settings and results. Mesh and the two-phase inlet lead the Results, followed by accumulation, collection, startup and wall behaviour. Repeated explanation was cut, and detailed calculations and checks moved to the appendices. The [revision review](revision-review.md) records coverage and assessment guidance.

## Reading order

| Part | File | Purpose |
| --- | --- | --- |
| Front matter | [Title, abstract, declaration, contents and glossary](draft/00-front-matter.md) | State the research problem, key results and author information |
| 1 | [Introduction and literature review](draft/01-introduction-and-literature-review.md) | Establish liquid transport, collection and film release as the physical basis for the questions |
| 2 | [Model and methods](draft/02-model-and-methods.md) | Explain model choices, collection assumptions, procedures and the agent-assisted experiment workflow |
| 3 | [Results](draft/03-results.md) | Lead with mesh and inlet findings, then connect accumulation, collection, startup and wall-film behaviour |
| 4 | [Discussion, conclusions and future work](draft/04-discussion-conclusions-and-future-work.md) | Connect the findings and identify the next useful model and design comparisons |
| Supporting material | [References and appendices](draft/05-references-and-appendices.md) | Retain implementation, case identities, detailed numerical checks, figure provenance and contribution statement |
| Complete draft | [Combined Markdown report](draft/draft-v1.md) | The six parts assembled in the same order, with working internal links |

## Evidence selected for this draft

The central startup and wall-treatment sequence uses the 60,964-cell simplified domain. It includes the historical reduced-feed hold and checked ramp, common-parent roughness and accretion screens, contact collection, shortened startup and frozen-bulk film development to 500 ms.

The report also includes a concise account of the later release-mechanism and direct-film-drain tests, as selected by the author on 11 October. These use different film settings and developed bulk fields. They demonstrate active release routes and local lower-wall removal, with continuing upper-film storage. The rejected tail of the long drain continuation remains identified.

The 0.045 mm material-reference continuation supplies context for the later film settings; roughness, bulk advancement and film step changed together. Appendix A.14 maps the vertical blocker to the 154,063-cell vertical-slit geometry and the angled ramp to the 213,232-cell angle-slit geometry. Their selected evidence is a completed startup and a mesh audit, respectively. The external collection route remains a design proposal. Meeting records explain rationale and shared attribution rather than supply quantitative simulation results.

The separate absorber-free comparisons include coarse mixed/split-inlet numerical packages and developing 342k, 680k and 997k mesh checkpoints. They support interpretation of the liquid routes and the missing drain. They do not establish a converged mesh study or prove that mesh topology caused the later failure. Phase 9 remains an ongoing campaign; no completed mesh-convergence conclusion is selected here. Andy's separate later full-geometry and VOF campaigns are outside Shuhei's experimental account.

Figures 1–15 present the completed work; Figures 16–17 are reserved for Phase 9. Main Tables 1–9 include the pending Phase 9 comparison. Appendix A has Tables A1–A28. Appendix C records figure sources. Appendix A.9.4 gives residual and film-step details; A.12 gives later mechanism and drain tests; A.13 explains the full-geometry decisions; A.14 identifies design concepts; A.15 retains four supporting Results tables; and A.16 gives comparison designs. Table B2 summarises the supported research answers.

Section 4.13 reserves **four body pages for Phase 9**: the comparison basis, matched spatial fields, development and mesh-response plots, and the final table and finding. The verified input counts are 60,964, 342,609, 679,970, 997,604 and 2,596,657 cells. All result values remain pending. The abstract, discussion and conclusions identify where the final mesh finding must be added. Slit and ramp geometries remain separate design comparisons.

## Requirements and remaining author/document tasks

The draft follows the [report guidance](<Rough Guidance.md>), [structuring guidance](<Structuring your report.pdf>) and [2026 assessment rubric](<2026 P4P Final Report Rubric Students-1.pdf>). The scientific prose uses New Zealand English; author–date citations link to primary literature and version-matched documentation. The supplied ESB template defines the declaration and title-page fields.

The required body limit is **25 pages from Introduction to Conclusions**, in **12 pt Times New Roman**. The [body page proof](review/body-page-proof.pdf) is **25 pages**, including four whole Phase 9 pages at **19–22**. It uses 1.15 line spacing and the template margins, with compact paragraph and heading gaps. All 15 current main figures remain. The [rendering record](review/README.md) and [manifest](review/page-proof-manifest.json) give the exact settings and source hashes. This is a layout review, not the final submission PDF. Front matter, references and appendices follow the supplied inclusion rules.

The remaining author-only fields are student identification, submission date, final assembled word count and declaration signature. The declaration is explicitly unsigned. Supervisor and co-worker names follow the supplied poster; the acknowledgements and contribution/AI-use statements are drafted for the author's final review.

The report does not claim validated separation efficiency or pressure loss. Phase 9 is the reserved results addition. Other numerical and physical assessment tasks are stated as future research.
