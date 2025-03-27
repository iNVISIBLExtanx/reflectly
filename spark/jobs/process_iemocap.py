#!/usr/bin/env python3
"""
IEMOCAP Dataset Processing

This script processes the IEMOCAP dataset using PySpark to create:
1. Emotion Detection Models
2. Transition Probability Models
3. Emotion Coordinate Mapping
"""

import os
import sys
import json
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, when, lit, expr
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, FloatType
import pyspark.sql.functions as F
from pyspark.ml.feature import StringIndexer, OneHotEncoder, VectorAssembler
from pyspark.ml.classification import LogisticRegression
from pyspark.ml import Pipeline

# Initialize Spark Session
spark = SparkSession.builder \
    .appName("IEMOCAP Data Processing") \
    .getOrCreate()

# Define paths
BASE_DIR = "/Users/manodhyaopallage/Refection"
RAW_DATA_PATH = f"{BASE_DIR}/data/datasets/iemocap/raw/iemocap_full_dataset.csv"
PROCESSED_DIR = f"{BASE_DIR}/data/datasets/iemocap/processed"
MODELS_DIR = f"{BASE_DIR}/data/models/iemocap"

# Ensure output directories exist
os.makedirs(PROCESSED_DIR, exist_ok=True)
os.makedirs(MODELS_DIR, exist_ok=True)

# Define emotion mapping for standardization
EMOTION_MAPPING = {
    'neu': 'neutral',
    'hap': 'joy',
    'sad': 'sadness',
    'ang': 'anger',
    'fru': 'anger',  # Mapping frustration to anger
    'sur': 'surprise',
    'dis': 'disgust',
    'fea': 'fear',
    'exc': 'joy',    # Mapping excitement to joy
    'xxx': 'unknown' # Unknown emotion
}

# Define emotion coordinates in 2D space (valence-arousal)
EMOTION_COORDINATES = {
    'joy': {'x': 0.8, 'y': 0.6},
    'sadness': {'x': -0.7, 'y': -0.4},
    'anger': {'x': -0.6, 'y': 0.8},
    'fear': {'x': -0.8, 'y': 0.6},
    'surprise': {'x': 0.3, 'y': 0.8},
    'disgust': {'x': -0.7, 'y': 0.2},
    'neutral': {'x': 0.0, 'y': 0.0},
    'unknown': {'x': 0.0, 'y': 0.0}
}

def process_iemocap():
    """Process the IEMOCAP dataset and generate knowledge databases"""
    print("Loading IEMOCAP dataset...")
    
    # Read the CSV file
    iemocap_df = spark.read.option("header", "true").csv(RAW_DATA_PATH)
    
    # Show the schema and sample data
    iemocap_df.printSchema()
    iemocap_df.show(5)
    
    # Filter out rows with unknown emotions and low agreement
    filtered_df = iemocap_df.filter(
        (col("emotion") != "xxx") & 
        (col("agreement") >= 2)
    )
    
    # Map emotions to standardized format
    mapped_df = filtered_df.withColumn(
        "standardized_emotion",
        F.create_map([
            lit(x) for x in sum([(k, v) for k, v in EMOTION_MAPPING.items()], ())
        ])[col("emotion")]
    )
    
    # Add emotion coordinates
    coordinates_expr = F.create_map([
        lit(x) for x in sum([
            (k, json.dumps(v)) for k, v in EMOTION_COORDINATES.items()
        ], ())
    ])
    
    mapped_df = mapped_df.withColumn(
        "emotion_coordinates", 
        coordinates_expr[col("standardized_emotion")]
    )
    
    # Save processed data
    print("Saving processed IEMOCAP dataset...")
    mapped_df.write.mode("overwrite").parquet(f"{PROCESSED_DIR}/emotions")
    
    # Generate emotion distribution stats
    emotion_stats = mapped_df.groupBy("standardized_emotion").count()
    emotion_stats.show()
    
    # Save emotion distribution as JSON
    emotion_dist = {}
    for row in emotion_stats.collect():
        emotion_dist[row["standardized_emotion"]] = row["count"]
    
    with open(f"{PROCESSED_DIR}/emotion_distribution.json", "w") as f:
        json.dump(emotion_dist, f, indent=2)
    
    # Create transition probability matrix
    create_transition_matrix(mapped_df)
    
    # Extract emotion triggers
    extract_emotion_triggers(mapped_df)
    
    print("IEMOCAP processing complete!")

def create_transition_matrix(df):
    """Create a transition probability matrix between emotions"""
    print("Generating transition probability matrix...")
    
    # Group by session to maintain temporal order
    session_df = df.orderBy("session", "path")
    
    # Window function to get next emotion in sequence
    from pyspark.sql.window import Window
    import pyspark.sql.functions as F
    
    window_spec = Window.partitionBy("session").orderBy("path")
    
    # Add next emotion column
    transition_df = session_df.withColumn(
        "next_emotion", 
        F.lead("standardized_emotion", 1).over(window_spec)
    )
    
    # Filter out rows where next_emotion is null
    transition_df = transition_df.filter(col("next_emotion").isNotNull())
    
    # Count transitions between emotions
    transition_counts = transition_df.groupBy("standardized_emotion", "next_emotion").count()
    
    # Calculate total transitions from each emotion
    emotion_totals = transition_counts.groupBy("standardized_emotion") \
        .agg(F.sum("count").alias("total"))
    
    # Join to calculate probabilities
    transition_probs = transition_counts.join(
        emotion_totals,
        on="standardized_emotion"
    ).withColumn(
        "probability", 
        col("count") / col("total")
    )
    
    # Show transition probabilities
    transition_probs.select(
        "standardized_emotion", 
        "next_emotion", 
        "probability"
    ).orderBy(
        "standardized_emotion", 
        "probability", 
        ascending=[True, False]
    ).show()
    
    # Convert to dictionary format for easier use in application
    transition_matrix = {}
    
    for emotion in EMOTION_MAPPING.values():
        if emotion != 'unknown':
            transition_matrix[emotion] = {}
    
    for row in transition_probs.collect():
        from_emotion = row["standardized_emotion"]
        to_emotion = row["next_emotion"]
        prob = float(row["probability"])
        
        if from_emotion in transition_matrix:
            transition_matrix[from_emotion][to_emotion] = prob
    
    # Fill in missing transitions with small probabilities
    for from_emotion in transition_matrix:
        total_prob = sum(transition_matrix[from_emotion].values())
        
        # Add small probability for missing transitions
        for to_emotion in transition_matrix:
            if to_emotion not in transition_matrix[from_emotion]:
                transition_matrix[from_emotion][to_emotion] = 0.01
        
        # Normalize to ensure probabilities sum to 1
        new_total = sum(transition_matrix[from_emotion].values())
        for to_emotion in transition_matrix[from_emotion]:
            transition_matrix[from_emotion][to_emotion] /= new_total
    
    # Save transition matrix
    with open(f"{PROCESSED_DIR}/transition_matrix.json", "w") as f:
        json.dump(transition_matrix, f, indent=2)
    
    print("Transition probability matrix generated!")

def extract_emotion_triggers(df):
    """Extract common triggers for each emotion"""
    print("Extracting emotion triggers...")
    
    # In a real implementation, this would analyze text content
    # For our sample data, we'll use a simulated approach
    
    # Define default triggers for each emotion
    default_triggers = {
        'joy': ["achievement", "connection", "gratitude", "hope", "love"],
        'sadness': ["loss", "disappointment", "rejection", "loneliness", "failure"],
        'anger': ["argument", "injustice", "disrespect", "frustration", "betrayal"],
        'fear': ["threat", "uncertainty", "judgment", "change", "failure"],
        'surprise': ["unexpected", "novelty", "discovery", "revelation", "change"],
        'disgust': ["violation", "contamination", "aversion", "rejection", "immorality"],
        'neutral': ["routine", "stability", "balance", "normality", "calm"]
    }
    
    # Count occurrences of each emotion
    emotion_counts = df.groupBy("standardized_emotion").count()
    
    # Create emotion triggers data structure
    emotion_triggers = {}
    
    for row in emotion_counts.collect():
        emotion = row["standardized_emotion"]
        if emotion != 'unknown' and emotion in default_triggers:
            emotion_triggers[emotion] = {
                "count": row["count"],
                "triggers": default_triggers.get(emotion, []),
                "coordinates": EMOTION_COORDINATES.get(emotion, {"x": 0, "y": 0})
            }
    
    # Save emotion triggers
    with open(f"{PROCESSED_DIR}/emotion_triggers.json", "w") as f:
        json.dump(emotion_triggers, f, indent=2)
    
    print("Emotion triggers extracted!")

if __name__ == "__main__":
    process_iemocap()
    spark.stop()
