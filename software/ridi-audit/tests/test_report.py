from ridi_audit.core import audit_scores
from ridi_audit.report import render_markdown_report


def test_markdown_report_contains_core_audit_fields():
    ids = ["a", "b", "c", "d"]
    r0 = [4.0, 3.0, 2.0, 1.0]
    r1 = [4.0, 2.0, 3.0, 1.0]
    res = audit_scores(ids, r0, r1, [1, 2])
    text = render_markdown_report(res)
    assert "RIDI decision-reproducibility audit" in text
    assert "Global Spearman agreement" in text
    assert "Changed slots" in text
    assert "Margin certificate" in text
    assert "| 2 |" in text
