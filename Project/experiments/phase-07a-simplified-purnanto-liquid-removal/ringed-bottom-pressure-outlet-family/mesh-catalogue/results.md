# E6 mesh catalogue capability results

## Status

`NOT_RUN` — no Fluent mutation has been performed.

## Required evidence before promotion

Record the disposable child identity, Fluent/PyFluent fingerprint, exact
separation method, requested versus observed region/register bounds, resulting
face-zone names, per-zone face counts and areas, plane/adjacency checks, global
mesh invariants, mesh-check result, and pre-save/post-reopen type readback.

The capability result must state one of:

- `PASS_FACE_CATALOGUE`: five stable ring zones and the disposable pressure-
  outlet conversion survive save/reopen; or
- `BLOCK_FACE_CATALOGUE`: the requested topology cannot be implemented or
  proven safely on the supplied mesh.
