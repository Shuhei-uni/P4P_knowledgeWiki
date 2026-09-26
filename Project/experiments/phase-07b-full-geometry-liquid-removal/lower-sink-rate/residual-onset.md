# S40-T020 residual spikiness near N2700

**Terminal follow-up:** [G2 results](results.md#residual-spike-observation) now includes both N5000 weaker-sink dispositions and the baseline comparison. The N4500 analysis below remains the evidence for the original observation.

**Andy observed that the residuals looked more spiky after roughly N2700.**
The recorded histories support this, most clearly for epsilon. The other
equations develop larger, broader oscillations; they do not all develop the
same sharp spikes. This is a partial diagnostic through N4500, made while the
single approved controller continues toward N5000 with unchanged settings.

## What the histories show

![Raw residuals and maximum speed through N4500](../../../../PyAnsys/output/p7b-s40-t020-resume-20260921T231240Z/diagnostics/residual-onset-n04500/residuals-and-speed.png)

The dashed line marks Andy's approximate observation, not a statistically
identified change point. All curves are raw; the view begins at N1800 to
separate the behaviour from initialization. The native maximum mixture speed
briefly reaches 236.7 m/s at N2692. At N2821, epsilon reaches 0.12206 and the
maximum speed reaches 443.1 m/s on the same iteration. Further shared bursts
include N3786 (epsilon 0.17019; speed 661.9 m/s), N4124 (0.45891; 632.2 m/s)
and N4328 (0.19305; 819.0 m/s). The largest epsilon excursion in N2001–4500
is 1.008 at N4140, within two iterations of a 418.3 m/s speed excursion.
These are numerical field extrema, not credible physical operating speeds.

| Descriptive window | Epsilon peak | Adjacent epsilon changes greater than a factor of 1.5, either direction | Mean vessel liquid, kg | Mean native removal, kg/s | Mean viscosity-limited cells |
| --- | ---: | ---: | ---: | ---: | ---: |
| N2001–2700 | 0.02385 | 0 / 699 | 226.6 | 208.9 | 1,834 |
| N2701–3400 | 0.12206 | 6 / 699 | 354.4 | 263.4 | 1,828 |
| N3401–4100 | 0.33763 | 28 / 699 | 525.5 | 359.3 | 2,440 |
| N4101–4500 | 1.00800 | 33 / 399 | 660.0 | 417.0 | 3,126 |

The first three windows have equal length. The last is explicitly shorter.
The jump threshold is a descriptive diagnostic selected after the observation,
not a convergence criterion. The 95th percentile of the absolute adjacent
log10 epsilon change rises from 0.00778 to 0.01282, 0.11938 and 0.24584 in
these windows. Phase-fraction residuals do not show a comparable increase in
this sharp-jump measure. The full seven-equation statistics are retained in
the [machine summary](../../../../PyAnsys/output/p7b-s40-t020-resume-20260921T231240Z/diagnostics/residual-onset-n04500/summary.json).

![Removal, inventory, warning counts and mass closure](../../../../PyAnsys/output/p7b-s40-t020-resume-20260921T231240Z/diagnostics/residual-onset-n04500/coupled-histories.png)

The fixed tau does not imply fixed removal: the source scales with local
liquid fraction. Mean collector liquid increases from 4.176 kg in N2001–2700
to 7.186 kg in N3401–4100, and mean applied removal increases from 208.9 to
359.3 kg/s, against the fixed measured liquid feed of 116.921 kg/s. Whole-
vessel liquid also grows. Applied-source liquid closure worsens from a signed
window mean of −81.0% to −219.5% of feed across those windows. Steady-iteration
inventory growth is not interpreted as physical storage that closes this
balance.

## Interpretation and competing explanations

The strongest immediate clue is the coincidence of sharp epsilon excursions
with brief velocity-extremum excursions, embedded in a progressively changing
liquid field. This is consistent with worsening coupled flow/turbulence
numerical behaviour. The source also removes liquid momentum and shared
k/epsilon through the same mass-sink factor, so increasing liquid availability
and source magnitude make source/pressure/turbulence coupling a plausible
contributor. That mechanism remains a hypothesis: global histories neither
locate the affected cells nor separate which equation initiates each burst.
The integrated removal trace is much smoother than the sharpest epsilon/speed
bursts, so a simple instantaneous global source jump is not established.

Viscosity limiting becomes more widespread later, but its mean does not jump
in the first post-N2700 window. Outlet reverse-flow face counts are already
persistent beforehand and decline on average (306, 302, 288, then 266).
Those counts do not measure reversed mass flow and cannot exclude recirculation
as a contributor; they do not support a new outlet-warning onset at N2700.

A changed setting, checkpoint boundary or source-update interval is not
supported by the execution record. N2700 lies inside the uninterrupted
N2500–3000 solve block; the controller makes no scientific setting changes
between blocks. Several large bursts lie well away from save boundaries.
Native applied removal at N matches the current-field expression at N−1
across all 4,499 available pairs, with zero difference at stored precision.
There is therefore no observed new update delay coincident with the change,
although this does not rule out the existing lag as part of source coupling.
Scalar, exact-face flux and seven-equation residual histories are continuous
and finite through N4500, with no conflicting duplicates or rejected rows.

**Bounded conclusion:** increased spikiness is recorded and quantified,
especially in epsilon; its timing implicates coupled velocity/turbulence
excursions but does not establish a unique root cause. This is an additional
numerical-adequacy concern, not an early-stop rule. Finish the approved cap,
inspect endpoint spatial evidence, and compare against the baseline and fresh
S40-T100 before deciding whether source strength explains the behaviour. No
tuning, new tau, extra iterations or checkpoint reload was performed for this
diagnostic.

## Reproduction and provenance

Run: `p7b-s40-t020-resume-20260921T231240Z`, tau 0.02 s, fixed S40.
The [diagnostic script](../../../../PyAnsys/scripts/analysis/diagnose_phase07b_residual_onset.py)
uses the immutable [input snapshots](../../../../PyAnsys/output/p7b-s40-t020-resume-20260921T231240Z/diagnostics/residual-onset-n04500/raw/)
and records their hashes in the machine summary. The live transcript/flux
snapshots may extend beyond N4500; every diagnostic series is restricted to
the complete N1–4500 scalar history. Warning counts are associated with the
following residual row, and absent warnings are left missing, not set to zero.
Both figures were visually checked. This analysis made no Fluent API calls.
