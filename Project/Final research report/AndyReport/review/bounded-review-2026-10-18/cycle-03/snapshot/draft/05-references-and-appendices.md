# References and appendices

## References

Ansys. (2025). *Ansys Fluent Theory Guide*, Release 2025 R1, §23.3.1, Spatial discretization. [Source](https://ansyshelp.ansys.com/public/Views/Secured/corp/v251/en/flu_th/flu_th_SolveDiscretization_spatial.html).

Bangma, P. (1961). The Development and Performance of a Steam-Water Separator for Use on Geothermal Bores. *Proceedings of the U.N. Conference on New Sources of Energy Rome, Vol. 3*.

Foong, K. C. (2005). Design Concept for a More Efficient Steam-Water Separator. *Proceedings World Geothermal Congress*.

Gimbun, J., Chuah, T. G., Fakhru’l-Razi, A., & Choong, T. S. Y. (2005). The influence of temperature and inlet velocity on cyclone pressure drop: A CFD study. *Chemical Engineering and Processing: Process Intensification, 44*(1), 7–12. [DOI](https://doi.org/10.1016/j.cep.2004.03.005).

Lazalde-Crabtree, H. (1984). Design Approach of Steam-Water Separators and Steam Dryers for Geothermal Applications. *Geothermal Resources Council Bulletin*.

McKibbin, R. (1998). Fluid Flow in a Flashing Cyclone Separator. *Proceedings 20th NZ Geothermal Workshop*.

Mubarok, M. H., & Zarrouk, S. J. (2016). *Steam-Field Design Overview Of The Ulubelu Geothermal Project, Indonesia*.

National Aeronautics and Space Administration. (2021a, February 10). *Examining iterative convergence*. NPARC Alliance CFD verification and validation tutorial. [Source](https://www.grc.nasa.gov/www/wind/valid/tutorial/iterconv.html).

National Aeronautics and Space Administration. (2021b, February 10). *Validation assessment*. NPARC Alliance CFD verification and validation tutorial. [Source](https://www.grc.nasa.gov/www/wind/valid/tutorial/valassess.html).

Purnanto, M. H., Zarrouk, S. J., & Cater, J. E. (2013). CFD modelling of two-phase flow inside geothermal steam–water separators. *IPENZ Transactions, 40*, 1–10. [Author-uploaded full text](https://www.researchgate.net/publication/269519626_CFD_MODELLING_OF_TWO-PHASE_FLOW_INSIDE_GEOTHERMAL_STEAM-WATER_SEPARATORS).

Rizaldy, Zarrouk, S. J., & Morris, C. (2016, November 23–25). Liquid carryover in geothermal steam–water separators. In *Proceedings of the 38th New Zealand Geothermal Workshop*, Auckland, New Zealand.

Umanzor, C., & Zarrouk, S. J. (2022). *The Steamfield Process Design and Optimisation Tool (SPDOT)*.

Umanzor, C., Zarrouk, S. J., & Rodríguez, A. (2021). *Steam Purity Troubleshooting: The Berlin Geothermal Steam Field, El Salvador*.

Yokkaichi, S. (2026). *Development of a geothermal separator CFD model: liquid transport, collection and wall-film behaviour* [Unpublished draft Part IV Research Project Report, 14 October 2026]. The University of Auckland.

Zarrouk, S. J., & Purnanto, M. H. (2015). Geothermal steam–water separators: Design overview. *Geothermics, 53*, 236–254. [Publisher record](https://www.sciencedirect.com/science/article/abs/pii/S0375650514000637). [DOI](https://doi.org/10.1016/j.geothermics.2014.05.009). The supplied PDF prints 2014, which is retained in the reproduced literature citations and figure credits; the publisher lists the same article in the January 2015 issue. Both dates here identify this DOI.


## Appendix A. Project evidence register

The project-wide findings reference records the evidence reviewed on 16 October 2026. Its finding identifiers F01–F21 provide stable links between this report and the source assessment. Table A.1 selects the owning records for each finding; the findings reference retains additional sources and qualifications. The report combines both development routes, while keeping differences in domains, model packages and numerical clocks explicit.

| **Finding** | **Owning evidence** | **Use and boundary** |
|:---|:---|:---|
| F01: reconstructed baseline | Reconstructed split-inlet baseline; Inlet-loading continuation | High apparent outlet quality coexisted with imbalance and iteration dependence. These are reconstructed cases. |
| F02: historical mesh study | Seven-mesh study and continuation | Within-run pressure and inventory drift limited cross-mesh interpretation. |
| F03: historical DPM | Twelve-case reconstruction; feed-partition control | Injection categories were accounted for; incomplete trajectories remained unresolved. |
| F04: early film mechanisms | Mechanism comparison; continuation | Deposition and release were represented; event counts did not establish separation efficiency. |
| F05: full-geometry outlet | Boundary screen; loading controls | Adding a brine boundary did not by itself establish stable operating discharge. |
| F06: pool feedback | Phase 6 results | Local inventory feedback worked, but its proxy was not a measured pool level. |
| F07: simplified sink | Applied-source check; interpretation | Liquid-only numerical withdrawal was implemented; report reduction and units mattered. |
| F08: inlet ramp and smooth-wall control | Preparation; control window; source account | Lower residuals and exact sink-command tracking did not close the steady liquid account. |
| F09: full-domain collectors | Closure; collector-rate comparison | Liquid reached the collector, but controlled changes did not remove global imbalance. |
| F10: wall treatment | Roughness; EWF family | Lower outlet liquid flux was accompanied by changes in bulk and film stores. |
| F11: startup and local checks | Early EWF startup; commercial steel; Staged film development | Selected active-bulk film accounts and inner solves passed; whole-system acceptance remained separate. |
| F12: film drainage | Reference 500 ms; direct-drain comparison | Film reached a drain and could be removed; storage persisted elsewhere. |
| F13: inlet/model comparison | Split inlet; Matched coupled-DPM comparison with and without EWF | Computed retention and routing changed. Small bulk-boundary gaps did not establish useful separation. |
| F14: short resolved drainage | Historical resolved-outlet tests | Short conservative rest/drainage checks passed; longer operating holds did not retain the required behaviour. |
| F15: drain-law verification | Corrected benchmark; full-separator extension | The simple pressure–flow implementation passed; full-separator stationarity and balance did not. |
| F16: pressure and gravity | Diagnostic index; pressure–gravity closure | Separate controls narrowed possible explanations without establishing a unique cause. |
| F17: EWF mesh development | Selected states; Staged film-development procedure; 679,970-cell mesh local accounts | Developed film states and local checks were obtained; final matched whole-system assessment remained incomplete. |
| F18: proposed designs | Design comparison; vertical continuation | Both basic-EWF designs reached 150 ms. A 500 ms design completion or isolated design advantage was not established. |
| F19: single-inlet mesh family | Results; saved-field assessment | Spatial and iteration differences remained substantial despite similar selected scalar outputs. |
| F20: reconstructed particle outputs | Carrier assessment; tracking cap; five enthalpies | Historical estimates were reproduced conditionally; incomplete mass and carryover sensitivity remained. |
| F21: computational cost | Tetrahedral comparison | Fixed-horizon cost was measured; intended geometry parity and equivalent accuracy were not demonstrated. |

*Table A.1. Evidence register for the integrated project findings.*

Historical records preserve reported observations from original notes. Not every remote or archived raw history was available for reanalysis. The review checked selected local machine summaries, including the corrected drain benchmark, the pool-feedback window and the five-enthalpy particle comparison. A completed record or saved case establishes execution evidence; it does not automatically establish scientific acceptance.

## Appendix B. Scope of selected successful numerical checks

The following checks support specific implementation or local-accounting claims. Their different denominators, clocks and system boundaries must be retained when comparing them.

| **Check** | **Reported result** | **Scope of the pass** |
|:---|:---|:---|
| Historical DPM accounts, F03 | All twelve cases met the 0.2% per-injection mass-accounting tolerance. | Reconciliation of particle categories, including the unresolved category; not proof that incomplete droplets were captured. |
| Selected steel-wall roughness, F11 | Continuity mean 0.00184594; film-account error 0.009931% of integrated accretion. | Selected active-bulk window; inner-film residuals unavailable; complete bulk–film–particle closure unverified. |
| Staged film development, F11 | After 35 ms additional film development, at iteration 36,020, 1000/1000 inner solves passed; source-accounting discrepancy 0.252404% of the summed magnitudes of integrated net-phase and DPM sources. | Active-bulk film checks passed; bulk/outlet/collector acceptance did not. The later 1.16832% trial did not pass its 1% film limit. |
| Vertical-blocker film, F11/F18 | At iteration 5290 and film time 7.75 ms, checked inner solves all passed; film mass-balance error 0.000009% of integrated phase accretion. | Bulk was frozen. Accretion 76.003567 kg/s was mostly stored in the film (75.990820 kg/s), so this was not a stationary-film result. |
| Short resolved drainage, F14 | Pool-depletion test at 0.2 ms: storage-aware error 0.4601% of feed; 0.05%-feed test over 1.28 ms: total remainder about $-9.11 \times 10^{-8}$ kg/s at its ten-step check. | Distinct short transient checks; neither establishes sustained full-load operation. |
| Corrected drain-law repeat, F15 | Four cases passed analytical, conservation, residual and stability criteria over iterations 401–500, with no speed/nonfinite guard breach over all 500. | Single-liquid frictionless duct; not calibration of the separator drain. |

*Table B.1. Selected successful checks and their inference limits. Sources are listed under the corresponding findings in Table A.1; the vertical-slit check is recorded in the early film-development result.*

For the corrected duct benchmark, the analytical relation was $U=\sqrt{2\Delta p/[\rho(1+K)]}$. The tested $(K,\Delta p)$ pairs were (0, 200 Pa), (0, 800 Pa), (9, 200 Pa) and (9, 800 Pa), with terminal speeds 0.673523, 1.347046, 0.212987 and 0.425973 m/s, respectively. The analysis and guard audit distinguish this successful corrected repeat from the earlier startup-guard violations.

### Numerical criteria and assessment windows

These are recorded study tolerances, not universal CFD criteria or estimates of physical accuracy. Residuals retain the solver's scaling. Passing one row does not qualify a different model family.

| **Assessment** | **Window and selected numerical criteria** |
|:---|:---|
| Full-geometry collector | Compare iterations 4001–4500 and 4501–5000. Final-window mean absolute source-inclusive phase/mixture imbalance ≤1% of respective measured feed; all active residuals ≤$10^{-3}$. Liquid-volume window-mean change ≤1%, divided by the larger mean with a $10^{-6}$ m$^3$ floor. |
| Steady VOF pool | Final 1000 iterations, split into 500-iteration halves. Phase/mixture mean absolute imbalance ≤0.5%, maximum ≤1% of respective feed. Total and lower-region inventory range ≤1%; half-mean change ≤0.25%, both divided by the complete-window mean. All active residuals ≤$10^{-3}$. Additional routing and two-start requirements below. |
| Single-inlet carrier | Final 500 iterations: maximum sampled phase/mixture flux error ≤1% of respective feed; inventory change ≤1%; pressure-drop drift ≤0.5%; mean velocity/vorticity drift ≤1%. Continuity ≤$10^{-4}$ and other active residuals ≤$10^{-3}$. Sampling details for the reconstruction are below. |
| Corrected single-liquid duct | Iterations 401–500: analytical flow error ≤2%; maximum mass imbalance ≤0.1% of outlet mass flow; flow range/mean ≤0.1%; pressure range/driving pressure ≤0.1%; active residuals ≤$10^{-6}$. Speed >20 m/s and nonfinite-value guards applied over all 500 iterations. |

*Table B.2. Principal numerical thresholds. The pool and carrier rows are completed by the definitions below; film-window criteria are stated with Table 5.*

The pool also required no systematic inventory drift, stable interface and occupancy, and interface-height change ≤0.02 m or one local vertical cell spacing, whichever was larger. At least 99% of liquid feed had to leave through brine and 99% of vapour through steam, with reverse-phase inflow below 0.1% of its feed. Both starts had to pass jointly and agree within 1% in inventory, 0.5% of feed in outlet phase flux, and 2% in pressure drop. Phase-summed versus native-mixture discrepancies above 0.1% of total feed required audit. Persistent clipping, saturation, divergence or nonfinite fields were unacceptable; persistence after save/reopen was also required.

For the 1500-iteration carrier reconstruction, residuals were checked over iterations 1001–1500; boundary reports sampled iterations 1010–1500 every ten iterations. Inventory change used endpoints 1000 and 1500, divided by the iteration-1000 inventory. The prescribed horizon was completed despite failed numerical qualification, as documented in the carrier assessment.

## Appendix C. Unresolved evidence and final-report checks

| **Item** | **Treatment in this draft** | **Evidence needed for a stronger statement** |
|:---|:---|:---|
| Current tetrahedral/poly-hexcore geometry | Intended equality is recorded; inferred volumes remain 27.9610 and 22.7930 m³. Cost is reported for the two cases. | Direct volume and boundary/domain comparison before claiming a mesh-only saving. |
| Phase 5 disputed continuations | Claimed outcomes for the disputed turbulence-model, full-load progressive-loading and later diagnostic tests are excluded. | Terminal records or raw histories confirming execution and results. |
| Final EWF mesh comparison | Selected 195 ms development and supplementary bulk-active stages are distinguished. Final whole-separator closure is unverified. | Matched endpoint fields and complete bulk, film, particle, source and inventory accounts. |
| Proposed-design continuation | Verified 150 ms basic-EWF endpoints are reported; later 500 ms completion is not claimed. | Verified terminal results from the later continuation, with matched preparation and settings. |
| Historical reconstruction | Incomplete-as-separated convention; unrecovered July binary/tracking cap; Fluent 2024 R2 versus 2025 R2. | Matched settings, boundary-specific escape rates and resolved fates before exact-replication or physical-efficiency claims. |
| Bibliography | Missing entries were restored from the submitted first-report PDF. Some publication details remain incomplete; the design-overview date difference is explained in its reference entry. | Complete the remaining publication details; retain secondary-source wording for Pointon et al. and Arifien and Zarrouk unless their originals are consulted. |

*Table C.1. Evidence gaps that affect the strength of the final claims.*

Case-specific numerical controls, boundary definitions and mesh statistics remain in the linked records. Appendix E reproduces the principal nine-group injection inputs used in the historical-output comparison. The reconstruction settings audit provides the traceable injection and model settings for the later DPM comparison. Missing settings are not assumed to be software defaults. Reused figures require creator/source credit in their captions, even where the surrounding scientific account presents the work as one project.

## Appendix D. Model assumptions and their purposes

| **Choice** | **Purpose and limit** |
|:---|:---|
| Inherited material and turbulence settings | Preserve a comparison basis for the reconstructed model. They were not independently validated for the resulting liquid distributions. Steady RANS tested a stationary mean-flow assumption; failure to converge does not prove physical unsteadiness. |
| Collector and pool parameters | The 10 µm continuum diameter, 200 kg feedback target, depletion times and film capture time were modelling or control choices, not measured plant properties. Selected paired changes tested numerical response; these choices did not calibrate a physical drain. |
| Roughness | The 8 mm case was a sensitivity test, not a manufacturing recommendation. The later 0.045 mm steel-wall value was assumed, not measured on the separator. |
| Macroscopic VOF pool | Fixed properties and omission of phase change/surface tension isolated bulk pool and outlet behaviour. Thermal response, capillary wetting and interfacial breakup were outside that assessment. The 620,431-cell domain volume was 27.0631 m$^3$. |
| Poly-hexcore construction | Curvature/proximity sizing with 12 requested wall layers and growth factor 1.15. Local stair-stepping warnings remained; requested layers did not establish achieved or matched wall resolution. |
| Historical enthalpy reconstruction | Total feed was 197.61 kg/s. Steam/liquid feeds at 1440, 1520, 1600, 1680 and 1760 kJ/kg were respectively 64.85/132.76, 72.77/124.84, 80.69/116.92, 88.61/109.00 and 96.52/101.09 kg/s. These were prescribed operating inputs, not predictions from an energy balance. |

*Table D.1. Why the main assumptions were used and what they do not establish. Source settings: collector, pool feedback, steady pool, film and roughness, direct drain, mesh family and enthalpy reconstruction.*


### Spatial definitions for the principal comparisons

The nominal reference dimensions below describe the intended reconstruction basis. They do not prove that every supplied mesh has the same geometry. Coordinates belong to the named family and are not plant elevations.

| **Configuration or feature** | **Spatial definition and evidence limit** |
|:---|:---|
| Nominal spiral-inlet reference | Vessel diameter 2.134 m; square inlet 0.724 × 0.724 m; nominal steam passage diameter 0.876 m; nominal brine pipe diameter 0.508 m. These reference dimensions do not resolve the tetrahedral/poly-hexcore volume discrepancy. |
| Later truncated meshes | The inspected 342,609-cell mesh has a closed bottom at approximately $y=0$ m. The 60,964-cell contact-collector model uses the existing 715-cell lower zone selected by cell-centre $y\leq0.10$ m. Its separating-face vertices span $y=0.03211$–0.18477 m; this is a stepped mesh boundary, not a fitted plane. |
| Direct film drain | Lower outer-wall segment in the truncated model: 34 faces with centres at $y=0.043964$–0.047341 m. Vertices extend to 0.118351 m. The sink acts on film on these faces; its extent is not identical to the bulk-cell selection. |
| Full-geometry collector comparison | On the 620,431-cell mesh, the numerical lower datum is $y=-1.484584$ m. The mapped historical truncation is $y=+0.020$ m. The matched 0.02/0.10 s depletion-time comparison selects all fluid cell centres up to $y=-0.882750$ m, with no horizontal crop: 41,258 cells over the lower 40% of that vertical span. This is a height fraction, not a volume fraction. |
| Matched mixed/split inlet comparison | On the 60,964-cell mesh, outer-strip area 0.0048899165 m$^2$ and remaining-face area 0.51928608 m$^2$; the strip is 0.93288% of total area. Mixed feed gives 26.81 m/s on both faces. Pure-phase split commands give 27.13795 m/s liquid and 26.80691 m/s vapour. Both configurations retain the same face geometry and per-face turbulence inputs. |

*Table D.2. Reference dimensions and recorded extents used to interpret the central comparisons. Sources: reference geometry, truncated-mesh inspection, contact collector, direct film drain, full-mesh mapping, matched collector setup and inlet parity audit.* 

The available spatial checks do not establish complete CAD parity across all families. Dimensioned as-built views of the proposed blocker and ramp are not supplied here; those cases support only the reported development endpoints, not a reproducible geometric design comparison.


## Appendix E. Particle inputs for the historical enthalpy reconstruction

Each group was an inert, uniform-diameter surface injection over the mixed inlet boundary, in the stationary global frame. Release positions were not randomised. The prescribed velocity was normal to each inlet face, with the same magnitude for all nine groups at a given enthalpy (Table E.2). Turbulent dispersion was disabled. The recorded Stokes–Cunningham drag law with Cunningham factor 1.0 was retained to reproduce the historical settings; its applicability over this diameter range was not established by the reported evidence. These inputs define the numerical reconstruction, not a measured inlet droplet population or a qualified drag model for performance prediction.

| **Group** | **Mass weight (%)** | **1440** | **1520** | **1600** | **1680** | **1760** |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 0.1625 | 7.149 | 6.2979 | 5.6214 | 5.0712 | 4.616 |
| 2 | 0.6675 | 35.745 | 31.489 | 28.107 | 25.356 | 23.08 |
| 3 | 0.8300 | 71.49 | 62.979 | 56.214 | 50.712 | 46.16 |
| 4 | 1.6700 | 142.98 | 125.96 | 112.43 | 101.42 | 92.32 |
| 5 | 1.6700 | 214.47 | 188.94 | 168.64 | 152.14 | 138.48 |
| 6 | 20.0000 | 443.23 | 390.47 | 348.52 | 314.42 | 286.19 |
| 7 | 25.0000 | 714.89 | 629.79 | 562.14 | 507.12 | 461.6 |
| 8 | 25.0000 | 1072.3 | 944.68 | 843.2 | 760.68 | 692.4 |
| 9 | 25.0000 | 2073.2 | 1826.4 | 1630.2 | 1470.7 | 1338.6 |

*Table E.1. Diameters in µm for each enthalpy column (kJ/kg), rounded to five significant figures. Group weights are percentages of represented injected liquid mass and sum to 100%; they are not parcel-count fractions. The recorded six-decimal mass-flow inputs produce only rounding-level differences in the first two weights at 1760 kJ/kg.*

| **Enthalpy (kJ/kg)** | **Face-normal injection speed (m/s)** | **Total represented particle flow (kg/s)** |
|---:|---:|---:|
| 1440 | 21.591272 | 132.76 |
| 1520 | 24.228170 | 124.84 |
| 1600 | 26.865069 | 116.92 |
| 1680 | 29.501968 | 109.00 |
| 1760 | 32.135537 | 101.09 |

*Table E.2. Prescribed particle speed and represented mass-flow basis. Multiply a Table E.1 mass fraction by the corresponding total here to recover each group's mass-flow weight, subject to the stated rounding.*

The carrier retained the full Eulerian phase feeds listed in Table D.1. Because this reconstruction used one-way diagnostic tracking, the particle weights in Table E.2 were not added as an extra physical liquid feed. Enthalpy changed the prescribed phase feeds, particle diameters and injection speed; it did not activate energy or phase-change calculations. Particle boundary fates and tracking controls are stated in Section 3.6. The exact July case binary and original tracking cap remain unrecovered, so these recovered inputs do not establish byte-identical historical replication.

Sources: recovered settings audit, enthalpy reconstruction protocol, exact 1600 kJ/kg injection readbacks and case-specific reconstruction inputs. The completed result records verify that the saved injection readbacks matched those inputs.
