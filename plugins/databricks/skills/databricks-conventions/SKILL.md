---
name: databricks-conventions
description: Luca's project-specific Databricks rules, the ones that differ from ordinary Databricks practice. Unity Catalog only with no DBFS anywhere, three fixed bundle targets, and secrets handling on Free Edition. Load alongside the vendor databricks-core and databricks-dabs skills, which cover general platform and bundle guidance. This one covers only the deltas, so it does not replace them.
---

# Project conventions

General Databricks and DAB guidance lives in the vendor `databricks-core` and
`databricks-dabs` skills. Defer to those. This file holds only the rules that are
specific to these repos, which no vendor skill knows about.

## Unity Catalog only, no DBFS

Flag any of `/dbfs/`, `/mnt/`, `dbutils.fs.*`, bare `/tmp/`, `dbfs:/`.

Expected shapes: `<catalog>.<schema>.<table>` tables, and
`/Volumes/<catalog>/<schema>/<volume>/` paths.

Blocker wherever it appears. The PreToolUse guard in this plugin already blocks
writes containing these, so if one reaches a review, something bypassed the hook
and that is worth mentioning.

## Bundle targets

Exactly three: `dev`, `stage`, `prod`. Flag a missing target, a fourth one, or
`mode: development` missing on `dev`.

Catalogs, schemas and workspace hosts are target variables, never literals. Resource
names carry `${bundle.target}` or `${workspace.current_user.short_name}` where two
targets share a workspace.

## Secrets

Free Edition has no account console, so authentication is PAT based and OAuth M2M is
not available. PATs belong in a GitHub Environment secret or a Databricks secret
scope, never in code, YAML or committed config. Flag any literal token, connection
string, key, password or personal data.
