# Phase 8 Stage 1 — Storyline reconstruction on the new mesh

| Item | Phase 8 — Storyline reconstruction on the new mesh |
| --- | --- |
| — | Phase 8 recreates selected earlier setups on the existing Phase 7.2A 60k mesh to explain how the project reached its current model |
| Its primary deliverable | is a reproducible simulation history explaining the past steps that led to the current model, supported by common reports |
| Mass-imbalance closure and continuity reduction | are not Phase 8 goals or progression gates; unsuccessful and unresolved simulations belong in the storyline |
| — | See the human clarification in [the phase contract](CONTEXT.md) |
| Only the human-authorized Server 1 matched batch | is resumed; the broader loop remains paused |

<details>
<summary>Supporting detail — Phase 8 — Storyline reconstruction on the new mesh</summary>

| Item | Phase 8 — Storyline reconstruction on the new mesh |
| --- | --- |
| Historical results guide case selection but | are not quantitative baselines |
| [phase context](CONTEXT.md) | records the four-family scientific envelope and remaining matrix choices |
| — | The [common run and report contract](report-contract.md) defines measurements and provenance required of every selected case |
| [26.81 m/s F1/F2 baseline lineage audit](baseline-lineage-audit.md) compares the saved initialized cases against the historical | records and identifies the remaining run gates |
| — | Families 1–4 have no absorber; an absorber comparison follows only after Phase 7.2A is finalized |
| source narrative | is the [Phase 1](../../phase-01-purnanto-baseline-and-inlet-exploration/interpretation.md) through [Phase 7.2A](../../phase-07-2a-wall-liquid-routing/interpretation.md) interpretation chain |
| — | The [phase result](results.md) brings together the family plots, native Fluent contours/vectors, and supported changes across stages |

</details>

## Family setups

| Item | Family setups |
| --- | --- |
| — | [F0 — mixed inlet, SIMPLE and one-way DPM](f0-simple/setup.md) |
|  | [F1 — mixed one-inlet carrier and one-way DPM](f1-one-inlet/setup.md) |
|  | [F2 — split two-phase carrier and one-way DPM](f2-split-inlet/setup.md) |
|  | [F3 — split inlet with two-way DPM fraction screen](f3-coupled-dpm/setup.md) |
|  | [F4 — coupled DPM plus EWF](f4-coupled-dpm-ewf/setup.md) |

<details>
<summary>Supporting detail — Family setups</summary>

| Item | Family setups |
| --- | --- |
| — | F1 and F2 each have all five Coupled speed cases at N10,000 |
|  | F0 contains the former F1 five-speed SIMPLE reconstruction at N10,000, reported as a numerical-package comparison with its own one-way DPM diagnostics and explicit numerical claim limits; it does not change the selected Coupled branch |
|  | The main F1 topology applies mixed feed to both original inlet faces; the merged single-face recreation is a separate case. [F1 results](f1-one-inlet/results.md) and [F2 results](f2-split-inlet/results.md) compare speed response, internal liquid distribution and diagnostic particle fates |
|  | [F3 results](f3-coupled-dpm/results.md) contain four 2.5% N11,000 pilots (20.11, 23.46, 26.81 and 32.14 m/s), a 5% reference-speed pilot, and later numerical/tracking investigations. [F4 results](f4-coupled-dpm-ewf/results.md) contain one provisional E2.7-based 5% reference-speed N11,000 film pilot |
| Its EWF basis | remains provisional because Phase 7.2A has not closed |
| intended 65-case matrix | includes five F0 points and remains incomplete |
| A five-speed, 5% one-way allocated bridge | is optional |
| figures | were produced from saved evidence without new carrier iterations |
| Numerical gaps and unresolved particle fates | remain claim limits |
| experimental loop | remains paused |

</details>

## Authorized Server 1 matched continuation

| Item | Authorized Server 1 matched continuation |
| --- | --- |
| — | The [3 October batch](../../../../PyAnsys/output/phase8-server1-matched-20261003/batch-spec.json) extends five unaveraged-source F3 points to N16,000 and supplies five matching F4 EWF points |
|  | All have the same N10,000 developed carrier basis, 6,000 mechanism-active iterations and N15,500–16,000 summary windows |
|  | Original recoveries and tracking-cap probes stay separate |
| batch | is complete and verified; the [uniform comparison](results.md#current-family-organization-and-matched-n16000-comparison) is current |
| Phase 8 | is paused at this boundary |
| Execution evidence | is in the [batch manifest](../../../../PyAnsys/output/phase8-server1-matched-20261003/batch-manifest.json) |
