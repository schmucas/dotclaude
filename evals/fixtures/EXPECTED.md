# Expected findings

What a correct review of `bad_transformation.py` must report. Use it as the answer
key when checking output quality:

```
Review evals/fixtures/bad_transformation.py, then compare against
evals/fixtures/EXPECTED.md and list anything you missed.
```

Severity is the level the skill should assign, not merely whether it noticed.

| ID | Line | Violation | Severity | Owning skill or agent |
|---|---|---|---|---|
| V1 | 8, 12, 17 | `import dlt` and `@dlt.table`, legacy API spelling | BLOCKER | lakeflow-review |
| V2 | 15 | `/dbfs/mnt/` path, should be a UC Volume | BLOCKER | databricks-conventions |
| V3 | 20 | Hardcoded catalog and schema instead of a target variable | WARN | databricks-conventions |
| V4 | 23 | PAT literal in source | BLOCKER | security-scanner |
| V5 | 27 | `collect()` on an unbounded read, driver OOM at scale | HIGH | cost-perf-auditor |
| V6 | 30 | `withColumn` in a Python loop, deep plan | MED | cost-perf-auditor |
| V7 | 36 | SCD2 join ignoring the validity interval, silent fanout | BLOCKER | lakeflow-review |
| V8 | 39 | `repartition` on a high cardinality column | MED | cost-perf-auditor |
| V9 | 44 | `dbutils.fs`, DBFS era | BLOCKER | databricks-conventions |

## Which ones actually matter

V7 is the case worth watching. Everything else is a pattern match that a grep could
approximate, and a review that only ever catches those is not doing more than the
hook already does. V7 compiles, runs, and produces wrong numbers quietly. If the
review misses V7 while catching the other eight, the skill is not yet earning its
place.

V4 should be reported by `security-scanner` rather than a Databricks skill. If a
Databricks skill claims it first, the descriptions are overlapping and one of them
needs narrowing.

## Adding a fixture

One planted violation per line, numbered `V<n>` in a comment, and a row here. Keep
each fixture focused on one review surface, since a fixture that breaks every rule
at once cannot tell you which rule stopped working.
