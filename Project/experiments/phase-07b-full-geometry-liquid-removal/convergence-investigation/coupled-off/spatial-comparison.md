# E4 native spatial comparison

Status: COMPLETE_NATIVE_EXPORTS_QA_PASS. Nine native images inspected; E4 final N5000 restored after export, with zero solve iterations.

Question: Does the Coupled/Off treatment redistribute liquid and reduce inlet-region velocity excursions relative to the same-initial-field SIMPLE control?

Sources: E4 `p7b-s40-t020-coupled-off-20260922T134224Z`, E3 `p7b-s40-t020-diag-resume-20260922T122811Z`, and original T020 `p7b-s40-t020-resume-20260921T231240Z`, each preserved final N5000 pair. All are finite discovery endpoints, unqualified.

Geometry: common full 620,431-cell separator, Cartesian metres. Hotspot horizontal plane y=2.4272831100788324 m, liquid VOF and mixture speed; full-height axial x=0 m, liquid VOF. Native original initial/final horizontal and axial arrays remain required evidence separately.

Comparison: fixed VOF 0–1, shared speed limits discovered from the union of all three native horizontal plane ranges and rounded outward. No clipping, facet values, contour only, identical orthographic cameras as G3. Horizontal target (0.3,y,−1), −y viewing direction, −z up, field 1.0 by 0.8 m; axial target (0,2.755,0), −x viewing direction, +y up, field 6 by 10.2 m. Native exports at 2400 by 1800 / 1600 by 2400 pixels.

Claim limit: terminal matched spatial differences do not locate unsaved peaks or demonstrate conservation, steady convergence or unique causation. Restore the preserved E4 N5000 endpoint after export, with no solving or source-pair overwrite.

## Observations and artifacts

The shared speed range is 0–80 m/s; VOF is 0–1. At the historical inlet-upper plane, E4 has less liquid along the displayed curved band and lower displayed speeds than original/E3. The full-height x=0 cuts retain liquid near walls in both, with less visible interior liquid in E4. These endpoint observations agree with the inventory difference; they do not prove physically correct separation or locate all maximum-speed cells. Original and E3 scenes visually agree.

![E4 inlet-upper liquid](../../../../../PyAnsys/output/phase07b-g4/native-figures/COUPLED-N5000-hot-liquid.png)

![SIMPLE inlet-upper liquid](../../../../../PyAnsys/output/phase07b-g4/native-figures/ORIGINAL-N5000-hot-liquid.png)

The [native figure manifest](../../../../../PyAnsys/output/phase07b-g4/native-graphics-manifest.json) owns exact pairs, observed ranges, cameras, hashes and all nine files, including speed and full-height axial contours. The exporter's original manifest is retained with its pre-visual-QA status.
