# Final research report — Markdown draft

The draft is split into four main parts. Its focus is **model development and evidence limits**, with **the absorber implementation and staged startup as the main project contribution**. The early history leading to N45606 provides the central evidence: low-feed field development, a verified inlet ramp, and a developed full-feed parent that enabled roughness and wall-film experiments.

This is a working draft, revised after Shuhei's review on 7 October 2026. Revise one part at a time, using the same files. The text uses New Zealand English. The draft files use Markdown only.

The F0–F4 reconstruction is provisional. Its detailed comparisons and figures are excluded from the main argument until stronger numerical evidence is available. A proposed repeat on a substantially finer mesh must establish sensitivity; refinement is not assumed to repair the results.

## Reading order and size

| Part | Draft file | Main task | Planned body pages |
| --- | --- | --- | ---: |
| Front matter | [Title, abstract, declaration, contents, acknowledgements and glossary](draft/00-front-matter.md) | Complete the author information and align the abstract with the revised findings | Outside the Introduction–Conclusions count |
| 1 | [Introduction and literature review](draft/01-introduction-and-literature-review.md) | Establish the problem, the study question and the relevant prior work | 2 + 3 |
| 2 | [Model and methods](draft/02-model-and-methods.md) | Explain the absorber, startup sequence and subsequent wall experiments | 6 |
| 3 | [Results](draft/03-results.md) | Lead with early numerical development, then show the experiments it enabled | 9 |
| 4 | [Discussion, conclusions and future work](draft/04-discussion-conclusions-and-future-work.md) | Answer the study question and explain what the results permit | 3 + 2 |
| Supporting material | [References and appendices](draft/05-references-and-appendices.md) | Keep the citations, evidence routes and reproducibility detail together | Excluded |
| **Body total** | | | **25** |

The [report guidance](<Rough Guidance.md>) sets a maximum of 25 pages from Introduction to Conclusions. The supplied template uses APA 7 referencing. The page allocation above is a writing budget; Markdown does not verify the final page count. The required 12 pt Times New Roman format will be checked at the later document stage.

## Working argument

| Question | Evidence selected for the draft | Answer supported by that evidence | Main limit |
| --- | --- | --- | --- |
| What enabled sustained model development? | Early N45606 lineage; verified v2 absorber; low-feed hold and corrected ramp | Continuity and inventory behaviour improved enough to obtain a common developed parent for later experiments | The sequence does not isolate each cause or establish complete mass closure |
| What did the absorber implementation contribute? | Phase-2 mass removal weighted by local liquid, with liquid-velocity momentum and turbulence removal | A verified liquid-removal treatment in a model with no resolved lower discharge path | The treatment is numerical; its throughput law leaves a full-feed balance error |
| What experiments did the developed parent enable? | Common-parent roughness and E0/E2.7 screens; combined N45606 history | Wall treatment strongly changes the represented liquid state | Inventory changes, open balances and film-solver limits |
| Can the startup approach carry the added complexity? | Revised startup from the saved low-feed fields; subsequent film development | The combined recipe lowers ramp excursions and produces a film-development endpoint | Activation and late inner-film failures; later frozen bulk fields |

The central distinction is between a useful model-development advance and a qualified physical prediction. The startup and absorber made the later studies possible. Their remaining limits stay beside that contribution. Each comparison retains its own parent, collector law, solver settings and sampling window.

## Section-by-section revision

1. Revise Part 1 first. Settle the wording of the aim and research questions before expanding the background.
2. Complete the exact method table in Part 2 and Appendix A. Use the saved case records for each comparison.
3. Revise Part 3 around the figures. Keep each numerical observation next to the limit that affects its meaning.
4. Revise Part 4 against the stated questions. Then update the abstract and title.

## Specific items to complete

| Item | Required work | Where it affects the draft |
| --- | --- | --- |
| Author information and contribution | Confirm supervisor names, co-worker details and the author's contribution statement | Front matter |
| Full methods detail | Add verified geometry dimensions, material properties, wall treatment and complete source-hook identities for the selected cases; both absorber laws and the historical startup sequence are included | Part 2; Appendix A |
| Early mass-balance evidence | The low-feed residual and inventory histories are available. Add a quantitative early balance claim only with aligned native inlet, outlet and applied-source reports; the full-feed endpoint has been checked | Parts 2–4; Appendix B |
| Newer film evidence | The completed 500 ms reference arm is included; review any completed additional speed arms and the Stage 4 feedback-OFF continuation before selecting the final endpoint | Parts 3–4 |
| Mesh study | Assess the selected startup and wall-treatment model on matched meshes; the current input audit is preparation evidence | Parts 2–4 |
| Deferred F0–F4 reconstruction | Repeat and assess on a substantially finer mesh before deciding which comparisons deserve report space; also resolve accounting, tracking and raw-source gaps | Short note in Part 3; Appendix A |

The primary literature checked for this pass is Purnanto et al. (2013), Zarrouk and Purnanto (2015), Skoog (2020), and NASA's verification and validation guidance. The local design-overview PDF and wiki use a 2014 label; the DOI's publisher metadata gives the volume publication as January 2015. The draft uses 2015 consistently.
