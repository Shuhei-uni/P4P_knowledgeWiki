# Source-treatment audit — 28 September 2026

| Item | Source-treatment audit — 28 September 2026 |
| --- | --- |
| — | The bounded audit found no concrete assignment, sign, unit or missing transported-property source defect in E7 |
| actual implicit derivative of its named-expression sink | remains unverified |
| — | This finding permits E7 to continue unchanged; it does not validate the collector physically or establish that Fluent uses either a zero or nonzero source Jacobian |
|  | The recovered N500 original-pair and unique-pair reopens, followed by the N505 live check, verified the stored source expressions and phase slots exactly |
|  | Only the collector's secondary phase receives mass removal |

<details>
<summary>Supporting detail — Source-treatment audit — 28 September 2026</summary>

| Item | Source-treatment audit — 28 September 2026 |
| --- | --- |
| — | Its mixture momentum terms remove the liquid-phase momentum; the mixture k and epsilon terms remove the corresponding transported quantities |
| Primary mass and the other fluid zone's sources | are off |
| — | No separate mixture mass sink duplicates the phase source |
| Profile update interval | remains one |
| — | Recovered N1–505 has 504 consecutive pairs for which native applied removal at N equals the expression evaluated at N−1, with zero discrepancy |
|  | That proves source evaluation timing, not linearization or mass closure |
| Reported | Fluent v252 User's Guide §27.2.11.3.2, Table27.5 assigns Mixture mass sources to individual phases and other sources to the mixture |
|  | E7 follows that ownership |
|  | UG §8.2.7 describes source signs, units and corresponding transported-property sources |
|  | These support the implemented bookkeeping, while the collector law itself remains an idealization. [Multiphase source ownership](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/flu_ug_sec_multiphase_setup.html), [cell-zone source terms](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/flu_ug_bcs_sec_cell_zones.html) |
| Missing information | the implicit Jacobian and treatment of clipping/cross-equation dependence |
|  | Customization Manual §2.3.45 documents supplied `DEFINE_SOURCE` derivatives and a degassing example, but that mechanism requires a C UDF, whether interpreted or compiled |
|  | It does not establish how a named-expression source is linearized |
|  | The local PyFluent0.39.0 `settings_252` cell-source schema exposes option, value, profile name, field name and UDF; it exposes no derivative input |
|  | The `linearized_mass_transfer_udf` control concerns mass-transfer UDF macros and is not evidence for this expression source |
|  | Expression postprocessing derivatives likewise do not prove implicit differentiation. [Source UDF API](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_udf/flu_udf_ModelSpecificDEFINE.html), [expression documentation](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/flu_ug_expressions_create_and_use.html) |
| Decision | retain the original source treatment and record the derivative uncertainty |
|  | No evidence here justifies a speculative source rewrite, new C code, or toggling an unrelated mass-transfer control |
|  | E7's terminal conservation/inventory/residual evidence determines whether qualification or the accepted single startup contrast is warranted |
|  | The latter must still be predeclared and assessed at full feed |
|  | No additional experiment is selected by this source audit alone |
| Machine evidence | `PyAnsys/output/phase07b-convergence-investigation/e7/recovery-n500-20260928/preservation.json`, `preservation-n505.json`, `n505-prefix-audit.json`, and `source-documentation-audit.md` |
|  | The documentation packet includes exact manual sections, static API class locations, input hashes and scope limits |
|  | The documentation lookup made no Fluent connection; the single owning recovery process performed all live checks |

</details>
