---
name: lakeflow-review
description: Review a Lakeflow Declarative Pipeline transformation or pipeline resource against Luca's project rules: current dp API spelling, Python pipelines only and never SQL, transformations that stay declarative rather than importable. Use when asked to review a transformation file, a pipeline definition, or whether a pipeline change follows project standards. For how declarative pipelines work in general, defer to the vendor databricks-pipelines skill. Pair with databricks-conventions.
---

# Pipeline review

For how Lakeflow Declarative Pipelines work, use the vendor `databricks-pipelines`
skill. This file is only the project rules that skill cannot know, and the review
format.

Report findings. Do not rewrite the code unless explicitly asked.

## Checks

### 1. API spelling (BLOCKER)

Correct: `from pyspark import pipelines as dp` and `@dp.table`.
Legacy: `import dlt` and `@dlt.table`. Functional, but drift, so flag it.

### 2. Python pipelines only (BLOCKER)

Every pipeline is Python. A `.sql` file inside a pipeline's source glob is a
blocker, with no exceptions and no "consider SQL here" suggestions. Ordinary
`spark.sql(...)` inside a Python transformation is fine.

### 3. Transformations stay declarative (WARN)

Transformation files run inside the pipeline. They are not imported. Flag:

- module level factories such as `def build_table(cfg)` meant to be imported
- `if __name__ == "__main__"` blocks
- imports from sibling transformation files
- classes wrapping table definitions

Reusable logic belongs in the utils wheel repo, not here. Do not suggest
refactoring a transformation into a reusable module inside the pipeline, that is
the wrong direction.

## Output format

```
[BLOCKER|WARN|NIT] <file>:<line> - <what is wrong>
  Why: <one line>
  Fix: <one line describing the change, not a rewrite>
```

Say so in one line when a category is clean. Finish with a one line verdict.
