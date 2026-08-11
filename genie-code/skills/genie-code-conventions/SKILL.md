---
name: genie-code-conventions
description: Org-specific Databricks rule that differs from ordinary practice, Unity Catalog only with no DBFS anywhere. Use whenever Genie Code writes or reviews code across notebooks, the SQL editor, Lakeflow Pipelines, or dashboards in this workspace.
---

# Project conventions

The rule specific to this workspace, on top of Genie Code's own general Databricks
knowledge.

## Unity Catalog only, no DBFS

Flag any of `/dbfs/`, `/mnt/`, `dbutils.fs.*`, bare `/tmp/`, `dbfs:/`.

Expected shapes: `<catalog>.<schema>.<table>` tables, and
`/Volumes/<catalog>/<schema>/<volume>/` paths.

Applies everywhere Genie Code writes a path or a table reference: notebooks, the
SQL editor, pipeline transformations, and dashboard datasets.
