"""Evidence-strength primitives for the Anti-DDI v2 resource.

This module implements, exactly as documented in ``data/DATA_DICTIONARY.md``,
the two derived quantities that define the resource's evidence layer:

``min_detectable_ror``
    The smallest reporting odds ratio that a pair's observed FAERS
    co-exposure count could have detected, had an interaction existed.
    It converts a co-report count into a statement about statistical
    resolution, so that a negative label can be qualified rather than
    asserted.

``assign_tier``
    The six-way evidence tier applied to each pair.

Both functions are deterministic and depend only on values shipped in
``data/antiddi_v2_dataset.csv``; running them over that file reproduces the
shipped ``min_detectable_ror`` and ``evidence_tier`` columns for all 797
rows (see ``validate.py``).

Nothing in this module makes, or supports, a clinical recommendation. A
pair's tier describes how much evidence exists about it, not whether it is
safe to co-prescribe.
"""

from __future__ import annotations

import math
from typing import Any, Mapping

__all__ = [
    "min_detectable_ror",
    "assign_tier",
    "ANCHOR_DRUGS",
    "FAERS_DENOMINATOR",
    "TIER_ORDER",
    "USABLE_TIERS",
]

#: Total FAERS reports in the openFDA release used as the denominator for
#: every expected-count calculation in the shipped dataset.
FAERS_DENOMINATOR = 20_328_575

#: The 13-drug greedy vertex cover of the 797-pair graph. Every pair in the
#: resource contains at least one of these drugs; the remaining 148 drugs form
#: an independent set. Shipped as a constant because it is the structural fact
#: a user of this resource most needs to guard against (see README).
ANCHOR_DRUGS = (
    "sevelamer",
    "ustekinumab",
    "dalteparin",
    "atenolol",
    "levetiracetam",
    "liraglutide",
    "heparin",
    "hydrocodone",
    "dextromethorphan",
    "citalopram",
    "conjugated estrogens",
    "chlorpheniramine",
    "lactulose",
)

TIER_ORDER = (
    "T1_wellpowered",
    "T2_moderate",
    "T3_limited",
    "T3_trivial_inert",
    "T4_uninformative",
    "EXCLUDED_clinical",
)

#: Tiers that constitute the usable benchmark set (538 pairs).
USABLE_TIERS = ("T1_wellpowered", "T2_moderate")

# Normal quantiles for the default alpha = 0.05 (two-sided) and power = 0.80.
# Computed with scipy at import time when available, otherwise from a small
# rational approximation, so that the module has no hard scipy requirement.
try:  # pragma: no cover - trivial import branch
    from scipy.stats import norm as _norm

    def _z(p: float) -> float:
        return float(_norm.ppf(p))

except Exception:  # pragma: no cover

    def _z(p: float) -> float:
        # Acklam's inverse-normal approximation; |error| < 1.15e-9.
        a = (
            -3.969683028665376e01,
            2.209460984245205e02,
            -2.759285104469687e02,
            1.383577518672690e02,
            -3.066479806614716e01,
            2.506628277459239e00,
        )
        b = (
            -5.447609879822406e01,
            1.615858368580409e02,
            -1.556989798598866e02,
            6.680131188771972e01,
            -1.328068155288572e01,
        )
        c = (
            -7.784894002430293e-03,
            -3.223964580411365e-01,
            -2.400758277161838e00,
            -2.549732539343734e00,
            4.374664141464968e00,
            2.938163982698783e00,
        )
        d = (
            7.784695709041462e-03,
            3.224671290700398e-01,
            2.445134137142996e00,
            3.754408661907416e00,
        )
        plow, phigh = 0.02425, 1 - 0.02425
        if p < plow:
            q = math.sqrt(-2 * math.log(p))
            return (((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / (
                ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1)
            )
        if p > phigh:
            q = math.sqrt(-2 * math.log(1 - p))
            return -(((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / (
                ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1)
            )
        q = p - 0.5
        r = q * q
        return (((((a[0] * r + a[1]) * r + a[2]) * r + a[3]) * r + a[4]) * r + a[5]) * q / (
            (((((b[0] * r + b[1]) * r + b[2]) * r + b[3]) * r + b[4]) * r + 1)
        )


def min_detectable_ror(
    n_coreports: float | None,
    p0: float = 0.01,
    alpha: float = 0.05,
    power: float = 0.80,
    grid_step: float = 0.05,
    max_ror: float = 30.0,
) -> float:
    """Smallest reporting odds ratio detectable at a given co-exposure count.

    A pair co-reported ``n_coreports`` times in FAERS supports only
    interaction effects at least this large. Small counts therefore do not
    license a negative claim; they only establish that no claim can be made.
    The value is what the shipped ``min_detectable_ror`` column contains.

    Model
    -----
    Two-proportion comparison of the adverse-event rate among co-exposed
    reports against a background rate ``p0``, using the two-sided normal
    approximation with a pooled variance for the type-I term and separate
    variances for the type-II term::

        p1  = ROR * p0 / (1 + p0 * (ROR - 1))
        pbar = (p0 + p1) / 2
        required  =  z(1 - alpha/2) * sqrt(2 * pbar * (1 - pbar))
                   + z(power)       * sqrt(p0*(1 - p0) + p1*(1 - p1))
        detectable  iff  (p1 - p0) * sqrt(n_coreports) >= required

    The smallest ``ROR`` on a ``grid_step`` grid starting at
    ``1 + grid_step`` that satisfies the inequality is returned. Both arms
    are taken to have ``n_coreports`` reports, i.e. the co-exposed stratum
    is the binding constraint; this is deliberately the conservative
    reading of the available power.

    Parameters
    ----------
    n_coreports : float or None
        FAERS co-report count for the pair. ``None``, ``nan`` and values
        ``<= 0`` return ``inf``.
    p0 : float, default 0.01
        Assumed background adverse-event rate per report.
    alpha : float, default 0.05
        Two-sided type-I error rate.
    power : float, default 0.80
        Target statistical power.
    grid_step : float, default 0.05
        Resolution of the ROR grid searched. The shipped column was
        generated at this resolution; changing it changes the values.
    max_ror : float, default 30.0
        Search ceiling. Pairs whose smallest detectable effect exceeds this
        return ``inf`` and are reported as uninformative rather than as
        carrying an implausibly precise number.

    Returns
    -------
    float
        The minimum detectable ROR, or ``inf`` when no effect at or below
        ``max_ror`` is detectable at the requested alpha and power.

    Examples
    --------
    >>> round(min_detectable_ror(2019), 2)
    2.15
    >>> min_detectable_ror(11)
    inf
    >>> min_detectable_ror(0)
    inf
    """
    if n_coreports is None:
        return math.inf
    try:
        n = float(n_coreports)
    except (TypeError, ValueError):
        return math.inf
    if not math.isfinite(n) or n <= 0:
        return math.inf
    if not 0.0 < p0 < 1.0:
        raise ValueError("p0 must lie strictly between 0 and 1")
    if not 0.0 < alpha < 1.0:
        raise ValueError("alpha must lie strictly between 0 and 1")
    if not 0.0 < power < 1.0:
        raise ValueError("power must lie strictly between 0 and 1")
    if grid_step <= 0:
        raise ValueError("grid_step must be positive")

    z_alpha = _z(1.0 - alpha / 2.0)
    z_beta = _z(power)
    root_n = math.sqrt(n)

    steps = int(round((max_ror - 1.0) / grid_step))
    for k in range(1, steps + 1):
        ror = 1.0 + k * grid_step
        p1 = ror * p0 / (1.0 + p0 * (ror - 1.0))
        pbar = (p0 + p1) / 2.0
        required = z_alpha * math.sqrt(2.0 * pbar * (1.0 - pbar)) + z_beta * math.sqrt(
            p0 * (1.0 - p0) + p1 * (1.0 - p1)
        )
        if (p1 - p0) * root_n >= required:
            return round(ror, 10)
    return math.inf


def _get(row: Mapping[str, Any] | Any, key: str, default: Any = None) -> Any:
    """Read ``key`` from a mapping, a pandas Series, or a namedtuple-like row."""
    try:
        return row[key]
    except (TypeError, KeyError, IndexError):
        return getattr(row, key, default)


def _truthy(value: Any) -> bool:
    if isinstance(value, str):
        return value.strip().lower() in {"true", "t", "yes", "y", "1"}
    return bool(value)


def assign_tier(row: Mapping[str, Any] | Any) -> str:
    """Assign the evidence tier for one pair, in the documented rule order.

    Reproduces the shipped ``evidence_tier`` column for all 797 rows. The
    rules are evaluated strictly in this order, and the first match wins::

        1. excluded_clinical is true            -> EXCLUDED_clinical
        2. faers_coreports < 25                 -> T4_uninformative
        3. both_pk_inert is true                -> T3_trivial_inert
        4. faers_coreports >= 500
             and min_detectable_ror <= 3.0      -> T1_wellpowered
        5. faers_coreports >= 100               -> T2_moderate
        6. otherwise                            -> T3_limited

    Rule 1 precedes every evidence rule: a pair excluded on clinical
    grounds is excluded regardless of how well powered it is. Rule 2
    precedes rule 3 so that a pair with too little co-exposure to say
    anything is reported as uninformative rather than as trivially inert.

    Parameters
    ----------
    row : mapping or pandas Series or namedtuple-like
        Must expose ``faers_coreports``, ``both_pk_inert`` and
        ``excluded_clinical``. ``min_detectable_ror`` is read if present and
        otherwise recomputed from ``faers_coreports`` with the defaults of
        :func:`min_detectable_ror`.

    Returns
    -------
    str
        One of the six values in :data:`TIER_ORDER`.

    Examples
    --------
    >>> assign_tier({"faers_coreports": 2019, "min_detectable_ror": 2.15,
    ...              "both_pk_inert": False, "excluded_clinical": False})
    'T1_wellpowered'
    >>> assign_tier({"faers_coreports": 19544, "min_detectable_ror": 1.35,
    ...              "both_pk_inert": False, "excluded_clinical": True})
    'EXCLUDED_clinical'
    >>> assign_tier({"faers_coreports": 11, "min_detectable_ror": float("inf"),
    ...              "both_pk_inert": False, "excluded_clinical": False})
    'T4_uninformative'
    """
    if _truthy(_get(row, "excluded_clinical", False)):
        return "EXCLUDED_clinical"

    raw = _get(row, "faers_coreports", None)
    try:
        n = float(raw)
    except (TypeError, ValueError):
        n = float("nan")
    if not math.isfinite(n):
        n = -1.0

    if n < 25:
        return "T4_uninformative"

    if _truthy(_get(row, "both_pk_inert", False)):
        return "T3_trivial_inert"

    mdror = _get(row, "min_detectable_ror", None)
    if mdror is None:
        mdror = min_detectable_ror(n)
    else:
        try:
            mdror = float(mdror)
        except (TypeError, ValueError):
            mdror = min_detectable_ror(n)

    if n >= 500 and math.isfinite(mdror) and mdror <= 3.0:
        return "T1_wellpowered"
    if n >= 100:
        return "T2_moderate"
    return "T3_limited"
