# RIDI Audit Minimum Reporting Standard v1

A study may describe an analysis as a **representation-aware decision reproducibility audit** only when it reports all required elements below.

1. **Freeze source evidence (S).** Identify the exact evidence-bearing records used in both arms, with version and integrity hash where feasible.
2. **Define the representation intervention (R0 → R1).** State exactly what changes and what does not. Distinguish nominal relabelling, structural remapping, compression and learned representation changes.
3. **Freeze inference and decision context (F, C).** Keep the inference procedure, candidate identities, decision rule and pre-specified cutoffs fixed within the contrast, or explicitly model any randomness Z.
4. **Report conventional performance.** Provide the task-appropriate aggregate metric(s) so decision turnover is not confused with ordinary performance collapse.
5. **Report decision identity.** Report RIDI and changed slots at every pre-specified cutoff, with deterministic tie handling and the common candidate universe made explicit.
6. **Run an invariance control.** Include a transformation expected to preserve the computation (for example, a bijective relabelling or coordinate permutation) and verify zero decision turnover within the declared numerical tolerance.
7. **Check the margin certificate when score vectors are comparable.** Report γ_k, ε and whether γ_k > 2ε certifies stability.
8. **Calibrate learned systems against stochasticity.** Compare R0→R1 turnover with same-representation retraining variability using pre-specified seeds or ensembles; do not attribute turnover to representation when it is statistically indistinguishable from the retraining null.
9. **Preserve adverse outcomes and protocol lineage.** Report failed controls, null results and implementation corrections without replacing the original confirmatory estimand post-outcome.

The minimum interpretive claim is: **decision identity is or is not invariant under the stated representation intervention**. The audit alone does not establish clinical harm, causal utility or superiority of one representation.
