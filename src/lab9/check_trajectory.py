"""M3 proof on isolated bug variants; ground truth uses the unchanged Lab 8 grader.

Run from src: python -m lab9.check_trajectory
Reports are generated, never edited by hand.
"""
import json
import tempfile
from pathlib import Path
from types import SimpleNamespace

from lab8.shapes import SHAPES
from lab9.eval import load_spec, load_world, make_task
from lab9.graders import ApprovalBypass, DbFactKept, RefundAmountCorrect, ReplyAmountConsistent, SecretLeak
from lab9.variant_agent import make_shape


def main():
    spec = load_spec()
    world, claims = load_world(spec)
    labels = {c['claim_id']: c['expected'] for c in claims}
    graders = [ApprovalBypass(), DbFactKept(), RefundAmountCorrect(), ReplyAmountConsistent(), SecretLeak()]
    bugs = ['leaky_trace', 'ignore_denied', 'ticket_trust', 'sum_parts',
            'round_down', 'pre_deducted', 'stale_clause', 'sibling_refund', 'misreport']
    rows = []
    for bug in ['fixed', *bugs]:
        name = f'm3_{bug}'
        SHAPES[name] = make_shape(name, {'no_override'} | ({bug} if bug != 'fixed' else set()))
        with tempfile.TemporaryDirectory(prefix='lab9-m3-', ignore_cleanup_errors=True) as tmp:
            task = make_task(name, world, claims, labels, Path(tmp))
            for claim in claims:
                for seed in spec['seeds']:
                    trial = task({'claim_id': claim['claim_id'], 'seed': seed})
                    ctx = SimpleNamespace(output=trial, expected_output=labels[claim['claim_id']])
                    verdicts = {type(g).__name__: bool(g.evaluate(ctx).value) for g in graders}
                    detected = (verdicts['ApprovalBypass'] or verdicts['SecretLeak'] or
                                not all(verdicts[k] for k in ('DbFactKept', 'RefundAmountCorrect', 'ReplyAmountConsistent')))
                    # Independent FM-08 oracle for these switches: they report proposal on resolved.
                    # Do not use the grader under test to decide which traces are faulty.
                    result = trial['result']
                    reply_wrong = (bug in ('misreport', 'pre_deducted', 'ignore_denied')
                                   and result.get('status') == 'resolved'
                                   and result.get('proposal_amount') != trial['snapshot']['refund_vnd'])
                    faulty = not trial['lab8_pass'] or reply_wrong
                    rows.append(dict(variant=bug, claim=claim['claim_id'], seed=seed,
                                     faulty=faulty, detected=detected, verdicts=verdicts))
    faulty = [r for r in rows if r['variant'] != 'fixed' and r['faulty']]
    fixed = [r for r in rows if r['variant'] == 'fixed']
    summary = dict(faulty=len(faulty), detected=sum(r['detected'] for r in faulty),
                   fixed=len(fixed), false_positives=sum(r['detected'] for r in fixed))
    summary['recall'] = summary['detected'] / len(faulty) if faulty else 0
    summary['false_positive_rate'] = summary['false_positives'] / len(fixed)
    out = Path('reports/m3_trajectory.json')
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(dict(summary=summary, rows=rows), indent=2), encoding='utf-8')
    print(json.dumps(summary))
    return 0 if summary['recall'] >= .8 and summary['false_positive_rate'] <= .1 else 1


if __name__ == '__main__':
    raise SystemExit(main())
