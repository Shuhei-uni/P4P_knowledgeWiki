# Server 6 — 223k startup

| Check | Result |
| --- | --- |
| Status | RUNNING on Server 6 host; native iteration progress confirmed |
| Mesh | 223,546 cells; original input hash matched on Server 6 |
| Bottom | Five original parts closed and merged as `bottom`; no bottom pressure outlet |
| Collector | Same y <= 0.10 m selection; 59,535 lower cells; 164,011 upper cells |
| Recovery method | Mesh-only ASCII export from intact saved HDF5 target |
| Native export validation | Exact cell/face topology, physical bounds and boundary areas preserved |
| Failed method | Binary legacy case write disabled; incomplete old output excluded |
| Native replacement | Original non-stripping N1580 parent; selected Stage 4 and approved bulk settings applied after interpolation |
| Complete setup comparison | PASS; all setup groups, including boundaries and cell zones, match source template exactly |
| Additional controls | Methods, pseudo-time settings, film model, numerical controls and source hooks match |
| DPM | Six intended injections; no duplicate names; definitions match |
| Feed | Liquid 29.23 kg/s; vapour 20.1725 kg/s; 25% loading |
| Bulk equations | drift, flow, ke and mp active |
| Paired reopen | PASS at N1580; first-reopen flux refresh followed by repeatable second pair |
| Prepared case | Host-local `223k/prepared-stable-low-feed-N1580.cas.h5` |
| Prepared data | Host-local `223k/prepared-stable-low-feed-N1580.dat.h5` |
| Smoke | PASS N1580 to N1600; accepted film time 0 to 2 µs; all report histories complete |
| Smoke peak film Courant | 5.645803e-7 |
| Latest verified pair | N1600 low-feed smoke pair; saved, hashed and reopened |
| Active stage | Low-feed hold N1600 to N2580; 25% feed |
| Observed progress | Native transcript reached N1654; film lines through 7.4 µs; not a new checkpoint |
| Execution | Detached host worker; no laptop required |
| Claim limit | Verified startup setup; no mesh-independence, steady-film or performance claim |

| Evidence | Owner |
| --- | --- |
| Code review | [Reviewed path and code hashes](../../../../PyAnsys/output/phase9-server6-223k/20261015/code-review.json) |
| Settings | [Complete comparison](../../../../PyAnsys/output/phase9-server6-223k/20261015/settings-match.json) |
| Paired child | [Native prepared receipt](../../../../PyAnsys/output/phase9-server6-223k/20261015/223k-prepared-audited.json) |
| Mesh conversion | [Native validation and topology](../../../../PyAnsys/output/phase9-server6-223k/20261015/223k-mapped.json) |
| Bottom components | [Original names and treatment](../../../../PyAnsys/output/phase9-server6-223k/20261015/bottom-map.json) |
| Reference family | [60k/342k/680k/997k template comparison](../../../../PyAnsys/output/phase9-server6-223k/20261015/reference-family-comparison.json) |

| Live run evidence | Owner |
| --- | --- |
| Start proof | [Host worker and native progress](../../../../PyAnsys/output/phase9-server6-223k/20261015/startup-proof.json) |
| Deployment | [Host paths and code bundle hash](../../../../PyAnsys/output/phase9-server6-223k/20261015/host-launch.json) |
| Native sample | [Passive transcript sample](../../../../PyAnsys/output/phase9-server6-223k/20261015/host-live-transcript-sample.txt) |
