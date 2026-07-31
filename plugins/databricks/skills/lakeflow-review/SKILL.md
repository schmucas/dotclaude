---
name: lakeflow-review
description: Review Databricks Lakeflow Declarative Pipeline code, Declarative Automation Bundle (DAB) YAML, and Unity Catalog usage against a fixed set of conventions. Use when reviewing a transformation file, a databricks.yml, a job or pipeline resource definition, or when the user asks whether a Databricks change follows project standards.
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

### 4. No wheel task (BLOCKER)

`python_wheel_task` and any `artifacts:` block in `databricks.yml` are out of scope
for the bundle. `notebook_task`, `pipeline_task`, and other task types are fine and
expected. A job mixing task types is not drift.

### 5. Unity Catalog only, no DBFS (BLOCKER)

Flag any of: `/dbfs/`, `/mnt/`, `dbutils.fs.*`, bare `/tmp/`, `dbfs:/`.

Expected shapes: `<catalog>.<schema>.<table>` tables and
`/Volumes/<catalog>/<schema>/<volume>/` paths.

### 6. Bundle hygiene (WARN)

- Hardcoded workspace URLs, catalog names or paths that should be target variables.
- Missing or inconsistent `dev` / `stage` / `prod` targets.
- `mode: development` missing on the dev target.
- Resource names that will collide across targets (no `${bundle.target}` or
  `${workspace.current_user.short_name}` prefix where one is needed).

### 7. Secrets and PII (BLOCKER)

Flag any literal token, PAT, connection string, key, password, or personal data in
code, YAML, notebooks, or committed config. PATs belong in GitHub Environment
secrets or a Databricks secret scope.

### 8. Serverless assumptions (NIT)

Target environment is serverless only. Flag cluster policy references, instance
type or worker count settings, and init scripts, since none of those apply.

## Notes

- Do not propose SQL alternatives, ever.
- Do not propose extracting logic into this repo as an importable package. Point at
  the utils wheel instead.
- Notebook tasks inside jobs are expected. Do not flag them.
