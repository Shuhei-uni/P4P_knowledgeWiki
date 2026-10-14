# New-mesh Purnanto replication — proposed next scope

| Decision | Status |
| --- | --- |
| Human end goal | Repeat Purnanto 2013 on the new mesh; assess agreement and measurable improvement |
| Current selected action | Recover and compare saved pre-divergence OFF flow fields; no new solve |
| Smallest useful present deliverable | Field/profile agreement, iteration dependence and attempted solver cost; do not require another cause investigation |
| Further body-force cause tests | Not selected; human prefers to stop this line |
| Seven-level baseline | M01–M06 failed; M07 user-skipped; classifications retained |
| What current fields can answer | Fixed-iteration mesh sensitivity and retained flow structure |
| What current fields cannot answer | Accepted steady mesh independence, reliable separator efficiency, or validated physical accuracy |
| Recommended approach | One defensible carrier baseline, small output-based refinement check, then paper replication and cost comparison |
| New simulations | Proposal only; physical/boundary changes need separate scientific selection |

## Claims and evidence

| Intended claim | Required comparison | Current position |
| --- | --- | --- |
| Paper flow features reproduced | Same geometry/operating point; paper velocity and pressure targets with matched locations and definitions | Saved fields can support exploratory pattern comparison; source coordinate/geometry mapping remains to verify |
| Mesh sensitivity is small for the outputs used | Numerically acceptable states on two or three resolutions; pressure drop, profiles and carryover | Current fixed-iteration evidence remains mixed with iteration error |
| New mesh costs less | Same hardware, precision, ranks, model, reporting and accepted-output criterion; solver time and memory | Poly per-block times exist; comparable qualified tet timing is missing |
| New mesh is more accurate | Independent reference and quantified error at comparable cost | No evidence establishes this |
| Droplet tracking is better resolved | Same injection mass weights, tracking controls and wall/outlet fates; escaped/trapped/incomplete represented-mass fractions on acceptable carrier fields | Current Phase 10 carrier fields do not qualify an efficiency calculation |
| New mesh is generally better | Specify which of accuracy, runtime, memory, reliability or particle resolution improves | Use narrower measurable claims instead |

## Smallest useful future study — not launched

| Stage | Comparison | Evidence / stop condition |
| --- | --- | --- |
| 1. Define one baseline | Spiral inlet at 1600 kJ/kg and recorded 197.61 kg/s; verify exact geometry, phase loading and liquid handling | Resolve the paper's fixed-water-level assumption and current inventory growth before accepting an endpoint |
| 2. Obtain a credible carrier state | One practical poly-hexcore mesh; numerical changes documented explicitly | Mass balance, bounded inventory, residuals and stable pressure/velocity profiles must support the chosen statement |
| 3. Check relevant resolution | Production candidate plus a neighbouring finer mesh; add a third only if needed to resolve a trend | Pressure drop and paper-location profiles first; no fixed-iteration substitute for numerical acceptance |
| 4. Compare with the paper | Velocity profiles, pressure pattern, then outlet steam-quality trend if carrier acceptance permits DPM | Use the paper's fields as replication targets; keep empirical/experimental comparison distinct |
| 5. Compare mesh cost | One audited single-inlet tet/poly operating point under the same accepted-output criterion; do not substitute the historical split-inlet study | Measure solve time, memory, restart robustness and output differences; separate I/O/setup |
| 6. Extend operating envelope | Only after the representative point supports the intended claim | Then repeat selected enthalpy/inlet-speed points; avoid a broad unqualified sweep |

The production mesh is not selected from cell count or minimum orthogonal quality alone. The pending saved-field analysis can identify candidates, but cannot qualify one.

## Paper targets and gaps

| Evidence | Reported source | Effect |
| --- | --- | --- |
| Spiral-inlet velocity vectors at 1600 kJ/kg | Purnanto 2013 §4.1, Figure 11, pp6–7 | Qualitative flow-pattern target |
| Spiral-inlet velocity profile | Figure 14, p7; height −3.31 m from vessel top | Verify coordinate mapping and original plotting direction before digitizing; current height-slab means are a different quantity |
| Spiral-inlet pressure field | §4.2, Figure 17, p8, 1760 kJ/kg | A different operating point; do not compare it as the 1600 kJ/kg case |
| Steam quality versus inlet velocity | §4.3, Figure 20, p9 | Replication target with model and particle-fate uncertainty |
| DPM after carrier convergence | Abstract p1 and particle strategy p4 | Pre-divergence snapshots cannot qualify a paper-equivalent efficiency result |
| Unresolved particle fates | §4.3, p8; incomplete tracks assumed separated in the reported estimate | Report unresolved represented mass and a bracket; do not claim improvement by hiding it |
| Fixed water level / omitted brine-pipe flow | §3.1, p5 | Continuum level enforcement is unspecified; current growing inventory is not verified equivalent |
| Experimental calibration still needed | §4.3 and conclusions, p9 | Agreement with this CFD paper alone is not independent validation |
| Historical tet study | [Historical reference](historical-reference.md) | Split inlet and unqualified windows; not a trusted accuracy target for the single-inlet series |

Sources: [Purnanto 2013 primary paper](https://www.researchgate.net/publication/269519626_CFD_MODELLING_OF_TWO-PHASE_FLOW_INSIDE_GEOTHERMAL_STEAM-WATER_SEPARATORS), [NASA grid-convergence guidance](https://www.grc.nasa.gov/www/wind/valid/tutorial/spatconv.html), and [NASA error classification](https://www.grc.nasa.gov/WWW/wind/valid/tutorial/errors.html). The paper text was verified; visual digitization of Figure 14 has not been performed. The maintained wiki extraction is supporting navigation, not a substitute for the checked primary text.

## If no further simulation is practical

| Available report result | Wording limit |
| --- | --- |
| Prepared mesh quality / geometry | Mesh construction and audited quality, not flow accuracy |
| Saved OFF fields at N1000/N2000 | Pre-divergence mesh sensitivity; similarities and disagreements reported explicitly |
| Six baseline failures plus ON failure | Tested steady route remained unqualified; not proof that a steady solution is impossible |
| Per-block poly solver times | Computational cost of these attempts; not time to a converged solution or tet/poly speedup |
| Future replication plan | Proposed method and unresolved evidence; no claimed validation |
