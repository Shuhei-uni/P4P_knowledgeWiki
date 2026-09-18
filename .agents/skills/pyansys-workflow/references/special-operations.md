# Special operations

Use this file for narrow Fluent operations that do not deserve their own skill.

## Pool patch / liquid inventory initialization

Treat a pool as an initial-condition cell selection, not a claim about the final
liquid level.

- inspect the live mesh/zone and coordinate convention;
- create or reuse an explicit cell register for the requested bounds;
- verify the selected cells/volume before patching;
- initialize only when the case requires it;
- patch only the requested liquid phase/state;
- report selected geometric/phase volume and the exact register/bounds.

If the selection intersects unintended zones or the requested geometry is
ambiguous, derive a safer zone-restricted/register definition from the case
rather than patching blindly.

Other one-off operations belong here when they are implementation details of an
active experiment and do not need independent invocation.
