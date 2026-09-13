"""RIDI audit: representation-aware decision reproducibility."""
from .core import ridi, changed_slots, deterministic_topk, margin_certificate, audit_scores
__all__ = ["ridi", "changed_slots", "deterministic_topk", "margin_certificate", "audit_scores"]
__version__ = "0.2.0"
