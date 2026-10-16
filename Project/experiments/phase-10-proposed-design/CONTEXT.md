# Phase 10 — Proposed design contract

| Current authority — 15 October 2026 | Selected scope |
| --- | --- |
| Server | 5 only from now; no other server queries or control |
| Goal | Continue both retained 150 ms slit cases to 500 ms with current Phase 9 EWF Plan v1 |
| Selected implementation | [Server 5 campaign](server5-planv1-500ms.md); vertical then angled; preserve all source endpoints |

| Item | Current scope |
| --- | --- |
| Authority | Human, 12 October 2026: group vertical and angled slit records under Phase 10; assess proposed design changes |
| Question | Do the blocker and ramp change liquid routing, inlet interaction, liquid carried through the steam outlet, or pressure loss? |
| Vertical concept | Block circulating wall liquid before it meets incoming steam |
| Angled concept | Redirect wall liquid towards lower collection |
| Selected evidence | Completed basic-EWF vertical N34661 / 50.000 ms and angle N33492 / 50.000 ms; enhanced vertical N84000 / 50.9 ms preserved |
| Current activity | Both basic-EWF designs complete at 150 ms: vertical N44661, angled N43492; both 50 ms endpoints retained |
| New run authority | Human follow-up, 12 October: [vertical slit with angled EWF settings at 10 µs](vertical-slit154k/basic-ewf-10us/setup.md), to the same 50 ms endpoint |
| Comparison limit | Basic EWF and main 10 µs step now matched; mesh, initial fields, earlier film history and parent film age differ |
| Interpretation | Track liquid destination and pressure loss together; lower film storage alone does not prove better separation |
| Records | [Setup](setup.md), [results](results.md), [case navigation](index.md) |
| Provenance | Original Phase 7.2A startup and Phase 9 continuation remain labelled within the design folders; machine evidence retains its original PyAnsys paths |

| Additional run authority — 13 October 2026 | Selected scope |
| --- | --- |
| Human request | Another 100 ms on the current vertical basic-EWF case |
| Horizon | N34661 / 50 ms → N44661 / 150 ms; 10,000 fixed 10 µs updates |
| Scope | Same EWF and frozen bulk; Server 6 vertical branch only; no numerical thresholds |

| Latest result — 13 October 2026 | Evidence |
| --- | --- |
| Vertical continuation | N44661 / 150 ms saved/reopened and OneDrive hashes verified; 50 ms pair retained |
| Current activity | Compare existing records; both 150 ms runs complete; no further solve selected |

| Completed angle follow-up — 13 October 2026 | Evidence |
| --- | --- |
| Angle endpoint | N43492 / 150 ms; paired reopen and OneDrive hashes verified |
| Current run authority | Complete; no further updates or new case selected |
