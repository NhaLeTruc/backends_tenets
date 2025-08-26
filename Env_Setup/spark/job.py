import time

from pyspark.sql import SparkSession
import pyspark.sql.functions as F

from common import create_spark_session

def analyze_data(spark: SparkSession):
    data = spark.read.parquet("/opt/spark-data/*.parquet").repartition(4)

    print(f"The data contains: {data.count()} rows")

    aggregted_by_pickup_location = (
        data.groupBy("PULocationID")
        .agg(
            F.count(F.lit(1)).alias("num_rows"), 
            F.avg("tip_amount").alias("avg_tip")
        )
        .filter(F.col("num_rows") > 20)
    )

    aggregted_by_pickup_location.sort(F.col("avg_tip").desc()).show(truncate = False, n=10)
    aggregted_by_pickup_location.write.option("header", "true").csv(f"/opt/spark-data/output-{time.time()}")

if __name__ == '__main__':
    spark = create_spark_session("test job")
    analyze_data(spark=spark)