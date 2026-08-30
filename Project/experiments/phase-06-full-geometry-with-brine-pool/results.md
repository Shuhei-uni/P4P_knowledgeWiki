# Phase 06 — Full Geometry with Brine Pool — results

## Status

**Stage 01 has one completed fixed-pressure reference; no controlled outlet or
controlled brine-pool state has been established.** The reference is a bounded
repeatability/observable screen from the canonical F11 parent. Its paired
final case/data artifacts and nine inherited report histories were retained.

## Carried evidence from Stage 5

**Observed.** Under a fixed brine-outlet pressure, all completed Stage-5
practical-`k-epsilon` screens retained non-zero imbalance and continuing liquid
inventory movement. At `1.115 MPa`, RNG `k-epsilon` was less poor than
Standard and Realizable on the selected imbalance measures, but its exact
1,000-iteration restart did not arrest inventory movement. Raising the brine
outlet pressure to `1.1375 MPa` materially worsened the two tested closures.

**Inferred.** Those results rule out the tested fixed-pressure/
practical-`k-epsilon` directions as a credible steady reference route. They
do not isolate the cause as Mixture model form because the actual separator's
reported level-control feedback was not represented in those boundary
conditions.

## Current claim boundary

The project does not yet know whether a properly specified brine-pool control
boundary would yield a credible controlled operating point. It also does not
yet know whether the retained Mixture formulation can supply a valid pool-level
observable at the real instrument location. Both remain open Phase-06
questions.

## Stage-01 reference observation

**Observed.** Over native report coordinates 15,000–15,550, the lower-region
phase-2 liquid-mass inventories increased by 27.68 kg (`y≤0.10 m`) and
27.94 kg (`y≤0.30 m`). Total phase-2 liquid mass increased by 33.10 kg. The
last-100-sample mean derived liquid net rate was +21.42 kg/s, close to the
full-domain mass-imbalance mean (+21.42 kg/s); relative imbalance averaged
0.1079. The fixed-pressure reference is therefore accumulating and materially
unclosed within this short screen.

**Inferred, with strict limit.** The current lower-region liquid-mass reports
are responsive inventory proxies, but not a level signal. They show neither a
steady liquid inventory nor a controlled level condition. Scaled residual
history was unavailable after reconnecting, so this screen cannot establish
numerical convergence.

The detailed evidence and figures are in the
[Stage-01 results](stage-01-level-observable-and-outlet-response/results.md).
The matched outlet-vent `K=10` comparison is also complete. It worsened
liquid drainage, liquid inventory growth, and the retained imbalance measures,
so that uncalibrated resistance representation is not advanced as a
controlled-pool candidate. The result tests response-representation
capability, not a plant valve setting.

## Stage-02 data-gate outcome

**Observed.** The mesh has identifiable lower-region selection geometry and
both geometric- and liquid-volume report definitions, so a mesh-coordinate
volume/elevation map is technically feasible. The local project record does
not contain the real level instrument datum, target/band, outlet hardware,
downstream condition, or valve/controller relation required to turn that map
into a physical level-control model.

**Decision.** Return to the human for that phase-level physical boundary
rather than inventing it or filling Stages 3–5 with arbitrary resistance,
pressure, or turbulence variations. See the
[Stage-02 data-gate result](stage-02-level-mapping-and-control-data-gate/results.md).

## Missing information

The plant level setpoint, sensor location, outlet hardware/characteristic,
downstream condition, and any required controller behaviour are presently
missing from this record. No guessed controller or outlet relation is used.
