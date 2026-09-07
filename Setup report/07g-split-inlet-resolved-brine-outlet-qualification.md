# Split-Inlet Resolved Brine-Outlet Carrier Qualification

## Purpose and status

Setup `07g` is the first physical liquid-discharge child of setup `07` after
the closed-bottom mesh study (`07a`) and numerical sink diagnostics
(`07b`-`07f`). It tests whether a resolved brine pipe and outlet face allow the
steady Mixture carrier field to establish complete phase/mixture closure and
iteration-independent monitors on one mesh before mesh convergence, DPM or EWF
is reconsidered.

- Study ID: `split_inlet_resolved_brine_outlet_20260813`
- Run label: `brine620k_07g_pressure_equal_psep_v1`
- Status: `Stopped at verified iteration 500; diagnostic/unresolved`.
- Classification: `Diagnostic`; not a valid carrier baseline.
- Parent physics: [07-pure-phase-split-actual-area.md](07-pure-phase-split-actual-area.md).
- Prior formulation evidence: [07a-split-inlet-carrier-mesh-convergence.md](07a-split-inlet-carrier-mesh-convergence.md) and setups `07b`-`07f`.
- DPM/EWF: off; no injection update, tracking or wall-film model.
- Numerical sink: absent; no setup-07b-07f UDF is loaded, compiled or hooked.

## Authoritative inputs

- Original mesh:
  `C:\Users\qtra338\Documents\Mesh study\Meshes\brine-outlet-620kcells.msh.h5`
- Mesh SHA-256:
  `0d75a86e53bc020aeefa4b13ef8616413a862b15646355d90d8037d1be888394`
- Carrier settings:
  `C:\Users\qtra338\Documents\Mesh study\Source\mesh_study_settings.set`
- Fluent: `2024 R2`, 16 partitions.
- Preparation fingerprint:
  `223fd8d3e69bd130e61ce62e8b4799165ccd4ddcf8a55f1507ff4915c8039b30`.
- Saved solution data used as an initial condition: none. The clean mesh was
  configured and freshly Hybrid Initialized before its iteration-zero pair was
  written.

The pre-existing live sink-study field was preserved separately before the new
mesh was loaded:

```text
pre_brine_mesh_live_state_unverified.cas.h5
pre_brine_mesh_live_state_unverified.dat.h5
```

These files are recovery evidence only and are not an initial condition for
setup 07g.

## Geometry and mesh preflight

The HDF5 mesh is not an alias of the closed-bottom setup-07a meshes. Fluent
read a dedicated `brine-outlet` pressure face and the following mesh metrics:

| Quantity | Readback |
|---|---:|
| cells | 620,431 |
| faces | 2,852,567 |
| nodes | 1,724,499 distributed |
| partitions | 16 |
| total fluid volume | 27.06309 m3 |
| characteristic size `(V/N)^(1/3)` | 0.03520151 m |
| minimum cell volume | 8.077534e-10 m3 |
| minimum face area | 4.434417e-11 m2 |
| minimum orthogonal quality | 0.250003 |
| maximum aspect ratio | 66.0258 |
| negative-volume check | none reported |

Boundary areas from Fluent are:

| Boundary | Area |
|---|---:|
| liquid inlet | 0.0048896797 m2 |
| steam inlet | 0.51928636 m2 |
| steam outlet | 0.60130517 m2 |
| brine outlet | 0.19936247 m2 |
| inlet outer wall | 2.1364073 m2 |
| main wall | 79.885175 m2 |

The raw mesh contains two velocity inlets, two pressure outlets, two wall
zones, one interior and one fluid cell zone. The formerly separate `bottom`
wall does not exist; its replacement is the resolved lower vessel/brine-pipe
geometry.

## Zone normalization

The settings file was not trusted to match the raw mesher names implicitly.
Before importing settings, Fluent TUI renames were issued and then read back:

```text
simple-spiral-separator--brine-outlet- -> fluid
liquid-inlet                           -> liquidinlet
steam-inlet                            -> steaminlet
steam-outlet                           -> steamoutlet
brine-outlet                           -> brineoutlet
wall                                   -> wall-fluid
inlet-outer-wall-wall-...              -> inlet-outer-wall
```

The settings transcript contains expected missing-zone warnings for the legacy
`bottom`, generic `wall` and `interior-fluid` names. They are non-critical in
this branch because the new physical zones were explicitly mapped, typed and
verified after import. No required inlet, steam outlet, brine outlet or fluid
zone is missing.

## Controlled carrier setup

Readback after settings import and after Hybrid Initialization verified:

- steady pressure-based Mixture model;
- phase 1 `water-vapor-at-psep`, phase 2 `water-liquid-at-psep`;
- RNG k-epsilon with established options and standard wall functions;
- gravity `(0,-9.81,0) m/s2`;
- Energy off;
- SIMPLE/PRESTO, Green-Gauss node-based gradients and inherited
  discretization/under-relaxation factors;
- liquid inlet `116.92 kg/s` in phase 2 only;
- steam inlet `80.69 kg/s` in phase 1 only;
- steam outlet pressure `1.12 MPa`, liquid backflow VF `0`;
- DPM interaction off and no active cell-zone source terms.

Both wall zones receive the same established no-slip wall state.

## First brine-outlet boundary condition

The first qualification uses a pressure outlet:

```text
brineoutlet gauge pressure = 1.12 MPa
phase-2 liquid backflow volume fraction = 1.0
```

The pressure equals the steam-outlet reference pressure. This is a deliberately
neutral first test of the resolved geometry: it lets the vessel hydrostatic and
dynamic field determine the brine flow without forcing the answer to
`116.92 kg/s`. It is not a claim that the downstream brine system pressure is
known. A later pressure bracket is justified only after the physical downstream
pressure or liquid-level datum is supplied. A prescribed mass-flow outlet may
be used only as a diagnostic bracket, not the validation baseline.

## Execution contract

- clean iteration-zero case/data saved before production;
- guarded first blocks of 25 and 225 iterations;
- 250-iteration blocks thereafter to 3,000 iterations;
- separate 250, 500, 1,000, 2,000 and 3,000 case/data checkpoints;
- transcripts, residual rows, physical-monitor histories and machine-readable
  manifests saved after every block;
- stop if either pressure outlet is not discharging after iteration 250;
- no DPM, EWF or numerical sink run.

The first controller completed 25 iterations, proven by 25 Fluent transcript
residual rows, but PyFluent's monitor stream returned zero points. The live
state was saved separately as a verified iteration-25 checkpoint. The failed
controller evidence was preserved, and execution resumed from that checkpoint
with iteration completion proved by either the monitor stream or Fluent's own
residual transcript. The resumed block reached iteration 250 and was preserved
separately; its first post-processing attempt then rejected the alias
`phase-2-volume-fraction`. Fluent's allowed-value readback identified the valid
field as `phase-2-vof`. The controller and recovery manifest were corrected,
tested and resumed from the verified iteration-250 pair. No duplicated
controller is active.

## Quantities and acceptance

Every block records:

- continuity and all other residuals;
- complete mixture, vapor and liquid fluxes over both inlets and both outlets;
- steam-outlet vapor/liquid flow and steam quality;
- brine-outlet liquid/vapor flow and liquid fraction;
- vapor recovery, liquid recovery, carryover and carry-under fractions;
- pressure drop to both outlets;
- steam/brine outlet velocities;
- volume-averaged velocity, vorticity and liquid volume fraction.

Iteration independence over iterations 2,500-3,000 requires:

- mixture, vapor and liquid imbalance no greater than 0.5%, preferably 0.2%;
- no outlet flow reversal in the integrated mixture flux;
- no more than 0.5% drift in both pressure drops and the dominant outlet phase
  flows;
- no more than 1% drift in outlet/domain velocity, vorticity and domain liquid
  volume fraction;
- residual histories that are bounded and non-growing. Residual count alone is
  never acceptance.

An accepted setup-07g result would qualify the boundary formulation on this
single mesh only. It would not establish mesh independence, separator
efficiency, DPM carryover or EWF behavior.

## Interim iteration-500 evidence

The first complete physical-monitor row is `Diagnostic / Unresolved`:

- mixture steam outlet `-38.76477 kg/s`;
- mixture brine outlet `-37.179327 kg/s`;
- mixture imbalance `61.5687%`;
- vapor imbalance `0.9362%`;
- liquid imbalance `104.7145%`;
- brine phase fluxes: vapor `-42.680678 kg/s`, liquid `+5.512239 kg/s`;
- steam-outlet phase fluxes: vapor `-38.76477 kg/s`, liquid approximately zero;
- pressure drop to steam/brine outlets `7.8008/9.7230 kPa`;
- domain-average liquid VF `0.00404834`.

Negative is outward at an outlet. Therefore both outlets discharge net mixture,
but the brine face is vapor-dominant and liquid is entering through it. This
does not satisfy the intended phase route. The following requested
250-iteration block produced only 62 residual rows before Fluent stopped, so it
was not credited. The later live field reached overflow-scale values and is not
used as physical evidence. The separately saved iteration-500 case/data pair is
the terminal verified state for this branch.

The main interpretation is an initialization dependency: a dry Hybrid start
does not establish the liquid reservoir needed for outward brine drainage.
Setup `07h` therefore repeats the same source-free geometry and boundary
formulation with an explicit lower liquid pool, without changing the carrier
physics or inventing a hydrostatic pressure offset.

## Outputs

Local evidence:

```text
PyAnsys/output/split_inlet_resolved_brine_outlet_20260813/
  preflight/
  brine620k_07g_pressure_equal_psep_v1/
```

Remote case/data evidence:

```text
C:\Users\qtra338\Documents\Mesh study\split_inlet_resolved_brine_outlet_20260813\
```

Status command:

```bash
cd PyAnsys
.venv/bin/python scripts/connection/check_setup07g_status.py
```

## Decision rule

Do not continue from the unphysical live field. Use the clean original mesh for
setup `07h`. If the pool-initialized steady branch establishes correct
discharge, phase/mixture closure and iteration-independent monitors, it may
qualify this boundary formulation on one mesh. If the result remains dependent
on the patched inventory or the pool drains, the next controlled branch is
transient; downstream-pressure sensitivity is deferred until a defensible
plant brine pressure is supplied.
