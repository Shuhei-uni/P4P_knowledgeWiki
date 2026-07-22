# Fluent 2024 R2 EWF/DPM Post-Processing Discovery

## Source

Live GUI/journal capture from the Purnanto separator EWF case, Fluent 24.2.

## Confirmed configuration observations

- Active EWF wall: `wall`.
- `bottom` is a normal wall and not an Eulerian Film Wall.
- Global EWF Particle Splashing can be enabled while Edge Separation and Particle Stripping remain disabled.
- Wall-level DPM Wall Splash is enabled independently on the active film wall.
- Impingement model shown in the GUI: `stanton-rutland`.
- Number of Splashed Particles shown in the GUI: `4`.
- No UDF override was selected for impingement model, film regime, or splashing distribution.

## Confirmed report construction pattern

The GUI created surface report definitions under:

```text
Solution -> Report Definitions -> New -> Surface Report
```

Observed semantic mappings:

- Facet Maximum + Film Courant Number
- Sum + Film Mass
- Facet Maximum + Film Thickness
- Area-Weighted Average + Film Thickness
- Sum + Film DPM Mass Source
- Sum + Film Outflow Mass
- Area-Weighted Average + Film Velocity Magnitude
- Facet Maximum + Film Velocity Magnitude

The production adapter must use live allowed values rather than GUI numeric list indices.

## Confirmed final values from the captured case state

- maximum Film Courant Number: `0.010627651`
- Film Mass: `0.074310961 kg`
- maximum Film Thickness: `0.00016408537 m`
- area-weighted Film Thickness: `1.2587309e-06 m`
- Film DPM Mass Source: `3.991379 kg/s`
- Film Outflow Mass: `9.2668918e-08 kg`
- area-weighted Film Velocity Magnitude: `0.067914232 m/s`
- maximum Film Velocity Magnitude: `30.605619 m/s`

These values came from one final snapshot and must not be combined into a transient closure without a time basis.

## Confirmed film flux path

GUI path:

```text
Results -> Reports -> Fluxes -> Film Mass Flow Rate
```

Equivalent documented TUI family:

```text
report/fluxes/film-mass-flow
```

Captured mixture result:

```text
steamoutlet = -6.5910833e-06 kg/s
```

## Confirmed DPM tracking path

The existing 2024 R2 particle-track adapter remains valid:

```text
/display/set/particle-tracks/report-type summary
/display/set/particle-tracks/report-to screen
/display/set/particle-tracks/display? no
/display/particle-tracks particle-tracks mixture particle-resid-time "<injection>" () 0 0
```

Enable zone-resolved per-injection summaries before tracking:

```text
/report/dpm-zone-summaries-per-injection? yes
```

## Safety finding

The exploratory journal temporarily toggled Edge Separation and Particle Stripping on to reveal dependent controls, then toggled them off. Never replay that journal as an analysis script. Production post-processing must not activate an inactive mechanism merely to expose its field variable.

## Implementation consequence

- Audit model activity first.
- Skip stripped/separated mass reports when the corresponding mechanism is not active.
- Create only namespaced report definitions.
- Reload a clean baseline between controlled per-injection studies when state contamination is possible.
- Keep splash event/parcel counts separate from represented mass and final fates.
