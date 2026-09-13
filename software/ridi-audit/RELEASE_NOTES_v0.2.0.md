# ridi-audit v0.2.0

Release-candidate changes for the Nature submission:

- preserves the original deterministic RIDI and top-k audit core;
- adds a human-readable Markdown audit report alongside JSON output;
- reports changed decision slots, overlap, global Spearman agreement, gamma_k and epsilon;
- labels the sufficient margin certificate as PASS only when gamma_k > 2 epsilon;
- includes the eight-element minimum reporting standard;
- adds CITATION.cff and explicit source metadata;
- retains the interpretation rule that learned systems require a same-representation retraining null before attributing turnover to representation.

Scientific results and locked experiment endpoints were not changed by this software-reporting update.
