from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, udf
from pyspark.sql.types import StructType, StructField, IntegerType, DoubleType, FloatType
import pickle
from pyspark.sql.streaming import StreamingQuery

# Define the schema for the incoming JSON data
schema = StructType([
    StructField("day_of_data", IntegerType(), True),
    StructField("day_of_week", IntegerType(), True),
    StructField("direction_of_travel", IntegerType(), True),
    StructField("lane_of_travel", IntegerType(), True),
    StructField("month_of_data", IntegerType(), True),
    StructField("station_id", IntegerType(), True),
    StructField("1_to_4", DoubleType(), True),
    StructField("5_to_8", DoubleType(), True),
    StructField("9_to_12", DoubleType(), True),
    StructField("13_to_16", DoubleType(), True),
    StructField("17_to_20", DoubleType(), True),
    StructField("21_to_24", DoubleType(), True)
])

# Load the pre-trained model
with open('lr_model.pkl', 'rb') as file:
    model = pickle.load(file)

def create_spark_session():
    return (SparkSession.builder
            .appName("TrafficPrediction")
            .getOrCreate())

# Define a UDF for prediction
@udf(returnType=FloatType())
def predict_traffic_udf(*features):
    import numpy as np
    feature_vector = np.array(features).reshape(1, -1)
    prediction = model.predict(feature_vector)
    return float(prediction[0])

def process_batch(df, epoch_id):
    # Select the features used for prediction
    features = ['day_of_data', 'day_of_week', 'lane_of_travel', 'direction_of_travel',
                'month_of_data', 'station_id', '1_to_4', '5_to_8', '9_to_12',
                '13_to_16', '17_to_20', '21_to_24']
    
    # Apply the UDF to make predictions
    df_with_prediction = df.withColumn("predicted_total_traffic", 
                                       predict_traffic_udf(*[col(c) for c in features]))
    
    # Show the results (you can modify this to write to a sink)
    df_with_prediction.show()

if __name__ == "__main__":
    spark = create_spark_session()
    
    # Create DataFrame representing the stream of input lines from Kafka
    df = (spark
          .readStream
          .format("kafka")
          .option("kafka.bootstrap.servers", "localhost:9092")
          .option("subscribe", "traffic_data")
          .load()
          .select(from_json(col("value").cast("string"), schema).alias("data"))
          .select("data.*"))
    
    # Process the streaming data
    query = (df
             .writeStream
             .foreachBatch(process_batch)
             .outputMode("update")
             .start())
    
    query.awaitTermination()