---
name: pool-patch-volume
description: "Apply an explicitly authorized pool initial condition through MCP: verify a mesh-local cell selection and liquid phase, patch it, measure geometric and phase volume, and optionally report scoped pressure."
---

# Pool Patch Volume

A pool patch is an initial condition, not a brine-outlet backflow condition or
proof of an eventual operating level. Follow
[MCP integration](../fluent-live-inspection/mcp-integration.md).

## Establish scope before mutation

Require the requested or approved setup's pool bounds, liquid phase, patch intent
and session ownership. Resolve exact case/mesh identity independently of the
server alias. Patching/resetting remains human-controlled where the phase says so;
this skill cannot turn an autonomous recovery suggestion into patch permission.

Keep the operation pool-only. Do not change boundary conditions, run iterations,
advance time or save case/data unless separately authorized. Initialization or
model/phase creation must also be explicitly included in the request/setup;
otherwise return the missing prerequisite rather than destroying a developed
field or choosing physics just to make the patch legal.

## 1. Discover current state through MCP

Use `find_api`/`get_help` for candidate paths, then `describe_path`, `get_state`
and named-object tools to inspect models, phases, fluid zones and cell registers.
Use `list_fields` for actual field names. Record version, case/mesh identity,
coordinate units, gravity direction, phase/domain mapping and relevant bounds.

A register's existence does not prove its geometry or membership. Read back its
type, limits, inside/outside flag and intended zones. Reuse it only when these
match; create a new name or obtain authorized replacement for a conflicting one.
Existing setup scripts are historical implementation evidence, not the live
path authority and not a reason to run combined boundary/setup code.

## 2. Create or reuse the exact selection

Derive the unconstrained bounds from the current mesh and use the supplied pool
cutoff in the verified vertical direction. Confirm that the selection intersects
the intended fluid cells, not solids or unrelated pipes. Do not borrow bounds
from another mesh or assume the vertical direction is Y.

Discover the current register template and command arguments, then validate and
run the smallest creation/update snippet through MCP. Reacquire and independently
read back the selection. Obtain the marked-cell count from Fluent or a verified
cell-data reduction; a bounding-box calculation is not a selected-cell count.

## 3. Patch the intended liquid phase

Initialize only when explicitly authorized and required. Ground the patch command
and phase/variable arguments against the live API; names such as `phase-2` or
`mp` are not portable assumptions. Validate/run the patch and reacquire state.
A successful call or marked count does not prove every cell received the intended
phase fraction. Verify through actual phase-volume evidence below.

## 4. Measure two different volumes

Measure and report:

- `V_geom`: geometric volume of the selected cells;
- `V_liq`: integral of the selected liquid volume fraction over those cells;
- marked-cell count and `fill_fraction = V_liq / V_geom`.

Use MCP-grounded Settings report/integral commands through validated `run_code`.
Prove that each result refers to the actual register and domain, with finite
values and units. Register support differs by API/version. If unsupported,
use a reviewed field-data/offline reduction only when its identical membership
can be established; record the missing capability and exact method. Never
substitute the whole fluid-zone volume for the selected region.

Where appropriate, measure complementary vapor volume and check whether
`V_liq + V_vapor` agrees with `V_geom`. Report a material discrepancy and its
uncertainty rather than replacing actual liquid volume with geometric volume.
A missing/zero/whole-domain-looking result is unverified, not successful filling.

## 5. Optional pressure information

Pressure is supplementary unless explicitly requested. Use actual density,
gravity, elevation reference and operating pressure. A hydrostatic estimate
`p(y) ≈ p_ref + rho * g * (y_ref - y)` assumes a mostly static liquid and omits
swirl, acceleration, losses and vapor dynamics; label it as an approximation.

For measured pressure, ground the field and scoped reduction through MCP.
Distinguish gauge/absolute pressure and volume/area weighting. A mixed register
average is not liquid-only pressure; phase-conditioned statistics need verified
selection. Boundary loads require face/surface reductions, not cell averages.
Fresh initialization/patch pressure is only an initialization diagnostic.
Operational or high-consequence conclusions need independent numerical/physical
validation; this skill gathers evidence, not equipment-rating approval.

## Handoff and failure

Return register name/type/bounds/units/inside flag, intended zones and marked
count; phase/domain/patch variable/value; `V_geom`, `V_liq`, fill fraction and
optional complementary volume; pressure definition/reference and method when
used; whether initialization/model changes occurred; and any readback mismatch.
State iterations/time advancement and boundary changes explicitly (normally
none). Record save paths only when saving was authorized; otherwise state that
the live state is unsaved. Persistence claims require approved paired save/reopen
verification. Leave the Fluent session running and the source pair untouched.

If prerequisites, identity, bounds or phase mapping cannot be established, block
before patching. Reacquire after dependency changes; use semantic manual research
when MCP cannot resolve meaning. Do not enable a model, initialize, guess a deep
path or bypass MCP as an automatic repair.
