from pathlib import Path
root=Path(__file__).resolve().parent
models=(root/'src/models.py').read_text(); loaders=(root/'src/loaders.py').read_text(); protocol=(root/'PROTOCOL_LOCK_EXTERNAL_REPLICATION.md').read_text(); protos=(root/'src/protocols.py').read_text()
for bad in ['LogisticRegression','MLPClassifier','train_test_split']:
    assert bad not in models, f'supervised evaluation leakage token present: {bad}'
assert 'M0_popularity' in models and 'M7_diffusion_svd' in models
assert 'P3_degree_matched' in protos and 'P5_config_rewire' in protos
assert 'N=N-P' in loaders.replace(' ','')
assert 'not an OSF preregistration' in protocol
assert 'Holm' in protocol and 'at least 6/8' in protocol
print('PASS: graph-only scoring, explicit pair-level CRESCENDDI aggregation, multiplicity control, and external interpretation boundaries are locked.')
