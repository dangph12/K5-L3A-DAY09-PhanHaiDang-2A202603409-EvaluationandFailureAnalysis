"""C-002@11: reproduce the first wrong step and verify the fixed counterfactual."""
import pytest

pytestmark = pytest.mark.student


def test_c002_ticket_override_regression():
    from lab9.trace_case import investigate
    from lab9.graders import DbFactKept
    from types import SimpleNamespace

    broken = investigate('seeded_regression', 'C-002', 11)['trial']
    fixed = investigate('fixed', 'C-002', 11)['trial']
    override = next(i for i, event in enumerate(broken['events']) if event['kind'] == 'model_override')
    assert [e['kind'] for e in broken['events'][:override]] == ['handoff', 'investigator']
    assert broken['events'][1]['payload']['lookup_order']['order']['delay_days'] == 2
    assert broken['events'][override]['payload']['delay_days'] == 5
    assert DbFactKept().evaluate(SimpleNamespace(output=broken)).value is False
    assert DbFactKept().evaluate(SimpleNamespace(output=fixed)).value is True
    assert broken['snapshot']['refund_vnd'] == 20000
    assert fixed['snapshot']['refund_vnd'] == 0
    assert broken['lab8_pass'] is False
    assert fixed['lab8_pass'] is True
