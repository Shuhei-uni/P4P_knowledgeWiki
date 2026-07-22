# Observation 04 — `010V2` EWF Mechanism Comparison

## Comparison question

Starting from the clean Eulerian Wall Film (EWF) deposition control, what changes are reported when splash, edge separation, particle stripping, and their combined configuration are enabled?

## Comparison scope and evidence quality

All five branches retain the `09cV2` `5%` liquid/DPM accounting basis, EWF DPM-to-film coupling, the `wall` film wall, six original surface injections, and global DPM interaction `Off`. They are a useful mechanism-screening family, but not a matched performance study: the captured states come from different servers, Fluent versions, and iteration windows, and each reported carrier flux scope remains open.

| Case | Intended change from `010V2` | Captured session / checkpoint | Evidence available now | Comparison use |
|---|---|---|---|---|
| `010V2` | clean deposition/drainage control | server `3`; Fluent `2025 R2`; residual monitor to `1884` | carrier/residual, six complete DPM summaries, final film snapshot | control state |
| `010V2a` | particle splash only | server `2`; Fluent `2024 R2`; monitor to `1963` | carrier/residual, six complete DPM summaries, wall splash readback, final film snapshot | splash activation and snapshot sensitivity |
| `010V2b` | edge separation only | Fluent `2025 R2.03`; console checkpoint `1498`; server not recorded | complete console DPM/final-film checkpoint; no residual history for that exact checkpoint | edge-separation activation and snapshot sensitivity |
| `010V2c` | particle stripping only | server `4`; Fluent `2025 R2`; monitor to `1446` | carrier/residual, six complete DPM summaries, final film snapshot | reported stripping-branch fate and film response |
| `010V2d` | combined optional mechanisms; global DPM still off | server `3`; Fluent `2024 R2`; monitor to `1520` | carrier/residual, six complete DPM summaries, wall splash/separation evidence, final film snapshot | combined-configuration diagnostic |

Every captured carrier state has a selected-surface phase-flow imbalance of about `57.54%` of inlet mixture flow. Therefore, steam-outlet liquid flow, apparent phase efficiency, and dryness are not used below as separator-performance measures.

## Common clean-EWF baseline

`010V2` is the clean deposition/drainage control: EWF and DPM-to-film coupling are on; splash, edge separation, and stripping are intended off. It establishes a finite, localized film and a reproducible size-selective DPM fate pattern:

- fine droplets predominantly escape through `steamoutlet`;
- absorption overtakes direct escape at `168.81 µm` and remains dominant for `348.88 µm`;
- the film is localized: its `0.152 mm` maximum thickness is much larger than its `1.211 µm` area average.

This is a DPM/EWF mechanism baseline, not a validated separator baseline.

## Final film morphology relative to the clean control

All values are final snapshots on the confirmed `wall` film wall. `Δ inventory` is relative to `010V2`; it describes the captured state only and is not an accumulated film mass balance.

| Case | Film inventory | Δ inventory vs `010V2` | Maximum / area-average thickness | Derived area-average speed | Final CFL | Reported steam-outlet film flow |
|---|---:|---:|---:|---:|---:|---:|
| `010V2` control | `0.07150 kg` | baseline | `0.152 mm` / `1.211 µm` | `0.0630 m/s` | `0.00327` | `-1.76e-6 kg/s` |
| `010V2a` splash | `0.07431 kg` | `+3.9%` | `0.164 mm` / `1.259 µm` | `0.0665 m/s` | `0.01063` | `-6.59e-6 kg/s` |
| `010V2b` edge separation | `0.05639 kg` | `-21.1%` | `0.123 mm` / `0.955 µm` | `0.0530 m/s` | `0.00323` | `0 kg/s` |
| `010V2c` stripping branch | `0.05440 kg` | `-23.9%` | `0.121 mm` / `0.921 µm` | `0.0516 m/s` | `0.00285` | `-2.22e-6 kg/s` |
| `010V2d` combined | `0.05668 kg` | `-20.7%` | `0.125 mm` / `0.960 µm` | `0.0533 m/s` | `0.00321` | `0 kg/s` |

The splash snapshot has the largest stored film, thickness, and final CFL in this family, although its CFL remains small. The edge-separation, stripping, and combined snapshots all contain roughly one-fifth less film inventory than the clean control and have lower derived film speed. This is a useful directional film-state contrast, but the different checkpoint maturity and versions prevent attributing those differences to a mechanism alone.

## Size-resolved DPM fate comparison

The original-particle terminal mass-transfer rows close to normal printed precision for the reported complete DPM sweeps. The table compares absorbed represented mass, which is the most direct common measure of original particles reaching the film. Escape remains dominant at `5.63`, `28.14`, `56.27`, and `112.54 µm`; absorption overtakes escape at `168.81 µm` in every completed branch.

| Diameter | `010V2` clean | `010V2a` splash | `010V2b` edge separation | `010V2c` stripping branch | `010V2d` combined |
|---:|---:|---:|---:|---:|---:|
| `56.27 µm` absorbed mass | `0.01959 kg/s` | `0.01413 kg/s` | `0.01324 kg/s` | `0.009659 kg/s` | `0.01189 kg/s` |
| `112.54 µm` absorbed mass | `0.1192 kg/s` | `0.1152 kg/s` | `0.1156 kg/s` | `0.1116 kg/s` | `0.1120 kg/s` |
| `168.81 µm` absorbed mass | `0.2077 kg/s` | `0.2032 kg/s` | `0.1988 kg/s` | `0.1952 kg/s` | `0.1960 kg/s` |
| `348.88 µm` absorbed mass | `3.619 kg/s` | `3.624 kg/s` | `3.610 kg/s` | `3.567 kg/s` | `3.601 kg/s` |
| Absorption-over-escape crossover | `168.81 µm` | `168.81 µm` | `168.81 µm` | `168.81 µm` | `168.81 µm` |

The shared crossover is the strongest family-wide DPM observation: optional EWF mechanisms do not remove the baseline size-selective deposition behaviour at these diagnostic checkpoints. The stripping branch has complete console-reported terminal fates and follows the same progression: `1655` of `2170` tracked `348.88 µm` parcels are absorbed, compared with `474` escapes and `41` traps. Its lower absorbed mass than the clean control is a reported branch response, not a quantified stripping loss.

## Optional-mechanism activation and reported outputs

Event counters, original-particle fates, and generated particles are different accounting layers. An event count is not added to original-particle fate counts or treated as represented mass.

| Mechanism / branch | Confirmed or reported activation signal | Reported DPM/film response | Narrowest supported conclusion |
|---|---|---|---|
| Clean control — `010V2` | no optional-mechanism event is reported | finite film and six complete original-particle fate summaries | establishes clean EWF deposition pattern |
| Splash — `010V2a` | wall splash readback on; `12` splash events: four each at `56.27`, `112.54`, and `168.81 µm` | film inventory is `3.9%` above control; original-particle absorption remains size-selective | splash pathway is active for middle-size impacts; event mass is not yet reconciled |
| Edge separation — `010V2b` | film-boundary separation permitted; `120` separated particles reported for `348.88 µm` | film inventory is `21.1%` below control; coarse class remains absorption-dominant | edge separation activates for the coarse class; its count is not a terminal mass sink |
| Stripping branch — `010V2c` | stripping-only configuration; complete console fate and film results reported | lower film inventory and absorbed mass than control while retaining the same `168.81 µm` crossover | the stripping branch has a coherent reported response; it does not yet quantify stripped-particle mass separately |
| Combined — `010V2d` | wall splash/separation active; `20` splash events and `120` separation events for `348.88 µm` | film inventory is `20.7%` below control; coarse absorption remains dominant | combined configuration is operable and repeats coarse optional-mechanism signals; no synergy claim is justified |

`010V2b` requires a specific count caution: the `348.88 µm` console checkpoint reports `2290` tracked and `120` separated particles, while its displayed terminal fate counts sum to `2410`. Preserve the count as an activation signal, but do not use it in a particle or mass closure until Fluent's separated-particle definition is clarified.

## Bookkeeping interpretation

The reported outputs fit the following EWF accounting map:

```text
original DPM impact
  -> direct escape / bottom trap / film absorption
  -> film inventory change + film boundary outflow
  -> optional splash, edge-separation, or stripping generated particles
  -> generated-particle terminal fates
```

The completed original-particle fate rows and final film snapshots provide useful screening evidence. They do not close the optional-mechanism ledger because the captured snapshots are not histories and the reported splash/separation counts have no represented generated-particle mass. The stripping branch should be read from its complete console fate/film outputs, not from an assumed zero response; however, it also lacks a separately reported stripping-generated mass term.

## Working interpretation

**Reported:** every branch retains a finite, localized low-CFL wall film and the same size-selective transition from fine-droplet escape to coarse-droplet absorption. Splash and edge-separation event signals appear only where their related mechanism branches or the combined branch are configured. The stripping branch has complete reported fates and a smaller final film snapshot than the clean control.

**Inferred:** the optional mechanisms alter the captured film state and can generate secondary-event signals without overturning the primary size-selective deposition pattern. The lower final inventory in the edge-separation, stripping, and combined branches is a useful hypothesis that optional film-removal pathways may reduce stored wall liquid.

**Unresolved:** whether any optional mechanism changes time-integrated liquid carryover, film inventory, or deposition efficiency; whether the lower final inventory is a mechanism effect rather than checkpoint maturity; and how event counts map to represented secondary-particle mass.

The combined branch is a configuration diagnostic, not evidence of mechanism synergy. Its setup rule requires individually bounded, reportable mechanism mass before a physical combined claim; that gate is not yet met.

## Reasoning for the next simulations

Use one accepted `010V2` case/data checkpoint and one defined physical-time interval for all isolated reruns.

1. Correct the Fluent `2025 R2` diagnostic field tokens and record histories for film inventory, coverage, CFL, `film-dpm-mass-src`, film outflow, `film-stripped-mass`, `film-separated-mass`, and generated injection flow.
2. Run clean EWF, splash-only, edge-separation-only, and stripping-only cases over the identical interval, preserving the six original injection settings and global DPM interaction state.
3. Report original-particle fates and generated-particle fates separately, with a mass closure for each mechanism rather than event counts alone.
4. Include the lower liquid path and mixture/phase fluxes so carrier and film bookkeeping can be closed over the same interval.
5. Combine only mechanisms that first show bounded film inventory and a reportable generated-particle mass; compare the combination against the same clean-control window.

## Evidence

- [010V2 control result](../../Setups/reports/010V2/results.md)
- [010V2a splash result](../../Setups/reports/010V2a/results.md)
- [010V2b edge-separation result](../../Setups/reports/010V2b/results.md)
- [010V2c stripping result](../../Setups/reports/010V2c/results.md)
- [010V2d combined result](../../Setups/reports/010V2d/results.md)
- [010V2 control DPM fate rows](../../PyAnsys/output/ewf_dpm_diagnostics/010V2-20260722-dpm/dpm_zone_summary.csv)
- [010V2c stripping-branch DPM fate rows](../../PyAnsys/output/ewf_dpm_diagnostics/010V2c-server4-20260722-dpm/dpm_zone_summary.csv)
- [010V2d combined DPM fate rows](../../PyAnsys/output/ewf_dpm_diagnostics/010V2d-server3-20260722-dpm/dpm_zone_summary.csv)
