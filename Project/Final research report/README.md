# Final research report — Markdown draft

The draft is split into four main parts. The research aim is to **develop and assess an existing Fluent separator model, improve understanding of internal steam and liquid transport, and establish a basis for predicting separation efficiency and pressure drop**. The intended use is separator-performance assessment, with predictions compared against field measurements. The aim and research questions are stated in [Part 1](draft/01-introduction-and-literature-review.md#13-research-aim-and-questions).

The report's focus is **model development and evidence limits**, with **the absorber implementation and staged startup as the main contribution**. The early history leading to N45606 provides the central evidence: low-feed field development, a verified inlet ramp, and a developed full-feed parent that enabled roughness and wall-film experiments. Field validation and qualified performance predictions remain open. Optimum separation pressure and separator location are outside the scope of the calculations presented.

This is a working draft, revised after Shuhei's review on 7 October 2026. Revise one part at a time, using the same files. The text uses New Zealand English. The draft files use Markdown only.

The F0–F4 reconstruction remains provisional. Part 2 describes the comparison design; Appendix A.2 retains the 08b/F0 and F1/F2 procedures. Part 3 contains a small provisional observation table, and Part 4 considers the mesh and solver explanations. The mesh views document structure, with the paired historical views retained in Appendix A.2. Detailed F3/F4 comparisons remain deferred. The revised SIMPLE cases and mesh work must establish sensitivity before stronger claims are selected.

The [2026 final report rubric](<2026 P4P Final Report Rubric Students-1.pdf>) guides the revision. Part 1 now starts with separator operation, develops the relevant physics and performance definitions, compares previous studies, and connects their assumptions and limits to the research questions.

## Reading order and size

| Part | Draft file | Main task | Planned body pages |
| --- | --- | --- | ---: |
| Front matter | [Title, abstract, declaration, contents, acknowledgements and glossary](draft/00-front-matter.md) | Complete the author information and align the abstract with the revised findings | Outside the Introduction–Conclusions count |
| 1 | [Introduction and literature review](draft/01-introduction-and-literature-review.md) | Explain separator operation and physics; assess prior work; establish the research direction | 1 + 4 |
| 2 | [Model and methods](draft/02-model-and-methods.md) | Define and justify the model, comparison design, numerical procedures and analysis | 7 |
| 3 | [Results](draft/03-results.md) | Lead with early numerical development, then show the experiments it enabled | 9 |
| 4 | [Discussion, conclusions and future work](draft/04-discussion-conclusions-and-future-work.md) | Explain the enabling contribution, numerical credibility and remaining prediction limits | 2 + 2 |
| Supporting material | [References and appendices](draft/05-references-and-appendices.md) | Keep the citations, evidence routes and reproducibility detail together | Excluded |
| **Body total** | | | **25** |

The [report guidance](<Rough Guidance.md>) sets a maximum of 25 pages from Introduction to Conclusions. The supplied template uses APA 7 referencing. The page allocation above is a writing budget; Markdown does not verify the final page count. The required 12 pt Times New Roman format will be checked at the later document stage. Part 1 assigns more of its planned space to the literature review. Its expanded text, comparison table and operation diagram must be checked against the final page allocation. Part 2 now follows the model definition, numerical method and comparison design. Exact source assignments, reconstruction settings and run schedules remain in the appendices. Final page use still needs a layout check.

## Rubric response in Part 1

The weights below apply to the whole report. They identify the criteria addressed by this revision, rather than scores assigned to the draft.

| Criterion | Whole-report weight | Revision in Part 1 |
| --- | ---: | --- |
| A. Literature & Field Knowledge | 10% | Explain operation and physics; compare the contributions, assumptions and evidence limits of the selected studies |
| B. Problem Definition / Research Framing | 10% | Identify the inherited model's unresolved collection and startup problems, then connect them to the aim and questions |
| C. Study Design | 20% | Establish reasons for absorber development, staged startup, roughness and film studies; carry the implementation detail into Part 2 |
| F. Technical Writing & Research Communication | 5% | Define performance quantities, introduce technical terms and show the steam and liquid routes in a conceptual diagram |

## Role of Model and Methods

The [structuring guidance](<Structuring your report.pdf>) requires a clear description of the approach, justification against the aims and enough detail for a similar investigation to be repeated. The [template](ESB_part_IV_latex_report_template_v2/ESB_report_template.tex) permits middle sections appropriate to the project. A Model and Methods section is suitable for this CFD study; it must define what was calculated and how each comparison was made.

| Rubric criterion | Weight | Requirement applied to the draft |
| --- | ---: | --- |
| C. Study Design | 20% | Connect theory, model assumptions, comparison controls and procedures to the research questions |
| D. Study Execution, Findings & Evaluation | 30% | Describe actual model execution and analysis in Methods; present observations and supporting evidence in Results |
| E. Interpretation, Contribution / Impact | 25% | Explain the mesh hypothesis, absorber contribution and solver/wall implications in Discussion, with claims proportionate to the findings |
| F. Technical Writing & Research Communication | 5% | Use a clear sequence, reproducible definitions and useful figures; keep detailed machine history in the appendices |

These are the rubric's whole-report weights, not section marks. Part 2 is organised around the computational domain, physical model, boundary conditions and collector, mesh, numerical solution, comparison design, and data reduction. The proposed improvements guide the Results and Discussion structure. The 25-page body limit remains the constraint for final selection.

The provisional findings plan retains the five topics and the staged startup that enabled later comparisons:

| Topic | Evidence to present in Results | Question for Discussion |
| --- | --- | --- |
| Mesh representation | Mesh structure and saved liquid fields; matched resolution comparisons when completed | Does the evidence support the proposed wall-region representation, and what competing case differences remain? |
| Inlet phase placement | Provisional F1/F2 inventories and outlet flows; revised SIMPLE comparison when assessed | How sensitive is the response to inlet placement, mesh and the numerical package? |
| Absorber | Implemented collection routes, source checks, inventory and removal histories | What does numerical collection enable, and what physical pool behaviour is omitted? |
| Coupled continuation | Residual and output histories for the actual numerical package | Which changes can be attributed to the tested package, and what remains unisolated? |
| Wall–liquid interaction | Roughness, accretion, film storage, drainage and selected added-mechanism results | Which liquid routes change, and are the fields still developing? |
| Staged startup | Reduced-feed hold, verified ramp and common-parent development | How does the executed procedure provide a basis for subsequent comparisons? |

## Working argument

| Question | Evidence selected for the draft | Answer supported by that evidence | Main limit |
| --- | --- | --- | --- |
| What enabled sustained model development? | Early N45606 lineage; verified v2 absorber; low-feed hold and corrected ramp | Continuity and inventory behaviour improved enough to obtain a common developed parent for later experiments | The sequence does not isolate each cause or establish complete mass closure |
| What did the final absorber implementation contribute? | Local contact mass removal, liquid-velocity momentum and turbulence terms, with separate film and droplet collection | A verified contact-removal treatment for the truncated model, with explicit numerical controls and field-specific routes | Finite depletion time, varying removal and unresolved whole-separator qualification |
| What experiments did the developed parent enable? | Common-parent roughness and E0/E2.7 screens; combined N45606 history | Wall treatment strongly changes the represented liquid state | Inventory changes, open balances and film-solver limits |
| Can the startup approach carry the added complexity? | Revised startup from the saved low-feed fields; subsequent film development | The combined recipe lowers ramp excursions and produces a film-development endpoint | Activation and late inner-film failures; later frozen bulk fields |

The central distinction is between a useful model-development advance and a qualified physical prediction. The startup and absorber made the later studies possible. Their remaining limits stay beside that contribution. Each comparison retains its own parent, collector law, solver settings and sampling window.

## Section-by-section revision

1. Use the aim and research questions in Part 1 to guide the later section revisions. Keep the report self-contained, with direct descriptions of the research purpose, methods and findings.
2. Complete the exact method table in Part 2 and Appendix A. Use the saved case records for each comparison.
3. Revise Part 3 around the figures. Keep each numerical observation next to the limit that affects its meaning.
4. Revise Part 4 against the stated questions. Then update the abstract and title.

Part 2 defines the model before describing how it was solved and compared. Section 3.3 now derives phase flow from pressure and enthalpy, converts mass to volumetric flow, explains the inlet split and velocity, and states the Fluent boundary entries. Section 3.5 gives the discrete ramp and preserved-field rules. Table 4 states the assessment procedures, and Table 5 defines the reported quantities. Section 4.9 carries the provisional F0–F2 observations, and Section 5.6 retains the mesh and solver explanations. Appendix A.2 holds the reconstruction details, A.3–A.4 the final source assignments and strength evidence, A.5 the early v2 law and protocols, A.6 the full-feed control settings, A.7 the worked inlet calculation, and A.8 the zone assignments and paired starting states.

## Specific items to complete

| Item | Required work | Where it affects the draft |
| --- | --- | --- |
| Author information and contribution | Confirm supervisor names, co-worker details and the author's contribution statement | Front matter |
| Full methods detail | The inlet derivation, property bases, ramp rule, zone assignments and starting-state map are included. Add verified CAD dimensions, mesh quality/layers and wall resolution, exact interphase closures, remaining case controls and final Stage 4 settings | Part 2; Appendix A |
| Early mass-balance evidence | The low-feed residual and inventory histories are available. Add a quantitative early balance claim only with aligned native inlet, outlet and applied-source reports; the full-feed endpoint has been checked | Parts 2–4; Appendix B |
| Newer film evidence | The completed 500 ms reference arm is included; review any completed additional speed arms and the Stage 4 feedback-OFF continuation before selecting the final endpoint | Parts 3–4 |
| Mesh study | Assess the selected startup and wall-treatment model on matched meshes; the current input audit is preparation evidence | Parts 2–4 |
| Provisional reconstruction | Update the comparison procedures and provisional observations after assessing revised cases; retain numerical, accounting and tracking limits | Part 2; Section 4.9; Section 5.6; Appendix A |

The primary literature checked for this pass is Pointon et al. (2009), Purnanto et al. (2013), Zarrouk and Purnanto (2015), Rizaldy et al. (2016), and Skoog (2020). The numerical and modelling context uses Ansys Fluent 2025 R2 documentation for the Mixture model, roughness, EWF and source terms, together with NASA's iterative-convergence, verification and validation guidance. The Part 2 revision adds the version-matched mesh, pressure–velocity coupling and multiphase solution guidance. The local design-overview PDF and wiki use a 2014 label; the DOI's publisher metadata gives the volume publication as January 2015. The draft uses 2015 consistently.

The literature review includes four figures: BOC flow routes, empirical wetness versus inlet velocity, paired inlet geometries and tangential-velocity fields, and wall-film entrainment mechanisms. The selected panels are stored in [figures/literature](figures/literature/). Their captions identify the published sources, define the source symbols where needed, and distinguish conceptual diagrams, empirical observations and CFD predictions. They replace the earlier operation flowchart and bring the main figure sequence to 1–11.

The [literature figure shortlist](literature-figure-shortlist.md) records the selected placements, original source numbers, page locations, previews and interpretation limits. It also retains alternatives for performance definitions, field sampling and the inherited model's literature basis. The four selected placements are now Figures 1–4 in Part 1. Final page use remains to be checked with the expanded text and figures.
