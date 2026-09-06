# D06R capability proof — steady Eulerian coupled route

Status: `VERIFIED_RECIPE` for configuration mechanics only. This does not make
Eulerian scientifically preferred and does not authorize a discovery solve.

## Fingerprint

| Field | Observed value |
|---|---|
| Fluent | Ansys Fluent 2025 R2 |
| Parent | paired F11 reference case/data from the campaign contract |
| Solver boundary | steady, pressure-based |
| Parent model | Mixture / RNG |
| Child model | Eulerian, two phases |
| Phase mapping | `phase-1=water-vapor-at-psep`; `phase-2=water-liquid-at-psep` |
| Parent coupling | `SIMPLE` |
| Eulerian available coupling choices | `Phase Coupled SIMPLE`, `Coupled` |

## Research question

Can the exact Fluent 2025 R2 F11 child be switched to Eulerian and given the
officially recommended steady-Eulerian `Coupled` pressure–velocity route, with
both states surviving a paired save/reopen?

The manual basis is Fluent's steady Eulerian stability guidance, which
recommends the Multiphase Coupled solver for a steady Eulerian solution and
calls for conservative numerical control when difficulties occur:
[official stability/convergence guidance](https://ansyshelp.ansys.com/public/Views/Secured/corp/v242/en/flu_th/flu_th_sec_multiphase_stab_conv.html).

## Verified dependency order and readbacks

1. Connected to quiescent server 2 and loaded the canonical F11 parent pair.
2. Switched only `setup.models.multiphase.model` from `mixture` to `eulerian`.
3. Reacquired dependency-sensitive objects. The phase/material mapping was
   unchanged.
4. Inspected `solution.methods.p_v_coupling.flow_scheme`; live allowed values
   were `Phase Coupled SIMPLE` and `Coupled`.
5. Set `flow_scheme=Coupled` and read back
   `{flow_scheme: Coupled, coupled_form: false, solve_n_phase: false}`.
6. Saved the disposable model/coupling child under
   `C:\Users\syok443\Documents\FluentRuns\P6\D06R-capability-20260831T204500Z`.
7. Reopened that pair and independently reread `model=eulerian`, the exact
   phase/material mapping, and `flow_scheme=Coupled`.
8. In a second disposable Eulerian + `Coupled` child, redirected all 30
   inherited report files to the declared child monitor root, saved the paired
   child under
   `C:\Users\syok443\Documents\FluentRuns\P6\D06R-report-capability-20260831T205500Z`,
   and reopened it. `readback_report_paths` proved all 30 report identities
   and resolved destinations after reopen; every path remained under that
   child monitor root. This is direct report-package compatibility proof for
   the same Eulerian + `Coupled` configuration, not an inference from the
   Mixture parent.

The pseudo-time Settings branch was inactive in this live Eulerian child.
Therefore D06R must not guess or force a pseudo-time option. The verified
numerical delta is the `Coupled` scheme only; any Courant-control extension
would require a separate live/manual proof.

## Scientific classifications

- `experiment-specified`: full geometry, steady state, F11 parent, 1.115 MPa
  gauge pressure, reports, residual path, 50 + 500 attached horizon.
- `manual-required / verified mechanical state`: Eulerian `Coupled` pressure–
  velocity scheme for the D06R numerical-architecture repair.
- `manual-default retained`: `coupled_form=false`, `solve_n_phase=false`.
- `not selected`: pseudo-time manipulation, Courant override, interaction-law
  invention, or phase/material changes.

## Limitations

This proof establishes a reproducible Fluent configuration path. It does not
prove a smoke solve, numerical adequacy, or the physical relevance of
Eulerian. Those are evidence gates for the separately reviewed D06R screen.
