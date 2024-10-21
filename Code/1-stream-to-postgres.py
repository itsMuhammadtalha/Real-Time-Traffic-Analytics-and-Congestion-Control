from kafka import KafkaConsumer
from pyspark.sql import SparkSession
from pyspark.ml import PipelineModel
import json

# Initialize Spark session
spark = SparkSession.builder \
    .appName("TrafficPredictionConsumer") \
    .config("spark.jars", "/home/talha/Downloads/postgresql-42.7.4.jar")\
    .getOrCreate()

# Kafka Consumer Configuration
KAFKA_TOPIC = "traffic_data"
KAFKA_BROKER = "localhost:9092"

# Initialize Kafka Consumer
consumer = KafkaConsumer(
    KAFKA_TOPIC,
    bootstrap_servers=KAFKA_BROKER,
    value_deserializer=lambda v: json.loads(v.decode('utf-8'))
)

# Load pre-trained models (as PipelineModels)
try:
    models = {
        target: PipelineModel.load(f"traffic_model_{target}")
        for target in ['1_to_4', '5_to_8', '9_to_12', '13_to_16', '17_to_20', '21_to_24', 'total_traffic']
    }
except Exception as e:
    print(f"Error loading model: {str(e)}")

# Define feature columns used in training
feature_cols = ['day_of_data', 'day_of_week', 'lane_of_travel', 'direction_of_travel',
                'month_of_data', 'station_id']

# PostgreSQL connection properties
pg_url = "jdbc:postgresql://localhost:5432/traffic_data"
pg_properties = {
    "user": "traffic_user",
    "password": "password",
    "driver": "org.postgresql.Driver"
}

print("Starting to consume messages...")
for message in consumer:
    data = message.value  # Extract the message content
    print(f"Received: {data}")

    # Create DataFrame from the consumed data
    df = spark.createDataFrame([data]).select(*feature_cols)

    # Predict traffic for each time interval and total traffic
    predictions = {}
    for target, model in models.items():
        pred_df = model.transform(df).select("prediction").collect()
        predictions[target] = pred_df[0][0] if pred_df else None

    print(f"Predicted Traffic: {predictions}")

    # Prepare data for PostgreSQL
    traffic_data = [(data['day_of_data'], data['day_of_week'], data['lane_of_travel'],
                     data['direction_of_travel'], data['month_of_data'], data['station_id'],
                     data['1_to_4'], data['5_to_8'], data['9_to_12'],
                     data['13_to_16'], data['17_to_20'], data['21_to_24'],
                     predictions['1_to_4'], predictions['5_to_8'],
                     predictions['9_to_12'], predictions['13_to_16'],
                     predictions['17_to_20'], predictions['21_to_24'],
                     predictions['total_traffic'])]
    
    # Write data to PostgreSQL
    traffic_data_df = spark.createDataFrame(traffic_data, 
        ['day_of_data', 'day_of_week', 'lane_of_travel', 'direction_of_travel',
         'month_of_data', 'station_id', 'traffic_1_to_4', 'traffic_5_to_8',
         'traffic_9_to_12', 'traffic_13_to_16', 'traffic_17_to_20', 
         'traffic_21_to_24', 'predicted_1_to_4', 'predicted_5_to_8',
         'predicted_9_to_12', 'predicted_13_to_16', 'predicted_17_to_20', 
         'predicted_21_to_24', 'predicted_total_traffic'])

    traffic_data_df.write.jdbc(url=pg_url, table='TrafficData', mode='append', properties=pg_properties)

