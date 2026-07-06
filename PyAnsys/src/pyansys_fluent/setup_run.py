#!/usr/bin/env python3
"""Shared initialization and run helpers for Fluent setup scripts."""

from __future__ import annotations

from pyansys_fluent.run_persistence import RunPersistence
from pyansys_fluent.setup_common import print_header
from pyansys_fluent.common import try_action


class RunInterrupted(Exception):
    def __init__(self, completed_iterations: int):
        super().__init__(f"Run interrupted after approximately {completed_iterations} iterations")
        self.completed_iterations = completed_iterations


def initialize_case(solver) -> None:
    print_header("Initialize Target Case")
    if try_action("hybrid_initialize_settings_api", lambda: solver.settings.solution.initialization.hybrid_initialize()):
        return
    if try_action("hybrid_initialize_tui", lambda: solver.tui.solve.initialize.hyb_initialization()):
        return
    raise RuntimeError("Failed to initialize target case")


def iterate_case(
    solver,
    iterations: int,
    report_interval: int,
    checkpoint_interval: int,
    output_case: str,
    output_data: str,
    *,
    starting_completed_iterations: int = 0,
    persistence: RunPersistence | None = None,
) -> int:
    print_header("Run Target Case")
    if iterations <= 0:
        print("iterate: SKIPPED")
        return 0

    run_persistence = persistence or RunPersistence(
        output_case=output_case,
        output_data=output_data,
        checkpoint_interval=checkpoint_interval,
        report_interval=report_interval,
    )
    total_target_iterations = starting_completed_iterations + iterations
    run_persistence.record_run_start(
        total_target_iterations,
        completed_iterations=starting_completed_iterations,
    )

    chunk = max(1, report_interval)
    checkpoint_step = max(0, checkpoint_interval)
    completed = 0
    while completed < iterations:
        step = min(chunk, iterations - completed)
        try:
            ran = try_action(
                f"iterate_{completed + step}",
                lambda step=step: solver.settings.solution.run_calculation.iterate(iter_count=step),
            )
        except KeyboardInterrupt as exc:
            raise RunInterrupted(completed) from exc
        if not ran:
            try:
                ran = try_action(
                    f"iterate_tui_{completed + step}",
                    lambda step=step: solver.tui.solve.iterate(step),
                )
            except KeyboardInterrupt as exc:
                raise RunInterrupted(completed) from exc
        if not ran:
            raise RuntimeError(f"Iteration failed at step {completed + step}")
        completed += step
        current_completed = starting_completed_iterations + completed
        print(f"progress: {current_completed}/{total_target_iterations}")
        if checkpoint_step > 0 and completed < iterations and current_completed % checkpoint_step == 0:
            run_persistence.record_checkpoint(
                solver,
                completed_iterations=current_completed,
                total_iterations=total_target_iterations,
            )
    return starting_completed_iterations + completed
