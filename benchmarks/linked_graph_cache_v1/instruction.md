# Linked Dynamic Graph Compiler Consistency (LDGCC-5)

Maintain a CPU-only graph compiler with symbolic input lengths, local graph
rewrites, backend-specific code generation, in-process compilation caching,
and persistent compiled artifacts. Public smoke tests pass, but changing shape
contracts, operator parameters, backend options and process restarts can result
in silently incorrect numerical values or invalid specialization reuse.

Fix the root causes while keeping the existing public APIs and valid
optimization behavior.

## Invariants

1. For every valid graph, input and backend option combination, compiled
   execution agrees with `graphcache.reference.evaluate_reference`. Scalar
   arithmetic may use absolute error 1e-9; quantized integers must be exact.
2. Reuse specializations only when the input satisfies their original guards.
   Shape environments can be rebound or widened between calls.
3. Graph rewrites must preserve all explicit nondefault operator attributes.
4. Code-generation-affecting backend options must be part of cache
   equivalence; dictionary insertion order must not affect reuse.
5. Incompatible disk compiler ABI artifacts must not execute. Compatible,
   well-formed artifacts must remain reusable across process restarts.
6. Disabling the optimizer, specialization, or caches entirely is not a valid
   solution. Legal FMA fusion, shape specialization and cache reuse remain.

Edit `/app/graphcache/` and add regression tests if needed. Do not change the
public IR schema or the reference interpreter. Do not use hardcoded outputs.
No network, GPU, or external model service is needed.

Run public tests: `PYTHONPATH=/app python -m unittest discover -s /app/public_tests -v`

Submit code modifications and a concise explanation of the root causes.
