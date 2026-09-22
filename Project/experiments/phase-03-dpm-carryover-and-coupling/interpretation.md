# Phase 3 — Interpretation

## Why this phase existed

Phase 3 extended the two-phase carrier with Discrete Phase Model (DPM) droplets. This followed the general Purnanto modelling idea: establish the continuous separator flow field, inject droplets, and examine which droplets escape or are removed.

At this stage there was no strong experimental basis for the exact droplet population, size distribution, or represented DPM mass. The phase was therefore a sensitivity and model-learning exercise rather than a validated grade-efficiency study.

## Main hypothesis

The two-phase carrier can be used as the background flow for a Purnanto-like DPM carryover study, and droplet size, stochastic dispersion, and coupling strength should materially change escape behaviour.

## What was run

| Run | Main change | Question |
| --- | --- | --- |
| 09a | deterministic DPM | what happens without stochastic turbulent dispersion? |
| 09b | stochastic dispersion | how sensitive are fine-droplet escapes to turbulent random walk? |
| 09c | two-way DPM coupling | does droplet feedback materially change the carrier? |
| 09cV2 | DPM partition/loading control | how sensitive is the solution to represented dispersed loading? |
| 09cV3 | fine-mist PSD / 5% and 10% loading | how do smaller droplet bins and loading affect escape? |

## Representative evidence

The deterministic 09a sample showed the tracking problem immediately. In one sampled pass the 5.63 µm bin reported only 8 escaped tracks while 2162 were incomplete; the 28.14 and 56.27 µm bins were entirely incomplete.

The stochastic 09b study demonstrated that the model settings did change the fine-droplet result:

| Diameter | Random eddy lifetime | Escape fraction |
| ---: | --- | ---: |
| 5.63 µm | off | 12.54% |
| 5.63 µm | on | 10.65% |
| 10 µm | off | 15.53% |
| 10 µm | on | 13.56% |

However, most trajectories were still incomplete, so these are sensitivity signals rather than physical grade-efficiency points.

The later 09cV3 fine-mist runs similarly showed loading dependence. At the saved 5000-iteration checkpoints, the 7.07 µm bin reported 10 / 2170 escaped parcels in the 5% case and 20 / 2170 in the 10% case. Continuity remained around 1.6e-1, so the carrier was not numerically qualified.

## Interpretation

The scientific learning was that DPM outcomes are highly conditional on the assumed droplet model. Size, stochastic treatment, and represented loading all matter.

The more important project lesson was that a DPM efficiency curve cannot be stronger than the carrier field and tracking completeness underneath it. The project did not have experimental droplet-size data or sufficiently complete tracks to claim a validated separator efficiency.

This phase therefore taught more about which DPM assumptions matter than about the actual plant droplet distribution.

## Why this led to Phase 4

The DPM work treated droplets moving through the bulk flow, but a real cyclone also deposits liquid on the wall. The next question became whether explicit wall-film physics was needed to represent that interaction.

## Evidence gaps / TODO

- TODO: if a final report uses any DPM escape percentages, pair them with an incomplete-track fraction so the limitation is visible immediately.
- TODO: document any external basis that was used at the time for the selected droplet bins/PSD. If none existed, state explicitly that they were exploratory assumptions.
