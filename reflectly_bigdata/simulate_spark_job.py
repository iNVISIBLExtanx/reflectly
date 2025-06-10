#!/usr/bin/env python3
"""
Simulation script for Spark jobs
This simulates running the graph_processing.py Spark job without requiring a Spark installation
"""
import os
import json
import argparse
from datetime import datetime

def simulate_spark_graph_processing(input_path, output_path, patterns_path=None):
    """
    Simulate the graph_processing.py Spark job
    """
    print(f"Simulating Spark job: graph_processing.py")
    print(f"Input: {input_path}")
    print(f"Output: {output_path}")
    if patterns_path:
        print(f"Patterns: {patterns_path}")
    
    # Make sure output directories exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    if patterns_path:
        os.makedirs(os.path.dirname(patterns_path), exist_ok=True)
        os.makedirs(f"{patterns_path}/frequencies", exist_ok=True)
        os.makedirs(f"{patterns_path}/paths", exist_ok=True)
    
    # Load emotional states from input file
    print("\nReading emotional states...")
    emotional_states = []
    with open(input_path, 'r') as f:
        for line in f:
            state = json.loads(line.strip())
            emotional_states.append(state)
    
    print(f"Loaded {len(emotional_states)} emotional states")
    
    # Group by user and sort by timestamp
    print("\nGrouping and sorting emotional states...")
    users = {}
    for state in emotional_states:
        user_email = state['user_email']
        if user_email not in users:
            users[user_email] = []
        users[user_email].append(state)
    
    for user_email, states in users.items():
        states.sort(key=lambda x: x['timestamp'])
        print(f"User {user_email}: {len(states)} states")
    
    # Find transitions between emotional states
    print("\nFinding emotional transitions...")
    transitions = []
    
    for user_email, states in users.items():
        for i in range(len(states) - 1):
            current = states[i]
            next_state = states[i + 1]
            
            transition = {
                'user_email': user_email,
                'from_emotion': current['primary_emotion'],
                'to_emotion': next_state['primary_emotion'],
                'from_state_id': current['_id'],
                'to_state_id': next_state['_id'],
                'from_timestamp': current['timestamp'],
                'to_timestamp': next_state['timestamp'],
                'actions': [
                    {
                        'description': 'Practice mindfulness',
                        'success_rate': 0.7
                    },
                    {
                        'description': 'Engage in physical activity',
                        'success_rate': 0.6
                    }
                ]
            }
            transitions.append(transition)
    
    print(f"Found {len(transitions)} emotional transitions")
    
    # Write transitions to output file
    print(f"\nWriting transitions to {output_path}...")
    with open(output_path, 'w') as f:
        for transition in transitions:
            f.write(json.dumps(transition) + "\n")
    
    # If patterns path is provided, analyze transition patterns
    if patterns_path:
        print(f"\nAnalyzing transition patterns...")
        
        # Count transition frequencies
        frequencies = {}
        for transition in transitions:
            key = (transition['user_email'], transition['from_emotion'], transition['to_emotion'])
            if key not in frequencies:
                frequencies[key] = 0
            frequencies[key] += 1
        
        # Write frequencies to output file
        frequency_output = f"{patterns_path}/frequencies/part-00000.json"
        with open(frequency_output, 'w') as f:
            for (user_email, from_emotion, to_emotion), frequency in frequencies.items():
                f.write(json.dumps({
                    'user_email': user_email,
                    'from_emotion': from_emotion,
                    'to_emotion': to_emotion,
                    'frequency': frequency
                }) + "\n")
        
        print(f"Wrote {len(frequencies)} transition frequencies to {frequency_output}")
        
        # Find common paths (3-step)
        paths = {}
        for i in range(len(transitions) - 1):
            t1 = transitions[i]
            for j in range(i+1, len(transitions)):
                t2 = transitions[j]
                
                # Check if transitions form a path
                if (t1['user_email'] == t2['user_email'] and 
                    t1['to_emotion'] == t2['from_emotion'] and
                    t1['to_timestamp'] < t2['from_timestamp']):
                    
                    key = (t1['user_email'], t1['from_emotion'], t1['to_emotion'], t2['to_emotion'])
                    if key not in paths:
                        paths[key] = 0
                    paths[key] += 1
        
        # Write paths to output file
        paths_output = f"{patterns_path}/paths/part-00000.json"
        with open(paths_output, 'w') as f:
            for (user_email, start_emotion, middle_emotion, end_emotion), frequency in paths.items():
                f.write(json.dumps({
                    'user_email': user_email,
                    'start_emotion': start_emotion,
                    'middle_emotion': middle_emotion,
                    'end_emotion': end_emotion,
                    'frequency': frequency
                }) + "\n")
        
        print(f"Wrote {len(paths)} common paths to {paths_output}")
    
    print("\nSpark job simulation completed successfully")
    return len(transitions)

def main():
    parser = argparse.ArgumentParser(description="Simulate Spark job")
    parser.add_argument("--input", required=True, help="Path to input file (emotional states)")
    parser.add_argument("--output", required=True, help="Path to output file (emotional transitions)")
    parser.add_argument("--patterns", required=False, help="Path to patterns output")
    
    args = parser.parse_args()
    
    # Simulate the graph processing job
    count = simulate_spark_graph_processing(args.input, args.output, args.patterns)
    print(f"\nProcessed {count} emotional transitions")

if __name__ == "__main__":
    main()
