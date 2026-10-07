# Stage 2 — revised stepped startup results

| Item | Result |
| --- | --- |
| Status | Floating-point failure at native N518; incomplete 2,200-iteration trial |
| OFF segment | N0–N200 at 25% feed completed; paired N200 checkpoint preserved |
| Activation | Absorber enabled at N200; pre/post-enable pairs preserved |
| ON segment | N200–N518 at 25% feed; target N700 not reached |
| Ramp | Not reached |
| Failed endpoint | Paired N518 diagnostic-only save, hashes verified before loading 08b |
| Previous run | Cortex shutdown after printed N350; N300 save/reopen verified; distinct failure type |
| Current selection | [Original 08b mesh transfer](../08b-native997k/setup.md); no resumption of this failed trial |
| Claim limit | This startup failed with absorber active; it does not establish that absorber-OFF operation is numerically impossible |

| Evidence | Record |
| --- | --- |
| Protocol | [Setup](setup.md) |
| Native failure and paired saves | [Recovered terminal manifest](../../../../../PyAnsys/output/phase8-stage2/20261007/step-enable2200/recovered-third-failure-run-manifest.json) |
| Native transcript | [Recovered transcript](../../../../../PyAnsys/output/phase8-stage2/20261007/step-enable2200/raw/recovered-third-failure-native-transcript.txt) |
| Budget | 2,200 total requested; prior unrun 2,450-step preparation superseded |
