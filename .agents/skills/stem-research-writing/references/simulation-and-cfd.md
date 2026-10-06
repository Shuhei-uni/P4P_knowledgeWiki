# Simulation and CFD writing

## Describe numerical and physical evidence precisely

Apply this reference when the report contains simulations. Use project records and appropriate technical sources to check terminology; this file does not prescribe solver settings or acceptance thresholds.

Distinguish verification of a numerical implementation or calculation from validation against physical observations for an intended use. Describe which comparison was performed and its range of applicability. Do not infer physical accuracy from lower residuals or from using commercial software.

Report numerical credibility through the relevant evidence: iterative behaviour, conservation checks, sensitivity to mesh and time-step choices, and engineering quantities of interest. Different quantities can settle at different rates. State the observed interval and criteria rather than treating an iteration count as a universal guarantee.

| Wording to inspect | Evidence the report should identify |
| --- | --- |
| The solution converged | Which equations and monitored outputs met which criteria, over what interval |
| The result is mesh independent | Meshes compared, quantities assessed, remaining differences, and scope of the conclusion |
| The flow reached steady state | Evidence that relevant inventories and outputs ceased changing, or a clear definition of statistical stationarity |
| The model was validated | Relevant physical reference data, matched conditions, discrepancy, uncertainty, and intended use |
| Accuracy improved | Agreement against a suitable reference using a defined error measure |
| Realism improved | Evidence of better representation of the relevant physical behaviour; otherwise describe the added model terms |
| The design was optimised | Objective, constraints, search scope, evaluation, and uncertainty supporting the claim |

## Check computational comparisons

Identify whether cases share initial states, boundary conditions, geometry, mesh, numerical methods, and comparable sampling periods. State differences that may affect attribution. When several settings change together, describe a combined change unless evidence isolates individual effects.

Separate solver iterations, physical time, pseudo-time, and substeps. For a partitioned or frozen-field calculation, state which equations evolved and which fields were held fixed. Do not imply fully coupled physical development without methodological support.

## Apply conservation language carefully

Keep equation residuals distinct from a reported mass-balance measure. Define flux signs, included boundaries, sources and sinks, and accumulation where relevant. Distinguish liquid stored in a wall film from liquid discharged through an outlet. Explain the physical or numerical role of artificial absorbing regions and simplified boundaries when they affect the interpretation.

For developing films, distinguish a settled bulk-flow quantity from a settled film inventory. A finite observation interval supports a conclusion about that interval. Describe simulated behaviour as a model result until its relation to the physical device is established.

Keep numerical improvements, inclusion of additional physics, and validated predictive improvements distinct. Report useful partial progress accurately.

Basis: NASA NPARC [Verification assessment](https://www.grc.nasa.gov/www/wind/valid/tutorial/verassess.html), [Validation assessment](https://www.grc.nasa.gov/www/wind/valid/tutorial/valassess.html), and [Iterative convergence](https://www.grc.nasa.gov/www/wind/valid/tutorial/iterconv.html). The comparison, wall-film, and scope checks are original applications of these distinctions and conservation reasoning.
