---
name: lakeflow-jobs
description: Luca's house style for writing Databricks notebooks and job tasks: DataFrame API only and never Spark SQL, and a fixed cell layout with imports, constants and configs in the first four cells. Use whenever writing or editing a Databricks notebook or job task. For job orchestration itself, task types, triggers and schedules, defer to the vendor databricks-jobs skill. Not for declarative pipelines, see lakeflow-review.
---

# Notebook house style

Task types, triggers, schedules and notifications are covered by the vendor
`databricks-jobs` skill. This file is only how the notebook itself should read.

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
