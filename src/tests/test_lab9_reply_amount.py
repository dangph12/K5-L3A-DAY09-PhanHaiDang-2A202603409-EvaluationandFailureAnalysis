"""FM-08 regression: ledger correctness alone cannot detect misleading replies."""
from types import SimpleNamespace

import pytest

pytestmark = pytest.mark.student


@pytest.mark.parametrize('text,amount,want', [
    ('Đã hoàn 35.000đ.', 20000, False),
    ('Đã hoàn 20.000đ.', 20000, True),
    ('Đã hoàn 20,000 VND.', 20000, True),
    ('Đã hoàn 20000 đồng.', 20000, True),
    ('Chưa đủ điều kiện hoàn.', 0, True),
    ('Đã hoàn 35.000đ.', 0, False),
])
def test_reply_ledger_consistency(text, amount, want):
    from lab9.graders import ReplyAmountConsistent
    ctx = SimpleNamespace(output={'snapshot': {'refund_vnd': amount},
                                 'events': [{'kind': 'reply', 'payload': {'text': text}}]})
    assert ReplyAmountConsistent().evaluate(ctx).value is want


def test_missing_reply_fails_closed():
    from lab9.graders import ReplyAmountConsistent
    ctx = SimpleNamespace(output={'snapshot': {'refund_vnd': 0}, 'events': []})
    assert ReplyAmountConsistent().evaluate(ctx).value is False
