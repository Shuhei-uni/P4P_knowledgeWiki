# E6 localized bottom radial-band pressure-outlet family

This family is a human-authorized Phase 07A discovery branch created on
2026-09-15. It prepares multiple named radial bands on the existing planar
bottom so later children can keep selected bands as walls and convert only the
declared bands to pressure outlets. The first spatial pattern opens the
outermost resolved band and retains the inner four bands as walls.

The bands are approximate mesh-supported radial bands on a square-annular
bottom, not exact circular CAD annuli. The reusable catalogue and its
readback requirements are in [design.md](design.md).

## Execution order

1. Run the disposable [mesh catalogue capability test](mesh-catalogue/setup.md).
2. Require five stable face zones, invariant mesh readback, and save/reopen
   proof before any solve.
3. Use the verified ringed child as the common parent for the three initial
   outer-band pressure settings.
4. Classify phase-resolved ring flux, vapor loss, liquid inventory, mass
   closure, junction behaviour, and numerical survivability before considering
   any continuation or different ring mask.

## Packets

- [family design and collision review](design.md)
- [mesh catalogue capability setup](mesh-catalogue/setup.md)
- [mesh catalogue capability results](mesh-catalogue/results.md)
- [outer-band pressure matrix](outer-ring-pressure-matrix.md)

Initial child packets:

- [P1120 setup](outer-ring-po-p1120/setup.md) / [results](outer-ring-po-p1120/results.md)
- [P1160 setup](outer-ring-po-p1160/setup.md) / [results](outer-ring-po-p1160/results.md)
- [P1200 setup](outer-ring-po-p1200/setup.md) / [results](outer-ring-po-p1200/results.md)

No packet has been placed on a Fluent server or executed. The active Phase
07A queue remains unchanged until the mesh capability result is available and
the human/phase-loop launch decision is recorded.
