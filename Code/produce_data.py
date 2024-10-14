import json
import random
import time
from kafka import KafkaProducer

def generate_traffic_data():
    return {
        "day_of_data": random.randint(1, 31),
        "day_of_week": random.randint(1, 7),
        "direction_of_travel": random.randint(1, 8),
        "lane_of_travel": random.randint(1, 3),
        "month_of_data": random.randint(1, 12),
        "station_id": random.randint(1000, 4000),
        "1_to_4": round(random.uniform(0, 300), 2),
        "5_to_8": round(random.uniform(0, 500), 2),
        "9_to_12": round(random.uniform(0, 1000), 2),
        "13_to_16": round(random.uniform(0, 1500), 2),
        "17_to_20": round(random.uniform(0, 1200), 2),
        "21_to_24": round(random.uniform(0, 800), 2)
    }

def json_serializer(data):
    return json.dumps(data).encode('utf-8')

producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=json_serializer
)

if __name__ == "__main__":
    while True:
        traffic_data = generate_traffic_data()
        producer.send('traffic_data', traffic_data)
        print(f"Sent: {traffic_data}")
        time.sleep(1)  # Generate data every second