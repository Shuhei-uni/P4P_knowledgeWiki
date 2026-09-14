# Phase 06 figure package

Status: **blocked pending recovery of the exact Phase 06 late checkpoint**.

The requested spatial figure is the lower-region pool-control scene: a
phase-2 volume-fraction contour on the centre cuts, with a separate native
Fluent vector-only view if the flow field is useful. The source must be the
paired late state from the long-horizon surrogate:

```text
C:\Users\syok443\Documents\FluentRuns\P6\S6\long-hypothesis-server2-20260831T004750Z\checkpoints\checkpoint-chunk-100.cas.h5
C:\Users\syok443\Documents\FluentRuns\P6\S6\long-hypothesis-server2-20260831T004750Z\checkpoints\checkpoint-chunk-100.dat.h5
```

That endpoint is on server2, which is offline. Read-only checks on the
connected student, server1, and server3 hosts did not find the exact paired
checkpoint, and the local project tree does not contain a copy of the P6
checkpoint. No substitute Phase 05 or earlier state is being used: it would
not support the Phase 06 late-control claim.

The quantitative Phase 06 plots remain usable for the meeting narrative. The
new spatial figure should be generated only after the exact pair is
recoverable. Because the experiment did not record a patch operation for this
checkpoint, there is no additional post-patch figure requirement for this
specific state.
