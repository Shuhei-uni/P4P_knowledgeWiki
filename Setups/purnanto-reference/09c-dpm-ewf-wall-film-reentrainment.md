# Setup 09c — Two-Way DPM Coupling

## Canonical metadata

| Field | Value |
|---|---|
| Programme | `purnanto-reference` |
| Legacy setup ID | `09c` |
| Lifecycle | `reported` |
| Role | two-way DPM coupling branch |
| Parent | [09b — RSM/DPM split-inlet accuracy](../past/reported/09b-rsm-dpm-split-inlet-accuracy.md) |
| Evidence-use label | preliminary two-way-coupling diagnostic; not converged |
| Detailed frozen source | [09c compatibility snapshot](../past/compatibility/09c-dpm-ewf-wall-film-reentrainment.md) |
| Numerical evidence | [09c results](../reports/purnanto-reference/09c/results.md) |

## Intent

Test whether the represented droplet loading feeds back strongly enough into the carrier flow that one-way DPM is no longer sufficient.

This is the first `09`-family branch that allows DPM to influence the continuous phase. The historical filename contains `ewf-wall-film-reentrainment`, but the recorded branch role is the smaller **two-way DPM coupling** experiment rather than the later wall-film/re-entrainment plan.

The detailed compatibility snapshot remains the authority for exact inherited case state, DPM loading, solver controls, run notes, and limitations. This canonical record establishes the Purnanto/reference programme as the setup's current physical/navigation owner.

## Interpretation

The setup is retained as reported diagnostic evidence, not a converged or validated physical baseline. Use the linked result report for measured behavior and preserve its limitations when comparing descendants.
