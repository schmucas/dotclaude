# Fixture, not real code. Every line here is wrong on purpose.
# The violations are listed in EXPECTED.md. A review that misses one is a
# regression in the skill, which is the whole point of keeping this file.
#
# The convention guard hook skips anything under evals/fixtures/, otherwise it
# would block this file from ever being written.

import dlt  # V1: legacy API spelling, should be `from pyspark import pipelines as dp`
from pyspark.sql import functions as F


@dlt.table(name="bronze_orders")  # V1 again
def bronze_orders():
    # V2: DBFS path, should be a UC Volume
    return spark.read.json("/dbfs/mnt/landing/orders/")


@dlt.table(name="silver_customers")
def silver_customers():
    # V3: hardcoded catalog and schema, should be a target variable
    df = spark.read.table("prod_catalog.raw.customers")

    # V4: token in source
    token = "dapi0123456789abcdef0123456789abcd"
    print(f"using {token}")

    # V5: collect() on an unbounded read, pulls the whole table to the driver
    ids = [r.id for r in df.collect()]

    # V6: driver side loop building a deep plan instead of a single expression
    for column in ["name", "email", "phone"]:
        df = df.withColumn(column, F.upper(F.col(column)))

    # V7: SCD2 join ignoring the validity interval, so every historical version
    # matches and the fact fans out. Compiles, produces wrong numbers.
    orders = spark.read.table("silver.orders")
    joined = orders.join(df, orders.customer_id == df.customer_id, "left")

    # V8: partitioning on a high cardinality column
    return joined.filter(F.col("id").isin(ids)).repartition("customer_id")


def cleanup():
    # V9: dbutils.fs, DBFS era
    dbutils.fs.rm("/tmp/scratch", recurse=True)  # noqa: F821
