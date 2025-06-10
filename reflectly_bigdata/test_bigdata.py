#!/usr/bin/env python3
"""
Test script for Reflectly Big Data functionality
This demonstrates how to use the components with the sample data
"""
import os
import sys
import json
import time
from backend.services.kafka_service import KafkaService
from backend.services.hdfs_service import HDFSService
from backend.services.spark_service import SparkService
from backend.models.emotional_graph_bigdata import EmotionalGraphBigData

def load_sample_data(filename):
    """Load sample emotional states from a JSON file"""
    emotional_states = []
    with open(filename, 'r') as f:
        for line in f:
            state = json.loads(line.strip())
            emotional_states.append(state)
    return emotional_states

def main():
    # Get current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    print("=== Reflectly Big Data Test ===")
    
    # Initialize services with local development settings
    print("\n1. Initializing services...")
    
    # For testing purposes, we can use these local connections
    # Adjust these based on your local setup
    kafka_service = KafkaService(bootstrap_servers="localhost:9092")
    hdfs_service = HDFSService(namenode="localhost:9000", hdfs_bin="hadoop")
    spark_service = SparkService(spark_master="local[*]", spark_submit_path="spark-submit")
    
    print("   Services initialized")
    
    # Create an instance of the EmotionalGraphBigData class
    print("\n2. Creating EmotionalGraphBigData instance...")
    emotional_graph = EmotionalGraphBigData(
        kafka_service=kafka_service,
        hdfs_service=hdfs_service,
        spark_service=spark_service
    )
    print("   EmotionalGraphBigData instance created")
    
    # Load sample data
    print("\n3. Loading sample data...")
    sample_data_path = os.path.join(current_dir, "data/input/sample_emotional_states.json")
    emotional_states = load_sample_data(sample_data_path)
    print(f"   Loaded {len(emotional_states)} emotional states from {sample_data_path}")
    
    # Process sample data
    print("\n4. Testing emotional state processing...")
    for state in emotional_states[:2]:  # Process just a few states for testing
        print(f"   Processing emotional state: {state['primary_emotion']} for user {state['user_email']}")
        emotional_graph.process_emotional_state(
            user_email=state['user_email'],
            primary_emotion=state['primary_emotion'],
            emotion_scores=state['emotion_scores'],
            entry_id=state['entry_id']
        )
    print("   Emotional states processed")
    
    # Test transition recommendations
    print("\n5. Testing emotional transition recommendations...")
    from_emotion = "sadness"
    to_emotion = "joy"
    recommendations = emotional_graph.get_transition_recommendations(from_emotion, to_emotion)
    print(f"   Recommendations for {from_emotion} → {to_emotion}:")
    print(f"   Actions: {recommendations['action']}")
    print(f"   Insight: {recommendations['insight']}")
    
    # Demonstrate running a Spark job (simulation mode)
    print("\n6. Testing Spark job submission...")
    print("   Simulating submission of graph processing job...")
    
    # For actual job submission (when Spark is available):
    # job_id = spark_service.submit_job(
    #     os.path.join(current_dir, "spark/jobs/graph_processing.py"),
    #     job_args=["--input", sample_data_path, 
    #               "--output", os.path.join(current_dir, "data/output/emotional_transitions"),
    #               "--patterns", os.path.join(current_dir, "data/output/patterns")]
    # )
    # print(f"   Job submitted with ID: {job_id}")
    
    print("\n=== Test completed successfully ===")
    print("Note: Some operations were simulated since they require actual Kafka, HDFS and Spark services")
    print("To run with actual services, update the connection parameters and uncomment the relevant code")

if __name__ == "__main__":
    main()
