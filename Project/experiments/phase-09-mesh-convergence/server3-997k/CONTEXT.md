# Server 3 — 997k EWF continuation

| Contract | Selected value |
| --- | --- |
| Authority | Human, 10 October 2026: move this chat’s 997k EWF work from Server 6 to Server 3; restart the initial EWF settings if needed |
| Mesh and parent | 997,604 cells; verified N8080 pair; inherited film age 0.650 ms |
| Method | [EWF Plan v1](../ewf-plan-v1.md); preserve the parent bulk and upper film fields; no bulk initialization |
| Target | 200 ms total film age; final 195–200 ms with bulk active; nominal N50900 |
| Session safety | Loaded N9380 pair preserved before replacement. Preserve Fluent. Server 6 watcher paused; its Fluent remains untouched. |
| Implementation | Working Server 5 controller/watcher pattern, with native EWF callback and save/reopen at control changes. Desktop must remain awake to dispatch later stages. |
| Evidence | [Machine output](../../../../PyAnsys/output/phase9-ewf-server3-997k/20261010/) |
| Claim limit | Numerical development only; no steady film, full mass closure, or physical validation claim |
