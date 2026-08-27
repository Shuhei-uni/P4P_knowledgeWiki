> **Legacy source:** ResearchProject_wiki/observations/04-010v2-ewf-mechanism-comparison.md  
> **Migration note:** Historical wording, evidence status, and uncertainty labels are preserved; this Project copy is not a reinterpretation. Raw and machine-generated artifacts remain at their legacy paths.

# Observation 04 — `010V2` EWF Mechanism Comparison

## Comparison question

Starting from the clean Eulerian Wall Film (EWF) deposition control, what changes are reported when splash, edge separation, particle stripping, and their combined configuration are enabled?

## Comparison scope and evidence quality

All five branches retain the `09cV2` `5%` liquid/DPM accounting basis, EWF DPM-to-film coupling, the `wall` film wall, six original surface injections, and global DPM interaction `Off`. This update now uses the completed 5,000-iteration evidence for every branch. It is still not a matched performance study: the branches use different servers/releases and each reported carrier flux scope remains open. A fresh 2026-07-27 `010V2b` capture reproduces the EWF/DPM endpoint values but did not produce a new carrier residual/flux bundle.

| Case | Intended change from `010V2` | Captured session / checkpoint | Evidence available now | Comparison use |
|---|---|---|---|---|
| `010V2` | clean deposition/drainage control | server `1`; Fluent `2025 R2`; requested 5,000 checkpoint; residual monitor to `4996` | carrier/residual, six complete DPM summaries, final film snapshot | 5,000-iteration control state |
| `010V2a` | particle splash only | server `2`; Fluent `2025 R2`; 5,000 iterations | carrier/residual, six complete DPM summaries, wall splash readback, final film snapshot | 5,000-iteration splash diagnostic |
| `010V2b` | edge separation only | server `3`; Fluent `2025 R2`; completed 5,000 checkpoint; residual monitor to index `4999` | carrier/residual, six complete DPM summaries, wall separation runtime evidence, final film snapshot; fresh 2024 R2 recapture has no carrier bundle | 5,000-iteration edge-separation diagnostic |
| `010V2c` | particle stripping only | server `2`; Fluent `2025 R2`; user-reported 5,000 checkpoint | complete six-injection DPM/final-film analysis; carrier residual/flux bundle not captured | 5,000-iteration stripping diagnostic with carrier gap |
| `010V2d` | combined optional mechanisms; global DPM still off | server `1`; Fluent `2024 R2`; 5,000 iterations | carrier/residual, six complete DPM summaries, wall splash/separation/stripping event evidence, final film snapshot | 5,000-iteration combined diagnostic |

Every captured carrier state has a selected-surface phase-flow imbalance of about `57.54%` of inlet mixture flow. Therefore, steam-outlet liquid flow, apparent phase efficiency, and dryness are not used below as separator-performance measures.

## Common clean-EWF baseline

`010V2` is the clean deposition/drainage control: EWF and DPM-to-film coupling are on; splash, edge separation, and stripping are intended off. At the new checkpoint it has a larger but still finite final film and a stronger size-selective DPM fate pattern:

- fine droplets predominantly escape through `steamoutlet`;
- absorption overtakes direct escape at `168.81 µm` and remains dominant for `348.88 µm`;
- the film is localized: its `0.471 mm` maximum thickness is much larger than its `3.464 µm` area average.

This is a DPM/EWF mechanism baseline, not a validated separator baseline.

## Final film morphology relative to the clean control

All values are final snapshots on the confirmed `wall` film wall. `Δ inventory` is relative to `010V2`; it describes the captured state only and is not an accumulated film mass balance.

| Case | Film inventory | Δ inventory vs `010V2` | Maximum / area-average thickness | Derived area-average speed | Final CFL | Reported steam-outlet film flow |
|---|---:|---:|---:|---:|---:|---:|
| `010V2` control, 5,000 | `0.20449 kg` | baseline | `0.471 mm` / `3.464 µm` | `0.1496 m/s`* | `0.00552` | `-1.53e-6 kg/s` |
| `010V2a` splash, 5,000 | `0.20656 kg` | `+1.0%` | `0.399 mm` / `3.499 µm` | `0.1801 m/s` | `0.01076` | `-2.98e-6 kg/s` |
| `010V2b` edge separation, 5,000 | `0.20543 kg` | `+0.5%` | `0.450 mm` / `3.480 µm` | `0.1587 m/s` | `0.01096` | `0 kg/s` |
| `010V2c` stripping branch, 5,000 | `0.20107 kg` | `-1.7%` | `0.410 mm` / `3.406 µm` | `0.1340 m/s` | `0.00493` | `-1.78e-6 kg/s` |
| `010V2d` combined, 5,000 | `0.20221 kg` | `-1.1%` | `0.457 mm` / `3.425 µm` | `0.1331 m/s` | `0.00507` | `0 kg/s` |

\* Derived from the reported area-weighted velocity components; the Fluent magnitude reduction was unavailable.

At 5,000 iterations, the clean control has the largest local film thickness (`0.471 mm`), the splash branch has the largest area-average thickness and derived film speed, and `010V2b` has the largest final film CFL (`0.01096`). The completed branches have film inventories within about `1.7%` of one another. This is a snapshot contrast, not a mechanism-only effect, because checkpoint maturity, software release, and history/closure evidence differ.

## Size-resolved DPM fate comparison

The original-particle terminal mass-transfer rows close to normal printed precision for the reported complete DPM sweeps. The table compares absorbed represented mass, which is the most direct common measure of original particles reaching the film. Escape remains dominant at `5.63`, `28.14`, `56.27`, and `112.54 µm`; absorption overtakes escape at `168.81 µm` in every completed branch.

| Diameter | `010V2` clean | `010V2a` splash | `010V2b` edge separation | `010V2c` stripping branch | `010V2d` combined |
|---:|---:|---:|---:|---:|---:|
| `56.27 µm` absorbed mass | `0.02558 kg/s` | `0.02531 kg/s` | `0.01708 kg/s` | `0.02549 kg/s` | `0.03649 kg/s` |
| `112.54 µm` absorbed mass | `0.1392 kg/s` | `0.1638 kg/s` | `0.1454 kg/s` | `0.1402 kg/s` | `0.1763 kg/s` |
| `168.81 µm` absorbed mass | `0.2172 kg/s` | `0.2304 kg/s` | `0.2289 kg/s` | `0.2039 kg/s` | `0.2463 kg/s` |
| `348.88 µm` absorbed mass | `4.210 kg/s` | `4.276 kg/s` | `4.264 kg/s` | `4.236 kg/s` | `4.310 kg/s` |
| Absorption-over-escape crossover | `168.81 µm` | `168.81 µm` | `168.81 µm` | `168.81 µm` | `168.81 µm` |

The shared crossover is the strongest family-wide DPM observation: optional EWF mechanisms do not remove the baseline size-selective deposition behaviour at these diagnostic checkpoints. At 5,000, all branches report `4.210–4.310 kg/s` absorbed for `348.88 µm`. These are reported branch responses, not quantified mechanism-specific mass losses.

## Optional-mechanism activation and reported outputs

Event counters, original-particle fates, and generated particles are different accounting layers. An event count is not added to original-particle fate counts or treated as represented mass.

| Mechanism / branch | Confirmed or reported activation signal | Reported DPM/film response | Narrowest supported conclusion |
|---|---|---|---|
| Clean control — `010V2` | no optional-mechanism event is reported | finite film and six complete original-particle fate summaries | establishes clean EWF deposition pattern |
| Splash — `010V2a` | wall splash readback on; splash events printed at `112.54`, `168.81`, and `348.88 µm` (`4`, `8`, and `104` events) | 5,000-iteration film inventory is `1.0%` above the control; original-particle absorption remains size-selective | splash pathway is active; event mass is not yet reconciled |
| Edge separation — `010V2b` | film-boundary separation permitted; `171` separated events/particles reported for `348.88 µm` at 5,000 | film inventory is `0.5%` above the 5,000 control; coarse absorbed flow is `4.264 kg/s` | edge-separation runtime activity is reported, but separated mass remains unavailable |
| Stripping branch — `010V2c` | 5,000-iteration adapter pass did not provide root stripping readback or stripped mass | film inventory is `1.7%` below the 5,000 control; coarse absorbed flow is `4.236 kg/s` | the later state changes the film/fate snapshot, but stripping-specific activity and mass remain unquantified |
| Combined — `010V2d` | wall splash/separation active; `256` splash and `179` separation events for `348.88 µm`; `11` stripping events also printed | 5,000-iteration film inventory is `1.1%` below the control; coarse absorption remains dominant | combined configuration is operable and repeats coarse optional-mechanism signals; no synergy claim is justified |

`010V2b` still requires a mass-accounting caution: the 5,000-iteration terminal fate counts close to the tracked count (`236` escaped + `79` trapped + `2` incomplete + `2024` absorbed = `2341`), while the `171` separated events/particles are reported separately. Do not add separated events to the terminal closure or infer represented separated mass from the count.

## Bookkeeping interpretation

The reported outputs fit the following EWF accounting map:

```text
original DPM impact
  -> direct escape / bottom trap / film absorption
  -> film inventory change + film boundary outflow
  -> optional splash, edge-separation, or stripping generated particles
  -> generated-particle terminal fates
```

The completed original-particle fate rows and final film snapshots provide useful screening evidence. They do not close the optional-mechanism ledger because the captured snapshots are not histories and the reported splash/separation counts have no represented generated-particle mass. The stripping branch should be read from its complete DPM/final-film outputs, not from an assumed zero response; however, it also lacks a separately reported stripping-generated mass term.

## Working interpretation

**Reported:** every completed checkpoint retains a finite, localized wall film and the same size-selective transition from fine-droplet escape to coarse-droplet absorption. Splash and edge-separation event signals appear where their related mechanism branches or the combined branch are configured. The 5,000-iteration control, splash, stripping, and combined snapshots have similar final film inventories (within about `2%`), but their DPM absorption values differ materially at the larger diameters.

**Inferred:** the optional mechanisms can alter the captured DPM fate and generate secondary-event signals without overturning the primary size-selective deposition pattern. At the 5,000 endpoints, the edge-separation branch has a similar film inventory to the clean control but a higher final CFL and stronger coarse interception than its earlier checkpoint; checkpoint maturity and Fluent-version differences remain confounded.

**Unresolved:** whether any optional mechanism changes time-integrated liquid carryover, film inventory, or deposition efficiency; whether the lower final inventory is a mechanism effect rather than checkpoint maturity; and how event counts map to represented secondary-particle mass.

The combined branch is a configuration diagnostic, not evidence of mechanism synergy. Its setup rule requires individually bounded, reportable mechanism mass before a physical combined claim; that gate is not yet met.

## Reasoning for the next simulations

Use one accepted `010V2` case/data checkpoint and one defined physical-time interval for all isolated reruns.

1. Correct the Fluent `2025 R2` diagnostic field tokens and record histories for film inventory, coverage, CFL, `film-dpm-mass-src`, film outflow, `film-stripped-mass`, `film-separated-mass`, and generated injection flow.
2. Run clean EWF, splash-only, edge-separation-only, and stripping-only cases over the identical interval, preserving the six original injection settings and global DPM interaction state; use the completed `010V2b` checkpoint as the edge-separation evidence anchor.
3. Report original-particle fates and generated-particle fates separately, with a mass closure for each mechanism rather than event counts alone.
4. Include the lower liquid path and mixture/phase fluxes so carrier and film bookkeeping can be closed over the same interval.
5. Combine only mechanisms that first show bounded film inventory and a reportable generated-particle mass; compare the combination against the same clean-control window.

## Evidence

- [010V2 control result](../experiments/purnanto-010V2-clean-ewf-deposition/results.md)
- [010V2a splash result](../experiments/purnanto-010V2a-ewf-splash/results.md)
- [010V2b edge-separation result](../experiments/purnanto-010V2b-ewf-edge-separation/results.md)
- [010V2c stripping result](../experiments/purnanto-010V2c-ewf-particle-stripping/results.md)
- [010V2d combined result](../experiments/purnanto-010V2d-ewf-combined-mechanisms/results.md)
- 010V2 5,000-iteration DPM fate rows (historical machine artifact path: `../../PyAnsys/output/ewf_dpm_diagnostics/010V2-5000it-20260723-dpm/dpm_zone_summary.csv`; not migrated)
- 010V2a 5,000-iteration DPM fate rows (historical machine artifact path: `../../PyAnsys/output/ewf_dpm_diagnostics/010V2a-server2-20260724-5000-dpm/dpm_zone_summary.csv`; not migrated)
- 010V2c 5,000-iteration DPM fate rows (historical machine artifact path: `../../PyAnsys/output/ewf_dpm_diagnostics/010V2c-server2-20260723-5000it-dpm/dpm_zone_summary.csv`; not migrated)
- 010V2d 5,000-iteration DPM fate rows (historical machine artifact path: `../../PyAnsys/output/ewf_dpm_diagnostics/010V2d-server1-20260723-5000-dpm/dpm_zone_summary.csv`; not migrated)
- 010V2b 5,000-iteration DPM fate rows (historical machine artifact path: `../../PyAnsys/output/ewf_dpm_diagnostics/010V2b-5000-dpm-20260723-r2/dpm_zone_summary.csv`; not migrated)
- 010V2b 5,000-iteration carrier/residual checks (historical machine artifact path: `../../PyAnsys/output/post_simulation_analysis/010V2b-5000-20260723-flux-check.json`; not migrated), residual history (historical machine artifact path: `../../PyAnsys/output/post_simulation_analysis/010V2b-5000-20260723-residual-check.json`; not migrated)
- 010V2b fresh 2026-07-27 DPM fate rows (historical machine artifact path: `../../PyAnsys/output/ewf_dpm_diagnostics/010V2b-server3-20260727-4999-dpm/dpm_zone_summary.csv`; not migrated)
