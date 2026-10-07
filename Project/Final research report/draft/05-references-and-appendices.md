# References and appendices

*Working draft. The supplied report template specifies APA 7. Author–date links in the Markdown body are working citations for that style.*

## References

National Aeronautics and Space Administration. (2021a, February 10). *Validation assessment*. NPARC Alliance CFD verification and validation tutorial. [Source page](https://www.grc.nasa.gov/www/wind/valid/tutorial/valassess.html).

National Aeronautics and Space Administration. (2021b, February 10). *Verification assessment*. NPARC Alliance CFD verification and validation tutorial. [Source page](https://www.grc.nasa.gov/www/wind/valid/tutorial/verassess.html).

Purnanto, M. H., Zarrouk, S. J., & Cater, J. E. (2013). CFD modelling of two-phase flow inside geothermal steam–water separators. *IPENZ Transactions, 40*, 1–10. [Publisher identifier](https://search.informit.org/doi/10.3316/informit.366967552564856). [Primary paper copy consulted](https://www.researchgate.net/publication/269519626_CFD_MODELLING_OF_TWO-PHASE_FLOW_INSIDE_GEOTHERMAL_STEAM-WATER_SEPARATORS).

Skoog, E. (2020). *CFD annular flow modelling based on a three-field approach* [Master's thesis, Luleå University of Technology]. [University-hosted thesis](https://www.diva-portal.org/smash/get/diva2:1452100/FULLTEXT02.pdf). [Local primary copy consulted](../../../CFD_wiki/raw/FULLTEXT02.pdf).

Zarrouk, S. J., & Purnanto, M. H. (2015). Geothermal steam–water separators: Design overview. *Geothermics, 53*, 236–254. [DOI](https://doi.org/10.1016/j.geothermics.2014.05.009). [Local primary copy consulted](<../../../CFD_wiki/raw/Zarrouk and Purnanto 2014.pdf>).

The design-overview year follows the DOI's volume-publication metadata, January 2015. Its retained local filename, PDF header and wiki label use 2014. That difference is bibliographic and does not change the study's technical content.

## Appendix A. Method detail and reproducibility

### A.1. Exact settings to carry into the final methods table

*Table A1. Method facts and remaining detail for the central startup and absorber contribution. A missing entry must not be inferred from another branch.*

| Setting group | Draft basis | Remaining detail / owning record |
| --- | --- | --- |
| Geometry and mesh | Simplified 60,964-cell mesh; 715-cell absorber at $y\leq0.10$ m | Add dimensions, topology and quality from the [mesh inspection](../../experiments/phase-07a-simplified-purnanto-liquid-removal/mesh-inspection.md) and [verified v2 build](../../experiments/phase-07-1a-absorber-convergence/baseline-v2-virtual-liquid-outlet/results.md) |
| Feed | Hold: 29.23/20.1725 kg/s liquid/vapour; full feed: 116.92/80.69 kg/s | Retain actual boundary readbacks beside the intended schedule; [startup provenance](../../experiments/phase-07-1a-absorber-convergence/roughness-family/r0-smooth-control/provenance.md) |
| Materials and walls | Fixed-property vapour/liquid; smooth-wall parent | Add the selected cases' exact density, viscosity and wall-treatment readbacks |
| Original absorber | Liquid-weighted throughput law; phase-2 mass; liquid-velocity momentum; shared k/epsilon removal | Add exact expression and source-hook identities from the [verified build manifest](../../experiments/phase-07-1a-absorber-convergence/baseline-v2-virtual-liquid-outlet/build-manifest.json) |
| Historical startup | Actual 25% hold to N1580; verified 2000-update ramp to N3580; Coupled/Global Time Step continuation to N5586 | Keep intended and executed schedules distinct; [selected native history](../../experiments/phase-07-2a-wall-liquid-routing/stage-02-combined-ewf-roughness/case-history-N45606.md) |
| Full-feed control | Terminal control separated from hold, ramp and warm-up | Carry complete scheme and control readbacks from [R0 setup](../../experiments/phase-07-1a-absorber-convergence/roughness-family/r0-smooth-control/setup.md); use the [declared control window](../../experiments/phase-07-1a-absorber-convergence/roughness-family/r0-smooth-control/control-window.md) |
| Corrected contact absorber | $S_L=-\rho_L\alpha_L/\tau$; $\tau=10^{-5}$ s; liquid-velocity momentum removal; `libcontactv2` | Complete derivative and hook identities from the [contact-treatment setup](../../experiments/phase-07-2a-wall-liquid-routing/stage-02-combined-ewf-roughness/ewf-absorber/setup.md) |
| Roughness screen | Common N5586 fields; EWF off; 3000 updates; final-500 means | Retain height, constant, inventory and oscillation evidence from the [R-family result](../../experiments/phase-07-2a-wall-liquid-routing/roughness-family/results.md) |
| E0/E2.7 | Smooth walls; EWF off/on package; accretion on in E2.7; film equations coupled; wall momentum feedback off; 10 µs film step | Retain force, source, wall and outlet assignments; [E-family results](../../experiments/phase-07-2a-wall-liquid-routing/ewf-family/results.md) |
| Combined lineage | Original E2.7 fields; later roughness, contact absorber and smaller film step; selected replay and adaptive continuation | Keep branches, accepted film steps and normalisation changes from the [N45606 history](../../experiments/phase-07-2a-wall-liquid-routing/stage-02-combined-ewf-roughness/case-history-N45606.md) |
| Revised startup | Same N1580 fields; 500 updates at 25%; 2000-update ramp; 1000-update full-feed hold; 1 µs film step | [Revised-startup protocol and parent identity](../../experiments/phase-07-2a-wall-liquid-routing/stage-03-shortened-reconstruction/early-ewf-startup/setup.md) |
| Film development | Bulk frozen after N5080; actual accepted film steps and native clock | Retain selected restart lineage and local step-check scope; [film-development evidence](../../experiments/phase-07-2a-wall-liquid-routing/stage-03-shortened-reconstruction/early-ewf-startup/film-development/results.md) |

### A.2. Deferred reconstruction

The separate F0–F4 series covered numerical packages, mixed and split inlets, allocated droplets and a provisional film treatment. It used the common 60,964-cell simplified mesh with the absorber disabled. Its detailed performance comparisons are deferred because numerical behaviour, balance and particle completeness remain unresolved. A substantially finer-mesh repeat is proposed before deciding which results to use in the report.

The [owning Phase 8 results](../../experiments/phase-08-storyline-reconstruction/stage-01-60k-storyline/results.md) and [report contract](../../experiments/phase-08-storyline-reconstruction/stage-01-60k-storyline/report-contract.md) retain the methods, values and source routes. The [fine-mist distribution specification](../../experiments/phase-03-dpm-carryover-and-coupling/purnanto-09cV3-fine-mist-psd/setup.md) remains an assumed design input. No detailed reconstruction table or figure is used to support the present conclusions.

## Appendix B. Evidence routes and source limits

*Table B1. Sources for the main findings. Project records own the scientific results; linked machine evidence preserves their run identity.*

| Finding | Owning evidence | Scope of this draft's check |
| --- | --- | --- |
| Verified absorber implementation | [v2 build result](../../experiments/phase-07-1a-absorber-convergence/baseline-v2-virtual-liquid-outlet/results.md) and [source specification](../../experiments/phase-07-1a-absorber-convergence/baseline-v2-virtual-liquid-outlet/deffered.md) | Liquid weighting, phase scope, momentum/turbulence terms, save/reopen and trial-update evidence |
| Low-feed numerical development | [N45606 case history](../../experiments/phase-07-2a-wall-liquid-routing/stage-02-combined-ewf-roughness/case-history-N45606.md) | Carrier CSV minimum at N1556 and inventory/outlet CSV values checked; quantitative early closure is not inferred |
| Corrected ramp and common parent | [R0 provenance](../../experiments/phase-07-1a-absorber-convergence/roughness-family/r0-smooth-control/provenance.md), [selection context](../../experiments/phase-07-1a-absorber-convergence/CONTEXT.md) and [handoff](../../experiments/phase-07-2a-wall-liquid-routing/baseline-control-handoff.md) | Actual boundary schedule and loading/solver sequence kept distinct from the terminal control |
| R0 full-feed balance | [R0 audit](../../experiments/phase-07b-full-geometry-liquid-removal/convergence-investigation/shuhei-audit.md), supplemented by [native run4 histories](../../../PyAnsys/output/phase71a_r0_control_run4/report-histories-batched.json) | N5586 phase fluxes, native mixture flux and applied source aligned and checked; the historical audit's raw-availability limit is not repeated as the present state |
| Roughness response | [R-family results](../../experiments/phase-07-2a-wall-liquid-routing/roughness-family/results.md) and [existing replot](../../observations/07-wall-liquid-interaction.md) | Common-parent tail values and whole-run inventory losses retained |
| E0/E2.7 response | [Wall–liquid comparison](../../observations/07-wall-liquid-interaction.md) | Existing native-history replot and its declared window |
| Combined development to N45606 | [Selected case history](../../experiments/phase-07-2a-wall-liquid-routing/stage-02-combined-ewf-roughness/case-history-N45606.md) | Actual field lineage, changed absorber, accepted film clock, film ledger and inner-solve limits |
| Revised startup | [Early-start result](../../experiments/phase-07-2a-wall-liquid-routing/stage-03-shortened-reconstruction/early-ewf-startup/results.md) | Ramp peaks, separate activation spike and late inner-film failures |
| Selected N25815 film | [Film-development result](../../experiments/phase-07-2a-wall-liquid-routing/stage-03-shortened-reconstruction/early-ewf-startup/film-development/results.md) | Selected lineage, frozen equations, local step check and developing inventory |
| Longer reference-speed film | [500 ms campaign result](../../experiments/phase-07-2a-wall-liquid-routing/stage-03-shortened-reconstruction/early-ewf-startup/inlet-speed-500ms/results.md) | Completed reference arm and final-10-ms window; other arms retain their incomplete status |
| Further coupled mechanisms | [Feedback-ON failure record](../../experiments/phase-07-2a-wall-liquid-routing/stage-04-ewf-wall-parameters/realism-continuation/results.md) | Combined numerical failures retained; feedback-OFF outcome requires its own completed window |
| Mesh-study status | [Phase 9 results](../../experiments/phase-09-mesh-convergence/results.md) | Input and transfer preparation only; no completed convergence comparison used |

The early numerical values are checked against the [carrier residual CSV](../../../PyAnsys/output/phase72a-lineage-N45606/20261005/carrier-residuals.csv) and [selected liquid-history CSV](../../../PyAnsys/output/phase72a-lineage-N45606/20261005/selected-lineage-histories.csv). The [lineage manifest](../../../PyAnsys/output/phase72a-lineage-N45606/20261005/lineage-manifest.json) records sources, coverage, joins and normalisation limits. This revision checks the central scalar values and their provenance; it does not replace the owning analyses with a new full-run audit.

The roughness record's statement that R11 gives the lowest outlet conflicts with its table, where R7 is lower. The draft uses the table values and makes no optimum claim. Reconstruction coverage totals and rounded endpoint tables remain outside the main argument pending reassessment.

## Appendix C. Figure register

*Table C1. Existing figures used in the draft. Images remain at their original owning locations.*

| Figure | Subject | Evidence and caption requirement |
| --- | --- | --- |
| 1 | Early startup and carrier development | Actual 25% hold; verified ramp; Coupled continuation; iteration distinct from physical time |
| 2 | Roughness response | Common developed parent; N8087–N8586 means; connected settings are not fitted curves |
| 3 | E0/E2.7 outlet histories | All native points; positive outward flow; package and inventory limits |
| 4 | Complete selected liquid history to N45606 | Same field lineage; changed absorber; negative outward sign; accepted film clock and inner-solve limits |
| 5 | Revised-startup ramp comparison | Matched loading progress; activation window excluded; common continuity normalisation |
| 6 | Selected film-development history | Frozen bulk after N5080; native outlet sign; selected restart lineage |
| 7 | Film-thickness views | Shared camera and 0–0.30 mm scale; stated saved film times |

The methods sequence diagram in Section 3.1 summarises the development path. The main figures support that path and its enabled experiments; the deferred reconstruction figures are not included.

## Appendix D. Author contribution

[TO COMPLETE: state Shuhei's contribution to geometry, absorber implementation, startup development, simulations, analysis and writing. Identify any co-worker results used as context and attribute them. Complete this statement from the author's account and the project records.]
