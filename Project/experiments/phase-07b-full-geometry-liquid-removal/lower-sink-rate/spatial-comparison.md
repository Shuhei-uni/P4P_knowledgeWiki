# G2 — Native Fluent spatial comparison

All panels show original saved **N5000 finite discovery endpoints** on the
same 620,431-cell geometry. They do not demonstrate convergence or physical
separation performance. Initial and final native field arrays are preserved
in each run; initial liquid fraction is zero and no pool was patched.

Each panel is an unchanged Fluent contour export. The [figure manifest](../../../../PyAnsys/output/phase07b-g2/native-graphics-manifest.json)
records the exact case/data pair, plane definition, live surface range,
fixed displayed range, camera readback, resolution, remote/local SHA256 and
visual QA. Phase-2 is liquid. Scalar facets are used without node averaging;
no vector overlay is present. Colours are linear sequential viridis, with
VOF **0–1** and mixture speed **0–120 m/s** in every corresponding panel.
The speed limit rounds outward from the joint horizontal-surface maximum
115.59 m/s; no displayed surface value is clipped. It is not the whole-volume
maximum or a bound on the earlier iteration spikes.

Horizontal views look along −y, with −z upward. Full-height centre cuts look
along −x or −z, with +y upward. All are orthographic and use identical cameras
for a given plane: horizontal 2400×1800 pixels, axial 1600×2400 pixels.
The four horizontal cuts are above the fixed S40 collector top at y≈−0.883 m;
they do not measure collector inventory. The axial cuts include the lower region.

## Liquid distribution at four heights

| Plane | S40 baseline | S40-T020 | S40-T100 |
| --- | --- | --- | --- |
| y = 0.5 m | ![S40 baseline, N5000, y0p5, phase-2-vof](../../../../PyAnsys/output/phase07b-g2/native-figures-v3/S40-N5000-y0p5-liquid.png) | ![S40-T020, N5000, y0p5, phase-2-vof](../../../../PyAnsys/output/phase07b-g2/native-figures-v3/T020-N5000-y0p5-liquid.png) | ![S40-T100, N5000, y0p5, phase-2-vof](../../../../PyAnsys/output/phase07b-g2/native-figures-v3/T100-N5000-y0p5-liquid.png) |
| y = 1.5 m | ![S40 baseline, N5000, y1p5, phase-2-vof](../../../../PyAnsys/output/phase07b-g2/native-figures-v3/S40-N5000-y1p5-liquid.png) | ![S40-T020, N5000, y1p5, phase-2-vof](../../../../PyAnsys/output/phase07b-g2/native-figures-v3/T020-N5000-y1p5-liquid.png) | ![S40-T100, N5000, y1p5, phase-2-vof](../../../../PyAnsys/output/phase07b-g2/native-figures-v3/T100-N5000-y1p5-liquid.png) |
| y = 3 m | ![S40 baseline, N5000, y3p0, phase-2-vof](../../../../PyAnsys/output/phase07b-g2/native-figures-v3/S40-N5000-y3p0-liquid.png) | ![S40-T020, N5000, y3p0, phase-2-vof](../../../../PyAnsys/output/phase07b-g2/native-figures-v3/T020-N5000-y3p0-liquid.png) | ![S40-T100, N5000, y3p0, phase-2-vof](../../../../PyAnsys/output/phase07b-g2/native-figures-v3/T100-N5000-y3p0-liquid.png) |
| y = 5 m | ![S40 baseline, N5000, y5p0, phase-2-vof](../../../../PyAnsys/output/phase07b-g2/native-figures-v3/S40-N5000-y5p0-liquid.png) | ![S40-T020, N5000, y5p0, phase-2-vof](../../../../PyAnsys/output/phase07b-g2/native-figures-v3/T020-N5000-y5p0-liquid.png) | ![S40-T100, N5000, y5p0, phase-2-vof](../../../../PyAnsys/output/phase07b-g2/native-figures-v3/T100-N5000-y5p0-liquid.png) |

At all four heights, liquid concentrates in a narrow outer-wall band while
most of the annular interior has low liquid fraction. The upper cuts at
3 and 5 m retain more broadly distributed wall liquid. Wall asymmetry and
band thickness vary; no monotonic tau trend is established by these snapshots.

## Mixture speed at the same heights

| Plane | S40 baseline | S40-T020 | S40-T100 |
| --- | --- | --- | --- |
| y = 0.5 m | ![S40 baseline, N5000, y0p5, velocity-magnitude](../../../../PyAnsys/output/phase07b-g2/native-figures-v3/S40-N5000-y0p5-speed.png) | ![S40-T020, N5000, y0p5, velocity-magnitude](../../../../PyAnsys/output/phase07b-g2/native-figures-v3/T020-N5000-y0p5-speed.png) | ![S40-T100, N5000, y0p5, velocity-magnitude](../../../../PyAnsys/output/phase07b-g2/native-figures-v3/T100-N5000-y0p5-speed.png) |
| y = 1.5 m | ![S40 baseline, N5000, y1p5, velocity-magnitude](../../../../PyAnsys/output/phase07b-g2/native-figures-v3/S40-N5000-y1p5-speed.png) | ![S40-T020, N5000, y1p5, velocity-magnitude](../../../../PyAnsys/output/phase07b-g2/native-figures-v3/T020-N5000-y1p5-speed.png) | ![S40-T100, N5000, y1p5, velocity-magnitude](../../../../PyAnsys/output/phase07b-g2/native-figures-v3/T100-N5000-y1p5-speed.png) |
| y = 3 m | ![S40 baseline, N5000, y3p0, velocity-magnitude](../../../../PyAnsys/output/phase07b-g2/native-figures-v3/S40-N5000-y3p0-speed.png) | ![S40-T020, N5000, y3p0, velocity-magnitude](../../../../PyAnsys/output/phase07b-g2/native-figures-v3/T020-N5000-y3p0-speed.png) | ![S40-T100, N5000, y3p0, velocity-magnitude](../../../../PyAnsys/output/phase07b-g2/native-figures-v3/T100-N5000-y3p0-speed.png) |
| y = 5 m | ![S40 baseline, N5000, y5p0, velocity-magnitude](../../../../PyAnsys/output/phase07b-g2/native-figures-v3/S40-N5000-y5p0-speed.png) | ![S40-T020, N5000, y5p0, velocity-magnitude](../../../../PyAnsys/output/phase07b-g2/native-figures-v3/T020-N5000-y5p0-speed.png) | ![S40-T100, N5000, y5p0, velocity-magnitude](../../../../PyAnsys/output/phase07b-g2/native-figures-v3/T100-N5000-y5p0-speed.png) |

The strongest displayed speed patch occurs near the outer wall of T020 at
y=1.5 m. T100 has a lower speed range at that endpoint, but its histories still
contain severe earlier excursions. Endpoint colour differences cannot identify
the location or initiator of the earlier residual spikes.

## Full-height liquid centre cuts

| Plane | S40 baseline | S40-T020 | S40-T100 |
| --- | --- | --- | --- |
| x = 0 m | ![S40 baseline, N5000, x0, phase-2-vof](../../../../PyAnsys/output/phase07b-g2/native-axial-label-repair/S40-N5000-x0-liquid.png) | ![S40-T020, N5000, x0, phase-2-vof](../../../../PyAnsys/output/phase07b-g2/native-axial-label-repair/T020-N5000-x0-liquid.png) | ![S40-T100, N5000, x0, phase-2-vof](../../../../PyAnsys/output/phase07b-g2/native-axial-label-repair/T100-N5000-x0-liquid.png) |
| z = 0 m | ![S40 baseline, N5000, z0, phase-2-vof](../../../../PyAnsys/output/phase07b-g2/native-axial-label-repair/S40-N5000-z0-liquid.png) | ![S40-T020, N5000, z0, phase-2-vof](../../../../PyAnsys/output/phase07b-g2/native-axial-label-repair/T020-N5000-z0-liquid.png) | ![S40-T100, N5000, z0, phase-2-vof](../../../../PyAnsys/output/phase07b-g2/native-axial-label-repair/T100-N5000-z0-liquid.png) |

The centre cuts retain wall-concentrated liquid over much of the height,
with localized lower-region liquid. The weakest sink retains more collector
liquid in the integrated records; these cuts are spatial context, not a
standing-pool or steady-state qualification. See [G2 results](results.md) for
inventory, source-inclusive conservation, residuals and the bounded decision.
