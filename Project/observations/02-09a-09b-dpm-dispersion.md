> **Retired source:** ResearchProject_wiki/observations/02-09a-09b-dpm-dispersion.md
> **Migration note:** Historical wording, evidence status, and uncertainty labels are preserved; this Project copy is not a reinterpretation. Machine-generated artifacts remain with their original external owners; the retired written source is recoverable from Git history.

# Observation 02 — 09a/09b DPM Injection and Dispersion

## Comparison question

How much does the DPM tracking treatment itself alter the reported fine-droplet fate before changing carrier-flow or wall-film physics?

## Intended controlled difference

`09a` is the deterministic one-way-DPM baseline inherited from the split-inlet carrier field. `09b` retains one-way DPM and tests turbulent stochastic dispersion / random-walk treatment, including random-eddy-lifetime sensitivity. The intended fixed quantities are the carrier field, injection location, droplet size, represented loading, wall fate, step controls, and particle count.

The current evidence uses different sampling budgets and is therefore not a strict numerical one-to-one comparison. It is still enough to establish that the tracking treatment is a material modelling choice.

## Observed fate changes

| Diameter and setting | `09a` deterministic observation | `09b` stochastic observation | Interpretation |
|---|---:|---:|---|
| `5.63 µm` | `8 / 2170` escaped (`0.37%` of that bin) | `2722 / 21700` escaped with eddy lifetime off (`12.54%`); `2312 / 21700` on (`10.65%`) | dispersion changes the completed escape population materially |
| `10 µm` | `1 / 2170` escaped in the manual diagnostic | `3370 / 21700` off (`15.53%`); `2943 / 21700` on (`13.56%`) | same direction: random-walk treatment exposes more completed fine-droplet escape |
| `28.14 µm` | no resolved completed fate in the inherited sample | no escape in either stochastic setting; nearly all tracks incomplete | no size-resolved carryover conclusion yet |
| `40 µm` | not an established deterministic result | no escape; all tracks incomplete | unresolved, not proved collected |

In both fine-droplet tests, enabling random eddy lifetime reduces the reported escape fraction relative to the otherwise stochastic case. It does not remove the dominant incomplete population.

## Working interpretation

The deterministic `09a` sample is too incomplete to stand alone as a carryover estimate. `09b` shows that turbulence-driven particle dispersion can change the number of fine droplets that complete an outlet trajectory by an order of magnitude relative to the very limited deterministic sample.

This does **not** prove that stochastic tracking is more correct. It proves that the fine-droplet conclusion is sensitive to the DPM treatment and that the dispersion setting must be recorded in every comparison. The large incomplete population remains an unresolved residence-time/fate category.

## Reasoning for the next simulations

Use a fixed, named DPM protocol for all future fine-droplet comparisons:

1. run a deterministic one-way reference and a stochastic one-way reference from the same saved carrier state;
2. retain the same injection locations, mass flows, parcel count, step limit, wall fates, and physical-time/tracking budget;
3. report escaped, trapped, incomplete, and represented mass for each size; and
4. repeat stochastic runs sufficiently to show whether random-walk variance is smaller than the observed model effect.

Only after that comparison is bounded should a difference be attributed to inlet loading, global DPM interaction, or EWF physics rather than the DPM tracking treatment itself.

## Evidence

- [09a result](../experiments/purnanto-09a-dpm-deterministic-carryover/results.md)
- [09b result](../experiments/purnanto-09b-dpm-stochastic-dispersion/results.md)
- [09a setup definition](../experiments/purnanto-09a-dpm-deterministic-carryover/setup.md)
- [09b setup definition](../experiments/purnanto-09b-dpm-stochastic-dispersion/setup.md)
