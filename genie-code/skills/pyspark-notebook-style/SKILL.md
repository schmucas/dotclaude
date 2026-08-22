---
name: pyspark-notebook-style
description: "LOAD THIS FIRST when user says: 'create [a/two/bronze/silver] table(s)', 'build [two/N] dataset(s)', 'generate [N/10M] records', 'create inventory and sales tables', 'use PySpark DataFrame API', 'build a pipeline', or any request to create/write/transform data in notebooks. Enforces: Cell 1=imports, Cell 2=config/constants, Cell 3+=one-action-per-cell (never combine CREATE SCHEMA + DataFrame + write in one cell), parentheses style for DataFrames, no hardcoded table names. User has repeatedly complained about code being crammed into one cell - this skill prevents that."
---

# PySpark Notebook Style Guide

## ⚠️ CRITICAL: Load This Skill FIRST

**This skill is MANDATORY and must be loaded BEFORE writing any PySpark notebook code.**

### Trigger Phrases - Load This Skill Immediately When User Says:

* "Create a [bronze/silver/gold] table"
* "Build two datasets"
* "Generate [N] records"
* "Create tables for inventory and sales"
* "Build a pipeline"
* "Transform the data"
* "Write to a table"
* "Use PySpark DataFrame API"
* "Create messy/test/synthetic data"

**If the user mentions tables, datasets, DataFrames, or data generation in notebooks → LOAD THIS SKILL FIRST.**

### Pre-Flight Checklist (Required Before Writing Code)

Before writing ANY notebook code:

1. ✅ Have you loaded the `pyspark-notebook-style` skill?
2. ✅ Will you use Cell 1 for imports only?
3. ✅ Will you use Cell 2 for configuration/constants?
4. ✅ Will you create ONE cell per action (not combine CREATE SCHEMA + DataFrame + write)?
5. ✅ Will you use constants instead of hardcoded table names?

If any answer is "no" or "not sure", load this skill now.

---

This skill defines mandatory coding style and organization standards for PySpark DataFrames in Databricks notebooks.

## Mandatory Standards

This skill enforces three non-negotiable standards:

1. **One Action Per Cell** - Never combine multiple actions (imports + schema creation + DataFrame generation + write) in one cell
2. **Cell 1 = Imports, Cell 2 = Configuration** - All imports in Cell 1, all constants/configs in Cell 2
3. **Parentheses Style** - Use `df = (\n  source\n  .method()\n)` not backslashes

## Core Rule: One Action Per Cell

**CRITICAL**: Every notebook must follow the one-action-per-cell pattern. This is NOT optional.

**Each cell should contain exactly ONE of:**
* One imports block (always cell 1)
* One configuration block (always cell 2)
* One Python function definition
* One read operation (loading a table)
* One transformation DataFrame (df_cleaned, df_enriched, etc.)
* One window specification
* One deduplication/aggregation DataFrame
* One final selection DataFrame
* One write operation
* SQL operations for one table (CREATE TABLE + multiple ALTER statements are fine in one cell; but don't mix CREATE/ALTER with DataFrame writes for the same table)

**Never combine different types of actions in one cell** - e.g., don't mix CREATE TABLE with DataFrame writes, or imports with data processing. However, multiple SQL statements for the same table (CREATE + multiple ALTERs) can share a cell.

### Why This Matters

**Without this skill, you will:**
* Cram imports, CREATE SCHEMA, DataFrame generation, and writes into one cell
* Use hardcoded table names instead of constants
* Make notebooks impossible to debug
* Violate the user's coding standards

**The user has seen this problem multiple times. Follow this skill strictly.**

### Example: User Says "Create inventory and sales tables with 10M records"

**❌ WRONG - What happens WITHOUT loading this skill:**
```python
# Cell 1: Everything crammed together (THIS IS THE PROBLEM THE USER KEEPS SEEING)
from pyspark.sql import functions as F
from pyspark.sql.types import *

# Create schema if not exists
spark.sql("CREATE SCHEMA IF NOT EXISTS workspace.bronze_vibecode")

# Set seed for reproducibility
seed_value = 42

print("Generating raw inventory data...")

# Generate 10M inventory records with messy data
inventory_df = (
    spark.range(0, 10_000_000, numPartitions=200)
    .withColumn("inventory_id", F.col("id"))
    .withColumn("product_id", (F.rand(seed_value) * 5000).cast("int") + 1)
    # ... 20 more withColumn calls ...
)

inventory_df.write.format("delta").mode("overwrite").saveAsTable("workspace.bronze_vibecode.raw_inventory")
spark.sql("ALTER TABLE workspace.bronze_vibecode.raw_inventory SET TBLPROPERTIES ('quality' = 'bronze')")

# Now do sales in the same cell... another 30 lines
```

**Problem:** Imports + CREATE SCHEMA + seed + print + DataFrame + write + ALTER TABLE all in ONE cell.
**Result:** Impossible to debug. User has complained about this multiple times.

**✓ CORRECT - WITH this skill loaded - One action per cell:**
```python
# Cell 1: Imports ONLY
from pyspark.sql import functions as F
from pyspark.sql.types import *

# Cell 2: Configuration ONLY
CATALOG = "workspace"
BRONZE_SCHEMA = f"{CATALOG}.bronze_vibecode"
INVENTORY_TABLE = f"{BRONZE_SCHEMA}.raw_inventory"
SALES_TABLE = f"{BRONZE_SCHEMA}.raw_sales"
RECORD_COUNT = 10_000_000
SEED_VALUE = 42

# Cell 3+: One action per cell (exact sequence depends on your task)

# Example: Define a function
def clean_column(df, col_name):
    return df.withColumn(f"{col_name}_cleaned", F.upper(F.trim(F.col(col_name))))

# Example: Create schema
spark.sql(f"CREATE SCHEMA IF NOT EXISTS {BRONZE_SCHEMA}")

# Example: Create table with properties (multiple SQL statements for same table OK)
spark.sql(f"CREATE TABLE {TARGET_TABLE} ...")
spark.sql(f"ALTER TABLE {TARGET_TABLE} SET TBLPROPERTIES ('quality' = 'bronze')")
spark.sql(f"ALTER TABLE {TARGET_TABLE} SET TBLPROPERTIES ('delta.enableChangeDataFeed' = 'true')")

# Example: Read from table
df_raw = spark.table(SOURCE_TABLE)

# Example: Generate base data
df_generated = spark.range(0, RECORD_COUNT, numPartitions=200)

# Example: Transform data
df_transformed = (
    df_raw
    .withColumn("new_col", F.col("old_col") * 2)
    .withColumn("another_col", F.upper(F.col("name")))
)

# Example: Write to table (separate from CREATE/ALTER)
(
    df_transformed.write
    .format("delta")
    .mode("overwrite")
    .saveAsTable(TARGET_TABLE)
)
```

**✅ Result:** Each action gets its own cell. Easy to debug. Constants in Cell 2. No hardcoded strings.

**Key Principle:**
* **Cell 1**: Imports
* **Cell 2**: Configuration/constants
* **Cell 3+**: ONE action per cell - could be CREATE SCHEMA, read, transform, write, ALTER TABLE, window spec, etc.

**The order depends on your task.** The rule is: **one action per cell**, not a specific sequence.

## DataFrame Coding Style

### Use Parentheses, Not Backslashes

Always use parentheses to wrap multi-line DataFrame chains. Never use backslash continuation.

**✓ CORRECT - Parentheses style:**
```python
df_cleaned = (
    df_raw
    .filter(F.col("id").isNotNull())
    .withColumn(
        "name_cleaned",
        F.when(F.col("name").isNull(), F.lit("Unknown"))
        .otherwise(F.trim(F.col("name")))
    )
    .withColumn(
        "amount",
        F.when(F.col("amount") < 0, F.lit(0))
        .otherwise(F.col("amount"))
    )
)
```

**✗ WRONG - Backslash continuation:**
```python
df_cleaned = df_raw \
    .filter(F.col("id").isNotNull()) \
    .withColumn("name_cleaned", expr) \
    .withColumn("amount", expr)
```

### Formatting Rules

1. **Opening parenthesis on assignment line**, closing parenthesis on its own line:
   ```python
   df = (
       source_df
       .method1()
       .method2()
   )
   ```

2. **One method per line** - each DataFrame method call on its own line

3. **Indent methods consistently** - 4 spaces from the opening parenthesis

4. **Multi-line arguments** - when a method has complex arguments, break them across lines:
   ```python
   df = (
       df
       .withColumn(
           "complex_column",
           F.when(condition1, value1)
           .when(condition2, value2)
           .otherwise(default_value)
       )
   )
   ```

5. **Write operations** - wrap `.write` chains in parentheses:
   ```python
   (
       df.write
       .format("delta")
       .mode("overwrite")
       .option("overwriteSchema", "true")
       .clusterBy("date", "id")
       .saveAsTable("catalog.schema.table")
   )
   ```

6. **Read operations** - wrap multi-option reads:
   ```python
   df = (
       spark.read
       .format("delta")
       .option("readChangeFeed", "true")
       .option("startingVersion", 0)
       .table("source_table")
   )
   ```

### Window Specs and Complex Expressions

Window specifications can stay on one or multiple lines depending on complexity:

```python
# Simple window - one line is fine
window_spec = Window.partitionBy("id").orderBy(F.col("date").desc())

# Complex window - use parentheses
window_spec = (
    Window
    .partitionBy("customer_id", "region")
    .orderBy(F.col("timestamp").desc())
    .rowsBetween(Window.unboundedPreceding, Window.currentRow)
)
```



## Configuration and Constants

### Rule: Cell 2 is for Configuration

After imports, **cell 2 should contain all configuration, constants, and parameters**. This includes:

* Catalog, schema, and table references
* Environment variables
* Widget parameter definitions (using `dbutils.widgets`)
* File paths and volume paths
* API endpoints or connection strings
* Configuration dictionaries
* Any hardcoded values that might change between environments

**✓ CORRECT - Configuration in Cell 2:**
```python
# Cell 1: Imports
from pyspark.sql import functions as F
from pyspark.sql.window import Window
import dbutils

# Cell 2: Configuration and Constants
# Catalog and schema references
CATALOG = "workspace"
BRONZE_SCHEMA = f"{CATALOG}.bronze_vibecode"
SILVER_SCHEMA = f"{CATALOG}.silver_vibecode"

# Table names
RAW_SALES_TABLE = f"{BRONZE_SCHEMA}.raw_sales"
RAW_INVENTORY_TABLE = f"{BRONZE_SCHEMA}.raw_inventory"
SILVER_SALES_TABLE = f"{SILVER_SCHEMA}.sales"
SILVER_INVENTORY_TABLE = f"{SILVER_SCHEMA}.inventory"

# Widget parameters
dbutils.widgets.text("environment", "dev", "Environment")
dbutils.widgets.text("batch_date", "2024-01-01", "Batch Date")

# Get widget values
ENVIRONMENT = dbutils.widgets.get("environment")
BATCH_DATE = dbutils.widgets.get("batch_date")

# Volume paths
DATA_VOLUME = f"/Volumes/{CATALOG}/data/landing"
CHECKPOINT_PATH = f"/Volumes/{CATALOG}/checkpoints"

# Processing configuration
BATCH_SIZE = 10_000_000
SKEW_THRESHOLD = 0.20

# Cell 3: Start actual processing
df_raw = spark.table(RAW_SALES_TABLE)
```

**✗ WRONG - Constants scattered throughout:**
```python
# Cell 1: Imports
from pyspark.sql import functions as F

# Cell 2: Read data
df_raw = spark.table("workspace.bronze.raw_sales")  # ✗ hardcoded table name

# Cell 5: Write data
df.write.saveAsTable("workspace.silver.sales")  # ✗ hardcoded table name

# Cell 8: More processing
batch_size = 10000000  # ✗ constant defined late
```

### Benefits of Cell 2 Configuration:

* **Single source of truth** - all configurable values in one place
* **Easy environment switching** - change dev/prod by updating cell 2
* **Clear documentation** - immediately see what's configurable
* **Widget integration** - parameters and widgets grouped together
* **No magic strings** - use named constants instead of literals

### What Goes in Cell 2:

1. **Catalog/Schema/Table references** - use constants for all table names
2. **Widget definitions and retrievals** - define and get all widgets here
3. **Path constants** - volumes, checkpoints, temp locations
4. **Environment config** - dev/staging/prod settings
5. **Processing parameters** - batch sizes, thresholds, limits
6. **Connection strings** - external system references (if not secrets)

### What Does NOT Go in Cell 2:

* DataFrame transformations
* Business logic
* Function definitions (each function gets its own cell)
* Class definitions
* Data processing code

## Import Management

### Rule: All Imports at the Top

Place **all imports in the first code cell** of the notebook. Never scatter imports across multiple cells.

**✓ CORRECT - First cell of notebook:**
```python
# Cell 1: Imports
from pyspark.sql import functions as F
from pyspark.sql.window import Window
from pyspark.sql.types import StructType, StructField, StringType, IntegerType
from datetime import datetime, timedelta
import pandas as pd
```

**✗ WRONG - Imports scattered:**
```python
# Cell 1
from pyspark.sql import functions as F
# ... code ...

# Cell 5
from pyspark.sql.window import Window  # ✗ DON'T DO THIS
# ... more code ...
```

### No Duplicate Imports

Before adding an import, check if it's already imported in the first cell. Update the first cell if needed, never re-import.

### Standard Import Patterns

Use these standard import aliases:

```python
# PySpark
from pyspark.sql import functions as F
from pyspark.sql.window import Window
from pyspark.sql.types import *  # or import specific types

# Python standard library
from datetime import datetime, timedelta, date
import os
import json
import re

# Data science
import pandas as pd
import numpy as np
```

### Import Organization

Group imports in this order, separated by blank lines:

1. PySpark imports
2. Python standard library
3. Third-party libraries (pandas, numpy, etc.)
4. Local/custom modules

```python
# PySpark
from pyspark.sql import functions as F
from pyspark.sql.window import Window

# Standard library
from datetime import datetime
import json

# Third-party
import pandas as pd
```





## Quick Checklist

**Before completing ANY notebook work (table creation, transformations, pipelines):**

### ❗ CRITICAL - Cell Organization
- [ ] **Cell 1**: Imports only
- [ ] **Cell 2**: Configuration and constants (catalog, schema, tables, widgets, paths)
- [ ] **Cell 3+**: One action per cell - NEVER combine multiple actions in one cell
- [ ] **Each action gets its own cell**: Python functions, CREATE SCHEMA, SQL table operations (CREATE TABLE + ALTERs for same table OK), read, transform, window spec, dedupe, select, write
- [ ] **The exact sequence depends on your task** - there's no mandated order, just one action per cell
- [ ] **No hardcoded strings** - use constants from Cell 2 instead of literals like "workspace.bronze.table"

### DataFrame Style
- [ ] All DataFrame chains use parentheses, not backslashes
- [ ] Each DataFrame method is on its own line
- [ ] Complex nested expressions are properly indented
- [ ] Write operations are wrapped in parentheses

### Import Management
- [ ] All imports are in the first cell only
- [ ] No duplicate imports across cells
- [ ] Imports are grouped: PySpark → stdlib → third-party

### Common Mistakes to Avoid
- [ ] ❌ DO NOT combine multiple actions in one cell (e.g., CREATE SCHEMA + DataFrame + write)
- [ ] ❌ DO NOT combine multiple DataFrame transformations in one cell (e.g., df_raw, df_cleaned, df_deduped all in one cell)
- [ ] ❌ DO NOT add imports in cells other than Cell 1
- [ ] ❌ DO NOT use backslash continuation for DataFrames
- [ ] ❌ DO NOT hardcode table/schema names - use constants from Cell 2
