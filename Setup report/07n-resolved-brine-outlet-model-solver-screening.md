# Resolved Brine-Outlet Model and Solver Screening

## Purpose and classification

Setup `07n` is the carrier-only sensitivity family for the separator
with the lower liquid pool, resolved brine pipe and brine outlet included in
the computational domain. It is intended to determine which Fluent
constant-level representation, multiphase formulation, pressure-velocity
solver and turbulence closure can produce a bounded, storage-consistent
drainage solution before a new mesh convergence study begins.

The separator is assumed to operate with a controlled, approximately constant
water level. That pool is a required steam seal over the brine outlet, not
merely an initialization convenience. The geometry-derived `y=0 m` pool used
by setup 07l currently reaches approximately to the inferred brine-pipe crown;
it is an initial lower bracket, not yet proof of adequate submergence. Results
remain `Diagnostic / unresolved` with respect to the plant until the required
submergence and downstream valve/pressure response are established.

DPM must retain zero injection objects and remain off. EWF and every numerical
mass or momentum sink remain off throughout this carrier-screening family.

## 2026-08-28 calibrated pressure-step long hold

An independently cold-loaded server-2 branch tested whether the short-window
0.05%-feed balance could persist after one evidence-calibrated brine-pressure
change. The checksum-bound clean step-90 pair was the sole parent. The branch
held `0.05846 kg/s` liquid and `0.040345 kg/s` vapor feed at
`1,122,263.621237 Pa` through additional step 10, then applied one
`+23.218830875 Pa` change and held `1,122,286.840068 Pa` through step 70.
The timestep remained `1.28e-4 s`, the inner cap remained 100, and explicit
VOF/PISO/PRESTO/Geo-Reconstruct/WFGC/RNG k-epsilon, DPM zero/off, EWF off and
all source-off states were preserved.

The branch completed all 70 steps and passed every numerical, clock,
VOF/pressure/velocity, liquid-seal and cross-phase-routing hard gate. Final
continuity was `7.93757e-4`, the preceding value was `7.90715e-4`, Courant was
`0.00764008`, the brine face stayed liquid VF `1.0`, vapor through brine and
liquid through steam stayed zero, and the reported liquid inventory stayed
`3877.468071 kg`. However, drainage continued increasing after the earlier
36-step balance window. At step 70, liquid/vapor/total net imbalance was
`-0.01155471`, `+0.0000760171` and `-0.011478693 kg/s`. The maximum absolute
liquid/vapor/total imbalance over steps 61-70 was therefore
`0.01155471/0.0000760171/0.011478693 kg/s`, failing the required
`+/-0.005 kg/s` sustained gate.

Classification is **diagnostic / unresolved calibrated pressure-step
0.05%-feed long hold**. The step-70 checkpoint and every intermediate endpoint
remain `eligible_parent:false`, non-resumable and unsuitable for an unchanged
repeat. The generated nested campaign-member summary retained stale
`accepted ... zero-feed` wording; the campaign/member final classifications
and the non-overwriting
`longhold_nonacceptance_disposition_20260828.json` control interpretation.
This evidence shows that low residuals and a perfect liquid steam seal do not
guarantee sustained hydraulic balance. It is not level-control proof and the
pressure remains CFD-derived rather than plant-valid.

The next bounded one-factor diagnostic, when a full execution window is
available, should cold-load the original clean step-90 pair and add only one
second small held pressure action after the established short balance window,
with all flow, timestep, numerics and physics unchanged. It must be described
as mass-flow-balance control, not water-level control, until a sufficiently
precise interface/inventory observable and plant target level exist.

## 2026-08-26 sustained 0.05%-feed and pressure-controller outcome

The accepted ten-step 0.05%-feed result did **not** remain mass-balanced over a
longer fixed-pressure hold. From an independent cold load of the checksum-bound
server-2 step-90 pair, the same `0.05846 kg/s` liquid feed,
`0.040345 kg/s` vapor feed, `1,122,263.621237 Pa` brine pressure,
`dt=1.28e-4 s` and 100 inner iterations reached 36 fully monitored steps.
Continuity remained low (`7.91749e-4`) and Courant was `0.00452474`, the brine
face remained liquid VF `1.0`, cross-phase leakage remained zero and the
reported phase inventories were unchanged. Nevertheless, liquid drainage rose
to `0.10864564 kg/s`, giving liquid and total net imbalances of
`-0.050185643` and `-0.049855477 kg/s`. The controller stopped the branch; the
following solve was interrupted and is uncredited. This is
`diagnostic / unresolved`, not an accepted long hold.

Two pressure-feedback sensitivities then cold-loaded the same clean step-90
parent. Both delayed feedback until additional step 10 and changed no flow,
timestep, solver, model or source setting:

- gain `0.25` completed 50 steps and crossed the balance point, but overshot.
  Final continuity was `7.73340e-4` and Courant `0.00567281`, while the final
  five-step maximum liquid/total imbalance was
  `0.019462106` / `0.019334063 kg/s`. The steam seal and routing gates passed,
  but the sustained balance gate failed.
- gain `0.05` reached 47 fully monitored steps before the next Fluent RPC lost
  its stream (`recvmsg: Can't assign requested address`). At the last credited
  state, continuity was `7.72592e-4`, Courant `0.00542563`, brine liquid VF was
  `1.0`, cross-phase leakage was zero and inventory was unchanged. Liquid and
  total imbalances were still `-0.038632126` and `-0.038377965 kg/s`; the
  final-five maximum liquid imbalance was `0.03967104 kg/s`. The interrupted
  step is uncredited and the stopped field is not resumable.

Therefore the pressure outlet can drain a submerged pool cleanly, but the
current instantaneous pressure-feedback law does not yet provide a stable
constant-level/mass-balance model. Every endpoint remains
`eligible_parent:false`. No writer is active. A bounded unauthenticated check
on 2026-08-27 found server-2 TCP reachable, but Fluent health/ranks were not
re-authenticated after the stopped run. The next useful controller test should
address the observed response lag (for example, a settle-and-update or
filtered/PI level controller) from the clean step-90 parent rather than resume
either adaptive endpoint.

## 2026-08-25 accepted 0.05%-feed carrier-pathline video

A post-processing-only export cold-loaded the accepted server-2 step-100 pair
at `t=0.00639 s` and verified its case/data SHA-256 values
`d0247380...bd52` / `38447356...e97b`, Fluent 2024 R2, 16 ranks, pressure,
0.05% inlet rates, clock, phase identities, DPM zero/off, EWF off and source-off
state. It performed zero initialization, zero physical steps, zero DPM updates
and zero case/data writes.

The accepted movie contains 12 progressively integrated pathline views from
the exact `liquidinlet` release, using 827 massless seeds in the frozen endpoint
VOF carrier-velocity field. It is a pathway reveal, not physical-time playback
and not a droplet/DPM trajectory. Fluent again substituted `wall-fluid` when
`steaminlet` was requested; that optional scene was rejected. Fluent also
exposed `auto-range` / `clip-to-range`, not the contour-style
`auto-range-off` child, so the retained pathline frames use the exact per-frame
automatic velocity scale recorded in the manifest.

This visualization cannot be used to infer phase-specific carryover: VOF has a
shared carrier velocity, whereas the accepted phase-flux reports independently
show zero liquid through the steam outlet. The six-second H.264 MP4, raw PNGs
and manifest are under
`../PyAnsys/output/split_inlet_resolved_brine_outlet_20260813/brine620k_07n_s2_p1122264_0p05feed_step100_carrier_pathline_video_attempt3_20260825/`.

## 2026-08-25 server-2 open-drain result

Every member independently cold-loaded the checksum-bound clean server-2
step-90 pair. Fluent read back 2024 R2, exactly 16 ranks, explicit VOF/PISO,
the unchanged 98,473-cell pool, DPM zero/off, EWF off and no sources. Live
inspection found only phasic mass-flow-outlet rates, not one writable bulk
mixture rate, so setup 07n-b remains unresolved and phase routing was not
prescribed.

At 0.05% common feed (0.05846 kg/s liquid, 0.040345 kg/s vapor), dt=128 us,
100 inner iterations and brine pressure 1,122,263.621237 Pa, ten guarded steps
ended at step 100 / t=0.00639 s. Liquid drainage was 0.058460099 kg/s, steam
discharge 0.040344992 kg/s and total net imbalance -9.11e-8 kg/s. Continuity
tail was 0.00201686/0.00173276, Courant 0.00248721, VOF stayed [0,1], the
brine face stayed liquid VF 1.0 and cross-phase leakage was zero. This is an
accepted diagnostic proving resolved drainage, an intact steam seal and closed
phase/total balance at very low feed. The CFD-interpolated pressure is not a
plant boundary and the saved pair is not a production parent.

At the same pressure, 0.05625% completed ten steps with final continuity
0.00190599 and liquid net +0.00195577 kg/s. The 0.0625% and 0.075% members
stopped after their first step at continuity 1.05293 and 1.26332; both are
terminal. The current startup limit is therefore bracketed between 0.05625%
and 0.0625%; full flow remains unproved.

The next one-factor comparison, if authorized in a later execution window, is
the same 0.05625% feed cold-loaded from step 90 with pressure retargeted to
approximately 1,122,261.011 Pa. That value is an interpolation for diagnostic
balance only; it must not be recorded as plant pressure.

## Reset after review of setups 07l and 07m

Setups `07l` and `07m` are retained as forensic numerical evidence, not as an
authoritative physical modelling recipe. Setup 07l proved only that a closed,
patched pool stayed bounded for ten very small physical steps. It did not prove
that `y=0 m` is the operating level or that the field was dynamically relaxed
on a separator time scale. Setup 07m proved that an opened pressure boundary
responded in a finite way over a small-flow micro-startup. Its
`1,122,090.400 Pa` setting remains a CFD-derived rest diagnostic, not a known
downstream condition, level-control law or steam-seal model.

Consequently, 07n will not continue the setup-07m fraction ladder as its main
lineage. It will reconstruct its time-zero state from the accepted mesh and
read-back physics, patch the selected liquid level explicitly, and qualify the
level/outlet representation over a physically interpretable time window. The
setup-07l case may be used as a convenient settings carrier only after a fresh
readback; its data field is not assumed to be the correct 07n initial field.

## Correction to the older setup-09 interpretation

The statement in setup `09` that VOF was not the preferred production model
was written for the earlier truncated separator model, where bottom drainage
was deliberately outside the CFD domain and the principal question was mist
carryover. It does not decide the current resolved-drainage problem.

Purnanto et al. modelled the separator body with a Mixture/DPM-style workflow,
but explicitly excluded flow into the brine pipe and assumed a fixed water
level immediately above it. Pointon et al. likewise excluded the downstream
brine exit piping. Those papers support cyclone carrier-flow and droplet
tracking choices, but they do not provide a validated boundary condition for
the newly resolved liquid pool and drain.

Zarrouk and Purnanto's design review adds the missing plant interpretation:
the brine outlet is normally connected to a water drum to control separator
level, form a seal against steam loss and damp pressure/flow surges. It also
identifies a U-bend brine-pipe loop seal as an operating design. This means
that a geometrically liquid-filled leg plus level control is the physical
target; a phase value entered at an outlet is not a substitute.

Vani et al.'s ANSYS-led gravity-separator CFD study is an analogy rather than
a geothermal validation, but it provides a relevant implementation pattern:
when liquid-outlet pressure is not measured, use a feedback controller that
adjusts outlet pressure from interface-level error. This supports testing
pressure feedback in 07n rather than inventing one fixed downstream pressure.

For the present problem:

- VOF is relevant because the lower pool/free-surface position and drainage
  are part of the requested solution.
- A constant-level model must remove liquid at the same long-time rate that it
  enters while keeping the brine outlet submerged. A closed wall or a fixed
  initial pool alone cannot satisfy that balance.
- Mixture remains a useful lower-cost sensitivity for dispersed steam-water
  flow, but it is not an interface-resolving level model.
- Eulerian or Eulerian Multi-Fluid VOF is a higher-cost sensitivity when
  separate phase velocities and a resolved interface are both important.
- DPM and EWF answer later carryover and wall-film questions; neither closes
  the current bulk liquid inventory by itself.

## Evidence base

Repository sources:

- `purnanto-2013`: steady pressure-based Mixture interpretation, RNG
  `k-epsilon`, SIMPLE/PRESTO and later DPM logic; brine-pipe flow excluded and
  the water level prescribed.
- `pointon-2009`: RNG `k-epsilon` plus DPM for geothermal cyclone design;
  downstream exit piping to the brine drum excluded.
- `chen-2025`: experiment-backed transient RSM-DPM cyclone workflow; useful
  for later turbulence and carryover sensitivity, not direct geothermal
  drainage boundary values.
- `mondal-2024` and `skoog-2020`: DPM plus EWF three-field workflows for wall
  film/deposition/entrainment; useful only after carrier qualification and
  with calibrated closures.

Official Fluent guidance:

- [Multiphase approaches](https://ansyshelp.ansys.com/public/Views/Secured/corp/v242/en/flu_th/flu_th_sec_mphase_approaches.html)
  identifies VOF for tracked immiscible interfaces, Mixture for lower-cost
  interpenetrating/dispersed flows including cyclones, and Eulerian for
  separate phase momentum equations.
- [Multiphase setup](https://ansyshelp.ansys.com/public/Views/Secured/corp/v242/en/flu_ug/flu_ug_sec_multiphase_setup.html)
  recommends double precision and states that transient treatment is needed
  when the final state depends on the initial phase field or the phases do not
  have distinct inflow boundaries.
- [Swirling-flow guidance](https://ansyshelp.ansys.com/public/views/secured/corp/v251/en/flu_ug/flu_ug_uns_sec_models_swirl.html)
  supports RNG/realizable `k-epsilon` for moderate swirl, RSM for high swirl,
  PRESTO for steep swirl-pressure gradients and sufficient core refinement.
- [Multiphase solution strategies](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/flu_ug_sec_multiphase_solution.html)
  makes PISO/SIMPLE/SIMPLEC/Coupled available for VOF/Mixture and Phase-Coupled
  SIMPLE or Coupled available for Eulerian flows.
- [Boundary-condition guidance](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/flu_ug_bcs_sec_bound_cond.html)
  prefers a pressure outlet over outflow where recirculation or a non-developed
  exit is plausible. A porous jump can represent a known Darcy/inertial loss,
  but it needs a suitable internal face and defensible coefficients.
- [PyFluent field-data API](https://fluent.docs.pyansys.com/version/stable/api/services/field_data.html)
  documents `get_mesh(cell_zone)` as the supported node/element mesh route.
  That is the exact route attempted here; the Fluent 2024 R2 endpoint returned
  gRPC `UNIMPLEMENTED`, so the fallback cannot be represented as an equivalent
  successful volume-cell readback.

Analogy-level gas-liquid cyclone evidence also commonly uses both overflow and
underflow as pressure outlets with Mixture or Eulerian-Eulerian formulations
and RSM turbulence. These studies support testing the formulation, but their
zero-gauge outlet values cannot be imported into a submerged geothermal drain.

## Geometry and hydraulic implication

The current brine outlet area is `0.19936247 m2`, equivalent to a circular
diameter of about `0.504 m`. At the reference liquid feed `116.92 kg/s` and
liquid density about `881.21 kg/m3`, the mean full-flow outlet velocity is only
about `0.666 m/s` and one velocity head is about `195 Pa`.

The accepted hydrostatic-rest case observed approximately `2090.4 Pa` between
the lower face and steam outlet. This is roughly eleven full-flow velocity
heads. Therefore pipe, valve and control losses can be of the same order as
the available hydrostatic driving head. Omitting that resistance can materially
over-drive drainage even when the pressure outlet itself is numerically valid.
This is a diagnostic scaling observation, not a fitted loss coefficient.

## Controlled screening order

### Stage 0 — geometry, level and time-scale definition

Before another flow solve, determine from the resolved mesh rather than the
equivalent-area estimate:

1. the brine-pipe crown and outlet-leg vertical extent;
2. the local cell heights around the crown and intended free surface;
3. the liquid volume/inventory below each candidate level;
4. whether the current geometry contains enough liquid-leg or water-drum
   volume to represent a persistent steam seal; and
5. a characteristic gravitational, residence and inventory-response time so
   that a few microseconds are not mistaken for a relaxed separator state.

The first pool levels will be defined as resolved distances above the actual
pipe crown, preferably using the operating level if it can be recovered. If no
plant level is available, crown plus two and four local vertical cell heights
will be explicit numerical sensitivities, not claimed plant values.

### Stage 1 — constant-level carrier configurations

The primary physical target is an inventory-controlled water pool whose upper
surface remains close to a stated target and whose brine outlet remains liquid
sealed. Test distinct implementations from a freshly reconstructed 07n
time-zero state:

| Branch | Configuration | Purpose |
|---|---|---|
| `07n-a` | closed-drain hydrostatic pool qualification | establish a dynamically relaxed, mesh-resolved pool for each candidate submergence without inheriting the 07l data field as truth |
| `07n-b` | ideal constant-level flow balance | prescribe total brine-outlet flow equal to the liquid feed while allowing VOF to determine the outgoing phase composition; use only when the outlet face is demonstrably liquid-filled |
| `07n-c` | level-feedback outlet-pressure control | adjust brine-outlet pressure between physical steps from measured interface/inventory error with bounded pressure and slew rate |
| `07n-d` | explicit water-drum or loop-seal geometry | test a physical liquid seal if the current short outlet leg cannot keep the brine boundary isolated from steam |

The failed setup-07k result does not reject `07n-b`: setup 07k abruptly applied
the full `116.92 kg/s` outlet command to a quiescent, non-hydrostatic startup
field. The new branch starts from accepted hydrostatic rest and ramps inlet and
outlet together at the same small fractions. It is a new controlled test and
must not resume setup 07k.

There is also a boundary-definition distinction. Setup 07k prescribed
`phase-1 = 0` and `phase-2 = 116.92 kg/s`; that fixes the desired outgoing
phase route and is not the 07n-b test. Setup 07n-b requires one total
mixture/bulk outlet-rate command while the adjacent VOF field determines the
phase composition. Fluent 2024 R2 must expose and read back that interpretation
after boundary-type conversion. If its live mass-flow-outlet object exposes
only phasic rates, 07n-b is not implementable as written and must stop rather
than reuse the 07k command.

Neither a pressure outlet nor a mass-flow outlet is made liquid-only by setting
a backflow volume fraction. For outward flow, Fluent obtains the phase
composition from the adjacent VOF field. A mass-flow outlet pumps the specified
total mixture flow and scales boundary velocity; it does not form a
phase-selective membrane. Therefore the required proof is that the resolved
outlet leg is filled with liquid and remains separated from the steam region.

For `07n-c`, derive the inventory setpoint from the accepted 07n-a target level,
not automatically from setup 07l. The setup-07l value `3774.370486 kg` remains
the recorded inventory of its `y<=0 m` patch and is only a comparison datum. A
suitable diagnostic pressure-controller form is

```text
p_brine,next = clamp(p_brine + Kp*(level_target-level_measured)
                     + Ki*integral(level_target-level_measured),
                     lower_pressure, upper_pressure)
```

with anti-windup and a per-step pressure slew limit. With the stated
`target - measured` error, a low level should increase brine backpressure; the
previous minus sign was therefore reversed. The sign and response must still
be verified by bounded positive and negative pressure perturbations before
closed-loop use. `Kp`, `Ki`,
limits and slew rate are numerical/control sensitivities, not plant
calibration. The controller must not delete liquid volumetrically; it changes
only the resolved brine-outlet boundary. A separate flow-command controller
may be retained as an ideal-control comparison.

All constant-level branches must prove that the pool covers the brine-pipe
crown by a resolved margin and that vapor flow through the brine outlet becomes
negligible without being prescribed. A stable total mass balance without this
emergent steam-seal check is insufficient.

### Stage 2 — pressure-velocity and volume-fraction solver sensitivities

Only after a clean baseline exists, change one numerical item at a time over a
matched physical-time window:

| Branch | One change | Purpose |
|---|---|---|
| `07n-e` | PISO -> plain Coupled while explicit VOF is retained | test stronger pressure/momentum coupling without changing the VOF formulation |
| `07n-f` | explicit -> implicit VOF, retain transient marching | test robustness versus added interface diffusion |
| `07n-g` | first-order -> second-order physical time after startup | test time-discretization dependence |

Fluent 2024 R2 does not support the separate **Coupled with Volume Fractions**
option with explicit VOF. That option may be inspected only after an implicit-
VOF baseline has been established. It is not a legal one-factor replacement
for PISO in the explicit-VOF 07n-a lineage.

Residual magnitudes are not compared alone across algorithms. The decision is
based on the same phase fluxes, inventory/storage closure, pressure, velocity,
VOF and clock window.

### Stage 3 — multiphase-model sensitivities

Each physics branch must be reconstructed from the same clean mesh and
hydrostatic initial-condition definition, written to a new time-zero case/data
pair and fully read back. No failed setup-07h/07i/07j/07k/server-2 field is a
parent.

The old server-2 steady Mixture field is terminal and prohibited from resume.
A new Mixture branch must be freshly prepared and must first pass the same
zero-feed hydrostatic/opening checks as the VOF lineage.

### Stage 4 — turbulence sensitivity

Retain RNG `k-epsilon` as the cost-effective baseline. Once one drainage
formulation passes, compare RSM from the same accepted carrier state and over a
matched window. SST `k-omega` may be retained as an optional near-wall
sensitivity, but it is not substituted merely to improve residual appearance.
RSM is promoted only if swirl, pressure distribution and phase routing change
materially and the extra equations remain converged.

### Stage 5 — physical downstream/control closure

The constant-level assumption is sufficient for a controlled CFD baseline even
when the real valve curve is unavailable: prescribe or control the liquid
outflow so pool inventory remains fixed, and classify the result accordingly.
The preferred progression toward plant fidelity is:

1. a sufficiently submerged liquid-filled outlet leg, with phase composition
   determined by the resolved VOF field;
2. a paired inlet/total-outlet-flow condition representing ideal level control;
3. a bounded inventory-feedback outlet controller representing active level
   control;
4. a measured downstream static-pressure/head condition at a sufficiently
   extended brine pipe;
5. an explicit pipe/valve resistance, using resolved geometry or a calibrated
   porous loss representation;
6. a measured level-controller law if operating level and valve response are
   available.

The existing pressure bracket remains useful for sensitivity only. A prescribed
mass-flow outlet is a rate-forced diagnostic and the failed setup-07k field is
not resumed. Outflow is not the first choice because the present short outlet
may have strong gradients or recirculation.

## Common gates

Every branch must preserve and report:

- exact Fluent version, 16-rank roster, client ownership and parent hashes;
- zero DPM injection objects, DPM off, EWF off and no source/sink hooks;
- finite pressure, velocity, volume fraction, turbulence and Courant fields;
- total, vapor and liquid flux at both inlets and both outlets;
- phase routing: vapor mainly to steam outlet and liquid mainly to brine outlet;
- steam seal: the pool remains above the brine-pipe crown and brine-outlet
  vapor carry-under is negligible and non-growing as an emergent result, not a
  prescribed outgoing phase condition;
- liquid and vapor inventories at every physical step;
- controlled-level drift relative to the accepted 07n-a target level and its
  independently calculated liquid inventory;
- transient storage closure `dM_q/dt - sum(mdot_q,boundaries)`;
- two consecutive end-step continuity values no greater than `0.01` for a
  numerical promotion, followed by the stricter physical-window drift gates;
- a matched `dt/2` window before time-step independence is claimed.

No branch proceeds to a mesh ladder until its residual envelope, phase balance,
inventory/level behaviour and principal physical monitors are stable. Model
form, turbulence and downstream-boundary uncertainty must be screened before
mesh uncertainty, otherwise the mesh study would refine an unresolved problem.

## Immediate execution decision

### Stage-0 execution on 22 August 2026

The local process/PID audit found no Fluent/PyFluent/controller writer. Both
configured endpoints were `SERVING`, Fluent 2024 R2 and exactly 16 ranks, with
no other connected client. Server 1 contained the accepted mesh, setup-07l
step-10 case/data and forensic setup-07m 1% pair. Server 2 contained only the
mesh; none of those case/data parents was present, so it is ineligible for the
07n lineage.

The stale zero-step setup-07m 1% hold was preserved without altering its
original `running` manifest. Its correction record credits zero physical steps
and prohibits resume.

Mesh-only attempt 5 produced the accepted surface-geometry diagnostic:

- SHA-256 `0d75a86e53bc020aeefa4b13ef8616413a862b15646355d90d8037d1be888394`;
- polygon-integrated brine area `0.1993624690 m2`, matching the accepted area
  to `4.98e-9` relative difference;
- resolved crown `y=-0.0015579789 m`, invert `y=-0.5067311525 m` and opening
  height `0.5051731736 m`;
- median vertical size of the two boundary faces touching the crown
  `0.0089871744 m`;
- mesh-derived cylindrical-wall extent approximately `1.95976 m`, retained as
  an inferred outlet-leg length rather than a CAD dimension.

The public PyFluent 0.39 `get_mesh(cell_zone)` RPC returned gRPC
`UNIMPLEMENTED` against Fluent 2024 R2. A temporary cell-register volume
surface created successfully but was not exposed as a field-data surface, and
the initialized UTL `volumes=[...]` report path failed with unbound
`pm/volumes`. Every temporary register was deleted. The first initialized UTL
manifest incorrectly labelled the attempt accepted; a separate checksum-bound
correction record downgrades it to `diagnostic / unresolved` without modifying
the original evidence.

The supported initialization/patch/integral route then measured two explicit
numerical brackets, each from a case-only load followed by fresh Hybrid
Initialization. No data file was read and no physical step or case/data write
occurred:

| Candidate | Target `y` (m) | Marked cells | Liquid volume (m3) | Liquid inventory (kg) |
|---|---:|---:|---:|---:|
| crown + 2 crown-face heights | `0.0164163698` | `98,473` | `4.40015912` | `3877.46807` |
| crown + 4 crown-face heights | `0.0343907186` | `99,647` | `4.43625099` | `3909.27263` |

Both candidates retained zero DPM injection objects, interaction/tracking off,
all mixture/phase source containers off and the brine face closed as a wall.
They are accepted geometry/inventory diagnostics only. Their elevations use an
exact boundary-face-height proxy because the adjacent volume-cell heights are
still unavailable. No 07n-a relaxation field was therefore promoted or run.
No Fluent controller/writer remains active. The server-1 session still holds
the second patched candidate in memory as an **unsaved diagnostic field**;
that field is explicitly ineligible as a parent. The next writer must
cold-load the accepted settings carrier before doing any further setup or
calculation. A checksum-bound companion JSON preserves the transcript cell
counts and this live-state disposition without altering the run manifest.

Evidence is under
`PyAnsys/output/split_inlet_resolved_brine_outlet_20260813/brine620k_07n_stage0_geometry_v1/`.

1. Audit the actual mesh crown, outlet leg and local vertical resolution.
   Crown, opening and surface resolution are accepted; adjacent volume-cell
   height remains unresolved in Fluent 2024 R2/PyFluent 0.39.
2. Resolve the volume-cell-height gate, then reconstruct a fresh VOF time-zero pool at mesh-resolved candidate levels
   and qualify closed-drain hydrostatic relaxation over a meaningful physical
   window.
3. Open the submerged outlet and run a bounded pressure perturbation to prove
   the sign and magnitude of its hydraulic response without adopting 07m's
   pressure as a plant value.
4. Run the ideal balanced-flow constant-level branch at low feed, requiring
   the outgoing phase composition to remain emergently liquid.
5. Implement bounded level-feedback pressure control and compare its level,
   mass balance and steam-seal behaviour with the ideal flow command.
6. If the current outlet leg loses its seal, stop numerical tuning and test an
   explicit water-drum or U-bend loop-seal geometry.
7. Perform Coupled, implicit-VOF and time-step one-factor comparisons only on
   the accepted constant-level configuration.
8. Prepare fresh Eulerian/Mixture sensitivity branches only after the VOF
   baseline is understood; Mixture is not eligible to prove the sharp pool.

This order tests solvers and models without confusing numerical convergence
with the still-missing downstream plant hydraulics.

## Bounded lower-face-proxy execution on 22 August 2026

The unresolved adjacent-volume-cell-height gate was not waived or silently
promoted. A separately labelled lower-candidate pilot was nevertheless run as
`diagnostic / unresolved` implementation evidence using the exact accepted
boundary-face proxy at `y=0.016416369820944965 m`. It cannot qualify a physical
water level or conforming 07n-a pool.

The authoritative pilot was
`brine620k_07n_a_closeddrain_lower_faceproxy_pilot_attempt4_20260822`.
Server 1 passed raw TCP preflight, exclusive-client, Fluent-2024-R2 and exact
16-rank gates. The setup-07l step-10 case was checksum-bound and loaded without
its data. After complete settings readback, fresh Hybrid Initialization marked
exactly `98,473` cells and patched the expected `4.400159116 m3` /
`3877.468071 kg` liquid. EWF was proved off through
`(rpgetvar 'sg-wallfilm?) = #f`; DPM had
zero injection objects with interaction/tracking off; all phase/mixture source
containers were disabled; both inlets were zero; the brine face remained a
wall; PISO/PRESTO/Geo-Reconstruct/WFGC and explicit VOF were retained.

The pilot saved and hashed separate time-zero, step-1, step-5 and step-10
case/data pairs. Ten one-step RPCs at `dt=1e-6 s` and 20 inner iterations all
passed. The one-factor follow-up
`brine620k_07n_a_closeddrain_lower_faceproxy_dt2em6_extension_attempt1_20260822`
verified the step-10 parent hashes, changed only `dt` to `2e-6 s`, and saved
hashed additional-step-1, 5 and 10 pairs while completing ten more one-step
RPCs.

| Evidence | Pilot step 10 | `dt=2e-6 s` extension end |
|---|---:|---:|
| Cumulative physical step | `10` | `20` |
| Cumulative physical time | `10 us` | `30 us` |
| End-step continuity | `2.74398e-6` | `4.64048e-6` |
| Global Courant | `7.73149e-9` | `4.81584e-8` |
| Liquid inventory (kg) | `3877.468071` | `3877.468071` |
| Brine-face liquid VF min/max | `1.0 / 1.0` | `1.0 / 1.0` |
| Pressure min/max (MPa) | `1.1199992 / 1.1329161` | `1.1199992 / 1.1329162` |
| Maximum velocity (m/s) | `6.63818e-5` | `1.64972e-4` |
| Liquid steam-outlet flow (kg/s) | `0` | `0` |
| Gate failures | `0` | `0` |

The last two continuity values passed the `0.01` numerical envelope in both
runs. Domain VOF remained `[0,1]`, phase storage closure remained at numerical
round-off, the brine wall remained fully liquid covered and steam-outlet vapor
flow was round-off scale. These are useful startup and automation results.
They do **not** establish dynamic relaxation: `30 us` is only about `0.07%` of
the local `~0.0428 s` gravity scale.

Pilot attempt 3 is preserved as a post-solve monitoring failure. Fluent
physically completed one finite step (`continuity=0.0015476`, `Co=1e-16`,
clock `1 us`) before a storage-key mismatch prevented controller credit and a
step-1 checkpoint. Its original manifest was not modified; a checksum-bound
companion record marks the uncheckpointed field ineligible and prohibits
resume. Attempts 1 and 2 remain zero-step API-discovery failures. None is a
parent.

Evidence manifests and histories are under:

```text
PyAnsys/output/split_inlet_resolved_brine_outlet_20260813/
  brine620k_07n_a_closeddrain_lower_faceproxy_pilot_attempt4_20260822/
  brine620k_07n_a_closeddrain_lower_faceproxy_dt2em6_extension_attempt1_20260822/
```

The extension endpoint is eligible only for another conservative same-proxy
diagnostic dt step. No general 07n parent is promoted. The next physical action
remains: resolve adjacent volume-cell spacing, reconstruct the resulting
mesh-defined level, then relax it over a meaningful physical window before any
outlet opening, constant-level control, solver/model comparison or mesh study.
No controller or writer was active after the runs.

## Exact whole-cell pool selection and meaningful-time relaxation on 22 August 2026

The adjacent-cell vertex-height API remains unavailable, but that limitation
no longer prevents a reproducible whole-cell initialization. A checksum-bound
threshold scan was run from the setup-07l step-10 **case only**, with one fresh
Hybrid Initialization, zero physical steps and no case/data output. Forty-four
reversible patch/reset queries isolated the complete interval over which the
same `98,473` volume cells are selected:

- lower transition bracket:
  `[0.0164023302091, 0.0164023303045] m`;
- upper transition bracket:
  `[0.0165144008650, 0.0165144009603] m`;
- invariant inner interval width: `0.0001120705605 m`;
- centered selection threshold: `y=0.0164583655847 m`;
- resulting liquid volume/inventory:
  `4.400159116 m3` / `3877.468071 kg`.

Attempts 1 and 3 could not observe the marked-cell count through the first
console path; attempt 2 hid the post-load rank rows by redirecting the live
stream too early. All three remain non-overwriting zero-step
`diagnostic / unresolved` evidence. Attempt 4 changed the observation path,
reproved Fluent 2024 R2, exclusive ownership, `n0..n15`, the carrier checksum,
DPM/EWF/source-off state and the exact count, and is classified
`accepted mesh-selection diagnostic`. Its manifest SHA-256 is
`d3e1b4b559420feb1c19c0054d21a075b27300324189c59976b01f0ccdbaced5`.
The centered threshold is a CFD-defined selection level, not a measured plant
level and not a direct cell-vertex measurement.

The fresh mesh-selected run
`brine620k_07n_a_closeddrain_meshselected_startup_attempt1_20260822` then
cold-loaded the same settings carrier without data, Hybrid Initialized,
patched that centered threshold, saved and cold-reloaded a unique time-zero
pair, and repeated the complete settings and field gates. The explicit-VOF,
PISO, PRESTO, Geo-Reconstruct, WFGC, RNG k-epsilon, zero-feed, closed-brine
contract was unchanged; DPM had zero injections and remained off, EWF was
false, and every source/sink remained disabled.

The physical timestep was increased only by guarded factors of two through
`256 us`, then held fixed. Every step used 20 inner iterations and one physical
step per RPC. Each listed endpoint passed residual, Courant, VOF, pressure,
velocity, inventory, storage, clock, DPM, EWF and settings gates:

| Cumulative step | Cumulative time (s) | dt (s) | End continuity | Global Co | Maximum velocity (m/s) |
|---:|---:|---:|---:|---:|---:|
| 10 | `0.00001` | `1e-6` | `2.74398e-6` | `7.73149e-9` | `6.63818e-5` |
| 20 | `0.00003` | `2e-6` | `4.64048e-6` | `4.81584e-8` | `1.64972e-4` |
| 30 | `0.00007` | `4e-6` | `8.98346e-6` | `2.27224e-7` | `3.53560e-4` |
| 40 | `0.00015` | `8e-6` | `1.78209e-5` | `9.78157e-7` | `7.25974e-4` |
| 50 | `0.00031` | `1.6e-5` | `3.54594e-5` | `4.05099e-6` | `0.00146767` |
| 60 | `0.00063` | `3.2e-5` | `7.11562e-5` | `1.64770e-5` | `0.00294986` |
| 70 | `0.00127` | `6.4e-5` | `1.42945e-4` | `6.63939e-5` | `0.00591996` |
| 80 | `0.00255` | `1.28e-4` | `3.14609e-4` | `2.65624e-4` | `0.0118860` |
| 90 | `0.00511` | `2.56e-4` | `8.09494e-4` | `0.00104946` | `0.0242263` |
| 140 | `0.01791` | `2.56e-4` | `7.52714e-4` | `0.00400200` | `0.0539114` |
| 240 | `0.04351` | `2.56e-4` | `5.49791e-4` | `0.00890710` | `0.0946598` |

At step 240 the brine-face liquid VF remained exactly `1.0`, liquid inventory
remained `3877.468071 kg`, liquid storage closure was `0 kg/s`, liquid flow at
the steam outlet was zero, and pressure remained bounded at
`1.1199993-1.1329369 MPa`. The last two continuity values passed the `0.01`
numerical gate. The endpoint case/data hashes are
`f4ab4217...32a9fc3` / `97775992...932e6eb`.

This is the first bounded mesh-selected trajectory to reach approximately one
local gravity time (`~0.0428 s`), but it is not yet dynamically stationary.
Across the final 20 steps, maximum velocity rose `5.02%`, domain-average
velocity `10.65%`, vorticity `10.49%` and Courant `12.43%`, while continuity
fell `1.23%`. Therefore the endpoint was eligible only for a continued
same-`dt`, closed-drain diagnostic. The second 100-step hold
`brine620k_07n_a_closeddrain_meshselected_dt256em6_hold100_stage2_attempt1_20260822`
completed cleanly at step 340 / `0.06911 s`: continuity `4.15884e-4`, Courant
`0.0108716`, maximum velocity `0.171626 m/s`, inventory unchanged, brine-face
liquid VF `1.0`, storage closure `0 kg/s` and zero gate failures. Its endpoint
case/data hashes are `ad3b4abf...833609` / `e2605174...303195`.

Stage 2 also remained physically non-stationary. Across its final 20 steps,
maximum velocity rose `10.52%`, domain-average velocity `5.83%` and vorticity
`5.43%`; continuity was effectively flat (`+0.018%`) and Courant fell `1.57%`.
A third through eighth unchanged-`dt` continuation then extended the same
closed-pool field to step 940 / `0.22271 s`. Every completed stage retained
the exact zero-feed, brine-wall, explicit-VOF/PISO contract and passed the
residual, Courant, VOF, pressure, velocity, inventory, storage, steam-seal,
clock, DPM, EWF, source and settings gates:

| Stage endpoint | Physical time (s) | End continuity | Global Co | Domain-average velocity (m/s) | Domain-average vorticity (1/s) | Maximum velocity (m/s) |
|---:|---:|---:|---:|---:|---:|---:|
| 340 | `0.06911` | `4.15884e-4` | `0.0108716` | not retained in this summary | not retained in this summary | `0.171626` |
| 440 | `0.09471` | `4.15701e-4` | `0.0106579` | `0.00313986` | `0.0285355` | `0.216434` |
| 540 | `0.12031` | `3.77846e-4` | `0.0104779` | `0.00360821` | `0.0320651` | `0.212749` |
| 640 | `0.14591` | `3.88322e-4` | `0.0121609` | `0.00388335` | `0.0340609` | `0.195527` |
| 740 | `0.17151` | `3.65929e-4` | `0.0108453` | `0.00395394` | `0.0346611` | `0.185780` |
| 840 | `0.19711` | `3.88318e-4` | `0.0124395` | `0.00383331` | `0.0341789` | `0.146011` |
| 940 | `0.22271` | `3.67467e-4` | `0.0125058` | `0.00357883` | `0.0331321` | `0.144127` |

The first stage-5 attempt is preserved separately as
`brine620k_07n_a_closeddrain_meshselected_dt256em6_hold100_stage5_attempt1_20260822`.
It has status `stopped_postsolve_monitoring`: 27 steps through cumulative step
567 have complete monitor rows, while step 568 was physically solved but its
post-solve monitoring was interrupted. Its intermediate checkpoints remain
ineligible and its in-memory field was not resumed. The non-overwriting
replacement
`brine620k_07n_a_closeddrain_meshselected_dt256em6_hold100_stage5_attempt2_20260823`
cold-loaded the verified step-540 parent and completed the full 100-step block
to step 640.

By stage 8 the local maximum had stopped the earlier monotonic rise, and the
final 20-step regressions were `+0.021%` for Courant, `-1.540%` for
domain-average velocity, `-0.637%` for vorticity and `-0.912%` for maximum
velocity. The corresponding final-50 values were `+1.764%`, `-3.761%`,
`-1.644%` and `-1.646%`. Pressure was effectively flat, liquid inventory was
exactly `3877.468071 kg`, the brine-face liquid VF stayed exactly `1.0`, and
liquid steam-outlet flow stayed zero. This is a bounded, nearly quiescent pool
with a preserved steam seal, but the relative bulk-motion drift remains above
the strict `1%` stationarity target. The step-940 case/data pair is bound by
SHA-256 `03383ac0...6c7c9` / `a5963dfa...0772a` and is eligible only for
closed-pool diagnostic comparisons.

### Matched physical-time `dt/2` and `dt/4` result on 23 August 2026

Three checksum-bound branches cold-loaded that same step-940 case/data pair and
advanced the identical `0.00512 s` physical window:

- baseline: 20 steps at `dt=2.56e-4 s`, ending at step 960;
- half step: 40 steps at `dt=1.28e-4 s`, ending at step 980;
- quarter step: 80 steps at `dt=6.4e-5 s`, ending at step 1020.

All ended at `t=0.22783 s`, passed every hard gate, kept liquid inventory and
phase inventories exactly equal, retained brine-face liquid VF `1.0`, zero
liquid steam-outlet flow and flat pressure, and saved separately hashed
case/data pairs. The endpoint comparison was:

| Endpoint metric | `dt=2.56e-4 s` | `dt=1.28e-4 s` | `dt=6.4e-5 s` | Quarter vs half |
|---|---:|---:|---:|---:|
| End continuity | `3.81644e-4` | `2.45702e-4` | `1.99940e-4` | `-18.62%` |
| Global Courant | `0.0123977` | `0.00618867` | `0.00309052` | `-50.06%` |
| Domain-average velocity (m/s) | `0.00351760` | `0.00348574` | `0.00343598` | `-1.427%` |
| Domain-average vorticity (1/s) | `0.0329238` | `0.0326138` | `0.0321559` | `-1.404%` |
| Maximum velocity (m/s) | `0.142191` | `0.131766` | `0.121895` | `-7.491%` |
| Brine-wall mean pressure (Pa) | `1122423.2` | `1122420.5` | `1122416.0` | `-4.5 Pa` / `-0.000401%` |
| Liquid inventory (kg) | `3877.468071` | `3877.468071` | `3877.468071` | `0` |

Across all 20 matched physical-time samples, the mean absolute difference was
`0.506%` for domain-average velocity and `0.526%` for vorticity, but `5.173%`
for maximum velocity; the maximum matched-sample differences were `0.906%`,
`0.941%` and `7.332%`, respectively. A known turbulent-viscosity limiter
remained confined to one of `620,431` cells and did not couple to a hard-gate
failure; later localization excludes it as the maximum-velocity cell.

Across the 40 half-versus-quarter matched samples, the mean absolute
differences increased to `0.817%`, `0.810%` and `5.935%`; their maxima were
`1.427%`, `1.404%` and `7.491%`. Base-versus-quarter endpoint differences were
`2.320%`, `2.332%` and `14.274%`. The discrepancy therefore did not contract
under a second halving, despite continuity improving and Courant scaling as
expected.

A fourth checksum-bound branch then repeated the 20-step baseline at fixed
`dt=2.56e-4 s` with only the inner-iteration cap changed from 20 to 100. It
also ended at step 960 / `t=0.22783 s` and passed every hard gate. Relative to
the 20-inner baseline, endpoint average velocity, vorticity and maximum
velocity changed only `-0.00000853%`, `+0.00000607%` and `+0.00000703%`.
Across all 20 matched samples, their maximum differences remained below
`0.000009%`. Endpoint continuity improved from `3.81644e-4` to `1.14616e-6`
(`-99.70%`) without changing the physical field. This is an accepted numerical
diagnostic: 20 inner iterations are field-independent over this window, and
incomplete inner convergence does not explain the timestep sensitivity.

Post-processing-only attempt 4 then fetched aligned `SV_CENTROID`, `SV_U`,
`SV_V` and `SV_W` arrays for all `620,431` cells from each matched endpoint.
The base, half and quarter branches place the maximum on the exact same array
index `382511` and centroid `(0.809789, 0.0420206, 0.651966) m`. This cell is
`0.0255622 m` above the selected whole-cell pool threshold and is interfacial:
its liquid VF is `0.134811`, `0.134823` and `0.134831`, respectively. Its
velocity magnitude falls monotonically `0.142191 -> 0.131766 -> 0.121895 m/s`.
The top-20 velocity sets overlap by 18 cells between base/half, 16 between
half/quarter and 14 across all three, so the sensitivity belongs to a small
repeatable interfacial region rather than a migrating or isolated cell.

The maximum-cell pressure changes by less than `0.000041%`, and its turbulent
viscosity is only `0.20-0.24%` of the domain maximum. The previously reported
one-cell turbulent-viscosity limiter is therefore not the localized velocity
maximum and is not a credible explanation for this timestep trend. The two
earlier localization attempts are preserved as zero-iteration stopped
diagnostics: Fluent 2024 R2 rejected the cell-register `pm/volumes` path and
the surface API correctly rejected `fluid` as a surface. Attempt 4 used the
supported native solution-variable cell arrays, performed zero iterations,
zero initializations and zero case/data writes, and is an accepted diagnostic.

The final explicit-VOF discriminator cold-loaded the same step-940 parent and
advanced 160 steps at `dt=3.2e-5 s`, again ending at `t=0.22783 s`. Every hard
gate passed; continuity was `1.47877e-4`, Courant `0.00154527`, inventory was
exact, brine-face liquid VF remained `1.0`, and liquid steam-outlet flow stayed
zero. The final case/data hashes are `b9a7e269...67f79` /
`4d8ba586...17c4f`.

Quarter-to-eighth endpoint differences were `-2.150%` for average velocity,
`-1.936%` for vorticity and `-7.283%` for maximum velocity. Across 80 matched
samples their mean absolute differences were `1.284%`, `1.217%` and `6.092%`;
their maxima were `2.150%`, `1.936%` and `7.283%`. Continuity improved
`26.04%` and Courant halved exactly, but the field differences did not
contract into an asymptotic sequence. Explicit-VOF timestep halving is stopped.

The result is therefore `diagnostic / unresolved`, not time-step independent.
Bulk pressure, inventory, VOF, steam seal and volume-averaged motion are nearly
bounded over this window, but the bulk and localized velocity measures do not
show an asymptotic timestep-independent sequence. None of the four endpoints
is promoted to outlet opening, level control,
outlet/control work or the mesh ladder. The successor implicit-VOF probe and
matched solver screen are reported below. No Fluent writer/controller remained
active after the explicit timestep comparison.

### Implicit-VOF and pressure-velocity solver screen on 23 August 2026

The zero-step formulation probe was completed before any implicit physical
marching. Attempts 1-7 are preserved as non-overwriting `stopped_zero_step`
diagnostics covering the sandboxed TCP path, incorrect Settings-API paths,
settings-export transport and exact explicit-restore checks. None initialized,
iterated or wrote case/data. Attempts 8 and 9 independently passed and are
accepted zero-step diagnostics; their manifest SHA-256 values are
`d5a74e5c...fb345` and `ab0e8491...ab42d`.

The accepted readback proves that Fluent 2024 R2 supports implicit VOF with
PISO on this case. The settings export contains `(mp/scheme-type 0)`, Fluent
automatically changes Geo-Reconstruct to Compressive, and the live allowed
implicit interface schemes are `Compressive` and `Modified-HRIC`. The exact
implicit Courant monitor is `cell-convective-courant-number`. The explicit
parent was cold-restored exactly after each reversible probe. This does not
authorize `Coupled with Volume Fractions` on explicit VOF; that separate
option is unsupported for the explicit formulation.

Five matched branches then cold-loaded the same checksum-bound step-940
case/data pair and advanced the same `0.00512 s` physical window at
`dt=2.56e-4 s`, 20 physical steps and 20 inner iterations:

| Formulation / coupling / interface / time | End continuity | Average velocity (m/s) | Vorticity (1/s) | Maximum velocity (m/s) | Result |
|---|---:|---:|---:|---:|---|
| Explicit / PISO / Geo-Reconstruct / first order | `3.81644e-4` | `0.0035175954` | `0.032923764` | `0.14219102` | all hard gates passed |
| Implicit / PISO / Compressive / first order | `8.51484e-4` | `0.0035482901` | `0.033308462` | `0.16020479` | all hard gates passed; non-promotable |
| Implicit / PISO / Compressive / second order | `7.14202e-4` | `0.0035302233` | `0.033132853` | `0.15213465` | better implicit candidate; non-promotable |
| Implicit / PISO / Modified-HRIC / second order | `7.00262e-4` | `0.0035281957` | `0.033105440` | `0.15190372` | slightly closer implicit candidate; non-promotable |
| Explicit / plain Coupled / Geo-Reconstruct / first order | `2.395996e-4` | `0.0035175976` | `0.032923763` | `0.14219098` | field-equivalent to PISO; non-promotable endpoint |

Every completed branch retained bounded VOF and pressure, stable liquid
inventory (the maximum cross-branch endpoint difference was `0.0002385 kg`),
brine-face liquid VF `1.0`, zero liquid
through the steam outlet, passing storage/clock gates, DPM with zero injection
objects and off, EWF off, and all sources/sinks off. The implicit branches
used maximum cell-convective Courant values of about `0.00977-0.01235`; the
explicit branches used Fluent's separate Global Explicit-VOF Courant metric,
about `0.01240-0.01250`. Those two Courant definitions are gated separately
and are not numerically equated.

First-order implicit VOF changed the explicit endpoint by `+0.873%` in
average velocity, `+1.168%` in vorticity and `+12.669%` in maximum velocity.
Second-order time reduced the remaining differences to `+0.359%`, `+0.635%`
and `+6.993%`. Modified-HRIC moved them only slightly further, to `+0.301%`,
`+0.552%` and `+6.831%`. Modified-HRIC and second-order Compressive differ by
only `0.057%`, `0.083%` and `0.152%` in those measures. Thus the implicit
interface scheme is not the main unresolved axis and formulation independence
is not established.

Plain Coupled was read back as `flow_scheme=Coupled` with
`coupled_form=false`, proving that the unsupported Coupled-with-Volume-
Fractions mode was not selected. Coupled reproduced the PISO physical field to
better than `0.000063%` at the endpoint and throughout the matched samples.
It lowered endpoint continuity by `37.22%` but consumed `1460.57 s` of summed
per-step wall time versus `451.64 s` for PISO, a diagnostic ratio of `3.2339`.
PISO is therefore retained as the efficient closed-pool pressure-velocity
baseline. Pressure-velocity coupling does not explain the timestep or
explicit/implicit interfacial differences.

The first Coupled attempt is preserved as a zero-step local raw-TCP sandbox
denial. The second authenticated, changed the scheme and stopped before a
physical step because the wrapper incorrectly expected an explicit-VOF phase
residual equation; its real settings all read back correctly. Attempt 3 used a
fresh label, cold-loaded the parent again and completed the accepted matched
diagnostic. No stopped in-memory field was resumed.

Machine-readable comparison records are:

- `implicit_piso_comparison.json`, SHA-256 `88353f55...5f21`;
- `implicit_temporal_order_comparison.json`, SHA-256 `9a585f4f...adb0`;
- `implicit_interface_scheme_comparison.json`, SHA-256
  `e87de881...cae4`;
- `pressure_velocity_coupling_comparison.json`, SHA-256
  `ccec7afc...7248`.

Classification is `accepted diagnostic` for the solver sensitivities and
`diagnostic / unresolved` for the model as a whole. The authoritative common
parent remains the explicit/PISO step-940 pair, SHA-256
`03383ac0...6c7c9` / `a5963dfa...0772a`. No implicit or Coupled endpoint is
promoted. Solver swapping is stopped because it no longer addresses the
dominant uncertainty. The next physical model step is a separately gated
constant-level brine-outlet strategy with an emergent liquid seal; it still
requires explicit assumptions or data for downstream pressure/head,
pipe/valve resistance and operating liquid level. Mesh convergence remains
withheld until that boundary/control model is fixed.

### First open-drain pressure-response launch on 23 August 2026

The next physical experiment was implemented as
`run_setup07n_c_pressure_response_sign_probe.py`. Each centre/low/high member
must independently cold-load the accepted explicit/PISO step-940 pair, retain
zero inlet flow, convert only `brineoutlet` from wall to pressure outlet and
advance ten guarded steps at `dt=2.56e-4 s` with 100 inner iterations. The
diagnostic centre is the accepted step-940 closed-face mean
`1,122,423.2 Pa`; the bracket is one full-liquid-feed reference velocity head,
`+/-195.156 Pa`. These remain CFD-derived modified pressures, not plant data.

No open-drain physical step has yet been credited. Attempt 1 authenticated,
verified Fluent 2024 R2/16 ranks, cold-loaded and checksum-verified the exact
parent and passed its closed settings gate, then lost the gRPC stream during a
redundant read-only parent phase-flux report. It stopped before boundary
conversion, initialization, solve or case/data write. Its manifest SHA-256 is
`d58d06c9...c26`; a non-overwriting disposition record, SHA-256
`0c008bd3...8449`, classifies it `stopped_zero_step_before_boundary_change`
and prohibits resume.

Attempt 2 used a fresh label but the bounded unauthenticated raw-TCP preflight
timed out before authentication. Its manifest and disposition SHA-256 values
are `d0e5963e...238` and `dd391d0d...854`; it is
`stopped_zero_step_before_authentication`. The Windows host still answered two
ICMP probes at `8.6-9.0 ms`, while Fluent port `57329` timed out repeatedly.
This isolates the present execution blocker to the stopped/unreachable Fluent
server endpoint rather than the host route. Attempt 3 is prepared under a new
non-overwriting label but must not start until raw TCP returns. No controller
or level feedback has been authorized, and no setup-07n writer is active.

The earlier server-2 rejection conflated two endpoints. The occupied partner
Stage-4 endpoint was Fluent 2025 R2. The separately configured server 2 was
independently audited as Fluent 2024 R2, `Status.SERVING`, exactly 16 ranks
(`n0..n15`) and no connected client before ownership. It did not contain the
authoritative server-1 step-940 pair, so it was not permitted to continue or
replace that lineage. It was used only for the independent clean
reconstruction below.

### Independent configured-server-2 closed-pool reconstruction on 24 August 2026

Exact local process and lock audits found no writer before each stage. Every
stage used a bounded raw-TCP preflight, a no-client/version/rank/file gate and
one owner with `cleanup_on_exit=False`. The forbidden server-2 steady Mixture
field was never loaded or resumed. Instead, a setup-07j settings carrier was
reconstructed into a clean setup-07l isolation state, followed by a fresh
Hybrid Initialization, exact `98,473`-cell pool patch, time-zero save/reload
and full boundary/model/DPM/EWF/source readback. Liquid volume and inventory
were `4.400159116 m3` and `3877.468071393 kg`.

The independent explicit-VOF/PISO ladder advanced ten physical steps at each
factor-two timestep with 20 inner iterations and one step per RPC:

| `dt` | Cumulative step/time | Maximum inner continuity in stage | Final end-step continuity | Final Global Courant | Final maximum velocity |
|---:|---:|---:|---:|---:|---:|
| `1 us` | `10 / 0.00001 s` | startup bounded | `2.84006e-6` | `7.73149e-9` | `6.63818e-5 m/s` |
| `2 us` | `20 / 0.00003 s` | `0.00103931` | `4.74447e-6` | `4.81584e-8` | `1.64973e-4 m/s` |
| `4 us` | `30 / 0.00007 s` | `0.00226804` | `9.20350e-6` | `2.27224e-7` | `3.53561e-4 m/s` |
| `8 us` | `40 / 0.00015 s` | `0.00460693` | `1.85065e-5` | `9.78157e-7` | `7.25976e-4 m/s` |
| `16 us` | `50 / 0.00031 s` | `0.00925466` | `3.63730e-5` | `4.05095e-6` | `0.00146763 m/s` |
| `32 us` | `60 / 0.00063 s` | `0.0185170` | `7.34912e-5` | `1.64766e-5` | `0.00294974 m/s` |
| `64 us` | `70 / 0.00127 s` | `0.0370824` | `1.47452e-4` | `6.63914e-5` | `0.00591963 m/s` |
| `128 us` | `80 / 0.00255 s` | `0.0744209` | `3.19936e-4` | `2.65612e-4` | `0.0118853 m/s` |
| `256 us` | `90 / 0.00511 s` | `0.450821` | `7.94905e-4` | `0.00104941` | `0.0242414 m/s` |
| `512 us` | `100 / 0.01023 s` | `2.56074` | `0.00254275` | `0.00457429` | `0.0530950 m/s` |

The `256 us` stage is the last clean independent comparison. Its endpoint
case/data SHA-256 values are
`763fae763ce43c36505c7dc06986082f361e257c93afc778b5583a41dd15fd22` and
`9513a957ae42e59db076466754a226c44b7bfdfa7f8a69b40e44139fa2bae6b7`.
The `512 us` stage completed but is a **terminal diagnostic**: every physical
step had an inner continuity spike above `1`, the stage maximum was `2.56074`,
and the first end-step continuity was `0.0104354`. Its later tail recovery
does not override the failed residual envelope. A separate non-overwriting
`nonpromotion_adjudication_20260824.json` sets promotion, resume, parent use
and the next timestep extension to false. The endpoint is preserved only as
evidence, with case/data SHA-256
`1dd70482a874dba6ff37e894e25c9c2deea06537987f94fa66d341e0c7add6e6` /
`b51affd9d24f05a939a117433392228666f9f26aee18513a7c1c695e0a42bf5d`.

At every stage liquid inventory was exactly unchanged, liquid flow through the
steam outlet was zero, brine-face liquid volume fraction remained `1.0`, and
net mixture flow was only round-off-scale vapor flux. These are steam-seal and
closed-pool conservation results, not an operating mass-balance result: both
feeds were zero and the brine boundary was a wall, so there was no injection
or drainage. The configured-server-2 chain remains independent and
non-authoritative; it does not supersede, merge into or qualify the server-1
step-940 parent, the open outlet, constant-level control or mesh convergence.

### Independent still-pool contour package on 25 August 2026

A sole post-processing client checksum-verified and cold-loaded the independent
server-2 time-zero, startup step-10 (`t=10 us`) and last-clean step-90
(`t=0.00511 s`) pairs. Fluent 2024 R2, 16 ranks, closed brine wall, zero feed,
phase identity, DPM zero/off, EWF off and all sources off read back correctly.
No initialization, iteration, DPM update or case/data write was issued.

Twelve matched 1920 x 1440 Fluent hardcopies and five report-ready composites
were saved under
`brine620k_07n_a_server2_independent_stillpool_figures_attempt1_20260825`.
The brine-axis liquid-volume-fraction views show that the selected liquid pool
covers the resolved brine-leg entrance and remains unchanged through the
displayed interval. The initially constant pressure field develops lower-pool
head, while velocity remains small and localized near the interface/pipe
entrance. The vessel-axis `x=-1.5 m` raw slice did not intersect this selected
pool and is preserved but excluded from interpretation.

This is accepted as a traceable **post-processing diagnostic**, not a new
physical acceptance gate. The literal accepted setup-07l stepped trajectory is
still on unavailable server 1. The displayed server-2 field remains an
independent setup-07n reconstruction with zero inlets and a wall at the brine
face; it cannot prove drainage, open-boundary steam sealing, level control or
operating mass balance.

### First independent server-2 drainage launch on 25 August 2026

The clean server-2 step-90 pair was separately adjudicated for independent
same-`dt` control and zero-feed pressure-response use without changing its
original manifest. This does not make the pair authoritative or eligible for
the server-1 lineage. The pressure centre was recalculated from this parent,
not imported from setup 07m or server 1: the closed-face mean modified
pressure is `1,122,349.5 Pa`, with diagnostic one-velocity-head members at
`1,122,154.344 Pa` and `1,122,544.656 Pa`.

A matched closed-wall control cold-loaded the exact pair, reverified Fluent
2024 R2, ranks `n0..n15`, ownership, checksums, settings, DPM zero/off, EWF off
and source-off state, then advanced at unchanged `dt=2.56e-4 s` and 20 inner
iterations. Four steps were fully monitored and passed every gate:

| Cumulative step | End-step continuity | Global Courant | Maximum velocity | Liquid inventory | Brine-face liquid VF |
|---:|---:|---:|---:|---:|---:|
| `91` | `8.77262e-4` | `0.00110266` | `0.0252033 m/s` | `3877.468071 kg` | `1.0` |
| `92` | `8.26976e-4` | `0.00115564` | `0.0261306 m/s` | `3877.468071 kg` | `1.0` |
| `93` | `8.09759e-4` | `0.00121011` | `0.0270324 m/s` | `3877.468071 kg` | `1.0` |
| `94` | `8.67273e-4` | `0.00127507` | `0.0279062 m/s` | `3877.468071 kg` | `1.0` |

Fluent physically advanced step 95 to `t=0.006390 s`, but a Scheme/gRPC call
stalled while verifying deletion of an already-read, uniquely named scratch
report. The controller was stopped after a bounded wait. Step 95 is
observed-but-uncredited, no step-5 checkpoint was written, and the entire
attempt is `diagnostic / unresolved` and non-resumable. A checksum-bound
companion disposition preserves the distinction between four fully monitored
steps and the uncredited fifth field.

The pressure-response controller was then changed only to retain unique
scratch report files instead of issuing that optional cleanup RPC. After a
fresh process audit and three successful raw-TCP probes, its first attempt
stalled before authentication while PyFluent waited for Fluent's Scheme
version response. It was stopped after 120 s and preserved as a zero-step
connection failure: no connected-client report, version/rank readback, parent
load, boundary conversion, physical step or case/data write occurred. Raw TCP
reachability therefore does not currently establish Fluent service health.

No drainage result has yet been produced. The next attempt must use a new
label, cold-load the original step-90 pair, and pass a bounded gRPC handshake,
exclusive-client, version, rank, checksum and complete settings gate before
opening the brine boundary. The stopped control field and zero-step pressure
attempt must never be resumed. Full feed, feedback control and setup 07n-b
remain withheld until the zero-feed pressure bracket passes.

The reusable method check now documented in
[the CFD-wiki separator-method synthesis](../CFD_wiki/wiki/synthesis/fluent-separator-efficiency-methods.md)
supports this ordering. Published VOF work provides precedent for matching a
total outlet rate to the inlet to maintain a constant level, while the Purnanto
geothermal baseline assumed the level and excluded resolved water flow into the
brine pipe. This supports `07n-b` as an ideal diagnostic only; it does not supply
the missing plant pressure, resistance or operating level, and it does not
justify prescribing the outlet phase split.

A later read-only recovery preflight repeated the same distinction: server 2
passed three raw-TCP probes but produced no Fluent version response within a
90 s guarded idle limit; server 1 timed out on its first 3 s raw-TCP probe.
No local Fluent/PyFluent/controller process remained afterward. Therefore
neither configured server was safe for a writer at the close of this attempt.
