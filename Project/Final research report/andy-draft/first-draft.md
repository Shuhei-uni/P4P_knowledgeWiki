# Numerical assessment of liquid removal and solution credibility in a geothermal separator CFD model

**Part IV Research Project Report — first draft**  
**Author:** Andy [full name and student ID to complete]  
**Institution:** The University of Auckland  
**Supervisors:** [to complete]  
**Draft date:** 11 October 2026

> Working draft for discussion. The main argument centres on Andy's recorded replication, liquid-removal and numerical investigations. Shuhei Yokkaichi's work is identified separately. Internal evidence links support revision and will be replaced or organised for submission. The ongoing mesh study is reported only to the recorded 11 October snapshot. This Markdown draft has not been paginated against the 25-page body limit.

## Abstract

Computational fluid dynamics can support the assessment of geothermal steam–water separators, but performance predictions require a credible account of liquid transport, storage and removal. This study investigated these requirements in an inherited separator model using baseline replication, mesh assessment, numerical liquid collectors, resolved-outlet calculations and pressure–gravity initialization controls. The investigation combined exploratory development with controlled comparisons within individual calculation families.

Twelve historical enthalpy and droplet-tracking calculations produced a traceable replication dataset, but incomplete trajectories and unsettled carrier fields limited the interpretation of predicted outlet quality. Mesh comparisons also retained appreciable within-run drift. Subsequent full-geometry calculations tested whether a liquid-only numerical collector could establish steady operation. Correct source application did not establish conservation: a selected weaker-sink case retained a mean absolute liquid imbalance of 148.21% of inlet liquid flow over its final 500 iterations. Resolved-outlet calculations achieved brief drainage at very low feed, but this behaviour did not persist in longer tests. A later steady Volume of Fluid calculation continued to lose inventory and retained large phase-balance errors after an additional 1000 iterations. Initialization controls identified pressure-representation sensitivity at zero gravity and an unresolved gravity-on disturbance that also occurred with homogeneous liquid.

The tested treatments did not establish a conservative stationary operating solution. The contribution is a set of bounded model assessments and accounting checks that distinguish successful implementation from numerical and physical credibility. Further work should establish simpler hydrostatic benchmarks, constrain the downstream boundary model and qualify a reference solution before drawing separator-performance conclusions.

## Declaration

[Insert the prescribed University declaration and complete the author details.]

## Acknowledgements

[Add confirmed supervisor, collaborator and organisational acknowledgements.]

## Contents

1. Introduction
2. Literature review
3. Model and methods
4. Results
5. Discussion
6. Conclusions and future work
7. References
8. Appendices

## Glossary

| Term | Meaning |
| --- | --- |
| BOC | Bottom-outlet cyclone separator |
| CFD | Computational fluid dynamics |
| DPM | Discrete Phase Model, used to track individual droplet trajectories |
| EWF | Eulerian Wall Film, a surface representation of liquid-film transport |
| RNG | Renormalisation group; used here in the RNG k–ε turbulence model |
| VOF | Volume of Fluid, used in the resolved-pool investigations |
| Carrier field | The computed bulk flow through which diagnostic droplets are tracked |
| Collector | A prescribed numerical region that removes liquid through source terms |
| Stationary inventory | Retained liquid mass that satisfies the declared change limits over a specified window |
| Qualified solution | A calculation that meets the stated numerical, conservation, inventory and routing requirements |
| Validation | Assessment against suitable physical evidence for the intended use |

## 1. Introduction

### 1.1 Engineering problem

Geothermal steam–water separators supply steam to turbines while removing entrained liquid. Liquid carryover can contribute to erosion and mineral deposition, so separator assessment must consider steam quality as well as pressure loss. Established design methods address separator sizing and operation; CFD adds access to internal flow fields that are difficult to measure. These roles are described by [Zarrouk and Purnanto (2015)](https://www.sciencedirect.com/science/article/abs/pii/S0375650514000637).

The wider project sought to develop an existing Fluent model for assessing internal flow, separation efficiency and pressure drop. During this work, numerical convergence and liquid accounting became central obstacles. A low liquid flow at the steam outlet could not be interpreted without determining whether liquid had been collected, retained inside the vessel or lost through an unresolved numerical balance.

This report examines the model-development work undertaken to address that problem. The calculations considered alternative representations of liquid removal and investigated whether their numerical solutions met the conditions needed for a steady operating prediction. The original performance objective remained the intended use of the model, while the completed work established the limits of the tested routes towards that use.

### 1.2 Research aim and questions

The aim was to assess and develop the numerical basis for liquid removal in a geothermal separator CFD model, with particular attention to conservation, retained inventory and solution stability. Three questions guide this report:

1. What did reconstruction and mesh assessment establish about the reliability of the inherited model outputs?
2. Could the tested numerical collector and resolved-outlet treatments establish conservative, stationary liquid removal?
3. What did controlled numerical and initialization tests reveal about the remaining barriers?

The contribution is a traceable evaluation of these questions using phase-flow accounts, liquid inventories, residual histories and selected spatial evidence. This includes negative and incomplete results where they materially affect the interpretation. No validated separator-efficiency or pressure-loss prediction was obtained from the selected evidence.

### 1.3 Scope and contribution boundaries

The report covers Andy's historical replication and mesh investigations, closed-bottom sink diagnostics, resolved-outlet studies, full-geometry ideal-collector campaign and later pressure–gravity controls. The new single-inlet mesh family is included as an incomplete numerical assessment at the draft cutoff. These families differ in geometry, initialization and model formulation; they are not treated as one continuous controlled experiment.

Shuhei Yokkaichi's simplified-domain absorber, startup and wall-film investigations provide related project context. Their results are attributed in the discussion. Different geometry and modelling choices prevent a direct ranking of the two development routes. The final author-contribution statement will identify individual and shared tasks more precisely.

## 2. Literature review

### 2.1 Separator modelling and performance quantities

The design review by [Zarrouk and Purnanto (2015)](https://www.sciencedirect.com/science/article/abs/pii/S0375650514000637) places internal pressure loss, separation performance and operating-pressure selection within the wider separator-design problem. These quantities should remain distinct when assessing a CFD model. A local flow feature or a small outlet liquid rate does not, on its own, answer the complete design question.

For this study, outlet steam quality is defined from the outward vapour and liquid mass flows at the steam outlet:

\[
x_{\mathrm{out}}=\frac{\dot m_{V,\mathrm{out}}}{\dot m_{V,\mathrm{out}}+\dot m_{L,\mathrm{out}}}.
\]

This differs from the fraction of inlet liquid collected through a drain. Either quantity requires a clear sampling boundary. When retained liquid changes or the mass account does not close, an outlet ratio can describe the calculated state without establishing sustained separator performance.

### 2.2 Inherited CFD approach

[Purnanto et al. (2013)](https://www.researchgate.net/publication/269519626_CFD_MODELLING_OF_TWO-PHASE_FLOW_INSIDE_GEOTHERMAL_STEAM-WATER_SEPARATORS) investigated geothermal separator flow using Fluent, including changes in inlet conditions and geometry. Their approach used RNG k–ε turbulence modelling and droplet injection after development of the carrier solution, with a Harwell-based estimate of droplet size. This work supplied the reference for the project's reconstruction studies.

Reconstruction requires more than matching a reported headline output. The present replication records identify uncertainties in exact geometry parity, inherited particle settings and the interpretation of incomplete trajectories. Accordingly, the historical calculations are assessed as a reproduction attempt with an explicit discrepancy record, rather than assumed to reproduce all aspects of the original study.

### 2.3 Representing liquid removal

The project investigated two distinct representations of collection. A numerical collector removed liquid from selected cells while keeping the physical lower boundary closed. A resolved-outlet model instead represented discharge through an open brine boundary. The collector imposed a removal law; the outlet required a downstream pressure or discharge assumption. Neither treatment supplied measured plant behaviour by itself.

The bulk liquid, diagnostic droplets and wall film also require separate accounts where they coexist. A decrease in one represented liquid store can result from transfer to another store rather than discharge from the vessel. This distinction is particularly relevant to the related wall-film results discussed in Section 5.4.

[Literature development: add a focused comparison of numerical collectors, resolved pool/outlet models and wall-film collection. Check the relevant primary passages and version-specific Fluent theory before expanding these modelling arguments.]

### 2.4 Numerical credibility

Iterative convergence should be assessed using both equation residuals and the quantities the calculation is intended to predict. Different outputs may settle at different rates. [NASA's iterative-convergence guidance](https://www.grc.nasa.gov/www/wind/valid/tutorial/iterconv.html) therefore provides a useful basis for examining pressure, inventory and outlet histories alongside residuals.

Physical validation requires comparison with suitable observations and consideration of their uncertainty. It applies to an intended use and range of conditions. [NASA's validation guidance](https://www.grc.nasa.gov/www/wind/valid/tutorial/valassess.html) also identifies iterative, spatial and applicable temporal assessment as parts of that process. The present investigation addresses prerequisites for such validation; it does not replace a physical comparison.

The resulting research gap is specific to the inherited model: a liquid-removal treatment had to produce a credible numerical operating state before changes in predicted separator performance could be interpreted. This motivated the controlled collection, drainage and initialization studies that follow.

## 3. Model and methods

### 3.1 Investigation design

The work developed through exploratory calculations followed by more focused tests. Within each family, the retained setup records define the parent fields, controlled changes, calculation horizon and assessment conditions. Table 1 summarises the roles of the principal families. Historical case numbers are retained only where needed to trace results.

*Table 1. Investigation families and their comparison scope.*

| Family | Main question | Important distinction |
| --- | --- | --- |
| Enthalpy and DPM replication | Could the inherited approach reproduce reported trends? | Two six-condition families; geometry, velocity and droplet inputs were not isolated from one another |
| Historical mesh assessment | Were carrier outputs insensitive to resolution? | Equal iteration counts did not establish equal solution maturity |
| Closed-bottom sink studies | Could local liquid removal stabilise the carrier field? | Numerical removal with no resolved drain |
| Full-geometry ideal collector, Phase 7b | Could collection support balanced steady full-feed flow? | Full lower geometry retained, physical brine face closed; no standing pool required |
| Resolved-outlet studies | Could a pool and physical discharge route support sustained drainage? | Transient and steady VOF families had separate controls and interpretation |
| Pressure–gravity controls | Which changes affected the startup disturbance? | Short, guarded initialization tests, not operating simulations |
| Current single-inlet meshes | Could a matched family support a resolution comparison? | Study incomplete at the draft cutoff |

### 3.2 Geometry, operating inputs and phase models

The full-geometry collector and later steady VOF investigations used the recorded 620,431-cell mesh. Phase 7b retained the lower vessel geometry but closed the physical brine outlet, making the prescribed collector the separate liquid-removal mechanism. The steady VOF study rebuilt the case from the mesh and reopened the brine boundary. An unqualified collector solution was not used as its operating parent.

The Phase 7b reference used steady Mixture flow with algebraic slip, vapour as the primary phase, liquid as the secondary phase and RNG k–ε turbulence. Energy, DPM and EWF were disabled. The recorded liquid and vapour densities were 881.77 and 5.73 kg/m³, respectively. Separate pure-phase velocity inlets used 27.118 m/s, giving approximately 116.921 kg/s liquid and 80.690 kg/s vapour. Gravity acted downwards at 9.81 m/s². These values belong to this family and are not substituted for the different property or boundary values used in other branches.

The later steady pool study used implicit VOF with a shared velocity and the same recorded full-geometry mesh. It included no numerical sink, wall film or phase change. Its downstream pressure represented an assumed external liquid reservoir, without calibrated valve or pipe resistance. Independently initialised pool levels of 0.10 and 0.30 m tested the effect of the initial liquid state while retaining the external level at 0.10 m.

[Figure to add: annotated full-geometry domain with inlets, steam outlet, brine face and the Phase 7b collector region. Show the closed-collector and open-drain treatments separately.]

Evidence: [collector reference setup](../../experiments/phase-07b-full-geometry-liquid-removal/s040-collector/setup.md); [steady VOF setup](../../experiments/phase-09-steady-vof-pool/setup.md).

### 3.3 Numerical collector

The Phase 7b liquid source followed a local depletion law of the form

\[
S_L=-\chi\frac{\rho_L\alpha_L}{\tau},\qquad S_V=0,
\]

where \(\chi\) identifies the collector cells, \(\rho_L\) is liquid density, \(\alpha_L\) is liquid volume fraction and \(\tau\) sets removal strength. Associated momentum and turbulence terms represented transport removed with the liquid. The source was a numerical collection assumption, not a calibrated physical drain law.

The initial screen changed collector thickness. Subsequent comparisons examined removal strength and numerical treatment. The final controlled comparison retained the preceding Coupled/N-phase configuration and changed \(\tau\) from 0.02 to 0.10 s. Both cases began from the same clean initial physical fields. The assigned expression source and native applied source were checked separately; exact source tracking did not establish the internal source Jacobian or conservation.

Evidence: [source definition](../../experiments/phase-07b-full-geometry-liquid-removal/s040-collector/setup.md); [controlled weaker-sink comparison](../../experiments/phase-07b-full-geometry-liquid-removal/convergence-investigation/coupled-nphase-weaker-sink/results.md).

### 3.4 Numerical procedures and evidence collection

The historical replication used Fluent 2024 R2; the later recorded campaigns used version-specific setups, including Fluent 2025 R2 for the current mesh preparation. Exact solver versions and controls will be listed per family in the final methods appendix. No single solver package is assumed across the entire investigation.

Calculations retained native report histories, solver transcripts and paired case/data checkpoints where available. Selected campaigns also used independent field reductions and spatial exports to check reported inventories and regional flow accounts. A saved endpoint or successful script exit was treated as execution evidence. Its scientific status depended on the corresponding solution checks.

The pressure–gravity campaign used controlled changes to pressure representation, gravity, phase composition and body-force treatment. Most gravity-on tests reached a startup guard after one iteration. The zero-gravity pressure-datum comparison used matched 40-iteration windows. These short horizons were appropriate to the declared first-iteration rest question, but did not test whether an initially disturbed flow would eventually converge.

### 3.5 Mass accounting and assessment criteria

Native boundary fluxes were treated as positive into the domain. For an EWF-off liquid calculation with a numerical source, the steady liquid remainder was

\[
R_L=\sum_b\dot m_{L,b}+\dot m_{L,\mathrm{source}}.
\]

The applied source was negative for removal and was included once. Vapour and native-mixture accounts were assessed separately using their corresponding feeds. A normalised instantaneous liquid error was \(100|R_L|/\dot m_{L,\mathrm{in}}\). Mean absolute errors were computed from the absolute sample errors over the stated window; they were not the absolute value of a signed average.

Liquid inventory was assessed independently:

\[
M_L=\int_V\rho_L\alpha_L\,\mathrm dV.
\]

For physical transient calculations, storage belongs in a time-based mass account. Steady solver iterations do not provide that physical time coordinate. Inventory change per iteration was therefore used to detect numerical development, not converted into a physical mass-flow rate.

Assessment combined source-inclusive phase balances, inventory change, outlet routing, active residuals and spatial evidence. Requirements differed by experiment. For example, the late Phase 7b screen required phase and native-mixture closure within 1% of their feeds, inventory-window change within 1%, and continuity below 0.001 throughout the assessment window. The steady VOF study used stricter mean-balance and inventory-window limits, retained with its results.

```mermaid
flowchart LR
    A[Check geometry, boundaries and source application] --> B[Assess phase and mixture balances]
    B --> C[Check inventory, routing and active residuals]
    C --> D[Assess numerical sensitivity]
    D --> E[Compare with physical evidence]
```

*Figure 1. Assessment sequence used to structure the report. Passing an earlier check does not establish the later requirements.*

## 4. Results

### 4.1 Replication produced a dataset but did not qualify performance

The historical enthalpy investigation completed six baseline calculations and six spiral-inlet calculations. Each used nine Harwell-derived injection bins and a nominal 1500-iteration carrier horizon. The conditions comprised five enthalpies from 1440 to 1760 kJ/kg and a sixth case at 1600 kJ/kg with total flow reduced by 25%.

All twelve calculations passed the recorded 0.2% per-injection fate-mass tolerance. This reconciled the reported particle mass but did not determine the eventual fate of incomplete tracks. In the baseline family, incomplete particle mass exceeded confirmed escaped mass in every case. Final carrier continuity remained approximately 0.193–0.343 for baseline Cases 2–6 and 0.145–0.229 for the spiral cases.

The recorded provisional quality values ranged from 99.6718% to 99.8507% in the baseline family and 99.9668% to 99.9795% in the spiral family. Their definition used inlet steam flow and confirmed escaped liquid. They were not independently verified outlet-steam-quality measurements. Differences between the families also included inlet area, velocity and derived droplet inputs, so they could not establish an isolated geometry effect.

These calculations supplied a reproducible operating matrix and a discrepancy record. The unresolved carrier and particle behaviour prevented the apparent agreement near 100% from establishing physical validation. [Replication record](../../experiments/parallel-andy-studies/enthalpy-dpm-replication.md).

### 4.2 Historical mesh comparisons retained significant iterative drift

All seven historical meshes eventually reached their nominal 3000-iteration endpoint. Their labels did not equal their actual cell counts: the family ranged from approximately 1.69 to 13.37 million cells. Although some endpoint outputs appeared close between fine meshes, within-run changes remained material.

The pressure-drop difference between the historical 1900k- and 2000k-labelled cases was approximately 0.51%, while their final-window pressure drift was approximately 2.69% and 2.46%, respectively. The apparent cross-mesh agreement was therefore smaller than the continuing change within either calculation.

An independent continuation of the 900k-labelled case reached 6000 iterations. Between iterations 4000 and 6000, liquid inventory increased from 104.054 to 171.030 kg and pressure drop increased from 31.029 to 34.049 kPa. Pressure drift over the final 500 iterations remained 4.612%. The pressure comparison was still affected by a changing liquid distribution, so neither a production mesh nor a Richardson/GCI result was accepted. [Historical mesh assessment and later closure](../../experiments/phase-02-parity-reset-and-pre-v2-qualification/purnanto-08b-parity-split-inlet/mesh-convergence-checkpoint-20260803.md).

### 4.3 Numerical liquid removal did not establish steady conservation

Early closed-bottom sink tests increased removal by changing the source region and its strength, but did not establish an accepted stability window. A source-accounting audit also corrected a double count: the phase report's Net already included the liquid source. After correction, the first two reported liquid imbalances were 91.19% and 80.77%. This affected the interpretation of earlier apparent improvements and established the need to distinguish boundary-only reports from source-inclusive reports. [Historical sink diagnostics](../../experiments/parallel-andy-studies/closed-bottom-liquid-sinks.md).

The later full-geometry Phase 7b campaign tested collector thickness, removal strength and numerical controls. Four of the five initial thickness cases reached 5000 iterations without satisfying the combined assessment; the thickest case diverged before that horizon. Later numerical changes altered residuals and extreme velocity events but did not establish balanced stationary collection.

The final controlled comparison weakened the sink by increasing its depletion time fivefold. Table 2 gives the resulting late-window evidence.

*Table 2. Final Phase 7b comparison. Flow and residual statistics use iterations 4501–5000. Inventory change compares means over 4001–4500 and 4501–5000, divided by the larger mean.*

| Quantity | E6: τ = 0.02 s | E7: τ = 0.10 s | Required |
| --- | ---: | ---: | ---: |
| Mean absolute liquid imbalance (% liquid feed) | 144.369 | 148.213 | ≤1 |
| Mean absolute vapour imbalance (% vapour feed) | 1.520 | 1.776 | ≤1 |
| Mean absolute native-mixture imbalance (% total feed) | 84.841 | 87.000 | ≤1 |
| Inventory mean increase (%) | 18.451 | 15.195 | ≤1 |
| Maximum continuity residual | 1.3259 | 1.3222 | <0.001 |
| Mean applied liquid removal (kg/s) | 275.962 | 272.028 | Assessed within the complete balance |

The mean collector inventory rose by approximately 4.93 times when the depletion time increased fivefold. Mean removal consequently remained close to its earlier value. In E7, removal of 272.028 kg/s exceeded liquid feed of 116.921 kg/s while whole-domain inventory still increased. These outputs were inconsistent with a conservative steady interpretation.

The source checks and independently reduced inventories supported the recorded observations. Regional accounts placed most of the late signed liquid deficit above the collector, but did not isolate a source, transport, mesh or startup mechanism as its cause. The correct application of the specified removal law therefore did not resolve the broader flow inconsistency.

Phase 7b closed without a qualified steady solution. A subsequent conditioning experiment was stopped at iteration 128, before its first planned gate and before restoration of the full equations. It was an incomplete test, not evidence that the proposed conditioning method failed. [Phase closure](../../experiments/phase-07b-full-geometry-liquid-removal/closure.md).

### 4.4 Brief resolved drainage did not persist in longer tests

The historical resolved-outlet studies removed the volumetric sink and introduced a physical brine boundary. Clean transient VOF tests achieved a short drainage window at 0.05% of nominal feed. During that ten-step window, the brine face remained liquid-filled and the reported total imbalance was approximately −9.11 × 10⁻⁸ kg/s.

Longer tests changed the conclusion. At the same fixed pressure, the subsequent hold failed its liquid-balance requirement. A separate 70-step test with one pressure adjustment retained low continuity, liquid coverage at the drain and no wrong-phase leakage, but its final-ten maximum liquid imbalance was 0.01155 kg/s against a 0.005 kg/s limit. The short success therefore did not establish sustained drainage. [Resolved-outlet history](../../experiments/parallel-andy-studies/resolved-brine-outlet.md).

The later steady VOF study tested two initial pool levels at unchanged downstream head. Both lost liquid and failed the required conservation and stationarity conditions. Greater initial submergence reduced final vapour leakage through the drain at iteration 1000, but increased the liquid imbalance. Loss of the liquid seal alone was therefore insufficient to explain all the observed inadequacy.

![Two initial pool levels under the same numerical treatment](../../../PyAnsys/output/phase09/comparison/two-start-comparison.png)

*Figure 2. Recorded steady VOF comparison from two initial pool levels. The fields develop over solver iterations, not physical elapsed time. Neither case establishes a stationary operating pool. Source: the phase's audited two-start comparison.*

An unchanged continuation of the higher-pool case from iteration 1000 to 2000 also failed to establish stationary drainage (Table 3).

*Table 3. Higher-pool steady VOF extension, iterations 1001–2000.*

| Measure | Recorded result | Required |
| --- | ---: | --- |
| Mean absolute liquid imbalance (% liquid feed) | 401.175 | ≤0.5 |
| Mean absolute vapour imbalance (% vapour feed) | 3.754 | ≤0.5 |
| Mean absolute mixture imbalance (% total feed) | 235.832 | ≤0.5 |
| Whole-domain liquid inventory (kg) | 3990.817 → 3369.910 | Stationary window |
| Whole-domain half-window mean change (%) | −8.281 | Magnitude ≤0.25 |
| Final continuity residual | 0.35136 | ≤0.001 throughout window |

The final 200 iterations lost a further 118.949 kg of liquid. Spatial comparison also showed continuing phase redistribution. Additional unchanged iteration had not resolved the principal problem, and the campaign closed unqualified. The result concerns the tested steady formulation and assumed downstream boundary; it does not rule out a steady physical separator state. [Extension results](../../experiments/phase-09-steady-vof-pool/results.md).

### 4.5 Initialization controls narrowed the pressure–gravity question

The pressure–gravity campaign examined whether the prepared initial state preserved rest and which controlled changes affected its first response. Seven contrasts used 85 solved iterations in total. Table 4 separates the completed matched controls from the guarded one-iteration tests.

*Table 4. Pressure–gravity initialization diagnostics. Peak speed is measured over each recorded run; the horizons differ by design.*

| Contrast | Solved iterations | Peak speed (m/s) | Outcome |
| --- | ---: | ---: | --- |
| Two-phase, body-force update set to one | 1 | 25.729 | Speed guard |
| Low-order face interpolation | 1 | 30.930 | Speed guard |
| Zero gravity, 1.12 MPa gauge representation | 40 | 2.81 × 10⁻⁶ | Inventory guard |
| Zero gravity, equivalent zero-gauge representation | 40 | 0 | Matched diagnostic conditions passed |
| Gravity restored, equivalent pressure datum | 1 | 30.930 | Speed guard |
| Homogeneous liquid with matched hydrostatic outlets | 1 | 4.394 | Speed guard |
| Homogeneous liquid, body-force update set to one | 1 | 31.847 | Speed guard |

Changing to the equivalent zero-gauge representation removed the inventory drift in the matched zero-gravity test. The same pressure representation did not resolve the gravity-on first-iteration motion. The pressure-offset effect therefore explained only part of the observed behaviour.

Homogeneous liquid also lost rest, showing that an interface was not necessary for this startup disturbance. Its nearly unchanged liquid inventory did not establish conservation because substantial boundary fluxes remained. These tests narrowed the diagnostic question to a gravity-on initialization and numerical-response problem without isolating one internal cause.

The campaign tested preservation of rest from the first iteration. It did not test eventual convergence after an initial disturbance. Its endpoints cannot support drainage, operating performance or a general conclusion that steady simulation is impossible. [Pressure–gravity closure](../../experiments/pressure-gravity-initialization/closure.md).

### 4.6 Current mesh preparation has not established mesh independence

The current single-inlet family contains seven meshes from 357,145 to 5,479,605 cells. Geometry and file checks established a common supplied CAD basis, positive cell volumes and no free or multiple boundary faces in the recorded audits. Minimum orthogonal quality ranged from approximately 0.203 to 0.240. These checks establish preparation evidence, not solution accuracy.

At the recorded 11 October cutoff, M01–M05 had failed numerically before the intended 5000-iteration horizon. M06–M07 and the selected body-force follow-up had not supplied a completed qualified comparison. The detailed M01–M04 diagnosis found liquid accumulation and large liquid-flux deficits before velocity and residual overflow. The shared behaviour supported investigation of common setup and numerical factors; it did not eliminate local mesh effects.

![Liquid inventory and outlet-flow histories from the mesh-family diagnosis](../../../PyAnsys/output/phase10-single-inlet-mesh-convergence/divergence-diagnosis-20261011/liquid-balance.png)

*Figure 3. Preserved diagnostic snapshot of the new mesh family. M01–M04 cover the selected pre-overflow samples; M05 is partial in this figure and subsequently failed. These traces show numerical development rather than converged mesh outputs. Source: the 11 October divergence diagnosis.*

The family therefore supports a mesh-preparation and failure-assessment result at this stage. It does not support mesh independence, a GCI estimate or an accuracy or timing advantage over the historical meshes. [Current results](../../experiments/phase-10-single-inlet-mesh-convergence/results.md).

## 5. Discussion

### 5.1 The main result is a limit on the tested operating models

The selected studies consistently required more than a plausible velocity field or low liquid flow at the steam outlet. In the replication work, incomplete droplet fates and unsettled carrier solutions limited output interpretation. In the collection studies, liquid removal could be applied correctly while the surrounding flow failed conservation and inventory tests. In the resolved-outlet work, brief drainage success did not persist.

These observations support a bounded conclusion: the tested routes had not established the numerical operating state required for credible separator-performance prediction. They do not establish that the physical separator is ineffective. They also do not justify rejecting Mixture, VOF or numerical collection in all applications. Each result retains its geometry, boundary assumptions, numerical treatment and observation horizon.

### 5.2 Source application, conservation and stationarity answer different questions

Source readback establishes whether the intended removal term was assigned and applied. A mass account then tests whether the calculated flows and sources are mutually consistent. Inventory histories provide a separate assessment of whether the solution is still changing. These checks can give different answers, as the Phase 7b comparison demonstrates.

The source-accounting correction was particularly important because it changed the apparent severity of earlier imbalance. Adding a removal term to a report that already included it counted the same process twice. Independent definitions of boundary-only flow and applied source were therefore necessary before judging improvement.

Likewise, normalising a reported phase fraction or reproducing native inventory through an independent reduction verifies the interpretation of that field. It does not repair a failed mass balance. The practical contribution of the evidence system was to expose these distinctions and prevent an implementation success from being treated as a physically qualified result.

### 5.3 Numerical remedies require discriminating tests

The collector and pressure–gravity campaigns narrowed specific hypotheses. A fivefold increase in collector depletion time caused collector inventory to increase while removal remained similar; it did not restore balance. A pressure-datum change corrected the zero-gravity drift but did not remove the gravity-on startup disturbance. Homogeneous-liquid tests showed that the interface was not required for that disturbance.

None of these findings identifies a unique mechanism for all observed failures. The studies span different formulations, so similar symptoms do not establish one shared cause. Their value is to define smaller follow-up questions. In particular, a simple homogeneous hydrostatic benchmark could separate initialization and discretisation behaviour from the full separator's geometric and outlet complexity.

The mesh results make a related point. Changes between grids cannot be assigned to spatial resolution when the outputs still drift strongly within each calculation. More cells or better selected mesh-quality metrics do not resolve that comparison by themselves. A credible reference requires sufficiently settled outputs before a refinement trend can be interpreted.

### 5.4 Relationship to Shuhei's model development

Shuhei Yokkaichi's separate investigation used a simplified domain and developed numerical liquid collection with a reduced-feed hold, checked inlet ramp and subsequent solver continuation. The resulting full-feed parent enabled common-starting-field roughness and wall-film comparisons. His draft treats this as a model-development contribution while retaining a terminal liquid-balance remainder of approximately 20.81% of liquid feed.

The wall-film comparison reduced mean bulk-liquid steam-outlet flow from 24.369 to 1.735 kg/s, but also changed retained inventory and added another liquid store. A later film calculation reached 500 ms under frozen bulk fields with 9.5444 kg of film. Final-window accretion, drainage and storage were approximately 81.121, 69.600 and 11.528 kg/s, respectively. The film therefore drained while continuing to accumulate liquid. [Shuhei's report results](../draft/03-results.md); [owning film-development record](../../experiments/phase-07-2a-wall-liquid-routing/stage-03-shortened-reconstruction/early-ewf-startup/inlet-speed-500ms/results.md).

These results extend the project evidence on represented liquid routes. They do not form a controlled comparison with the full-geometry campaigns in this report. Differences in geometry, source law, startup, active equations and mesh prevent attribution of the outcomes to one approach. Together, the branches identify the need to assess collection, internal transfer and retained inventory alongside outlet flow.

### 5.5 Limitations and implications

The investigation combined exploratory work and controlled comparisons, with unequal horizons and incomplete records in some historical cases. The original replication lacked complete geometry and inherited-setting parity. Current mesh qualification is incomplete, and the downstream pressure and resistance assumptions lack matched plant evidence. No branch in this report establishes validated separator performance.

The steady calculations also limit interpretation of inventory evolution. Their iteration coordinate describes numerical development, not the physical filling or draining time of the vessel. Short transient diagnostics supplied physical time coordinates, but their low feed and short duration did not establish operating capability.

The appropriate engineering use of the present results is to guide model development and specify the evidence required for a later performance assessment. Selecting an optimum inlet, operating pressure or collection treatment would exceed the completed comparison evidence.

## 6. Conclusions and future work

### 6.1 Conclusions

The reconstruction and mesh investigations produced useful diagnostic datasets but did not qualify the inherited performance outputs. Incomplete droplet trajectories, carrier residuals and continuing inventory and pressure changes limited the interpretation of provisional quality and mesh trends.

The tested liquid-removal treatments did not establish conservative stationary operation. Numerical collectors removed liquid according to their prescribed laws while phase balances and inventories remained inadequate. Brief resolved drainage at very low feed did not persist in longer holds, and the later steady VOF continuation retained large liquid-balance errors and ongoing inventory loss.

Controlled initialization tests identified a pressure-representation effect in the zero-gravity case and an unresolved gravity-on disturbance. Homogeneous liquid also developed motion, so the interface was not necessary for that startup response. These observations narrow the next diagnostic question without establishing one cause or excluding eventual steady convergence.

The study's contribution is a bounded assessment of the tested models and a traceable separation of implementation, accounting, numerical development and physical prediction. Complete operating conservation, stationarity, resolution assessment and validation remain necessary before reporting separator-efficiency or pressure-loss performance.

### 6.2 Future work

The first priority is a simpler hydrostatic benchmark with a verified initialization sequence and compatible pressure boundaries. It should assess pressure, velocity and boundary flux errors and distinguish first-iteration rest preservation from eventual convergence. This would test the pressure–gravity question without the full separator geometry.

The next priority is to constrain the resolved drain model using the intended downstream head and resistance. These quantities should be justified independently rather than adjusted solely to obtain a favourable computed balance. A collector-based alternative should retain its explicit model assumptions and be assessed against the same operating requirements.

A qualified reference would then support matched mesh and applicable timestep comparisons using stable quantities of interest. The ongoing mesh campaign should be reported according to its completed evidence, including failed levels, without converting queue completion into a convergence claim.

Finally, performance assessment requires suitable measurements of liquid carryover, brine discharge and pressure loss with compatible definitions and uncertainty. Renewed droplet or film studies should maintain separate liquid accounts and establish the fate of represented liquid before interpreting reduced outlet flow as improved separation.

## 7. References

National Aeronautics and Space Administration. (2021a, February 10). *Examining iterative convergence*. NPARC Alliance CFD verification and validation tutorial. [Source](https://www.grc.nasa.gov/www/wind/valid/tutorial/iterconv.html).

National Aeronautics and Space Administration. (2021b, February 10). *Validation assessment*. NPARC Alliance CFD verification and validation tutorial. [Source](https://www.grc.nasa.gov/www/wind/valid/tutorial/valassess.html).

Purnanto, M. H., Zarrouk, S. J., & Cater, J. E. (2013). CFD modelling of two-phase flow inside geothermal steam–water separators. *IPENZ Transactions, 40*, 1–10. [Author-uploaded full text](https://www.researchgate.net/publication/269519626_CFD_MODELLING_OF_TWO-PHASE_FLOW_INSIDE_GEOTHERMAL_STEAM-WATER_SEPARATORS).

Zarrouk, S. J., & Purnanto, M. H. (2015). Geothermal steam–water separators: Design overview. *Geothermics, 53*, 236–254. [Publisher record](https://www.sciencedirect.com/science/article/abs/pii/S0375650514000637). [DOI](https://doi.org/10.1016/j.geothermics.2014.05.009).

## Appendix A. Project evidence register

These internal links retain the route from draft claims to the owning project records. They are working evidence notes, not a substitute for the final reference and data-availability format.

| Draft section | Owning record | Main use |
| --- | --- | --- |
| 1 and 5 | [Project scope](../../scope.md); [V&V limits](../../vnv.md) | Research purpose and overall claim boundary |
| 3 and 4.1 | [Replication](../../experiments/parallel-andy-studies/enthalpy-dpm-replication.md) | Operating matrix, particle accounts and limitations |
| 4.2 | [Historical mesh study](../../experiments/phase-02-parity-reset-and-pre-v2-qualification/purnanto-08b-parity-split-inlet/mesh-convergence-checkpoint-20260803.md) | Dated checkpoint plus later seven-mesh closure and continuation |
| 4.3 | [Historical sinks](../../experiments/parallel-andy-studies/closed-bottom-liquid-sinks.md) | Corrected source accounting and failed stability windows |
| 3 and 4.3 | [Phase 7b closure](../../experiments/phase-07b-full-geometry-liquid-removal/closure.md); [E7 comparison](../../experiments/phase-07b-full-geometry-liquid-removal/convergence-investigation/coupled-nphase-weaker-sink/results.md) | Selected quantitative comparison and partial-test disposition |
| 4.4 | [Historical resolved outlet](../../experiments/parallel-andy-studies/resolved-brine-outlet.md) | Brief transient success and later nonacceptance |
| 3 and 4.4 | [Steady VOF setup](../../experiments/phase-09-steady-vof-pool/setup.md); [results](../../experiments/phase-09-steady-vof-pool/results.md); [closure](../../experiments/phase-09-steady-vof-pool/closure.md) | Two-start assessment and authoritative N2000 extension results |
| 4.5 | [Pressure–gravity closure](../../experiments/pressure-gravity-initialization/closure.md) | Seven diagnostic outcomes and limits |
| 4.6 | [Mesh results](../../experiments/phase-10-single-inlet-mesh-convergence/results.md); [failure diagnosis](../../experiments/phase-10-single-inlet-mesh-convergence/divergence-diagnosis-20261011.md) | Dated preparation and failure snapshot |
| 5.4 | [Shuhei's draft](../draft/03-results.md); [film campaign](../../experiments/phase-07-2a-wall-liquid-routing/stage-03-shortened-reconstruction/early-ewf-startup/inlet-speed-500ms/results.md) | Attributed comparison context |

Historical migration records preserve reported observations from the original notes. Their linked remote or archived machine artifacts have not all been re-audited for this draft. These source limits must remain attached to any quantitative comparison developed from them.

## Appendix B. Items for the next writing pass

| Item | Required development |
| --- | --- |
| Author contribution | Confirm individual work, shared geometry/code and any co-worker figures used |
| Research framing | Review the proposed emphasis and title with Andy |
| Literature | Expand the short review with primary-source comparisons of collection, VOF, wall transport and reproducibility |
| Model description | Add geometry dimensions, governing equations and a compact per-family settings table from the exact records |
| Figures | Add a full-geometry domain view and a Phase 7b conservation/inventory comparison; simplify the diagnostic figures for final print size |
| Current mesh results | Refresh the dated cutoff when the selected calculations and review are complete |
| Historical results | Reconcile selected plots with available machine histories before final quantitative reuse |
| References | Complete APA 7 formatting, add checked version-specific Fluent references and establish an appropriate citation for co-worker results |
| Report requirements | Recover the original rubric and structuring PDFs; confirm declarations, contribution requirements and final page count |
| Front matter | Complete names, declaration, acknowledgements and final contents |

The next pass should develop the main Results argument and its figures before expanding background material or finalising the abstract.
