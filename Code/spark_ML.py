from pyspark.sql import SparkSession
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.regression import RandomForestRegressor
from pyspark.ml.evaluation import RegressionEvaluator
from pyspark.ml import Pipeline
from pyspark.sql.types import StructType, StructField, IntegerType, DoubleType, StringType
import time

def create_spark_session(app_name="TrafficPredictionML"):
    return SparkSession.builder \
        .appName(app_name) \
        .config("spark.executor.memory", "4g") \
        .config("spark.driver.memory", "4g") \
        .getOrCreate()

def load_and_prepare_data(spark, file_path):
    # Read the CSV file to infer the schema
    df = spark.read.option("header", "true").csv(file_path)
    
    # Get the column names from the DataFrame
    columns = df.columns
    
    # Create a schema based on the inferred column names
    schema = StructType([StructField(col, StringType(), True) for col in columns])
    
    # Load data with the defined schema
    data = spark.read.option("header", "true").schema(schema).csv(file_path)
    
    # Convert necessary columns to the correct data type
    for col in data.columns:
        if col in ['day_of_data', 'day_of_week', 'lane_of_travel', 'direction_of_travel', 'month_of_data', 'station_id']:
            data = data.withColumn(col, data[col].cast(IntegerType()))
        elif col in ['1_to_4', '5_to_8', '9_to_12', '13_to_16', '17_to_20', '21_to_24', 'total_traffic']:
            data = data.withColumn(col, data[col].cast(DoubleType()))
    
    # Define feature columns (you may need to adjust this based on your actual data)
    feature_cols = ['day_of_data', 'day_of_week', 'lane_of_travel', 'direction_of_travel',
                    'month_of_data', 'station_id']
    
    # Define target columns
    target_cols = ['1_to_4', '5_to_8', '9_to_12', '13_to_16', '17_to_20', '21_to_24', 'total_traffic']
    
    # Create feature vector
    assembler = VectorAssembler(inputCols=feature_cols, outputCol="features")
    
    return data, assembler, feature_cols, target_cols

def train_model(data, assembler, feature_cols, target_cols):
    # Split data into training and testing sets
    train_data, test_data = data.randomSplit([0.8, 0.2], seed=42)
    
    # Create a list to store individual models and their corresponding assemblers
    models = []
    
    for target in target_cols:
        # Create and train a Random Forest model for each target
        rf = RandomForestRegressor(featuresCol="features", labelCol=target, numTrees=10, maxDepth=5)
        pipeline = Pipeline(stages=[assembler, rf])
        
        start_time = time.time()
        model = pipeline.fit(train_data)
        train_time = time.time() - start_time
        
        models.append((target, model, train_time))
    
    return models, train_data, test_data

def evaluate_models(models, test_data):
    for target, model, train_time in models:
        predictions = model.transform(test_data)
        evaluator = RegressionEvaluator(labelCol=target, predictionCol="prediction", metricName="r2")
        r2 = evaluator.evaluate(predictions)
        
        print(f"Model for {target}:")
        print(f"  R2 Score: {r2:.4f}")
        print(f"  Training Time: {train_time:.2f} seconds")
        print()

def main(file_path):
    # Create Spark session
    spark = create_spark_session()
    
    try:
        # Load and prepare data
        data, assembler, feature_cols, target_cols = load_and_prepare_data(spark, file_path)
        
        # Print schema and show a few rows to verify data loading
        print("Data Schema:")
        data.printSchema()
        print("\nSample Data:")
        data.show(5)
        
        # Train models
        models, train_data, test_data = train_model(data, assembler, feature_cols, target_cols)
        
        # Evaluate models
        evaluate_models(models, test_data)
        
        # Save models
        for target, model, _ in models:
            model.write().overwrite().save(f"traffic_model_{target}")
        
        print("Models saved successfully.")
    
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Stop Spark session
        spark.stop()

if __name__ == "__main__":
    file_path = "modified_traffic_data.csv"
    main(file_path)