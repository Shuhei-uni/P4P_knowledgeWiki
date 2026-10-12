# Steady drainage-boundary verification (Andy)

Authorized by Andy on 30 September 2026: “Sounds good. do that”, accepting the drainage-boundary proposal. This unnumbered diagnostic is separate from closed Phase 9 and Phase 7b. Use only Andy server1 after preserving its N2000 endpoint. Restore that endpoint after tests. Never use Shuhei sessions.

Question: does a passive outlet-vent resistance produce the expected conservative steady head-to-flow relation? This is an idealized implementation test, not calibration or separator qualification.

Use a fresh 3D 1 m long, 0.5×0.5 m straight duct with symmetry sides, single incompressible liquid (881.77 kg/m³), laminar, steady, gravity off. With uniform slip flow there is no wall-friction loss; inlet total pressure minus downstream static ambient equals (1+K) rho U²/2. K=0 and K=9 are declared synthetic controls; total pressure differences 200 and 800 Pa. No value is fitted to Phase 9. Pressure drives flow; no discharge is imposed.

Four cases max, 500 iterations each, 2000 total or two solver-hours including retries. Fresh initialization and case/data save-reopen setup readback for every case. Require final100 history: relative closure<=0.1%, all active residuals<=1e-6, flow/pressure variation<=0.1%, predicted flow agreement<=2%, monotonic response. Stop on nonfinite fields, speed>20m/s or deadline. Preserve every failed endpoint. No VOF separator run is authorized by this diagnostic; propose its contract after review. No new geometry of the separator is authorized or required here.
