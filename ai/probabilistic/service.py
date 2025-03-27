"""
Service for probabilistic reasoning about emotional states.
"""

import json
import os
import logging
import threading
from flask import Flask, request, jsonify
from kafka import KafkaConsumer, KafkaProducer
from typing import Dict, List, Any, Optional

from .bayesian_network import BayesianNetwork
from .markov_model import MarkovModel

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)

# Global variables
emotions = []
actions = []
bayesian_network = None
markov_model = None

# Kafka configuration
KAFKA_BOOTSTRAP_SERVERS = 'kafka:9092'
KAFKA_TOPIC_REQUESTS = 'probabilistic-reasoning-requests'
KAFKA_TOPIC_RESULTS = 'probabilistic-reasoning-results'

# Kafka producer
producer = None


def load_emotions_and_actions(data_path: str):
    """
    Load emotions and actions from a JSON file.
    
    Args:
        data_path: Path to the JSON file containing emotions and actions
    """
    global emotions, actions
    
    try:
        with open(data_path, 'r') as f:
            data = json.load(f)
        
        emotions = data.get('emotions', [])
        actions = data.get('actions', [])
        
        logger.info(f"Loaded {len(emotions)} emotions and {len(actions)} actions from {data_path}")
    except Exception as e:
        logger.error(f"Error loading emotions and actions: {str(e)}")


def initialize_models():
    """Initialize Bayesian network and Markov model."""
    global bayesian_network, markov_model
    
    # Initialize Bayesian network
    bayesian_network = BayesianNetwork.create_emotional_network(emotions, actions)
    
    # Initialize Markov model
    markov_model = MarkovModel.create_emotional_model(emotions)
    
    logger.info("Initialized Bayesian network and Markov model")


def load_model_parameters(data_path: str):
    """
    Load model parameters from a JSON file.
    
    Args:
        data_path: Path to the JSON file containing model parameters
    """
    global bayesian_network, markov_model
    
    try:
        with open(data_path, 'r') as f:
            data = json.load(f)
        
        # Load Bayesian network parameters
        if 'bayesian_network' in data and bayesian_network is not None:
            bn_data = data['bayesian_network']
            
            # Load CPTs
            for node_name, cpt_data in bn_data.get('cpts', {}).items():
                # Convert string keys to tuples
                cpt = {}
                for key_str, value in cpt_data.items():
                    if key_str == '()':
                        key = ()
                    else:
                        key = tuple(key_str.strip('()').split(','))
                    cpt[key] = value
                
                bayesian_network.set_cpt(node_name, cpt)
        
        # Load Markov model parameters
        if 'markov_model' in data and markov_model is not None:
            mm_data = data['markov_model']
            
            # Load transition probabilities
            for from_state, transitions in mm_data.get('transitions', {}).items():
                for to_state, probability in transitions.items():
                    markov_model.set_transition_probability(from_state, to_state, probability)
        
        logger.info(f"Loaded model parameters from {data_path}")
    except Exception as e:
        logger.error(f"Error loading model parameters: {str(e)}")


def process_prediction_request(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process a prediction request.
    
    Args:
        request_data: Dictionary containing the prediction request data
        
    Returns:
        Dictionary containing the prediction results
    """
    try:
        # Extract request data
        request_type = request_data.get('type', 'next_emotion')
        current_emotion = request_data.get('current_emotion')
        actions = request_data.get('actions', [])
        evidence = request_data.get('evidence', {})
        steps = request_data.get('steps', 1)
        
        # Validate request data
        if not current_emotion:
            return {
                'error': 'Missing required parameter: current_emotion',
                'request_id': request_data.get('request_id')
            }
        
        # Process based on request type
        if request_type == 'next_emotion':
            # Predict next emotion using Bayesian network
            if bayesian_network is not None:
                predictions = bayesian_network.predict_emotion(current_emotion, actions, evidence)
            else:
                return {
                    'error': 'Bayesian network not initialized',
                    'request_id': request_data.get('request_id')
                }
        elif request_type == 'emotion_sequence':
            # Predict emotion sequence using Markov model
            if markov_model is not None:
                predictions = markov_model.predict_state_after_n_steps(current_emotion, steps)
            else:
                return {
                    'error': 'Markov model not initialized',
                    'request_id': request_data.get('request_id')
                }
        elif request_type == 'action_recommendation':
            # Recommend actions using Bayesian network
            target_emotion = request_data.get('target_emotion')
            available_actions = request_data.get('available_actions', actions)
            num_recommendations = request_data.get('num_recommendations', 3)
            
            if not target_emotion:
                return {
                    'error': 'Missing required parameter: target_emotion',
                    'request_id': request_data.get('request_id')
                }
            
            if bayesian_network is not None:
                recommendations = bayesian_network.recommend_actions(
                    current_emotion, target_emotion, available_actions, evidence, num_recommendations
                )
                
                return {
                    'request_id': request_data.get('request_id'),
                    'current_emotion': current_emotion,
                    'target_emotion': target_emotion,
                    'recommendations': recommendations
                }
            else:
                return {
                    'error': 'Bayesian network not initialized',
                    'request_id': request_data.get('request_id')
                }
        else:
            return {
                'error': f"Unknown request type: {request_type}",
                'request_id': request_data.get('request_id')
            }
        
        # Create response
        response = {
            'request_id': request_data.get('request_id'),
            'current_emotion': current_emotion,
            'predictions': predictions
        }
        
        return response
    except Exception as e:
        logger.error(f"Error processing prediction request: {str(e)}")
        return {
            'error': f"Error processing prediction request: {str(e)}",
            'request_id': request_data.get('request_id')
        }


def kafka_consumer_thread():
    """Kafka consumer thread for processing probabilistic reasoning requests."""
    global producer
    
    try:
        # Create Kafka consumer
        consumer = KafkaConsumer(
            KAFKA_TOPIC_REQUESTS,
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            group_id='probabilistic-reasoning-service',
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
            
            # Process the prediction request
            response = process_prediction_request(message.value)
            
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
        'service': 'probabilistic-reasoning',
        'models': {
            'bayesian_network': 'initialized' if bayesian_network is not None else 'not initialized',
            'markov_model': 'initialized' if markov_model is not None else 'not initialized'
        }
    })


@app.route('/predict', methods=['POST'])
def predict():
    """Endpoint for making predictions."""
    # Get request data
    request_data = request.get_json()
    
    # Process the prediction request
    response = process_prediction_request(request_data)
    
    return jsonify(response)


def start_service(host='0.0.0.0', port=5011, data_path=None, model_params_path=None):
    """
    Start the probabilistic reasoning service.
    
    Args:
        host: Host to bind to
        port: Port to bind to
        data_path: Path to the JSON file containing emotions and actions
        model_params_path: Path to the JSON file containing model parameters
    """
    # Load emotions and actions if provided
    if data_path:
        load_emotions_and_actions(data_path)
    else:
        # Use default emotions and actions
        global emotions, actions
        emotions = ['happy', 'sad', 'angry', 'anxious', 'calm', 'excited']
        actions = ['exercise', 'meditate', 'socialize', 'rest', 'work']
    
    # Initialize models
    initialize_models()
    
    # Load model parameters if provided
    if model_params_path:
        load_model_parameters(model_params_path)
    
    # Start Kafka consumer thread
    threading.Thread(target=kafka_consumer_thread, daemon=True).start()
    
    # Start Flask app
    app.run(host=host, port=port)


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Probabilistic Reasoning Service')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=5011, help='Port to bind to')
    parser.add_argument('--data', type=str, help='Path to emotions and actions JSON file')
    parser.add_argument('--model-params', type=str, help='Path to model parameters JSON file')
    
    args = parser.parse_args()
    
    start_service(args.host, args.port, args.data, args.model_params)
