# Shuhei's interpretation of the separator modelling work

*Author context captured from the poster discussion, the supplied working poster, and report drafts 01–03 on 11 October 2026.*

## Purpose and central argument

This document records the reasoning Shuhei wants the poster and report to convey: what was unsatisfactory in the inherited model, what each change made possible, what the resulting behaviour suggested, and why that led to the next investigation. The experiment records remain the owners of settings and measured results. This document supplies the connections between them and preserves the author's interpretation where it is stronger or broader than the conclusions already written in those records.

The central question is **whether the model gives liquid a physically credible path through the separator**. Swirl should move liquid towards the wall; wall liquid can form a film, move around and down the vessel, return to the steam as droplets, or reach a collector. A useful model must represent enough of these routes to explain the result. A low continuity residual or small mass imbalance is useful evidence, but it cannot make an unsuitable liquid route physically convincing.

Shuhei therefore sees the work as progressive improvement of the model's physical representation. A change can reveal an existing modelling problem even when the calculation becomes harder to run. In particular, stronger retention of liquid near the wall and base can expose the absence of a liquid drain. The research contribution includes recognising that problem, supplying an explicit collection route, and developing the model far enough to investigate wall-film behaviour and possible design changes.

The interpretation and the evidence have different roles. Shuhei's experience supports the practical value of the new meshing workflow. Saved fields and histories establish which behaviours occurred. Reduced numerical diffusion, the cause of a solver failure, and greater physical accuracy require additional comparison. Preserving those distinctions allows the physical argument to remain clear without presenting a working explanation as a completed validation result.

The poster's topic selection also defines the report's emphasis. In the 11 October review of **A1 Landscape — Geothermal Separator Poster — Working Draft (2).png**, Shuhei clarified that mesh and the two-phase inlet are major findings he values, alongside the absorber, wall interaction and film behaviour. They need their own visible Results sections and spatial evidence, rather than appearing mainly as Methods detail or late numerical qualifications.

The learning sequence is organised by scientific dependency. Phase 8 revisited earlier assumptions after the absorber and wall studies, so phase numbers are not the order in which the poster's argument needs to be told.

| Part of the story | What it contributes | Connection to the next question |
| --- | --- | --- |
| Background and inherited model | A separator must move, retain and discharge liquid while supplying dry steam. | Which of those routes does the CFD model actually represent? |
| Mesh and solver response | Mesh structure and numerical settings change the predicted liquid distribution. | Does apparent numerical improvement preserve credible liquid transport? |
| Two-phase inlet | The model tests liquid already concentrated beside the wall. | How does that liquid move after entering the vessel? |
| Absorber and startup | A declared collection model and controlled loading support further development. | What controls the liquid that remains near the wall or reaches the steam outlet? |
| Wall–liquid interaction | Roughness and film treatment strongly change the calculated liquid state. | Where is wall liquid stored, and how does it leave? |
| Film development and added mechanisms | Separate runs reveal spreading, accumulation, drainage and release back into the flow. | Can transport towards collection be improved? |
| Experiment workflow | Literature, hypotheses, execution and interpretation form a repeatable learning process. | Which next comparison resolves the important uncertainty? |
| Design proposals | Proposed features act on the liquid paths identified by the modelling. | Do they improve collection without unacceptable carryover or pressure loss? |

## 1. Background: the physical liquid path is the starting point

The engineering purpose is to supply dry, clean steam to the turbine. Liquid carryover can cause erosion and carry dissolved minerals that form deposits. The separator therefore needs to do more than move liquid outwards: the liquid must remain in a collection path and leave through a suitable discharge route.

This is the link between the literature and Shuhei's model development. Purnanto supplies a useful starting geometry, operating condition and modelling approach, but its assumptions are open to investigation. Pointon recognises films in upstream piping and droplet generation from films inside the separator. Rizaldy describes wall-film entrainment mechanisms. Together, these sources motivate a model that can distinguish liquid in the bulk flow, liquid on the wall, droplets released from the wall, and liquid actually collected.

The centre flow image and solver-settings panel support this physical account. The image helps the viewer understand rotation and the location of the wall and collector. A streamline image alone does not show film thickness, captured liquid mass or separation efficiency. Similarly, the settings describe how a particular flow field was calculated; they are not a universal configuration shared by every experiment in the poster.

Evidence and background: [report Introduction and literature review, §§1.1–2.5](draft/01-introduction-and-literature-review.md); [Pointon primary paper, printed p.945](../../CFD_wiki/raw/1028587.pdf); [Rizaldy primary paper, film and liquid routes](../../CFD_wiki/raw/053_Rizaldy_Final.pdf).

## 2. Mesh: a practical improvement that made liquid accumulation more apparent

**Shuhei regards the move from the inherited tetrahedral mesh to the Fluent Meshing poly-hex approach as a significant improvement.** The practical benefit is that useful meshes with controlled wall refinement are easier to produce and develop. The physical motivation is to represent the concentrated wall liquid and rotating flow more faithfully, rather than choose a mesh mainly because it lets the solver run without difficulty.

The wall-following layers are central to this reasoning. Fine spacing normal to the wall supports the steep changes across the wall region, while the surface arrangement follows the vessel around which liquid circulates and drains. Shuhei expects this structure to reduce artificial smearing of wall liquid. Polyhedral cells support the surrounding gradient reconstruction and transitions, while the hexahedral core provides an efficient volume mesh. The precise expectation is better control of wall-region resolution and transport; the entire hexcore does not align exactly with every direction of a three-dimensional swirling flow.

The earlier saved comparison showed a broader liquid-rich wall region on the 60,964-cell mixed-inlet SIMPLE reconstruction than on the 7,601,261-cell historical tetrahedral reference. This matters to Shuhei because it suggests that the old representation may have allowed concentrated wall liquid to become too diffuse. The comparison itself changed more than mesh, so it is an observation that motivated the explanation, rather than an isolated measurement of diffusion error. The comparison page also uses a 342k mesh illustration alongside that 60k reconstruction field; the illustrated mesh and the source of a liquid contour must remain identifiable.

Phase 8 Stage 2 made the missing-drain interpretation more concrete. In the 680k SIMPLE case without an absorber, liquid inventory increased from **455.41 kg at N3000 to 764.74 kg at N4000**. At N4000, **69.62% of that liquid was below y = 2 m**, and steam-outlet liquid was only **8.00 kg/s against 116.92 kg/s supplied**. The continuation later encountered AMG divergence and a floating-point exception after the last printed N4211. The separately completed 997k N3000 case also concentrated liquid low in the vessel while sending very little liquid through the steam outlet.

Shuhei's interpretation is that improved retention of wall liquid exposes an incomplete physical model: liquid is being kept away from the steam outlet but has no brine-discharge route. Continuing accumulation is understandable under those conditions. The important observation is the location and destination of the liquid, followed by the numerical difficulty. These are steady solver iterations, so the inventory changes describe numerical development rather than a physical filling rate. The failure itself is not the reason to call the mesh better.

Shuhei recalls no equivalent inventory failure in the earlier tetrahedral reference, and Purnanto did not discuss such a failure. That contrast belongs in the author's reasoning. It does not establish that tetrahedral meshes generally prevent accumulation, or that the historical model's behaviour was correct. Purnanto assumed a fixed water level and excluded brine-pipe flow; the reported study does not provide the inventory history needed for a direct comparison.

Two distinctions keep this explanation tied to the right experiments. The archived 08b settings and fields were successfully transferred to the 997k mesh and save/reopen verified. Its continuation then diverged and crashed after the last printed N10022, while liquid inventory fell slightly. That is a separate failure sequence from the 680k accumulation above, and interpolation had changed the starting distribution. The local Stage 2 cases used a related SIMPLE setup with changed controls, rather than an exact historical replay. Also, the 60k report states still have very high recorded wall y+ and incomplete mesh-quality/layer evidence. Practical improvement and a credible mesh hypothesis remain worth explaining while quantitative accuracy is unresolved.

Evidence: [native mesh and liquid-section comparison](../meetings/Poster/poster-sections/mesh-and-volume-fraction-comparison.md); [Fluent Meshing structure inspection](../experiments/phase-07a-simplified-purnanto-liquid-removal/mesh-inspection.md); [680k accumulation and later failure](../experiments/phase-08-storyline-reconstruction/stage-02-fine-mesh-simple/direct-student-680k/n4000/results.md); [matched Stage 2 mesh endpoints](../experiments/phase-08-storyline-reconstruction/stage-02-fine-mesh-simple/direct-student-342k/n3000/results.md); [separate exact-08b transfer](../experiments/phase-08-storyline-reconstruction/stage-02-fine-mesh-simple/08b-native997k/run2000-off/results.md). Numerical basis: [Fluent mesh guidance, §7.1.3.3](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/flu_ug_GridTypes.html); [Methods §3.4](draft/02-model-and-methods.md).

## 3. SIMPLE and Coupled: numerical closure must be interpreted through the available outlets

Shuhei's criticism of Coupled concerns the **absorber-free model with only the steam outlet available**, not every use of Coupled. In that truncated vessel, a stationary mass-conserving result has to send the incoming liquid through the steam outlet if no other removal route is active. The solver can therefore produce a small boundary imbalance while representing an unsuitable separator state.

The coarse Phase 8 reconstruction illustrates the issue. The mixed-inlet and split-inlet Coupled cases sent approximately **99.67% and 99.40% of inlet liquid through the steam outlet**. Changing inlet placement changed retained inventory, but it did not create a collection path. Shuhei does not regard that apparently better closure as an adequate reason to prefer those fields physically. The question is whether the liquid destinations make sense for the intended separator.

The later SIMPLE wall/base accumulation gives a different clue: stronger exclusion of liquid from the steam outlet exposes the need for removal below. This does not make all SIMPLE results acceptable. The coarse mixed-inlet SIMPLE case discharged more than three times its liquid feed while still gaining inventory, and its balance error was large. That case cannot supply a physical accumulation rate or establish solver superiority. The compared packages also changed pseudo-time and discretisation alongside pressure–velocity coupling.

Once an explicit collector was introduced, Coupled became useful within the startup and continuation method. These positions are consistent: Shuhei rejects accepting a numerically settled but physically unsuitable liquid route, while retaining a solver that helps develop a model with the intended collection route represented.

Evidence: [Stage 1 reconstruction findings](../experiments/phase-08-storyline-reconstruction/stage-01-60k-storyline/results.md); [mixed-inlet Coupled account](../experiments/phase-08-storyline-reconstruction/stage-01-60k-storyline/f1-one-inlet/results.md); [997k SIMPLE spatial and outlet result](../experiments/phase-08-storyline-reconstruction/stage-02-fine-mesh-simple/direct-student-997k/n3000/results.md); [report Results §§4.2 and 4.9](draft/03-results.md).

## 4. Two-phase inlet: make the assumed liquid arrangement explicit

The inlet change tests whether incoming liquid concentrated near the wall gives a more useful representation than a uniformly mixed or mist-like feed. Upstream pipe films are physically plausible, and rotation moves liquid towards the separator wall. The pure-liquid strip on the outer-wall side therefore represents an assumed incoming wall-rich region. Its purpose is to study the subsequent wall transport, film formation and drainage with a clear, reproducible inlet condition.

The strip is not a measured profile, and the literature does not establish complete segregation before entry. The point is to make the inlet assumption explicit and examine its consequences. This connects directly to the mesh: a narrow imposed strip must be represented by the inlet faces and nearby cells well enough that numerical spreading does not dominate the intended comparison.

There are two separate calculations behind the split. Purnanto's reference **197.61 kg/s** total feed and **1600 kJ/kg at 11.2 bar absolute** give a steam mass fraction of 0.4083 through the saturated enthalpy balance. The retained phase commands are **116.92 kg/s liquid and 80.69 kg/s steam**. Density then converts those mass flows to volume flows. Under the original equal-velocity design assumption, the 0.724 × 0.724 m inlet requires **27.118 m/s**, with **0.004890 m² liquid area** and **0.519286 m² steam area**: a **6.754 mm liquid strip** beside the wall.

Thus the small liquid area does not mean little liquid mass. Liquid carries most of the mass but occupies little volume because its density is much greater. The enthalpy fixes the mass split before the CFD solve; it is not a flashing calculation within the energy-disabled model. Later material values slightly change the phase velocities on the retained geometry, so the original design velocity and later nominal 26.81 m/s label have different bases.

Evidence: [inlet development interpretation](../experiments/phase-01-purnanto-baseline-and-inlet-exploration/interpretation.md); [original split-area derivation](../experiments/phase-02-parity-reset-and-pre-v2-qualification/purnanto-08c-inlet-loading-sensitivity/inlet-regimes-interpretation.md); [Methods §§3.3.1–3.3.3](draft/02-model-and-methods.md); [split-inlet assumptions](../../CFD_wiki/wiki/setups/geothermal-boc-separator-two-zone-split-inlet.md).

## 5. Absorber: represent the omitted liquid destination

The absorber follows from the mesh, inlet and outlet questions. If the model directs liquid towards the lower wall, it needs a way to represent that liquid entering the omitted brine pool. Continued inventory growth is therefore a modelling problem to understand, rather than only a residual to suppress.

The physical assumption is simple: **liquid entering the collector transfers its mass and momentum into the brine pool**. The simplified model removes those quantities from its represented domain. It does not resolve the receiving pool's free surface, pressure response or momentum. Removing liquid alone, with its associated momentum, gives the upper separator a declared collection route without creating an unintended vapour outlet at the base.

The earlier full-geometry work explains why this simplification was chosen. Adding the lower vessel and brine outlet introduced difficult drainage, vapour-routing and pool-control behaviour. The long pressure-control investigation still accumulated lower-region liquid while the controller remained at its bound. Shuhei returned to the truncated geometry so that internal separator transport could be investigated while the pool hydraulics remained a separate problem. The absorber is a deliberate model boundary, not a finding that real pool behaviour is unimportant.

Absorber development also changed the meaning of removal. The early throughput-controlled law could remove the entire commanded liquid feed even while additional liquid left through the steam outlet. Its source command was applied correctly, but that did not make the combined account correct. The later contact law made removal depend on liquid actually present in the lower region, with momentum removed using the liquid velocity. This better matches the intended collection assumption.

The different liquid representations require their own collection routes. Bulk liquid uses the volume source. The early selected film cases use native outflow where the film wall ends. Later cases introduce a direct film source that removes film mass and matching momentum at the lower collector. Diagnostic droplets use their specified collector boundary treatment. These routes must remain identifiable when rates are discussed; they are not several measurements of one interchangeable absorber.

The poster's continuity reduction is supporting evidence that the development procedure became more manageable. It does not isolate absorber causality because startup and numerical controls also changed, and it is not a percentage mass-balance error. The main contribution is an explicit, inspectable liquid-removal model that enabled the wall studies.

Evidence: [full-geometry scope decision](../experiments/phase-06-full-geometry-with-brine-pool/conclusion.md); [simplified liquid-removal interpretation](../experiments/phase-07a-simplified-purnanto-liquid-removal/interpretation.md); [R0 source-inclusive account in Results §4.2](draft/03-results.md); [contact law and collection routes in Methods §3.3.4](draft/02-model-and-methods.md); [later direct-film-drain proof](../experiments/phase-07-2a-wall-liquid-routing/stage-04-ewf-wall-parameters/ewf-only-drain/results.md).

## 6. Startup: learning how to introduce the model and its loading

Startup is part of the modelling method because the field from which a calculation begins affects whether additional wall physics can be developed. Shuhei wants the reduced-feed hold, gradual loading and preserved starting fields understood as a way of introducing the intended model in stages.

The original low-feed hold arose from a failed ramp command. Its useful field development was an observation made during recovery. The later work turned that observation into checked loading procedures, rather than retrospectively claiming that the original sequence was a fully planned experiment. The shortened startup activated the combined contact, roughness and film treatment before the full-feed ramp.

At matched ramp progress, that revised package reduced peak continuity and retained liquid by about 70%, and peak outlet liquid by about 76%. These are useful results of the combined recipe. They do not isolate one setting, and the activation spike and later film-solver failures remain part of the account. The connection to the next stage is that a repeatable saved starting state made comparisons and longer film development possible.

Evidence: [Phase 7.1A interpretation](../experiments/phase-07-1a-absorber-convergence/interpretation.md); [shortened-startup results](../experiments/phase-07-2a-wall-liquid-routing/stage-03-shortened-reconstruction/early-ewf-startup/results.md); [report Results §§4.1 and 4.6](draft/03-results.md).

## 7. Wall–liquid interaction: why wall treatment becomes a central research question

Shuhei expects much of the separated liquid to travel near the wall. Wall friction, attachment, film motion and drainage therefore act directly on a major liquid path. This is why changes to wall treatment deserve substantial attention, rather than being treated as minor solver settings.

The experiments show a strong response. The roughness screen changed outlet liquid non-monotonically: a small roughness increase initially raised it, while the 8 mm case reduced it by about 44% relative to the smooth continuation. Separately, the accretion-enabled film package reduced mean bulk-liquid outlet flow from approximately **24.37 to 1.74 kg/s**. These observations made wall treatment an important candidate explanation for the model's liquid routing.

The intended learning is the sensitivity and the need to follow the liquid. The large reductions occurred alongside inventory changes; the film comparison also changed a package of settings and retained momentum feedback off. Neither the roughest tested surface nor the lowest bulk-liquid outlet rate is thereby an optimum separator design. Instead, the result leads to the next physical question: did liquid drain, move into the film, remain stored, or return to the flow through another route?

Evidence: [roughness screen](../experiments/phase-07-2a-wall-liquid-routing/roughness-family/results.md); [matched wall-treatment observations](../observations/07-wall-liquid-interaction.md); [report Results §§4.3–4.4](draft/03-results.md).

## 8. Wall film: connect learning from development, release and drainage runs

Shuhei explicitly wants this part to combine learning from different runs. The narrative begins with the visible film, then introduces the processes that change its fate, and finally uses mass rates to explain growth or removal. Each run answers part of that argument; they do not all use one final configuration.

The early development run showed film spreading and thickening over the lower and middle walls while the upper wall stayed thinner. Between 75.66 and 265.18 ms, the area with film thickness at least 0.10 mm increased from **40.34% to 61.98%**. This makes spatial growth a useful finding: the film occupied a wider appreciable region, rather than only increasing its maximum thickness.

The same reference case then continued from 265.18 to 500 ms. Film mass increased from **6.69 to 9.54 kg**, about 43%. At 500 ms, mean film input was **81.12 kg/s**, drainage **69.60 kg/s**, and accumulation **11.53 kg/s** over the final 10 ms. Drainage had developed, but it remained below input. The useful conclusion is that a visible film and substantial drainage can coexist with continuing storage.

Those fields developed under frozen bulk flow, and stripping, splashing and droplet edge separation were off. The film was responding to prescribed bulk forcing. Constant bulk quantities were imposed by the freeze, and accretion did not advance a reciprocal bulk depletion calculation. This scope belongs beside the result without obscuring what the run taught about the evolving surface film.

Later runs added routes by which liquid could leave the wall and return to the flowing steam:

- **Stripping:** steam shear removes droplets from the film.
- **Splashing:** droplets strike the film and create additional droplets.
- **Edge separation:** film leaves wall edges as droplets.

Shuhei's intended point is that these additions increase the physical detail of the model: wall capture is followed by transport, possible release and possible collection again. They make the liquid paths more complete. Greater complexity does not automatically establish greater predictive accuracy, but the added mechanisms address identifiable processes in the literature and expose questions that the simpler calculation could not answer.

The later mechanism runs recorded stripping and edge-separation transfers. Their summaries do not isolate a closed splash contribution. These transfers remove liquid from the film but do not necessarily remove it from the separator. A direct-film-drain comparison then showed that removal at the lower collector could operate with frozen bulk. The longer continuation still accumulated liquid almost entirely on the upper wall, despite active removal below. That is the important connection to design: a working local drain is insufficient if liquid continues to collect elsewhere or cannot reach it fast enough. The long run later failed its numerical guard, so its transfer rates are diagnostic results rather than validated operating performance.

The conceptual film balance is collection and returning droplets, less release and drainage, leaving storage. Its implementation must follow the actual native source definitions and the checked ledger for that case. Report labels can describe net transfers or cumulative masses; neither the label nor a negative source value alone determines which separate release terms belong in the account. Each transfer must be counted once. Bulk absorber removal also belongs to the bulk account unless a direct film source is active. This is why a compact rate comparison should use one identified case and window, even though the surrounding scientific story connects several cases.

**Figure identity matters.** The attached working poster shows 5.90, 75.66 and **171.16 ms**, ending at N18615 with **5.419 kg** of film. The newer report figure ends at **265.18 ms**, N25815, with **6.688 kg**. The **500 ms** value is a later history endpoint. A description must not silently treat any of these as the same final image. In addition, the report's current 265 ms rates use a 1000-update window; the chat's matched final-10-ms comparison gives drainage/storage of **68.16/12.97 kg/s**, instead of **68.18/12.95 kg/s**. The small difference is a reporting-window difference.

Evidence: [spatial film development](../experiments/phase-07-2a-wall-liquid-routing/stage-03-shortened-reconstruction/early-ewf-startup/film-development/results.md); [linked 500 ms continuation](../experiments/phase-07-2a-wall-liquid-routing/stage-03-shortened-reconstruction/early-ewf-startup/inlet-speed-500ms/results.md); [selected history for the matched windows](../../PyAnsys/output/phase72a-stage3-speed-sensitivity-server1/20261006/selected-film-history-reference.csv); [later release-mechanism result](../experiments/phase-07-2a-wall-liquid-routing/stage-04-ewf-wall-parameters/realism-continuation/feedback-off/results.md); [direct drain comparison](../experiments/phase-07-2a-wall-liquid-routing/stage-04-ewf-wall-parameters/ewf-only-drain/results.md); [upper-film accumulation with active lower drainage](../experiments/phase-07-2a-wall-liquid-routing/stage-04-ewf-wall-parameters/ewf-only-drain/long-development/results.md). Mechanism definitions: [Fluent 2025 R2 film submodels](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_th/flu_th_ewf_sec_film_submodels.html).

## 9. Methodology: the Fluent agent harness supports an iterative scientific process

The methodology card explains how the experiments were conceived and carried out. Shuhei brings the physical interpretation, chooses or changes the scientific direction, and discusses hypotheses with the agent. Literature, the CFD wiki and previous runs supply evidence and possible explanations. The resulting question and scope are recorded in `CONTEXT.md`, with the intended comparison in `setup.md`.

Skills are instructions that guide the agent's work. Reviewed Python runners or MCP tools use PyFluent to configure and command Fluent; Fluent performs the numerical calculation. Settings readback and saved/reopened cases check the implemented model. Native reports, fields and transcripts support analysis, figures and results records, which feed the next discussion and experiment.

The contribution of the harness is the ability to carry out and compare a growing set of investigations while retaining their scientific purpose and evidence. Automated execution does not supply the physical interpretation by itself. This context file captures the reasoning that would otherwise be lost between the separate setup, result and source records. The poster describes the current workflow; earlier runs did not necessarily use today's skill names or MCP route.

Evidence: [current harness card](../Poster/Fluent_Agent_Harness_Card.html); [workflow ownership](../../.agents/invocation.md); [comparison design in Methods §3.6](draft/02-model-and-methods.md).

## 10. Design proposals: act on the wall-liquid path revealed by the studies

The design concepts in the supplied poster follow from the wall-film investigations. If much of the liquid circulates along the wall, can return to the steam, and may accumulate before reaching the lower collector, then features that intercept or redirect that film are reasonable candidates to test.

| Proposed feature | Intended physical action | Connection to the model learning |
| --- | --- | --- |
| Vertical film blocker | Intercept circulating wall liquid before it meets incoming steam. | Test whether interrupting that encounter reduces disturbance and renewed release. |
| Angled film ramp | Guide wall liquid towards the lower collection region. | Address transport to the collector, as well as initial film formation. |
| External collection channel | Collect wall liquid through a shell opening and route it down an external drain. | Provide a proposed route out of the main swirling region. |

These are Shuhei's design hypotheses as presented in the working poster. Their purpose is more specific than a general promise to increase efficiency. Each changes a liquid route suggested by the preceding studies. The assessment should therefore follow collected liquid, steam-outlet liquid, film storage and pressure drop. A lower film inventory alone could mean either improved drainage or more release into steam, so the destination matters.

The existing slit and angled-geometry records do not automatically validate these three concepts. Their geometry, controls and comparison basis need to match before results are attached to a proposal. The attached poster is the source for the three concept descriptions; no dedicated Project evidence record for that exact set was found during this review.

## 11. What the report and later comparisons need to carry forward

The current report already contains much of the factual basis, but its opening gives high continuity and mass imbalance considerable prominence. Shuhei's intended emphasis is the physical problem beneath those diagnostics: the representation of wall liquid and its eventual destination. The numerical evidence remains necessary; it supports judgement about that physical account instead of replacing it.

| Report part | Connection to make clear |
| --- | --- |
| 01 — Introduction and literature review | Begin with the need to move, retain and discharge liquid. Connect published assumptions about mist, wall collection and film release to the project questions. |
| 02 — Model and methods | Explain why the mesh, inlet, collector and startup choices were made before giving their implementation. Preserve the distinct bulk, film and droplet representations. |
| 03 — Results | Show the observed fields, rates and numerical responses for identified cases. Make the question answered by each comparison visible. |
| Discussion and later revisions | Connect the findings across phases: more apparent wall retention exposes missing removal; collection enables wall studies; film studies motivate release models and design changes. State Shuhei's working explanations alongside the evidence that could test them. |

Phase 9 follows naturally from this argument. A common model on different mesh resolutions can test whether the wall-liquid distribution and collection behaviour persist. It should assess those fields and rates as well as residuals. Changing geometry to a slit or ramp answers a design question and cannot be treated as mesh refinement alone. The current context does not declare the mesh study complete or convert its live state into a final result.

Three explanations remain especially useful to test: whether the old mesh smeared wall liquid more strongly; whether the missing collection route accounts for the retained liquid in the newer SIMPLE cases; and which combination of film transport, release and collection controls continued upper-wall storage. They are specific research connections, not reasons to discard the learning already obtained.

The report drafts currently select results through Stage 3 and defer the later wall-parameter investigation. Shuhei's poster discussion now explicitly connects that early work to later film mechanisms and drainage. This document preserves that wider interpretation without changing the current report's evidence selection. The account concerns Shuhei's development path; Andy's separate later campaigns are not evidence for it.

Reviewed report sources: [01 — Introduction and literature review](draft/01-introduction-and-literature-review.md), [02 — Model and methods](draft/02-model-and-methods.md), [03 — Results](draft/03-results.md), [report scope and revision plan](README.md), and [Phase 9 question](../experiments/phase-09-mesh-convergence/CONTEXT.md). Author framing also comes directly from the poster-development chat and the supplied **A1 Landscape — Geothermal Separator Poster — Working Draft (1).png**. This file records interpretation as of 11 October 2026; future numerical results remain in their experiment owners.
