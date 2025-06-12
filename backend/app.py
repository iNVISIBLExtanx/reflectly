"""
Simplified Reflectly Flask App - AI-Focused Version
Contains only the core AI functionality for emotional pathfinding and analysis.
"""
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from models.emotional_graph import EmotionalGraph
from models.emotion_analyzer import EmotionAnalyzer
from models.memory_manager import MemoryManager
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# MongoDB connection
mongo_uri = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/reflectly')
mongo_client = MongoClient(mongo_uri)
db = mongo_client.reflectly

# Initialize AI models
emotional_graph = EmotionalGraph(db)
emotion_analyzer = EmotionAnalyzer()
memory_manager = MemoryManager(db)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "reflectly-ai"})

@app.route('/api/emotions/analyze', methods=['POST'])
def analyze_emotion():
    """Analyze emotion from text input"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        user_email = data.get('user_email', '')
        
        if not text:
            return jsonify({"error": "Text is required"}), 400
            
        # Analyze emotion
        emotion_result = emotion_analyzer.analyze_emotion(text)
        
        # Record emotion if user_email provided
        if user_email:
            emotion_id = emotional_graph.record_emotion(user_email, emotion_result)
            emotion_result['emotion_id'] = emotion_id
            
        return jsonify(emotion_result)
        
    except Exception as e:
        logger.error(f"Error analyzing emotion: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/emotions/path', methods=['POST'])
def find_emotional_path():
    """Find optimal path between emotions using A* search"""
    try:
        data = request.get_json()
        user_email = data.get('user_email', '')
        current_emotion = data.get('current_emotion', '')
        target_emotion = data.get('target_emotion', '')
        max_depth = data.get('max_depth', 10)
        
        if not all([user_email, current_emotion, target_emotion]):
            return jsonify({"error": "user_email, current_emotion, and target_emotion are required"}), 400
            
        # Find optimal path
        path_result = emotional_graph.get_emotional_path(
            user_email, current_emotion, target_emotion, max_depth
        )
        
        return jsonify(path_result)
        
    except Exception as e:
        logger.error(f"Error finding emotional path: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/emotions/suggestions', methods=['POST'])
def get_emotion_suggestions():
    """Get personalized action suggestions for current emotion"""
    try:
        data = request.get_json()
        user_email = data.get('user_email', '')
        current_emotion = data.get('current_emotion', '')
        
        if not all([user_email, current_emotion]):
            return jsonify({"error": "user_email and current_emotion are required"}), 400
            
        # Get suggestions
        suggestions = emotional_graph.get_suggested_actions(user_email, current_emotion)
        
        return jsonify({"suggestions": suggestions})
        
    except Exception as e:
        logger.error(f"Error getting emotion suggestions: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/emotions/history/<user_email>', methods=['GET'])
def get_emotion_history(user_email):
    """Get user's emotion history"""
    try:
        limit = request.args.get('limit', 10, type=int)
        
        # Get emotion history
        history = emotional_graph.get_emotion_history(user_email, limit)
        
        return jsonify({"history": history})
        
    except Exception as e:
        logger.error(f"Error getting emotion history: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/emotions/transitions/<user_email>', methods=['GET'])
def get_user_transitions(user_email):
    """Get user's emotional transitions for graph visualization"""
    try:
        # Get transitions
        transitions = emotional_graph.get_user_transitions(user_email)
        
        # Get available emotions for graph nodes
        available_emotions = emotional_graph.get_available_emotions()
        
        return jsonify({
            "transitions": transitions,
            "emotions": available_emotions
        })
        
    except Exception as e:
        logger.error(f"Error getting user transitions: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/emotions/graph-data/<user_email>', methods=['GET'])
def get_graph_data(user_email):
    """Get formatted data for emotional journey graph visualization"""
    try:
        # Get transitions
        transitions = emotional_graph.get_user_transitions(user_email)
        
        # Get emotion history
        history = emotional_graph.get_emotion_history(user_email, 50)
        
        # Format for graph visualization
        nodes = set()
        edges = []
        
        # Create nodes from emotions
        for emotion in emotional_graph.get_available_emotions():
            nodes.add(emotion)
            
        # Create edges from transitions
        for transition in transitions:
            from_emotion = transition.get('from_emotion')
            to_emotion = transition.get('to_emotion')
            
            if from_emotion and to_emotion:
                # Calculate edge weight based on frequency
                edge_exists = False
                for edge in edges:
                    if edge['from'] == from_emotion and edge['to'] == to_emotion:
                        edge['weight'] += 1
                        edge_exists = True
                        break
                        
                if not edge_exists:
                    edges.append({
                        'from': from_emotion,
                        'to': to_emotion,
                        'weight': 1,
                        'actions': transition.get('actions', [])
                    })
        
        # Convert nodes set to list of objects
        node_list = [{'id': emotion, 'label': emotion.title()} for emotion in nodes]
        
        return jsonify({
            "nodes": node_list,
            "edges": edges,
            "history": history
        })
        
    except Exception as e:
        logger.error(f"Error getting graph data: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/emotions/available', methods=['GET'])
def get_available_emotions():
    """Get list of available emotions"""
    try:
        emotions = emotional_graph.get_available_emotions()
        return jsonify({"emotions": emotions})
        
    except Exception as e:
        logger.error(f"Error getting available emotions: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/journal/analyze', methods=['POST'])
def analyze_journal_entry():
    """Analyze a journal entry and record emotional state"""
    try:
        data = request.get_json()
        user_email = data.get('user_email', '')
        content = data.get('content', '')
        
        if not all([user_email, content]):
            return jsonify({"error": "user_email and content are required"}), 400
            
        # Save journal entry
        entry_id = memory_manager.save_memory(user_email, content)
        
        # Analyze emotion
        emotion_result = emotion_analyzer.analyze_emotion(content)
        
        # Record emotion with entry link
        emotion_id = emotional_graph.record_emotion(user_email, emotion_result, entry_id)
        
        return jsonify({
            "entry_id": entry_id,
            "emotion_id": emotion_id,
            "emotion_analysis": emotion_result
        })
        
    except Exception as e:
        logger.error(f"Error analyzing journal entry: {e}")
        return jsonify({"error": "Internal server error"}), 500

# Health check for AI services
@app.route('/api/ai/status', methods=['GET'])
def ai_status():
    """Check status of AI components"""
    try:
        status = {
            "emotional_graph": True,
            "emotion_analyzer": True,
            "search_algorithm": True,
            "database_connection": True
        }
        
        # Test database connection
        try:
            db.list_collection_names()
        except:
            status["database_connection"] = False
            
        return jsonify(status)
        
    except Exception as e:
        logger.error(f"Error checking AI status: {e}")
        return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)
