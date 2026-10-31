# LDGCC-8.1 — Dynamic Compiler Replay Consistency

## Engineering incident

A CPU graph compiler specializing symbolic input lengths intermittently returns
numerically incorrect values when used as a long-lived service. A restart may
change the result even if the graph, input and backend configuration are
unchanged. Multiple workers sharing a cache sometimes lose previously usable
compiled programs. Source graphs and backend options are application-owned and
may be mutated after a program is compiled.

The incident reproduction utility in `incidents/replay_incident.py` illustrates
an affected workload. The public smoke tests pass on the initial repository.
The bug may involve multiple stages of the compilation and execution pipeline.

## Goal

Repair the pipeline in `/app/graphcache/` so that correct results and valid
specialization reuse hold for arbitrary valid graph inputs and histories,
including shape changes, backend changes, process restarts, concurrent workers,
and interrupted persistent-cache updates. Keep existing public interfaces.

## Required observable properties

- Compiled execution agrees with the independent reference semantics in
  `graphcache.reference.evaluate_reference` (integer outputs exact, floating
  outputs absolute tolerance 1e-9). The reference is a specification of
  computation, **not a permitted replacement for the compilation process**.
- A compiled program retains the behavior of the graph and backend configuration
  captured at its compilation boundary, regardless of later caller mutation.
- Reuse is permitted only while the exact assumptions of the existing compiled
  program remain valid. Rebinding a symbolic environment or replaying a disk
  artifact must not silently change semantics.
- Concurrent independent compiler instances may share a persistent cache.
  Valid artifacts must survive restarts and overlapping writes without yielding
  incorrect execution. Damaged or incompatible records must not be executed.
- Existing valid optimizations and specializations remain enabled. Normal
  repeated workloads must continue to produce observable cache hits, and
  disjoint valid specializations must be reusable after restart.

## Constraints

Do not modify `graphcache/reference.py`, `graphcache/ir.py`, public tests, or
input/output APIs. Do not disable fusion or the caches, return hard-coded
answers, or execute every graph through the reference interpreter. You may
modify the compiler, optimizer, shape environment and cache implementation.
No network, GPU or external models are required.

Public checks: `PYTHONPATH=/app python -m unittest discover -s /app/public_tests -v`.
