from pathlib import Path
import sys
from types import SimpleNamespace

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from pyansys_fluent.dependency_workflow import WorkflowStep, execute_step, execute_workflow, values_equal
from pyansys_fluent.setup_snapshot_diff import compare_snapshots


def make_step(name, expected, *, mismatch=False):
    return WorkflowStep(name, name, getter=lambda root: root,
                        setter=lambda root: setattr(root, 'value', expected if not mismatch else 'wrong'),
                        readback=lambda root: root.value, expected=expected)


def test_mismatch_stops_dependent_mutation():
    root = SimpleNamespace(value=0)
    results = execute_workflow(root, [make_step('first',1,mismatch=True), make_step('second',2)])
    assert [r.result for r in results] == ['readback_mismatch','blocked']
    assert root.value == 'wrong'
    assert results[0].category == 'readback mismatch'


def test_no_verifier_no_mutation():
    root = SimpleNamespace(value=0)
    step = WorkflowStep('x','x',lambda root: root,lambda root: setattr(root,'value',9))
    result = execute_step(root, step)
    assert result.result == 'blocked'
    assert root.value == 0


def test_expected_none_can_be_verified():
    assert execute_step(SimpleNamespace(), make_step('x',None)).verified


def test_exception_stops_all_successors():
    def fail(root):
        raise RuntimeError('setter failed')
    first = make_step('x',1)
    first.setter = fail
    results = execute_workflow(SimpleNamespace(), [first, make_step('y',2), make_step('z',3)])
    assert [r.result for r in results] == ['failed','blocked','blocked']


@pytest.mark.parametrize('observed,expected,answer', [(True,1,False), ('1',1,False), (float('nan'),float('nan'),False), ({'a':1},{'a':1.0},True), ([1,2],[1,3],False)])
def test_typed_readbacks(observed,expected,answer):
    assert values_equal(observed,expected) is answer


def test_explicit_tolerances():
    assert not values_equal(1.000001,1.0)
    assert values_equal(1.000001,1.0,abs_tol=0.00001)


def snapshot(value):
    return {'schema':'p4p.mcp-inspection.v1','status':'OBSERVED','paths':['setup.x'],'errors':{},'results':{'get_state':{'setup.x':value}}}


def test_undeclared_difference_blocks():
    assert compare_snapshots(snapshot(1),snapshot(2),[])['status'] == 'BLOCKED'
    result = compare_snapshots(snapshot(1),snapshot(2),['setup.x'])
    assert result['status'] == 'WITHIN_DECLARED_DIFF_SCOPE'
    assert 'Verify artifact identity' in result['claim_limit']


@pytest.mark.parametrize('value', [None, {'error':'unavailable'}, {'inactive':True}, {'skipped':'command_or_query'}, '<large_state_omitted>'])
def test_unknown_or_truncated_state_never_proves_invariant(value):
    with pytest.raises(ValueError):
        compare_snapshots(snapshot(value),snapshot(value),[])


def test_missing_path_coverage_blocks():
    a=snapshot(1)
    a['results']['get_state']={'wrong.path':1}
    with pytest.raises(ValueError):
        compare_snapshots(a,a,[])
