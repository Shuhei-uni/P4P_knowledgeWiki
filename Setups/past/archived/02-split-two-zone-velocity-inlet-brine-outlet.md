# Split Two-Phase Velocity-Inlet Setup Report (Full Geometry with Brine Outlet)

## Setup metadata

| Field | Value |
|---|---|
| Setup ID | `02` |
| Lifecycle | `archived` |
| Role | full-geometry diagnostic parent |
| Parent setup | [01](01-split-two-zone-massflow-inlet.md) |
| Evidence-use label | setup definition only |
| Outcome | superseded |
| Linked report | none |

## 1. Objective

Build a new trial setup based on the split two-phase inlet concept, but with:

- `Velocity Inlet` at both split inlet zones
- `Pressure Outlet` at steam outlet
- `Pressure Outlet` at brine outlet
- Full separator geometry retained (no cutoff at water level)

This report is for the first run path only: **no internal water initialization patch yet**.

## 2. Setup intent and scope

Compared to the earlier split-inlet report, this trial changes:

1. Inlet BC type: `Mass-Flow Inlet` -> `Velocity Inlet`
2. Domain scope: lower brine region is included
3. Outlet treatment: steam and brine are both active `Pressure Outlet` boundaries

Everything else should stay as close as possible to baseline unless required for stability.

## 3. Geometry and boundary layout

Use these boundary zones (rename to your actual zone names if different):

- `inlet_liquid_outer` (outer-wall side split inlet half)
- `inlet_steam_inner` (inner/core side split inlet half)
- `outlet_steam_top`
- `outlet_brine_bottom`
- separator walls

Critical check:

- confirm split inlet zones are physically correct (outer-wall side vs core side), not camera-left/right labels.

## 4. Baseline model stack to keep

For this first velocity-inlet test, keep:

- Solver: `Pressure-Based`
- Time: `Steady` (first run)
- Multiphase: `Mixture`
- Turbulence: `RNG k-epsilon`
- Energy: `Off` (isothermal path)
- Gravity: `On`
- Operating pressure: same convention as current baseline
- Pressure scheme: `PRESTO!`
- Pressure-velocity coupling: `SIMPLE`

## 5. Boundary conditions

### 5.1 Split velocity inlets

Both inlet zones use `Velocity Inlet`.

#### Inlet A: `inlet_liquid_outer`

- Type: `Velocity Inlet`
- Velocity direction: `Normal to Boundary`
- Phase condition target: liquid-dominant side
  - if phase-fraction field is available at inlet, set liquid fraction to `1.0`
  - steam fraction `0.0`
- Turbulence: start with same turbulence specification style as baseline

#### Inlet B: `inlet_steam_inner`

- Type: `Velocity Inlet`
- Velocity direction: `Normal to Boundary`
- Phase condition target: steam-dominant side
  - liquid fraction `0.0`
  - steam fraction `1.0`

### 5.2 Steam outlet

- Boundary: `outlet_steam_top`
- Type: `Pressure Outlet`
- Gauge pressure: baseline steam-outlet value
- Backflow phase fractions: set explicitly, steam-dominant

### 5.3 Brine outlet

- Boundary: `outlet_brine_bottom`
- Type: `Pressure Outlet`
- Gauge pressure: start with same plant reference pressure convention as other outlet
- Backflow phase fractions: set explicitly, liquid-dominant

Important:

- do not leave backflow phase fractions at inconsistent defaults; this is a common source of unphysical recirculation with two active outlets.

## 6. Velocity-inlet sizing method (what to enter)

Because BC type is now velocity-driven, compute inlet velocities from target phase mass flow and split-face area.

Use:

- `V_liquid = m_dot_liquid / (rho_liquid * A_liquid_inlet)`
- `V_steam = m_dot_steam / (rho_steam * A_steam_inlet)`

Where:

- `m_dot_liquid`, `m_dot_steam` are your target phase mass flows
- `rho_liquid`, `rho_steam` are model property values used in Fluent
- `A_liquid_inlet`, `A_steam_inlet` are actual split-face areas from your geometry

If you preserve earlier phase mass targets (`116.92 kg/s` liquid, `80.69 kg/s` steam), steam velocity may be very high due to low steam density. That is expected mathematically and must be checked for physical realism.

## 7. First-run recommendation (no internal water initialization yet)

For the first run of this new branch:

1. Keep initialization: `Hybrid Initialization`
2. Do not patch water pool initially
3. Run short convergence test first
4. Inspect whether lower region drains/recirculates physically with active brine outlet

This isolates the effect of changing inlet BC type before adding initialization complexity.

## 8. Monitors and acceptance checks

Track these from iteration 1:

1. Mass imbalance (global continuity)
2. Steam outlet mass flow
3. Brine outlet mass flow
4. Volume fraction contours near:
   - split inlet plane
   - lower vessel / brine outlet region
5. Velocity vectors near inlet and near brine outlet
6. Backflow warnings at both outlets

Minimum accept criteria for this trial:

- no runaway divergence
- bounded phase fractions
- no obviously nonphysical “spray everywhere” pattern at inlet
- outlet split trend is stable, not oscillating wildly in steady solve

## 9. Common failure modes specific to this setup

### Failure mode 1: steam jet dominates and shreds inlet interface

Cause:

- very high steam-side velocity from density contrast + equal-area split

Action:

- reduce steam-side target velocity (or revise target phase flow split)
- increase inlet transition length upstream if available

### Failure mode 2: nonphysical backflow loops from bottom outlet

Cause:

- poorly matched pressure-outlet/backflow settings with full lower domain present

Action:

- set explicit backflow phase fractions at both outlets
- verify outlet gauge pressure consistency and gravity orientation

### Failure mode 3: liquid accumulates unrealistically in lower vessel

Cause:

- brine outlet pressure/flow driving not sufficient

Action:

- re-check outlet pressure level and hydrostatic consistency
- evaluate whether transient run is needed for stable phase distribution

## 10. Next step after this first velocity-inlet run

Once this run is stable enough to interpret, create a second variant:

- same setup + **initialize water region inside separator** (patch/register method)

Do not combine too many changes before you get one stable reference result for this branch.

## 11. Execution checklist

| Done | Item | Target |
|---|---|---|
| ☐ | Use full geometry | Brine outlet region included |
| ☐ | Split inlet zones present | `inlet_liquid_outer` + `inlet_steam_inner` |
| ☐ | Inlet BC type | Velocity Inlet (both) |
| ☐ | Inlet directions | Normal to boundary |
| ☐ | Liquid-side phase state | liquid = 1.0 |
| ☐ | Steam-side phase state | liquid = 0.0 |
| ☐ | Steam outlet BC | Pressure Outlet |
| ☐ | Brine outlet BC | Pressure Outlet |
| ☐ | Outlet backflow fractions | Explicitly set |
| ☐ | Initialization | Hybrid (no patch yet) |
| ☐ | Short trial run completed | Residual and monitor trend checked |
