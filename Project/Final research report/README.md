# Final research report — Markdown draft

The report examines **how liquid moves through the separator and reaches a collection route**. Its main contribution connects mesh and inlet choices to liquid retention, collection and wall-film behaviour, supported by practical absorber and startup development. Mesh and inlet assumptions, absorber-free accumulation, wall roughness, film growth, release and drainage form a connected research argument.

The 11 October 2026 revision uses [Shuhei's interpretation](Shuhei-Context.md) to frame the discussion, while experiment records remain the source of settings and results. Each main section leads with the finding and its meaning, with the material limits kept near the end. The poster defines the findings to emphasise: mesh and the two-phase inlet lead the Results in their own sections with native spatial comparisons, followed by accumulation, collection and wall behaviour. Detailed solver histories, reproducibility checks and the wider experiment overview are retained in the appendices.

## Reading order

| Part | File | Purpose |
| --- | --- | --- |
| Front matter | [Title, abstract, declaration, contents and glossary](draft/00-front-matter.md) | State the research problem, key results and author information |
| 1 | [Introduction and literature review](draft/01-introduction-and-literature-review.md) | Establish liquid transport, collection and film release as the physical basis for the questions |
| 2 | [Model and methods](draft/02-model-and-methods.md) | Explain model choices, collection assumptions, procedures and the agent-assisted experiment workflow |
| 3 | [Results](draft/03-results.md) | Lead with mesh and inlet findings, then connect accumulation, collection, startup and wall-film behaviour |
| 4 | [Discussion, conclusions and future work](draft/04-discussion-conclusions-and-future-work.md) | Connect the findings and identify the next useful model and design comparisons |
| Supporting material | [References and appendices](draft/05-references-and-appendices.md) | Retain implementation, case identities, detailed numerical checks, figure provenance and contribution statement |

## Evidence selected for this draft

The central startup and wall-treatment sequence uses the 60,964-cell simplified domain. It includes the historical reduced-feed hold and checked ramp, common-parent roughness and accretion screens, contact collection, shortened startup and frozen-bulk film development to 500 ms.

The report also includes a concise account of the later release-mechanism and direct-film-drain tests, as selected by the author on 11 October. These use different film settings and developed bulk fields. They demonstrate active release routes and local lower-wall removal, with continuing upper-film storage. The rejected tail of the long drain continuation remains identified.

The separate absorber-free comparisons include coarse mixed/split-inlet numerical packages and developing 342k, 680k and 997k mesh checkpoints. They support interpretation of the liquid routes and the missing drain. They do not establish a converged mesh study or prove that mesh topology caused the later failure. Phase 9 remains an ongoing campaign; no completed mesh-convergence conclusion is selected here. Andy's separate later full-geometry and VOF campaigns are outside Shuhei's experimental account.

The figures are numbered 1–15, the main tables 1–16 and Appendix A tables A1–A22. Appendix C records the figures and their sources. Earlier residual and local film-step tables have moved from the main Results to Appendix A.9.4. Appendix A.12 supplies the added mechanism and drain details; Appendix A.13 retains the wider experiment history and pool-control figure.

## Requirements and remaining author/document tasks

The draft follows the [report guidance](<Rough Guidance.md>), [structuring guidance](<Structuring your report.pdf>) and [2026 assessment rubric](<2026 P4P Final Report Rubric Students-1.pdf>). The scientific prose uses New Zealand English; author–date citations link to primary literature and version-matched documentation. The supplied ESB template defines the declaration and title-page fields.

The required body limit is **25 pages from Introduction to Conclusions**, in **12 pt Times New Roman**. This revision completes the Markdown content; it does not establish final pagination. The main displays and prose must be checked together during document layout. Front matter, references and appendices follow the supplied inclusion rules.

The remaining author-only fields are student identification, submission date, final assembled word count and declaration signature. The declaration is explicitly unsigned. Supervisor and co-worker names follow the supplied poster; the acknowledgements and contribution/AI-use statements are drafted for the author's final review.

The report does not claim validated separation efficiency or pressure loss. Further numerical and physical work is described as future research, rather than left as unfinished report text.
