# P7-E5-PSINK-G025 results

## Answer at a glance

Observed: the frozen hexahedral register for the separator-purnanto cells with
0 <= y <= 0.10 m was created and read back. Fluent 2025 R2 exposed phase-2
source terms as a uniform fluid-zone source list with value/none controls, but
the live tree exposed no cell-register selector or region-specific binding for
the required liquid-only mass and associated momentum sources. No solve was
started for gain G=0.25.

The official Fluent User's Guide describes volumetric mass and momentum sources
as being applied to a cell zone and states that cells requiring a source must
be placed in a separate zone. The official UDF guidance provides the available
route for a cell-dependent DEFINE_SOURCE implementation. That evidence supports
the diagnosis but does not authorize a mesh-zone split or a new UDF for this
project packet.

**Evidence status:** capability probe complete; executable E5 setup blocked
before solve. **Queue state:** BLOCKED_VERIFIED.

## Core visual evidence

No F1--F4 figures are applicable: E5 did not pass capability proof and has no
valid residual, inventory, routing, controller, or balance history. The
register state and source-tree readback are the core evidence for this packet.

## Capability evidence and numerical adequacy

- Observed: the frozen register geometry and cell-selection state were read
  back before cleanup.
- Observed: phase-2 mass-source terms were exposed only at the fluid-zone
  source-list level; no region selector was exposed.
- Observed: the required associated liquid momentum source and zero direct
  vapor source could not be bound to the frozen register.
- Research result: the generic Fluent mechanism is zone-scoped for GUI source
  terms; a spatially varying source requires a UDF or a separate cell zone.
- Not run: smoke, checkpoints, final horizon, report histories, residual
  histories, controller updates, and phase balances.

## Interpretation and blocker

- Observed: this is an API/model-capability block, not a physical failure of
  the phase-selective sink concept.
- Inferred: applying a uniform source to the entire fluid zone would violate
  the approved frozen-region contract and would not be a valid fallback.
- Competing route: a centroid-conditional compiled UDF could in principle
  implement the y-range and liquid-only source/momentum coupling, but that is
  a new implementation route requiring explicit human approval under CONTEXT.md.
- Claim boundary: no statement about E5 mechanism performance is supported.

## Decision and checklist

| Phase Loop item | Status | Evidence |
| --- | --- | --- |
| Frozen register created and read back | PASS | capability manifest |
| Region-specific liquid-only source binding | BLOCKED | live Settings tree |
| Associated momentum / zero vapor source proof | NOT RUN | target state unavailable |
| Solve, histories, and core figures | NOT RUN | capability gate failed |
| Planned analysis and interpretation | NOT APPLICABLE | no solve |

**Decision:** keep E5 at the human-owned capability boundary. Do not substitute a
whole-zone source, move the region, split the mesh, or invent a UDF inside this
packet.

## Run and artifact details

- Capability manifest: PyAnsys/output/phase07_treatment_screen/P7-E5-PSINK-server1-20260908T150000Z-manifest.json
- Local reusable guidance: CFD_wiki/wiki/synthesis/fluent-separator-efficiency-methods.md
- Official Fluent cell-zone source guidance: https://ansyshelp.ansys.com/public/Views/Secured/corp/v251/en/flu_ug/flu_ug_bcs_sec_cell_zones.html
- Official Fluent UDF source-hook guidance: https://ansyshelp.ansys.com/public/Views/Secured/corp/v251/en/flu_udf/flu_udf_ActivatingModelSpecificUDFs.html

