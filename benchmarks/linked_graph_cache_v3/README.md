# LDGCC-9 V3.3 - Agent-facing task

Read `instruction.md`. The faulty CPU compiler is under `environment/graphcache`.
Run the public tests with:

```sh
PYTHONPATH=environment python -m unittest discover -s environment/public_tests -v
PYTHONPATH=environment python environment/incidents/customer_history.py
```

The independent private tests and Oracle implementation are held by the task
owner. Do not expect them in this task package.
