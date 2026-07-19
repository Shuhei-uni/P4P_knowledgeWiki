# Live Fluent Post-Processing Report: TwoPhaseInletV2(Purnanto)-25-05000

## Source Case/Data
- Server id: `3`
- Case file: `C:\Users\syok443\Documents\TwoPhaseInletV2(Purnanto)\TwoPhaseInletV2(Purnanto)-25-05000.cas.h5`
- Data file: `C:\Users\syok443\Documents\TwoPhaseInletV2(Purnanto)\TwoPhaseInletV2(Purnanto)-25-05000.dat.h5`
- Load mode: `already-loaded-session`

## Boundary/Model Sanity
- Fluent version: `Ansys Fluent 2024 R2`

## Carrier Flux Metrics
- Liquid inlet mass flow: `unavailable kg/s`
- Vapor inlet mass flow: `unavailable kg/s`
- Steam-outlet liquid mass flow: `unavailable kg/s`
- Steam-outlet vapor mass flow: `unavailable kg/s`
- Phase-flux efficiency `eta_phase`: `unavailable`
- Steam-outlet dryness `x_out`: `unavailable`
- Mass imbalance: `unavailable kg/s`
- Mass-imbalance note: Mass imbalance could not be assessed from the available flux report.

## DPM Inventory
- DPM enabled: `False`
- Active injections: `0`
- Stored DPM result fields available: `False`
- Active diameters [um]: `none found`
- Represented mass-flow total: `unavailable kg/s`

## Limitations / Claim Class
- Claim class ceiling: `Debug only`
- This workflow is post-processing only. No setup rebuild, mesh replay, injection creation, or new DPM tracking was performed.
- The aggregate DPM interpretation for this run is intentionally partial because the user excluded 562 um, 844 um, 1631 um.
- Session warning: Could not discover phase-material mapping from the live state; using fallback phase-1=vapor, phase-2=liquid.
- Session warning: Could not identify expected zone for role: liquid_inlet
- Session warning: Could not identify expected zone for role: steam_inlet
- Session warning: Could not identify expected zone for role: steam_outlet
- DPM warning: Discrete phase branch unavailable: InactiveObjectError: '<session>.setup.models' is currently inactive.
