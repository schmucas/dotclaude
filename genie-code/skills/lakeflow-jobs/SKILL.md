---
name: genie-code-lakeflow-jobs
description: "House style for Databricks notebooks and job tasks: DataFrame API only, never Spark SQL, with a fixed cell layout (imports, constants and configs in the first four cells). Use whenever Genie Code writes or edits a notebook or job task. Not for the SQL editor, where SQL is the point, and not for declarative pipelines"
---

# Notebook house style

Applies to the notebook and job-task surface only, not the SQL editor, where
writing SQL is expected. Task types, triggers, schedules and notifications are
covered by Genie Code's own built-in Databricks knowledge. This file is only how
the notebook itself should read.

## DataFrame API, never Spark SQL

Always the PySpark DataFrame API. Do not write `spark.sql("SELECT ...")` in a
notebook task, and do not offer it as an alternative.

Chain transformations one operation per line, parenthesised:

```python
# COMMAND ----------
df = (
    spark.readStream
    .option("readChangeFeed", "true")
    .option("startingVersion", 0)
    .table(source_table)
    .withColumn("_ingested_at", F.current_timestamp())
    )
```

## Cell layout

One logical step per cell, in this order. Imports first and alone, constants second,
configs third and fourth, then derived names, then transformations.

```python
# Databricks notebook source
from pyspark.sql import functions as F
from pyspark.sql import DataFrame

# COMMAND ----------
#Constants
SOURCE_TABLE_NAME = "customers"
TABLE_NAME = "customers_raw"
SCHEMA = "bronze"
INGEST_CATALOG = "sl_ingest"

# COMMAND ----------
#Configs
configs = dict(dbutils.notebook.entry_point.getCurrentBindings())
ENV = configs.get('env', 'dev')
INITIAL_RUN = configs.get('initial_run', 'False').lower() == "true"

CATALOG        = f"sl_{ENV}"
CHECKPOINT_BASE = f"/Volumes/{CATALOG}/{SCHEMA}/checkpoints"

print(f"ENV={ENV} | source schema: {INGEST_CATALOG}.{ENV} | catalog: {CATALOG} | checkpoints: {CHECKPOINT_BASE}")

# COMMAND ----------
source_table = f"{INGEST_CATALOG}.{ENV}.{SOURCE_TABLE_NAME}"
target_table = f"{CATALOG}.{SCHEMA}.{TABLE_NAME}"
checkpoint_path = f"{CHECKPOINT_BASE}/{TABLE_NAME}/"
print(source_table, target_table, checkpoint_path)
```

Catalog and schema come from a config cell, never hardcoded mid-notebook.
Checkpoints live under a UC Volume, never DBFS.
