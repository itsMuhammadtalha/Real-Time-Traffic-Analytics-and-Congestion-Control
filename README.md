# Real-Time Traffic Analytics and Dynamic Signaling

## Abstract
Our final year project, titled "Real-Time Traffic Analytics and Dynamic Signaling," aims to address the challenges of traffic congestion in urban areas by leveraging real-time traffic data analytics and dynamic signaling systems. By utilizing advanced technologies such as machine learning and data analytics, our project seeks to optimize traffic flow, reduce congestion, and improve overall transportation efficiency. This README file provides an overview of our project.

## Problem Statement
Traditional traffic signal systems often struggle to adapt to changing traffic conditions, leading to congestion, delays, and inefficiencies in traffic flow. Our project seeks to overcome these challenges by implementing real-time traffic analytics and dynamic signaling systems. By monitoring and analyzing traffic patterns, dynamically adjusting signal timings, and prioritizing congestion alleviation strategies, we aim to improve traffic management and enhance urban mobility.

## implementation
This project implements a real-time traffic prediction system using Apache Kafka, PySpark, PostgreSQL, and Flask. It streams live traffic data, predicts traffic volumes across different time intervals using machine learning models, and stores the predictions for further analysis.

### Project Workflow
- Kafka Producer: Streams real-time traffic data to a Kafka topic.
- Spark Streaming Consumer:
- Reads data from the Kafka topic.
- Predicts traffic volumes for multiple time intervals using pre-trained Random Forest models.
- Stores the predictions along with input data in a PostgreSQL database.
- Data Warehouse: PostgreSQL stores real-time predictions for later analysis.
- Dashboard (Streamlit):
   - Displays historical data and trends via interactive graphs.
   - Allows users to query predictions based on custom date-time ranges.
   - Includes seasonality insights and recurring patterns identified during data exploration.
 
## Tech Stack
Kafka: For real-time data streaming.
PySpark: To process and predict traffic data.
PostgreSQL: Data warehouse for storing predictions.
Streamlit: Web framework for the dashboard.
Plotly / Matplotlib: Visualize traffic trends and patterns.

## How to Use
1. Start Kafka and PostgreSQL servers.
2. Run the Kafka producer to send traffic data.
3. Run the Spark stream consumer to predict and store data in PostgreSQL.
4. Launch the dashboard to explore trends, query predictions, and view seasonal patterns.

## Project Links  
- [Defense Presentation Slides](https://github.com/itsMuhammadtalha/Real-Time-Traffic-Analytics-and-Congestion-Control/blob/master/fyp1-presentation-1-final.pptx)

## Architecture
![Architecture Diagram](https://github.com/itsMuhammadtalha/Real-Time-Traffic-Analytics-and-Congestion-Control/assets/80144916/0a9afd36-d734-4ad7-992e-73e6e0766381)



---
*maintained by [Muhammad Talha](https://github.com/itsMuhammadtalha)* <br>
                      *[Irsa Khan](https://github.com/IrsaKhan)*
                      
