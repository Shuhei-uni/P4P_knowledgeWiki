# Source: Design and Evaluation of Geothermal Steam Separators State-of-Art Review (2015)

## Source Metadata
- Source ID: `rivas-cruz-2015`
- File: `raw/1032231.pdf`
- Authors: Fernando Rivas-Cruz, Alfonso Garcia-Gutierrez, Juan I. Martinez-Estrella, Angel A. Ortiz-Bolanos
- Venue: GRC Transactions Vol. 39 (2015)
- Type: Review paper

## One-Page Summary
This review compiles historical methods and software workflows used for geothermal separator and dryer design/evaluation, with special focus on Webre-type separators and Lazalde-Crabtree methodology adoption in operational practice ([rivas-cruz-2015], p.881-883).

The paper is mainly a methodology survey (not a new CFD or experiment dataset) and positions CFD tools as promising design-support methods when linked with established empirical frameworks ([rivas-cruz-2015], p.884-886).

## A) Study Scope
- Objective: summarize design/evaluation methods and software support for geothermal separator performance assessment, especially for Cerro Prieto context ([rivas-cruz-2015], p.881-882).
- Scope: literature matrix across Bangma, Lazalde-Crabtree, and later CFD-assisted works ([rivas-cruz-2015], p.882-885).
- Outputs: comparative method inventory and conclusions on dominant design approach.

## B) Physics and Models
- Emphasized physical mechanism: centrifugal separation in Webre/BOC style separators ([rivas-cruz-2015], p.881-883).
- Dominant design model in reviewed literature: Lazalde-Crabtree empirical framework ([rivas-cruz-2015], p.885-886).
- CFD models are discussed as complementary tools, often benchmarked against empirical design curves ([rivas-cruz-2015], p.884-885).

## C) Material and Operating Conditions
- Review cites typical inlet-velocity and steam-quality design envelopes from prior work; no new independent operating dataset is produced (`Reported-as-review`).
- Focus is on engineering practice transfer rather than new property tables.

## D) Boundary and Initial Conditions
- No new standalone CFD case in this paper; BC/IC are inherited through cited works (`Missing`).

## E) Mesh and Numerics
- No new mesh/numerics package is introduced by this review (`Missing`).
- CFD references are described at conceptual workflow level only.

## F) Validation and Results
- Main conclusion: Webre-type separators and Lazalde-Crabtree methodology remain the most common practical design/evaluation route in reviewed geothermal applications ([rivas-cruz-2015], p.885-886).
- Steam quality targets above approximately 99.95% are repeatedly associated with accepted operation in cited methods ([rivas-cruz-2015], p.883, p.886).

## G) Reproducibility Risk
### Missing Parameter List
- No original CFD or experimental run data.
- No explicit solver-control values.

### Assumptions Used in This Wiki
- Treat this as a method lineage source, not a primary numerics source (`Assumed`, `Low Risk`).

### Confidence Rating
`High` for historical-method mapping; `Low` for direct numerical reconstruction.

### Minimal Sensitivity Tests
1. Cross-check cited legacy design limits against current field chemistry and flow transients.
2. Validate any imported empirical constants via modern CFD and plant data.

## H) Cross-Paper Linkage (Mandatory)
- Closest related pages:
  - [zarrouk-purnanto-2014-geothermal-separator-design-overview](zarrouk-purnanto-2014-geothermal-separator-design-overview.md)
  - [purnanto-2013-cfd-geothermal-separator](purnanto-2013-cfd-geothermal-separator.md)
- Relations:
  - `supports`: supports continued use of Lazalde-Crabtree/Bangma-rooted design logic.
  - `reuses`: reuses the same separator design family evidence base.
- Reuse recommendation:
  - Use for method selection and legacy compatibility checks before detailed simulation.
