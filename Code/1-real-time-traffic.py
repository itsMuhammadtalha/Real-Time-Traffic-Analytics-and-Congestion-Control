from kafka import KafkaProducer
import pandas as pd
import json
import time
import random
from datetime import datetime

# Kafka Configuration
KAFKA_TOPIC = "traffic_data"
KAFKA_BROKER = "localhost:9092"  # Change if your broker is different

# Initialize Kafka Producer
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')  # Convert to JSON format
)

# Get current date information
current_date = datetime.now()
day_of_data = current_date.day
day_of_week = current_date.weekday() + 1  # Monday is 1, Sunday is 7
month_of_data = current_date.month

# Stream simulated data row-by-row to Kafka
for _ in range(100):  # Adjust the range for how many rows you want to send
    data = {
        'day_of_data': day_of_data,
        'day_of_week': day_of_week,
        'lane_of_travel': random.randint(1, 9),  # Random lane from 1 to 9
        'direction_of_travel': random.randint(1, 9),  # Random direction from 1 to 9
        'month_of_data': month_of_data,
        'station_id': random.randint(1, 50),  # Random station ID (1 to 50, for example)
        '1_to_4': random.randint(0, 100),  # Random traffic count for the time intervals
        '5_to_8': random.randint(0, 100),
        '9_to_12': random.randint(0, 100),
        '13_to_16': random.randint(0, 100),
        '17_to_20': random.randint(0, 100),
        '21_to_24': random.randint(0, 100)
    }

    producer.send(KAFKA_TOPIC, value=data)  # Send data to Kafka topic
    print(f"Sent: {data}")  # Optional: Print the sent data
    time.sleep(1)  # Simulate a delay between messages (adjust as needed)

# Close the producer when done
producer.flush()
producer.close()
