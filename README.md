# Pathways

A dependency-free Python CLI that offers a next-step recommendation from the synthetic data in `SPEC.md`.

Run the app with:

```powershell
python pathways.py
```

Run the acceptance tests with:

```powershell
python -m unittest -v
```

The name, age, advisor note, and raw question are never included in the mock model prompt. The free-text question is classified locally into a controlled topic. Each mock call appends its exact prompt and response to `model-calls.log` in the current directory.