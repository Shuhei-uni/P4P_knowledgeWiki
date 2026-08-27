> **Retired source:** ResearchProject_wiki/wiki/technical/purnanto-live-setup-reference.md
> **Migration note:** Historical wording, evidence status, and uncertainty labels are preserved; this Project copy is not a reinterpretation. Machine-generated artifacts remain with their original external owners; the retired written source is recoverable from Git history.

# Purnanto Live Setup Reference

## Purpose
Fast reference for the audited Fluent HDF5 case/data pair that now anchors the Purnanto setup in this project.

Use this page when you need the saved Fluent settings rather than the paper narrative.

## Files
- Case: `PyAnsys/data/4800-iterations-300412-1.cas.h5`
- Data: `PyAnsys/data/4800-iterations-300412-1-05000.dat.h5`

Related report:
- [00a live setup audit](setup.md)

Related source pages:
- [Purnanto source extraction](../../../CFD_wiki/wiki/sources/purnanto-2013-cfd-geothermal-separator.md)
- [purnanto-2013-cfd-geothermal-separator](../../../CFD_wiki/wiki/sources/purnanto-2013-cfd-geothermal-separator.md)

## Audited Snapshot

| Item | Value | Label |
|---|---:|---|
| Fluent version | `24.2` | `Observed` |
| Mesh cells | `2,964,593` | `Observed` |
| Mesh nodes | `572,556` | `Observed` |
| Mesh faces | `6,063,406` | `Observed` |
| Minimum orthogonal quality | `0.277635` | `Observed` |
| Maximum aspect ratio | `12.8899` | `Observed` |
| Solver family | pressure-based, steady, `Mixture` | `Observed` |
| Phases | `phase-1 = water-vapor-at-psep`; `phase-2 = water-liquid-at-psep` | `Observed` |
| Turbulence model | `RNG k-epsilon` | `Observed` |
| Energy | off | `Observed` |
| Gravity | `(0, -9.81, 0) m/s2` | `Observed` |
| Operating pressure | `0 Pa` | `Observed` |
| Inlet type | mass-flow inlet | `Observed` |
| Inlet vapor mass flow | `80.69 kg/s` | `Observed` |
| Inlet liquid mass flow | `116.92 kg/s` | `Observed` |
| Inlet pressure field | `1,140,000 Pa` | `Observed` |
| Inlet turbulence intensity | `2.11 %` | `Observed` |
| Inlet hydraulic diameter | `0.724 m` | `Observed` |
| Outlet type | pressure outlet | `Observed` |
| Outlet pressure field | `1,120,000 Pa` | `Observed` |
| Outlet backflow liquid VF | `0.0` | `Observed` |
| Wall zones | `wall-fluid`, `bottom` stationary no-slip walls | `Observed` |
| Residual criteria | continuity `1e-4`; velocity, `k`, `epsilon`, and volume fraction `1e-3` | `Observed` |
| Under-relaxation factors | pressure `0.3`, momentum `0.7`, volume fraction `0.4`, `k` `0.8`, `epsilon` `0.8` | `Observed` |
| Saved iteration count | `5000` | `Observed` |
| DPM injections | none active in the saved case | `Observed` |

## What This Reference Replaces
- Paper-only guesses for mesh size and parity.
- Assumptions about inlet turbulence values, hydraulic diameter, and outlet pressure.
- Assumptions that the saved case only existed as a lab machine audit.

## What It Does Not Replace
- The paper source still governs what was originally reported.
- Initialization field values are still not fully reconstructed from the case file alone.
- Exact paper geometry variant still needs visual confirmation if geometry identity matters.

## Practical Use
Use this page first when you need:
- the exact audited Fluent stack;
- the BC values that are actually in the saved case;
- a short path into the more detailed setup report or source extraction.

Use the paper extraction pages when you need:
- what Purnanto explicitly reported in the 2013 paper;
- the missing-information register;
- the setup logic that still remains inferential rather than observed.
