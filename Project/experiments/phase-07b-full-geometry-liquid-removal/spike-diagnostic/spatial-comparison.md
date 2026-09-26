# G3 — native Fluent hotspot and vessel context

These are saved finite discovery states, not converged solutions. The original
and diagnostic N5000 fields reproduce; N4500 provides earlier context. The
[figure manifest with completed visual QA](../../../../PyAnsys/output/phase07b-g3/native-graphics-manifest.json)
records each explicit paired source, live iteration, surface, observed range,
camera, display state and matching remote/local image hash. Images are native
Fluent exports with unchanged scientific pixels.

The horizontal plane is **y=2.4272831100788324 m**, through the N4328
maximum-speed cell, near the other sampled event elevations and just below
the inlet upper edge. The camera focuses on the local x/z region with target
(0.3, y, −1.0) m, orthographic field 1.0×0.8 m, looking along −y with −z up.
The collector is far below this cut, ending at y=−0.882750 m.

All liquid panels use phase-2 VOF 0–1. All speed panels use mixture speed
0–80 m/s, rounded outward from the union of live surface ranges on these
three checkpoints; no displayed surface value is clipped. This range is not
a bound on whole-volume speeds or earlier spikes. Contours use native facet
values without node averaging or vectors, and identical cameras and linear
viridis scales between sources. Horizontal exports are 2400×1800; full-height
x=0 cuts are 1600×2400. Native source labels use `d` for diagnostic, `o` for
original, then iteration; `h` is the hotspot cut, `x` the full-height cut,
`vf` liquid fraction and `u` mixture speed.

## Saved-state hotspot region

| Field | Original N5000 | Diagnostic N4500 | Diagnostic N5000 |
| --- | --- | --- | --- |
| Liquid fraction | ![Original N5000 hotspot liquid](../../../../PyAnsys/output/phase07b-g3/native-figures-final/ORIGINAL-N5000-hot-liquid.png) | ![Diagnostic N4500 hotspot liquid](../../../../PyAnsys/output/phase07b-g3/native-figures-final/DIAG-N4500-hot-liquid.png) | ![Diagnostic N5000 hotspot liquid](../../../../PyAnsys/output/phase07b-g3/native-figures-final/DIAG-N5000-hot-liquid.png) |
| Mixture speed | ![Original N5000 hotspot speed](../../../../PyAnsys/output/phase07b-g3/native-figures-final/ORIGINAL-N5000-hot-speed.png) | ![Diagnostic N4500 hotspot speed](../../../../PyAnsys/output/phase07b-g3/native-figures-final/DIAG-N4500-hot-speed.png) | ![Diagnostic N5000 hotspot speed](../../../../PyAnsys/output/phase07b-g3/native-figures-final/DIAG-N5000-hot-speed.png) |

At N5000 a thin high-liquid-fraction band follows the curved structure,
with a broader speed distribution nearby. Facet-scale variation is visible;
these images do not establish defective cells or identify which equation
initiated the spikes. N4500 and N5000 bracket the N4763/N4764/N4768 captures
and the uncaptured N4767 peak. **None of these images depicts an event peak.**
Exact sampled-event values and locations come from the whole-cell arrays in
[results](results.md), not from interpreting the colours as event values.

## Full-height liquid context

| Original N5000, x=0 | Diagnostic N5000, x=0 |
| --- | --- |
| ![Original full-height liquid](../../../../PyAnsys/output/phase07b-g3/native-figures-final/ORIGINAL-N5000-axial-liquid.png) | ![Diagnostic full-height liquid](../../../../PyAnsys/output/phase07b-g3/native-figures-final/DIAG-N5000-axial-liquid.png) |

The matched centre cuts show wall-concentrated liquid and localized lower
liquid. They provide full-vessel context, not a steady pool or qualified phase
routing. Initial and final native arrays on four horizontal and two full-height
cuts are retained and [independently checked](../../../../PyAnsys/output/phase07b-g3/section-field-audit.json).
No liquid was patched at initialization. The numerical conservation and
stationarity failures govern the claim limits despite visually structured fields.

Export recovery changed only temporary graphics names: Fluent lowercases new
iso-surface names, and long object names were shortened to avoid truncated
source labels. All eight final images are native re-exports. The final E3
N5000 checkpoint is restored after postprocessing, with no extra iterations.
