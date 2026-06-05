# Physics Basis: Operating Pressure, Enthalpy, and Phase Split

## Scope
- Physical question: what thermodynamic and operating assumptions are currently used to reason about steam fraction, liquid loading, and inlet regime entering the separator?
- Why this question matters for separator CFD: many downstream CFD choices are really consequences of how the inlet phase package is framed before the flow enters the separator.

## Evidence Snapshot
| Topic | Current best statement | Evidence label | Main source |
|---|---|---|---|
| Purnanto separator pressure | Baseline separator pressure is `11.2 bara`. | `Reported` | [purnanto-2013], p.5 |
| Purnanto total inlet flow | Baseline total inlet mass flow is `197.61 kg/s`. | `Reported` | [purnanto-2013], p.5 |
| Enthalpy sweep effect | Higher inlet enthalpy increases steam fraction and reduces liquid fraction. | `Reported` | [purnanto-2013], p.5 |
| Typical BOC inlet velocity guidance | Practical inlet velocity guidance is about `30-40 m/s`. | `Reported` | [zarrouk-purnanto-2014], p.253 |
| Pressure effect on separator behavior | Higher pressure can reduce gas velocity and improve separation behavior in a cyclone separator analogy case. | `Reported`, analogy only | [chen-2025], p.15-18 |

## What Prior Research Reports
- `Reported`: Purnanto 2013 provides a useful separator-inlet phase package because the total flow remains `197.61 kg/s` while inlet enthalpy changes move the liquid/steam split from `132.76/64.85 kg/s` at `1440 kJ/kg` to `101.09/96.52 kg/s` at `1760 kJ/kg` ([purnanto-2013], p.5).
- `Reported`: the `1600 kJ/kg` case gives `116.92 kg/s` liquid and `80.69 kg/s` steam, which has become the main local geothermal comparison point in this wiki ([purnanto-2013], p.5).
- `Reported`: separator pressure selection matters to separator performance and plant tradeoffs, including steam production, pressure drop, and scaling risk ([zarrouk-purnanto-2014], p.242-247).
- `Reported`: Pointon 2009 explicitly includes NCGs in the geothermal-scale separator design case, showing that steam fraction alone is not always the full inlet package ([pointon-2009], p.944-945).
- `Reported`: Chen 2025 found that raising back pressure in an air-water cyclone case lowered pressure loss and improved separation because gas velocity and carry-under were reduced ([chen-2025], p.15-18).

## What Prior Research Assumes
- `Assumed`: once separator pressure and inlet enthalpy are known, the inlet can be summarized as a phase split suitable for CFD without fully resolving upstream flashing structure.
- `Assumed`: in the simplest separator-CFD framing, the inlet can be treated as a mist-like steam-dominant two-phase feed rather than a full transient regime map.
- `Assumed`: thermodynamic detail such as salinity, full NCG composition, and non-equilibrium flashing can be omitted in a first engineering comparison if the immediate question is separator flow behavior.

## Cross-Paper Inferences
- `Inferred`: inlet enthalpy is a first-order control on how much liquid the separator has to remove, so it is also a first-order control on how aggressive any droplet or film model needs to be.
- `Inferred`: separator pressure affects not only the thermodynamic split but also the flow field through density and velocity changes, which means pressure should be treated as both a thermodynamic and hydrodynamic variable.
- `Inferred`: a "two-phase inlet" is not one unique physical state. It can represent anything from a dispersed mist assumption to a stronger liquid-wall / vapor-core pre-separation picture, which is why inlet representation is a modeling decision rather than a mere data-entry step.

## Unknowns and Weak Evidence
- `Missing`: a public geothermal dataset tying separator-inlet pressure, enthalpy, NCG fraction, salinity, droplet PSD, and flow regime classification together for one case.
- `Missing`: direct measurements showing whether the separator inlet should be represented more like dispersed mist, annular flow, or a partially pre-segregated feed in the current project context.
- `Missing`: a general geothermal rule for when pressure variation changes carryover mainly through thermodynamics versus mainly through flow-field change.

## Governing Physics
- Total inlet specific enthalpy sets the steam/liquid split at the chosen separator pressure.
- Vapor mass fraction can be written as:
  - `x = m_vapor / (m_vapor + m_liquid)`
- Any change in pressure, enthalpy, or composition changes density and phase fraction, which then changes momentum distribution at fixed geometry.
- The separator therefore responds to both:
  - how much liquid is present;
  - how fast and in what form that liquid enters.

## Consequence for CFD Modeling
- A separator CFD case should make its thermodynamic framing explicit before model choice is debated.
- If the main uncertainty is the phase split itself, testing several enthalpy-driven inlet packages may be more informative than changing turbulence or numerics first.
- If the main uncertainty is how the inlet phases are spatially arranged, several inlet representations may be justified even with the same total mass flow and pressure.

## Reasonable CFD Representations to Test
| Candidate representation | What physical question it can answer | Main warning |
|---|---|---|
| Uniform mist-like inlet | Is a dispersed steam-dominant feed enough to reproduce baseline separator trends? | May hide pre-segregation effects. |
| Two-zone or pre-segregated inlet | Does inlet phase arrangement materially affect separator outcome at the same total phase split? | Arrangement may be assumption-driven rather than measured. |
| Pressure/enthalpy sweep | Does separator behavior change mainly because of changing steam fraction and velocity scale? | Requires consistent interpretation of pressure reference and properties. |

## What This Evidence Does Not Justify
- It does not justify treating one phase arrangement as the true inlet state when only bulk phase flows are known.
- It does not justify assuming pressure effects from Chen transfer numerically into geothermal separators without relabeling them as analogy only.
- It does not justify ignoring NCGs or chemistry forever just because a first-pass flow study omits them.

## Related Pages
- Sources:
  - [purnanto-2013-cfd-geothermal-separator](../sources/purnanto-2013-cfd-geothermal-separator.md)
  - [zarrouk-purnanto-2014-geothermal-separator-design-overview](../sources/zarrouk-purnanto-2014-geothermal-separator-design-overview.md)
  - [pointon-2009-geothermal-separator-sizing-cfd-validation](../sources/pointon-2009-geothermal-separator-sizing-cfd-validation.md)
  - [chen-2025-straight-through-cyclone-water-separator](../sources/chen-2025-straight-through-cyclone-water-separator.md)
- Synthesis:
  - [geothermal-separator-inlet-droplets-and-carryover](../synthesis/geothermal-separator-inlet-droplets-and-carryover.md)
- Concepts:
  - [two-phase-flow-regime-vs-cfd-representation](../concepts/two-phase-flow-regime-vs-cfd-representation.md)
