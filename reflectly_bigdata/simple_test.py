#!/usr/bin/env python3
"""
Simple test script for Reflectly Big Data structure
This demonstrates the directory structure and sample data
without requiring actual connections to Kafka, HDFS, or Spark
"""
import os
import json
import sys

def check_directory_structure():
    """Check if all expected directories and files exist"""
    expected_dirs = [
        "backend/models",
        "backend/services",
        "spark/jobs",
        "data/input",
        "data/output",
        "docs"
    ]
    
    expected_files = [
        "backend/models/emotional_graph_bigdata.py",
        "backend/services/kafka_service.py",
        "backend/services/hdfs_service.py",
        "backend/services/spark_service.py",
        "spark/jobs/dataset_import.py",
        "spark/jobs/emotion_analysis.py",
        "spark/jobs/graph_processing.py",
        "spark/jobs/path_finding.py",
        "data/input/sample_emotional_states.json",
        "docs/big_data_architecture.md",
        "README.md",
        "requirements.txt"
    ]
    
    print("\n=== Checking Directory Structure ===")
    
    all_exist = True
    for dir_path in expected_dirs:
        exists = os.path.isdir(dir_path)
        status = "✓" if exists else "✗"
        print(f"{status} Directory: {dir_path}")
        if not exists:
            all_exist = False
    
    print("\n=== Checking Expected Files ===")
    for file_path in expected_files:
        exists = os.path.isfile(file_path)
        status = "✓" if exists else "✗"
        print(f"{status} File: {file_path}")
        if not exists:
            all_exist = False
    
    return all_exist

def examine_sample_data():
    """Examine the sample emotional states data"""
    print("\n=== Examining Sample Data ===")
    sample_data_path = "data/input/sample_emotional_states.json"
    
    if not os.path.isfile(sample_data_path):
        print(f"Error: Sample data file {sample_data_path} not found")
        return False
    
    try:
        emotional_states = []
        with open(sample_data_path, 'r') as f:
            for line in f:
                state = json.loads(line.strip())
                emotional_states.append(state)
        
        print(f"Successfully loaded {len(emotional_states)} emotional states from {sample_data_path}")
        
        # Display a summary of the data
        users = set()
        emotions = {}
        
        for state in emotional_states:
            users.add(state['user_email'])
            emotion = state['primary_emotion']
            emotions[emotion] = emotions.get(emotion, 0) + 1
        
        print(f"\nUsers in the dataset: {', '.join(users)}")
        print("\nEmotion distribution:")
        for emotion, count in emotions.items():
            print(f"  {emotion}: {count} instances")
        
        print("\nSample emotional state:")
        print(json.dumps(emotional_states[0], indent=2))
        
        return True
    except Exception as e:
        print(f"Error examining sample data: {e}")
        return False

def demonstrate_spark_job():
    """Show what a Spark job would do with the sample data"""
    print("\n=== Demonstrating Spark Job Logic ===")
    sample_data_path = "data/input/sample_emotional_states.json"
    
    if not os.path.isfile(sample_data_path):
        print(f"Error: Sample data file {sample_data_path} not found")
        return False
    
    try:
        # Load emotional states
        emotional_states = []
        with open(sample_data_path, 'r') as f:
            for line in f:
                state = json.loads(line.strip())
                emotional_states.append(state)
        
        # Simulate a simplified version of the graph processing job
        print("Analyzing emotional transitions (simplified simulation):")
        
        # Sort by user and timestamp
        emotional_states.sort(key=lambda x: (x['user_email'], x['timestamp']))
        
        # Find transitions
        transitions = []
        for i in range(len(emotional_states) - 1):
            current = emotional_states[i]
            next_state = emotional_states[i + 1]
            
            if current['user_email'] == next_state['user_email']:
                transition = {
                    'user_email': current['user_email'],
                    'from_emotion': current['primary_emotion'],
                    'to_emotion': next_state['primary_emotion'],
                    'from_timestamp': current['timestamp'],
                    'to_timestamp': next_state['timestamp']
                }
                transitions.append(transition)
        
        print(f"\nFound {len(transitions)} emotional transitions")
        
        # Display some transitions
        if transitions:
            print("\nSample transitions:")
            for i, transition in enumerate(transitions[:3]):
                print(f"  {i+1}. {transition['user_email']}: {transition['from_emotion']} → {transition['to_emotion']}")
        
        return True
    except Exception as e:
        print(f"Error demonstrating Spark job: {e}")
        return False

def main():
    print("=== Reflectly Big Data Structure Test ===")
    current_dir = os.getcwd()
    print(f"Current directory: {current_dir}")
    
    structure_ok = check_directory_structure()
    data_ok = examine_sample_data()
    job_demo_ok = demonstrate_spark_job()
    
    print("\n=== Test Summary ===")
    print(f"Directory structure check: {'PASS' if structure_ok else 'FAIL'}")
    print(f"Sample data examination: {'PASS' if data_ok else 'FAIL'}")
    print(f"Spark job demonstration: {'PASS' if job_demo_ok else 'FAIL'}")
    
    print("\n=== Instructions for Real Testing ===")
    print("To run with actual services, you would need:")
    print("1. Install dependencies: pip install -r requirements.txt")
    print("2. Set up Kafka, HDFS, and Spark (or use local development settings)")
    print("3. Run the full test_bigdata.py script")
    print("4. For specific Spark job testing, run: spark-submit spark/jobs/graph_processing.py --input data/input/sample_emotional_states.json --output data/output/emotional_transitions")

if __name__ == "__main__":
    main()
