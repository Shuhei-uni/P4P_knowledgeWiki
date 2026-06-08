# Source: Geothermal Steam-Water Separators Design Overview (2014)

## Source Metadata
- Source ID: `zarrouk-purnanto-2014`
- File: `raw/Zarrouk and Purnanto 2014.pdf`
- Authors: Sadiq J. Zarrouk, Munggang H. Purnanto
- Venue: Geothermics 53 (2014) 236-254
- Type: Invited review

## One-Page Summary
This review synthesizes separator technology used in geothermal plants globally, emphasizing vertical BOC cyclone and horizontal separators, with practical design guidance for sizing, pressure selection, efficiency, pressure-drop control, and plant integration ([zarrouk-purnanto-2014], p.236-238, p.252-253).

The paper also summarizes early Wairakei test evidence and discusses CFD as a complementary tool for visualizing internal flow fields and improving separator optimization ([zarrouk-purnanto-2014], p.248-249, p.252-253).

## A) Study Scope
- Objective: provide state-of-practice design overview for geothermal steam-water separators ([zarrouk-purnanto-2014], p.236-237).
- Scope: separator types, global deployment, sizing equations, efficiency interpretation, location/design trade-offs, and CFD insights ([zarrouk-purnanto-2014], p.238-253).
- Outputs: design rules and comparison logic rather than one single numerical CFD case.

## B) Physics and Models
- Core physical basis: centrifugal separation (vertical cyclone) and gravity-dominant separation (horizontal) ([zarrouk-purnanto-2014], p.238-241).
- Governing-equation stack for one specific CFD run is not provided in this review (`Missing`).
- CFD discussion reports velocity/pressure/steam-quality profiling as useful design diagnostics ([zarrouk-purnanto-2014], p.248-249, p.252).

## C) Material and Operating Conditions
- Typical separator inlet velocity guidance: approximately 30-40 m/s for high efficiency and to remain below breakdown thresholds in common BOC designs ([zarrouk-purnanto-2014], p.253).
- Reported practical separation efficiencies for industry-scale designs are typically around 99.5-99.99% calculated/effective range ([zarrouk-purnanto-2014], p.253).

## D) Boundary and Initial Conditions
- Not a single solver case study; therefore CFD BC/IC tables are not explicitly defined (`Missing`).
- Practical operating boundary logic is discussed via pressure-drop minimization, steam quality, and separator location relative to plant and drains ([zarrouk-purnanto-2014], p.251-252).

## E) Mesh and Numerics
- No explicit mesh topology/count/scheme set is provided in this review (`Missing`).
- Reported CFD contribution is qualitative/diagnostic, not a full reproducibility package.

## F) Validation and Results
- Review conclusion: both vertical and horizontal designs can achieve high separator performance when properly designed; BOC with spiral inlet is described as dominant in modern practice ([zarrouk-purnanto-2014], p.253).
- Highlights operational issue: centralised separators near powerhouses may increase risk of mineral/moisture carryover impacts if drainage/scrubbing architecture is insufficient ([zarrouk-purnanto-2014], p.251-252).

## G) Reproducibility Risk
### Missing Parameter List
- No complete CFD numerical setup.
- No unified validation dataset released for all cited designs.

### Assumptions Used in This Wiki
- Treat this source as design-policy and synthesis evidence, not as a standalone CFD reconstruction recipe (`Assumed`, `Low Risk`).

### Confidence Rating
`High` for separator design context and cross-field deployment patterns; `Low` for direct CFD rerun reproducibility.

### Minimal Sensitivity Tests
1. Validate local separator size/velocity selection against modern plant-specific mass-flow envelopes.
2. Pair empirical sizing with CFD confirmation before final hardware freezing.

## H) Cross-Paper Linkage (Mandatory)
- Closest related pages:
  - [purnanto-2013-cfd-geothermal-separator](purnanto-2013-cfd-geothermal-separator.md)
  - [rivas-cruz-2015-geothermal-separator-state-of-art-review](rivas-cruz-2015-geothermal-separator-state-of-art-review.md)
- Relations:
  - `supports`: supports BOC separator practical dominance and Lazalde-Crabtree lineage.
  - `extends`: extends single-case CFD evidence into global design decision context.
- Reuse recommendation:
  - Use as top-level design decision map before detailed CFD/plant-specific optimization.
