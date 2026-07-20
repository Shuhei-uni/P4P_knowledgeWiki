# Live Fluent Post-Processing Report: 10a

## Source Case/Data
- Server id: `1`
- Case file: `C:\Users\syok443\Documents\TwoPhaseInletV2(Purnanto)\10a\10a-25-02000.cas.h5`
- Data file: `C:\Users\syok443\Documents\TwoPhaseInletV2(Purnanto)\10a\10a-25-02805.dat.h5`
- Load mode: `explicit-read_case-then-read_data`

## Boundary/Model Sanity
- Fluent version: `Ansys Fluent 2024 R2`
- mass_flow_inlet: `liquidinlet, steaminlet`
- pressure_outlet: `steamoutlet`
- wall: `bottom, wall`
- interior: `interior-fluid`

## Carrier Flux Metrics
- Liquid inlet mass flow: `116.920000 kg/s`
- Vapor inlet mass flow: `80.690000 kg/s`
- Steam-outlet liquid mass flow: `1.959642e-04 kg/s`
- Steam-outlet vapor mass flow: `81.452089 kg/s`
- Phase-flux efficiency `eta_phase`: `0.999998`
- Steam-outlet dryness `x_out`: `0.999998`
- Mass imbalance: `1.161577e+02 kg/s`
- Mass-imbalance note: Derived from phase-specific fluxes because the mixture mass-flow report was unavailable.

## DPM Inventory
- DPM enabled: `True`
- Active injections: `6`
- Stored DPM result fields available: `False`
- Active diameters [um]: `5.63, 28.14, 56.27, 112.54, 168.811, 348.88`
- Represented mass-flow total: `29.220000 kg/s`

## Limitations / Claim Class
- Claim class ceiling: `Debug only`
- This workflow is post-processing only. No setup rebuild, mesh replay, injection creation, or new DPM tracking was performed.
- The aggregate DPM interpretation for this run is intentionally partial because the user excluded 562 um, 844 um, 1631 um.
- Session warning: Could not discover phase-material mapping from the live state; using fallback phase-1=vapor, phase-2=liquid.
- DPM warning: No stored DPM fate/result summary fields were found in the loaded session; this pass is inventory-only for DPM.
