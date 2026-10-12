# Server 4 — 2.6M run contract

| Stage | Updates | Native endpoint |
| --- | ---: | ---: |
| Start | 0 | N1580 |
| Low-feed smoke, once; all 34 histories | 20 | N1600 |
| Remaining 25% feed hold | 1980 | N3580 |
| 25% to full-feed ramp; changes every 10 updates | 2000 | N5580 |
| Original minimum full-feed hold; superseded by user-selected endpoint | 4000 | N9580 |
| User-selected final initial bulk development state | 3000 full-feed | N8580 |
| Maximum full-feed budget | 20000 | N25580 |

| Acceptance | Requirement |
| --- | --- |
| Feed | Liquid 116.92 kg/s; vapor 80.69 kg/s |
| Pressure-drop range / absolute mean | ≤5% |
| Bulk liquid-mass range / mean | ≤10% |
| Signed steamoutlet liquid-flow range / full liquid feed | ≤5% |
| Original preparation acceptance | Two consecutive complete 1000-update windows and minimum hold; user now selects N8580 without claiming this acceptance |
| Range | Maximum minus minimum within the window |
| Pair promotion | Exact native horizon, finite complete film-clock rows, fixed timestep, Courant/error checks, local paired save and hash, reopen field/setup/method/bulk/clock proof |
| Report contract | Preserve native definitions, signs and source-inclusive versus without-sources distinctions |

| Implementation | Status |
| --- | --- |
| Separate runner | `PyAnsys/scripts/setup/run_phase9_server4_2_6M.py`; adapted from reviewed controller; syntax checked only |
| Separate watcher | `PyAnsys/scripts/orchestration/watch_phase9_server4.py` |
| Native host paths and audit interpreter | Discover and verify after authenticated live inspection |
| Launch gate | No solve until source, transfer, settings and paired child pass native checks |

| EWF settings build | Selection |
| --- | --- |
| Authority | User requests the settings changes only; no new solve in this step |
| Settings and counts | [Simplified EWF plan](../ewf-plan-v1.md) |
| Parent | Preserved final initial bulk pair, N8580 / 0.700 ms |
| Film surface tension | User-selected 0.04041000083088875 N/m, matching approved bulk value |
| Build stage | Bulk equations remain active and fixed film step remains 0.1 µs |
| New run schedule | 2500 active adjustment; 1000 frozen transition; 77,580 frozen updates at 2.5 µs; 2000 final active updates; 83,080 total |
