# vertical-slit154k — Plan v1 continuation

| Input / control | Selected value |
| --- | --- |
| Authority | Human, 15 October 2026; [Server 5 campaign](../../server5-planv1-500ms.md) |
| Server | 5 only |
| Mesh | 154063 cells |
| Parent | Hash-verified N44661 / 150 ms OneDrive case/data |
| Physics and stages | Current Phase 9 EWF Plan v1; sequential original implicit EWF; lower numerical film drain; 0.045 mm roughness; [full settings](../../server5-planv1-500ms.md) |
| Horizon | N187130 / 500 ms after numerical recovery; recalculate only from verified checkpoint if technical recovery changes counts |
| New updates | 142400 originally planned; recovery preserves 10 accepted updates and submits 142459 further updates from N44671 |
| Numerical recovery | FPE at N45047; restore verified N44671. Remaining bulk adjustment at 0.01 µs; frozen 0.1 µs transition aligned before main 2.5 µs stage. Same physics. See campaign recovery table |
| Bulk numerical retry | Restore N44681 after stopped FPE; bulk pseudo-time scale 1.0 → 0.1 for remaining bulk-active adjustment at 0.01 µs film step. Restore scale to 1.0 at freeze; save/reopen at changes |
| Final bulk state | Frozen; no final bulk-active extension |
| Source preservation | Retain source 150 ms pair and upper-film fields; newly allocated lower wall starts at zero film |
| Evidence | Local transcripts, paired saves/hashes/reopen, full settings readback, frozen direct-drain proof, selected shared pairs |
| Claim limit | Earlier 150 ms history retained; no geometry-only or fully coupled steady separator claim |
