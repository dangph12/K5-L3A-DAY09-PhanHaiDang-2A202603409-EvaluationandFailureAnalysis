"""Integrity attacks that must fail even when the aggregate looks green."""
import copy

import pytest

pytestmark = pytest.mark.student


def integrity_check(*args):
    # Lab 8 host CI collects student tests without Lab 9's optional dependencies.
    from lab9.gate import integrity_check as check
    return check(*args)

SPEC = {'eval_set_version': 'v2', 'metrics': [
    {'id': 'pass_rate', 'blocking': True, 'threshold': {'min': .85, 'no_significant_drop': True}}],
    'slices': [{'name': 'money_movement', 'metric': 'pass_rate', 'min': .95,
                'blocking': True, 'no_significant_drop': True}]}


def report():
    return {'manifest': {'items': 2, 'seeds': [11, 22], 'eval_set_sha': 'same'},
            'rows': [{'item_id': i, 'seed': s, 'slices': ['money_movement'], 'pass_rate': True}
                     for i in ['E-001', 'E-002'] for s in [11, 22]],
            'metrics': {'pass_rate': 1.0}, 'evaluator_failures': []}


def test_honest_report_passes():
    assert integrity_check(report(), report(), SPEC, SPEC) == []


@pytest.mark.parametrize('attack', ['duplicate', 'failure', 'relabel', 'missing', 'infinite'])
def test_green_report_attacks(attack):
    base = report()
    pr = copy.deepcopy(base)
    if attack == 'duplicate':
        pr['rows'][-1] = copy.deepcopy(pr['rows'][0])
    elif attack == 'failure':
        pr['evaluator_failures'] = ['grader crashed']
    elif attack == 'relabel':
        pr['rows'][0]['slices'] = []
    elif attack == 'missing':
        pr['rows'][0]['pass_rate'] = None
    else:
        pr['metrics']['pass_rate'] = float('inf')
    assert integrity_check(pr, base, SPEC)


@pytest.mark.parametrize('attack', ['drop_metric', 'drop_slice', 'drop_blocking', 'drop_ci', 'slice_floor'])
def test_ratchet(attack):
    spec = copy.deepcopy(SPEC)
    if attack == 'drop_metric':
        spec['metrics'] = []
    elif attack == 'drop_slice':
        spec['slices'] = []
    elif attack == 'drop_blocking':
        spec['metrics'][0]['blocking'] = False
    elif attack == 'drop_ci':
        spec['slices'][0]['no_significant_drop'] = False
    else:
        spec['slices'][0]['min'] = .5
    assert integrity_check(report(), report(), spec, SPEC)
