# Live Fluent Post-Processing Report: TwoPhaseInletV2(Purnanto)-25-05000

## Source Case/Data
- Server id: `2`
- Case file: `C:\Users\syok443\Documents\TwoPhaseInletV2(Purnanto)\TwoPhaseInletV2(Purnanto)-25-05000.cas.h5`
- Data file: `C:\Users\syok443\Documents\TwoPhaseInletV2(Purnanto)\TwoPhaseInletV2(Purnanto)-25-05000.dat.h5`
- Load mode: `already-loaded-session`

## Boundary/Model Sanity
- Fluent version: `Ansys Fluent 2024 R2`
- mass_flow_inlet: `liquidinlet, steaminlet`
- pressure_outlet: `steamoutlet`
- wall: `bottom, wall`
- interior: `interior-fluid`

## Carrier Flux Metrics
- Liquid inlet mass flow: `116.920000 kg/s`
- Vapor inlet mass flow: `80.690000 kg/s`
- Steam-outlet liquid mass flow: `8.213201e-02 kg/s`
- Steam-outlet vapor mass flow: `81.464165 kg/s`
- Phase-flux efficiency `eta_phase`: `0.999298`
- Steam-outlet dryness `x_out`: `0.998993`
- Mass imbalance: `1.160637e+02 kg/s`
- Mass-imbalance note: Mass imbalance is larger than the reported steam-line liquid carryover; do not treat carryover as strong quantitative evidence.

## DPM Inventory
- DPM enabled: `True`
- Active injections: `6`
- Stored DPM result fields available: `False`
- Active diameters [um]: `5.63, 28.14, 56.27, 112.54, 168.811, 348.88`
- Represented mass-flow total: `29.220000 kg/s`

## Per-Injection DPM Sample
- Sample mode: `dpm-sample-per-injection`
- Selected boundaries: `steamoutlet`
- Aggregate tracked: `13020`
- Aggregate escaped: `8`
- Aggregate trapped: `0`
- Aggregate incomplete: `13012`

- injection-112-micron: tracked `2170`, escaped `0`, trapped `0`, incomplete `2170`
- injection-168-micron: tracked `2170`, escaped `0`, trapped `0`, incomplete `2170`
- injection-28-micron: tracked `2170`, escaped `0`, trapped `0`, incomplete `2170`
- injection-348-micron: tracked `2170`, escaped `0`, trapped `0`, incomplete `2170`
- injection-5-micron: tracked `2170`, escaped `8`, trapped `0`, incomplete `2162`
- injection-56-micron: tracked `2170`, escaped `0`, trapped `0`, incomplete `2170`

## Limitations / Claim Class
- Claim class ceiling: `Debug only`
- This workflow reused the existing loaded case/data without setup rebuild, mesh replay, or injection creation. An explicit per-injection `dpm-sample` pass was run on the active injections.
- The aggregate DPM interpretation for this run is intentionally partial because the user excluded 562 um, 844 um, 1631 um.
- Per-injection DPM counts were sampled against the selected reporting boundaries only, so they remain diagnostic rather than full validated fate accounting.
- Session warning: Could not discover phase-material mapping from the live state; using fallback phase-1=vapor, phase-2=liquid.
- DPM warning: No stored DPM fate/result summary fields were found in the loaded session; this pass is inventory-only for DPM.
