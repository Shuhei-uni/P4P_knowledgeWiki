# Physics Basis: Uncertainties and Assumption Register

## Scope
- Physical question: which missing facts and inherited assumptions currently control separator CFD credibility?
- Why this question matters for separator CFD: sensitivity tests should be chosen by uncertainty importance, not only by what is easy to toggle in Fluent.

## Register
| Topic | Best current basis | Current assumption or gap | Risk | Reasonable CFD test this justifies | Evidence that would retire it |
|---|---|---|---|---|---|
| Inlet droplet PSD | Purnanto `10 um` plus Harwell relation; no measured geothermal inlet PSD | Use droplet-size sensitivity instead of one claimed true PSD | High | DPM sweep over `3-5 um`, `10 um`, `14.2 um`, `40-41 um` or equivalent bracket | Measured separator-inlet droplet distribution |
| Inlet flow regime | Mist-flow wording in Purnanto; no direct project inlet regime measurement | Treat inlet as an engineering representation, not a fully measured regime map | High | Compare uniform mist-style and pre-segregated inlet representations | Direct upstream flow-regime or void-fraction measurement |
| Wall-hit droplet fate | Pointon assumes adhesion in certain regions; simpler DPM often treats wall hit as collection | Permanent wall capture may be optimistic where film re-entrainment is plausible | High | Compare wall-trap interpretation against wall-film-aware sensitivity | Experimental film or carryover evidence showing wall capture permanence |
| Need for wall-film model | Annular literature shows film and droplets can be separate fields | Film/re-entrainment may matter when bulk carryover is low but fine mist persists | Medium-High | DPM + EWF or transient film-aware sensitivity case | Geothermal separator film or re-entrainment measurements |
| Turbulence closure level | Purnanto uses RNG `k-epsilon`; Chen uses RSM; Pointon uses RNG `k-epsilon` with swirl modification | Lower-cost RANS may be enough, but anisotropic swirl could still matter | Medium | RSM sensitivity on one representative geometry case | Validation data showing one closure clearly matches better |
| Pressure-effect interpretation | Geothermal reviews say pressure selection matters; Chen shows hydrodynamic pressure effect in analogy case | Pressure changes likely affect both phase split and flow field | Medium | Pressure or enthalpy sensitivity with consistent property package | Field or experiment dataset with matched geometry across pressure conditions |
| NCG and chemistry package | Pointon includes NCGs; many baseline CFD studies omit detailed chemistry | First-pass flow study may neglect chemistry, but real carryover can depend on it | Medium | Keep chemistry out of first-pass flow study but cross-check with tracer/chemistry validation | Site-specific NCG and carryover chemistry data |
| Simplified lower-liquid path | The current Purnanto-derived geometry does not model the brine/liquid outlet needed for whole-domain liquid closure | Accepted scope limitation | Ignore whole-domain liquid imbalance as an acceptance metric; assess steam-outlet escape only | Revised geometry with a defensible liquid outlet, BCs, and validation basis |
| DPM incomplete trajectories | Some trajectories do not reach a terminal fate within Fluent's tracking budget | Low within current scope | Preserve in raw output but exclude from blocker and decision logic; report observed escape only | Only required if a future study seeks complete fate or collection efficiency |
| Three-field complexity | Annular-flow sources justify droplets + film split in some regimes | Full three-field separator model is not the first justified default | Medium | Use only if re-entrainment becomes the central unresolved mechanism | Geothermal validation need showing simpler models systematically fail |

## What Prior Research Reports
- `Reported`: Purnanto explicitly states the inlet droplet distribution is hard to predict or measure and acknowledges incomplete DPM tracks that could not be removed even by increasing Euler steps substantially ([purnanto-2013], p.3-4, p.8).
- `Reported`: geothermal review papers are strong on design logic and operating envelopes but weak on fully reported CFD control stacks ([zarrouk-purnanto-2014], p.248-253; [rivas-cruz-2015], p.884-886).
- `Reported`: Pointon and Chen both show that model-family and boundary assumptions matter, but neither paper turns separator CFD into a universally complete recipe ([pointon-2009], p.945-948; [chen-2025], p.8-18).
- `Reported`: annular-flow studies show that separating droplets from wall film can materially change how entrainment is reasoned about ([mondal-2024], p.2883-2890; [skoog-2020], p.7-12).

## What Prior Research Assumes
- `Assumed`: missing data can be bridged with physically labeled assumptions so long as those assumptions are carried into sensitivity planning instead of hidden.
- `Assumed`: a lower-fidelity baseline model is acceptable if the next sensitivity is chosen to attack the highest remaining uncertainty.

## Cross-Paper Inferences
- `Inferred`: the highest-risk unknowns are currently inlet droplet structure, inlet phase arrangement, and wall-film fate.
- `Inferred`: numerics still matter, but the largest physical interpretation errors are likely to come from hidden inlet and wall-fate assumptions rather than from minor solver-control differences alone.
- `Inferred`: this register should drive model escalation. Move from simple to complex only when the unresolved uncertainty points to a missing mechanism, not simply to a more fashionable solver.

## Unknowns and Weak Evidence
- `Missing`: geothermal separator datasets combining inlet regime, droplet PSD, wall-film behavior, and outlet chemistry.
- `Missing`: a public geothermal benchmark that closes the loop between CFD assumptions and plant carryover measurements.

## Governing Physics
- Uncertainty matters because each unresolved physical term can force a different closure choice:
  - unknown inlet PSD affects particle-force and drag interpretation;
  - unknown flow regime affects phase topology assumptions;
  - unknown film fate affects whether liquid mass is removed or recycled.
- The practical result is that some CFD settings are really surrogate physics assumptions.

## Consequence for CFD Modeling
- A CFD test matrix should be organized around uncertainty retirement, not only around output generation.
- The next test to run should answer the highest-risk open assumption that can materially change separator interpretation.

## Reasonable CFD Representations to Test
- Use a mist-style DPM bracket when the main uncertainty is droplet size.
- Use alternate inlet arrangements when the main uncertainty is inlet topology.
- Use wall-film-aware or transient tests when the main uncertainty is re-entrainment.
- Use turbulence-model sensitivity when the main uncertainty is anisotropic swirl representation.

## What This Evidence Does Not Justify
- It does not justify treating all assumptions as equal-risk.
- It does not justify escalating immediately to the most complex model without naming which uncertainty it resolves.
- It does not justify reporting a single confident separator-efficiency value when the high-risk uncertainties remain untested.

## Related Pages
- [separator-flow-physics](separator-flow-physics.md)
- [droplets-carryover-and-re-entrainment](droplets-carryover-and-re-entrainment.md)
- [governing-equations-and-modeling-levels](governing-equations-and-modeling-levels.md)
- [operating-pressure-enthalpy-and-phase-split](operating-pressure-enthalpy-and-phase-split.md)
