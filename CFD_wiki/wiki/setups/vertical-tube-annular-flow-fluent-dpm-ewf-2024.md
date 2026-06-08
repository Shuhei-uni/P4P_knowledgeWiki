# Setup: Vertical Upward Annular Flow (Fluent DPM + EWF, 2024)

## Purpose
Reproduce annular-flow entrainment/deposition behavior using the `mondal-2024` three-field approach.

## Source
- Primary: [mondal-sharma-2024-air-water-annular-flow-cfd](../sources/mondal-sharma-2024-air-water-annular-flow-cfd.md)

## Step-by-Step Build Order
1. Create 9.4 mm ID vertical tube with injection and annular zones.
2. Generate wall-refined multi-block hexahedral mesh.
3. Configure transient SST k-omega + DPM + EWF model.
4. Implement entrainment UDF correlations (start with Bertodano).
5. Sweep air velocity and liquid Reynolds conditions.
6. Compare outlet EF against reference experimental envelope.

## Key Inputs
- Tube diameter 0.0094 m (`Reported`) ([mondal-2024], p.2883).
- Annular section length about 210D (`Reported`) ([mondal-2024], p.2883).
- Operating window: superficial gas velocity about 24-95 m/s, liquid Reynolds 450/950/1400, pressures 1.2/4/6 bar (`Reported`) ([mondal-2024], Table 1).

## Models
- Turbulence: SST k-omega (`Reported`) ([mondal-2024], p.2883).
- Gas core + droplets: DPM (`Reported`) ([mondal-2024], p.2883-2884).
- Wall film: Eulerian Wall Film (`Reported`) ([mondal-2024], p.2883-2884).

## Missing Info
- Full timestep schedule.
- Full parcel-control values.
- Complete initialization field values.

## Assumptions
- Start with Bertodano correlation as default entrainment closure (`Assumed`, `Medium Risk`).
- Treat 210D as equilibrium-length baseline (`Assumed`, `Medium Risk`).

## Sensitivity Plan
1. Correlation swap (Bertodano/Okawa/Hewitt-Govan).
2. Droplet-size and parcel-count sensitivity.
3. Mesh/time-step sensitivity at outlet.

## Common Failure Modes
- EF underprediction at low gas velocity.
- Non-equilibrium outlet profiles.
- Over-stiff source terms causing unstable film transport.

## Quick Diagnostics
- Compare deposition and entrainment rates near outlet.
- Track film-thickness decay with axial length.
- Confirm EF trend monotonicity with gas velocity.
