# Cover letter draft — Science

**Internal status:** do not submit until S6 contemporary-model result is frozen and the repository release/DOI is complete. Remove this line before submission.

Dear Editors,

Biomedical artificial intelligence increasingly determines which molecular hypotheses receive experimental attention, but the benchmarks used to select those models are usually treated as passive measuring instruments. In our Research Article, **“Benchmark design redirects biomedical discovery,”** we show that benchmark construction can itself become part of the scientific decision process: it can change which model is selected and, through that selection, which biology reaches the front of the experimental queue.

Across drug–target, protein–protein, compound–disease and disease–gene relation families, structural observability alone produced strong apparent discrimination under conventional sampled-unknown evaluation, and learned models depended on that signal unequally. In stability-controlled drug–target and protein-interaction analyses, changing the evaluation reversed the selected model and changed 100% and 99% of the respective top-100 hypotheses, far beyond within-model ensemble variability. We then tested whether this decision difference had consequences beyond benchmark scores. In a frozen historical BioGRID network, the model selected after structural neutralization recovered 522 of 5,635 interactions added in a later release among its top 50,000 candidates, compared with 181 for the conventional winner. In a separate ChEMBL 37 evidence source that was not used for fitting or model selection, the same selection principle concentrated more supported drug–target relations at the highest-priority experimental cutoffs; importantly, the advantage did not persist at broad cutoffs, a boundary we report explicitly.

We believe the work is of broad interest because it connects a known class of benchmark vulnerabilities to a previously unmeasured scientific consequence. The central advance is not another correction for degree bias or negative sampling. It is the demonstrated chain from **benchmark structure to model identity, hypothesis identity and later or independent evidence**. The manuscript includes non-reversal and instability controls, preserves adverse boundary results, and provides frozen code, data provenance and complete candidate-universe analyses designed to make the decision chain auditable. The study is distinct in question, evidence and principal conclusion from our separate work on Anti-DDI and allocation/representation identity; these related materials will be disclosed transparently at submission.

Thank you for considering our manuscript for publication in *Science*.

Sincerely,

Adeeb Noor
Department of Information Technology
Faculty of Computing and Information Technology
King Abdulaziz University
Jeddah, Saudi Arabia