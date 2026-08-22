---
name: delta-primary-key-constraints
description: Required pattern for adding PRIMARY KEY constraints to Delta tables. Load this when creating silver/gold tables with primary key constraints, or when ALTER TABLE ADD CONSTRAINT PRIMARY KEY fails with a nullable column error.
---

# Delta Table Primary Key Constraints

## The Problem

When adding a PRIMARY KEY constraint to a Delta table, the constraint will fail if the key column's schema marks it as nullable, even if the column contains no null values in practice.

**Symptom**: `ALTER TABLE ... ADD CONSTRAINT ... PRIMARY KEY (column_name)` fails with an error about the column being nullable.

## The Required Pattern

To successfully add a primary key constraint, follow this two-step sequence:

### Step 1: Set the column to NOT NULL

```python
spark.sql(f"""
    ALTER TABLE {table_name}
    ALTER COLUMN {key_column} SET NOT NULL
""")
```

### Step 2: Add the primary key constraint

```python
spark.sql(f"""
    ALTER TABLE {table_name}
    ADD CONSTRAINT {constraint_name} PRIMARY KEY ({key_column})
""")
```

## Complete Workflow Example

When creating a silver layer table with a primary key:

```python
# Cell 1: Clean and write the table
df_cleaned = (
    df_source
    .filter(F.col("id").isNotNull())
    .dropDuplicates(["id"])
)

(
    df_cleaned.write
    .format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .clusterBy("id")
    .saveAsTable("catalog.schema.silver_table")
)

# Cell 2: Set key column NOT NULL
spark.sql("""
    ALTER TABLE catalog.schema.silver_table
    ALTER COLUMN id SET NOT NULL
""")

# Cell 3: Add primary key constraint
spark.sql("""
    ALTER TABLE catalog.schema.silver_table
    ADD CONSTRAINT pk_silver_table PRIMARY KEY (id)
""")
```

## Why This Happens

DataFrame operations (`.filter()`, `.dropDuplicates()`) remove null values at runtime but don't change the schema's nullability metadata. The Delta table inherits the original column's nullable=true schema marker. Primary key constraints require NOT NULL at the schema level, so you must explicitly alter the column definition.

## Best Practices

1. **One action per cell**: Keep the NOT NULL alter and the constraint addition in separate cells, following the one-action-per-cell principle.
2. **Always filter nulls first**: Ensure your DataFrame filters out nulls on the key column before writing (`.filter(F.col("key_col").isNotNull())`), otherwise the SET NOT NULL will fail.
3. **Check before adding**: If you're unsure whether nulls exist, verify the key column has no nulls before attempting to set NOT NULL.

## When to Use This Pattern

- Creating silver or gold layer tables with primary keys
- Adding key constraints to existing Delta tables
- Any scenario where you want to enforce uniqueness and non-nullability via a PRIMARY KEY constraint

This pattern applies to all Delta tables in Databricks SQL, Spark DataFrames, and declarative pipelines.