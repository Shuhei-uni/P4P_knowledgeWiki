> **Retired source:** ResearchProject_wiki/wiki/progress/blockers.md
> **Migration note:** These excerpts preserve the historical blocker record; no blocker status or interpretation has been rewritten. Machine-generated artifacts remain with their original external owners; the retired written source is recoverable from Git history.

# Historical blocker notes

> **Retired source:** ResearchProject_wiki/wiki/progress/blockers.md
> **Migration note:** Selected historical limitations are preserved without changing their status or interpretation.

### BLK-008 | Setup 08b DPM result is dominated by incomplete tracks
- Status: Accepted scope limitation; not blocking
- First observed: 2026-07-02
- Related run(s): `PURNANTO-08B-POSTPROCESS-2026-07-02`
- Symptom: the refreshed live `08b` aggregate DPM summary reports `13012` incomplete particles and only `8` escaped particles for the current active 6-bin subset, with no trapped row printed in the summary output. The follow-up one-injection-at-a-time `dpm-sample` pass reproduces the same aggregate split and shows the completed sampled escape only in `injection-5-micron`, while the other active sampled bins remain fully incomplete.
- Current interpretation: incomplete tracks remain raw diagnostic context, but are not a project blocker or acceptance gate. Report-facing interpretation is limited to observed escape through `steamoutlet`.

### BLK-009 | Setup 08b steam-line carryover result is not backed by a closed whole-domain mass balance
- Status: Accepted scope limitation; not blocking
- First observed: 2026-07-02
- Related run(s): `PURNANTO-08B-POSTPROCESS-2026-07-02`
- Symptom: the live `08b` phase-flux post-processing gives steam-outlet liquid carryover `0.082132007 kg/s`, but the same report also shows a mixture imbalance of `116.063719 kg/s`, much larger than the steam-line carryover signal.
- Current interpretation: the simplified Purnanto geometry has no modelled lower-liquid discharge path, so whole-domain liquid/mixture imbalance is expected within scope and is informational only. Steam-outlet carryover remains a scoped outlet measure, not a closed whole-separator balance claim.
