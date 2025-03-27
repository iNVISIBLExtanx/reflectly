"""
Service for the intelligent agent.
"""

import json
import os
import logging
import threading
import uuid
from flask import Flask, request, jsonify
from kafka import KafkaConsumer, KafkaProducer
from typing import Dict, List, Any, Optional

from .state import AgentState
from .planner import ActionPlanner

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)

# Global variables
agent_states = {}  # Maps user IDs to AgentState objects
action_planner = None

# Kafka configuration
KAFKA_BOOTSTRAP_SERVERS = 'kafka:9092'
KAFKA_TOPIC_REQUESTS = 'agent-requests'
KAFKA_TOPIC_RESULTS = 'agent-results'
KAFKA_TOPIC_STATE_UPDATES = 'agent-state-updates'

# Kafka producer
producer = None


def initialize_planner(astar_service_url: str, probabilistic_service_url: str):
    """
    Initialize action planner.
    
    Args:
        astar_service_url: URL of the A* search service
        probabilistic_service_url: URL of the probabilistic reasoning service
    """
    global action_planner
    
    action_planner = ActionPlanner(astar_service_url, probabilistic_service_url)
    
    logger.info("Initialized action planner")


def load_agent_states(data_dir: str):
    """
    Load agent states from JSON files in a directory.
    
    Args:
        data_dir: Directory containing agent state JSON files
    """
    global agent_states
    
    try:
        # Create directory if it doesn't exist
        os.makedirs(data_dir, exist_ok=True)
        
        # Load each JSON file in the directory
        for filename in os.listdir(data_dir):
            if filename.endswith('.json'):
                file_path = os.path.join(data_dir, filename)
                
                with open(file_path, 'r') as f:
                    state_data = json.load(f)
                
                # Create AgentState from data
                state = AgentState.from_dict(state_data)
                
                # Add to agent_states
                agent_states[state.user_id] = state
        
        logger.info(f"Loaded {len(agent_states)} agent states from {data_dir}")
    except Exception as e:
        logger.error(f"Error loading agent states: {str(e)}")


def save_agent_state(state: AgentState, data_dir: str):
    """
    Save agent state to a JSON file.
    
    Args:
        state: Agent state to save
        data_dir: Directory to save the state in
    """
    try:
        # Create directory if it doesn't exist
        os.makedirs(data_dir, exist_ok=True)
        
        # Create file path
        file_path = os.path.join(data_dir, f"{state.user_id}.json")
        
        # Save state to file
        with open(file_path, 'w') as f:
            json.dump(state.to_dict(), f, indent=2)
        
        logger.info(f"Saved agent state for user {state.user_id} to {file_path}")
    except Exception as e:
        logger.error(f"Error saving agent state: {str(e)}")


def get_or_create_state(user_id: str) -> AgentState:
    """
    Get or create an agent state for a user.
    
    Args:
        user_id: User ID
        
    Returns:
        Agent state for the user
    """
    global agent_states
    
    # Create state if it doesn't exist
    if user_id not in agent_states:
        agent_states[user_id] = AgentState(user_id)
    
    return agent_states[user_id]


def process_agent_request(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process an agent request.
    
    Args:
        request_data: Dictionary containing the agent request data
        
    Returns:
        Dictionary containing the response
    """
    try:
        # Extract request data
        request_type = request_data.get('type', 'get_state')
        user_id = request_data.get('user_id')
        
        # Validate request data
        if not user_id:
            return {
                'error': 'Missing required parameter: user_id',
                'request_id': request_data.get('request_id')
            }
        
        # Get or create agent state
        state = get_or_create_state(user_id)
        
        # Process based on request type
        if request_type == 'get_state':
            # Return the current state
            return {
                'request_id': request_data.get('request_id'),
                'state': state.to_dict()
            }
        elif request_type == 'update_emotion':
            # Update the current emotion
            emotion = request_data.get('emotion')
            
            if not emotion:
                return {
                    'error': 'Missing required parameter: emotion',
                    'request_id': request_data.get('request_id')
                }
            
            state.update_emotion(emotion)
            
            # Save state
            if 'data_dir' in app.config:
                save_agent_state(state, app.config['data_dir'])
            
            # Publish state update
            if producer:
                producer.send(KAFKA_TOPIC_STATE_UPDATES, {
                    'user_id': user_id,
                    'state': state.to_dict()
                })
            
            return {
                'request_id': request_data.get('request_id'),
                'state': state.to_dict()
            }
        elif request_type == 'set_target_emotion':
            # Set the target emotion
            emotion = request_data.get('emotion')
            
            if not emotion:
                return {
                    'error': 'Missing required parameter: emotion',
                    'request_id': request_data.get('request_id')
                }
            
            state.set_target_emotion(emotion)
            
            # Save state
            if 'data_dir' in app.config:
                save_agent_state(state, app.config['data_dir'])
            
            # Publish state update
            if producer:
                producer.send(KAFKA_TOPIC_STATE_UPDATES, {
                    'user_id': user_id,
                    'state': state.to_dict()
                })
            
            return {
                'request_id': request_data.get('request_id'),
                'state': state.to_dict()
            }
        elif request_type == 'add_context':
            # Add context information
            key = request_data.get('key')
            value = request_data.get('value')
            
            if not key or value is None:
                return {
                    'error': 'Missing required parameters: key and value',
                    'request_id': request_data.get('request_id')
                }
            
            state.add_context(key, value)
            
            # Save state
            if 'data_dir' in app.config:
                save_agent_state(state, app.config['data_dir'])
            
            return {
                'request_id': request_data.get('request_id'),
                'state': state.to_dict()
            }
        elif request_type == 'remove_context':
            # Remove context information
            key = request_data.get('key')
            
            if not key:
                return {
                    'error': 'Missing required parameter: key',
                    'request_id': request_data.get('request_id')
                }
            
            state.remove_context(key)
            
            # Save state
            if 'data_dir' in app.config:
                save_agent_state(state, app.config['data_dir'])
            
            return {
                'request_id': request_data.get('request_id'),
                'state': state.to_dict()
            }
        elif request_type == 'get_next_action':
            # Get the next action to take
            if not action_planner:
                return {
                    'error': 'Action planner not initialized',
                    'request_id': request_data.get('request_id')
                }
            
            next_action = action_planner.get_next_action(state)
            
            if next_action:
                # Add action to state
                state.add_action(next_action)
                
                # Save state
                if 'data_dir' in app.config:
                    save_agent_state(state, app.config['data_dir'])
            
            return {
                'request_id': request_data.get('request_id'),
                'action': next_action
            }
        elif request_type == 'provide_feedback':
            # Process feedback for an action
            action_id = request_data.get('action_id')
            effectiveness = request_data.get('effectiveness')
            notes = request_data.get('notes')
            
            if not action_id or effectiveness is None:
                return {
                    'error': 'Missing required parameters: action_id and effectiveness',
                    'request_id': request_data.get('request_id')
                }
            
            if not action_planner:
                return {
                    'error': 'Action planner not initialized',
                    'request_id': request_data.get('request_id')
                }
            
            # Process feedback
            action_planner.process_feedback(state, action_id, effectiveness, notes)
            
            # Save state
            if 'data_dir' in app.config:
                save_agent_state(state, app.config['data_dir'])
            
            return {
                'request_id': request_data.get('request_id'),
                'state': state.to_dict()
            }
        else:
            return {
                'error': f"Unknown request type: {request_type}",
                'request_id': request_data.get('request_id')
            }
    except Exception as e:
        logger.error(f"Error processing agent request: {str(e)}")
        return {
            'error': f"Error processing agent request: {str(e)}",
            'request_id': request_data.get('request_id')
        }


def kafka_consumer_thread():
    """Kafka consumer thread for processing agent requests."""
    global producer
    
    try:
        # Create Kafka consumer
        consumer = KafkaConsumer(
            KAFKA_TOPIC_REQUESTS,
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            group_id='agent-service',
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
            
            # Process the agent request
            response = process_agent_request(message.value)
            
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
        'service': 'agent',
        'num_states': len(agent_states)
    })


@app.route('/state/<user_id>', methods=['GET'])
def get_state(user_id):
    """Get the agent state for a user."""
    state = get_or_create_state(user_id)
    return jsonify(state.to_dict())


@app.route('/state/<user_id>/emotion', methods=['POST'])
def update_emotion(user_id):
    """Update the current emotion for a user."""
    # Get request data
    request_data = request.get_json()
    emotion = request_data.get('emotion')
    
    if not emotion:
        return jsonify({
            'error': 'Missing required parameter: emotion'
        }), 400
    
    # Get or create state
    state = get_or_create_state(user_id)
    
    # Update emotion
    state.update_emotion(emotion)
    
    # Save state
    if 'data_dir' in app.config:
        save_agent_state(state, app.config['data_dir'])
    
    # Publish state update
    if producer:
        producer.send(KAFKA_TOPIC_STATE_UPDATES, {
            'user_id': user_id,
            'state': state.to_dict()
        })
    
    return jsonify(state.to_dict())


@app.route('/state/<user_id>/target', methods=['POST'])
def set_target_emotion(user_id):
    """Set the target emotion for a user."""
    # Get request data
    request_data = request.get_json()
    emotion = request_data.get('emotion')
    
    if not emotion:
        return jsonify({
            'error': 'Missing required parameter: emotion'
        }), 400
    
    # Get or create state
    state = get_or_create_state(user_id)
    
    # Set target emotion
    state.set_target_emotion(emotion)
    
    # Save state
    if 'data_dir' in app.config:
        save_agent_state(state, app.config['data_dir'])
    
    # Publish state update
    if producer:
        producer.send(KAFKA_TOPIC_STATE_UPDATES, {
            'user_id': user_id,
            'state': state.to_dict()
        })
    
    return jsonify(state.to_dict())


@app.route('/state/<user_id>/action', methods=['GET'])
def get_next_action(user_id):
    """Get the next action for a user."""
    if not action_planner:
        return jsonify({
            'error': 'Action planner not initialized'
        }), 500
    
    # Get or create state
    state = get_or_create_state(user_id)
    
    # Get next action
    next_action = action_planner.get_next_action(state)
    
    if next_action:
        # Add action to state
        state.add_action(next_action)
        
        # Save state
        if 'data_dir' in app.config:
            save_agent_state(state, app.config['data_dir'])
    
    return jsonify({
        'action': next_action
    })


@app.route('/state/<user_id>/feedback', methods=['POST'])
def provide_feedback(user_id):
    """Provide feedback for an action."""
    if not action_planner:
        return jsonify({
            'error': 'Action planner not initialized'
        }), 500
    
    # Get request data
    request_data = request.get_json()
    action_id = request_data.get('action_id')
    effectiveness = request_data.get('effectiveness')
    notes = request_data.get('notes')
    
    if not action_id or effectiveness is None:
        return jsonify({
            'error': 'Missing required parameters: action_id and effectiveness'
        }), 400
    
    # Get or create state
    state = get_or_create_state(user_id)
    
    # Process feedback
    action_planner.process_feedback(state, action_id, effectiveness, notes)
    
    # Save state
    if 'data_dir' in app.config:
        save_agent_state(state, app.config['data_dir'])
    
    return jsonify(state.to_dict())


def start_service(host='0.0.0.0', port=5012, data_dir=None, astar_service_url=None, probabilistic_service_url=None):
    """
    Start the agent service.
    
    Args:
        host: Host to bind to
        port: Port to bind to
        data_dir: Directory for storing agent states
        astar_service_url: URL of the A* search service
        probabilistic_service_url: URL of the probabilistic reasoning service
    """
    # Set data directory in app config
    if data_dir:
        app.config['data_dir'] = data_dir
        
        # Load agent states
        load_agent_states(data_dir)
    
    # Initialize action planner
    if astar_service_url and probabilistic_service_url:
        initialize_planner(astar_service_url, probabilistic_service_url)
    
    # Start Kafka consumer thread
    threading.Thread(target=kafka_consumer_thread, daemon=True).start()
    
    # Start Flask app
    app.run(host=host, port=port)


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Agent Service')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=5012, help='Port to bind to')
    parser.add_argument('--data-dir', type=str, help='Directory for storing agent states')
    parser.add_argument('--astar-service', type=str, help='URL of the A* search service')
    parser.add_argument('--probabilistic-service', type=str, help='URL of the probabilistic reasoning service')
    
    args = parser.parse_args()
    
    start_service(args.host, args.port, args.data_dir, args.astar_service, args.probabilistic_service)
