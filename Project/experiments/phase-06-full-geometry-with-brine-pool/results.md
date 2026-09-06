# Phase 06 — Full Geometry with Brine Pool — results

## Status

**Phase 06 is not closed under the current scientific-phase-loop gates.**
The short screens and 10,000-iteration long calculation provide useful bounded
numerical evidence, but the mandatory lifecycle is reopened at
`DISCOVERY_DESIGN`: only three valid short discovery cases are identified, the
long-run job is terminally `BLOCKED`, and the residual history and named final
pair promised by its setup are absent. The human has authorized a bounded
simple-surrogate route, not a physical plant-control claim. See
[phase-state.yaml](phase-state.yaml).

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

## Stage-06 long-horizon hypothesis outcome and gate review

**Observed.** `P6-S6-H-server2-20260831T004750Z` completed 10,000 incremental
iterations from F11 (plus a 50-iteration smoke). Its full retained report
histories show the lower-region numerical proxy finishing at 284.83 kg versus
the deliberately non-plant 200 kg target. The final-1,000-iteration proxy
mean was 284.45 kg with +0.00249 kg/iteration slope; the derived phase-2 net
liquid rate averaged +16.10 kg/s and the relative imbalance averaged 0.08115.
The bounded brine-pressure surrogate reached 1.115 MPa gauge and stayed at
that lower bound for 98/100 endpoints. A paired chunk-100 endpoint checkpoint
was independently verified readable.

**Numerical limitation.** The post-run PyFluent residual monitor did not
populate, so no residual-convergence claim is made and the named final pair
was not written after the completed calculation. The retained report histories
and verified checkpoint do support the bounded statement of persistent
numerical accumulation; they do not make a physical validation claim.

**Closure outcome under the current gates: RETURN TO HUMAN / PHASE-PLANNER.**
The calculation weakens H6 and supports a bounded diagnostic statement about
the tested numerical surrogate. It does not cure the skipped discovery gates,
the unresolved Stage-02 human lock, or the promised residual/final-artifact
gaps. Any useful next step requires the missing plant information or explicit
human authorization of a bounded surrogate discovery class and autonomy
envelope. The lifecycle must then restart at the first unpassed gate.

## Scientific-phase-loop completion audit

| Loop requirement | Current evidence | Status |
|---|---|---|
| Orient from Phase-05 Stage-05 and retained history | Phase-05 Stage-05 was reconciled as setup-only; fixed-pressure inheritance and its limitations are preserved above and in the Stage-06 setup. | Complete |
| Collision check before new compute | Stage-06 rejected redundant pressure/resistance cases, deferred the failed mass-flow family, and recorded the long post-saturation test as a justified partial repeat. | Complete |
| Live fleet and bold-probe consideration | Two-server fleet was inspected. No in-boundary nonredundant bold case survived the collision/scope check; the later server-3 ownership gate prevented use of that lane. | Complete with explicit no-valid-probe/ownership exception |
| Short discovery evidence | Stage-01 fixed-pressure/vent screens and Stage-03 five-chunk numerical-surrogate discovery are retained and analysed. | **BLOCK** — three cases, below the required six |
| Focused hypothesis test | Stage-04 sharpened H6; Stage-06 reached the planned 10,000 incremental iterations. | **BLOCK** — predecessor gates did not pass |
| Durable run identity and endpoint | Full report histories and a verified chunk-100 checkpoint pair exist. The canonical job is `BLOCKED`; the named final pair and residual capture are absent. | **BLOCK** |
| Planned numerical analysis | F1–F3 and exact late-window reductions were produced. Required F4 is unavailable and cannot be waived retrospectively. | **BLOCK** |
| Interpretation, assumptions, and closure | The bounded interpretation remains useful, but normal autonomous closure prerequisites are not satisfied. | **BLOCK** — restart at discovery design |
