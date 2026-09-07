# Split-Inlet Transient VOF with Prescribed Brine Mass-Flow Outlet

## Purpose and classification

Setup `07k` is the controlled boundary-condition successor to the failed
setup-07j equal-pressure transient bracket. It asks whether the resolved outlet
geometry and transient VOF carrier field remain bounded when the known liquid
feed is given a strictly outward discharge route. It is
`Diagnostic / terminal numerical failure`;
the imposed outlet flow is not a measured plant downstream condition.

## Controlled origin and only intended change

- Source: accepted clean setup-07j time-zero case/data.
- Mesh: `brine-outlet-620kcells.msh.h5`, 620,431 cells, 16 compute ranks.
- Models: transient pressure-based explicit VOF, Sharp interface,
  Geo-Reconstruct, RNG k-epsilon, WFGC enabled, gravity `(0,-9.81,0) m/s2`,
  Energy off.
- Inlets: liquid `116.92 kg/s`, vapor `80.69 kg/s`.
- Steam outlet: pressure outlet, `1.12 MPa`, vapor backflow.
- Initialization: fresh Hybrid Initialization followed by the same
  geometry-inferred liquid pool below `y=0 m`.
- EWF and numerical sink/source: off/absent. Global DPM interaction was off,
  but six inherited injection objects remained and Fluent tracked `6,456`
  one-way parcels. This carrier-only contract error was discovered
  retrospectively and is corrected in setup 07l.

The only boundary change is:

```text
brineoutlet:
  pressure outlet at 1.12 MPa
  -> mass-flow outlet
     phase-2 liquid = 116.92 kg/s outward
     phase-1 vapor  = 0 kg/s
```

Fluent settings are read back after conversion and after initialization. The
original 07j files are not overwritten.

## Execution and safety controls

- Fixed time step `1e-4 s`, maximum 20 inner iterations, first-order implicit
  startup and PISO.
- Exactly one physical time step per gRPC calculation call.
- Prove Fluent time-step and flow-time counters after every call.
- Record complete mixture/vapor/liquid boundary fluxes, pressure, velocity,
  vorticity, liquid volume fraction, phase inventories and storage-aware
  closure after every step.
- Stop on any non-finite field, out-of-bounds liquid fraction, incomplete time
  step or gross outlet flux.
- Save non-overwriting pairs at steps 1, 10, 50, 100, 500 and 1000.

The 1000-step target is `0.1 s` of simulated time. Passing that startup window
would still require a matched `dt/2` sensitivity and a defensible physical
downstream boundary before validation.

## Terminal evidence — 21 August 2026

Preparation passed: the boundary conversion, fresh initialization, pool patch,
complete readback and separate 07k time-zero case/data save all completed. At
step 1 the brine flow was exactly `-116.92 kg/s`, steam flow was initially zero
and domain-average liquid fraction was bounded at `0.158245`. At steps 2 and 3
the brine command remained exact while the steam outlet established outward
flow (`-80.3237` then `-83.5122 kg/s`). Phase routes and imposed flow alone
were misleading: by step 3 the mass-weighted inlet pressure was
`3.7445e9 Pa`, steam-outlet pressure was `-4.1102e13 Pa`, steam-outlet velocity
was `5.2599e6 m/s`, and domain-average velocity was `7.2714e4 m/s`.

The step-4 RPC then emitted no output for the guarded two-hour limit and was
terminated with exit code `124`. Step 4 is uncredited. The terminal verified
evidence is step 3, and it is already grossly nonphysical. No setup-07k
controller remains active, and neither the live state nor the step-1 checkpoint
may be resumed for this boundary formulation.

This result shows that prescribing the correct integrated liquid flow does not
cure the startup instability or validate the separator. A defensible coupled
downstream pressure/resistance or level-control formulation remains required.

Forensic correction: the startup also inherited constant-pressure Hybrid
Initialization before the dense liquid pool patch, and the full outlet command
was applied to that quiescent field immediately. Setup 07l subsequently proved
the same mesh and pool are bounded when first isolated at rest with zero DPM
injections, zero inlet flows and the brine face temporarily closed.

## Outputs

Local root:

```text
PyAnsys/output/split_inlet_resolved_brine_outlet_20260813/
  brine620k_07k_transient_vof_massflow_brine_v1/
```

The directory contains preparation/qualification/supervisor manifests,
transcripts, per-step physical history and checkpoint provenance. Remote
case/data use the same run label under the study directory and never overwrite
setup 07j.
