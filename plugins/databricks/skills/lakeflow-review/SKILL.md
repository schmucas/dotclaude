---
name: lakeflow-review
description: Review Databricks Lakeflow Declarative Pipeline code and Declarative Automation Bundle (DAB) YAML against pipeline-specific conventions (API spelling, SQL vs Python, declarative structure, wheel tasks, serverless assumptions). Use when reviewing a transformation file, a pipeline resource definition, or when the user asks whether a pipeline change follows project standards. Pair with the databricks-conventions skill for the cross-cutting Unity Catalog, bundle hygiene, and secrets checks that apply to any Databricks code, not just pipelines.
---

# Lakeflow / DAB review

Review the supplied Databricks code or YAML against the checks below. Report only
findings. Do not rewrite the user's code unless explicitly asked.

## Output format

For each finding:

```
[BLOCKER|WARN|NIT] <file>:<line> - <what is wrong>
  Why: <one line>
  Fix: <one line, describe the change, do not paste a full rewrite>
```

If nothing is found in a category, say so in one line. Finish with a one line verdict.

## Checks

Cross-cutting checks (Unity Catalog vs DBFS, bundle hygiene, secrets/PII) live in the
`databricks-conventions` skill and apply here too — run those alongside the
pipeline-specific checks below.

### 1. Pipeline API spelling (BLOCKER)

Declarative pipelines must use the current API:

- Correct: `from pyspark import pipelines as dp` and the `@dp.table` decorator.
- Legacy: `import dlt` and `@dlt.table`. Still functional, but flag it as drift.

Lakeflow Declarative Pipelines is the current name for what used to be DLT.

### 2. No SQL pipelines (BLOCKER)

All pipeline logic is Python. A `.sql` file included in a pipeline's source glob is
a blocker. Ordinary `spark.sql(...)` calls inside a Python transformation are fine.

### 3. Transformations stay declarative (WARN)

Transformation files run inside the pipeline, they are not imported. Flag any of:

- module level `def build_table(cfg)` factories intended to be imported
- `if __name__ == "__main__"` blocks
- imports from sibling transformation files
- classes wrapping table definitions

Reusable, testable logic belongs in the separate utils wheel, not here.
