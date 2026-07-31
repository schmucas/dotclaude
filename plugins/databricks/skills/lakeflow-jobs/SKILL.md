---
name: lakeflow-jobs
description: Write or develop a Databricks Workflows job, notebook task — orchestration and ETL logic that runs as a notebook or multi-task job on Databricks. Use whenever asked to write/build/create a Databricks notebook, task, or job. Do NOT use this for Lakeflow Declarative Pipelines (DLT / SPD / declarative pipeline) — those follow separate conventions (see lakeflow-review). Pair with the databricks-conventions skill for the cross-cutting Unity Catalog, bundle hygiene, and secrets checks that apply to any Databricks code, not just pipelines.
---

# Lakeflow Jobs / notebook task development

## Writing Style
- always use the data frame api in pyspark. dont write spark sql
- write df tranformations in a clear and human readable way like 
in this example:

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

## Notebook structure

- imports at the top and in a separate cell
- keep logical steps in separate cells like imports, configs, functions, data frame transformations
- in the second cell from the top, add constants
- add configs to the third and 4th cell

Example cell layout, shown in Databricks' notebook source format:

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