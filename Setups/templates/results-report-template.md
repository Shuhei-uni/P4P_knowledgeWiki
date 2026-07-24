# Results Report — Setup <ID>

## Setup link

- Setup definition: `<link>`
- Parent setup: `<link or none>`
- Run identity: `<run ID, date, case/data files>`

## 1. Run scope

State what was actually run and which controlled change was tested.

## 2. Numerical results

### Phase flux and efficiency

Record actual inlet/outlet values, units, equations, and scoped interpretation.

### DPM injection trajectory/fate

Record injection name, diameter, represented flow, injected count, and observed escaped count/represented mass at `steamoutlet`. Keep other Fluent fate categories in linked raw artifacts unless they directly answer the setup question.

## 3. Residuals and solution state

Record iteration count, residual behavior, monitor stability, mesh status, and convergence limitations. Whole-domain liquid/mixture imbalance is informational only for the simplified Purnanto geometry.

## 4. Visual findings

Record contour, vector, streamline, pathline, or geometry observations with evidence links.

## 5. Interpretation and limitations

Separate observed numerical results from inferred physical meaning. Keep raw unresolved categories traceable without presenting them as blockers.

## 6. Conclusion

State `keep`, `reject`, or `needs follow-up`, then identify the next setup or report action.
