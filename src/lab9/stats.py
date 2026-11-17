"""Statistics students implement (M2 judge calibration, M4 paired bootstrap).

Rules: a judge is a classifier -- measure it like one. A higher mean is not
"better" until the paired CI of the difference excludes 0.
Reference values to self-check are in tests/test_lab9_stats.py.
"""

from __future__ import annotations

from collections.abc import Sequence

POS = "FAIL"   # the judge's job is to FIND failures, so FAIL is the positive class


def confusion(human: Sequence[str], judge: Sequence[str]) -> dict[str, int]:
    """tp/fp/fn/tn with FAIL as positive."""
    if len(human) != len(judge) or not human:
        raise ValueError("labels must be nonempty and paired")
    if any(x not in ("PASS", "FAIL") for x in [*human, *judge]):
        raise ValueError("invalid label")
    return {k: sum((h == POS) == hp and (j == POS) == jp for h, j in zip(human, judge))
            for k, hp, jp in [("tp", True, True), ("fp", False, True), ("fn", True, False), ("tn", False, False)]}


def precision_recall(human: Sequence[str], judge: Sequence[str]) -> tuple[float, float]:
    c = confusion(human, judge)
    return tuple(c["tp"] / d if d else 0.0 for d in (c["tp"] + c["fp"], c["tp"] + c["fn"]))


def cohen_kappa(human: Sequence[str], judge: Sequence[str]) -> float:
    """kappa = (p_o - p_e) / (1 - p_e). Raise ValueError when undefined (p_e == 1):
    a constant judge has no signal and must FAIL calibration, not pass on a technicality."""
    c = confusion(human, judge)
    n = len(human)
    hp, jp = (c["tp"] + c["fn"]) / n, (c["tp"] + c["fp"]) / n
    pe = hp * jp + (1 - hp) * (1 - jp)
    if pe == 1:
        raise ValueError("undefined kappa")
    return ((c["tp"] + c["tn"]) / n - pe) / (1 - pe)


def rogan_gladen(observed_rate: float, sensitivity: float, specificity: float) -> float:
    """Correct an observed failure rate for judge error; clip to [0, 1]."""
    if not all(0 <= x <= 1 for x in (observed_rate, sensitivity, specificity)) or sensitivity + specificity <= 1:
        raise ValueError("invalid rates or uninformative judge")
    return min(1.0, max(0.0, (observed_rate + specificity - 1) / (sensitivity + specificity - 1)))


def paired_bootstrap(a: Sequence[float], b: Sequence[float], *, n_resamples: int = 1000,
                     rng: int = 2027, confidence: float = 0.95) -> tuple[float, float, float]:
    """a[i], b[i] = per-item mean over seeds, SAME items, SAME order.
    Return (mean(a)-mean(b), lo, hi) with scipy.stats.bootstrap(paired=True, method="percentile",
    rng=numpy.random.default_rng(rng)). If a == b everywhere return (0.0, 0.0, 0.0)."""
    import numpy as np
    from scipy.stats import bootstrap
    if len(a) != len(b) or not a:
        raise ValueError("nonempty paired samples required")
    aa, bb = np.asarray(a, dtype=float), np.asarray(b, dtype=float)
    if not np.isfinite(aa).all() or not np.isfinite(bb).all():
        raise ValueError("finite values required")
    if np.array_equal(aa, bb):
        return (0.0, 0.0, 0.0)
    res = bootstrap((aa, bb), lambda x, y, axis: np.mean(x-y, axis=axis), paired=True,
                    method="percentile", n_resamples=n_resamples, confidence_level=confidence,
                    rng=np.random.default_rng(rng))
    return float(np.mean(aa-bb)), float(res.confidence_interval.low), float(res.confidence_interval.high)


def pass_at_k(n: int, c: int, k: int) -> float:
    """Probability that AT LEAST ONE of k trials drawn from n (c of them passing) passes.
    Unbiased estimator (Chen et al. 2021): 1 - C(n-c, k) / C(n, k). Raise ValueError if k > n."""
    # TODO M6
    raise NotImplementedError


def pass_hat_k(n: int, c: int, k: int) -> float:
    """pass^k (tau-bench, Yao et al. 2024): probability that ALL k trials drawn from n pass.
    Unbiased estimator: C(c, k) / C(n, k). Raise ValueError if k > n.
    pass^k <= pass@1 <= pass@k; a reliable agent keeps pass^k close to pass@1."""
    # TODO M6
    raise NotImplementedError
