# Vertical-slit film development — current evidence

| Measure | Verified checkpoint |
| --- | --- |
| Controller status | Host launch blocked; live solver state unverified |
| Endpoint | N5290; paired save/reopen PASS |
| Native film time | 7.750000 ms |
| Film mass | 0.475163 kg |
| Numerical qualification | True |
| Bulk equations | Frozen; provisional film result |
| Actual step | 12.500000 µs |
| Peak film Courant in window | 0.037960 |
| Inner-film tolerance passes | 100.0%; COMPLETE |
| Terminal inner residuals above 1 | 0 |
| Film ledger error | 0.000009% |
| Accretion / drainage | 76.003567 / 0.012754 kg/s |
| Storage / drainage deficit | 75.990820 kg/s / 99.983219% |
| Maximum thickness in window | 0.157085 mm |
| Steady-film screen | False; whole-separator qualification remains separate |
| Evidence | [Manifest](../../../../../../../PyAnsys/output/phase72a-stage3-slit154k-film-development-server3/20261006/run-manifest.json); [live supervision](../../../../../../../PyAnsys/output/phase72a-stage3-slit154k-film-development-server3/20261006/live-supervision.json); [setup](setup.md) |

![Wall film thickness](../../../../../../../PyAnsys/output/phase72a-stage3-slit154k-film-development-server3/20261006/wall-film-thickness.png)

Native wall-facet values; angular projection can overlap non-cylindrical wall faces.

| Host handoff | Current limit |
| --- | --- |
| Last verified saved state | N5290 at 7.75 ms; healthy paired save/reopen |
| Server-side imports | Controller and watchdog import passed |
| Host launch | Control requests time out; controller start and watchdog coverage are unverified |
| Required recovery | Release the owned Windows launcher, retain Fluent, then inspect host logs and process receipt before resuming |
| Machine record | [Host handoff status](../../../../../../../PyAnsys/output/phase72a-stage3-slit154k-film-development-server3/20261006/host-handoff-status.json) |
