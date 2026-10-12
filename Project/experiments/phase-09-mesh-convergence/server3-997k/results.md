# Server 3 — 997k EWF run evidence

| Check | Verified result | Evidence |
| --- | --- | --- |
| Existing endpoint | Idle N9380 pair saved and hashed before replacement | [Preservation receipt](../../../../PyAnsys/output/phase9-ewf-server3-997k/20261010/preserved-before-replacement.json) |
| Selected parent | N8080, 0.650 ms; selected case/data hashes match | [Settings receipt](../../../../PyAnsys/output/phase9-ewf-server3-997k/20261010/997k-ewf-settings-current.json) |
| EWF preparation | Plan v1 settings applied, saved, hashed, and reopened; original upper film facets and bulk fields preserved | Same settings receipt |
| Drain evidence transfer | Same parent hashes and EWF controls as Server 6; direct removal evidence applies to this setup; full production mass closure remains unverified | [Identity proof](../../../../PyAnsys/output/phase9-ewf-server3-997k/20261010/same-parent-controls-proof.json) |
| Native schedule | Detached controller launched; each stage writes a local native transcript and paired checkpoint before continuation | [Current run manifest](../../../../PyAnsys/output/phase9-ewf-server3-997k/20261010/run-manifest.json) |
| Supervision | Read-only watcher queues this chat on a stop, delay, or final verification event; ordinary progress stays quiet | [Current supervision](../../../../PyAnsys/output/phase9-ewf-server3-997k/20261010/continuous-supervision.json) |
| Current verified endpoint | N17580 / 33.400 ms; native transcript has 5,000 updates; peak film Courant 0.06521368 below 0.8; case/data hashed and reopened with persistent fields and setup preserved | [Resume verification](../../../../PyAnsys/output/phase9-ewf-server3-997k/20261010/laptop-resume-verification.json) |
| Current command | 10,000 iterations, frozen bulk, 5 µs film step; target N27580 / 83.400 ms. Accepted film updates observed after 33.400 ms | [Recovery receipt](../../../../PyAnsys/output/phase9-ewf-server3-997k/20261010/completion-stream-recovery.json) |
| Final endpoint | Pending: N50900, 200 ms, bulk active, saved pair reopened and checked | Current run manifest |
