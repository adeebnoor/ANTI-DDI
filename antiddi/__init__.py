"""Anti-DDI v2: a tiered negative-control resource for drug-drug interaction research.

The package provides two things: the evidence-tier primitives that generated
the shipped dataset (:mod:`antiddi.evidence`) and the degree-controlled
evaluation protocol that the resource exists to make possible
(:mod:`antiddi.benchmark`).

The dataset is an evaluation and benchmarking resource. It does not license
the co-prescription of any pair, and no output of this package constitutes a
clinical recommendation.
"""

from __future__ import annotations

__version__ = "2.0.0"

from .evidence import (  # noqa: F401
    ANCHOR_DRUGS,
    FAERS_DENOMINATOR,
    TIER_ORDER,
    USABLE_TIERS,
    assign_tier,
    min_detectable_ror,
)
from .benchmark import (  # noqa: F401
    DEFAULT_DEGREE_BINS,
    ArmResult,
    EvaluationReport,
    auc_mann_whitney,
    compute_degrees,
    degree_matched_sample,
    evaluate,
    sample_random_negatives,
)

__all__ = [
    "__version__",
    "min_detectable_ror",
    "assign_tier",
    "ANCHOR_DRUGS",
    "FAERS_DENOMINATOR",
    "TIER_ORDER",
    "USABLE_TIERS",
    "evaluate",
    "degree_matched_sample",
    "compute_degrees",
    "sample_random_negatives",
    "auc_mann_whitney",
    "ArmResult",
    "EvaluationReport",
    "DEFAULT_DEGREE_BINS",
]
