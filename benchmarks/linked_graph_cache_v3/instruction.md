# LDGCC-9: Shared Compilation State Contract Under Interleaved Histories

The compiler service intermittently emits incorrect results and loses or misuses
previously compiled artifacts when application-owned graph objects change,
symbolic shape environments are rebound, workers overlap, or the service is
restarted. Multiple components consume the same compilation contract, but
apparently equivalent histories do not always produce equivalent results.

Repair the system while preserving the graph and interpreter specifications.
Investigate the compilation state contract and its consumers, rather than
fixing only the public incident trace. The repair must work across arbitrary
valid sequences of graph/configuration mutation, shape rebindings, parallel
compilation, disk reuse, and interrupted writes.

## Acceptance properties
- Compiled outputs equal the independent reference on valid inputs (floats
  within absolute 1e-9, integer outputs exact).
- A compiled program is immutable relative to later caller-owned changes.
- No stale specialization may execute outside the assumptions under which it
  was compiled; reusable valid specializations survive process restarts.
- Multiple workers sharing the cache cannot silently corrupt or erase valid
  records, including when a worker is interrupted during persistence.
- Valid graph fusion, shape specialization and cache reuse remain operational.
- Avoid broad invalidation: unchanged workloads should reuse artifacts.

Do not modify the reference interpreter, public IR schema, or public tests.
Do not bypass compilation, disable optimization, or return hard-coded results.
No GPU or external service is needed.

Run: `PYTHONPATH=/app python -m unittest discover -s /app/public_tests -v`.

## Additional observed incidents

A service-wide replay reproducer is available at
`PYTHONPATH=/app python /app/incidents/customer_history.py`. Customer-facing reports
may disagree across warmup order, month boundaries, backfills and restarts.
The same external anomaly has been observed in more than one execution history.
Preserve all acceptance requirements; a fix that only matches the sample trace
is insufficient.
