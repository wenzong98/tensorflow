# LDGCC-8 v2: transactional compilation and persistent cache consistency

This is an **independently authored CPU-only engineering benchmark** in a TensorFlow fork. It does not modify TensorFlow core. V1 is retained separately.

From `benchmarks/linked_graph_cache_v2`, run:
```sh
PYTHONPATH=environment python -m unittest discover -s environment/public_tests -v
```

Public smoke tests are intentionally insufficient to discover the linked bugs. Source of truth for execution semantics is the unoptimized reference interpreter. Repair the graph compiler, cache, and shape analysis without disabling optimizations.

**Oracle and private verifier are kept outside the public GitHub branch**; only the benchmark author delivery ZIP contains them. The task was tested with Python on Linux; Docker/Harbor and Apple Silicon execution remain unverified.

Research inputs:
- PyTorch symbolic shape cache: https://github.com/pytorch/pytorch/pull/202505
- PyTorch autotune identity: https://github.com/pytorch/pytorch/pull/201695
- PyTorch pattern matcher attrs: https://github.com/pytorch/pytorch/pull/199871
