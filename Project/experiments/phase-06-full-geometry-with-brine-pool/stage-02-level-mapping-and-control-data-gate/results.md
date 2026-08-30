# Phase 06 / Stage 02 — level mapping and control-data gate — results

## Status

**Data-gated; no new CFD calculation was run.** This is a substantive
read-only evidence audit following Stage 01, not an unexecuted simulation
scaffold.

## Evidence found

**Observed.** The loaded F11-derived outlet-vent endpoint contains the two
geometry-specific lower-region register bounds and both geometric-volume and
phase-2 liquid-volume report definitions described in the Stage-02 setup.
This proves that a mesh-specific volume/elevation method is technically
plausible and identifies the actual coordinate basis that must be audited.

**Observed.** The retained Project, reusable CFD wiki, and implementation
records contain no authoritative plant pool-level setpoint, level band,
instrument location/datum, brine valve or line characteristic, downstream
condition, or controller details. The prior documentation repeatedly labels
these as Missing Info; no local source overrode that state.

**Observed from the closest cited separator design source.** The
Purnanto-derived material supplies the separator and brine-outlet *geometry*,
but its stated CFD scope excludes water flow into the brine pipe. It is useful
for mesh-coordinate/geometry checks, not for reconstructing the plant's pool
measurement or downstream liquid-control mechanism. See
[Purnanto geometry record](../../../technical/purnanto-spiral-inlet-geometry.md)
and the reusable
[source scope record](../../../../CFD_wiki/wiki/sources/purnanto-2013-cfd-geothermal-separator.md).

**Observed from recoverable project history.** A search of retained Git
revisions for `setpoint`, `level control`, `control valve`, and `brine pipe`
found only the same design-scope statement and generic discussion of nominal
setpoints. It found no removed project record with separator-specific pool
level, instrument, valve, or controller data. The Missing Info state is not
only a limitation of the current trimmed checkout.

## Conclusion and next decision

**Phase-closure outcome: RETURN TO HUMAN / PHASE-PLANNER.** Phase 6 cannot
proceed honestly from a generic mesh coordinate to a *physically credible,
controlled* brine pool without the missing plant measurement and outlet-control
boundary. Further arbitrary steady resistance, pressure, or turbulence trials
would repeat the route Stage 01 has already challenged rather than reduce this
material uncertainty.

The bounded statement now supported is:

> In the retained F11 steady Mixture/RNG model, lower-region liquid-mass
> histories are usable response proxies and a generic outlet-vent `K=10`
> condition worsens their accumulation. No current evidence maps either proxy
> to the real separator's indicated level or specifies the physical outlet
> feedback needed to hold that level.

## Required human input to resume later stages

At minimum, provide or authorise a declared source for:

1. normal pool setpoint and acceptable band;
2. level instrument location/type and its geometry datum;
3. brine outlet hardware and downstream condition; and
4. valve/line characteristic or explicit approval of a bounded surrogate
   relation for a clearly labelled numerical—not plant-fidelity—study.

Scaled residual history also needs a durable capture method before any later
stage calls a result numerically credible.
