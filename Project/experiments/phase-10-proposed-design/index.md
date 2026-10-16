# Phase 10 — Proposed design improvements

| Design | Intended change | Retained endpoint | Records |
| --- | --- | --- | --- |
| Vertical slit / film blocker; 154,063 cells | Interrupt circulating wall liquid before it meets inlet steam | Basic EWF N44661 / 150 ms; N34661 / 50 ms and enhanced N84000 / 50.9 ms preserved | [Context](vertical-slit154k/CONTEXT.md), [setup](vertical-slit154k/setup.md), [results](vertical-slit154k/results.md), [state](vertical-slit154k/phase-state.yaml) |
| Angled slit / film ramp; 213,232 cells | Guide wall liquid towards lower collection | N43492 / 150 ms; N33492 / 50 ms preserved | [Context](angled-slit213k/CONTEXT.md), [setup](angled-slit213k/setup.md), [results](angled-slit213k/results.md), [state](angled-slit213k/phase-state.yaml) |

| Phase record | Purpose |
| --- | --- |
| [Context](CONTEXT.md) | Design question and scope |
| [Comparison setup](setup.md) | Comparison basis and control differences |
| [Comparison results](results.md) | Available observations and claim limits |
| [Phase state](phase-state.yaml) | Compact state and case pointers |
| [Vertical startup provenance](vertical-slit154k/startup-stage3/index.md) | Original Stage 3 startup and early film development |
| [Superseded angle plan](angled-slit213k/superseded-phase9-plan/CONTEXT.md) | Unexecuted former 100 ms plan; historical provenance only |

| Selected follow-up | Record |
| --- | --- |
| Completed vertical slit with angled basic EWF settings; N31000 → N34661 / 50.000 ms at 10 µs | [Setup](vertical-slit154k/basic-ewf-10us/setup.md), [results](vertical-slit154k/basic-ewf-10us/results.md), [state](vertical-slit154k/basic-ewf-10us/phase-state.yaml) |

| Current continuation | Record |
| --- | --- |
| Completed vertical basic EWF: 50 → 150 ms; 10,000 updates at 10 µs | [Selected setup](vertical-slit154k/basic-ewf-10us/setup.md), [current results](vertical-slit154k/basic-ewf-10us/results.md) |

| Selected angle continuation — 13 October 2026 | Record |
| --- | --- |
| Completed N33492 / 50 ms → N43492 / 150 ms; same angle settings, 10 µs | [Setup](angled-slit213k/setup.md), [results](angled-slit213k/results.md), [state](angled-slit213k/phase-state.yaml) |

| Current Server 5 campaign — 15 October 2026 | Record |
| --- | --- |
| Both slit designs: retained 150 ms → 500 ms, exact current Plan v1 settings; Server 5 only | [Setup and case states](server5-planv1-500ms.md) |
