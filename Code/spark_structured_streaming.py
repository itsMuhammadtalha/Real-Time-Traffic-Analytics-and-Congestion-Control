from pyspark.sql import SparkSession
from pyspark.ml.pipeline import PipelineModel
from pyspark.sql.functions import col, expr, split
from pyspark.sql.types import IntegerType, DoubleType, StructType, StructField

# Define the schema only for the required features
schema = StructType([
    StructField("day_of_data", IntegerType(), True),
    StructField("day_of_week", IntegerType(), True),
    StructField("lane_of_travel", IntegerType(), True),
    StructField("direction_of_travel", IntegerType(), True),
    StructField("month_of_data", IntegerType(), True),
    StructField("station_id", IntegerType(), True)
])

def create_spark_session(app_name="TrafficPredictionStream"):
    """Create and return a Spark session."""
    return SparkSession.builder \
        .appName(app_name) \
        .config("spark.sql.streaming.checkpointLocation", "/tmp/checkpoints") \
        .getOrCreate()

def main():
    # Step 1: Initialize Spark session
    spark = create_spark_session()

    # Step 2: Read data from Kafka topic
    kafka_df = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "localhost:9092") \
        .option("subscribe", "traffic_data") \
        .option("startingOffsets", "earliest") \
        .load()

    # Step 3: Extract relevant columns from the Kafka messages
    # Assume the incoming Kafka message is a comma-separated string (CSV-like)
    traffic_df = kafka_df.selectExpr("CAST(value AS STRING) as value")

    # Split the message into individual fields and map them to the required columns
    traffic_df = traffic_df.withColumn("fields", split(col("value"), ","))

    # Manually select and cast only the required columns for prediction
    selected_df = traffic_df.select(
        col("fields")[0].cast(IntegerType()).alias("day_of_data"),
        col("fields")[1].cast(IntegerType()).alias("day_of_week"),
        col("fields")[2].cast(IntegerType()).alias("lane_of_travel"),
        col("fields")[3].cast(IntegerType()).alias("direction_of_travel"),
        col("fields")[4].cast(IntegerType()).alias("month_of_data"),
        col("fields")[5].cast(IntegerType()).alias("station_id")
    )

    # Step 4: Load pre-trained models
    models = {}
    target_cols = ['1_to_4', '5_to_8', '9_to_12', '13_to_16', '17_to_20', '21_to_24', 'total_traffic']
    for target in target_cols:
        models[target] = PipelineModel.load(f"traffic_model_{target}")

    # Step 5: Apply each model to the streaming DataFrame
    for target, model in models.items():
        predictions_df = model.transform(selected_df)

        # Select only the relevant columns and rename the prediction column
        predictions_df = predictions_df.select(
            "station_id", "month_of_data", "day_of_data", "day_of_week", 
            "direction_of_travel", "lane_of_travel", "features", 
            col("prediction").alias(f"predicted_{target}")
        )

        # Step 6: Stream the predictions to the console
        query = predictions_df.writeStream \
                              .outputMode("append") \
                              .format("console") \
                              .option("truncate", "false") \
                              .start()

        # Wait for the query to finish
        query.awaitTermination()

if __name__ == "__main__":
    main()
