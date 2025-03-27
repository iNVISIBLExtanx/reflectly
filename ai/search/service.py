"""
A* search service for finding optimal paths through emotional states.
"""

import json
from flask import Flask, request, jsonify
from kafka import KafkaConsumer, KafkaProducer
import threading
import time
import logging
from typing import Dict, Any

from .astar import AStarSearch
from .emotional_heuristics import (
    create_valence_arousal_heuristic,
    create_transition_probability_heuristic,
    create_user_history_heuristic,
    create_combined_heuristic
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)

# Global variables
emotional_graph = {}
emotion_coordinates = {}
transition_probabilities = {}
user_histories = {}

# Kafka configuration
KAFKA_BOOTSTRAP_SERVERS = 'kafka:9092'
KAFKA_TOPIC_REQUESTS = 'astar-search-requests'
KAFKA_TOPIC_RESULTS = 'astar-search-results'

# Kafka producer
producer = None

# Initialize A* search
astar_search = None


def initialize_astar():
    """Initialize A* search with the emotional graph."""
    global astar_search
    astar_search = AStarSearch(emotional_graph)


def load_emotion_data(data_path: str):
    """
    Load emotion data from a JSON file.
    
    Args:
        data_path: Path to the JSON file containing emotion data
    """
    global emotional_graph, emotion_coordinates, transition_probabilities
    
    try:
        with open(data_path, 'r') as f:
            data = json.load(f)
        
        emotional_graph = data.get('graph', {})
        emotion_coordinates = data.get('coordinates', {})
        transition_probabilities = data.get('probabilities', {})
        
        # Initialize A* search with the loaded graph
        initialize_astar()
        
        logger.info(f"Loaded emotion data from {data_path}")
    except Exception as e:
        logger.error(f"Error loading emotion data: {str(e)}")


def load_user_history(user_email: str, data_path: str):
    """
    Load user history from a JSON file.
    
    Args:
        user_email: User's email
        data_path: Path to the JSON file containing user history
    """
    global user_histories
    
    try:
        with open(data_path, 'r') as f:
            data = json.load(f)
        
        user_histories[user_email] = data
        
        logger.info(f"Loaded user history for {user_email} from {data_path}")
    except Exception as e:
        logger.error(f"Error loading user history: {str(e)}")


def create_heuristic_for_user(user_email: str):
    """
    Create a heuristic function for a specific user.
    
    Args:
        user_email: User's email
        
    Returns:
        A heuristic function tailored for the user
    """
    # Create individual heuristics
    valence_arousal_heuristic = create_valence_arousal_heuristic(emotion_coordinates)
    
    transition_prob_heuristic = create_transition_probability_heuristic(transition_probabilities)
    
    # Create user history heuristic if available
    user_history_heuristic = None
    if user_email in user_histories:
        user_history_heuristic = create_user_history_heuristic(user_histories[user_email])
    
    # Combine heuristics with weights
    if user_history_heuristic:
        return create_combined_heuristic(
            [valence_arousal_heuristic, transition_prob_heuristic, user_history_heuristic],
            [0.3, 0.3, 0.4]  # Give more weight to user history
        )
    else:
        return create_combined_heuristic(
            [valence_arousal_heuristic, transition_prob_heuristic],
            [0.5, 0.5]
        )


def process_search_request(request_data: Dict[str, Any]):
    """
    Process an A* search request.
    
    Args:
        request_data: Dictionary containing the search request data
        
    Returns:
        Dictionary containing the search results
    """
    try:
        # Extract request data
        from_emotion = request_data.get('from_emotion')
        to_emotion = request_data.get('to_emotion')
        user_email = request_data.get('user_email')
        constraints = request_data.get('constraints', {})
        
        # Validate request data
        if not from_emotion or not to_emotion:
            return {
                'error': 'Missing required parameters: from_emotion and to_emotion',
                'request_id': request_data.get('request_id')
            }
        
        # Create heuristic for the user
        heuristic = create_heuristic_for_user(user_email)
        
        # Perform A* search
        path, cost = astar_search.search(from_emotion, to_emotion, None, heuristic)
        
        # Create response
        response = {
            'request_id': request_data.get('request_id'),
            'from_emotion': from_emotion,
            'to_emotion': to_emotion,
            'path': path,
            'cost': cost,
            'actions': []
        }
        
        # Add actions for each transition in the path
        for i in range(len(path) - 1):
            from_state = path[i]
            to_state = path[i + 1]
            
            # Get actions for this transition (would come from a database in a real implementation)
            actions = [
                {
                    'action': f"Action from {from_state} to {to_state}",
                    'effectiveness': 0.8,
                    'certainty': 0.7
                }
            ]
            
            response['actions'].append({
                'from': from_state,
                'to': to_state,
                'actions': actions
            })
        
        return response
    except Exception as e:
        logger.error(f"Error processing search request: {str(e)}")
        return {
            'error': f"Error processing search request: {str(e)}",
            'request_id': request_data.get('request_id')
        }


def kafka_consumer_thread():
    """Kafka consumer thread for processing A* search requests."""
    global producer
    
    try:
        # Create Kafka consumer
        consumer = KafkaConsumer(
            KAFKA_TOPIC_REQUESTS,
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            group_id='astar-search-service',
            auto_offset_reset='latest'
        )
        
        # Create Kafka producer
        producer = KafkaProducer(
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda m: json.dumps(m).encode('utf-8')
        )
        
        logger.info(f"Kafka consumer started for topic {KAFKA_TOPIC_REQUESTS}")
        
        # Process messages
        for message in consumer:
            logger.info(f"Received message: {message.value}")
            
            # Process the search request
            response = process_search_request(message.value)
            
            # Send the response
            producer.send(KAFKA_TOPIC_RESULTS, response)
            producer.flush()
            
            logger.info(f"Sent response: {response}")
    except Exception as e:
        logger.error(f"Error in Kafka consumer thread: {str(e)}")


# Flask routes
@app.route('/status', methods=['GET'])
def status():
    """Status endpoint for health checks."""
    return jsonify({
        'status': 'ok',
        'service': 'astar-search',
        'graph_size': len(emotional_graph) if emotional_graph else 0
    })


@app.route('/search', methods=['POST'])
def search():
    """Endpoint for performing A* search."""
    # Get request data
    request_data = request.get_json()
    
    # Process the search request
    response = process_search_request(request_data)
    
    return jsonify(response)


def start_service(host='0.0.0.0', port=5010, data_path=None):
    """
    Start the A* search service.
    
    Args:
        host: Host to bind to
        port: Port to bind to
        data_path: Path to the JSON file containing emotion data
    """
    # Load emotion data if provided
    if data_path:
        load_emotion_data(data_path)
    else:
        # Initialize with an empty graph
        initialize_astar()
    
    # Start Kafka consumer thread
    threading.Thread(target=kafka_consumer_thread, daemon=True).start()
    
    # Start Flask app
    app.run(host=host, port=port)


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='A* Search Service')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=5010, help='Port to bind to')
    parser.add_argument('--data', type=str, help='Path to emotion data JSON file')
    
    args = parser.parse_args()
    
    start_service(args.host, args.port, args.data)
