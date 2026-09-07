# Split-Inlet Hydrostatic-Rest Isolation Diagnostic

## Decision

Setup `07l` completed successfully and is accepted as a **bounded isolation
diagnostic**, not as a production separator model. The resolved 620,431-cell
geometry and the `y<=0 m` liquid pool remain essentially motionless when the
inlets are zero and the lower brine face is temporarily closed. This rules out
the mesh and patched pool being inherently unstable at rest. The failed
setups `07j` and `07k` were instead launched from an incompatible combination
of constant-pressure initialization and immediately imposed outlet forcing.

## Why the Fluent connections disappeared

The evidence separates connection symptoms from their causes.

1. Setup `07i` diverged first. Continuity reached `6.9888e14`; the Fluent GUI
   then recorded a Node-4 `SIGSEGV`, connection reset and server shutdown at
   iteration 21. The gRPC connection disappeared because Fluent crashed.
2. Setup `07k` was already nonphysical at step 3: steam-outlet pressure was
   `-4.1102e13 Pa`, outlet velocity was `5.2599e6 m/s`, and domain velocity was
   `7.2714e4 m/s`. The following step-4 RPC hung until its guarded timeout.
3. Earlier raw TCP timeouts occurred before authentication and were consistent
   with network/VPN reachability. A rejected password meant the endpoint
   answered but the server-info/credential pair was stale or mismatched.
4. The warning about an insecure non-TLS gRPC connection is a security warning;
   it is not evidence of solver instability.

The current server reconnected successfully, reported Fluent 2024 R2 and
exactly 16 compute ranks, and completed setup `07l` without a connection loss.

## Forensic corrections to the 07j/07k lineage

Two previously hidden startup problems were found.

- The case contained six inherited DPM injections. Although two-way
  interaction was disabled, the transcripts show Fluent injected and tracked
  `6,456` parcels. One-way tracking probably did not cause the carrier-field
  pressure failure, but the earlier “carrier only; no DPM tracked” statement
  was false.
- Hybrid Initialization explicitly reported that boundary pressure
  information was unavailable and initialized a constant pressure. The dense
  `y<=0 m` liquid pool was patched afterward, so the transient run did not
  start from a hydrostatic liquid-pressure field.

Setup `07l` therefore deletes every injection object, disables unsteady DPM
tracking and interaction, and refuses to run unless zero injections read back.

## Controlled setup

| Item | Setup 07l value |
|---|---|
| Source | accepted clean setup-07j time-zero lineage, never a failed 07j/07k step |
| Mesh | `brine-outlet-620kcells.msh.h5`, 620,431 cells, 16 ranks |
| Carrier | transient explicit VOF; vapor primary, liquid secondary |
| Turbulence | RNG `k-epsilon` |
| Gravity / Energy | `(0,-9.81,0) m/s2` / off |
| Numerics | PISO, PRESTO, Geo-Reconstruct, WFGC, first-order time |
| Liquid pool | phase-2 volume fraction 1 below geometry-inferred `y=0 m` |
| Inlets | both phase rates set to `0 kg/s` |
| Steam outlet | pressure outlet, `1.12 MPa` |
| Brine face | temporary wall |
| Operating density | specified vapor density, `5.79743385 kg/m3` |
| Reference pressure point | `(0,1,0) m`, in the gas region |
| DPM | six injections deleted; zero objects; unsteady tracking off; interaction off |
| Physical step | `1e-6 s`, 20 inner iterations, one step per RPC |

Fresh Hybrid Initialization and the pool patch were repeated, then a separate
time-zero case/data pair was saved. Ten physical steps were run with a distinct
case/data checkpoint after every step. No 07j or 07k file was overwritten.

## Results

| Quantity | Step 1 | Step 3 | Step 10 |
|---|---:|---:|---:|
| Flow time, s | `1e-6` | `3e-6` | `1e-5` |
| Domain-average velocity, m/s | `5.792e-8` | `1.598e-7` | `4.898e-7` |
| Domain liquid volume fraction | `0.15826588` | `0.15826588` | `0.15826588` |
| Liquid inventory, kg | `3774.370486` | `3774.370486` | `3774.370486` |
| Steam-outlet mixture flow, kg/s | `0` | `8.63e-10` | `1.17e-12` |
| Brine-wall minus steam pressure, Pa | `2092.6` | `2091.0` | `2090.4` |
| Global Courant | `1e-16` | `2.396e-9` | `1.010e-8` |
| Final inner continuity residual | `1.558e-3` | `2.288e-5` | `3.470e-6` |

The final velocity residuals were `1.36e-7`, `2.08e-7` and `1.28e-7` in the
three directions. No finite-field, VOF-boundedness, closed-flux, inventory,
pressure, velocity, clock or DPM gate failed. There was no `SIGSEGV`, FPE or
parcel-tracking text in either qualification transcript.

## Hydrostatic interpretation

The brine-face centroid is `0.25417245 m` below the geometry-inferred pool
level. With the liquid density used by Fluent,

```text
Delta p_h = rho_l g h
          = 881.2108765 x 9.81 x 0.25417245
          = 2197.24 Pa
```

Setup `07l` produced `2090.4 Pa` at step 10, only `4.86%` below this simple
centroid estimate. Therefore applying `1.12 MPa` at both the elevated steam
outlet and the submerged brine face is not neutral: it removes roughly the
internal hydrostatic head at the lower face and drives drainage. The exact
production pressure still cannot be chosen without the downstream pipe,
vessel level and loss/resistance data.

The steam pressure outlet printed reversed-flow face warnings during inner
iterations, but net flow and velocity were approximately zero. This does not
invalidate the rest test; it does mean outlet direction must be gated again
when the production boundaries are reopened.

## Next controlled branch

Do not resume 07j or 07k. The next branch should start from a clean,
DPM-deleted, hydrostatically relaxed state and use one-step gates before any
long run:

1. obtain the downstream brine static pressure, liquid-level datum, pipe loss
   or resistance curve if possible;
2. otherwise bracket the lower-face pressure around the observed
   `1.12209 MPa` rest value and label the result diagnostic;
3. open the brine pressure outlet first with zero inlets and test `1e-6`,
   `3e-6` and `1e-5 s` one-step cases;
4. only after a bounded outlet-opening test, ramp the phase inlets rather than
   applying full `116.92/80.69 kg/s` flow at the first step;
5. capture actual Global Courant, outlet reversals, phase fluxes, pressure
   extrema, liquid inventory and storage-aware closure after every step.

The Fluent 2024 R2 guidance supporting explicit-VOF Courant control, PISO,
operating-density treatment and careful transient startup is recorded in the
[VOF controls](https://ansyshelp.ansys.com/public/Views/Secured/corp/v242/en/flu_ug/flu_ug_sec_mphase_using_steps_vof.html),
[multiphase setup](https://ansyshelp.ansys.com/public/Views/Secured/corp/v242/en/flu_ug/flu_ug_sec_multiphase_setup.html),
and [multiphase solution strategy](https://ansyshelp.ansys.com/public/Views/Secured/corp/v242/en/flu_ug/flu_ug_sec_multiphase_solution.html).

## Evidence files

Local evidence root:

```text
PyAnsys/output/split_inlet_resolved_brine_outlet_20260813/
  brine620k_07l_hydrostatic_rest_v1/
```

It contains `preparation_manifest.json`, `qualification_manifest.json`,
`analysis_summary.json`, both transcripts, guarded-controller logs,
`residual_history.csv`, `transient_physical_history.csv`, the accepted time-zero
pair provenance and checkpoint provenance for steps 1 through 10.
