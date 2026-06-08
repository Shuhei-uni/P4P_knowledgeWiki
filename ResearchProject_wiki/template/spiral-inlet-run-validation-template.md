# Spiral-Inlet Run Validation Template

Use this template once per Fluent simulation/setup. Copy it into `ResearchProject_wiki/wiki/progress/experiments.md` or a run-specific note, then fill only the fields you have evidence for.

## Run Identity
- Run ID:
- Date:
- Operator:
- Fluent/ANSYS version:
- Case file:
- Data file:
- Geometry version:
- Mesh version:
- Setup report / notes:
- Purpose of this run:
- One variable changed from previous run:
- Previous run used for comparison:

## Decision Question
- Primary question this run must answer:
- Why this question matters:
- Stop condition / early-abort condition:
- Pass condition:
- Fail condition:
- Next branch if pass:
- Next branch if fail:

## Geometry And Mesh
- Geometry type: spiral inlet
- Steam outlet representation:
- Brine outlet representation:
- Inlet split / inlet zones:
- Cell count:
- Node count:
- Minimum orthogonal quality:
- Maximum skewness:
- Worst-cell location:
- Mesh notes:

## Physics And Solver Setup
- Solver:
- Time model: steady / transient
- Multiphase model:
- Primary phase:
- Secondary phase:
- Turbulence model:
- Energy equation: on / off
- Gravity:
- Pressure-velocity coupling:
- Pressure scheme:
- Momentum scheme:
- Volume fraction scheme:
- Other schemes:
- Under-relaxation factors:
- Initialization method:
- Patches used:
- Notes / deviations:

## Boundary Conditions

### Inlet
- Total inlet mass flow:
- Steam inlet mass flow:
- Liquid inlet mass flow:
- Inlet velocity:
- Phase split / dryness `x`:
- Inlet liquid volume fraction:
- Inlet steam volume fraction:
- Inlet pressure / total pressure:
- Inlet temperature / enthalpy:

### Steam Outlet
- Boundary type:
- Pressure:
- Backflow liquid volume fraction:
- Backflow steam volume fraction:
- Notes:

### Brine Outlet
- Boundary type:
- Pressure:
- Backflow liquid volume fraction:
- Backflow steam volume fraction:
- Notes:

### Walls / Other
- Wall roughness:
- Slip/no-slip:
- Other boundary notes:

## Validation Target Table

| Metric | Target / expected range | Source type | Source / note | Fluent output to compare | Result | Pass? |
|---|---:|---|---|---|---:|---|
| Inlet velocity | 30-40 m/s sanity band; ~42 m/s breakdown warning if comparable | literature sanity check | CFD_wiki separator design screening | inlet velocity |  |  |
| Pressure drop |  | analytical / partner / trend-only |  | inlet pressure - outlet pressure |  |  |
| Steam outlet liquid carryover |  | analytical / partner / trend-only |  | liquid mass flow through steam outlet |  |  |
| Implied separator efficiency | 99.5-99.99% sanity band if comparable | literature sanity check | CFD_wiki separator design screening | calculated from carryover |  |  |
| Brine outlet liquid flow |  | analytical / partner / trend-only |  | liquid mass flow through brine outlet |  |  |
| Mass imbalance | near-zero / chosen tolerance | numerical check | run-specific tolerance | flux report |  |  |

## Sanity Calculations

### Phase Split From Enthalpy
- `h`:
- `h_f`:
- `h_fg`:
- `x = (h - h_f) / h_fg`:
- `m_total`:
- `m_g = x * m_total`:
- `m_f = (1 - x) * m_total`:

### Separator Efficiency From Carryover
- Steam mass flow through steam outlet, `m_s`:
- Liquid/brine carryover through steam outlet, `m_b`:
- `eta_s = m_s / (m_s + m_b) * 100`:
- Liquid inlet mass flow, `m_w`:
- `eta_s = (m_w - m_b) / m_w * 100`:
- Interpretation:

### Pressure Drop Check
- Inlet pressure:
- Steam outlet pressure:
- Brine outlet pressure:
- CFD pressure drop:
- Analytical pressure drop available? yes / no
- `Ao`:
- `De`:
- `QVS`:
- `rho_v`:
- `u = QVS / Ao`:
- `NH = 16 * Ao / De^2`:
- `Delta P = (NH * u^2 * rho_v) / 2`:
- Interpretation:

## Convergence And Monitor History
- Iteration count / timestep count:
- Physical time simulated:
- Final continuity residual:
- Final x/y/z momentum residuals:
- Final turbulence residuals:
- Final volume fraction residual:
- Final energy residual, if used:
- Mass imbalance at final:
- Pressure-drop monitor trend: stable / drifting / oscillating
- Steam outlet liquid carryover trend: stable / declining / increasing / oscillating
- Brine outlet liquid flow trend: stable / declining / increasing / oscillating
- Convergence outcome: converged / partially converged / stalled / diverged

## Core Values To Record

| Quantity | Value | Units | Source / Fluent report | Notes |
|---|---:|---|---|---|
| Total inlet mass flow |  | kg/s |  |  |
| Steam inlet mass flow |  | kg/s |  |  |
| Liquid inlet mass flow |  | kg/s |  |  |
| Total outlet mass flow |  | kg/s |  |  |
| Steam outlet vapor mass flow |  | kg/s |  |  |
| Steam outlet liquid mass flow |  | kg/s |  | carryover |
| Brine outlet vapor mass flow |  | kg/s |  |  |
| Brine outlet liquid mass flow |  | kg/s |  |  |
| Net mass imbalance |  | kg/s or % |  |  |
| Inlet velocity |  | m/s |  |  |
| Pressure drop |  | Pa or bar |  |  |
| Implied separator efficiency |  | % | calculated |  |
| Minimum orthogonal quality |  | - | mesh check |  |
| Maximum skewness |  | - | mesh check |  |

## Required Figures

| Figure ID | Figure to create | File path / screenshot name | Done? | Key observation |
|---|---|---|---|---|
| F1 | Residual history |  |  |  |
| F2 | Phase-specific mass-flow history |  |  |  |
| F3 | Pressure contour on main vertical plane |  |  |  |
| F4 | Velocity magnitude contour on same plane |  |  |  |
| F5 | Velocity vectors or streamlines near spiral inlet |  |  |  |
| F6 | Velocity vectors or streamlines near steam outlet intake |  |  |  |
| F7 | Liquid volume fraction contour, whole separator |  |  |  |
| F8 | Liquid volume fraction close-up near steam outlet intake |  |  |  |
| F9 | Liquid volume fraction close-up near brine outlet |  |  |  |
| F10 | Steam outlet liquid carryover vs iteration/time |  |  |  |
| F11 | Brine outlet liquid flow vs iteration/time |  |  |  |
| F12 | Pressure-drop comparison against target/previous runs |  |  |  |
| F13 | Implied efficiency / steam quality comparison |  |  |  |

## Extra Figures By Run Type

### Split-Inlet Runs
- Inlet plane liquid volume fraction:
- Inlet plane velocity vectors:
- First-turn liquid distribution after spiral inlet:
- Outer-wall vs inner/core phase placement verification:

### Transient Runs
- Steam outlet liquid carryover vs physical time:
- Brine outlet liquid flow vs physical time:
- Average lower-pool liquid volume fraction vs physical time:
- Snapshot sequence at selected times:

### Mesh Sensitivity Runs
- Mesh level vs pressure drop:
- Mesh level vs steam outlet liquid carryover:
- Mesh level vs mass imbalance:
- Worst-cell location screenshot:
- Output-change summary:

### DPM Carryover Runs
- Droplet-size distribution / assumption:
- Particle tracks colored by trapped / escaped / incomplete:
- Escaped particle fraction:
- Trapped particle fraction:
- Incomplete particle fraction:
- Droplet-size sensitivity, if run:

## Result Interpretation
- What happened:
- Did it answer the decision question?
- Main evidence:
- Main uncertainty:
- Is the result physically plausible? yes / no / uncertain
- Is the result numerically trustworthy? yes / no / uncertain
- Is the result report-quality? yes / no / trend-only
- Recommended next action:

## Claim For Report
- Claim strength: validated / directionally supported / internally consistent / trend-only / unusable
- Sentence you can safely write:
- Caveat that must be included:

## Follow-Up
- Files to save:
- Wiki pages to update:
- Experiment log entry completed? yes / no
- Blockers updated? yes / no / not needed
- Validation target table updated? yes / no
