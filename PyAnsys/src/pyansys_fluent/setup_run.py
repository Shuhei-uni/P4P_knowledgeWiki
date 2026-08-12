#!/usr/bin/env python3
"""Setup-side initialization helper for Fluent case preparation.

Long iteration and checkpoint ownership deliberately do not live here. Fluent
must run and autosave through its own calculation activities so a temporary
PyFluent/gRPC disconnect cannot prevent the next recovery point.
"""

from __future__ import annotations

from pyansys_fluent.setup_common import print_header
from pyansys_fluent.common import try_action


def initialize_case(solver) -> None:
    """Hybrid-initialize a prepared case before a Fluent-native run.

    This helper returns after initialization only. It never starts a solver
    iteration and never schedules a client-side checkpoint.
    """

    print_header("Initialize Target Case")
    if try_action("hybrid_initialize_settings_api", lambda: solver.settings.solution.initialization.hybrid_initialize()):
        return
    if try_action("hybrid_initialize_tui", lambda: solver.tui.solve.initialize.hyb_initialization()):
        return
    raise RuntimeError("Failed to initialize target case")
