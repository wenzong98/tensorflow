# LDGCC-8.1: Original coupled state/replay engineering task

Run the public tests from `harbor-task`:

```sh
PYTHONPATH=environment python -m unittest discover -s environment/public_tests -v
```

An example reproducible incident is provided under `environment/incidents/`.
The initial implementation is faulty. The reference implementation and hidden
verifier must remain outside the agent-visible filesystem.
