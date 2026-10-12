# Selected setup

| Item | Value or source |
| --- | --- |
| Parent iteration | N8080 |
| Parent case SHA-256 | `5cf76ac725522133cea1a7735001d2635759a5bfae301715ba57dedef560bea6` |
| Parent data SHA-256 | `85b9eae0d663ac0b17edb30fe933f01a7cde02c7248d2d756e4a9770c552688f` |
| Fluent release | 2025 R2 |
| Guide | [Setting Up the Reynolds Stress Model, Section 16.10](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/flu_ug_rsm_setup.html) |
| TUI syntax | Installed PyFluent generated v252 TUI definitions, `define.models.viscous` |
| Model activation | `/define/models/viscous/reynolds-stress-model yes` |
| Pressure-strain selection | `/define/models/viscous/rsm-linear-pressure-strain yes` |
| Wall reflection | `/define/models/viscous/rsm-wall-echo yes` |
| Native solve | `/solve/iterate 2000` |
| Start and end pairs | New paths on Server 3 local disk; exact paths in run manifest |
| Reports | Existing definitions routed to a new local monitor directory |
| Native output | Server-local `native.trn`; desktop `client-transcript.txt` |
| Runner | [Implementation](../../../../PyAnsys/scripts/setup/run_rsm_server3_60k.py) |
| Runtime limit | Desktop client records completion while the desktop remains running; native calculation executes on Server 3 |

