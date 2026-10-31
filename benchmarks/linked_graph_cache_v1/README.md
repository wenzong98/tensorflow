# LDGCC-5 — Linked Dynamic Graph Compiler Consistency

A CPU-only independent graph compiler task housed in a TensorFlow fork.
**This is not a modification of TensorFlow core**. It is a reproducible,
purpose-built engineering challenge with coupled compiler/cache failures.

To run on macOS or Linux with Python 3.10+:

```sh
cd benchmarks/linked_graph_cache_v1
PYTHONPATH=environment python -m unittest discover -s environment/public_tests -v
```

Public smoke tests pass on the deliberately faulty snapshot; they are not
a full acceptance suite. A private authoring bundle with the reference
solution and verifier is provided separately to the benchmark owner, and
is not included in this public branch.

Research inspiration (not direct reproductions of upstream fixes):
- https://github.com/pytorch/pytorch/pull/202505
- https://github.com/pytorch/pytorch/pull/201695
- https://github.com/pytorch/pytorch/pull/199871

No TensorFlow build, CUDA, MPS, or third-party Python package is required.
