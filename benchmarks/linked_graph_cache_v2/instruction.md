# LDGCC-8: Transactional Dynamic Graph Compiler and Durable Cache

A small CPU graph compiler supports symbolic-shape specialization, fusion, backend option selection, in-memory and disk caches, and process restart. Normal executions pass public tests. Under changes of shape constraints, nondefault node kwargs, mutable inputs, backend switching, concurrent compilation and persistent cache recovery, it produces incorrect values or loses valid specializations.

Your task: repair the implementation in `/app/graphcache` without breaking existing APIs.

## Observable contract

1. Compiled results must agree with `graphcache.reference.evaluate_reference` on valid graphs, with exact integers and abs_tol=1e-9 for float outputs.
2. Specialization can only be executed if actual length is within its full guard. Rebinding shape constraints must not retain stale derived conclusions.
3. Fused operators must preserve explicit nondefault attrs; keep default-value FMA fusion.
4. Backend `extras` that affect execution must participate in compilation identity with order-independent dictionary canonicalization.
5. Persistent entries must validate ABI, graph identity and artifact integrity before execution; valid unchanged entries must be reusable after restart.
6. A compiled program is a snapshot: subsequent mutation of the source graph's nested attributes or backend options must not silently change that program.
7. Multiple disjoint shape specializations with the same graph/options must survive process restart and be selected by full guards.
8. Concurrent writers to the same cache key must not truncate the cache or erase each other's valid specializations. Updates must be atomic and recover from a previously interrupted update.
9. A compile in progress must not mix shape constraints from different rebinding epochs. It may complete using a consistent snapshot of the initial shape contract.

Do not disable fusion, caching, specialization, or disk reuse, and do not simply run the reference interpreter in lieu of compiled specialization. Do not change `reference.py`, public IR schema or public tests. No network/GPU dependencies.

Run: `PYTHONPATH=/app python -m unittest discover -s /app/public_tests -v`.
