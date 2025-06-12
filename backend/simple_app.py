"""
Ultra-Simple Reflectly Backend for Algorithm Development
Pure Python Flask app with in-memory storage - no databases, no Docker
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import datetime
from collections import defaultdict
import re
import math
import heapq

app = Flask(__name__)

# Configure CORS properly
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:3000", "http://127.0.0.1:3000"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# In-memory storage (replace database)
emotional_states = []
emotional_transitions = []
user_data = defaultdict(list)

# Available emotions
EMOTIONS = ['joy', 'sadness', 'anger', 'fear', 'disgust', 'surprise', 'neutral']
POSITIVE_EMOTIONS = ['joy', 'surprise']
NEGATIVE_EMOTIONS = ['sadness', 'anger', 'fear', 'disgust']

class SimpleEmotionAnalyzer:
    """Simple emotion analysis using keyword matching"""
    
    def __init__(self):
        self.emotion_keywords = {
            'joy': ['happy', 'excited', 'joy', 'cheerful', 'glad', 'delighted', 'pleased', 'thrilled', 'elated', 'amazing', 'awesome', 'fantastic', 'wonderful', 'great'],
            'sadness': ['sad', 'depressed', 'down', 'upset', 'miserable', 'gloomy', 'sorrowful', 'melancholy', 'disappointed', 'heartbroken', 'crying', 'tears'],
            'anger': ['angry', 'furious', 'mad', 'irritated', 'annoyed', 'frustrated', 'rage', 'livid', 'pissed', 'outraged', 'hostile', 'aggressive'],
            'fear': ['scared', 'afraid', 'frightened', 'worried', 'anxious', 'nervous', 'terrified', 'panic', 'overwhelmed', 'stressed', 'concerned', 'uneasy'],
            'disgust': ['disgusted', 'revolted', 'sickened', 'appalled', 'repulsed', 'nauseated', 'grossed', 'revolting', 'disgusting'],
            'surprise': ['surprised', 'shocked', 'amazed', 'astonished', 'stunned', 'unexpected', 'wow', 'incredible', 'unbelievable'],
        }
    
    def analyze(self, text):
        """Analyze emotion in text using simple keyword matching"""
        text_lower = text.lower()
        scores = {}
        
        for emotion, keywords in self.emotion_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            scores[emotion] = score
        
        # If no emotions detected, default to neutral
        if not any(scores.values()):
            scores['neutral'] = 1
        
        # Get primary emotion
        primary_emotion = max(scores, key=scores.get)
        
        # Normalize scores
        total_score = sum(scores.values())
        if total_score > 0:
            normalized_scores = {k: v/total_score for k, v in scores.items()}
        else:
            normalized_scores = {emotion: 1/len(EMOTIONS) for emotion in EMOTIONS}
        
        return {
            'primary_emotion': primary_emotion,
            'is_positive': primary_emotion in POSITIVE_EMOTIONS,
            'emotion_scores': normalized_scores,
            'confidence': max(normalized_scores.values())
        }

class AStarPathfinder:
    """A* algorithm for finding optimal emotional paths"""
    
    def __init__(self):
        # Default transition costs (can be personalized later)
        self.base_costs = {
            ('sadness', 'joy'): 2.0,
            ('sadness', 'neutral'): 1.0,
            ('sadness', 'anger'): 1.3,
            ('sadness', 'fear'): 1.2,
            ('sadness', 'disgust'): 1.1,
            ('sadness', 'surprise'): 1.8,
            
            ('anger', 'joy'): 2.2,
            ('anger', 'neutral'): 1.3,
            ('anger', 'sadness'): 1.2,
            ('anger', 'fear'): 1.1,
            ('anger', 'disgust'): 0.9,
            ('anger', 'surprise'): 1.5,
            
            ('fear', 'joy'): 2.1,
            ('fear', 'neutral'): 1.2,
            ('fear', 'sadness'): 1.1,
            ('fear', 'anger'): 1.0,
            ('fear', 'disgust'): 0.9,
            ('fear', 'surprise'): 1.4,
            
            ('disgust', 'joy'): 2.0,
            ('disgust', 'neutral'): 1.1,
            ('disgust', 'sadness'): 1.0,
            ('disgust', 'anger'): 0.8,
            ('disgust', 'fear'): 0.9,
            ('disgust', 'surprise'): 1.3,
            
            ('neutral', 'joy'): 0.7,
            ('neutral', 'sadness'): 0.8,
            ('neutral', 'anger'): 0.9,
            ('neutral', 'fear'): 0.8,
            ('neutral', 'disgust'): 0.9,
            ('neutral', 'surprise'): 0.6,
            
            ('joy', 'neutral'): 0.8,
            ('joy', 'sadness'): 1.5,
            ('joy', 'anger'): 1.8,
            ('joy', 'fear'): 1.7,
            ('joy', 'disgust'): 1.6,
            ('joy', 'surprise'): 0.5,
            
            ('surprise', 'joy'): 0.6,
            ('surprise', 'neutral'): 0.7,
            ('surprise', 'sadness'): 1.2,
            ('surprise', 'anger'): 1.4,
            ('surprise', 'fear'): 1.3,
            ('surprise', 'disgust'): 1.2,
        }
        
        # Fill in missing combinations with default values
        for from_emotion in EMOTIONS:
            for to_emotion in EMOTIONS:
                if from_emotion != to_emotion and (from_emotion, to_emotion) not in self.base_costs:
                    if to_emotion in POSITIVE_EMOTIONS:
                        self.base_costs[(from_emotion, to_emotion)] = 1.5
                    elif to_emotion == 'neutral':
                        self.base_costs[(from_emotion, to_emotion)] = 1.0
                    else:
                        self.base_costs[(from_emotion, to_emotion)] = 1.2
    
    def heuristic(self, current, target):
        """Heuristic function for A* search"""
        if current == target:
            return 0
        return self.base_costs.get((current, target), 1.5)
    
    def get_neighbors(self, emotion):
        """Get possible transitions from an emotion"""
        neighbors = {}
        for target in EMOTIONS:
            if target != emotion:
                cost = self.base_costs.get((emotion, target), 1.5)
                action = self.get_action(emotion, target)
                neighbors[target] = {
                    'cost': cost,
                    'action': action,
                    'success_rate': min(1.0, 1.0 / cost)  # Higher cost = lower success rate
                }
        return neighbors
    
    def get_action(self, from_emotion, to_emotion):
        """Get recommended action for transition"""
        actions = {
            ('sadness', 'joy'): "Engage in activities you enjoy",
            ('sadness', 'neutral'): "Practice mindfulness meditation",
            ('sadness', 'anger'): "Express your feelings constructively",
            ('sadness', 'fear'): "Identify specific concerns",
            ('sadness', 'disgust'): "Focus on positive aspects",
            ('sadness', 'surprise'): "Try something new and unexpected",
            
            ('anger', 'joy'): "Channel energy into positive activities",
            ('anger', 'neutral'): "Take deep breaths and count to 10",
            ('anger', 'sadness'): "Reflect on underlying feelings",
            ('anger', 'fear'): "Consider potential consequences",
            ('anger', 'disgust'): "Shift focus to solutions",
            ('anger', 'surprise'): "Do something unexpected to break the pattern",
            
            ('fear', 'joy'): "Focus on positive outcomes",
            ('fear', 'neutral'): "Ground yourself in the present moment",
            ('fear', 'sadness'): "Share your concerns with someone you trust",
            ('fear', 'anger'): "Channel fear into productive action",
            ('fear', 'disgust'): "Challenge negative thoughts",
            ('fear', 'surprise'): "Embrace uncertainty as opportunity",
            
            ('disgust', 'joy'): "Focus on things you appreciate",
            ('disgust', 'neutral'): "Practice acceptance",
            ('disgust', 'sadness'): "Explore underlying values",
            ('disgust', 'anger'): "Set boundaries",
            ('disgust', 'fear'): "Examine core concerns",
            ('disgust', 'surprise'): "Look for unexpected positive aspects",
            
            ('neutral', 'joy'): "Engage in activities you enjoy",
            ('neutral', 'sadness'): "Allow yourself to feel emotions",
            ('neutral', 'anger'): "Identify sources of frustration",
            ('neutral', 'fear'): "Acknowledge concerns",
            ('neutral', 'disgust'): "Identify values being challenged",
            ('neutral', 'surprise'): "Seek out new experiences",
            
            ('joy', 'neutral'): "Practice mindfulness",
            ('joy', 'sadness'): "Reflect on meaningful experiences",
            ('joy', 'anger'): "Channel energy constructively",
            ('joy', 'fear'): "Consider growth opportunities",
            ('joy', 'disgust'): "Examine values and boundaries",
            ('joy', 'surprise'): "Share your joy with others",
            
            ('surprise', 'joy'): "Embrace the unexpected",
            ('surprise', 'neutral'): "Reflect on what surprised you",
            ('surprise', 'sadness'): "Process your feelings about the surprise",
            ('surprise', 'anger'): "Consider why this triggered anger",
            ('surprise', 'fear'): "Identify what feels threatening",
            ('surprise', 'disgust'): "Examine your boundaries",
        }
        return actions.get((from_emotion, to_emotion), f"Work on transitioning from {from_emotion} to {to_emotion}")
    
    def find_path(self, start, goal, max_depth=5):
        """Find optimal path using A* algorithm"""
        if start == goal:
            return {
                'path': [start],
                'actions': [],
                'total_cost': 0,
                'estimated_success_rate': 1.0
            }
        
        # A* algorithm implementation
        open_set = [(0, start, [])]  # (f_score, current_node, path)
        closed_set = set()
        g_score = {start: 0}
        
        while open_set:
            current_f, current, path = heapq.heappop(open_set)
            
            if len(path) >= max_depth:
                continue
                
            if current in closed_set:
                continue
                
            closed_set.add(current)
            
            if current == goal:
                # Reconstruct path with actions
                full_path = path + [current]
                actions = []
                total_cost = g_score[current]
                
                for i in range(len(full_path) - 1):
                    from_emotion = full_path[i]
                    to_emotion = full_path[i + 1]
                    action = self.get_action(from_emotion, to_emotion)
                    cost = self.base_costs.get((from_emotion, to_emotion), 1.5)
                    
                    actions.append({
                        'from': from_emotion,
                        'to': to_emotion,
                        'action': action,
                        'success_rate': min(1.0, 1.0 / cost)
                    })
                
                # Calculate estimated success rate
                if actions:
                    success_rates = [action['success_rate'] for action in actions]
                    estimated_success_rate = 1.0
                    for rate in success_rates:
                        estimated_success_rate *= rate
                else:
                    estimated_success_rate = 1.0
                
                return {
                    'path': full_path,
                    'actions': actions,
                    'total_cost': total_cost,
                    'estimated_success_rate': estimated_success_rate
                }
            
            # Explore neighbors
            neighbors = self.get_neighbors(current)
            for neighbor, info in neighbors.items():
                if neighbor in closed_set:
                    continue
                
                tentative_g = g_score[current] + info['cost']
                
                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    g_score[neighbor] = tentative_g
                    f_score = tentative_g + self.heuristic(neighbor, goal)
                    heapq.heappush(open_set, (f_score, neighbor, path + [current]))
        
        # No path found, return direct transition
        return {
            'path': [start, goal],
            'actions': [{
                'from': start,
                'to': goal,
                'action': self.get_action(start, goal),
                'success_rate': 0.5
            }],
            'total_cost': self.base_costs.get((start, goal), 2.0),
            'estimated_success_rate': 0.5
        }

# Initialize AI components
emotion_analyzer = SimpleEmotionAnalyzer()
pathfinder = AStarPathfinder()

# API Routes
@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        "status": "healthy", 
        "message": "Simple AI backend running",
        "cors_enabled": True,
        "endpoints": [
            "/api/emotions/analyze",
            "/api/emotions/path", 
            "/api/emotions/available",
            "/api/emotions/suggestions",
            "/api/test-algorithm"
        ]
    })

@app.route('/api/emotions/analyze', methods=['POST', 'OPTIONS'])
def analyze_emotion():
    if request.method == 'OPTIONS':
        # Handle preflight request
        return '', 200
        
    try:
        data = request.get_json()
        text = data.get('text', '')
        user_email = data.get('user_email', 'demo@example.com')
        
        if not text:
            return jsonify({"error": "Text is required"}), 400
        
        # Analyze emotion
        result = emotion_analyzer.analyze(text)
        
        # Store in memory
        emotion_entry = {
            'id': len(emotional_states),
            'user_email': user_email,
            'text': text,
            'timestamp': datetime.datetime.now().isoformat(),
            **result
        }
        emotional_states.append(emotion_entry)
        user_data[user_email].append(emotion_entry)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": f"Analysis failed: {str(e)}"}), 500

@app.route('/api/emotions/path', methods=['POST', 'OPTIONS'])
def find_path():
    if request.method == 'OPTIONS':
        return '', 200
        
    try:
        data = request.get_json()
        current_emotion = data.get('current_emotion', '')
        target_emotion = data.get('target_emotion', '')
        
        if not current_emotion or not target_emotion:
            return jsonify({"error": "current_emotion and target_emotion are required"}), 400
        
        if current_emotion not in EMOTIONS or target_emotion not in EMOTIONS:
            return jsonify({"error": "Invalid emotion"}), 400
        
        # Find optimal path
        result = pathfinder.find_path(current_emotion, target_emotion)
        
        return jsonify({
            'current_emotion': current_emotion,
            'target_emotion': target_emotion,
            **result
        })
    except Exception as e:
        return jsonify({"error": f"Pathfinding failed: {str(e)}"}), 500

@app.route('/api/emotions/available', methods=['GET'])
def get_emotions():
    return jsonify({"emotions": EMOTIONS})

@app.route('/api/emotions/suggestions', methods=['POST', 'OPTIONS'])
def get_suggestions():
    if request.method == 'OPTIONS':
        return '', 200
        
    try:
        data = request.get_json()
        current_emotion = data.get('current_emotion', '')
        
        suggestions = {
            'sadness': [
                "Listen to uplifting music",
                "Call a friend or family member", 
                "Take a walk in nature",
                "Practice gratitude by writing 3 good things"
            ],
            'anger': [
                "Take 10 deep breaths",
                "Do some physical exercise",
                "Write down your feelings",
                "Count to 10 slowly"
            ],
            'fear': [
                "Practice grounding techniques (5-4-3-2-1 method)",
                "Challenge negative thoughts",
                "Talk to someone you trust",
                "Focus on what you can control"
            ],
            'disgust': [
                "Focus on positive aspects",
                "Practice acceptance",
                "Engage in a pleasant activity",
                "Connect with supportive people"
            ],
            'neutral': [
                "Set a small goal for today",
                "Practice mindfulness",
                "Try something new",
                "Express gratitude"
            ],
            'joy': [
                "Share your happiness with others",
                "Savor the moment",
                "Use this energy for creative activities",
                "Help someone else"
            ],
            'surprise': [
                "Reflect on what surprised you",
                "Consider what you can learn",
                "Share the experience",
                "Embrace the unexpected"
            ]
        }
        
        return jsonify({"suggestions": suggestions.get(current_emotion, [])})
    except Exception as e:
        return jsonify({"error": f"Failed to get suggestions: {str(e)}"}), 500

@app.route('/api/emotions/graph-data/<user_email>', methods=['GET'])
def get_graph_data(user_email):
    try:
        # Create simple graph data for visualization
        nodes = [{'id': emotion, 'label': emotion.title()} for emotion in EMOTIONS]
        
        # Create edges based on common transitions
        edges = []
        common_transitions = [
            ('sadness', 'neutral'), ('neutral', 'joy'),
            ('anger', 'neutral'), ('fear', 'neutral'),
            ('disgust', 'neutral'), ('surprise', 'joy')
        ]
        
        for from_emotion, to_emotion in common_transitions:
            edges.append({
                'from': from_emotion,
                'to': to_emotion,
                'weight': 1
            })
        
        # Add user's emotional history
        history = user_data.get(user_email, [])
        
        return jsonify({
            'nodes': nodes,
            'edges': edges,
            'history': history[-10:]  # Last 10 entries
        })
    except Exception as e:
        return jsonify({"error": f"Failed to get graph data: {str(e)}"}), 500

@app.route('/api/test-algorithm', methods=['GET'])
def test_algorithm():
    """Test endpoint to verify A* algorithm is working"""
    try:
        test_results = []
        
        test_cases = [
            ('sadness', 'joy'),
            ('anger', 'neutral'),
            ('fear', 'joy'),
            ('disgust', 'neutral'),
            ('anger', 'joy'),
            ('fear', 'surprise'),
            ('sadness', 'surprise')
        ]
        
        for start, goal in test_cases:
            result = pathfinder.find_path(start, goal)
            test_results.append({
                'test': f"{start} -> {goal}",
                'path': result['path'],
                'cost': result['total_cost'],
                'success_rate': result['estimated_success_rate'],
                'steps': len(result['path']) - 1
            })
        
        return jsonify({
            "algorithm_tests": test_results,
            "total_tests": len(test_cases),
            "algorithm": "A* Search",
            "average_success_rate": sum(t['success_rate'] for t in test_results) / len(test_results)
        })
    except Exception as e:
        return jsonify({"error": f"Algorithm test failed: {str(e)}"}), 500

if __name__ == '__main__':
    print("🧠 Starting Simple Reflectly AI Backend")
    print("🎯 Focus: Algorithm Development")
    print("📡 API: http://localhost:5000")
    print("🔬 Test endpoint: http://localhost:5000/api/test-algorithm")
    print("✅ CORS enabled for http://localhost:3000")
    app.run(host='0.0.0.0', port=5000, debug=True)
