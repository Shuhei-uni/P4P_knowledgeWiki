# Source Notes

These notes summarize public documentation used to ground this package.

- Ansys Fluent DPM setup is based on defining the initial particle position, velocity, size, temperature, and material/physical properties for trajectory and heat/mass-transfer calculations.
- Ansys Fluent multiphase model families include VOF, Mixture, and Eulerian; the available child settings depend on which family is active.
- Eulerian Wall Film is enabled from Fluent's Models task page, after which wall-film options and wall boundary film settings become available.
- PyFluent Settings APIs are object-based and allow inspection of child objects/commands, but generated paths differ across Fluent versions and active model states.
- Fluent TUI remains an important fallback when a PyFluent settings path is unavailable or has a wrapper issue.

Do not assume these notes are complete. Use `documentation_map.md` for fresh checks.
