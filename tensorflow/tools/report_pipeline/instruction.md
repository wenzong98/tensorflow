# Restore historical report reproducibility

A production analytics service evaluates short computation plans built from
TensorFlow GraphDef-compatible operations, specializes some jobs based on
runtime input characteristics, and stores reusable execution artifacts.
Customers report that the same report can produce different values when
replayed after unrelated workloads or after a process restart. Some incidents
only occur when workers share a persistent cache. Normal requests generally
complete without error.

Investigate the runtime under tensorflow/python/eager/plan_runtime and the
report entry points under tensorflow/tools/report_pipeline. Repair the
underlying causes, not only the demonstration workload. The implementation must
support valid input lengths, backend settings, caller mutation after
compilation, overlapping workers, corrupted persisted artifacts, and restarts.

For all valid plans and histories, execution results must match the independent
specification in reference.py, with exact integers and absolute float tolerance
1e-9. Previously compiled programs must preserve their original behavior.
Compatible optimized artifacts should be reusable across restarts, valid
optimizations must stay enabled, and repeated jobs must retain cache hits.

Do not modify ir.py, reference.py, or public interfaces. Do not route compiled
execution through the reference implementation, disable optimization, disable
caching, or hardcode workload-specific answers. CPU-only execution must work
using standard Python.

To reproduce an example run the history_replay report entry point.
