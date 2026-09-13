import numpy as np
from ridi_audit import ridi, changed_slots, deterministic_topk, margin_certificate, audit_scores


def test_ridi_identity_and_disjoint():
    assert ridi(['a','b'], ['a','b']) == 0
    assert ridi(['a','b'], ['c','d']) == 1


def test_tie_break_is_identity_deterministic():
    ids=['z','a','m']; scores=[1,1,0]
    assert deterministic_topk(ids,scores,2) == ['a','z']


def test_margin_certificate():
    ids=['a','b','c','d']; a=np.array([4.,3.,1.,0.]); b=a+np.array([.1,-.1,.1,-.1])
    c=margin_certificate(a,b,ids,2)
    assert c['certified_stable']
    out=audit_scores(ids,a,b,[1,2])
    assert out['cutoffs'][1]['ridi'] == 0
