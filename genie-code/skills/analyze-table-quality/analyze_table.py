def analyze_table(table_name):
    """
    Quick analysis of a Delta table: row count, null rates, ID column hot keys.
    Returns two DataFrames: null_analysis and hot_key_analysis.
    
    Args:
        table_name: Fully qualified table name (catalog.schema.table)
    """
    from pyspark.sql import functions as F
    
    df = spark.table(table_name)
    
    # Cache schema once to avoid repeated Analyze RPCs
    columns = df.columns
    total_count = df.count()
    
    print(f"\n{'='*60}")
    print(f"Table: {table_name}")
    print(f"Total Rows: {total_count:,}")
    print(f"Total Columns: {len(columns)}")
    print(f"{'='*60}\n")
    
    # NULL ANALYSIS - show all columns with their null percentages
    print("NULL ANALYSIS:")
    null_counts = df.select([
        F.sum(F.when(F.col(c).isNull(), 1).otherwise(0)).alias(c) 
        for c in columns
    ]).collect()[0].asDict()
    
    null_data = []
    for col in columns:
        null_count = null_counts[col]
        null_pct = round((null_count / total_count * 100)) if total_count > 0 else 0
        null_data.append((col, null_count, null_pct))
    
    null_df = spark.createDataFrame(null_data, ["column_name", "null_count", "null_pct"])
    null_df = null_df.orderBy(F.desc("null_pct"))
    display(null_df)
    
    # HOT KEY ANALYSIS - identify individual hot keys in ID/key columns
    id_cols = [c for c in columns if 
               c.lower().endswith('_id') or 
               c.lower().endswith('_key') or
               c.lower().endswith('id') or
               'key' in c.lower() or
               c.lower() in ['sk', 'pk']]
    
    if id_cols:
        print(f"\nHOT KEY ANALYSIS (ID/Key Columns):")
        hot_key_data = []
        
        for col in id_cols:
            # Get top value frequency
            top_value = (df.groupBy(col)
                        .count()
                        .orderBy(F.desc("count"))
                        .limit(1)
                        .collect())
            
            if top_value:
                top_count = top_value[0]['count']
                top_value_name = top_value[0][col]
                top_pct = (top_count / total_count * 100) if total_count > 0 else 0
                
                # Get distinct count
                distinct_count = df.select(col).distinct().count()
                
                hot_key_data.append((
                    col,
                    total_count,
                    distinct_count,
                    str(top_value_name)[:50],  # Truncate if needed
                    top_count,
                    round(top_pct)
                ))
        
        if hot_key_data:
            hot_key_df = spark.createDataFrame(
                hot_key_data, 
                ["column_name", "total_count", "distinct_count", "hottest_value", "hot_count", "hot_pct"]
            )
            hot_key_df = hot_key_df.orderBy(F.desc("hot_pct"))
            display(hot_key_df)
    
    print(f"\nDone! Check the tables above for null rates and hot keys.")

def analyze_dataframe(df, df_name="DataFrame"):
    """
    Quick analysis of a DataFrame: row count, null rates, ID column hot keys.
    Displays null_analysis and hot_key_analysis tables.
    
    Args:
        df: PySpark DataFrame to analyze
        df_name: Name for display purposes
    """
    from pyspark.sql import functions as F
    
    # Cache schema once to avoid repeated Analyze RPCs
    columns = df.columns
    total_count = df.count()
    
    print(f"\n{'='*60}")
    print(f"DataFrame: {df_name}")
    print(f"Total Rows: {total_count:,}")
    print(f"Total Columns: {len(columns)}")
    print(f"{'='*60}\n")
    
    # NULL ANALYSIS - show all columns with their null percentages
    print("NULL ANALYSIS:")
    null_counts = df.select([
        F.sum(F.when(F.col(c).isNull(), 1).otherwise(0)).alias(c) 
        for c in columns
    ]).collect()[0].asDict()
    
    null_data = []
    for col in columns:
        null_count = null_counts[col]
        null_pct = round((null_count / total_count * 100)) if total_count > 0 else 0
        null_data.append((col, null_count, null_pct))
    
    null_df = spark.createDataFrame(null_data, ["column_name", "null_count", "null_pct"])
    null_df = null_df.orderBy(F.desc("null_pct"))
    display(null_df)
    
    # HOT KEY ANALYSIS - identify individual hot keys in ID/key columns
    id_cols = [c for c in columns if 
               c.lower().endswith('_id') or 
               c.lower().endswith('_key') or
               c.lower().endswith('id') or
               'key' in c.lower() or
               c.lower() in ['sk', 'pk']]
    
    if id_cols:
        print(f"\nHOT KEY ANALYSIS (ID/Key Columns):")
        hot_key_data = []
        
        for col in id_cols:
            # Get top value frequency
            top_value = (df.groupBy(col)
                        .count()
                        .orderBy(F.desc("count"))
                        .limit(1)
                        .collect())
            
            if top_value:
                top_count = top_value[0]['count']
                top_value_name = top_value[0][col]
                top_pct = (top_count / total_count * 100) if total_count > 0 else 0
                
                # Get distinct count
                distinct_count = df.select(col).distinct().count()
                
                hot_key_data.append((
                    col,
                    total_count,
                    distinct_count,
                    str(top_value_name)[:50],  # Truncate if needed
                    top_count,
                    round(top_pct)
                ))
        
        if hot_key_data:
            hot_key_df = spark.createDataFrame(
                hot_key_data, 
                ["column_name", "total_count", "distinct_count", "hottest_value", "hot_count", "hot_pct"]
            )
            hot_key_df = hot_key_df.orderBy(F.desc("hot_pct"))
            display(hot_key_df)
    
    print(f"\n✓ Analysis complete! Check tables above for null rates and hot keys.")

# Example usage:
# analyze_table("catalog.schema.table_name")
# analyze_dataframe(df_sales, "df_sales")