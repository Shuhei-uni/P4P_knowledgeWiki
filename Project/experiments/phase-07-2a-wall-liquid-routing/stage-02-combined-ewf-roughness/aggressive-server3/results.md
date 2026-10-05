# Stage 2 — Server 3 aggressive continuation result

| Measure | Verified evidence |
| --- | --- |
| Status | SMOKE_COMPLETE |
| Verified native endpoint | N45906 |
| Additional updates | 300 |
| Film time added after N45606 | 1.590740 ms |
| Total corrected-restart added film time | 42.359756 ms |
| Accepted final film step | 3.207972 µs |
| Film inventory | 6.372747 kg |
| Last-window accretion | 82.174058 kg/s |
| Last-window drainage | 74.290978 kg/s |
| Last-window storage | 7.897607 kg/s |
| Last-window drainage deficit | 9.593149% |
| Overall film ledger error | 0.028385% |
| Maximum thickness in last window | 0.306824 mm |
| Peak CFL in last window | 0.094455 |
| Last-window final EWF residual above 1 | 29 / 100 updates |
| Last-window updates meeting the film stop value | 69.00% |
| Saved-endpoint reopen | PASS |
| Steady film | Not qualified by this record |

![Film continuation histories](film-convergence.png)

Native reports and final EWF subiteration residuals; rates use successive cumulative mass and film-clock differences. Intermediate clocks are rounded.

| Evidence / limit | Record |
| --- | --- |
| Controlled delta and parent | [Setup](setup.md) |
| Machine state and paired endpoint hashes | [Run manifest](../../../../../PyAnsys/output/phase72a-stage2-server3/20261005/run-manifest.json) |
| Native histories and quantitative summary | [Analysis summary](../../../../../PyAnsys/output/phase72a-stage2-server3/20261005/analysis-summary.json) |
| Film rates and residuals | [CSV](../../../../../PyAnsys/output/phase72a-stage2-server3/20261005/film-history.csv) |
| Comparison limit | Server transfer can change residual normalization; a smaller scaled residual alone cannot prove improvement |
| Implicit-film subiteration control | [Fluent 2025 R2 user guide §30.4](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/flu_ug_ewf_sec_eqns.html) |
| Verified numerical change at N45706 | {'sub-iter-nums': 30}; paired reopen PASS |
| Verified numerical change at N45806 | {'courant-number': 0.08}; paired reopen PASS |
| Accounting limit | Film ledger only; steady carrier pseudo-time is not physical film time |
| Scientific limit | No whole-separator closure, timestep independence or physical validation |
| Next action | Continue stable batches to the bounded horizon; repair severe inner-film failures before longer compute |
