"""Load and verify the exact N3000 parent; never initialize or solve.

Imports are offline. Host shell commands and OneDrive copy operations are absent.
The caller supplies one explicit server-side folder containing downloaded files.
This is preparation only: a separate reviewed runner must configure local outputs,
paired checkpoints, and terminal save/reopen verification before solving.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path, PureWindowsPath
import sys
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
CASE = '680-attempt01-N3000.cas.h5'
DATA = '680-attempt01-N3000.dat.h5'
START = 3000
ADDITIONAL = 5000
TARGET = START + ADDITIONAL
EXPRESSION = 'Direct680NativeIteration'


def parent_paths(directory):
    folder = PureWindowsPath(directory)
    if not folder.is_absolute() or '\x00' in str(folder) or '..' in folder.parts:
        raise ValueError('Require one absolute server-side Windows parent directory')
    return str(folder / CASE), str(folder / DATA)


def verify_sources_off(setup):
    fluids = setup['cell_zone_conditions']['fluid']
    if not fluids:
        raise RuntimeError('No fluid zones found')
    checked = {}
    for zone_name, zone in fluids.items():
        phases = zone.get('phase')
        if not isinstance(phases, dict) or not phases:
            raise RuntimeError(f'Cannot verify fluid phase sources in {zone_name}')
        for phase_name, phase in phases.items():
            enabled = phase.get('sources', {}).get('enable')
            if enabled is not False:
                raise RuntimeError(f'Source enabled or unverified: {zone_name}/{phase_name}')
            checked[f'{zone_name}/{phase_name}'] = False
    return checked


def native_iteration(solver):
    expressions = solver.settings.setup.named_expressions
    if EXPRESSION not in expressions.get_object_names():
        expressions.create(name=EXPRESSION)
        expressions[EXPRESSION].definition = 'Iteration'
    node = expressions[EXPRESSION]
    if node.definition() != 'Iteration':
        raise RuntimeError('Iteration expression name collision')
    value = float(node.get_value())
    if not value.is_integer():
        raise RuntimeError(f'Noninteger native iteration: {value}')
    return int(value)


def prepare(solver, directory, file_exists):
    case, data = parent_paths(directory)
    # Refuse replacement until a loaded endpoint has a separate preservation receipt.
    if solver.settings.setup.models.is_active():
        raise RuntimeError('Server 2 already has a case loaded; preserve/reconcile it before replacement')
    for path in (case, data):
        if not file_exists(solver, path):
            raise FileNotFoundError(path)
    solver.settings.file.read_case(file_name=case)
    solver.settings.file.read_data(file_name=data)
    if not solver.settings.solution.run_calculation.iterate.is_active():
        raise RuntimeError('Loaded solver is not idle/available for iteration')
    setup = solver.settings.setup.get_state()
    sources = verify_sources_off(setup)
    n = native_iteration(solver)
    if n != START:
        raise RuntimeError(f'Expected N{START}; loaded native coordinate is N{n}. Reconcile before solving.')
    return {
        'status': 'PARENT_LOADED_VERIFIED_RUN_NOT_CONFIGURED',
        'checked_utc': datetime.now(timezone.utc).isoformat(),
        'server_id': '2', 'case': case, 'data': data,
        'start_iteration': n, 'additional_iterations': ADDITIONAL,
        'target_iteration': TARGET, 'iterations_issued': 0,
        'absorber_enabled': False, 'source_readback': sources,
        'setup': solver.settings.setup.get_state(),
        'methods': solver.settings.solution.methods.get_state(),
        'controls': solver.settings.solution.controls.get_state(),
        'residual': solver.settings.solution.monitor.residual.get_state(),
        'report_files': solver.settings.solution.monitor.report_files.get_state(),
        'autosave': solver.settings.file.auto_save.get_state(),
        'verification_limit': 'Native read succeeded and N3000/source state checked; independent content hashes not yet established',
        'next_required': 'Review/configure server-local output paths and paired autosaves; save/reopen prepared pair; deploy fixed5000 runner and verifier',
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--parent-directory', required=True, help='Absolute Windows folder; both exact files must be downloaded')
    parser.add_argument('--output', type=Path, default=ROOT/'output/direct-student-680k/20261008-N3000-N8000')
    args = parser.parse_args(argv)
    parent_paths(args.parent_directory)  # Reject bad paths before attaching.
    sys.path[:0] = [str(ROOT/'src'), str(ROOT/'scripts/setup')]
    from run_phase8_stage2_f2_simple import attach
    from pyansys_fluent.common import remote_file_exists
    args.output.mkdir(parents=True, exist_ok=True)
    try:
        proof = prepare(attach(), args.parent_directory, remote_file_exists)
    except Exception as exc:
        (args.output/'preparation-error.json').write_text(json.dumps({
            'status': 'PREPARATION_STOPPED', 'error_type': type(exc).__name__,
            'error': str(exc), 'iterations_issued': 0,
        }, indent=2)+'\n')
        raise
    (args.output/'loaded-state.json').write_text(json.dumps(proof, indent=2)+'\n')
    print(json.dumps({k:proof[k] for k in ('status','start_iteration','target_iteration','iterations_issued')}))


if __name__ == '__main__':
    main()
