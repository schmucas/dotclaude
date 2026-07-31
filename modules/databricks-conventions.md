# Databricks conventions

Import this into a project `CLAUDE.md` with:

```
@~/.claude/modules/databricks-conventions.md
```

TODO: fill in. This is the shared prose you would otherwise retype in every
Databricks project. Candidates:

- Python declarative pipelines only, `pyspark.pipelines` / `@dp.table`.
- Unity Catalog only. `/Volumes/<cat>/<schema>/<vol>/` paths, never DBFS.
- Serverless compute only, no cluster configuration.
- Trunk based git flow, bundle targets are not branches.
