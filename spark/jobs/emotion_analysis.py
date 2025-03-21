"""
Emotion Analysis Spark Job for Reflectly
Analyzes emotions from journal entries using distributed processing
"""
import sys
import json
import argparse
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, udf, explode
from pyspark.sql.types import StringType, StructType, StructField, FloatType, ArrayType, BooleanType
import pyspark.sql.functions as F

def create_spark_session(app_name="reflectly-emotion-analysis"):
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

def analyze_emotion(text):
    """
    Analyze emotion from text
    This is a simplified version that would be replaced with a more sophisticated model
    
    Args:
        text (str): Text to analyze
        
    Returns:
        dict: Emotion analysis result
    """
    # This is a placeholder for the actual emotion analysis
    # In a real implementation, this would use a pre-trained model
    
    # Simple keyword-based analysis for demonstration
    joy_keywords = ["happy", "joy", "excited", "great", "wonderful", "love", "pleased", "delighted"]
    sadness_keywords = ["sad", "unhappy", "depressed", "miserable", "gloomy", "disappointed", "upset"]
    anger_keywords = ["angry", "mad", "furious", "annoyed", "irritated", "frustrated", "enraged"]
    fear_keywords = ["afraid", "scared", "fearful", "terrified", "anxious", "worried", "nervous"]
    disgust_keywords = ["disgusted", "revolted", "repulsed", "gross", "nauseous", "distasteful"]
    
    text_lower = text.lower()
    
    # Count occurrences of keywords
    joy_count = sum(1 for keyword in joy_keywords if keyword in text_lower)
    sadness_count = sum(1 for keyword in sadness_keywords if keyword in text_lower)
    anger_count = sum(1 for keyword in anger_keywords if keyword in text_lower)
    fear_count = sum(1 for keyword in fear_keywords if keyword in text_lower)
    disgust_count = sum(1 for keyword in disgust_keywords if keyword in text_lower)
    
    # Calculate total count
    total_count = joy_count + sadness_count + anger_count + fear_count + disgust_count
    
    # Calculate scores
    if total_count > 0:
        joy_score = joy_count / total_count
        sadness_score = sadness_count / total_count
        anger_score = anger_count / total_count
        fear_score = fear_count / total_count
        disgust_score = disgust_count / total_count
    else:
        # Default to neutral if no keywords found
        joy_score = 0.2
        sadness_score = 0.2
        anger_score = 0.2
        fear_score = 0.2
        disgust_score = 0.2
    
    # Determine primary emotion
    emotions = {
        "joy": joy_score,
        "sadness": sadness_score,
        "anger": anger_score,
        "fear": fear_score,
        "disgust": disgust_score
    }
    
    primary_emotion = max(emotions, key=emotions.get)
    is_positive = primary_emotion == "joy"
    
    return {
        "primary_emotion": primary_emotion,
        "is_positive": is_positive,
        "emotion_scores": {
            "joy": joy_score,
            "sadness": sadness_score,
            "anger": anger_score,
            "fear": fear_score,
            "disgust": disgust_score
        }
    }

def process_journal_entries(spark, input_path, output_path):
    """
    Process journal entries from HDFS
    
    Args:
        spark (SparkSession): Spark session
        input_path (str): Input path in HDFS
        output_path (str): Output path in HDFS
    """
    # Define schema for journal entries
    journal_schema = StructType([
        StructField("_id", StringType(), True),
        StructField("user_email", StringType(), True),
        StructField("content", StringType(), True),
        StructField("created_at", StringType(), True)
    ])
    
    # Read journal entries from HDFS
    journal_df = spark.read.json(input_path, schema=journal_schema)
    
    # Define UDF for emotion analysis
    emotion_analysis_udf = udf(analyze_emotion, 
        StructType([
            StructField("primary_emotion", StringType(), True),
            StructField("is_positive", BooleanType(), True),
            StructField("emotion_scores", 
                StructType([
                    StructField("joy", FloatType(), True),
                    StructField("sadness", FloatType(), True),
                    StructField("anger", FloatType(), True),
                    StructField("fear", FloatType(), True),
                    StructField("disgust", FloatType(), True)
                ]), True)
        ])
    )
    
    # Apply emotion analysis to journal entries
    result_df = journal_df.withColumn("emotion", emotion_analysis_udf(col("content")))
    
    # Write results to HDFS
    result_df.write.mode("overwrite").json(output_path)
    
    # Return count of processed entries
    return result_df.count()

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Emotion Analysis Spark Job")
    parser.add_argument("--input", required=True, help="Input path in HDFS")
    parser.add_argument("--output", required=True, help="Output path in HDFS")
    
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
        
    args = parser.parse_args()
    
    # Create Spark session
    spark = create_spark_session()
    
    try:
        # Process journal entries
        count = process_journal_entries(spark, args.input, args.output)
        print(f"Processed {count} journal entries")
    finally:
        # Stop Spark session
        spark.stop()

if __name__ == "__main__":
    main()
