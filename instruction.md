# Restore a deterministic analytics execution service

A CPU service executes short mathematical data-processing plans. Customers
occasionally observe that reproducing a saved report yields a different value
from its first execution. Other incidents involve older monthly reports that
cannot be reproduced after a service restart, even though the original input
and requested operation have not changed. Failures correlate with mixed
workloads and periods of higher concurrency, but individual requests often
complete successfully.

Investigate and repair the implementation under `/app/graphcache/`. The
historical workload in `/app/incidents/customer_history.py` is an example of
an observed customer report, not an exhaustive description of the incidents.

**Required behavior:** For valid plans and configurations, execution results
must agree with the independent computation semantics in
`graphcache.reference.evaluate_reference` (exact integer results and floating
results within 1e-9 absolute error). Previously created programs must remain
semantically stable even if caller-owned data structures are later modified.
The service must support changes in input size, different processing settings,
concurrent workers using the same storage directory, and restarts. A successful
repair must preserve efficient repeat execution: equivalent jobs should avoid
unnecessary recompilation and legally optimized plans should still be used.

Preserve public interfaces and the existing input representation. Do not edit
`graphcache/reference.py` or `graphcache/ir.py`, replace the service with a
reference-interpreter call, disable the cache or optimization subsystem, or
hardcode workload-specific output. The solution must use only Python standard
library modules and work on a CPU-only Linux environment.

You may run the sample incident with:

`PYTHONPATH=/app python /app/incidents/customer_history.py`

Changes should be made in `/app/graphcache/`.
