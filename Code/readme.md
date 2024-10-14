## How to Run ?!

#### Train the model
`python3 spark_ML.py`

#### Start the ZooKeeper service
`bin/zookeeper-server-start.sh config/zookeeper.properties`

#### Open a new terminal and start the Kafka broker service
`bin/kafka-server-start.sh config/server.properties`

#### create topic
`bin/kafka-topics.sh --create --topic traffic_data --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1`


#### listtopics see if the topic produced is visible 
`bin/kafka-topics.sh --list --bootstrap-server localhost:9092`

#### go to the repo containing producer_data.py file and type 
`python3 kafka_producer.py`

##### to capture the streaming data and view real time predictions 
`spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.0 prediction.py`

