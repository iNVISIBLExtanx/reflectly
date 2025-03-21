"""
Dataset Import Spark Job for Reflectly
Imports and processes IEMOCAP and mental health datasets
"""
import sys
import json
import argparse
import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, explode, regexp_replace, lower, trim
from pyspark.sql.types import StringType, StructType, StructField, FloatType, ArrayType, BooleanType
import pyspark.sql.functions as F

def create_spark_session(app_name="reflectly-dataset-import"):
    """
    Create a Spark session
    
    Args:
        app_name (str): Application name
        
    Returns:
        SparkSession: Spark session
    """
    return SparkSession.builder \
        .appName(app_name) \
        .getOrCreate()

def process_iemocap_dataset(spark, input_path, output_path):
    """
    Process IEMOCAP dataset
    
    Args:
        spark (SparkSession): Spark session
        input_path (str): Input path to IEMOCAP dataset
        output_path (str): Output path in HDFS
        
    Returns:
        int: Number of processed records
    """
    # Check if input path exists
    if not os.path.exists(input_path):
        print(f"IEMOCAP dataset not found at {input_path}")
        return 0
        
    print(f"Processing IEMOCAP dataset from {input_path}")
    
    # Define schema for IEMOCAP dataset
    # This is a simplified schema and would need to be adjusted based on the actual dataset structure
    iemocap_schema = StructType([
        StructField("utterance", StringType(), True),
        StructField("emotion", StringType(), True),
        StructField("valence", FloatType(), True),
        StructField("activation", FloatType(), True),
        StructField("dominance", FloatType(), True)
    ])
    
    try:
        # Read IEMOCAP dataset
        # The actual file format and structure would depend on the dataset
        iemocap_df = spark.read.csv(input_path, header=True, schema=iemocap_schema)
        
        # Clean and preprocess data
        cleaned_df = iemocap_df.withColumn("utterance", trim(lower(col("utterance"))))
        
        # Map emotions to our standard set
        emotion_mapping = {
            "happiness": "joy",
            "excited": "joy",
            "sadness": "sadness",
            "anger": "anger",
            "frustrated": "anger",
            "fear": "fear",
            "disgust": "disgust",
            "neutral": "neutral",
            "surprise": "joy"  # Mapping surprise to joy as a simplification
        }
        
        # Apply emotion mapping
        for original, mapped in emotion_mapping.items():
            cleaned_df = cleaned_df.withColumn(
                "emotion",
                F.when(F.lower(col("emotion")) == original, mapped).otherwise(col("emotion"))
            )
        
        # Extract insights for each emotion
        emotions = ["joy", "sadness", "anger", "fear", "disgust", "neutral"]
        
        for emotion in emotions:
            # Filter by emotion
            emotion_df = cleaned_df.filter(col("emotion") == emotion)
            
            # Calculate average valence, activation, and dominance
            avg_metrics = emotion_df.agg(
                F.avg("valence").alias("avg_valence"),
                F.avg("activation").alias("avg_activation"),
                F.avg("dominance").alias("avg_dominance")
            ).collect()[0]
            
            # Create insights DataFrame
            insights = {
                "emotion": emotion,
                "dataset": "IEMOCAP",
                "metrics": {
                    "avg_valence": float(avg_metrics["avg_valence"]) if avg_metrics["avg_valence"] else 0.0,
                    "avg_activation": float(avg_metrics["avg_activation"]) if avg_metrics["avg_activation"] else 0.0,
                    "avg_dominance": float(avg_metrics["avg_dominance"]) if avg_metrics["avg_dominance"] else 0.0
                },
                "common_utterances": [row["utterance"] for row in 
                                     emotion_df.orderBy(F.length("utterance").desc())
                                     .limit(10).select("utterance").collect()]
            }
            
            # Write insights to HDFS
            insights_df = spark.createDataFrame([insights])
            insights_df.write.mode("overwrite").json(f"{output_path}/{emotion}")
        
        return cleaned_df.count()
    except Exception as e:
        print(f"Error processing IEMOCAP dataset: {e}")
        return 0

def process_mental_health_dataset(spark, input_path, output_path):
    """
    Process mental health dataset
    
    Args:
        spark (SparkSession): Spark session
        input_path (str): Input path to mental health dataset
        output_path (str): Output path in HDFS
        
    Returns:
        int: Number of processed records
    """
    # Check if input path exists
    if not os.path.exists(input_path):
        print(f"Mental health dataset not found at {input_path}")
        return 0
        
    print(f"Processing mental health dataset from {input_path}")
    
    # Define schema for mental health dataset
    # This is a simplified schema and would need to be adjusted based on the actual dataset structure
    mental_health_schema = StructType([
        StructField("text", StringType(), True),
        StructField("emotion", StringType(), True),
        StructField("intervention", StringType(), True),
        StructField("effectiveness", FloatType(), True)
    ])
    
    try:
        # Read mental health dataset
        # The actual file format and structure would depend on the dataset
        mental_health_df = spark.read.csv(input_path, header=True, schema=mental_health_schema)
        
        # Clean and preprocess data
        cleaned_df = mental_health_df.withColumn("text", trim(lower(col("text"))))
        
        # Map emotions to our standard set
        emotion_mapping = {
            "happiness": "joy",
            "excited": "joy",
            "sadness": "sadness",
            "depression": "sadness",
            "anger": "anger",
            "frustrated": "anger",
            "anxiety": "fear",
            "fear": "fear",
            "disgust": "disgust",
            "neutral": "neutral",
            "surprise": "joy"  # Mapping surprise to joy as a simplification
        }
        
        # Apply emotion mapping
        for original, mapped in emotion_mapping.items():
            cleaned_df = cleaned_df.withColumn(
                "emotion",
                F.when(F.lower(col("emotion")) == original, mapped).otherwise(col("emotion"))
            )
        
        # Extract insights for each emotion
        emotions = ["joy", "sadness", "anger", "fear", "disgust", "neutral"]
        
        for emotion in emotions:
            # Filter by emotion
            emotion_df = cleaned_df.filter(col("emotion") == emotion)
            
            # Group interventions by effectiveness
            interventions_df = emotion_df.groupBy("intervention") \
                .agg(F.avg("effectiveness").alias("avg_effectiveness")) \
                .orderBy(col("avg_effectiveness").desc())
            
            # Get top interventions
            top_interventions = [
                {
                    "intervention": row["intervention"],
                    "effectiveness": float(row["avg_effectiveness"])
                }
                for row in interventions_df.limit(5).collect()
            ]
            
            # Create insights DataFrame
            insights = {
                "emotion": emotion,
                "dataset": "mental_health",
                "effective_interventions": top_interventions,
                "common_texts": [row["text"] for row in 
                               emotion_df.orderBy(F.length("text").desc())
                               .limit(10).select("text").collect()]
            }
            
            # Write insights to HDFS
            insights_df = spark.createDataFrame([insights])
            insights_df.write.mode("overwrite").json(f"{output_path}/{emotion}")
        
        return cleaned_df.count()
    except Exception as e:
        print(f"Error processing mental health dataset: {e}")
        return 0

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Dataset Import Spark Job")
    parser.add_argument("--iemocap", required=False, help="Input path to IEMOCAP dataset")
    parser.add_argument("--mental-health", required=False, help="Input path to mental health dataset")
    parser.add_argument("--output", required=True, help="Output path in HDFS")
    
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
        
    args = parser.parse_args()
    
    # Create Spark session
    spark = create_spark_session()
    
    try:
        total_count = 0
        
        # Process IEMOCAP dataset if provided
        if args.iemocap:
            iemocap_count = process_iemocap_dataset(spark, args.iemocap, f"{args.output}/iemocap")
            print(f"Processed {iemocap_count} records from IEMOCAP dataset")
            total_count += iemocap_count
        
        # Process mental health dataset if provided
        if args.mental_health:
            mental_health_count = process_mental_health_dataset(spark, args.mental_health, f"{args.output}/mental_health")
            print(f"Processed {mental_health_count} records from mental health dataset")
            total_count += mental_health_count
        
        print(f"Total processed records: {total_count}")
    finally:
        # Stop Spark session
        spark.stop()

if __name__ == "__main__":
    main()
