"""Anti-DDI v3.0.1: evidence framework and benchmark resource for drug non-interaction.

The package provides evidence-tier primitives and degree-controlled evaluation
tools. Anti-DDI is a research evidence framework, not a prescribing safety list.
The classifier/RIDI experiment documented in v3.0.0 is superseded and is not
validation evidence; see VALIDATION_NOTICE_20260820.md.
"""
from __future__ import annotations

__version__ = "3.0.1"

from .evidence import (  # noqa: F401
    ANCHOR_DRUGS, FAERS_DENOMINATOR, TIER_ORDER, USABLE_TIERS, assign_tier, min_detectable_ror,
)
from .benchmark import (  # noqa: F401
    DEFAULT_DEGREE_BINS, ArmResult, EvaluationReport, auc_mann_whitney, compute_degrees,
    degree_matched_sample, evaluate, sample_random_negatives,
)

__all__ = [
    "__version__", "min_detectable_ror", "assign_tier", "ANCHOR_DRUGS",
    "FAERS_DENOMINATOR", "TIER_ORDER", "USABLE_TIERS", "evaluate",
    "degree_matched_sample", "compute_degrees", "sample_random_negatives",
    "auc_mann_whitney", "ArmResult", "EvaluationReport", "DEFAULT_DEGREE_BINS",
]
