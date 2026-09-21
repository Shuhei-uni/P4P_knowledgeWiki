# Phase 7b meeting: story and speaker notes

Companion to the [meeting report](meeting-report.md). Scientific authority:
[G1 results](results.md). Page numbers below refer to the 13-page PDF.
No new scientific result or run authorization is introduced.

## The central story

> We wanted a simpler way to remove liquid while keeping the full separator
> model steady. The collector does remove liquid, and changing its thickness
> changes the predicted inventory and distribution. However, none of the
> tested settings reconciles removal with mass conservation and a stationary
> solution. That makes source strength and its numerical coupling the next
> question to investigate.

Keep three questions separate throughout: does liquid reach the collector;
does the source remove it; does the whole model reach a credible steady state?
The first two have supporting evidence. The third has not been demonstrated.

## Page 1 — Give the answer first

**Say:** “This was a five-case discovery screen. Four cases reached the
5,000-iteration limit, but none met our combined mass-balance, inventory and
residual criteria. The largest collector diverged before reaching the limit.
The useful finding is that removal is active, but increasing collector
coverage alone has not produced an acceptable steady solution.”

**Point to:** the completed-iteration column and the imbalance column.

**Interpretation:** reaching the iteration limit is execution completion,
not convergence. The table does not identify a successful operating case.

## Page 2 — Explain why this model exists

**Say:** “Previously, explicitly modelling the lower pool and brine outlet
became too complicated for our steady-state objective. Here I retain the full
geometry but replace the drainage process with a liquid-removal region. The
physical brine outlet is closed, and there is no requirement to hold a pool.”

**Point to:** the inlet, steam outlet, closed brine face and shaded lower region.

**Clarify:** the collector is a numerical representation of removal, not a
physical drain design. White gaps in the section lie outside the sampled
fluid domain; they are not the liquid-fraction colour for steam.

## Page 3 — Explain the controlled experiment

**Say:** “I changed how far the removal region extends upward: 20, 40, 60,
80 and 100 percent of the allowed height. The maximum reaches the previous
model cutoff. Everything else, including the source strength and fresh
initialization, was held fixed.”

**Point to:** the five upper elevations and common lower datum.

**Clarify:** the percentages describe height, not liquid volume, geometric
volume or removal efficiency. The blue shading shows where removal is allowed;
it does not show water. The finite sink removes faster when more liquid is
present; it is not guaranteed to remove every parcel instantaneously.

**Transition:** “The first question was whether changing coverage actually
changes the liquid behaviour.”

## Page 4 — The collector changes the solution

**Say:** “It does. The liquid inventory curves separate, and the removal
source becomes active. But removal varies substantially rather than settling
into a rate consistent with the feed. The lower panel shows that the global
liquid balance remains open.”

**Point to:** top panel for inventory, middle panel for removal and feed line,
then bottom panel for conservation. Read the three panels together.

**Clarify:** these are steady solver iterations, not physical time. The common
N1–4000 range permits a matched numerical-age comparison of all five cases;
it does not imply equal physical residence time.

**Transition:** “So a lower inventory is promising as a response, but it still
needs to pass the conservation and stationarity checks.”

## Page 5 — The decisive limitation: inventory and conservation

**Say:** “Across the four completed cases, the final-window mean liquid volume
falls from about 0.958 cubic metres in S20 to 0.647 in S80, a reduction of
roughly 32 percent. However, inventory still changes between the two late
windows, and the liquid imbalance remains about 253 to 503 percent of the
feed. That is well outside our one-percent screening criterion.”

**Point to:** the different inventory levels, the continuing late variation,
and the large negative closure excursions.

**If asked what the negative balance means:** the convention is

`liquid balance = inlet flow - outlet flow - native applied removal`.

For S40, approximate late means give `117 - 22 - 390 = -295 kg/s`. The
reported removal plus outlet flow exceeds the inlet. In an unconverged steady
calculation, that is an unresolved equation balance, not a credible prediction
of sustained physical removal. Do not add the inventory-versus-iteration slope
as though it were a physical storage term.

**Clarify:** 32% is a finite-window inventory comparison, not a performance
improvement or capture efficiency. S40 has the smallest late imbalance among
the four, but it is still unacceptable. No monotonic improvement of mass
balance follows from increasing collector thickness.

## Pages 6–7 — Use liquid fraction to locate the remaining liquid

**Say:** “These full-height sections show that the fluid is mostly vapour-rich
in much of the sampled interior, with liquid-rich bands near the outer
boundary. The lower collection region contains little liquid, while liquid
remains higher in the vessel. The second plane shows that the distribution
also varies around the separator.”

**Point to:** the shared 0–1 colour scale, outer liquid-rich regions and dashed
collector tops. Use the inventory reports to support the statement that most
liquid remains above the collector; a thin-looking band can contain substantial
liquid when it extends over a large area.

**Interpretation:** a nearly empty collector does not by itself mean liquid
never arrives. The measured collector crossings and active source show that
liquid reaches and leaves the region. Low collector inventory can coexist
with substantial throughput under this source law.

**Limits:** these are two planes, not a complete three-dimensional inventory
map or proof of a resolved physical wall film. S100 is N4000 recovery evidence;
the other cases are N5000. Do not rank S100 as a superior final solution.

## Page 8 — Check whether upper separation improved consistently

**Say:** “The horizontal sections let us compare the region above every
collector on the same planes and colour scale. Liquid-rich outer regions
persist, and the differences do not improve uniformly with thickness. Lower
global inventory therefore does not automatically mean cleaner separation
everywhere above the collector.”

**Point to:** a single height across all columns before moving to the next
height. At y=3 m, S40 has a greater area-mean liquid fraction than S20, despite
its lower whole-vessel inventory; S80 also exceeds S60 there.

**Limits:** these are unconverged snapshots. Avoid validated efficiency,
wall-film thickness or physical flow-regime claims.

## Pages 9–10 — Explain what the velocity fields add

**Say:** “Changing the lower collector also changes the velocity distribution
above it. That is why we need to assess the whole separator, not just how much
liquid is left at the bottom. These snapshots are useful for locating changes,
but they do not establish stable or accurate separation.”

**Point to:** the common scale, off-centre speed patterns and differences
between mixture and liquid velocity.

**Clarify:** a visually smooth endpoint can hide earlier excursions. These
four section planes do not capture the domain maximum. Zero liquid velocity
in a nearly liquid-free region should not be described as a stagnant pool.
Do not claim that the flow is unchanged, or infer three-dimensional circulation
solely from speed-magnitude panels.

## Page 11 — Residuals corroborate the balance problem

**Say:** “The three momentum residuals satisfy our late-window threshold, but
continuity, turbulent kinetic energy, dissipation and liquid fraction do not.
That agrees with the mass-balance and inventory evidence: the whole system
has not converged, even where individual equations look better.”

**Point to:** the 10^-3 line and the four histories remaining above it in the
late window. Early decreases or isolated threshold crossings are not sustained
late-window acceptance.

**Limits:** 10^-3 is the declared project screening convention, not proof of
accuracy by itself. Residual shape alone does not identify the root cause.

## Page 12 — Describe S100 as numerical failure

**Say:** “For the largest collector, the numerical solution deteriorated
sharply and the solver stopped with floating-point exceptions at attempted
iteration 4183. I retained every completed record through 4182. The N4000
checkpoint used for the contour figures was already unconverged, but it was
preserved before the terminal runaway.”

**Point to:** the escalation near the end of the right panel. Its vertical
scale is expanded; compare values rather than line angles between panels.

**Limits:** this is not evidence of a physical transient instability or a
proof that a full-depth collector cannot work. One failed attempt does not
establish repeatability. Epsilon rising first in a visible spike does not by
itself prove the turbulence model caused the failure.

## Page 13 — Close with the question the evidence now supports

**Say:** “The thickness screen confirms that the collector affects liquid
inventory and distribution, but none of these cases gives a balanced steady
solution. I propose fixing the geometry and varying only the removal strength.
This tests whether the present aggressive source is contributing to the
numerical difficulty.”

Use S40 as a diagnostic reference because its completed late-window imbalance
was the smallest, not because it is a satisfactory operating model. Proposed
new tau values are 0.02 s and 0.10 s, compared with the tested 0.00241 s.
At the same liquid inventory these make the source about eight and forty-two
times weaker, respectively. Start each comparison from the same fresh parent.
This is proposed work, not an approved or started run.

**Decision sought:** whether to pursue that controlled strength comparison,
or prioritize another explicitly framed coupling diagnostic. Preserve the
steady-state requirement and assess mass closure, inventory and all residuals
together.

## Likely supervisor questions

**Why not simply run longer?** The finite screen does not establish that longer
runs could never settle. However, large late mass imbalances, continuing
inventory change, speed excursions and one divergence give no basis to assume
that extra iterations alone will solve the problem.

**Does this mean the collector failed?** The source removes liquid and changes
the solution. What failed is the tested configuration's ability to demonstrate
an acceptable steady conservative state. The broader collector idea remains
unqualified, not physically disproved.

**Could the mass-balance calculation itself be wrong?** We used separately
measured signed boundary fluxes and the native applied source exactly once,
with the source lag recorded. That addresses the known double-counting and
current-versus-applied-source issues. It does not establish that every aspect
of source coupling or modelling is correct.

**Why test tau when earlier studies already did?** Those studies used a
different mesh and collector arrangement. They provide context but cannot
replace a controlled strength comparison in this geometry.

**Why not force removal to equal the inlet flow?** That could request removal
where liquid is unavailable and change the modelling assumption. The current
source depends on liquid present in the collector; any new controller would
be a separately defined experiment.

## One-sentence conclusion

> Increasing collector coverage changes the liquid inventory, but under the
> tested removal strength it does not establish a conservative steady solution;
> the next experiment should isolate removal strength from geometry.
