# Stage 2 — 08b settings on new 997k, absorber OFF

| Item | Run contract |
| --- | --- |
| Authority | Shuhei, 7 October 2026: run this case for 2,000 iterations without absorber; confirmed 08b settings with new mesh |
| Parent | [Verified native 08b transfer](../results.md); paired N10000 start |
| Mesh | Supplied 997,604-cell mesh; original 7,601,261-cell mesh replaced |
| Session | Server 2 only; attach; no Fluent restart, exit or termination |
| Start | Continue archived 08b fields interpolated onto new mesh; no initialization |
| Horizon | 2,000 additional carrier iterations; N10000 to N12000 |
| Batches | 1,000 to N11000; save; 1,000 to N12000; save/reopen |
| Absorber | OFF throughout; no lower absorber cell partition; all phase/mixture cell sources OFF |
| Carrier | Original 08b steady Mixture/RNG; SIMPLE, pseudo time OFF |
| Schemes | First-order k; second-order momentum/epsilon; PRESTO pressure; QUICK volume fraction; original remaining controls |
| Feed | Original 08b rates: liquid 116.92 kg/s, vapor 80.69 kg/s; no ramp |
| DPM | Original six injection definitions retained; feedback OFF |
| Allowed execution changes | Native reports/iteration expression; residual history and convergence-stop checks; local autosave/output paths |
| Reports | 17 file-backed reports every 10 iterations: 9 phase/mixture inlet/outlet fluxes, 2 inventories, 2 liquid-fraction extrema, maximum speed, 3 mean boundary pressures |
| Checkpoints | Paired autosave every 100 iterations, manual N11000 and N12000; Windows local disk |
| Stop | Requested N12000, solver failure or lost session; no further trial or automatic restart |
| Evidence | Paired identities/readback; native transcript/residuals; complete histories; terminal inventories and extrema |
| Claim limit | Stability of this transferred parent/setup/startup; no mesh independence, physical validation or universal impossibility claim |

| Machine record | Location |
| --- | --- |
| Prepared pair and settings | [Build](../../../../../../PyAnsys/output/phase8-stage2/20261007/08b-native997k/run2000-off/build.json) |
| Preparation transcript | [Native transcript](../../../../../../PyAnsys/output/phase8-stage2/20261007/08b-native997k/run2000-off/raw/preparation-native.txt) |
