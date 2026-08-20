"""Anti-DDI v3: an evidence framework and benchmark resource for drug non-interaction.

The package preserves the v2 evidence-tier and degree-controlled benchmarking
primitives while v3 adds explicit knowledge-state semantics and frozen Paper 5
release tables at the repository level.

Anti-DDI is a research evidence framework. It is not a prescribing safety list,
and no output of this package constitutes a clinical recommendation.
"""

from __future__ import annotations

__version__ = "3.0.0"

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
