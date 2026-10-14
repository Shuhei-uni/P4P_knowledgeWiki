# Pre-divergence mesh sensitivity

| Question | Evidence-backed answer |
| --- | --- |
| Can the saved flow fields be compared? | Yes: six OFF levels at N1000; five at N2000; all pairs rehashed and native fields extracted |
| Do the velocity profiles agree? | Broad rotation/height trends persist; speed and swirl profiles do not collapse across refinement |
| Does the comparison establish mesh convergence? | No. Spatial differences remain substantial and the same fields change with iteration |
| Is a production mesh selected? | No; apparent agreement in one bulk average does not qualify a mesh |
| Is the new mesh better than tet? | Not established; no matched qualified tet/poly output and cost comparison |
| New solver updates | 0; original source pairs untouched; BF01 ON N3005 restored with exact scientific state and idle proof |
| Next scope | [Proposed targeted Purnanto replication](replication-next-scope.md); no new numerical study selected |

## Native flow-field evidence

![Saved fields at N1000](../../../PyAnsys/output/phase10-single-inlet-mesh-convergence/predivergence-mesh-sensitivity/height-profiles-N1000.png)

Native cell-volume-weighted profiles in 70 fixed height slabs. M01–M06, original OFF checkpoints at N1000. Signed swirl uses the y-axis through x=z=0 and tangent (z,0,−x)/r. These whole-slab averages are not the paper's radial line profiles.

![Saved fields at N2000](../../../PyAnsys/output/phase10-single-inlet-mesh-convergence/predivergence-mesh-sensitivity/height-profiles-N2000.png)

Same reduction at N2000, M02–M06. M01 failed before this coordinate. The liquid distribution and the central-height speed/swirl patterns vary with both mesh and iteration; equal iteration does not mean equal numerical maturity or physical time.

## Separate mesh differences from iteration dependence

![Velocity comparison](../../../PyAnsys/output/phase10-single-inlet-mesh-convergence/predivergence-mesh-sensitivity/field-refinement.png)

Volume-weighted common spatial bins, 20×70×20. Values are projected velocity-vector RMS differences relative to the reference RMS magnitude, not discretisation-error estimates. M06 is a diagnostic reference. Mesh pairs cover approximately 86–91% of reference volume under the minimum-bin-volume weighting; same-mesh iteration comparisons cover 100%. The coarser 10×35×10 projection covers approximately 93–95% and supports the same bounded conclusion.

| Comparison | N1000 vector difference | N2000 vector difference | Meaning |
| --- | ---: | ---: | --- |
| M04 versus M06 | 16.78% | 16.41% | Resolution sensitivity remains |
| M05 versus M06 | 16.79% | 12.43% | Resolution sensitivity remains |

| Same mesh, N1000 → N2000 | Vector difference | Liquid inventory change |
| --- | ---: | ---: |
| M02 | 26.90% | +230.9% |
| M03 | 17.60% | +229.6% |
| M04 | 18.76% | +198.6% |
| M05 | 20.83% | +177.9% |
| M06 | 21.53% | +183.6% |

Iteration changes are comparable to or larger than the finer-mesh differences. The inventory change is solver-iteration dependence, not a physical filling rate. It prevents attribution of the observed differences solely to spatial discretisation.

| M05 versus M06: check of projection choice | N1000 | N2000 |
| --- | ---: | ---: |
| 20×70×20 vector difference | 16.79% | 12.43% |
| 10×35×10 vector difference | 14.32% | 10.37% |

## Scalar outputs and numerical adequacy

| Level / checkpoint | Cells | Δp, kPa | Mean speed, m/s | Liquid mass, kg | Liquid closure error |
| --- | ---: | ---: | ---: | ---: | ---: |
| M01 / N1000 | 357,145 | 24.622 | 28.822 | 288.318 | 92.9% |
| M02 / N1000 | 487,746 | 23.101 | 28.784 | 201.875 | 92.1% |
| M03 / N1000 | 681,844 | 22.219 | 28.265 | 147.580 | 93.9% |
| M04 / N1000 | 946,967 | 22.919 | 27.672 | 115.412 | 96.8% |
| M05 / N1000 | 1,430,497 | 24.463 | 27.205 | 93.763 | 99.1% |
| M06 / N1000 | 2,209,748 | 23.380 | 26.942 | 78.614 | 98.4% |
| M02 / N2000 | 487,746 | 27.701 | 25.482 | 668.016 | 86.4% |
| M03 / N2000 | 681,844 | 25.081 | 27.015 | 486.421 | 89.2% |
| M04 / N2000 | 946,967 | 25.127 | 27.422 | 344.614 | 90.0% |
| M05 / N2000 | 1,430,497 | 25.064 | 26.978 | 260.547 | 81.0% |
| M06 / N2000 | 2,209,748 | 24.247 | 26.099 | 222.960 | 83.7% |

Δp is original area-averaged inlet pressure minus steam-outlet pressure. Liquid closure error is |signed inlet+outlet flux|/116.92 kg/s. Native source reports use inward-positive flux. [Scalar refinement plot](../../../PyAnsys/output/phase10-single-inlet-mesh-convergence/predivergence-mesh-sensitivity/scalar-refinement.png) shows non-monotonic pressure and continuing inventory dependence. At N1000 M05/M06 mean speeds differ by only 0.98%, while their projected vector fields differ by 14–17%; the bulk mean hides local differences.

| Check | Result | Consequence |
| --- | --- | --- |
| Pair identity | All 22 case/data hashes match native manifests | Saved fields are traceable |
| Original scientific settings | All six native manifest readbacks agree; primary body-force flag OFF confirmed on every load | Mesh is the intended baseline contrast |
| Native field adequacy | Seven arrays per snapshot; finite values, positive volumes, bounded alpha, recorded cell counts | Fields usable for diagnostic comparison |
| Integral reconstruction | Liquid mass uses the exact recorded density; volume and mean speed match original checkpoint evidence | Native cell/phase data ordering and weights checked |
| Time/iteration maturity | Same-mesh vector differences 17.6–26.9% over N1000→N2000 | Iteration error not removed |
| Conservation/inventory | Large phase/mixture closure gaps and inventory growth | No accepted steady solution |
| Residuals / later failures | Existing baseline transcripts and [failure diagnosis](divergence-diagnosis-20261011.md) retained | Finite checkpoint is not a converged endpoint |
| Geometry representation | Common CAD; volume/outlet area discretisation differences remain | Include those differences in sensitivity limits |
| Excluded sources | M07 N718 and BF01 ON | No substituted iteration or mixed numerical setup |
| Error estimate | Richardson/GCI not calculated | Projected field differences cannot serve as numerical uncertainty bands |

NASA distinguishes iterative convergence error from spatial discretisation error; its [grid-convergence example](https://www.grc.nasa.gov/www/wind/valid/tutorial/spatconv.html) uses iteration-converged solutions. These snapshots answer a diagnostic sensitivity question, not that example's accepted error-estimation question.

## Attempt cost — distinct from replication accuracy

| Mesh | Native N1000→N2000 solve time, s | Seconds/update | Qualification status |
| --- | ---: | ---: | --- |
| M02 | 848.8 | 0.849 | Unqualified |
| M03 | 1285.5 | 1.286 | Unqualified |
| M04 | 1664.6 | 1.665 | Unqualified |
| M05 | 2533.9 | 2.534 | Unqualified |
| M06 | 4060.4 | 4.060 | Unqualified |

Controller solve-block timing excludes checkpoint I/O and field extraction. These are single observed block costs on the recorded 16-rank host; they are not time to comparable accuracy, robust performance benchmarks or tet/poly speedup. There is no N1000→N2000 M01 block.

## Decision and source map

| Decision | Current selection |
| --- | --- |
| Preserve failed series and BF01 | Yes |
| Continue unchanged body-force failure tests | No |
| Use saved fields in the report | Yes, as pre-divergence sensitivity and feasibility evidence |
| Select a production mesh / claim validation | No |
| Next study | Proposed single-point carrier acceptance, output-based refinement check and paper/cost comparison; [scope proposal](replication-next-scope.md) |
| Further solves | None selected |

| Machine evidence | Purpose |
| --- | --- |
| [Summary / exact source pairs](../../../PyAnsys/output/phase10-single-inlet-mesh-convergence/predivergence-mesh-sensitivity/summary.json) | Native paths, pair hashes, reductions and full comparisons |
| [Extraction receipt](../../../PyAnsys/output/phase10-single-inlet-mesh-convergence/predivergence-mesh-sensitivity/extraction.json) | Native rehashes, readback, raw-array identities and zero solves |
| [Raw field arrays](../../../PyAnsys/output/phase10-single-inlet-mesh-convergence/predivergence-mesh-sensitivity/raw/) | Eleven immutable cell-field NPZs and source metadata |
| [Scalar comparison](../../../PyAnsys/output/phase10-single-inlet-mesh-convergence/predivergence-mesh-sensitivity/scalar-comparison.csv) | Original checkpoint reports plus native liquid mean height |
| [Spatial comparison](../../../PyAnsys/output/phase10-single-inlet-mesh-convergence/predivergence-mesh-sensitivity/field-comparison.csv) | Mesh and iteration projected RMS comparisons |
| [Projection check](../../../PyAnsys/output/phase10-single-inlet-mesh-convergence/predivergence-mesh-sensitivity/projection-sensitivity.csv) | Coarser-bin comparison |
| [Height profiles](../../../PyAnsys/output/phase10-single-inlet-mesh-convergence/predivergence-mesh-sensitivity/height-profiles.csv) | Raw slab-averaged values and slab volumes |
| [Attempt timing](../../../PyAnsys/output/phase10-single-inlet-mesh-convergence/predivergence-mesh-sensitivity/attempt-solver-cost.csv) | Native solver-block costs |
| [Restore proof](../../../PyAnsys/output/phase10-single-inlet-mesh-convergence/predivergence-mesh-sensitivity/restored-state-proof.json) | Owned ON N3005 pair, exact scientific settings and idle verification |
