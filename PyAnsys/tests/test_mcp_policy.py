"""Offline regression checks for P4P's authority boundary."""
import os
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from pyansys_fluent import connection
from pyansys_fluent.mcp_policy import SessionPolicyError, check_generated_code


@pytest.mark.parametrize("code", [
    "solver.exit()", "stop = solver.exit; stop()", "solver.force_exit()",
    "solver.tui.file.read_case('x')", "solver.scheme.eval('(exit)')",
    "getattr(solver, 'exit')()", "from builtins import getattr as g; g(solver, 'exit')()",
    "import os; os.system('fluent')", "solver._fluent_connection.exit()",
    "solver.settings.file.read_journal(file_name='x.jou')", "", "  ",
])
def test_generated_lifecycle_routes_blocked(code):
    with pytest.raises(SessionPolicyError):
        check_generated_code(code)


@pytest.mark.parametrize("code", [
    "solver.settings.setup.models.energy.enabled = True",
    "solver.settings.file.write_case(file_name='C:/runs/child.cas.h5')",
    "solver.settings.solution.run_calculation.iterate(iter_count=50)",
    "import json\nprint(json.dumps({'value': 3}))",
])
def test_ordinary_snippets_allowed_for_upstream_validation(code):
    check_generated_code(code)


@pytest.fixture
def clean_config(monkeypatch):
    for key in list(os.environ):
        if key.startswith(('FLUENT_', 'STUDENT_')):
            monkeypatch.delenv(key)
    monkeypatch.setattr(connection, 'load_dotenv', lambda *_: False)
    return monkeypatch


@pytest.mark.parametrize("alias,prefix,suffix", [('1','FLUENT',''), ('2','FLUENT','2'), ('student','STUDENT','')])
def test_endpoint_aliases_and_session_preservation(clean_config, alias, prefix, suffix):
    for key,value in [('IP','127.0.0.1'), ('PORT','55000'), ('PASSWORD','not-for-logs')]:
        clean_config.setenv(f'{prefix}_{key}{suffix}', value)
    kwargs = connection.resolve_connection_kwargs(alias)
    assert kwargs['cleanup_on_exit'] is False
    assert kwargs['port'] == 55000
    assert kwargs['password'] == 'not-for-logs'
    assert kwargs['start_transcript'] is True


def test_local_executable_never_causes_launch(clean_config):
    clean_config.setenv('FLUENT_LOCAL_EXE', 'fluent.exe')
    with pytest.raises(SessionPolicyError):
        connection.resolve_connection_kwargs('1')
    with pytest.raises(SessionPolicyError):
        connection._launch_local_fluent()


def test_server_info_precedence_and_missing_file(clean_config, tmp_path):
    info = tmp_path/'server.txt'
    clean_config.setenv('FLUENT_SERVER_INFO_FILE', str(info))
    with pytest.raises(FileNotFoundError):
        connection.resolve_connection_kwargs()
    info.write_text('secret', encoding='utf-8')
    assert connection.resolve_connection_kwargs()['server_info_file_name'] == str(info)


def test_legacy_mapper_cannot_be_an_automatic_fallback(monkeypatch):
    from pyansys_fluent.settings_tree_mapper import capture_settings_tree
    monkeypatch.delenv('P4P_ALLOW_LEGACY_TREE_MAPPER', raising=False)
    with pytest.raises(RuntimeError, match='retired'):
        capture_settings_tree(object(), 'setup')
