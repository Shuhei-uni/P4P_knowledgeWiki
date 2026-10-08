# Conservative bulk-active hold: N13000 → N17000

| Contract | Setting / purpose |
| --- | --- |
| Authority | Human-approved phase scope; user resumes work, 8 October 2026. Continue the bulk-response test because the final collector/removal and outlet still trend |
| Question | Does the bulk response settle enough to freeze bulk for later film development? |
| Parent | Verified N13000 case/data from the [completed 4,000-iteration hold](../bulk-hold-4000/results.md); exact local Server 1 paths and SHA-256 in the machine manifest |
| Parent film clock | 0.005642000000000347 s |
| Reason for continuation | Final 500: bulk liquid +0.54%, contact removal −11.4%, outward outlet liquid +4.57%; do not freeze bulk |
| Controlled change | Extend the fixed-input hold by 4,000 bulk iterations; add native paired autosaves every 1,000 iterations |
| Bulk equations | Active throughout this command; no automatic bulk freeze |
| Film numerics | Fixed 1 µs; full film momentum; retained alternative implicit/coupled solution, first-order schemes, 30 inner iterations and 10⁻⁵ stopping value |
| Film physics | EWF, Phase Accretion, DPM collection/splashing, stripping and separation ON; retained force terms; Flow Momentum Coupling OFF |
| Drain | Retained direct lower-wall mass and matched momentum sinks, τ = 1.5 ms; frozen-bulk removal already proved for this setup |
| Fixed inputs | Mesh, materials, inlet feed, roughness, bulk collector, DPM cadence, film/source definitions and parent fields |
| Initialization | None |
| Run | One native `/solve/iterate 4000`; target N17000; expected +4 ms film time if one accepted 1 µs film step continues per bulk iteration |
| Checkpoints | Native case and data autosaves every 1,000 iterations; Server 1 local `FluentRuns` disk |
| Terminal output | Final N17000 case/data, complete native transcript, report files, residual XY and returned marker |
| Execution ownership | Fluent reads the uploaded journal; the laptop/Python connection is not required after submission; Fluent remains open |
| Observation | Passive native transcript/residual streams during solving; no Scheme status queries during the journal |
| Numeric rejection | Courant ≥1, film thickness ≥0.3 m, non-finite reports or fatal solver error; preserve endpoint and reject further continuation |
| Claim limit | Bulk-response and film-development diagnostic; no steady-film, physical-validation or mesh-convergence claim |
| Machine owner | [Manifest](../../../../../../PyAnsys/output/phase72a-stage4-replacement/20261008/run-manifest.json) |

| Required evidence after the command | Decision use |
| --- | --- |
| Native residual plot | Assess bounded behaviour and late trends over the full hold |
| Bulk and film inventory plots | Compare total bulk, lower collector and total/upper/lower film liquid; use native iteration and accepted film clock |
| Absorber and outlet traces | Keep direct film drain, bulk contact removal and actual outlet boundary flux separate from source-inclusive reports |
| Last two 500-iteration windows | Compare mean values and within-window slopes; persistent bulk inventory, collector/removal or outlet trends favour keeping bulk active |
| Freeze conditions | Bulk evidence supports a stationary flow, numerical fields remain bounded, and existing frozen-bulk direct-drain proof remains applicable |
| Film ledger | Retain original source accounting; unresolved DPM event mass and missing achieved inner residuals limit accuracy claims |
