# Runnable example

From `software/ridi-audit` after installation:

```bash
ridi-audit compare \
  --r0 examples/r0.csv \
  --r1 examples/r1.csv \
  --id-col id \
  --score-col score \
  --k 3 5 \
  --out examples/audit.json \
  --report examples/audit.md
```

The example deliberately changes top-3 membership while leaving most of the ranking unchanged. It is intended only to demonstrate the command-line interface and report structure; it is not a scientific benchmark.
