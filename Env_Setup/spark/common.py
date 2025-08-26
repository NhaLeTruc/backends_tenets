from pyspark import SparkConf
from pyspark.sql import SparkSession


def create_spark_session(app_name: str, local_mode: bool = False) -> SparkSession:

    if local_mode:
        print("Started local mode")
        conf = (
            SparkConf()
            .set("spark.driver.memory", "8g")
            .set("spark.sql.session.timeZone", "UTC")
            .set("spark.sql.execution.arrow.pyspark.enabled", "true")
            .set("spark.sql.execution.arrow.pyspark.fallback.enabled", "false")
            .set("spark.sql.execution.arrow.maxRecordsPerBatch", "2")
        )

        spark_session = SparkSession\
            .builder\
            .master("local[4]")\
            .config(conf=conf)\
            .appName(app_name) \
            .getOrCreate()
    else:
        print("Started for cluster")

        conf = (
            SparkConf()
            .set("spark.sql.session.timeZone", "UTC")
            .set("spark.sql.execution.arrow.pyspark.enabled", "true")
            .set("spark.sql.execution.arrow.pyspark.fallback.enabled", "false")
            .set("spark.sql.execution.arrow.maxRecordsPerBatch", "2")
        )

        spark_session = SparkSession\
            .builder\
            .config(conf=conf)\
            .appName(app_name) \
            .getOrCreate()

    return spark_session