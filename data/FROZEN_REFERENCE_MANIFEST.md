# Frozen ATC5 positive-reference manifest

The structural-bias analysis uses a frozen set of **8,094 unique unordered ATC level-5 positive class pairs over 437 ATC5 nodes** derived from the GoldD2ATC reference shipped with the accompanying reproducibility archive.

- Frozen CSV filename: `goldd2_atc5_positive_reference.csv`
- Rows (excluding header): 8,094
- Columns: `atc5_a,atc5_b`
- SHA-256: `1f96a2c3197db78ea7fe31444efec2e4c4cfffb19a5f1fed7bd2d0ca56166018`
- Construction: collapse each GoldD2ATC drug pair to the first five characters of each valid ATC code, remove self-pairs, sort the two members of each pair, and deduplicate.
- Use: input to `analysis/run_degree_bias_atc5.py` only.

The exact frozen CSV is included in the manuscript's Supplementary Code and Data archive. The repository stores the analysis code, replicate output and summary; the checksum above allows the input file to be verified byte-for-byte.

This ATC5 reference is a structural evaluation asset, not a clinical ground-truth set for non-interaction.
