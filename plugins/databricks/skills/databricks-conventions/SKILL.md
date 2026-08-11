---
name: databricks-conventions
description: User-specific Databricks rules, the ones that differ from ordinary Databricks practice. Unity Catalog only with no DBFS anywhere, three fixed bundle targets. Load alongside the vendor databricks-core and databricks-dabs skills, which cover general platform and bundle guidance. This one covers only the deltas, so it does not replace them.
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
