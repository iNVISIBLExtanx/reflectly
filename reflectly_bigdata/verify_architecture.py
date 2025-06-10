#!/usr/bin/env python3
"""
Script to verify that all components of the Reflectly Big Data architecture
are present in the package directory.
"""
import os
import sys
import json

def verify_architecture_components():
    """
    Verify that all components of the 5-layer architecture are present
    """
    print("=== Reflectly Big Data Architecture Verification ===\n")
    
    # 1. Data Ingestion Layer: Apache Kafka
    kafka_files = [
        "backend/services/kafka_service.py"
    ]
    
    # 2. Storage Layer: HDFS
    hdfs_files = [
        "backend/services/hdfs_service.py"
    ]
    
    # 3. Processing Layer: Apache Spark
    spark_files = [
        "backend/services/spark_service.py",
        "spark/jobs/graph_processing.py",
        "spark/jobs/dataset_import.py",
        "spark/jobs/emotion_analysis.py",
        "spark/jobs/path_finding.py"
    ]
    
    # 4. Database Layer: MongoDB
    # (MongoDB integration is in the emotional_graph_bigdata.py file)
    mongodb_files = [
        "backend/models/emotional_graph_bigdata.py"  # Contains MongoDB integration
    ]
    
    # 5. Analytics Layer: Custom algorithms
    analytics_files = [
        "backend/models/emotional_graph_bigdata.py",  # Contains analytics algorithms
        "spark/jobs/emotion_analysis.py",
        "spark/jobs/path_finding.py"
    ]
    
    # Check each layer
    layers = [
        ("1. Data Ingestion Layer (Apache Kafka)", kafka_files),
        ("2. Storage Layer (HDFS)", hdfs_files),
        ("3. Processing Layer (Apache Spark)", spark_files),
        ("4. Database Layer (MongoDB)", mongodb_files),
        ("5. Analytics Layer (Custom algorithms)", analytics_files)
    ]
    
    all_complete = True
    
    for layer_name, files in layers:
        print(f"Checking {layer_name}:")
        layer_complete = True
        
        for file_path in files:
            exists = os.path.isfile(file_path)
            status = "✓" if exists else "✗"
            print(f"  {status} {file_path}")
            
            if not exists:
                layer_complete = False
                all_complete = False
        
        status = "COMPLETE" if layer_complete else "INCOMPLETE"
        print(f"  Layer status: {status}\n")
    
    # Check for specific code elements in files
    print("Verifying integration code for each layer:")
    integrations = [
        ("Kafka producer/consumer", "backend/services/kafka_service.py", ["KafkaProducer", "KafkaConsumer"]),
        ("HDFS read/write", "backend/services/hdfs_service.py", ["read_file", "write_file"]),
        ("Spark job submission", "backend/services/spark_service.py", ["submit_job"]),
        ("MongoDB integration", "backend/models/emotional_graph_bigdata.py", ["MongoDB", "db"]),
        ("Analytics algorithms", "backend/models/emotional_graph_bigdata.py", ["get_emotion_history", "get_suggested_actions", "get_emotional_path", "get_successful_transitions"])
    ]
    
    for name, file_path, keywords in integrations:
        if os.path.isfile(file_path):
            with open(file_path, 'r') as f:
                content = f.read()
                found_all = all(keyword in content for keyword in keywords)
                status = "✓" if found_all else "✗"
                print(f"  {status} {name} in {file_path}")
                
                if not found_all:
                    all_complete = False
        else:
            print(f"  ✗ {name} (file {file_path} not found)")
            all_complete = False
    
    # Overall assessment
    print("\nOverall architecture assessment:")
    if all_complete:
        print("✓ All architecture components are present and properly integrated")
    else:
        print("✗ Some architecture components are missing or not properly integrated")
        print("  Please check the details above and add any missing components")
    
    return all_complete

if __name__ == "__main__":
    verify_architecture_components()
