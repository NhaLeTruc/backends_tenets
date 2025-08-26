import time

from common import create_spark_session
from analysis import calculate_avg_trip_duration

if __name__ == '__main__':
    spark = create_spark_session("test job", local_mode=True)

    trips_data = spark.read.parquet("data/*.parquet")
    avg_trip_duration = calculate_avg_trip_duration(trips_data = trips_data)

    avg_trip_duration.show(truncate=False)
    avg_trip_duration.write.option("header", "true").csv(f"/opt/spark-data/output-avg-trip-{time.time()}")
