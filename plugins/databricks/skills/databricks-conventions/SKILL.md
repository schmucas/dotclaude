---
name: databricks-conventions
description: User-specific Databricks rules, the ones that differ from ordinary Databricks practice. Unity Catalog only with no DBFS anywhere, three fixed bundle targets, liquid clustering on every Delta table. Load alongside the vendor databricks-core and databricks-dabs skills, which cover general platform and bundle guidance. This one covers only the deltas, so it does not replace them.
---

# Project conventions

General Databricks and DAB guidance lives in the vendor `databricks-core` and
`databricks-dabs` skills. Defer to those. This file holds only the rules that are
specific to these repos, which no vendor skill knows about.

## Unity Catalog only, no DBFS

Flag any of `/dbfs/`, `/mnt/`, `dbutils.fs.*`, bare `/tmp/`, `dbfs:/`.

Expected shapes: `<catalog>.<schema>.<table>` tables, and
`/Volumes/<catalog>/<schema>/<volume>/` paths.

## Bundle targets and environments

Exactly three: `dev`, `stage`, `prod`. Flag a missing target, a fourth one, or
`mode: development` missing on `dev`.

## Liquid clustering on every Delta table

Any time a Delta table gets created, add liquid clustering, regardless of how
it is created: a notebook (`CREATE TABLE`, `saveAsTable`, `writeTo`, a
streaming `toTable`), ad hoc SQL, or a Lakeflow Declarative Pipeline
(`@dp.table`, `@dp.materialized_view`, `create_streaming_table`). Skip it only
when the user explicitly says not to.

Default to AUTO mode. Only pick explicit clustering columns instead when there
is a clear, stable high-cardinality filter or join column to justify it over
AUTO.

- SQL: `CREATE TABLE ... CLUSTER BY AUTO` (or `ALTER TABLE ... CLUSTER BY AUTO`
  on an existing table)
- DataFrame writer: `.option("clusterByAuto", "true")` on `saveAsTable`,
  `writeTo(...).create()`, or a streaming `toTable`
- Declarative pipeline: `@dp.table(cluster_by_auto=True)`, or
  `cluster_by=[...]` for explicit columns (same parameters on
  `@dp.materialized_view` and `create_streaming_table`)

Flag any newly created Delta table missing one of these.
