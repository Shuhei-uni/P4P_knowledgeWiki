> **Legacy source:** ResearchProject_wiki/wiki/progress/blockers.md  
> **Migration note:** These excerpts preserve the historical blocker record; no blocker status or interpretation has been rewritten. Raw and machine-generated artifacts remain at their legacy paths.

# Historical blocker notes

> **Legacy source:** ResearchProject_wiki/wiki/progress/blockers.md
> **Migration note:** Selected historical limitations are preserved without changing their status or interpretation.

### BLK-010 | IC1 brine-pipe VOF patch has no unambiguous cell-volume selection
- Status: Active — human selection required
- First observed: 2026-08-14
- Related run(s): `VOF-IC1-PATCH-PLATFORM-2026-08-14`
- Symptom: the coarse patch-test mesh has one combined fluid cell zone (`simple-spiral-separator--brine-outlet-`) and no pre-existing brine-pipe-only cell register. `brine-outlet` is a pressure-outlet face zone, so it cannot itself serve as a volume-fraction patch target for the complete pipe volume.
- Current interpretation: IC1 and independent IC2 plane-pool checkpoints at `+0.00 m` and visually approved `+0.30 m` have been patched and saved as coarse platform artifacts. IC2 now has a reproducible planned height matrix (`+0.00`, `+0.15`, `+0.30`, `+0.45`, `+0.60 m`). The unbuilt sensitivity levels still require marked-volume and initialized-liquid-mass recording before any transient interpretation.
- Recovery action: create each planned global-coordinate register, report its marked volume/cell count and corresponding initial liquid mass, then preserve the same timestep/monitor/averaging gates as IC0 before authorizing a solve.
