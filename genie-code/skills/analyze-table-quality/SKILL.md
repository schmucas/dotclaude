---
name: analyze-table-quality
description: Quick table quality analysis showing null rates and hot key skewness. Load this skill when the user asks to "analyze table", "analyze for nulls", "analyze for skewness", "analyze nulls and skewness", "check for nulls", "check for skewness", "check data quality", "find hot keys", "identify skewed columns", or mentions analyzing a DataFrame/df/variable. Works for both table names and in-memory DataFrames.
---

# Table Quality Analysis Skill

Use these functions to quickly assess data quality with focus on:
1. **Null rates** per column
2. **Hot key detection** in ID/key columns (skewness)

## When to Use

- User asks to analyze a table's data quality
- Need to identify columns with high null rates
- Looking for skewed join keys or hot keys that cause performance issues
- Debugging slow joins or aggregations (often caused by hot keys)
- Quick health check before building pipelines or queries

## How to Use

**For Unity Catalog tables:**
```python
analyze_table("catalog.schema.table_name")
```

**For in-memory DataFrames:**
```python
analyze_dataframe(df_sales, "df_sales")
# or
analyze_dataframe(df, "my dataset")
```

Both functions produce two tables:

### 1. NULL ANALYSIS
Shows all columns with their null percentages (rounded to whole numbers).
- Columns sorted by `null_pct` descending
- Quickly identify which columns need null handling

**Columns:**
- `column_name`: Column name
- `null_count`: Number of null values
- `null_pct`: Percentage of nulls (0-100, no decimals)

### 2. HOT KEY ANALYSIS
Analyzes columns that look like IDs or keys (ending with `_id`, `_key`, `id`, or containing `key`, `sk`, `pk`).
- Shows total count for easy comparison with distinct count
- Identifies the single hottest value per column
- `hot_pct` shows what percentage of rows have that value

**Columns:**
- `column_name`: The ID/key column name
- `total_count`: Total rows in table (for reference)
- `distinct_count`: Number of unique values in this column
- `hottest_value`: The most frequent value (truncated to 50 chars)
- `hot_count`: How many times the hottest value appears
- `hot_pct`: Percentage of rows with the hottest value (0-100, no decimals)

## Interpreting Results

**Null Analysis:**
- 0-5%: Generally acceptable
- 5-20%: May need null handling in queries
- 20%+: Significant data quality issue

**Hot Key Analysis:**
- `hot_pct` 0-5%: Healthy distribution
- `hot_pct` 5-10%: Minor skew, monitor for performance
- `hot_pct` 10%+: **HIGH SKEW** - will cause join/aggregation bottlenecks
- Compare `distinct_count` vs `total_count` to understand cardinality

**Example interpretation:**
```
product_id: 11.5M total → 50K distinct → hot key "12345" at 20%
```
This means one product ID dominates 20% of all rows - major skew issue!

## Implementation

See `analyze_table.py` in this folder for both function implementations:
- `analyze_table(table_name)` - for Unity Catalog tables
- `analyze_dataframe(df, df_name)` - for in-memory DataFrames

## Performance Notes

- Function caches the schema once to avoid repeated Analyze RPCs (Spark Connect optimization)
- Single pass for null analysis across all columns
- One distinct count per ID column (can be slow on very large tables with high cardinality)
- Consider sampling for initial exploration on tables > 100M rows