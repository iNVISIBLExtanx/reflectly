"""
Graph Processing Spark Job for Reflectly
Processes emotional transitions and builds the emotional graph
"""
import sys
import json
import argparse
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, explode, collect_list, struct, lit
from pyspark.sql.types import StringType, StructType, StructField, FloatType, ArrayType, BooleanType
import pyspark.sql.functions as F

def create_spark_session(app_name="reflectly-graph-processing"):
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

def process_emotional_states(spark, input_path, output_path):
    """
    Process emotional states and build the emotional graph
    
    Args:
        spark (SparkSession): Spark session
        input_path (str): Input path in HDFS (emotional states)
        output_path (str): Output path in HDFS (emotional transitions)
    """
    # Define schema for emotional states
    emotional_state_schema = StructType([
        StructField("_id", StringType(), True),
        StructField("user_email", StringType(), True),
        StructField("primary_emotion", StringType(), True),
        StructField("is_positive", BooleanType(), True),
        StructField("emotion_scores", 
            StructType([
                StructField("joy", FloatType(), True),
                StructField("sadness", FloatType(), True),
                StructField("anger", FloatType(), True),
                StructField("fear", FloatType(), True),
                StructField("disgust", FloatType(), True)
            ]), True),
        StructField("entry_id", StringType(), True),
        StructField("timestamp", StringType(), True)
    ])
    
    # Read emotional states from HDFS
    emotional_states_df = spark.read.json(input_path, schema=emotional_state_schema)
    
    # Register the DataFrame as a temporary view
    emotional_states_df.createOrReplaceTempView("emotional_states")
    
    # Find transitions between emotional states
    transitions_df = spark.sql("""
        SELECT 
            a.user_email,
            a.primary_emotion as from_emotion,
            b.primary_emotion as to_emotion,
            a._id as from_state_id,
            b._id as to_state_id,
            a.timestamp as from_timestamp,
            b.timestamp as to_timestamp
        FROM 
            emotional_states a
        JOIN 
            emotional_states b
        ON 
            a.user_email = b.user_email AND
            a.timestamp < b.timestamp
        WHERE 
            NOT EXISTS (
                SELECT 1 
                FROM emotional_states c 
                WHERE 
                    c.user_email = a.user_email AND
                    c.timestamp > a.timestamp AND
                    c.timestamp < b.timestamp
            )
    """)
    
    # Add default actions based on emotion transitions
    transitions_with_actions_df = transitions_df.withColumn(
        "actions",
        F.array(
            F.struct(
                F.lit("Practice mindfulness").alias("description"),
                F.lit(0.7).alias("success_rate")
            ),
            F.struct(
                F.lit("Engage in physical activity").alias("description"),
                F.lit(0.6).alias("success_rate")
            )
        )
    )
    
    # Write transitions to HDFS
    transitions_with_actions_df.write.mode("overwrite").json(output_path)
    
    # Return count of processed transitions
    return transitions_with_actions_df.count()

def analyze_transition_patterns(spark, transitions_path, patterns_output_path):
    """
    Analyze patterns in emotional transitions
    
    Args:
        spark (SparkSession): Spark session
        transitions_path (str): Path to emotional transitions in HDFS
        patterns_output_path (str): Output path for patterns in HDFS
    """
    # Read transitions from HDFS
    transitions_df = spark.read.json(transitions_path)
    
    # Register the DataFrame as a temporary view
    transitions_df.createOrReplaceTempView("transitions")
    
    # Analyze transition frequencies
    transition_frequencies_df = spark.sql("""
        SELECT 
            user_email,
            from_emotion,
            to_emotion,
            COUNT(*) as frequency
        FROM 
            transitions
        GROUP BY 
            user_email, from_emotion, to_emotion
        ORDER BY 
            user_email, frequency DESC
    """)
    
    # Analyze common paths
    common_paths_df = spark.sql("""
        SELECT 
            t1.user_email,
            t1.from_emotion as start_emotion,
            t1.to_emotion as middle_emotion,
            t2.to_emotion as end_emotion,
            COUNT(*) as frequency
        FROM 
            transitions t1
        JOIN 
            transitions t2
        ON 
            t1.user_email = t2.user_email AND
            t1.to_emotion = t2.from_emotion AND
            t1.to_timestamp < t2.from_timestamp
        GROUP BY 
            t1.user_email, start_emotion, middle_emotion, end_emotion
        ORDER BY 
            t1.user_email, frequency DESC
    """)
    
    # Combine results
    transition_frequencies_df.write.mode("overwrite").json(f"{patterns_output_path}/frequencies")
    common_paths_df.write.mode("overwrite").json(f"{patterns_output_path}/paths")
    
    return {
        "frequencies": transition_frequencies_df.count(),
        "paths": common_paths_df.count()
    }

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Graph Processing Spark Job")
    parser.add_argument("--input", required=True, help="Input path in HDFS (emotional states)")
    parser.add_argument("--output", required=True, help="Output path in HDFS (emotional transitions)")
    parser.add_argument("--patterns", required=False, help="Output path for patterns in HDFS")
    
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
        
    args = parser.parse_args()
    
    # Create Spark session
    spark = create_spark_session()
    
    try:
        # Process emotional states
        count = process_emotional_states(spark, args.input, args.output)
        print(f"Processed {count} emotional transitions")
        
        # Analyze transition patterns if patterns output path is provided
        if args.patterns:
            pattern_counts = analyze_transition_patterns(spark, args.output, args.patterns)
            print(f"Analyzed {pattern_counts['frequencies']} transition frequencies and {pattern_counts['paths']} common paths")
    finally:
        # Stop Spark session
        spark.stop()

if __name__ == "__main__":
    main()
