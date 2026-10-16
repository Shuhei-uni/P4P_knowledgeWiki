# Server 6 — 223k setup

| Item | Value / status |
| --- | --- |
| Intended parent | Same verified Phase 9 N1580 startup basis as other mesh preparations |
| Transfer ordering | Original non-stripping A parent for native interpolation; selected Stage 4 and approved bulk settings applied afterwards |
| Target | `purnanto-separator(bottomrings)-223k.msh.h5`; 223,546 cells |
| Mesh hash | `546e034389b53070414e5b400859a90262e6b3cd6b689f3fe0850b33c675ab1c` |
| Bottom delta | Convert three pressure-outlet components to wall; merge all five bottom parts as `bottom` |
| Lower collector | Same physical y <= 0.10 m selection; 59,535 target cells |
| Scale | Native metre extents verified; no scale change |
| Feed | Human confirmed 25% low-feed startup |
| Fixed settings | Parent owns models, materials, sources, wall film, injections, methods and controls; comparison pending |
| Bulk initialization | None submitted |
| Startup authority | Human, 15 October 2026: review changed code, then start the run |
| Low-feed hold | 1,000 updates total at 25%, including 20-update smoke |
| Feed ramp | 2,000 updates; inlet changes every 10 updates |
| Full-feed hold | At least 2,000 updates; 1,000-update blocks; existing Phase 9 stability screen |
| Full-feed limit | 20,000 updates maximum |
| Bulk equations | All four active throughout startup |
| EWF step | Original Stage 4 startup fixed 0.1 µs |
| Replacement input | Mesh-only ASCII from intact HDF5 target; exact native topology, coordinates and boundary areas verified |
| Failed path | Binary legacy case writer disabled; incomplete old output excluded |
| Required finish | Full settings audit, paired reopen, bounded smoke, detached startup |
| Implementation | [Reviewed staged runner](../../../../PyAnsys/scripts/setup/prepare_phase9_server6_223k.py) |
