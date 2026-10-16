# Server 3 — verified 997k EWF endpoint

| Check | Result | Evidence |
| --- | --- | --- |
| Status | Complete: 997,604-cell EWF Plan v1 numerical schedule; 42,820 new native iterations | [Run manifest](../../../../PyAnsys/output/phase9-ewf-server3-997k/20261010/run-manifest.json) |
| Parent and preparation | Selected N8080 / 0.650 ms pair; source hashes matched; initial fields preserved; settings saved and reopened | [Settings receipt](../../../../PyAnsys/output/phase9-ewf-server3-997k/20261010/997k-ewf-settings-current.json) |
| Previous loaded case | Idle N9380 pair preserved before replacement | [Preservation receipt](../../../../PyAnsys/output/phase9-ewf-server3-997k/20261010/preserved-before-replacement.json) |
| Final endpoint | N50900 / 200.000 ms; final 195–200 ms stage has all four bulk equations active; 1,000 accepted updates at 5 µs | [Final reopen proof](../../../../PyAnsys/output/phase9-ewf-server3-997k/20261010/final-reopen.json) |
| Final pair | Case/data hashed and reopened; persistent fields, setup, methods, feed, drain, native iteration and film clock verified | [Final reopen proof](../../../../PyAnsys/output/phase9-ewf-server3-997k/20261010/final-reopen.json) |
| Stage checkpoints | All ten case/data pairs rehashed at closure against their recorded SHA256 values | [Checkpoint hashes](../../../../PyAnsys/output/phase9-ewf-server3-997k/20261010/final-checkpoint-hashes.json) |
| Report histories | All 34 final report files contain consecutive native coordinates through N50900 with finite values | [History checks](../../../../PyAnsys/output/phase9-ewf-server3-997k/20261010/final-report-history-checks.json) |
| Selected shared pairs | End-bulk N9580 / 0.800 ms, frozen N49900 / 195 ms, and final N50900 / 200 ms are together in the host OneDrive artifact folder. Case/data hashes verified for all copies; cloud sync not independently queried | [Additional stage copies](../../../../PyAnsys/output/phase9-ewf-server3-997k/20261010/selected-stage-shared-copies.json), [final pair](../../../../PyAnsys/output/phase9-ewf-server3-997k/20261010/final-shared-copy.json) |
| Supervision and Fluent | Watcher stopped and disabled after completion. No further iteration command queued. Fluent preserved with final pair loaded | [Supervision receipt](../../../../PyAnsys/output/phase9-ewf-server3-997k/20261010/continuous-supervision.json) |
| Numerical limit policy | Operating threshold gates disabled by human direction on 12 October; Courant retained as diagnostic only | [Setup](setup.md) |
| Drain and claim limits | Same-parent direct-removal proof retained; full production mass closure, steady film and physical validation are not established | [Identity proof](../../../../PyAnsys/output/phase9-ewf-server3-997k/20261010/same-parent-controls-proof.json) |

| Completed stage | Bulk equations | New iterations | Native endpoint | Film age (ms) |
| --- | --- | ---: | ---: | ---: |
| bulk-adjustment | Active | 1,500 | 9,580 | 0.800 |
| frozen-transition | Frozen | 1,000 | 10,580 | 0.900 |
| step-2p5us | Frozen | 1,000 | 11,580 | 3.400 |
| step-5us | Frozen | 1,000 | 12,580 | 8.400 |
| growth-5000 | Frozen | 5,000 | 17,580 | 33.400 |
| growth-10000-a | Frozen | 10,000 | 27,580 | 83.400 |
| growth-10000-b | Frozen | 10,000 | 37,580 | 133.400 |
| growth-10000-c | Frozen | 10,000 | 47,580 | 183.400 |
| growth-to-195ms | Frozen | 2,320 | 49,900 | 195.000 |
| bulk-reactivation-to-200ms | Active | 1,000 | 50,900 | 200.000 |

| Shared milestone | Native iteration | Film age (ms) | Saved bulk state | Case/data filename stem |
| --- | ---: | ---: | --- | --- |
| End of bulk adjustment, immediately before freeze | 9,580 | 0.800 | Active | `997k-ewf-end-bulk-N9580` |
| End of frozen film development | 49,900 | 195.000 | Frozen | `997k-ewf-195ms-N49900` |
| Final endpoint | 50,900 | 200.000 | Active | `997k-ewf-final-N50900` |
