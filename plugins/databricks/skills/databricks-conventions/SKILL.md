---
name: databricks-conventions
description: Cross-cutting Databricks platform conventions — Unity Catalog vs DBFS, bundle/target hygiene, secrets and PII handling — that apply to any Databricks code or databricks.yml, regardless of whether it's a Lakeflow Declarative Pipeline, a Lakeflow Job/notebook task, or something else. This is the shared baseline lakeflow-review and lakeflow-jobs both build on; load it alongside whichever of those matches the task rather than as a standalone trigger.
---

# Databricks platform conventions

Rules that hold across every kind of Databricks work in this environment — pipelines,
jobs, notebooks, DAB YAML. Task-specific skills (`lakeflow-review` for reviewing
Lakeflow Declarative Pipelines, `lakeflow-jobs` for writing notebook tasks/jobs) build
on these instead of repeating them.

## Unity Catalog only, no DBFS

Flag any of: `/dbfs/`, `/mnt/`, `dbutils.fs.*`, bare `/tmp/`, `dbfs:/`.

Expected shapes: `<catalog>.<schema>.<table>` tables and
`/Volumes/<catalog>/<schema>/<volume>/` paths.

This is a blocker wherever it appears — pipeline code, notebook tasks, or ad hoc
scripts alike.

## Bundle hygiene

- Hardcoded workspace URLs, catalog names or paths that should be target variables.
- Missing or inconsistent `dev` / `stage` / `prod` targets.
- `mode: development` missing on the dev target.
- Resource names that will collide across targets (no `${bundle.target}` or
  `${workspace.current_user.short_name}` prefix where one is needed).

## Secrets and PII

Flag any literal token, PAT, connection string, key, password, or personal data in
code, YAML, notebooks, or committed config. PATs belong in GitHub Environment
secrets or a Databricks secret scope (`dbutils.secrets.get(...)`), never hardcoded.
