# Final report revision review

The current draft has been reviewed sentence by sentence, paragraph by paragraph and figure by figure. The section order is preserved. The revision uses plain scientific English, puts the finding before its explanation, and keeps each material limit beside the claim it affects.

## Review coverage

| Report part | Review and resulting change |
| --- | --- |
| [Front matter](draft/00-front-matter.md) | Title, 289-word abstract, prescribed declaration, contents, lists, acknowledgements, glossary and symbols reviewed. The abstract follows liquid destinations and leaves Phase 9 explicitly pending. |
| [Introduction and literature](draft/01-introduction-and-literature-review.md) | Every paragraph, equation, table and literature caption reviewed. Repeated background was cut; each study now contributes a method, assumption or comparison limit to the research question. |
| [Model and methods](draft/02-model-and-methods.md) | Every sentence, equation, table and domain caption reviewed. Main text retains the model choices, collection law, comparison basis and mass accounts. Detailed derivations, controls and comparison designs are in the appendices. |
| [Results](draft/03-results.md) | Every comparison, value, table, figure and caption reviewed. Mesh and inlet evidence remain first. Four supporting numerical tables moved to Appendix A.15. Section 4.13 reserves four pages for Phase 9. |
| [Discussion and conclusions](draft/04-discussion-conclusions-and-future-work.md) | Each paragraph checked against the Results and research questions. Interpretation now explains the liquid destination and the next useful comparison. The repeated answer table moved to Appendix B. |
| [References and appendices](draft/05-references-and-appendices.md) | All 20 references, appendix paragraphs, equations, tables and captions reviewed. Repeated study inventories were shortened. Source signs, reporting windows, parents and contribution statements remain explicit. |

Evidence review covered the selected experiment setup, results and interpretation records, Shuhei's context, all 16 Otter meeting records, and the relevant September and October meeting reports. Meeting proposals explain the development rationale; experiment records supply the settings and numerical findings.

## Figure review

All 28 original image embeds, representing 27 unique source PNGs, were visually inspected. The revised section files use 22 unique images. All retained figures and new compositions were checked against their captions and source identities.

| Figures | Action |
| --- | --- |
| 1–4 | Retained the published panels and source credits. Captions distinguish conceptual diagrams, empirical measurements and earlier CFD, and define the required axes and units. |
| 5 | Clarified the solved domain, collector extent and computational steam-outlet boundary. |
| 6–7 | Replaced separate exports with readable compositions. Case meshes, native field colours and the verified shared 0–1 scale remain identifiable. |
| 8–12 | Checked mesh checkpoints, loading, roughness, outlet histories and spatial comparisons against their cases and windows. |
| 13 | Rebuilt as three panels using the exact histories. Removed the residual panel with incompatible normalisation and defined the signed outlet flux. |
| 14–15 | Checked accepted film time, snapshot identity, common scale, frozen bulk and the different rate windows. |
| A1–A6 | Reviewed all appendix images. Rebuilt A2 with clear legends, units and event labels while preserving every selected point and restart. |
| 16–17 | Reserved for Phase 9 spatial and development/mesh comparisons. No result image or outcome is assumed. |

The two spatial compositions and two rebuilt history figures have reproducible Python scripts and source-hash records. Independent reruns produced identical image hashes. The history plots retain every selected numerical point without smoothing.

## Assessment guidance applied

| Rubric criterion | Weight | Report response |
| --- | ---: | --- |
| Literature and field knowledge | 10% | Compare assumptions and assessment evidence; explain which methods transfer to this separator. |
| Problem definition and framing | 10% | Connect the incomplete liquid path to four explicit research questions. |
| Study design | 20% | Justify the inlet, collector, wall models and comparison procedures; retain reproducible detail in appendices. |
| Execution, findings and evaluation | 30% | Lead with fields and rates from identified cases; preserve failed and incomplete routes where they explain a decision. |
| Interpretation and contribution | 25% | Explain collection, storage and release separately; keep numerical diagnostics distinct from physical performance. |
| Technical communication | 5% | Use direct sentences, concise captions, consistent terminology and working evidence links. |

Sources: [2026 rubric](<../2026 P4P Final Report Rubric Students-1.pdf>), [report structure guidance](<../Structuring your report.pdf>), [abstract guidance](<../writing an abstract.pdf>) and [report requirements](<../Rough Guidance.md>). This review does not assign a grade.

## Completion limits

The [body page proof](review/body-page-proof.pdf) is **25 pages**, with **four whole Phase 9 pages at 19–22**. It retains all 15 main figures, 12 pt Times New Roman body text, 1.15 line spacing and the template margins. Paragraph and heading gaps are compact; captions use 11 pt as allowed by the template. Current section and image hashes match the [render manifest](review/page-proof-manifest.json). The [rendering record](review/README.md) provides the reproduction command. No clipped boxes or missing glyphs were reported, and the rendered pages were visually inspected.

Phase 9 still needs selected results at comparable film ages and bulk-development stages. Its four-page allocation includes Figures 16–17, the final mesh table and a supported finding. The abstract, discussion and conclusions identify where that finding must be added.

The report retains model-development scope. Mesh independence, sustained combined conservation, stationary film and physical validation are not established by the editorial review. The Purnanto primary paper could not be reopened from this checkout; the reported inputs and citation provenance were retained. The roughness source's conflicting prose was resolved in favour of its numerical table, without an optimum claim.

Student identification, submission date, final word count, declaration review and signature remain author tasks. The body page proof checks layout and reserved space; it is not the final submission PDF.
